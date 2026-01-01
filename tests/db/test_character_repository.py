import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import CharacterRepository
from models.pydantic_models import CharacterCreate, CharacterUpdate
from uuid import uuid4

# Assuming you have a fixture for an async test database session
# This fixture would handle setup and teardown of the test database
# For now, let's mock it or use a simple in-memory equivalent if possible for initial structure


@pytest_asyncio.fixture
async def character_repo(async_session: AsyncSession):
    return CharacterRepository(async_session)


@pytest.mark.asyncio
async def test_create_character(
    character_repo: CharacterRepository, async_session: AsyncSession
):
    character_data = CharacterCreate(
        discord_user_id=123456789,
        discord_username=f"test_user_{uuid4().hex[:8]}",
        name="TestCharacter",
        race="Human",
        class_name="Warrior",
        roles=[],
        professions=["Mining", "Blacksmithing"],
        backstory="A brave warrior from Stormwind.",
        trait_1="Brave",
        trait_2="Strong",
        trait_3="Loyal",
    )
    new_character = await character_repo.create_character(character_data)
    assert new_character.id is not None
    assert new_character.name == "TestCharacter"

    retrieved_character = await character_repo.get_character_by_id(new_character.id)
    assert retrieved_character.name == "TestCharacter"


@pytest.mark.asyncio
async def test_get_character_by_discord_id(
    character_repo: CharacterRepository, async_session: AsyncSession
):
    discord_user_id = 987654321
    character_data = CharacterCreate(
        discord_user_id=discord_user_id,
        discord_username=f"test_user_{uuid4().hex[:8]}",
        name="DiscordUser",
        race="Orc",
        class_name="Shaman",
        roles=[],
        professions=["Herbalism", "Alchemy"],
        backstory="A humble shaman from Orgrimmar.",
        trait_1="Wise",
        trait_2="Spiritual",
        trait_3="Patient",
    )
    await character_repo.create_character(character_data)

    retrieved_character = await character_repo.get_character_by_discord_id(
        discord_user_id
    )
    assert retrieved_character is not None
    assert retrieved_character.discord_user_id == discord_user_id


@pytest.mark.asyncio
async def test_update_character(
    character_repo: CharacterRepository, async_session: AsyncSession
):
    discord_user_id = 111222333
    character_data = CharacterCreate(
        discord_user_id=discord_user_id,
        discord_username=f"update_test_{uuid4().hex[:8]}",
        name="OldName",
        race="Gnome",
        class_name="Mage",
        roles=[],
        professions=["Engineering"],
        backstory="A curious gnome from Ironforge.",
        trait_1="Curious",
        trait_2="Intelligent",
        trait_3="Inventive",
    )
    initial_character = await character_repo.create_character(character_data)

    update_data = CharacterUpdate(name="NewName", backstory="An experienced mage.")
    updated_character = await character_repo.update_character(
        initial_character.id, update_data
    )

    assert updated_character.name == "NewName"
    assert updated_character.backstory == "An experienced mage."
    assert updated_character.id == initial_character.id


@pytest.mark.asyncio
async def test_delete_character(
    character_repo: CharacterRepository, async_session: AsyncSession
):
    discord_user_id = 444555666
    character_data = CharacterCreate(
        discord_user_id=discord_user_id,
        discord_username=f"delete_test_{uuid4().hex[:8]}",
        name="ToBeDeleted",
        race="Troll",
        class_name="Hunter",
        roles=[],
        professions=["Skinning", "Leatherworking"],
        backstory="A hunter's tale from the Darkspear tribe.",
        trait_1="Swift",
        trait_2="Sharp",
        trait_3="Cunning",
    )
    new_character = await character_repo.create_character(character_data)

    deleted = await character_repo.delete_character(new_character.id)
    assert deleted is True

    retrieved_character = await character_repo.get_character_by_id(new_character.id)
    assert retrieved_character is None
