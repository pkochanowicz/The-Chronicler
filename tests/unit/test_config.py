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

"""
Unit tests for configuration settings.
Tests Settings validation, role ID parsing, and environment variable handling.
"""
import pytest
import os
from unittest.mock import patch
from config.settings import Settings


class TestSettings:
    """Test suite for Settings class."""

    def test_settings_loads_from_env(self):
        """Test Settings loads configuration from environment variables."""
        # Arrange
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token_12345",
            "GUILD_ID": "111222333",
            "RECRUITMENT_CHANNEL_ID": "444555666",
            "FORUM_CHANNEL_ID": "777888999",
            "CEMETERY_CHANNEL_ID": "101010101",
            "WANDERER_ROLE_ID": "123",
            "SEEKER_ROLE_ID": "456",
            "PATHFINDER_ROLE_ID": "789",
            "TRAILWARDEN_ROLE_ID": "012",
            "GOOGLE_SHEET_ID": "test_sheet_id",
            "GOOGLE_CREDENTIALS_FILE": "test_creds.json",
            "POLL_INTERVAL_SECONDS": "60",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long"
        }):
            # Act
            settings = Settings()

            # Assert
            assert settings.DISCORD_BOT_TOKEN == "test_token_12345"
            assert settings.GUILD_ID == 111222333
            assert settings.RECRUITMENT_CHANNEL_ID == 444555666
            assert settings.WEBHOOK_SECRET == "a_very_long_secret_that_is_at_least_32_chars_long"

    def test_guild_member_role_ids_property(self):
        """Test GUILD_MEMBER_ROLE_IDS property returns all 4 roles."""
        # Arrange
        with patch.dict(os.environ, {
            "WANDERER_ROLE_ID": "100",
            "SEEKER_ROLE_ID": "200",
            "PATHFINDER_ROLE_ID": "300",
            "TRAILWARDEN_ROLE_ID": "400"
        }):
            settings = Settings()

            # Act
            role_ids = settings.GUILD_MEMBER_ROLE_IDS

            # Assert
            assert len(role_ids) == 4
            assert 100 in role_ids
            assert 200 in role_ids
            assert 300 in role_ids
            assert 400 in role_ids

    def test_lifecycle_role_ids_property(self):
        """Test LIFECYCLE_ROLE_IDS property returns Pathfinder and Trailwarden."""
        # Arrange
        with patch.dict(os.environ, {
            "PATHFINDER_ROLE_ID": "789",
            "TRAILWARDEN_ROLE_ID": "012"
        }):
            settings = Settings()

            # Act
            role_ids = settings.LIFECYCLE_ROLE_IDS

            # Assert
            assert len(role_ids) == 2
            assert 789 in role_ids
            assert 12 in role_ids

    def test_validate_success_with_all_required_fields(self):
        """Test Settings.validate() succeeds with all required fields."""
        # Arrange
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "GUILD_ID": "111",
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
            "WANDERER_ROLE_ID": "100",
            "PATHFINDER_ROLE_ID": "200"
        }):
            settings = Settings()

            # Assert (should not raise, as validation is implicit)
            assert isinstance(settings, Settings)

    def test_validate_fails_missing_discord_token(self):
        """Test Settings.validate() fails if DISCORD_BOT_TOKEN missing."""
        # Arrange
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "",
            "GUILD_ID": "111",
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long"
        }):
            # Act & Assert
            with pytest.raises(ValueError, match="DISCORD_BOT_TOKEN"):
                Settings()

    def test_validate_fails_missing_guild_id(self):
        """Test Settings.validate() fails if GUILD_ID missing or 0."""
        # Arrange
        from pydantic_core import ValidationError as PydanticValidationError
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "GUILD_ID": "0",  # Invalid GUILD_ID
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long"
        }):
            # Act & Assert
            with pytest.raises(PydanticValidationError, match="Input should be greater than 0"):
                Settings()

    def test_validate_fails_no_guild_member_roles(self):
        """Test Settings.validate() fails if no guild member roles configured.

        Settings._validate_guild_roles() checks that at least one GUILD_MEMBER_ROLE_ID
        is greater than 0. If all role IDs are 0, the bot is misconfigured and
        validation should raise ValueError.
        """
        # Arrange
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "GUILD_ID": "111",
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
            "WANDERER_ROLE_ID": "0",
            "SEEKER_ROLE_ID": "0",
            "PATHFINDER_ROLE_ID": "0",
            "TRAILWARDEN_ROLE_ID": "0"
        }):
            # Act & Assert
            # Settings.validate() is called in __init__() and should raise ValueError
            with pytest.raises(ValueError, match="At least one Guild Member Role ID must be configured."):
                Settings()

    def test_validate_fails_no_lifecycle_roles(self):
        """Test Settings configuration with no lifecycle roles (Pathfinder/Trailwarden).

        NOTE: This test documents current validation behavior. Settings._validate_guild_roles()
        checks that at least one GUILD_MEMBER_ROLE_ID > 0, which includes lifecycle roles.
        However, it does NOT specifically require that lifecycle roles (Pathfinder/Trailwarden)
        be configured separately from other member roles.

        If Wanderer or Seeker roles are configured but lifecycle roles are 0, the bot will
        pass validation but officers won't be able to approve/reject characters or perform burials.

        This test verifies that if ONLY lifecycle roles are 0 (but other roles exist),
        validation still passes. This documents a potential enhancement area.
        """
        # Arrange - Set lifecycle roles to 0, but keep other member roles configured
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "GUILD_ID": "111",
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
            "WANDERER_ROLE_ID": "123",  # At least one role configured
            "SEEKER_ROLE_ID": "456",
            "PATHFINDER_ROLE_ID": "0",  # Lifecycle roles not configured
            "TRAILWARDEN_ROLE_ID": "0"
        }):
            settings = Settings()

            # Act
            lifecycle_ids = settings.OFFICER_ROLE_IDS

            # Assert - Validation passes, but lifecycle functionality is limited
            assert len(lifecycle_ids) == 2, "Should have 2 lifecycle role IDs defined"
            assert all(role_id == 0 for role_id in lifecycle_ids), \
                "Both lifecycle role IDs are 0 (officer commands won't work)"

            # Document: Validation currently passes because Wanderer/Seeker are configured.
            # Future enhancement: Could add specific check for officer roles if needed.

    def test_class_emojis_defined(self):
        """Test CLASS_EMOJIS dictionary is properly defined."""
        # Need minimal env
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test", "GUILD_ID": "1", "RECRUITMENT_CHANNEL_ID": "1", 
            "FORUM_CHANNEL_ID": "1", "GOOGLE_SHEET_ID": "1", 
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
            "WANDERER_ROLE_ID": "1"
        }):
            settings = Settings()
            # Act
            emojis = settings.CLASS_EMOJIS
            # Assert
            assert len(emojis) == 9
            assert emojis["Warrior"] == "⚔️"

    def test_reaction_emojis_defined(self):
        """Test reaction emojis are properly defined."""
        # Need minimal env
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test", "GUILD_ID": "1", "RECRUITMENT_CHANNEL_ID": "1", 
            "FORUM_CHANNEL_ID": "1", "GOOGLE_SHEET_ID": "1", 
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
            "WANDERER_ROLE_ID": "1"
        }):
            settings = Settings()
            # Assert
            assert settings.APPROVE_EMOJI == "✅"
            assert settings.REJECT_EMOJI == "❌"

    def test_default_poll_interval(self):
        """Test POLL_INTERVAL_SECONDS has sensible default."""
        # Arrange
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test", "GUILD_ID": "1", "RECRUITMENT_CHANNEL_ID": "1", 
            "FORUM_CHANNEL_ID": "1", "GOOGLE_SHEET_ID": "1", 
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
            "WANDERER_ROLE_ID": "1"
        }, clear=True):
            # Act
            settings = Settings()

            # Assert
            assert settings.POLL_INTERVAL_SECONDS == 60

        def test_integer_parsing_for_ids(self):        """Test channel and role IDs are parsed as integers."""
        # Arrange
        with patch.dict(os.environ, {
            "GUILD_ID": "123456789",
            "RECRUITMENT_CHANNEL_ID": "987654321",
            "WANDERER_ROLE_ID": "111222333",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
             # Min requirements
            "DISCORD_BOT_TOKEN": "test", "FORUM_CHANNEL_ID": "1", "GOOGLE_SHEET_ID": "1"
        }):
            settings = Settings()

            # Assert
            assert isinstance(settings.GUILD_ID, int)
            assert isinstance(settings.RECRUITMENT_CHANNEL_ID, int)
            assert isinstance(settings.WANDERER_ROLE_ID, int)
            assert settings.GUILD_ID == 123456789
            assert settings.RECRUITMENT_CHANNEL_ID == 987654321
            assert settings.WANDERER_ROLE_ID == 111222333

    def test_webhook_secret_minimum_length(self):
        """Test that WEBHOOK_SECRET must be at least 32 characters.

        Per TECHNICAL.md and audit findings, webhook secret must be
        at least 32 characters for security. Shorter secrets are vulnerable
        to brute force attacks.
        """
        # Test with secret that's too short (< 32 chars)
        from pydantic_core import ValidationError as PydanticValidationError
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "GUILD_ID": "111",
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "short_secret_only_12"  # Only 21 chars
        }):
            # Settings should raise ValueError on init due to validation
            with pytest.raises(PydanticValidationError, match="String should have at least 32 characters"):
                Settings()

        # Test with secret that's exactly 32 chars (boundary case)
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "GUILD_ID": "111",
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "a" * 32  # Exactly 32 chars
        }):
            settings = Settings()
            assert len(settings.WEBHOOK_SECRET) == 32

        # Test with secret longer than 32 chars (should pass)
        with patch.dict(os.environ, {
            "DISCORD_BOT_TOKEN": "test_token",
            "GUILD_ID": "111",
            "RECRUITMENT_CHANNEL_ID": "222",
            "FORUM_CHANNEL_ID": "333",
            "GOOGLE_SHEET_ID": "test_sheet",
            "WEBHOOK_SECRET": "a_very_long_secret_that_is_definitely_more_than_32_characters_long"
        }):
            settings = Settings()
            assert len(settings.WEBHOOK_SECRET) > 32