import pytest
import asyncio
import httpx
import os
from unittest.mock import MagicMock, AsyncMock
import sys 
import pytest_asyncio 

# --- Set environment variables for Pydantic Settings IMMEDIATELY for collection phase ---
# This prevents Pydantic validation errors when modules are imported during pytest collection
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:password@localhost:5432/testdb"
os.environ["SUPABASE_URL"] = "https://mock.supabase.co"
os.environ["SUPABASE_KEY"] = "mock_supabase_key"
os.environ["DISCORD_BOT_TOKEN"] = "mock_discord_bot_token"
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

# --- Set environment variables for Pydantic Settings using os.environ directly for session scope ---
@pytest.fixture(scope="session", autouse=True)
def set_pydantic_settings_env_vars():
    # Store original env vars to restore them later
    original_env = {key: os.environ.get(key) for key in [
        "DATABASE_URL", "SUPABASE_URL", "SUPABASE_KEY", "DISCORD_BOT_TOKEN", "WEBHOOK_SECRET",
        "GUILD_ID", "RECRUITMENT_CHANNEL_ID", "FORUM_CHANNEL_ID", "CEMETERY_CHANNEL_ID",
        "WANDERER_ROLE_ID", "SEEKER_ROLE_ID", "PATHFINDER_ROLE_ID", "TRAILWARDEN_ROLE_ID",
        "INTERACTIVE_TIMEOUT_SECONDS", "POLL_INTERVAL_SECONDS", "DEFAULT_PORTRAIT_URL",
        "PATHFINDER_ROLE_MENTION", "TRAILWARDEN_ROLE_MENTION", "CHARACTER_SHEET_VAULT_CHANNEL_ID"
    ]}

    # Set mock environment variables (Redundant but safe for fixture lifecycle)
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:password@localhost:5432/testdb"
    # ... (rest are already set above, but fixture ensures cleanup)
    
    yield
    
    # Restore original environment variables
    for key, value in original_env.items():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value

# from main import app # Import the FastAPI app - Commented out as not needed for schema tests

# --- Integration Tests: Database Fixtures ---
# We use Testcontainers to spin up a real Postgres DB for integration tests.
# This ensures we are not mocking the DB driver, but testing real SQL.


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
def postgres_container():
    """
    Spins up a Postgres container for integration tests.
    Requires Docker to be running.
    """
    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:
        pytest_asyncio.skip("testcontainers not installed", allow_module_level=True)
        
    try:
        # Use a fixed version to ensure stability
        postgres = PostgresContainer("postgres:15-alpine")
        postgres.start()
        
        # Override the DATABASE_URL setting to point to the test container
        # Note: We need to use the async driver (postgresql+asyncpg)
        db_url = postgres.get_connection_url().replace("psycopg2", "asyncpg")
        # Temporarily set the DATABASE_URL for the current test run
        os.environ["DATABASE_URL"] = db_url # Override for get_settings() to pick up
        
        yield postgres
        
    finally: # Added finally block
        postgres.stop()

@pytest_asyncio.fixture(scope="session")
async def empty_test_db_engine(postgres_container):
    """
    Creates an async SQLAlchemy engine connected to the test container,
    without creating any tables. This is for schema tests that expect an empty DB.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    settings = config.settings.get_settings() # Updated usage
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def initialized_test_db_engine(postgres_container):
    """Creates an async SQLAlchemy engine connected to the test container and initializes the schema."""
    from sqlalchemy.ext.asyncio import create_async_engine
    
    # Get settings after DB container is up and env var is set
    print(f"DEBUG: DISCORD_BOT_TOKEN from os.environ: {os.environ.get('DISCORD_BOT_TOKEN')}") # Debug print
    settings = config.settings.get_settings() # Updated usage
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Initialize Schema (create tables)
    from db.database import Base
    # Explicitly import all models to ensure they are registered with Base.metadata
    from schemas.db_schemas import (
        Character, CharacterTalent, Graveyard, Talent, TalentTree, Item, ItemSet, Npc, Quest, Spell, Faction, Image,
        ItemQualityEnum, CharacterRaceEnum, CharacterClassEnum, CharacterRoleEnum, CharacterStatusEnum,
        CreatureTypeEnum, SpellSchoolEnum, FactionAlignmentEnum, QuestTypeEnum
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Drop existing tables
        print(f"DEBUG: Base.metadata.sorted_tables BEFORE create_all: {[table.name for table in Base.metadata.sorted_tables]}")
        
        # Debugging DDL generation
        from sqlalchemy.schema import CreateTable
        for table in Base.metadata.sorted_tables:
            print(f"DEBUG: DDL for {table.name}:\n{CreateTable(table).compile(engine)}")
        
        await conn.run_sync(Base.metadata.create_all) # Create fresh tables
        
    yield engine
    
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(initialized_test_db_engine):
    """Provides a fresh async session for each test."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(
        initialized_test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        # Rollback after each test to keep DB clean
        await session.rollback()

@pytest.fixture
def mock_complete_character_data():
    """Fixture providing complete character data for registration."""
    return {
        "discord_id": "123456789",
        "discord_name": "TestUser#1234",
        "char_name": "Thorgar Ironforge",
        "race": "Dwarf",
        "class": "Warrior",
        "roles": "Tank, Melee DPS",
        "professions": "Mining, Blacksmithing",
        "backstory": "Born in the depths of Ironforge, Thorgar learned the ways of war...",
        "personality": "Stoic, Loyal, Fearless",
        "quotes": "For Khaz Modan!|No dwarf left behind!",
        "portrait_url": "https://example.com/thorgar.png",
        "trait_1": "Stoic",
        "trait_2": "Loyal",
        "trait_3": "Fearless",
        "status": "PENDING",
        "confirmation": True,
        "request_sdxl": False
    }

# --- Mock Fixtures for Unit/API Tests ---

@pytest.fixture
def mock_discord_interaction():
    """Mocks a Discord Interaction object."""
    interaction = MagicMock()
    interaction.response = MagicMock()
    interaction.followup = MagicMock()
    interaction.user.id = 123456789
    interaction.user.display_name = "TestUser"
    return interaction

@pytest.fixture
def mock_settings():
    """Mocks a Settings object for webhook testing."""
    mock = MagicMock()
    # It's important that this secret matches the one used in the test_webhooks.py
    mock.WEBHOOK_SECRET = "test_secret_123"
    mock.DISCORD_BOT_TOKEN = "mock_discord_bot_token" # Added
    return mock

@pytest.fixture(autouse=True)
def mock_global_settings(monkeypatch, mock_settings):
    """
    Monkeypatches the global get_settings() function in config.settings
    with a mock version for tests.
    """
    monkeypatch.setattr(config.settings, "get_settings", lambda: mock_settings)

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from uuid import uuid4 # Import uuid4

@pytest.fixture(autouse=True)
def mock_create_async_engine(monkeypatch):
    """
    Mocks create_async_engine to return a MagicMock that behaves like an AsyncEngine.
    This prevents actual database connection attempts during engine creation for tests
    that don't explicitly rely on the postgres_container fixture.
    """
    mock_engine = MagicMock(spec=AsyncEngine)
    # Mock the begin() method to return an async context manager
    mock_connection = MagicMock()
    mock_connection.__aenter__.return_value = MagicMock()
    mock_connection.__aexit__.return_value = None
    mock_engine.begin.return_value = mock_connection
    
    # Mock run_sync needed for Base.metadata.create_all
    mock_connection.__aenter__.return_value.run_sync = AsyncMock()

    monkeypatch.setattr(
        "db.database.create_async_engine",
        lambda *args, **kwargs: mock_engine
    )

    # --- Mock AsyncSessionLocal to simulate ID generation on commit ---
    mock_session_instance = MagicMock(spec=AsyncSession)
    
    # Mock add method: store added objects in a list
    mock_session_instance.added_objects = []
    def mock_add(obj):
        mock_session_instance.added_objects.append(obj)
    mock_session_instance.add.side_effect = mock_add

    # Mock commit method: assign UUID and timestamps to objects that need it
    async def mock_commit():
        from datetime import datetime, timezone
        for obj in mock_session_instance.added_objects:
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = uuid4() # Simulate UUID generation
            if hasattr(obj, 'created_at') and obj.created_at is None:
                obj.created_at = datetime.now(timezone.utc)
            if hasattr(obj, 'updated_at') and obj.updated_at is None:
                obj.updated_at = datetime.now(timezone.utc)
        mock_session_instance.added_objects.clear() # Clear added objects after commit
    mock_session_instance.commit.side_effect = mock_commit

    # Mock refresh method: ensure ID and timestamps are present
    async def mock_refresh(obj):
        from datetime import datetime, timezone
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = uuid4()
        if hasattr(obj, 'created_at') and obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)
        if hasattr(obj, 'updated_at') and obj.updated_at is None:
            obj.updated_at = datetime.now(timezone.utc)
    mock_session_instance.refresh.side_effect = mock_refresh
    
    # Mock AsyncSessionLocal to return our mocked session instance
    mock_session_maker = MagicMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session_instance
    mock_session_maker.return_value.__aexit__.return_value = None

    monkeypatch.setattr("db.database._AsyncSessionLocal", mock_session_maker)
    # Also patch the get_engine_and_session_maker to return our mocks
    monkeypatch.setattr(
        "db.database.get_engine_and_session_maker",
        lambda: (mock_engine, mock_session_maker)
    )

@pytest.fixture(scope="session")
def client():
    """Synchronous TestClient for testing FastAPI endpoints."""
    return TestClient(app)