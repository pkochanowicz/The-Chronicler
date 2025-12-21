from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DISCORD_TOKEN: str
    WEBHOOK_SECRET: str

    # Discord Configuration
    GUILD_ID: int
    RECRUITMENT_CHANNEL_ID: int
    CHARACTER_SHEET_VAULT_CHANNEL_ID: int # New name
    CEMETERY_CHANNEL_ID: int

    # Guild Member Role IDs
    WANDERER_ROLE_ID: int
    SEEKER_ROLE_ID: int
    PATHFINDER_ROLE_ID: int
    TRAILWARDEN_ROLE_ID: int

    # Officer Role Mentions
    PATHFINDER_ROLE_MENTION: str
    TRAILWARDEN_ROLE_MENTION: str

    # Bot Behavior
    INTERACTIVE_TIMEOUT_SECONDS: int = 300
    DEFAULT_PORTRAIT_URL: str = "https://i.imgur.com/default_placeholder.png"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()