import pytest
import asyncio
import httpx
import os
from unittest.mock import MagicMock, AsyncMock
import sys 
import pytest_asyncio 

# --- Set environment variables for Pydantic Settings IMMEDIATELY for collection phase ---
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:password@localhost:5432/testdb"
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_supabase_key"
os.environ["DISCORD_BOT_TOKEN"] = "mock_discord_bot_token_long_enough" 
os.environ["WEBHOOK_SECRET"] = "a_very_long_mock_secret_for_testing_purposes"
os.environ["GUILD_ID"] = "12345"
os.environ["RECRUITMENT_CHANNEL_ID"] = "67890"
os.environ["FORUM_CHANNEL_ID"] = "11223"
os.environ["CEMETERY_CHANNEL_ID"] = "44556"
os.environ["WANDERER_ROLE_ID"] = "100"
os.environ["SEEKER_ROLE_ID"] = "200"
os.environ["PATHFINDER_ROLE_ID"] = "300"
os.environ["TRAILWARDEN_ROLE_ID"] = "400"
os.environ["INTERACTIVE_TIMEOUT_SECONDS"] = "10"
os.environ["POLL_INTERVAL_SECONDS"] = "5"
os.environ["DEFAULT_PORTRAIT_URL"] = "https://mock.url/portrait.png"
os.environ["PATHFINDER_ROLE_MENTION"] = "<@&300>"
os.environ["TRAILWARDEN_ROLE_MENTION"] = "<@&400>"
os.environ["CHARACTER_SHEET_VAULT_CHANNEL_ID"] = "99887"

import config.settings 
from main import app 

@pytest.fixture(scope="session", autouse=True)
def set_pydantic_settings_env_vars():
    original_env = {key: os.environ.get(key) for key in [
        "DATABASE_URL", "SUPABASE_URL", "SUPABASE_KEY", "DISCORD_BOT_TOKEN", "WEBHOOK_SECRET",
        "GUILD_ID", "RECRUITMENT_CHANNEL_ID", "FORUM_CHANNEL_ID", "CEMETERY_CHANNEL_ID",
        "WANDERER_ROLE_ID", "SEEKER_ROLE_ID", "PATHFINDER_ROLE_ID", "TRAILWARDEN_ROLE_ID",
        "INTERACTIVE_TIMEOUT_SECONDS", "POLL_INTERVAL_SECONDS", "DEFAULT_PORTRAIT_URL",
        "PATHFINDER_ROLE_MENTION", "TRAILWARDEN_ROLE_MENTION", "CHARACTER_SHEET_VAULT_CHANNEL_ID"
    ]}
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:password@localhost:5432/testdb"
    yield
    for key, value in original_env.items():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
def postgres_container():
    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:
        pytest_asyncio.skip("testcontainers not installed", allow_module_level=True)
    try:
        postgres = PostgresContainer("postgres:15", driver="asyncpg")
        postgres.start()
        db_url = postgres.get_connection_url().replace("psycopg2", "asyncpg")
        os.environ["DATABASE_URL"] = db_url 
        yield postgres
    finally:
        postgres.stop()

@pytest_asyncio.fixture(scope="session")
async def initialized_test_db_engine(postgres_container):
    from sqlalchemy.ext.asyncio import create_async_engine
    
    settings = config.settings.get_settings() 
    settings.DATABASE_URL = os.environ["DATABASE_URL"] 
    
    import db.database
    db.database._engine = create_async_engine(settings.DATABASE_URL, echo=False)
    db.database._AsyncSessionLocal = None 
    
    from schemas.db_schemas import Base
    import schemas.db_schemas
    
    engine = db.database._engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 
        await conn.run_sync(Base.metadata.create_all) 
        
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(initialized_test_db_engine):
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(
        initialized_test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(scope="session")
async def empty_test_db_engine(postgres_container):
    from sqlalchemy.ext.asyncio import create_async_engine
    settings = config.settings.get_settings() 
    settings.DATABASE_URL = os.environ["DATABASE_URL"]
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()

@pytest.fixture
def mock_settings():
    mock = MagicMock()
    mock.WEBHOOK_SECRET = "test_secret_123_longer_than_32_chars"
    mock.DISCORD_BOT_TOKEN = "mock_discord_bot_token_long_enough"
    mock.RECRUITMENT_CHANNEL_ID = 67890
    mock.CEMETERY_CHANNEL_ID = 44556
    mock.PATHFINDER_ROLE_ID = 300
    mock.TRAILWARDEN_ROLE_ID = 400
    mock.GUILD_MEMBER_ROLE_IDS = [100, 200, 300, 400]
    mock.OFFICER_ROLE_IDS = [300, 400]
    mock.PATHFINDER_ROLE_MENTION = "<@&300>"
    mock.TRAILWARDEN_ROLE_MENTION = "<@&400>"
    mock.APPROVE_EMOJI = "✅"
    mock.REJECT_EMOJI = "❌"
    mock.PORT = 8080
    mock.DEFAULT_PORTRAIT_URL = "https://mock.url/portrait.png"
    mock.INTERACTIVE_TIMEOUT_SECONDS = 10
    mock.POLL_INTERVAL_SECONDS = 5
    mock.CHARACTER_SHEET_VAULT_CHANNEL_ID = 99887
    return mock

@pytest.fixture
def mock_interaction():
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.response = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.user = MagicMock(spec=discord.User)
    interaction.user.id = 123456789
    interaction.user.name = "TestUser"
    interaction.user.display_name = "Test User"
    interaction.guild = MagicMock(spec=discord.Guild)
    interaction.guild.id = 987654321
    interaction.channel = MagicMock(spec=discord.TextChannel)
    interaction.channel.id = 555555555
    interaction.client = AsyncMock()
    return interaction

@pytest.fixture
def mock_discord_context():
    ctx = AsyncMock()
    ctx.author.id = 123456789
    ctx.author.name = "TestUser"
    ctx.send = AsyncMock()
    return ctx

from fastapi.testclient import TestClient
import discord
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="session")
def client(initialized_test_db_engine):
    return TestClient(app)

@pytest_asyncio.fixture(scope="session")
async def async_client(initialized_test_db_engine):
    """Async Client for testing FastAPI endpoints without blocking loops."""
    # Use ASGITransport to test the app directly without a running server, but in async context
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c