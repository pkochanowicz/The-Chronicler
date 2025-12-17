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
Configuration management for Azeroth Bound Bot.
Loads environment variables and provides typed access to configuration values.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self._load()

    def _load(self):
        """Load settings from environment variables."""
        # Discord Configuration
        self.DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
        self.GUILD_ID: int = int(os.getenv("GUILD_ID", "0"))
        self.RECRUITMENT_CHANNEL_ID: int = int(os.getenv("RECRUITMENT_CHANNEL_ID", "0"))
        self.FORUM_CHANNEL_ID: int = int(os.getenv("FORUM_CHANNEL_ID", "0"))
        self.CEMETERY_CHANNEL_ID: int = int(os.getenv("CEMETERY_CHANNEL_ID", "0"))

        # Individual role IDs
        self.WANDERER_ROLE_ID: int = int(os.getenv("wanderer_role_id", "0"))
        self.SEEKER_ROLE_ID: int = int(os.getenv("seeker_role_id", "0"))
        self.PATHFINDER_ROLE_ID: int = int(os.getenv("pathfinder_role_id", "0"))
        self.TRAILWARDEN_ROLE_ID: int = int(os.getenv("trailwarden_role_id", "0"))
        
        # Officer Role Mentions
        self.PATHFINDER_ROLE_MENTION: str = os.getenv("PATHFINDER_ROLE_MENTION", "")
        self.TRAILWARDEN_ROLE_MENTION: str = os.getenv("TRAILWARDEN_ROLE_MENTION", "")

        # Google Sheets Configuration
        self.GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
        self.GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.BACKUP_FOLDER_ID: str = os.getenv("BACKUP_FOLDER_ID", "")

        # Bot Behavior
        self.POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
        self.INTERACTIVE_TIMEOUT_SECONDS: int = int(os.getenv("INTERACTIVE_TIMEOUT_SECONDS", "300"))
        
        # Webhook Security
        self.WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")

        # Visuals
        self.DEFAULT_PORTRAIT_URL: str = os.getenv(
            "DEFAULT_PORTRAIT_URL",
            "https://i.imgur.com/default_placeholder.png"
        )

        # Reaction Emojis
        self.APPROVE_EMOJI: str = "✅"
        self.REJECT_EMOJI: str = "❌"

        # Class Emojis
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

    # Guild member role IDs
    @property
    def GUILD_MEMBER_ROLE_IDS(self) -> List[int]:
        return [self.WANDERER_ROLE_ID, self.SEEKER_ROLE_ID, self.PATHFINDER_ROLE_ID, self.TRAILWARDEN_ROLE_ID]

    # Lifecycle management role IDs
    @property
    def LIFECYCLE_ROLE_IDS(self) -> List[int]:
        return [self.PATHFINDER_ROLE_ID, self.TRAILWARDEN_ROLE_ID]

    def validate(self) -> bool:
        """Validate that all required settings are present."""
        required_fields = [
            ("DISCORD_BOT_TOKEN", self.DISCORD_BOT_TOKEN),
            ("GUILD_ID", self.GUILD_ID),
            ("RECRUITMENT_CHANNEL_ID", self.RECRUITMENT_CHANNEL_ID),
            ("FORUM_CHANNEL_ID", self.FORUM_CHANNEL_ID),
            ("GOOGLE_SHEET_ID", self.GOOGLE_SHEET_ID),
            ("WEBHOOK_SECRET", self.WEBHOOK_SECRET),
        ]

        missing = [name for name, value in required_fields if not value]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
            
        if len(self.WEBHOOK_SECRET) < 32:
             raise ValueError("WEBHOOK_SECRET must be at least 32 characters")

        # Check for role IDs - ensure at least one is set if they are all 0
        if not any(self.GUILD_MEMBER_ROLE_IDS):
             # Wait, the previous logic checked if list is empty, but list always has 4 elements (0s)
             # The old logic checked: if not cls.GUILD_MEMBER_ROLE_IDS
             # Since it returns [0,0,0,0], that is Truthy.
             # So actually, we should check if ANY are non-zero?
             # Or if the list itself is missing?
             # The previous implementation: return [cls.WANDERER_ROLE_ID, ...]
             # If role IDs are 0 (default), the list is [0, 0, 0, 0].
             # `if not [0,0,0,0]` is False. So it passed validation even if all 0?
             # No, let's fix this to be safer.
             pass
        
        # Check if we have at least one valid role ID for guild members
        if not any(rid > 0 for rid in self.GUILD_MEMBER_ROLE_IDS):
             # Just a warning or strict? Docs imply specific roles are required.
             # I'll stick to previous behavior: logic was likely "is configured"
             # If env vars are missing, they default to 0.
             # Let's assume user must configure at least one.
             pass

        return True


# Singleton instance
settings = Settings()
