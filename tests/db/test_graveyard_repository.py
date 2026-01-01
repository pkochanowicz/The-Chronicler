import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import GraveyardRepository, CharacterRepository
from models.pydantic_models import GraveyardCreate, CharacterCreate
from uuid import uuid4


@pytest_asyncio.fixture
async def graveyard_repo(async_session: AsyncSession):
    return GraveyardRepository(async_session)


@pytest_asyncio.fixture
async def character_repo_for_graveyard(async_session: AsyncSession):
    return CharacterRepository(async_session)


@pytest.mark.asyncio
async def test_create_graveyard_entry(
    graveyard_repo: GraveyardRepository,
    character_repo_for_graveyard: CharacterRepository,
    async_session: AsyncSession,
):
    # First create a character to link the graveyard entry to
    character_data = CharacterCreate(
        discord_user_id=777888999,
        discord_username=f"graveyard_test_{uuid4().hex[:8]}",
        name="FallenHero",
        race="Night Elf",
        class_name="Rogue",
        roles=[],
        professions=["Skinning"],
        backstory="A tale cut short by the darkness.",
        trait_1="Stealthy",
        trait_2="Agile",
        trait_3="Deadly",
    )
    new_character = await character_repo_for_graveyard.create_character(character_data)

    graveyard_entry_data = GraveyardCreate(
        character_id=new_character.id,
        cause_of_death="Killed by Hogger",
        eulogy="Rest in peace, brave rogue.",
    )
    new_entry = await graveyard_repo.create_graveyard_entry(graveyard_entry_data)
    assert new_entry.id is not None
    assert new_entry.character_id == new_character.id
    assert new_entry.cause_of_death == "Killed by Hogger"

    retrieved_entry = await graveyard_repo.get_graveyard_entry_by_id(new_entry.id)
    assert retrieved_entry.cause_of_death == "Killed by Hogger"


@pytest.mark.asyncio
async def test_get_graveyard_entries_by_character_id(
    graveyard_repo: GraveyardRepository,
    character_repo_for_graveyard: CharacterRepository,
    async_session: AsyncSession,
):
    character_data = CharacterCreate(
        discord_user_id=888999000,
        discord_username=f"multi_grave_{uuid4().hex[:8]}",
        name="MultipleDeaths",
        race="Undead",
        class_name="Warlock",
        roles=[],
        professions=["Tailoring", "Enchanting"],
        backstory="Many lives lost to the dark arts.",
        trait_1="Dark",
        trait_2="Mysterious",
        trait_3="Resilient",
    )
    new_character = await character_repo_for_graveyard.create_character(character_data)

    await graveyard_repo.create_graveyard_entry(
        GraveyardCreate(character_id=new_character.id, cause_of_death="First death")
    )
    await graveyard_repo.create_graveyard_entry(
        GraveyardCreate(character_id=new_character.id, cause_of_death="Second death")
    )

    entries = await graveyard_repo.get_graveyard_entries_by_character_id(
        new_character.id
    )
    assert len(entries) == 2
    assert entries[0].cause_of_death == "First death"
    assert entries[1].cause_of_death == "Second death"


@pytest.mark.asyncio
async def test_delete_graveyard_entry(
    graveyard_repo: GraveyardRepository,
    character_repo_for_graveyard: CharacterRepository,
    async_session: AsyncSession,
):
    character_data = CharacterCreate(
        discord_user_id=999000111,
        discord_username=f"delete_grave_{uuid4().hex[:8]}",
        name="ToDieAndBeForgotten",
        race="Tauren",
        class_name="Druid",
        roles=[],
        professions=["Herbalism", "Alchemy"],
        backstory="A peaceful life in Mulgore, ended by tragedy.",
        trait_1="Peaceful",
        trait_2="Naturalist",
        trait_3="Protective",
    )
    new_character = await character_repo_for_graveyard.create_character(character_data)

    graveyard_entry_data = GraveyardCreate(
        character_id=new_character.id, cause_of_death="Natural causes"
    )
    new_entry = await graveyard_repo.create_graveyard_entry(graveyard_entry_data)

    deleted = await graveyard_repo.delete_graveyard_entry(new_entry.id)
    assert deleted is True

    retrieved_entry = await graveyard_repo.get_graveyard_entry_by_id(new_entry.id)
    assert retrieved_entry is None
