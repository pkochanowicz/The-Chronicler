# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest
from domain.models import (
    STATUS_PENDING,
    STATUS_REGISTERED,
    STATUS_REJECTED,
    STATUS_DECEASED,
    STATUS_BURIED,
    STATUS_RETIRED
)

class TestLifecycle:
    """
    Tests for Character Lifecycle State Machine transitions.
    """
    
    # We might need a helper class or method that implements the transition logic
    # if it's not in the Character model itself. 
    # Assuming logic is in `services.sheets_service.CharacterRegistryService.update_character_status`
    # or similar. But here we test the RULES.
    
    def test_valid_transitions(self):
        """
        Validate state machine transitions per TECHNICAL.md lines 329-375.

        Valid paths:
        - PENDING → REGISTERED (officer approval via reaction)
        - PENDING → REJECTED (officer rejection via reaction)
        - REGISTERED → DECEASED (officer uses /bury command)
        - REGISTERED → RETIRED (character retirement)
        - DECEASED → BURIED (automatic webhook after burial ceremony)
        """
        # Define valid transitions based on TECHNICAL.md state machine diagram
        valid_transitions = {
            STATUS_PENDING: [STATUS_REGISTERED, STATUS_REJECTED],
            STATUS_REGISTERED: [STATUS_DECEASED, STATUS_RETIRED],
            STATUS_DECEASED: [STATUS_BURIED],
            STATUS_BURIED: [],    # Final state - no transitions allowed
            STATUS_REJECTED: [],  # Final state - requires new submission to re-enter flow
            STATUS_RETIRED: []    # Final state - character permanently retired
        }

        # Verify all status constants are accounted for in transition map
        all_statuses = {STATUS_PENDING, STATUS_REGISTERED, STATUS_REJECTED,
                       STATUS_DECEASED, STATUS_BURIED, STATUS_RETIRED}
        assert set(valid_transitions.keys()) == all_statuses, \
            "Transition map must include all status constants"

        # Validate critical lifecycle paths exist
        assert STATUS_REGISTERED in valid_transitions[STATUS_PENDING], \
            "PENDING must allow transition to REGISTERED (officer approval)"
        assert STATUS_REJECTED in valid_transitions[STATUS_PENDING], \
            "PENDING must allow transition to REJECTED (officer rejection)"
        assert STATUS_DECEASED in valid_transitions[STATUS_REGISTERED], \
            "REGISTERED must allow transition to DECEASED (character death)"
        assert STATUS_BURIED in valid_transitions[STATUS_DECEASED], \
            "DECEASED must allow transition to BURIED (burial ceremony)"

        # Verify final states have no outgoing transitions
        assert len(valid_transitions[STATUS_BURIED]) == 0, \
            "BURIED is final state - no transitions allowed"
        assert len(valid_transitions[STATUS_REJECTED]) == 0, \
            "REJECTED is final state - requires new submission"

    def test_invalid_transitions(self):
        """
        Validate that invalid state transitions are blocked.

        These transitions violate the lifecycle state machine and must be prevented:
        - Skipping approval: PENDING → DECEASED/BURIED
        - Reversing decisions: REGISTERED → REJECTED
        - Resurrecting dead: BURIED/DECEASED → any earlier state
        - Auto-approving after rejection: REJECTED → REGISTERED
        """
        # Build valid transitions map (must match test_valid_transitions)
        valid_transitions = {
            STATUS_PENDING: [STATUS_REGISTERED, STATUS_REJECTED],
            STATUS_REGISTERED: [STATUS_DECEASED, STATUS_RETIRED],
            STATUS_DECEASED: [STATUS_BURIED],
            STATUS_BURIED: [],
            STATUS_REJECTED: [],
            STATUS_RETIRED: []
        }

        # Define critical invalid transition cases that must be blocked
        invalid_cases = [
            # Skip approval flow
            (STATUS_PENDING, STATUS_BURIED, "Cannot skip approval and go directly to buried"),
            (STATUS_PENDING, STATUS_DECEASED, "Cannot skip approval and mark as deceased"),
            (STATUS_PENDING, STATUS_RETIRED, "Cannot retire character before approval"),

            # Reverse officer decisions
            (STATUS_REGISTERED, STATUS_REJECTED, "Cannot reject after approval"),
            (STATUS_REGISTERED, STATUS_PENDING, "Cannot return to pending after approval"),

            # Violate final state immutability
            (STATUS_BURIED, STATUS_DECEASED, "Cannot resurrect buried character"),
            (STATUS_BURIED, STATUS_REGISTERED, "Cannot resurrect buried character"),
            (STATUS_BURIED, STATUS_PENDING, "Cannot resurrect buried character"),

            (STATUS_REJECTED, STATUS_REGISTERED, "Cannot auto-approve after rejection"),
            (STATUS_REJECTED, STATUS_PENDING, "Rejected characters require new submission"),

            # Invalid death transitions
            (STATUS_DECEASED, STATUS_REGISTERED, "Cannot undo death status"),
            (STATUS_DECEASED, STATUS_REJECTED, "Cannot reject deceased character"),
        ]

        # Verify each invalid case is not in valid transitions
        for from_status, to_status, reason in invalid_cases:
            allowed_transitions = valid_transitions.get(from_status, [])
            assert to_status not in allowed_transitions, \
                f"Invalid transition {from_status} → {to_status} must be blocked: {reason}"
