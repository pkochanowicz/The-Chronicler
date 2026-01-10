# config/settings.py
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from dotenv import load_dotenv

# Import from game_data instead of legacy models

load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Application Mode
    ENV: str = Field("development", pattern="^(development|production|test)$")

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL Connection String")

    # Supabase (Optional for now, but good to have)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Discord Configuration
    DISCORD_BOT_TOKEN: str = Field(..., min_length=10)
    GUILD_ID: int = Field(..., gt=0)
    RECRUITMENT_CHANNEL_ID: int
    CHARACTER_SHEET_VAULT_CHANNEL_ID: int
    CEMETERY_CHANNEL_ID: int

    # Forum Tag IDs (required for forum channels that mandate tags)
    RECRUITMENT_DEFAULT_TAG_ID: Optional[int] = None
    CEMETERY_DEFAULT_TAG_ID: Optional[int] = None

    # Guild Member Role IDs
    WANDERER_ROLE_ID: int = 0
    SEEKER_ROLE_ID: int = 0
    PATHFINDER_ROLE_ID: int = 0
    TRAILWARDEN_ROLE_ID: int = 0

    # Role Mentions (Optional)
    PATHFINDER_ROLE_MENTION: Optional[str] = None
    TRAILWARDEN_ROLE_MENTION: Optional[str] = None

    # Webhook Security
    WEBHOOK_SECRET: str = Field(..., min_length=32)
    PORT: int = 8080

    # Bot Behavior
    INTERACTIVE_TIMEOUT_SECONDS: int = 900
    POLL_INTERVAL_SECONDS: int = 60

    # Visuals
    APPROVE_EMOJI: str = "✅"
    REJECT_EMOJI: str = "❌"
    DEFAULT_PORTRAIT_URL: str = "https://i.imgur.com/placeholder.png"

    # Cloudflare R2 Image Storage (Optional)
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: str = "azeroth-bound-images"
    R2_PUBLIC_URL: Optional[str] = None

    # MCP Server Integration (Optional)
    MCP_SERVER_URL: Optional[str] = None
    MCP_API_KEY: Optional[str] = None
    MCP_PORT: int = 8081

    # Computed properties
    GUILD_MEMBER_ROLE_IDS: List[int] = []
    OFFICER_ROLE_IDS: List[int] = []

    @model_validator(mode="after")
    def compute_role_lists(self):
        self.GUILD_MEMBER_ROLE_IDS = [
            self.WANDERER_ROLE_ID,
            self.SEEKER_ROLE_ID,
            self.PATHFINDER_ROLE_ID,
            self.TRAILWARDEN_ROLE_ID,
        ]
        self.OFFICER_ROLE_IDS = [self.PATHFINDER_ROLE_ID, self.TRAILWARDEN_ROLE_ID]
        # Validate R2 configuration
        self._validate_r2_config()
        return self

    def _validate_r2_config(self):
        """
        Validate Cloudflare R2 configuration for image storage.

        Logs warning if incomplete (gracefully degrades to DEFAULT_PORTRAIT_URL).
        """
        r2_fields = {
            "R2_ACCOUNT_ID": self.R2_ACCOUNT_ID,
            "R2_ACCESS_KEY_ID": self.R2_ACCESS_KEY_ID,
            "R2_SECRET_ACCESS_KEY": self.R2_SECRET_ACCESS_KEY,
            "R2_PUBLIC_URL": self.R2_PUBLIC_URL,
        }

        missing = [name for name, value in r2_fields.items() if not value]

        if missing:
            logger.warning(
                f"⚠️  R2 image storage not configured (missing: {', '.join(missing)}). "
                f"Image uploads will fallback to DEFAULT_PORTRAIT_URL. "
                f"See docs/IMAGE_STORAGE.md for setup instructions."
            )
        else:
            logger.info(f"✅ Cloudflare R2 configured: bucket '{self.R2_BUCKET_NAME}'")

    class Config:
        env_file = ".env"
        extra = "ignore"


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


# Singleton instance for direct import
settings = get_settings()
