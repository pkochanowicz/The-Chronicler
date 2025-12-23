import pytest_asyncio # Added for explicit async fixture decorator
import pytest
from sqlalchemy import inspect, text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.exc import ProgrammingError, OperationalError
from db.database import Base # Ensure Base is imported for metadata access

@pytest_asyncio.fixture(scope="function")
async def empty_sqlite_db_engine():
    """
    Provides an async SQLAlchemy engine connected to an in-memory SQLite database.
    No tables are created by default, making it suitable for testing table absence.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    yield engine
    await engine.dispose()

@pytest.mark.asyncio
async def test_tables_do_not_exist_in_empty_db(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that no tables are present in an empty database.
    This test is expected to pass when no schema has been applied.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        table_names = await connection.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    assert len(table_names) == 0, f"Expected 0 tables, but found: {table_names}"

@pytest.mark.asyncio
async def test_character_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'characters' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        # SQLite raises OperationalError for missing tables, not ProgrammingError
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo: # Using ProgrammingError for broad compatibility
            await connection.execute(text("SELECT 1 FROM characters"))
        
        # Check for a specific error message indicating table absence
        assert "no such table: characters" in str(excinfo.value) or "relation \"characters\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_talents_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'talents' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM talents"))
        assert "no such table: talents" in str(excinfo.value) or "relation \"talents\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_talent_trees_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'talent_trees' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM talent_trees"))
        assert "no such table: talent_trees" in str(excinfo.value) or "relation \"talent_trees\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_items_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'items' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM items"))
        assert "no such table: items" in str(excinfo.value) or "relation \"items\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_item_sets_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'item_sets' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM item_sets"))
        assert "no such table: item_sets" in str(excinfo.value) or "relation \"item_sets\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_npcs_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'npcs' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM npcs"))
        assert "no such table: npcs" in str(excinfo.value) or "relation \"npcs\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_quests_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'quests' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM quests"))
        assert "no such table: quests" in str(excinfo.value) or "relation \"quests\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_spells_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'spells' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM spells"))
        assert "no such table: spells" in str(excinfo.value) or "relation \"spells\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_factions_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'factions' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM factions"))
        assert "no such table: factions" in str(excinfo.value) or "relation \"factions\" does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_images_table_is_initially_missing(empty_sqlite_db_engine: AsyncEngine):
    """
    Tests that the 'images' table is missing in an empty database.
    This test is expected to FAIL initially, as the schema has not been applied yet.
    """
    async with empty_sqlite_db_engine.connect() as connection:
        with pytest.raises((ProgrammingError, OperationalError)) as excinfo:
            await connection.execute(text("SELECT 1 FROM images"))
        assert "no such table: images" in str(excinfo.value) or "relation \"images\" does not exist" in str(excinfo.value)
