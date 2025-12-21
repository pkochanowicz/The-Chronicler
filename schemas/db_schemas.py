from sqlalchemy import Column, Integer, String, Boolean, DateTime, UUID, Enum, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from db.database import Base
import enum

class ChallengeMode(enum.Enum):
    None_ = "None"
    Hardcore = "Hardcore"
    Immortal = "Immortal"
    Inferno = "Inferno"

class Character(Base):
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    discord_id = Column(String(255), unique=True, nullable=False)
    character_name = Column(String(100), nullable=False)
    race = Column(String(50), nullable=False)
    faction = Column(String(50), nullable=False)
    class_name = Column("class", String(50), nullable=False) # 'class' is a reserved keyword in Python
    level = Column(Integer, nullable=False)
    challenge_mode = Column(Enum(ChallengeMode), default=ChallengeMode.None_, nullable=False)
    story = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    talents = relationship("CharacterTalent", back_populates="character", cascade="all, delete-orphan")
    graveyard_entries = relationship("Graveyard", back_populates="character", cascade="all, delete-orphan")

class CharacterTalent(Base):
    __tablename__ = "character_talents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    talent_tree_id = Column(String(255), nullable=False)
    talent_id = Column(String(255), nullable=False)
    points_spent = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    character = relationship("Character", back_populates="talents")

    __table_args__ = (
        CheckConstraint('points_spent >= 0', name='points_spent_positive'),
        UniqueConstraint('character_id', 'talent_id', name='uq_character_talent')
    )

class Graveyard(Base):
    __tablename__ = "graveyard"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    death_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    cause_of_death = Column(Text, nullable=True)
    eulogy = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    character = relationship("Character", back_populates="graveyard_entries")