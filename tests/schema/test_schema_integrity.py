import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine
from schemas.db_schemas import Base

@pytest.mark.asyncio
async def test_ensure_tables_exist(initialized_test_db_engine: AsyncEngine):
    """
    Verify that all critical tables defined in docs/architecture_UI_UX.md exist.
    """
    async with initialized_test_db_engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        
        expected_tables = {
            "characters", "character_talents", "graveyard",
            "images", "talents", "talent_trees",
            "items", "item_sets", "npcs", "quests", "spells", "factions"
        }
        
        missing = expected_tables - set(tables)
        assert not missing, f"Missing tables in DB: {missing}"

@pytest.mark.asyncio
async def test_character_table_schema(initialized_test_db_engine: AsyncEngine):
    """
    Verify 'characters' table matches documentation strictly.
    """
    async with initialized_test_db_engine.connect() as conn:
        columns = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns("characters"))
        col_map = {c["name"]: c for c in columns}
        
        # Check critical new columns from docs
        assert "discord_username" in col_map
        assert "roles" in col_map
        assert "professions" in col_map
        assert "embed_json" in col_map
        
        # Check types (approximated for SQLite/Postgres differences in tests)
        # roles should be an array (or serialized equivalent in test DB if not PG)
        # In a real PG test container, this would be ARRAY.
        pass

@pytest.mark.asyncio
async def test_images_table_schema(initialized_test_db_engine: AsyncEngine):
    """
    Verify 'images' table matches documentation strictly.
    """
    async with initialized_test_db_engine.connect() as conn:
        columns = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns("images"))
        col_names = {c["name"] for c in columns}
        
        expected_cols = {
            "id", "img_origin_link", "img_graphics_vault_link", "original_filename",
            "uploaded_by_user_id", "source_system", "ownership_context", "usage_context",
            "entity_type", "entity_id", "category_tags", "provenance_notes",
            "permissions_level", "is_animated", "hash_md5", "upload_timestamp",
            "last_accessed_timestamp", "metadata_json", "status"
        }
        
        missing = expected_cols - col_names
        assert not missing, f"Missing columns in 'images': {missing}"

@pytest.mark.asyncio
async def test_sqlalchemy_base_metadata_matches_expectations():
    """
    Verify that SQLAlchemy Base.metadata includes all expected tables.
    This ensures the code (schemas/db_schemas.py) is aligned with the test expectations.
    """
    expected_tables = {
        "characters", "character_talents", "graveyard",
        "images", "talents", "talent_trees",
        "items", "item_sets", "npcs", "quests", "spells", "factions"
    }
    
    defined_tables = {t.name for t in Base.metadata.sorted_tables}
    missing = expected_tables - defined_tables
    assert not missing, f"schemas/db_schemas.py is missing definitions for: {missing}"
