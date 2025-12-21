# tests/integration/services/test_character_service.py
import pytest
from services.character_service import CharacterService
from models import pydantic_models
from uuid import UUID

# Use the 'db_session' fixture from conftest.py which connects to the Testcontainer
@pytest.mark.asyncio
async def test_create_character_flow(db_session):
    """
    Tier 3 Integration Test: The Engine.
    Verifies CharacterService + Repository + Real DB (Container).
    """
    service = CharacterService(db_session)
    
    # 1. Prepare Data
    char_data = pydantic_models.CharacterCreate(
        discord_id="999888777",
        character_name="Thorgar_Test",
        race="Orc",
        faction="Horde",
        class_name="Warrior",
        level=10,
        challenge_mode="Hardcore", # Enum name might differ, checking definition
        story="A test warrior."
    )
    
    # 2. Execute Service Method
    created_char = await service.create_character(char_data)
    
    # 3. Verify Result (Pydantic Model)
    assert created_char.character_name == "Thorgar_Test"
    assert isinstance(created_char.id, UUID)
    assert created_char.level == 10
    
    # 4. Verify DB Persistence (Query directly)
    # We can use the service again to fetch, or raw SQL if we want to be strict.
    # Using service to test 'get_character_by_id' as well.
    fetched_char = await service.get_character_by_id(created_char.id)
    assert fetched_char is not None
    assert fetched_char.discord_id == "999888777"

@pytest.mark.asyncio
async def test_duplicate_character_prevention(db_session):
    """Verifies that we cannot create two characters with the same ID (if constraint exists) or name."""
    service = CharacterService(db_session)
    
    char_data = pydantic_models.CharacterCreate(
        discord_id="111222333",
        character_name="UniqueName",
        race="Human",
        faction="Alliance",
        class_name="Mage",
        level=1,
        challenge_mode="None"
    )
    
    # Create first
    await service.create_character(char_data)
    
    # Try to create identical one (assuming unique constraint on name or ID is not set on model but maybe logic)
    # If the DB schema has UNIQUE(name), this should raise an IntegrityError.
    # Let's assume we want to catch that.
    
    from sqlalchemy.exc import IntegrityError
    
    # Note: 'character_name' might not be unique in schema_v1.sql without checking it.
    # If not unique, this test serves to document that behavior. 
    # Checking Technical docs: "name (Text): Character name (Unique)." -> It IS unique.
    
    with pytest.raises(IntegrityError):
        await service.create_character(char_data)
        await db_session.flush() # Force SQL execution
