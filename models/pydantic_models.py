from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from schemas.db_schemas import (
    CharacterRaceEnum, 
    CharacterClassEnum, 
    CharacterRoleEnum, 
    CharacterStatusEnum, 
    ChallengeMode
)

# --- Character Models ---

class CharacterBase(BaseModel):
    name: str = Field(..., max_length=64, description="Character's unique name")
    race: CharacterRaceEnum
    class_name: CharacterClassEnum = Field(..., alias="class")
    roles: List[CharacterRoleEnum] = Field(default_factory=list)
    professions: List[str] = Field(default_factory=list)
    backstory: str = Field(..., description="Character backstory")
    personality: Optional[str] = None
    quotes: Optional[str] = None
    portrait_url: Optional[str] = None
    trait_1: str = Field(..., max_length=128)
    trait_2: str = Field(..., max_length=128)
    trait_3: str = Field(..., max_length=128)
    request_sdxl: bool = False
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class CharacterCreate(CharacterBase):
    discord_user_id: int
    discord_username: str = Field(..., max_length=64)

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=64)
    race: Optional[CharacterRaceEnum] = None
    class_name: Optional[CharacterClassEnum] = Field(None, alias="class")
    roles: Optional[List[CharacterRoleEnum]] = None
    professions: Optional[List[str]] = None
    backstory: Optional[str] = None
    personality: Optional[str] = None
    quotes: Optional[str] = None
    portrait_url: Optional[str] = None
    trait_1: Optional[str] = Field(None, max_length=128)
    trait_2: Optional[str] = Field(None, max_length=128)
    trait_3: Optional[str] = Field(None, max_length=128)
    status: Optional[CharacterStatusEnum] = None
    is_confirmed: Optional[bool] = None
    request_sdxl: Optional[bool] = None
    
    model_config = ConfigDict(populate_by_name=True)

class CharacterInDB(CharacterCreate):
    id: int
    status: CharacterStatusEnum = CharacterStatusEnum.PENDING
    is_confirmed: bool = False
    created_at: datetime
    updated_at: datetime
    
    # Additional DB fields
    recruitment_msg_id: Optional[int] = None
    forum_post_id: Optional[int] = None
    reviewed_by_user_id: Optional[int] = None
    embed_json: Dict[str, Any] = Field(default_factory=dict)
    death_cause: Optional[str] = None
    death_story: Optional[str] = None
    talents_json: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None

# --- Talent Models ---

class CharacterTalentBase(BaseModel):
    character_id: int
    talent_tree_id: str = Field(..., max_length=255)
    talent_id: str = Field(..., max_length=255)
    points_spent: int = Field(..., ge=0)
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class CharacterTalentCreate(CharacterTalentBase):
    pass

class CharacterTalentInDB(CharacterTalentBase):
    id: int
    created_at: datetime
    updated_at: datetime

# --- Graveyard Models ---

class GraveyardBase(BaseModel):
    character_id: int
    death_timestamp: Optional[datetime] = None
    cause_of_death: Optional[str] = None
    eulogy: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class GraveyardCreate(GraveyardBase):
    pass

class GraveyardInDB(GraveyardBase):
    id: int
    created_at: datetime
