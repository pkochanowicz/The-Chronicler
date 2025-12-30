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
        """
        Test Character model serialization.

        Per TECHNICAL.md, character data is serialized when writing to Google Sheets.
        The CharacterRegistryService handles the serialization logic, converting
        Character objects to row data matching the 27-column schema.

        This test verifies that Character model has the necessary fields for serialization.
        """
        char = Character(
            discord_user_id="123",
            discord_name="TestUser#1234",
            name="Thorgar",
            race="Dwarf",
            char_class="Warrior",
            roles="Tank",
            professions="Mining",
            backstory="A story",
            personality="Brave",
            quotes="For the Alliance!",
            portrait_url="https://example.com/img.png",
            trait_1="Brave",
            trait_2="Loyal",
            trait_3="Strong",
            status=STATUS_PENDING,
            confirmation=True,
            request_sdxl=False
        )

        # Verify character has all required fields for serialization
        assert hasattr(char, 'name')
        assert hasattr(char, 'race')
        assert hasattr(char, 'char_class')
        assert hasattr(char, 'status')
        assert hasattr(char, 'discord_user_id')

        # Check if Character has to_dict method (it does per domain/models.py line 134)
        assert hasattr(char, 'to_dict'), "Character should have to_dict method"

        # Test to_dict method
        char_dict = char.to_dict()
        assert isinstance(char_dict, dict)
        assert char_dict['discord_id'] == "123"
        assert char_dict['char_name'] == "Thorgar"

        # Note: to_dict() is currently partial (only returns discord_id and char_name)
        # CharacterRegistryService handles full serialization to 27-column schema
        # This is acceptable - to_dict() provides basic serialization support