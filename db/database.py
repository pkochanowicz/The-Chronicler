from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings
from typing import Optional

Base = declarative_base()

_engine: Optional[AsyncEngine] = None
_AsyncSessionLocal: Optional[sessionmaker] = None

def get_engine_and_session_maker():
    global _engine, _AsyncSessionLocal
    if _engine is None or _AsyncSessionLocal is None:
        _engine = create_async_engine(settings.DATABASE_URL, echo=True)
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
    engine, _ = get_engine_and_session_maker()
    async with engine.begin() as conn:
        # Import all models here that might be needed to create tables
        from schemas import db_schemas # Import models so Base.metadata knows about them
        await conn.run_sync(Base.metadata.create_all)