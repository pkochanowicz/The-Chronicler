from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from schemas import db_schemas
from models import pydantic_models
from typing import List, Optional

class CharacterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_character(self, character: pydantic_models.CharacterCreate) -> db_schemas.Character:
        data = character.model_dump(by_alias=False)
        if 'roles' in data and data['roles']:
            data['roles'] = [r.value if hasattr(r, 'value') else str(r) for r in data['roles']]
        db_character = db_schemas.Character(**data)
        self.db.add(db_character)
        await self.db.commit()
        await self.db.refresh(db_character)
        return db_character

    async def get_character_by_id(self, character_id: int) -> Optional[db_schemas.Character]:
        result = await self.db.execute(
            select(db_schemas.Character).filter(db_schemas.Character.id == character_id)
        )
        return result.scalar_one_or_none()

    async def get_character_by_discord_id(self, discord_user_id: int) -> Optional[db_schemas.Character]:
        result = await self.db.execute(
            select(db_schemas.Character).filter(db_schemas.Character.discord_user_id == discord_user_id)
        )
        return result.scalar_one_or_none()

    async def get_character_by_name(self, name: str) -> Optional[db_schemas.Character]:
        result = await self.db.execute(
            select(db_schemas.Character).filter(db_schemas.Character.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_characters(self, skip: int = 0, limit: int = 100) -> List[db_schemas.Character]:
        result = await self.db.execute(
            select(db_schemas.Character).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_character(self, character_id: int, character: pydantic_models.CharacterUpdate) -> Optional[db_schemas.Character]:
        db_character = await self.get_character_by_id(character_id)
        if not db_character:
            return None

        update_data = character.model_dump(exclude_unset=True, by_alias=False)
        if 'roles' in update_data and update_data['roles']:
             update_data['roles'] = [r.value if hasattr(r, 'value') else str(r) for r in update_data['roles']]

        for key, value in update_data.items():
            setattr(db_character, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_character)
        return db_character

    async def delete_character(self, character_id: int) -> bool:
        result = await self.db.execute(
            delete(db_schemas.Character).where(db_schemas.Character.id == character_id)
        )
        await self.db.commit()
        return result.rowcount > 0

class GraveyardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_graveyard_entry(self, entry: pydantic_models.GraveyardCreate) -> db_schemas.Graveyard:
        db_entry = db_schemas.Graveyard(**entry.model_dump())
        self.db.add(db_entry)
        await self.db.commit()
        await self.db.refresh(db_entry)
        return db_entry

    async def get_graveyard_entry_by_id(self, entry_id: int) -> Optional[db_schemas.Graveyard]:
        result = await self.db.execute(
            select(db_schemas.Graveyard).filter(db_schemas.Graveyard.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_graveyard_entries_by_character_id(self, character_id: int) -> List[db_schemas.Graveyard]:
        result = await self.db.execute(
            select(db_schemas.Graveyard).filter(db_schemas.Graveyard.character_id == character_id)
        )
        return result.scalars().all()

    async def get_all_graveyard_entries(self, skip: int = 0, limit: int = 100) -> List[db_schemas.Graveyard]:
        result = await self.db.execute(
            select(db_schemas.Graveyard).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def delete_graveyard_entry(self, entry_id: int) -> bool:
        result = await self.db.execute(
            delete(db_schemas.Graveyard).where(db_schemas.Graveyard.id == entry_id)
        )
        await self.db.commit()
        return result.rowcount > 0
