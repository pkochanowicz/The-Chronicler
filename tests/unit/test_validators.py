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
from domain.validators import (
    validate_race,
    validate_class,
    validate_roles,
    validate_professions,
    validate_url,
    ValidationError
)

class TestValidators:
    """
    Tests for validation logic based on TECHNICAL.md enum definitions.
    """

    def test_validate_race_valid(self):
        """Test that all valid races are accepted."""
        valid_races = [
            "Human", "Dwarf", "Night Elf", "Gnome", "High Elf",
            "Orc", "Undead", "Tauren", "Troll", "Goblin",
            "Other"
        ]
        for race in valid_races:
            assert validate_race(race) is True

    def test_validate_race_invalid(self):
        """Test that invalid races are rejected."""
        invalid_races = ["Pandaren", "Vulpera", "Eredar", "", None]
        for race in invalid_races:
            with pytest.raises(ValidationError, match="Invalid race"):
                validate_race(race)

    def test_validate_class_valid(self):
        """Test that all valid classes are accepted."""
        valid_classes = [
            "Warrior", "Paladin", "Hunter", "Rogue", "Priest",
            "Shaman", "Mage", "Warlock", "Druid"
        ]
        for char_class in valid_classes:
            assert validate_class(char_class) is True

    def test_validate_class_invalid(self):
        """Test that invalid classes are rejected."""
        invalid_classes = ["Death Knight", "Monk", "Demon Hunter", "Evoker", ""]
        for char_class in invalid_classes:
            with pytest.raises(ValidationError, match="Invalid class"):
                validate_class(char_class)

    def test_validate_roles_valid_single(self):
        """Test valid single role selection."""
        assert validate_roles(["Tank"]) is True

    def test_validate_roles_valid_multiple(self):
        """Test valid multiple role selection."""
        assert validate_roles(["Tank", "Melee DPS"]) is True
        assert validate_roles(["Healer", "Ranged DPS"]) is True

    def test_validate_roles_invalid_empty(self):
        """Test that empty role selection is rejected (min 1)."""
        with pytest.raises(ValidationError, match="At least one role must be selected"):
            validate_roles([])

    def test_validate_roles_invalid_option(self):
        """Test that invalid role options are rejected."""
        with pytest.raises(ValidationError, match="Invalid role"):
            validate_roles(["Tank", "Cheerleader"])

    def test_validate_professions_valid_empty(self):
        """Test that empty professions list is valid (optional)."""
        assert validate_professions([]) is True

    def test_validate_professions_valid_selection(self):
        """Test valid profession selection."""
        assert validate_professions(["Mining", "Blacksmithing"]) is True
        assert validate_professions(["Cooking", "Fishing", "First Aid"]) is True
        assert validate_professions(["Survival"]) is True

    def test_validate_professions_invalid_option(self):
        """Test that invalid profession options are rejected."""
        with pytest.raises(ValidationError, match="Invalid profession"):
            validate_professions(["Mining", "Video Gaming"])

    def test_validate_url_valid(self):
        """Test valid URL formats."""
        valid_urls = [
            "https://example.com/image.png",
            "http://test.com/pic.jpg",
            "https://i.imgur.com/xyz.png"
        ]
        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_invalid(self):
        """Test invalid URL formats."""
        invalid_urls = [
            "ftp://example.com",
            "www.example.com",
            "example.com",
            "not a url"
        ]
        for url in invalid_urls:
            with pytest.raises(ValidationError, match="Invalid URL format"):
                validate_url(url)

    def test_validate_professions_max_primary(self):
        """Test that maximum 2 primary professions are allowed.

        Per WoW game rules and TECHNICAL.md, characters can have:
        - Maximum 2 primary professions (gathering/crafting)
        - Maximum 4 secondary professions (utility)

        Primary professions: Alchemy, Blacksmithing, Enchanting, Engineering,
        Herbalism, Leatherworking, Mining, Skinning, Tailoring, Jewelcrafting
        """
        # Valid: Exactly 2 primary professions
        assert validate_professions(["Mining", "Blacksmithing"]) is True

        # Valid: 1 primary profession
        assert validate_professions(["Engineering"]) is True

        # Invalid: 3 primary professions (exceeds limit)
        with pytest.raises(ValidationError, match="Cannot have more than 2 primary"):
            validate_professions(["Mining", "Blacksmithing", "Engineering"])

    def test_validate_professions_mixed_limits(self):
        """Test profession limits with mixed primary/secondary combinations."""
        # Valid: 1 primary + 3 secondary
        assert validate_professions([
            "Mining",  # Primary
            "First Aid", "Cooking", "Fishing"  # Secondary
        ]) is True

        # Valid: 2 primary + 2 secondary
        assert validate_professions([
            "Herbalism", "Alchemy",  # Primary
            "Cooking", "First Aid"  # Secondary
        ]) is True

        # Invalid: 3 primary + 2 secondary (primary limit exceeded)
        with pytest.raises(ValidationError, match="Cannot have more than 2 primary"):
            validate_professions([
                "Mining", "Blacksmithing", "Engineering",  # 3 primary (INVALID)
                "Cooking", "First Aid"  # 2 secondary (ok)
            ])

    def test_validate_professions_categories(self):
        """Test that profession categories are correctly identified.

        This test documents which professions are primary vs secondary.
        Validates that the profession enforcement logic correctly categorizes
        all valid professions.
        """
        from domain.validators import VALID_PROFESSIONS

        # Define expected categories (per TECHNICAL.md)
        primary_professions = {
            "Alchemy", "Blacksmithing", "Enchanting", "Engineering",
            "Herbalism", "Leatherworking", "Mining", "Skinning",
            "Tailoring", "Jewelcrafting", "Inscription"
        }

        secondary_professions = {
            "First Aid", "Cooking", "Fishing", "Survival"
        }

        # Verify all valid professions are categorized
        all_professions = primary_professions | secondary_professions

        # Check that VALID_PROFESSIONS includes all categories
        for prof in VALID_PROFESSIONS:
            assert prof in all_professions, f"{prof} should be categorized"

        # Document: validate_professions() enforces:
        # - len([p for p in professions if p in primary_professions]) <= 2
        # - len([p for p in professions if p in secondary_professions]) <= 4

        # Test enforcement with maximum of each category
        assert validate_professions(list(primary_professions)[:2]) is True  # 2 primary ok
        assert validate_professions(list(secondary_professions)) is True  # 4 secondary ok

        # Test that exceeding primary limit raises error
        with pytest.raises(ValidationError, match="Cannot have more than 2 primary professions"):
            validate_professions(list(primary_professions)[:3])  # 3 primary fails