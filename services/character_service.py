from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories import CharacterRepository, GraveyardRepository
from models import pydantic_models
from typing import List, Optional
from uuid import UUID

class CharacterService:
    def __init__(self, db: AsyncSession):
        self.character_repo = CharacterRepository(db)
        self.graveyard_repo = GraveyardRepository(db)

    async def create_character(self, character_data: pydantic_models.CharacterCreate) -> pydantic_models.CharacterInDB:
        db_character = await self.character_repo.create_character(character_data)
        return pydantic_models.CharacterInDB.model_validate(db_character)

    async def get_character_by_id(self, character_id: UUID) -> Optional[pydantic_models.CharacterInDB]:
        db_character = await self.character_repo.get_character_by_id(character_id)
        if db_character:
            return pydantic_models.CharacterInDB.model_validate(db_character)
        return None

    async def get_character_by_discord_id(self, discord_id: str) -> Optional[pydantic_models.CharacterInDB]:
        db_character = await self.character_repo.get_character_by_discord_id(discord_id)
        if db_character:
            return pydantic_models.CharacterInDB.model_validate(db_character)
        return None

    async def get_all_characters(self, skip: int = 0, limit: int = 100) -> List[pydantic_models.CharacterInDB]:
        db_characters = await self.character_repo.get_all_characters(skip, limit)
        return [pydantic_models.CharacterInDB.model_validate(char) for char in db_characters]

    async def update_character(self, character_id: UUID, character_data: pydantic_models.CharacterUpdate) -> Optional[pydantic_models.CharacterInDB]:
        db_character = await self.character_repo.update_character(character_id, character_data)
        if db_character:
            return pydantic_models.CharacterInDB.model_validate(db_character)
        return None

    async def delete_character(self, character_id: UUID) -> bool:
        return await self.character_repo.delete_character(character_id)

    async def bury_character(self, character_id: UUID, cause_of_death: str, eulogy: Optional[str] = None) -> Optional[pydantic_models.GraveyardInDB]:
        # First, ensure character exists
        character = await self.character_repo.get_character_by_id(character_id)
        if not character:
            return None
        
        # Create graveyard entry
        graveyard_data = pydantic_models.GraveyardCreate(
            character_id=character_id,
            cause_of_death=cause_of_death,
            eulogy=eulogy
        )
        db_graveyard_entry = await self.graveyard_repo.create_graveyard_entry(graveyard_data)

        # Optionally, you might want to mark the character as 'dead' in the characters table,
        # or delete the character entirely, depending on business rules.
        # For now, just adding to graveyard and leaving character in main table.
        
        return pydantic_models.GraveyardInDB.model_validate(db_graveyard_entry)

class GraveyardService:
    def __init__(self, db: AsyncSession):
        self.graveyard_repo = GraveyardRepository(db)

    async def get_graveyard_entry_by_id(self, entry_id: UUID) -> Optional[pydantic_models.GraveyardInDB]:
        db_entry = await self.graveyard_repo.get_graveyard_entry_by_id(entry_id)
        if db_entry:
            return pydantic_models.GraveyardInDB.model_validate(db_entry)
        return None

    async def get_graveyard_entries_for_character(self, character_id: UUID) -> List[pydantic_models.GraveyardInDB]:
        db_entries = await self.graveyard_repo.get_graveyard_entries_by_character_id(character_id)
        return [pydantic_models.GraveyardInDB.model_validate(entry) for entry in db_entries]
    
    async def get_all_graveyard_entries(self, skip: int = 0, limit: int = 100) -> List[pydantic_models.GraveyardInDB]:
        db_entries = await self.graveyard_repo.get_all_graveyard_entries(skip, limit)
        return [pydantic_models.GraveyardInDB.model_validate(entry) for entry in db_entries]

    async def delete_graveyard_entry(self, entry_id: UUID) -> bool:
        return await self.graveyard_repo.delete_graveyard_entry(entry_id)