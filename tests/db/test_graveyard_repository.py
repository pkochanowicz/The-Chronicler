import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import GraveyardRepository, CharacterRepository
from schemas.db_schemas import Graveyard, ChallengeMode
from models.pydantic_models import GraveyardCreate, CharacterCreate
from uuid import uuid4
from datetime import datetime

@pytest.fixture
async def graveyard_repo(async_session: AsyncSession):
    return GraveyardRepository(async_session)

@pytest.fixture
async def character_repo_for_graveyard(async_session: AsyncSession):
    return CharacterRepository(async_session)

@pytest.mark.asyncio
async def test_create_graveyard_entry(
    graveyard_repo: GraveyardRepository, 
    character_repo_for_graveyard: CharacterRepository, 
    async_session: AsyncSession
):
    # First create a character to link the graveyard entry to
    character_data = CharacterCreate(
        discord_id=f"test_user_graveyard_{uuid4().hex}",
        character_name="FallenHero",
        race="Elf",
        faction="Alliance",
        class_name="Rogue",
        level=60,
        challenge_mode=ChallengeMode.Hardcore,
        story="A tale cut short."
    )
    new_character = await character_repo_for_graveyard.create_character(character_data)

    graveyard_entry_data = GraveyardCreate(
        character_id=new_character.id,
        cause_of_death="Killed by Hogger",
        eulogy="Rest in peace, brave rogue."
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
    async_session: AsyncSession
):
    character_data = CharacterCreate(
        discord_id=f"test_user_multi_graveyard_{uuid4().hex}",
        character_name="MultipleDeaths",
        race="Undead",
        faction="Horde",
        class_name="Warlock",
        level=15,
        challenge_mode=ChallengeMode.None_,
        story="Many lives lost."
    )
    new_character = await character_repo_for_graveyard.create_character(character_data)

    await graveyard_repo.create_graveyard_entry(GraveyardCreate(character_id=new_character.id, cause_of_death="First death"))
    await graveyard_repo.create_graveyard_entry(GraveyardCreate(character_id=new_character.id, cause_of_death="Second death"))

    entries = await graveyard_repo.get_graveyard_entries_by_character_id(new_character.id)
    assert len(entries) == 2
    assert entries[0].cause_of_death == "First death"
    assert entries[1].cause_of_death == "Second death"

@pytest.mark.asyncio
async def test_delete_graveyard_entry(
    graveyard_repo: GraveyardRepository, 
    character_repo_for_graveyard: CharacterRepository, 
    async_session: AsyncSession
):
    character_data = CharacterCreate(
        discord_id=f"test_user_delete_graveyard_{uuid4().hex}",
        character_name="ToDieAndBeForgotten",
        race="Tauren",
        faction="Horde",
        class_name="Druid",
        level=20,
        challenge_mode=ChallengeMode.Hardcore,
        story="A peaceful life, ended."
    )
    new_character = await character_repo_for_graveyard.create_character(character_data)

    graveyard_entry_data = GraveyardCreate(character_id=new_character.id, cause_of_death="Natural causes")
    new_entry = await graveyard_repo.create_graveyard_entry(graveyard_entry_data)
    
    deleted = await graveyard_repo.delete_graveyard_entry(new_entry.id)
    assert deleted is True

    retrieved_entry = await graveyard_repo.get_graveyard_entry_by_id(new_entry.id)
    assert retrieved_entry is None