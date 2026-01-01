import pytest
from httpx import AsyncClient
from models.pydantic_models import CharacterCreate
from schemas.db_schemas import (
    Character,
    CharacterRaceEnum,
    CharacterClassEnum,
    CharacterRoleEnum,
)
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import CharacterRepository
from uuid import uuid4

# Use pytest_asyncio.fixture for async fixtures
import pytest_asyncio


@pytest_asyncio.fixture
async def test_character(async_session: AsyncSession):
    character_data = CharacterCreate(
        discord_user_id=int(uuid4().int % 100000000),
        discord_username="APIUser",
        name=f"APIHero_{uuid4().hex[:6]}",
        race=CharacterRaceEnum.Human,
        class_name=CharacterClassEnum.Paladin,
        roles=[CharacterRoleEnum.Tank],
        professions=["Mining"],
        backstory="A righteous defender.",
        trait_1="A",
        trait_2="B",
        trait_3="C",
    )
    repo = CharacterRepository(async_session)
    char = await repo.create_character(character_data)
    return char


@pytest.mark.asyncio
async def test_create_character_api(async_client: AsyncClient):
    discord_id = int(uuid4().int % 100000000)
    character_data = {
        "discord_user_id": discord_id,
        "discord_username": "NewAPIUser",
        "name": "NewAPIChar",
        "race": "Night Elf",
        "class": "Druid",
        "roles": ["Healer"],
        "professions": ["Herbalism"],
        "backstory": "Freshly created.",
        "trait_1": "Wise",
        "trait_2": "Calm",
        "trait_3": "Nature-bound",
    }
    response = await async_client.post("/characters/", json=character_data)
    assert response.status_code == 201
    created_character = response.json()
    assert created_character["name"] == "NewAPIChar"
    assert created_character["discord_user_id"] == discord_id


@pytest.mark.asyncio
async def test_get_character_by_id_api(
    async_client: AsyncClient, test_character: Character
):
    response = await async_client.get(f"/characters/{test_character.id}")
    assert response.status_code == 200
    retrieved_character = response.json()
    assert retrieved_character["id"] == test_character.id
    assert retrieved_character["name"] == test_character.name


@pytest.mark.asyncio
async def test_get_character_by_discord_id_api(
    async_client: AsyncClient, test_character: Character
):
    response = await async_client.get(
        f"/characters/by-discord/{test_character.discord_user_id}"
    )
    assert response.status_code == 200
    retrieved_character = response.json()
    assert retrieved_character["discord_user_id"] == test_character.discord_user_id


@pytest.mark.asyncio
async def test_update_character_api(
    async_client: AsyncClient, test_character: Character
):
    update_data = {"name": "UpdatedAPIHero", "backstory": "New story"}
    response = await async_client.patch(
        f"/characters/{test_character.id}", json=update_data
    )
    assert response.status_code == 200
    updated_character = response.json()
    assert updated_character["name"] == "UpdatedAPIHero"
    assert updated_character["backstory"] == "New story"


@pytest.mark.asyncio
async def test_delete_character_api(
    async_client: AsyncClient, test_character: Character
):
    response = await async_client.delete(f"/characters/{test_character.id}")
    assert response.status_code == 204

    # Verify deletion
    check_response = await async_client.get(f"/characters/{test_character.id}")
    assert check_response.status_code == 404


@pytest.mark.asyncio
async def test_bury_character_api(async_client: AsyncClient, test_character: Character):
    cause_of_death = "Killed by a Murloc"
    eulogy = "Never forget the murlocs."
    # query params
    response = await async_client.post(
        f"/characters/{test_character.id}/bury",
        params={"cause_of_death": cause_of_death, "eulogy": eulogy},
    )
    assert response.status_code == 201
    graveyard_entry = response.json()
    assert graveyard_entry["character_id"] == test_character.id
    assert graveyard_entry["cause_of_death"] == cause_of_death
