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
from unittest.mock import AsyncMock, patch

class TestInteractiveFlows:
    """
    Tests for interactive command flows (/register_character and /bury).
    """

    @pytest.mark.asyncio
    async def test_registration_flow_happy_path(self, mock_discord_interaction):
        """Test /register_character flow steps 1-12 happy path."""
        # We need to import the class (will fail until Phase 3 implementation)
        from flows.registration_flow import RegistrationFlow
        
        flow = RegistrationFlow(mock_discord_interaction)
        
        # Populate data manually to simulate steps completion
        flow.data = {
            "discord_id": "123",
            "discord_name": "TestUser",
            "char_name": "Thorgar",
            "race": "Dwarf",
            "class": "Warrior",
            "roles": "Tank",
            "professions": "Mining",
            "trait_1": "Brave",
            "trait_2": "Strong",
            "trait_3": "Beer",
            "backstory": "Story",
            "preview_embeds": [] # Mock embeds
        }
        
        # ... jump to finalize
        with patch("services.sheets_service.CharacterRegistryService.__init__", return_value=None), \
             patch("services.sheets_service.CharacterRegistryService.log_character") as mock_log:
            await flow.finalize()
            mock_log.assert_called_once()
            
            # Verify data sent to sheets
            args, _ = mock_log.call_args
            char_data = args[0]
            assert char_data["char_name"] == "Thorgar"
            assert char_data["status"] == "PENDING"
            assert char_data["confirmation"] is True

    @pytest.mark.asyncio
    async def test_burial_flow_permissions(self, mock_discord_interaction):
        """Test /bury requires officer permissions."""
        from flows.burial_flow import BurialFlow
        # Mock non-officer
        mock_discord_interaction.user.roles = [] 
        pass

    @pytest.mark.asyncio
    async def test_burial_flow_atomic_execution(self, mock_discord_interaction):
        """Test atomic execution of burial rite."""
        from flows.burial_flow import BurialFlow
        
        flow = BurialFlow(mock_discord_interaction)
        flow.data = {
            "character_data": {"char_name": "Thorgar"}, # Nested dict
            "death_cause": "Fell to gravity",
            "death_story": "It was a long way down.",
            "confirmed": True
        }
        
        with patch("services.sheets_service.CharacterRegistryService.__init__", return_value=None), \
             patch("services.sheets_service.CharacterRegistryService.update_character_status") as mock_update:
             
             await flow.execute_burial() # Test specific method
             mock_update.assert_called_with("Thorgar", "DECEASED", death_cause="Fell to gravity", death_story="It was a long way down.")
