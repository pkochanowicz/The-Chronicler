from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from schemas.db_schemas import ChallengeMode

# Base Character Models
class CharacterBase(BaseModel):
    discord_id: str = Field(..., max_length=255)
    character_name: str = Field(..., max_length=100)
    race: str = Field(..., max_length=50)
    faction: str = Field(..., max_length=50)
    class_name: str = Field(..., alias="class", max_length=50)
    level: int = Field(..., ge=1, le=70)
    challenge_mode: ChallengeMode = Field(ChallengeMode.None_, alias="challenge_mode")
    story: Optional[str] = None

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(CharacterBase):
    discord_id: Optional[str] = Field(None, max_length=255)
    character_name: Optional[str] = Field(None, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    faction: Optional[str] = Field(None, max_length=50)
    class_name: Optional[str] = Field(None, alias="class", max_length=50)
    level: Optional[int] = Field(None, ge=1, le=70)
    challenge_mode: Optional[ChallengeMode] = Field(None, alias="challenge_mode")
    story: Optional[str] = None

class CharacterInDB(CharacterBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Character Talent Models
class CharacterTalentBase(BaseModel):
    character_id: UUID
    talent_tree_id: str = Field(..., max_length=255)
    talent_id: str = Field(..., max_length=255)
    points_spent: int = Field(..., ge=0)

class CharacterTalentCreate(CharacterTalentBase):
    pass

class CharacterTalentInDB(CharacterTalentBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Graveyard Models
class GraveyardBase(BaseModel):
    character_id: UUID
    death_timestamp: Optional[datetime] = None
    cause_of_death: Optional[str] = None
    eulogy: Optional[str] = None

class GraveyardCreate(GraveyardBase):
    pass

class GraveyardInDB(GraveyardBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)