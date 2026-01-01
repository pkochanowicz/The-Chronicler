import pytest
import pytest_asyncio
import os
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from alembic.config import Config

# We need a fixture that provides an EMPTY database on the test container
# The existing 'postgres_container' fixture in conftest.py yields a container.
# We can use that.


@pytest_asyncio.fixture(scope="function")
async def empty_db_connection_string(postgres_container):
    """
    Returns a connection string to a FRESH, EMPTY database on the container.
    It does this by creating a new random database for each test function.
    """
    # Connect to the default 'postgres' db to create a new one
    root_url = postgres_container.get_connection_url().replace("psycopg2", "asyncpg")
    root_engine = create_async_engine(root_url, isolation_level="AUTOCOMMIT")

    import uuid

    new_db_name = f"testdb_{uuid.uuid4().hex}"

    async with root_engine.connect() as conn:
        await conn.execute(text(f"CREATE DATABASE {new_db_name}"))

    await root_engine.dispose()

    # Construct the URL for the new DB
    base_url = root_url.rsplit("/", 1)[0]
    return f"{base_url}/{new_db_name}"


@pytest.mark.asyncio
async def test_alembic_upgrade_head_creates_schema(empty_db_connection_string):
    """
    Verifies that running 'alembic upgrade head' against an empty database
    successfully creates all the tables defined in our schema plan.
    """
    # 1. Set the DATABASE_URL env var to our fresh empty DB
    os.environ["DATABASE_URL"] = empty_db_connection_string

    # 2. Configure Alembic
    # We need to point to alembic.ini. It is in the root.
    alembic_cfg = Config("alembic.ini")

    # Override the sqlalchemy.url in the config object just to be safe,
    # though env.py should pick up os.environ["DATABASE_URL"]
    alembic_cfg.set_main_option("sqlalchemy.url", empty_db_connection_string)

    # 3. Run Upgrade Head (Synchronous command, but runs async migrations internally via env.py)
    # Alembic commands are blocking.
    # We run this in a thread executor to avoid blocking the async test loop if needed,
    # but for this test, simple call is fine as long as env.py handles the async loop correctly.
    # Wait, env.py uses asyncio.run(). If we are already in a loop (pytest-asyncio), this will fail!
    # "RuntimeError: asyncio.run() cannot be called from a running event loop"

    # To fix this, we need to subprocess it OR use a non-asyncio.run env.py for tests.
    # Or simpler: Just run the shell command!

    import subprocess
    import sys

    # Run alembic using the current python interpreter to ensure we use the venv
    cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]

    # We must pass the env vars to the subprocess
    env = os.environ.copy()
    env["DATABASE_URL"] = empty_db_connection_string

    # Run alembic
    process = subprocess.run(cmd, env=env, capture_output=True, text=True)

    assert (
        process.returncode == 0
    ), f"Alembic upgrade failed:\nSTDOUT: {process.stdout}\nSTDERR: {process.stderr}"

    # 4. Verify Tables Exist using SQLAlchemy inspection
    engine = create_async_engine(empty_db_connection_string)
    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )

        # Check against _SCHEMA_IMPLEMENTATION_PLAN.md expectations
        expected_tables = [
            "characters",
            "character_talents",
            "graveyard",
            "talents",
            "talent_trees",
            "items",
            "item_sets",
            "npcs",
            "quests",
            "spells",
            "factions",
            "images",
            "alembic_version",  # Alembic's own table
        ]

        missing = [t for t in expected_tables if t not in tables]
        assert not missing, f"Tables missing after migration: {missing}"

        # 5. Idempotency Check (Run it again!)
        process_2 = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert (
            process_2.returncode == 0
        ), "Idempotency check failed: Running upgrade head twice should be safe."

    await engine.dispose()
