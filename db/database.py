# db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
import asyncpg  # Explicitly import asyncpg
from typing import Optional
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine: Optional[AsyncEngine] = None
_AsyncSessionLocal: Optional[sessionmaker] = None

def get_engine_and_session_maker():
    from config.settings import get_settings  # Import get_settings here
    settings = get_settings()  # Get settings instance
    global _engine, _AsyncSessionLocal
    if _engine is None or _AsyncSessionLocal is None:
        # Ensure the DATABASE_URL uses the asyncpg driver
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        _engine = create_async_engine(db_url, echo=False)
        _AsyncSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _engine, _AsyncSessionLocal

async def get_db():
    engine, AsyncSessionLocal = get_engine_and_session_maker()
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """
    Initializes the database schema.
    In production, this should be handled by Alembic migrations.
    For local development/testing, it creates tables based on models.
    """
    logger.info("Initializing database schema...")
    logger.warning("Using Base.metadata.create_all for schema initialization. Use Alembic for production migrations.")
    engine, _ = get_engine_and_session_maker()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized.")
