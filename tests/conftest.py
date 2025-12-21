import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import Base, get_db, get_engine_and_session_maker
from main import app
from fastapi.testclient import TestClient
from config.settings import settings # Import settings

# Use a separate test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_chronicler"

# This fixture will ensure the settings are configured for the test database
@pytest.fixture(scope="session", autouse=True)
def override_settings_for_tests():
    # Patch the settings to use the test database URL
    # This is important for db.database.get_engine_and_session_maker()
    # to pick up the correct URL
    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = TEST_DATABASE_URL
    
    # Also ensure other dummy settings are present for validation to pass
    original_supabase_url = settings.SUPABASE_URL
    original_supabase_key = settings.SUPABASE_KEY
    original_discord_token = settings.DISCORD_TOKEN
    original_webhook_secret = settings.WEBHOOK_SECRET

    settings.SUPABASE_URL = "http://test-supabase.co"
    settings.SUPABASE_KEY = "test-key"
    settings.DISCORD_TOKEN = "test-discord-token"
    settings.WEBHOOK_SECRET = "a_very_long_test_secret_for_webhook_validation_32_chars"

    yield

    # Restore original settings after tests
    settings.DATABASE_URL = original_db_url
    settings.SUPABASE_URL = original_supabase_url
    settings.SUPABASE_KEY = original_supabase_key
    settings.DISCORD_TOKEN = original_discord_token
    settings.WEBHOOK_SECRET = original_webhook_secret


async def override_get_db_for_tests() -> AsyncGenerator[AsyncSession, None]:
    _, TestAsyncSessionLocal = get_engine_and_session_maker()
    async with TestAsyncSessionLocal() as session:
        yield session

# Override the app's get_db dependency to use the test database
app.dependency_overrides[get_db] = override_get_db_for_tests


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db(override_settings_for_tests): # Depend on settings fixture
    """Sets up and tears down the test database."""
    # Ensure Base.metadata knows about all models
    from schemas import db_schemas # noqa # pylint: disable=unused-import
    
    engine, _ = get_engine_and_session_maker()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def async_session(override_settings_for_tests) -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional scope for each test."""
    _, TestAsyncSessionLocal = get_engine_and_session_maker()
    async with TestAsyncSessionLocal() as session:
        await session.begin()  # Start a transaction
        yield session
        await session.rollback() # Rollback after each test

@pytest.fixture(scope="function")
def client() -> TestClient:
    """Provides a TestClient for FastAPI."""
    # No need to override settings again, autouse fixture handles it
    with TestClient(app) as c:
        yield c
