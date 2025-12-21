import pytest
from httpx import AsyncClient
from main import app
from models.pydantic_models import CharacterCreate, CharacterUpdate, ChallengeMode
from schemas.db_schemas import Character # Assuming Character model for direct DB access in test setup
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import CharacterRepository
from uuid import uuid4
from fastapi.testclient import TestClient

# Assuming a test_db_session fixture that provides an AsyncSession connected to a test database
# and handles cleanup. This would typically be defined in conftest.py



@pytest.fixture
async def test_character(async_session: AsyncSession):
    character_data = CharacterCreate(
        discord_id=f"test_discord_api_{uuid4().hex}",
        character_name="APIHero",
        race="Human",
        faction="Alliance",
        class_name="Paladin",
        level=60,
        challenge_mode=ChallengeMode.Hardcore,
        story="A righteous defender."
    )
    repo = CharacterRepository(async_session)
    char = await repo.create_character(character_data)
    return char

@pytest.mark.asyncio
async def test_create_character_api(client):
    discord_id = f"new_api_user_{uuid4().hex}"
    character_data = {
        "discord_id": discord_id,
        "character_name": "NewAPIChar",
        "race": "NightElf",
        "faction": "Alliance",
        "class": "Druid", # Using "class" as per Pydantic model alias
        "level": 1,
        "challenge_mode": "None",
        "story": "Freshly created."
    }
    response = client.post("/characters/", json=character_data)
    assert response.status_code == 201
    created_character = response.json()
    assert created_character["character_name"] == "NewAPIChar"
    assert created_character["discord_id"] == discord_id

@pytest.mark.asyncio
async def test_get_character_by_id_api(client, test_character: Character):
    response = client.get(f"/characters/{test_character.id}")
    assert response.status_code == 200
    retrieved_character = response.json()
    assert retrieved_character["id"] == str(test_character.id)
    assert retrieved_character["character_name"] == test_character.character_name

@pytest.mark.asyncio
async def test_get_character_by_discord_id_api(client, test_character: Character):
    response = client.get(f"/characters/by-discord/{test_character.discord_id}")
    assert response.status_code == 200
    retrieved_character = response.json()
    assert retrieved_character["discord_id"] == test_character.discord_id

@pytest.mark.asyncio
async def test_update_character_api(client, test_character: Character):
    update_data = {"character_name": "UpdatedAPIHero", "level": 61}
    response = client.patch(f"/characters/{test_character.id}", json=update_data)
    assert response.status_code == 200
    updated_character = response.json()
    assert updated_character["character_name"] == "UpdatedAPIHero"
    assert updated_character["level"] == 61

@pytest.mark.asyncio
async def test_delete_character_api(client, test_character: Character):
    response = client.delete(f"/characters/{test_character.id}")
    assert response.status_code == 204
    
    # Verify deletion
    check_response = client.get(f"/characters/{test_character.id}")
    assert check_response.status_code == 404

@pytest.mark.asyncio
async def test_bury_character_api(client, test_character: Character):
    cause_of_death = "Killed by a Murloc"
    eulogy = "Never forget the murlocs."
    response = client.post(f"/characters/{test_character.id}/bury?cause_of_death={cause_of_death}&eulogy={eulogy}")
    assert response.status_code == 201
    graveyard_entry = response.json()
    assert graveyard_entry["character_id"] == str(test_character.id)
    assert graveyard_entry["cause_of_death"] == cause_of_death
