import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import CharacterRepository
from schemas.db_schemas import Character, ChallengeMode
from models.pydantic_models import CharacterCreate, CharacterUpdate
from uuid import uuid4
from datetime import datetime

# Assuming you have a fixture for an async test database session
# This fixture would handle setup and teardown of the test database
# For now, let's mock it or use a simple in-memory equivalent if possible for initial structure

@pytest.fixture
async def character_repo(async_session: AsyncSession):
    return CharacterRepository(async_session)

@pytest.mark.asyncio
async def test_create_character(character_repo: CharacterRepository, async_session: AsyncSession):
    character_data = CharacterCreate(
        discord_id=f"test_user_{uuid4().hex}",
        character_name="TestCharacter",
        race="Human",
        faction="Alliance",
        class_name="Warrior",
        level=10,
        challenge_mode=ChallengeMode.Hardcore,
        story="A brave warrior."
    )
    new_character = await character_repo.create_character(character_data)
    assert new_character.id is not None
    assert new_character.character_name == "TestCharacter"
    assert new_character.challenge_mode == ChallengeMode.Hardcore
    
    retrieved_character = await character_repo.get_character_by_id(new_character.id)
    assert retrieved_character.character_name == "TestCharacter"

@pytest.mark.asyncio
async def test_get_character_by_discord_id(character_repo: CharacterRepository, async_session: AsyncSession):
    discord_id = f"test_discord_{uuid4().hex}"
    character_data = CharacterCreate(
        discord_id=discord_id,
        character_name="DiscordUser",
        race="Orc",
        faction="Horde",
        class_name="Shaman",
        level=5,
        challenge_mode=ChallengeMode.None_,
        story="A humble shaman."
    )
    await character_repo.create_character(character_data)

    retrieved_character = await character_repo.get_character_by_discord_id(discord_id)
    assert retrieved_character is not None
    assert retrieved_character.discord_id == discord_id

@pytest.mark.asyncio
async def test_update_character(character_repo: CharacterRepository, async_session: AsyncSession):
    discord_id = f"update_test_user_{uuid4().hex}"
    character_data = CharacterCreate(
        discord_id=discord_id,
        character_name="OldName",
        race="Gnome",
        faction="Alliance",
        class_name="Mage",
        level=1,
        challenge_mode=ChallengeMode.None_,
        story="A curious gnome."
    )
    initial_character = await character_repo.create_character(character_data)

    update_data = CharacterUpdate(character_name="NewName", level=2)
    updated_character = await character_repo.update_character(initial_character.id, update_data)

    assert updated_character.character_name == "NewName"
    assert updated_character.level == 2
    assert updated_character.id == initial_character.id

@pytest.mark.asyncio
async def test_delete_character(character_repo: CharacterRepository, async_session: AsyncSession):
    discord_id = f"delete_test_user_{uuid4().hex}"
    character_data = CharacterCreate(
        discord_id=discord_id,
        character_name="ToBeDeleted",
        race="Troll",
        faction="Horde",
        class_name="Hunter",
        level=1,
        challenge_mode=ChallengeMode.None_,
        story="A hunter's tale."
    )
    new_character = await character_repo.create_character(character_data)
    
    deleted = await character_repo.delete_character(new_character.id)
    assert deleted is True

    retrieved_character = await character_repo.get_character_by_id(new_character.id)
    assert retrieved_character is None
