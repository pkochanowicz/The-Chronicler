import asyncio

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv  # Import load_dotenv

load_dotenv()  # Load .env file

from alembic import context  # noqa: E402

# Import our project's Base for autogenerate support
from db.database import Base  # noqa: E402

# Import all db_schemas models to ensure Base.metadata discovers them
import schemas.db_schemas  # noqa

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# ...


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations_online() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    import os

    # Store original environment variables to restore them later
    original_env_vars = {
        key: os.environ.get(key)
        for key in [
            "DISCORD_BOT_TOKEN",
            "SUPABASE_URL",
            "SUPABASE_KEY",
            "WEBHOOK_SECRET",
            "GUILD_ID",
            "RECRUITMENT_CHANNEL_ID",
            "CHARACTER_SHEET_VAULT_CHANNEL_ID",
            "CEMETERY_CHANNEL_ID",
            "WANDERER_ROLE_ID",
            "SEEKER_ROLE_ID",
            "PATHFINDER_ROLE_ID",
            "TRAILWARDEN_ROLE_ID",
            "DATABASE_URL",
        ]
    }

    try:
        # Set dummy values for all required Pydantic settings fields if they are missing
        os.environ.setdefault("DISCORD_BOT_TOKEN", "dummy_token_alembic")
        os.environ.setdefault("SUPABASE_URL", "http://dummy.url")
        os.environ.setdefault("SUPABASE_KEY", "dummy_key")
        os.environ.setdefault(
            "WEBHOOK_SECRET", "dummy_secret_for_alembic_at_least_32_chars_long"
        )
        os.environ.setdefault("GUILD_ID", "1")
        os.environ.setdefault("RECRUITMENT_CHANNEL_ID", "2")
        os.environ.setdefault("CHARACTER_SHEET_VAULT_CHANNEL_ID", "3")
        os.environ.setdefault("CEMETERY_CHANNEL_ID", "4")
        os.environ.setdefault("WANDERER_ROLE_ID", "5")
        os.environ.setdefault("SEEKER_ROLE_ID", "6")
        os.environ.setdefault("PATHFINDER_ROLE_ID", "7")
        os.environ.setdefault("TRAILWARDEN_ROLE_ID", "8")
        os.environ.setdefault(
            "DATABASE_URL",
            "postgresql+asyncpg://user:password@localhost:5432/alembic_dummy_db",
        )  # This URL will be overridden by the actual settings.DATABASE_URL later

        # Now load the settings (it should succeed with dummy values if needed)
        from config.settings import get_settings

        settings = get_settings()
        print(
            f"DEBUG: Alembic using DATABASE_URL from settings: {settings.DATABASE_URL}"
        )  # Debug print

        # Dynamically set the database URL from settings
        # Ensure +asyncpg driver is used for online migrations
        config.set_main_option(
            "sqlalchemy.url",
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        )

        connectable = create_async_engine(
            url=config.get_main_option("sqlalchemy.url"),
            echo=config.get_main_option("sqlalchemy.echo", "False").lower() == "true",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()
    finally:
        # Restore original environment variables
        for key, value in original_env_vars.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations_online())


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # For autogenerate in offline mode, we don't need to connect to a real DB
    # We compare Base.metadata to target_metadata=None (which represents an empty DB)
    url = config.get_main_option("sqlalchemy.url")  # This can be a dummy URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
