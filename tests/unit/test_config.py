# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
"""
Unit tests for configuration settings.
Tests Settings validation, role ID parsing, and environment variable handling.
"""

import pytest
import os
from unittest.mock import patch
from config.settings import Settings
from pydantic_core import ValidationError as PydanticValidationError


class TestSettings:
    """Test suite for Settings class."""

    def test_settings_loads_from_env(self):
        """Test Settings loads configuration from environment variables."""
        # Arrange
        with patch.dict(
            os.environ,
            {
                "DISCORD_BOT_TOKEN": "test_token_12345",
                "GUILD_ID": "111222333",
                "RECRUITMENT_CHANNEL_ID": "444555666",
                "CHARACTER_SHEET_VAULT_CHANNEL_ID": "777888999",  # Changed from FORUM_CHANNEL_ID
                "CEMETERY_CHANNEL_ID": "101010101",
                "WANDERER_ROLE_ID": "123",
                "SEEKER_ROLE_ID": "456",
                "PATHFINDER_ROLE_ID": "789",
                "TRAILWARDEN_ROLE_ID": "012",
                "POLL_INTERVAL_SECONDS": "60",
                "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
                "DATABASE_URL": "postgresql://test:test@localhost:5432/testdb",  # Mandatory now
            },
        ):
            # Act
            settings = Settings()

            # Assert
            assert settings.DISCORD_BOT_TOKEN == "test_token_12345"
            assert settings.GUILD_ID == 111222333
            assert settings.RECRUITMENT_CHANNEL_ID == 444555666
            assert (
                settings.WEBHOOK_SECRET
                == "a_very_long_secret_that_is_at_least_32_chars_long"
            )

    def test_guild_member_role_ids_property(self):
        """Test GUILD_MEMBER_ROLE_IDS property returns all 4 roles."""
        with patch.dict(
            os.environ,
            {
                "DISCORD_BOT_TOKEN": "test_token_12345",
                "GUILD_ID": "1",
                "RECRUITMENT_CHANNEL_ID": "1",
                "CHARACTER_SHEET_VAULT_CHANNEL_ID": "1",
                "CEMETERY_CHANNEL_ID": "1",
                "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
                "DATABASE_URL": "sqlite:///:memory:",
                "WANDERER_ROLE_ID": "100",
                "SEEKER_ROLE_ID": "200",
                "PATHFINDER_ROLE_ID": "300",
                "TRAILWARDEN_ROLE_ID": "400",
            },
        ):
            settings = Settings()
            role_ids = settings.GUILD_MEMBER_ROLE_IDS
            assert len(role_ids) == 4
            assert 100 in role_ids
            assert 400 in role_ids

    def test_officer_role_ids_property(self):
        """Test OFFICER_ROLE_IDS property."""
        with patch.dict(
            os.environ,
            {
                "DISCORD_BOT_TOKEN": "test_token_12345",
                "GUILD_ID": "1",
                "RECRUITMENT_CHANNEL_ID": "1",
                "CHARACTER_SHEET_VAULT_CHANNEL_ID": "1",
                "CEMETERY_CHANNEL_ID": "1",
                "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
                "DATABASE_URL": "sqlite:///:memory:",
                "PATHFINDER_ROLE_ID": "789",
                "TRAILWARDEN_ROLE_ID": "012",
            },
        ):
            settings = Settings()
            role_ids = settings.OFFICER_ROLE_IDS
            assert len(role_ids) == 2
            assert 789 in role_ids
            assert 12 in role_ids

    def test_validate_fails_missing_discord_token(self):
        """Test Settings.validate() fails if DISCORD_BOT_TOKEN missing."""
        with patch.dict(
            os.environ,
            {
                "DISCORD_BOT_TOKEN": "",
                "GUILD_ID": "111",
                "RECRUITMENT_CHANNEL_ID": "222",
                "CHARACTER_SHEET_VAULT_CHANNEL_ID": "333",
                "CEMETERY_CHANNEL_ID": "1",
                "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
                "DATABASE_URL": "sqlite:///:memory:",
            },
        ):
            with pytest.raises(ValueError, match="DISCORD_BOT_TOKEN"):
                Settings()

    def test_reaction_emojis_defined(self):
        """Test reaction emojis are properly defined."""
        with patch.dict(
            os.environ,
            {
                "DISCORD_BOT_TOKEN": "test_token_12345",
                "GUILD_ID": "1",
                "RECRUITMENT_CHANNEL_ID": "1",
                "CHARACTER_SHEET_VAULT_CHANNEL_ID": "1",
                "CEMETERY_CHANNEL_ID": "1",
                "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
                "WANDERER_ROLE_ID": "1",
                "DATABASE_URL": "sqlite:///:memory:",
            },
        ):
            settings = Settings()
            assert settings.APPROVE_EMOJI == "✅"
            assert settings.REJECT_EMOJI == "❌"

    def test_default_poll_interval(self):
        """Test POLL_INTERVAL_SECONDS has sensible default."""
        with patch.dict(
            os.environ,
            {
                "DISCORD_BOT_TOKEN": "test_token_12345",
                "GUILD_ID": "1",
                "RECRUITMENT_CHANNEL_ID": "1",
                "CHARACTER_SHEET_VAULT_CHANNEL_ID": "1",
                "CEMETERY_CHANNEL_ID": "1",
                "WEBHOOK_SECRET": "a_very_long_secret_that_is_at_least_32_chars_long",
                "WANDERER_ROLE_ID": "1",
                "DATABASE_URL": "sqlite:///:memory:",
            },
            clear=True,
        ):
            settings = Settings()
            assert settings.POLL_INTERVAL_SECONDS == 60

    def test_webhook_secret_minimum_length(self):
        """Test that WEBHOOK_SECRET must be at least 32 characters."""
        with patch.dict(
            os.environ,
            {
                "DISCORD_BOT_TOKEN": "test_token_12345",
                "GUILD_ID": "111",
                "RECRUITMENT_CHANNEL_ID": "222",
                "CHARACTER_SHEET_VAULT_CHANNEL_ID": "333",
                "CEMETERY_CHANNEL_ID": "1",
                "WEBHOOK_SECRET": "short",
                "DATABASE_URL": "sqlite:///:memory:",
            },
        ):
            with pytest.raises(
                PydanticValidationError,
                match="String should have at least 32 characters",
            ):
                Settings()
