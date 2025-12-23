# db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_AsyncSessionLocal = None

def get_engine_and_session_maker():
    global _engine, _AsyncSessionLocal
    if _engine is None:
        settings = get_settings()
        # Use asyncpg driver
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        _engine = create_async_engine(db_url, echo=False)
        _AsyncSessionLocal = sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
    return _engine, _AsyncSessionLocal

async def get_db():
    _, session_maker = get_engine_and_session_maker()
    async with session_maker() as session:
        yield session

async def init_db():
    """
    Initializes the database. In production, use Alembic.
    This is mostly for local dev/testing quick start.
    """
    engine, _ = get_engine_and_session_maker()
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        import schemas.db_schemas 
        await conn.run_sync(Base.metadata.create_all)
