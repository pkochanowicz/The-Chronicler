# config/settings.py
import os
import base64
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
from dotenv import load_dotenv

# Import from game_data instead of legacy models
from domain.game_data import CLASS_DATA

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
    INTERACTIVE_TIMEOUT_SECONDS: int = 300
    POLL_INTERVAL_SECONDS: int = 60
    
    # Visuals
    APPROVE_EMOJI: str = "✅"
    REJECT_EMOJI: str = "❌"
    DEFAULT_PORTRAIT_URL: str = "https://i.imgur.com/placeholder.png"

    # Computed properties
    GUILD_MEMBER_ROLE_IDS: List[int] = []
    OFFICER_ROLE_IDS: List[int] = []

    @model_validator(mode='after')
    def compute_role_lists(self):
        self.GUILD_MEMBER_ROLE_IDS = [
            self.WANDERER_ROLE_ID, 
            self.SEEKER_ROLE_ID, 
            self.PATHFINDER_ROLE_ID, 
            self.TRAILWARDEN_ROLE_ID
        ]
        self.OFFICER_ROLE_IDS = [
            self.PATHFINDER_ROLE_ID, 
            self.TRAILWARDEN_ROLE_ID
        ]
        return self



    class Config:
        env_file = ".env"
        extra = "ignore"

_settings_instance: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance