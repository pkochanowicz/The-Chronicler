from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, CheckConstraint, UniqueConstraint, Numeric, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from db.database import Base
import enum

# --- Enums (from docs/architecture_UI_UX.md 2.3.1 Canonical Data Enums) ---

class ItemQualityEnum(enum.Enum):
    Poor = 0
    Common = 1
    Uncommon = 2
    Rare = 3
    Epic = 4
    Legendary = 5

class CharacterRaceEnum(enum.Enum):
    Human = "Human"
    Dwarf = "Dwarf"
    NightElf = "Night Elf"
    Gnome = "Gnome"
    Orc = "Orc"
    Troll = "Troll"
    Tauren = "Tauren"
    Undead = "Undead"
    Goblin = "Goblin"
    HighElf = "High Elf"
    Other = "Other"

class CharacterClassEnum(enum.Enum):
    Warrior = "Warrior"
    Paladin = "Paladin"
    Hunter = "Hunter"
    Rogue = "Rogue"
    Priest = "Priest"
    Shaman = "Shaman"
    Mage = "Mage"
    Warlock = "Warlock"
    Druid = "Druid"

class CharacterRoleEnum(enum.Enum):
    Tank = "Tank"
    Healer = "Healer"
    DPS = "DPS"

class CharacterStatusEnum(enum.Enum):
    PENDING = "PENDING"
    REGISTERED = "REGISTERED"
    REJECTED = "REJECTED"
    DECEASED = "DECEASED"
    BURIED = "BURIED"

class CreatureTypeEnum(enum.Enum):
    Beast = "Beast"
    Demon = "Demon"
    Dragonkin = "Dragonkin"
    Elemental = "Elemental"
    Giant = "Giant"
    Humanoid = "Humanoid"
    Mechanical = "Mechanical"
    Undead = "Undead"
    Critter = "Critter"
    Totem = "Totem"
    Other = "Other"

class SpellSchoolEnum(enum.Enum):
    Physical = "Physical"
    Arcane = "Arcane"
    Fire = "Fire"
    Frost = "Frost"
    Nature = "Nature"
    Shadow = "Shadow"
    Holy = "Holy"

class FactionAlignmentEnum(enum.Enum):
    Alliance = "Alliance"
    Horde = "Horde"
    Neutral = "Neutral"
    Hostile = "Hostile"

class QuestTypeEnum(enum.Enum):
    Normal = "Normal"
    Daily = "Daily"
    Dungeon = "Dungeon"
    Raid = "Raid"
    Profession = "Profession"
    ClassQuest = "Class Quest"
    Legendary = "Legendary"

class ChallengeMode(enum.Enum):
    None_ = "None"
    Hardcore = "Hardcore"
    Immortal = "Immortal"
    Inferno = "Inferno"

# --- Core Entities (from docs/architecture_UI_UX.md 2.3.2 Core Entity Schemas) ---

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_user_id = Column(BigInteger, nullable=False)
    discord_username = Column(String(64), nullable=False)
    name = Column(String(64), unique=True, nullable=False)
    race = Column(Enum(CharacterRaceEnum), nullable=False)
    class_name = Column("class", Enum(CharacterClassEnum), nullable=False)
    roles = Column(ARRAY(String), default=[], nullable=False) # TEXT[] per docs
    professions = Column(ARRAY(String), default=[], nullable=True) # TEXT[] per docs
    backstory = Column(Text, nullable=False)
    personality = Column(Text, nullable=True)
    quotes = Column(Text, nullable=True)
    portrait_url = Column(Text, nullable=True)
    trait_1 = Column(String(128), nullable=False)
    trait_2 = Column(String(128), nullable=False)
    trait_3 = Column(String(128), nullable=False)
    status = Column(Enum(CharacterStatusEnum), default=CharacterStatusEnum.PENDING, nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    request_sdxl = Column(Boolean, default=False, nullable=False)
    recruitment_msg_id = Column(BigInteger, nullable=True)
    forum_post_id = Column(BigInteger, unique=True, nullable=True)
    reviewed_by_user_id = Column(BigInteger, nullable=True)
    embed_json = Column(JSONB, default={}, nullable=False)
    death_cause = Column(String(256), nullable=True)
    death_story = Column(Text, nullable=True)
    talents_json = Column(JSONB, default={}, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    notes = Column(Text, nullable=True)

    talents = relationship("CharacterTalent", back_populates="character", cascade="all, delete-orphan")
    graveyard_entries = relationship("Graveyard", back_populates="character", cascade="all, delete-orphan")

class CharacterTalent(Base):
    __tablename__ = "character_talents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
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

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    death_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    cause_of_death = Column(Text, nullable=True)
    eulogy = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    character = relationship("Character", back_populates="graveyard_entries")

class Talent(Base):
    __tablename__ = "talents"

    id = Column(String(128), primary_key=True)
    name = Column(String(64), nullable=False)
    tree_id = Column(String(64), ForeignKey("talent_trees.id", ondelete="CASCADE"), nullable=False)
    tier = Column(Integer, nullable=False)
    talent_column = Column("column", Integer, nullable=True) # Mapped to "column" in DB
    max_rank = Column(Integer, default=1, nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(Text, nullable=False)
    prerequisite_id = Column(String(128), ForeignKey("talents.id"), nullable=True)
    points_req = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    prerequisite = relationship("Talent", remote_side=[id])
    talent_tree = relationship("TalentTree", back_populates="talents")

    __table_args__ = (
        CheckConstraint('tier >= 1 AND tier <= 7', name='talent_tier_range'),
        CheckConstraint('"column" >= 1 AND "column" <= 4', name='talent_column_range'),
        CheckConstraint('max_rank >= 1', name='talent_max_rank_positive'),
    )

class TalentTree(Base):
    __tablename__ = "talent_trees"

    id = Column(String(64), primary_key=True)
    class_name = Column("class", Enum(CharacterClassEnum), nullable=False)
    name = Column(String(64), nullable=False)
    background_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    talents = relationship("Talent", back_populates="talent_tree")

class Item(Base):
    __tablename__ = "items"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    turtle_db_url = Column(Text, nullable=False)
    icon_url = Column(Text, nullable=False)
    quality = Column(Enum(ItemQualityEnum), nullable=False)
    item_type = Column(String(64), nullable=False)
    item_subtype = Column(String(64), nullable=True)
    inventory_slot = Column(String(64), nullable=True)
    item_level = Column(Integer, nullable=True)
    required_level = Column(Integer, nullable=True)
    binding = Column(String(32), nullable=True)
    armor = Column(Integer, nullable=True)
    min_damage = Column(Integer, nullable=True)
    max_damage = Column(Integer, nullable=True)
    speed = Column(Numeric(4, 2), nullable=True)
    durability = Column(Integer, nullable=True)
    sell_price_copper = Column(Integer, nullable=True)
    buy_price_copper = Column(Integer, nullable=True)
    stats_json = Column(JSONB, default={}, nullable=True)
    use_effect_description = Column(Text, nullable=True)
    equip_effect_description = Column(Text, nullable=True)
    set_id = Column(BigInteger, ForeignKey("item_sets.id"), nullable=True)
    source_type = Column(String(64), nullable=True)
    source_details_json = Column(JSONB, default={}, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    item_set = relationship("ItemSet", back_populates="items")

    __table_args__ = (
        CheckConstraint('required_level >= 1 AND required_level <= 60', name='item_required_level_range'),
    )

class ItemSet(Base):
    __tablename__ = "item_sets"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    turtle_db_url = Column(Text, nullable=False)
    icon_url = Column(Text, nullable=True)
    required_level = Column(Integer, nullable=True)
    set_bonuses_json = Column(JSONB, default={}, nullable=False)
    items_in_set_ids = Column(ARRAY(BigInteger), default=[], nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    items = relationship("Item", back_populates="item_set")

class Npc(Base):
    __tablename__ = "npcs"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    turtle_db_url = Column(Text, nullable=False)
    creature_type = Column(Enum(CreatureTypeEnum), nullable=False)
    race = Column(String(64), nullable=True)
    faction_id = Column(BigInteger, ForeignKey("factions.id"), nullable=False)
    level = Column(Integer, nullable=True)
    classification = Column(String(64), nullable=True)
    zone = Column(String(128), nullable=True)
    coordinates_json = Column(JSONB, nullable=True)
    role = Column(String(64), nullable=True)
    model_url = Column(Text, nullable=True)
    abilities_json = Column(JSONB, default={}, nullable=True)
    is_vendor = Column(Boolean, default=False, nullable=False)
    is_quest_giver = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    faction = relationship("Faction", back_populates="npcs")

    __table_args__ = (
        CheckConstraint('level >= 1 AND level <= 63', name='npc_level_range'),
    )

class Quest(Base):
    __tablename__ = "quests"

    id = Column(BigInteger, primary_key=True)
    title = Column(String(256), nullable=False, unique=True)
    turtle_db_url = Column(Text, nullable=False)
    quest_type = Column(Enum(QuestTypeEnum), nullable=False)
    required_level = Column(Integer, default=1, nullable=False)
    zone = Column(String(128), nullable=False)
    quest_giver_npc_id = Column(BigInteger, ForeignKey("npcs.id"), nullable=True)
    quest_turnin_npc_id = Column(BigInteger, ForeignKey("npcs.id"), nullable=True)
    description = Column(Text, nullable=False)
    objectives_json = Column(JSONB, default={}, nullable=False)
    completion_text = Column(Text, nullable=True)
    xp_reward = Column(Integer, default=0, nullable=False)
    gold_reward_copper = Column(Integer, default=0, nullable=False)
    item_rewards_json = Column(JSONB, default={}, nullable=True)
    reputation_rewards_json = Column(JSONB, default={}, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    quest_giver = relationship("Npc", foreign_keys=[quest_giver_npc_id])
    quest_turnin = relationship("Npc", foreign_keys=[quest_turnin_npc_id])

    __table_args__ = (
        CheckConstraint('required_level >= 1 AND required_level <= 60', name='quest_required_level_range'),
    )

class Spell(Base):
    __tablename__ = "spells"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    turtle_db_url = Column(Text, nullable=False)
    icon_url = Column(Text, nullable=False)
    spell_school = Column(Enum(SpellSchoolEnum), nullable=False)
    spell_type = Column(String(64), nullable=True)
    rank = Column(String(32), nullable=True)
    cast_time = Column(String(64), nullable=False)
    cooldown = Column(String(64), nullable=True)
    mana_cost = Column(String(64), nullable=True)
    range = Column(String(64), nullable=True)
    duration = Column(String(64), nullable=True)
    target_type = Column(String(64), nullable=True)
    description = Column(Text, nullable=False)
    effect_details_json = Column(JSONB, default={}, nullable=True)
    talent_id = Column(String(128), ForeignKey("talents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    talent = relationship("Talent")

class Faction(Base):
    __tablename__ = "factions"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    turtle_db_url = Column(Text, nullable=True)
    alignment = Column(Enum(FactionAlignmentEnum), nullable=False)
    description = Column(Text, nullable=True)
    crest_url = Column(Text, nullable=True)
    primary_color_hex = Column(String(7), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    npcs = relationship("Npc", back_populates="faction")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    img_origin_link = Column(Text, nullable=False)
    img_graphics_vault_link = Column(Text, nullable=False, unique=True)
    original_filename = Column(String(256), nullable=False)
    uploaded_by_user_id = Column(BigInteger, nullable=True)
    source_system = Column(String(64), nullable=False)
    ownership_context = Column(String(64), nullable=False)
    usage_context = Column(String(64), nullable=False)
    entity_type = Column(String(64), nullable=True)
    entity_id = Column(BigInteger, nullable=True)
    category_tags = Column(ARRAY(String), default=[], nullable=False) # TEXT[]
    provenance_notes = Column(Text, nullable=True)
    permissions_level = Column(String(32), default="Public", nullable=False)
    is_animated = Column(Boolean, default=False, nullable=False)
    hash_md5 = Column(String(32), unique=True, nullable=True)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_timestamp = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSONB, default={}, nullable=True)
    status = Column(String(32), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())