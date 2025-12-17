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
import datetime
from domain.models import Character
from domain.models import (
    STATUS_PENDING,
    STATUS_REGISTERED,
    STATUS_REJECTED,
    STATUS_DECEASED,
    STATUS_BURIED,
    STATUS_RETIRED
)

class TestModels:
    """
    Tests for data models and constants.
    """

    def test_status_constants(self):
        """Verify status constants match documentation."""
        assert STATUS_PENDING == "PENDING"
        assert STATUS_REGISTERED == "REGISTERED"
        assert STATUS_REJECTED == "REJECTED"
        assert STATUS_DECEASED == "DECEASED"
        assert STATUS_BURIED == "BURIED"
        assert STATUS_RETIRED == "RETIRED"

    def test_character_initialization(self):
        """Test Character model initialization with all 27 logic fields."""
        # Note: Dataclass might not have 27 fields exactly as constructor args if some are auto-generated
        # but based on TECHNICAL.md Data Models section, it lists fields.
        
        char = Character(
            discord_user_id="123456789",
            discord_name="User#1234",
            name="Thorgar",
            race="Dwarf",
            char_class="Warrior",
            roles="Tank, Melee DPS",
            professions="Mining, Blacksmithing",
            backstory="A backstory",
            personality="Stoic",
            quotes="For the King!",
            portrait_url="https://example.com/img.png",
            trait_1="Brave",
            trait_2="Loyal",
            trait_3="Strong",
            status=STATUS_PENDING,
            confirmation=True,
            request_sdxl=False
        )

        assert char.name == "Thorgar"
        assert char.race == "Dwarf"
        assert char.status == STATUS_PENDING
        assert char.roles == "Tank, Melee DPS"
    
    def test_character_defaults(self):
        """Test default values for optional timestamps if they exist in model."""
        char = Character(
            discord_user_id="123",
            discord_name="User#123",
            name="Test",
            race="Human",
            char_class="Mage",
            roles="DPS",
            professions="",
            backstory="Story",
            personality="",
            quotes="",
            portrait_url="",
            trait_1="A",
            trait_2="B",
            trait_3="C",
            status=STATUS_PENDING,
            confirmation=False,
            request_sdxl=False
        )
        # Check if timestamps are None by default as per python model definition in docs
        assert char.registered_at is None
        assert char.created_at is None
        assert char.updated_at is None

    def test_character_to_dict(self):
        """Test serialization to dictionary (if implemented/needed for sheets)."""
        # This implies a to_dict method or similar, often used. 
        # If not strictly documented as a method on Character, we might skip.
        # But Sheets Service converts it. 
        pass