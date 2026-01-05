import pytest
from models import pydantic_models
from services.character_service import CharacterService
from schemas.db_schemas import CharacterRaceEnum, CharacterClassEnum, CharacterRoleEnum


# Use the 'async_session' fixture from conftest.py which connects to the Testcontainer
@pytest.mark.asyncio
async def test_create_character_flow(async_session):
    """
    Tier 3 Integration Test: The Engine.
    Verifies CharacterService + Repository + Real DB (Container).
    """
    service = CharacterService(async_session)

    # 1. Prepare Data
    char_data = pydantic_models.CharacterCreate(
        discord_user_id=222333444,  # Unique ID to avoid conflicts
        discord_username="ThorgarUser",
        name="Thorgar_Test",
        race=CharacterRaceEnum.Orc,
        class_name=CharacterClassEnum.Warrior,
        roles=[CharacterRoleEnum.Tank],
        professions=["Mining"],
        backstory="A test warrior.",
        trait_1="Strong",
        trait_2="Brave",
        trait_3="Orcish",
    )

    # 2. Execute Logic
    created_char = await service.create_character(char_data)

    # 3. Verify Persistence
    assert created_char.id is not None
    assert created_char.name == "Thorgar_Test"

    # 4. Verify Retrieval
    fetched_char = await service.get_character_by_discord_id(222333444)
    assert fetched_char is not None
    assert fetched_char.id == created_char.id
    assert fetched_char.discord_user_id == 222333444


@pytest.mark.asyncio
async def test_duplicate_character_prevention(async_session):
    """Verifies that we cannot create two characters with the same ID (if constraint exists) or name."""
    service = CharacterService(async_session)

    char_data = pydantic_models.CharacterCreate(
        discord_user_id=333444555,  # Unique ID to avoid conflicts
        discord_username="UniqueUser",
        name="UniqueName",
        race=CharacterRaceEnum.Human,
        class_name=CharacterClassEnum.Mage,
        roles=[CharacterRoleEnum.RangedDPS],
        backstory="Unique story",
        trait_1="Smart",
        trait_2="Quick",
        trait_3="Magical",
    )

    await service.create_character(char_data)

    # Try to create again with same Name (should fail due to Unique constraint on name)
    from sqlalchemy.exc import IntegrityError

    char_data_duplicate = pydantic_models.CharacterCreate(
        discord_user_id=444555666,  # Different user
        discord_username="OtherUser",
        name="UniqueName",  # Same Name
        race=CharacterRaceEnum.Human,
        class_name=CharacterClassEnum.Mage,
        roles=[CharacterRoleEnum.RangedDPS],
        backstory="Copycat",
        trait_1="A",
        trait_2="B",
        trait_3="C",
    )

    with pytest.raises(IntegrityError):
        await service.create_character(char_data_duplicate)
