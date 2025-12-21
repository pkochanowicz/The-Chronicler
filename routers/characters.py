from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from db.database import get_db
from models import pydantic_models
from services.character_service import CharacterService

router = APIRouter()

async def get_character_service(db: AsyncSession = Depends(get_db)) -> CharacterService:
    return CharacterService(db)

@router.post("/", response_model=pydantic_models.CharacterInDB, status_code=status.HTTP_201_CREATED)
async def create_character(
    character: pydantic_models.CharacterCreate,
    service: CharacterService = Depends(get_character_service)
):
    # TODO: Add validation if discord_id already exists
    return await service.create_character(character)

@router.get("/", response_model=List[pydantic_models.CharacterInDB])
async def get_all_characters(
    skip: int = 0, limit: int = 100,
    service: CharacterService = Depends(get_character_service)
):
    return await service.get_all_characters(skip, limit)

@router.get("/{character_id}", response_model=pydantic_models.CharacterInDB)
async def get_character_by_id(
    character_id: UUID,
    service: CharacterService = Depends(get_character_service)
):
    character = await service.get_character_by_id(character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return character

@router.get("/by-discord/{discord_id}", response_model=pydantic_models.CharacterInDB)
async def get_character_by_discord_id(
    discord_id: str,
    service: CharacterService = Depends(get_character_service)
):
    character = await service.get_character_by_discord_id(discord_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return character

@router.patch("/{character_id}", response_model=pydantic_models.CharacterInDB)
async def update_character(
    character_id: UUID,
    character: pydantic_models.CharacterUpdate,
    service: CharacterService = Depends(get_character_service)
):
    updated_character = await service.update_character(character_id, character)
    if updated_character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return updated_character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: UUID,
    service: CharacterService = Depends(get_character_service)
):
    success = await service.delete_character(character_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return {"message": "Character deleted successfully"}

@router.post("/{character_id}/bury", response_model=pydantic_models.GraveyardInDB, status_code=status.HTTP_201_CREATED)
async def bury_character(
    character_id: UUID,
    cause_of_death: str,
    eulogy: Optional[str] = None,
    service: CharacterService = Depends(get_character_service)
):
    graveyard_entry = await service.bury_character(character_id, cause_of_death, eulogy)
    if graveyard_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or could not be buried")
    return graveyard_entry

@router.get("/{character_id}/graveyard", response_model=List[pydantic_models.GraveyardInDB])
async def get_character_graveyard_entries(
    character_id: UUID,
    service: CharacterService = Depends(get_character_service)
):
    entries = await service.graveyard_repo.get_graveyard_entries_by_character_id(character_id)
    return [pydantic_models.GraveyardInDB.model_validate(entry) for entry in entries]
