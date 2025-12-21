from typing import List, Dict, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator

class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DISCORD_BOT_TOKEN: str = Field(..., min_length=1)
    WEBHOOK_SECRET: str = Field(..., min_length=32)

    # Discord Configuration
    GUILD_ID: int = Field(..., gt=0)
    RECRUITMENT_CHANNEL_ID: int
    FORUM_CHANNEL_ID: int # Was CHARACTER_SHEET_VAULT_CHANNEL_ID in prev version, reverting to match tests/legacy for now, or updating tests?
    # Test expects FORUM_CHANNEL_ID. Architecture says #character_sheet_vault. 
    # Let's keep FORUM_CHANNEL_ID as the variable name for the ID of that channel.
    CEMETERY_CHANNEL_ID: int

    # Guild Member Role IDs
    WANDERER_ROLE_ID: int
    SEEKER_ROLE_ID: int
    PATHFINDER_ROLE_ID: int
    TRAILWARDEN_ROLE_ID: int

    # Officer Role Mentions
    PATHFINDER_ROLE_MENTION: str = "<@&PATHFINDER_ID>" # Default placeholders if not in env?
    TRAILWARDEN_ROLE_MENTION: str = "<@&TRAILWARDEN_ID>"

    # Bot Behavior
    INTERACTIVE_TIMEOUT_SECONDS: int = 300
    POLL_INTERVAL_SECONDS: int = 60
    DEFAULT_PORTRAIT_URL: str = "https://i.imgur.com/default_placeholder.png"
    
    # Constants
    APPROVE_EMOJI: str = "✅"
    REJECT_EMOJI: str = "❌"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def GUILD_MEMBER_ROLE_IDS(self) -> List[int]:
        return [
            self.WANDERER_ROLE_ID,
            self.SEEKER_ROLE_ID,
            self.PATHFINDER_ROLE_ID,
            self.TRAILWARDEN_ROLE_ID
        ]

    @property
    def LIFECYCLE_ROLE_IDS(self) -> List[int]:
        return [
            self.PATHFINDER_ROLE_ID,
            self.TRAILWARDEN_ROLE_ID
        ]
    
    @property
    def OFFICER_ROLE_IDS(self) -> List[int]:
         # In v1 logic, officers were Pathfinders + Trailwardens
         return self.LIFECYCLE_ROLE_IDS

    @property
    def CLASS_EMOJIS(self) -> Dict[str, str]:
        from domain.models import CLASS_DATA
        return {k: v.emoji for k, v in CLASS_DATA.items()}

    @model_validator(mode='after')
    def check_guild_member_roles(self) -> 'Settings':
        """
        Custom validation to ensure at least one guild member role is configured.
        Runs after all fields are validated.
        """
        if all(r == 0 for r in self.GUILD_MEMBER_ROLE_IDS):
             raise ValueError("At least one Guild Member Role ID must be configured.")
        return self

settings = Settings()
