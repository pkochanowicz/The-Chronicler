# Azeroth Bound Discord Bot
# Copyright (C) 2025 Paweł Kochanowicz <github.com/pkochanowicz>
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
Configuration management for Azeroth Bound Bot.
Loads environment variables and provides typed access to configuration values.
"""
import os
import base64
import json
import tempfile
import logging
from typing import List
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.
    
    Automatically validates critical configuration on initialization.
    Supports both local development (credentials.json file) and 
    production deployment (base64-encoded credentials).
    """

    def __init__(self):
        """Initialize settings and validate configuration."""
        self._load_environment_variables()
        self._setup_derived_properties()
        self._validate_configuration()
        logger.info("✅ Configuration loaded and validated successfully")
        logger.info(f"   Guild ID: {self.GUILD_ID}")
        logger.info(f"   Recruitment Channel: {self.RECRUITMENT_CHANNEL_ID}")
        logger.info(f"   Forum Channel: {self.FORUM_CHANNEL_ID}")
        logger.info(f"   Cemetery Channel: {self.CEMETERY_CHANNEL_ID}")
        logger.info(f"   Interactive Timeout: {self.INTERACTIVE_TIMEOUT_SECONDS}s")
        # DO NOT log DISCORD_BOT_TOKEN, WEBHOOK_SECRET, or GOOGLE_CREDENTIALS!

    def _load_environment_variables(self):
        """Load all settings from environment variables."""
        
        # Discord Configuration
        self.DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
        self.GUILD_ID: int = int(os.getenv("GUILD_ID", "0"))
        self.RECRUITMENT_CHANNEL_ID: int = int(os.getenv("RECRUITMENT_CHANNEL_ID", "0"))
        self.FORUM_CHANNEL_ID: int = int(os.getenv("FORUM_CHANNEL_ID", "0"))
        self.CEMETERY_CHANNEL_ID: int = int(os.getenv("CEMETERY_CHANNEL_ID", "0"))
        self.GRAPHICS_STORAGE_CHANNEL_ID: int = int(os.getenv("GRAPHICS_STORAGE_CHANNEL_ID", "0")) # New

        # Guild Member Role IDs (FIXED: all uppercase)
        self.WANDERER_ROLE_ID: int = int(os.getenv("WANDERER_ROLE_ID", "0"))
        self.SEEKER_ROLE_ID: int = int(os.getenv("SEEKER_ROLE_ID", "0"))
        self.PATHFINDER_ROLE_ID: int = int(os.getenv("PATHFINDER_ROLE_ID", "0"))
        self.TRAILWARDEN_ROLE_ID: int = int(os.getenv("TRAILWARDEN_ROLE_ID", "0"))

        # Officer Role Mentions
        self.PATHFINDER_ROLE_MENTION: str = os.getenv("PATHFINDER_ROLE_MENTION", "")
        self.TRAILWARDEN_ROLE_MENTION: str = os.getenv("TRAILWARDEN_ROLE_MENTION", "")

        # Google Sheets Configuration
        self.GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
        self.BACKUP_FOLDER_ID: str = os.getenv("BACKUP_FOLDER_ID", "")

        # Bot Behavior
        self.POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
        self.INTERACTIVE_TIMEOUT_SECONDS: int = int(os.getenv("INTERACTIVE_TIMEOUT_SECONDS", "300"))

        # Webhook Security
        self.WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

        # MCP Server
        self.MCP_PORT: int = int(os.getenv("MCP_PORT", "8081"))
        self.MCP_API_KEY: str = os.getenv("MCP_API_KEY", "")

        # Deployment
        self.PORT: int = int(os.getenv("PORT", "8080"))

        # Visuals
        self.DEFAULT_PORTRAIT_URL: str = os.getenv(
            "DEFAULT_PORTRAIT_URL",
            "https://i.imgur.com/default_placeholder.png"
        )

        # Reaction Emojis (constants, not configurable)
        self.APPROVE_EMOJI: str = "✅"
        self.REJECT_EMOJI: str = "❌"

        # Class Emojis (constants, not configurable)
        self.CLASS_EMOJIS = {
            "Warrior": "⚔️",
            "Paladin": "🛡️",
            "Hunter": "🏹",
            "Rogue": "🗡️",
            "Priest": "✨",
            "Shaman": "🌩️",
            "Mage": "🔮",
            "Warlock": "👹",
            "Druid": "🌿",
        }

    def _setup_derived_properties(self):
        """Set up properties that depend on environment variables."""
        # Google credentials (FIXED: now actually called!)
        self.GOOGLE_CREDENTIALS_FILE: str = self._setup_google_credentials()

    def _setup_google_credentials(self) -> str:
        """
        Set up Google credentials from base64 env var or local file.
        
        Works for both Fly.io and Render.com deployments (base64) and
        local development (credentials.json file).
        
        Returns:
            str: Path to credentials file
            
        Raises:
            ValueError: If base64 decoding fails
            FileNotFoundError: If neither base64 nor file are available
        """
        creds_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")

        if creds_b64:
            # Production: decode from base64
            try:
                creds_json = base64.b64decode(creds_b64).decode('utf-8')
                creds = json.loads(creds_json)

                # Write to temp file for gspread to use
                temp_file = os.path.join(tempfile.gettempdir(), 'credentials.json')
                with open(temp_file, 'w') as f:
                    json.dump(creds, f)

                logger.info("✅ Google credentials loaded from GOOGLE_CREDENTIALS_B64")
                return temp_file
            except Exception as e:
                raise ValueError(f"Failed to decode GOOGLE_CREDENTIALS_B64: {e}")
        else:
            # Local development: use file directly
            local_creds = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
            if not os.path.exists(local_creds):
                raise FileNotFoundError(
                    f"credentials.json not found at '{local_creds}'. "
                    "Set GOOGLE_CREDENTIALS_B64 for production or add credentials.json locally."
                )
            logger.info(f"✅ Google credentials loaded from file: {local_creds}")
            return local_creds

    @property
    def GUILD_MEMBER_ROLE_IDS(self) -> List[int]:
        """
        List of all guild member role IDs.
        Users with any of these roles can use /register_character.
        """
        return [
            self.WANDERER_ROLE_ID,
            self.SEEKER_ROLE_ID,
            self.PATHFINDER_ROLE_ID,
            self.TRAILWARDEN_ROLE_ID
        ]

    @property
    def OFFICER_ROLE_IDS(self) -> List[int]:
        """
        List of officer role IDs.
        Users with these roles can approve/reject characters and use /bury.
        """
        return [
            self.PATHFINDER_ROLE_ID,
            self.TRAILWARDEN_ROLE_ID
        ]

    @property
    def LIFECYCLE_ROLE_IDS(self) -> List[int]:
        """
        List of roles authorized for lifecycle events (burial, etc).
        Same as Officer roles: Pathfinder and Trailwarden.
        """
        return [
            self.PATHFINDER_ROLE_ID,
            self.TRAILWARDEN_ROLE_ID
        ]

    def validate(self) -> bool:
        """
        Public method to trigger validation manually.
        Returns True if successful, raises ValueError otherwise.
        """
        self._validate_configuration()
        return True

    def _validate_configuration(self):
        """
        Validate all critical configuration.
        
        Raises:
            ValueError: If any required configuration is missing or invalid
        """
        self._validate_required_fields()
        self._validate_webhook_secret()
        self._validate_guild_roles()

    def _validate_required_fields(self):
        """Validate that all required fields are present."""
        required_fields = [
            ("DISCORD_BOT_TOKEN", self.DISCORD_BOT_TOKEN),
            ("GUILD_ID", self.GUILD_ID),
            ("RECRUITMENT_CHANNEL_ID", self.RECRUITMENT_CHANNEL_ID),
            ("FORUM_CHANNEL_ID", self.FORUM_CHANNEL_ID),
            ("GOOGLE_SHEET_ID", self.GOOGLE_SHEET_ID),
            ("WEBHOOK_SECRET", self.WEBHOOK_SECRET),
            ("MCP_API_KEY", self.MCP_API_KEY),
            ("GRAPHICS_STORAGE_CHANNEL_ID", self.GRAPHICS_STORAGE_CHANNEL_ID), # New
        ]

        missing = [name for name, value in required_fields if not value]

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Please check your .env file."
            )

    def _validate_webhook_secret(self):
        """Validate webhook secret meets security requirements."""
        if len(self.WEBHOOK_SECRET) < 32:
            raise ValueError(
                "WEBHOOK_SECRET must be at least 32 characters for security. "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

    def _validate_guild_roles(self):
        """
        Validate that at least one guild member role is configured.
        These roles are required for /register_character command access control.
        """
        if not any(role_id > 0 for role_id in self.GUILD_MEMBER_ROLE_IDS):
            raise ValueError(
                "At least one Guild Member Role must be configured! "
                "Set one of: WANDERER_ROLE_ID, SEEKER_ROLE_ID, "
                "PATHFINDER_ROLE_ID, or TRAILWARDEN_ROLE_ID in your .env file. "
                "These are Discord role IDs (integers), not role names."
            )

        # Log which roles are configured (helpful for debugging)
        role_names = ["Wanderer", "Seeker", "Pathfinder", "Trailwarden"]
        configured_roles = [
            name for name, role_id in zip(role_names, self.GUILD_MEMBER_ROLE_IDS)
            if role_id > 0
        ]

        logger.info(f"✅ Guild roles configured: {', '.join(configured_roles)}")


# Singleton instance for convenient importing
settings = Settings()
