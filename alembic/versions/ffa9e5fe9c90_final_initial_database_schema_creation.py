"""Final initial database schema creation

Revision ID: ffa9e5fe9c90
Revises: 
Create Date: 2025-12-21 23:50:26.537623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'ffa9e5fe9c90'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()

    # --- 1. Create New Tables (Unchanged) ---
    if 'factions' not in tables:
        op.create_table('factions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=128), nullable=False),
            sa.Column('turtle_db_url', sa.Text(), nullable=True),
            sa.Column('alignment', sa.Enum('Alliance', 'Horde', 'Neutral', 'Hostile', name='factionalignmentenum'), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('crest_url', sa.Text(), nullable=True),
            sa.Column('primary_color_hex', sa.String(length=7), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
    
    if 'images' not in tables:
        op.create_table('images',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('img_origin_link', sa.Text(), nullable=False),
            sa.Column('img_graphics_vault_link', sa.Text(), nullable=False),
            sa.Column('original_filename', sa.String(length=256), nullable=False),
            sa.Column('uploaded_by_user_id', sa.BigInteger(), nullable=True),
            sa.Column('source_system', sa.String(length=64), nullable=False),
            sa.Column('ownership_context', sa.String(length=64), nullable=False),
            sa.Column('usage_context', sa.String(length=64), nullable=False),
            sa.Column('entity_type', sa.String(length=64), nullable=True),
            sa.Column('entity_id', sa.BigInteger(), nullable=True),
            sa.Column('category_tags', postgresql.ARRAY(sa.String()), nullable=False),
            sa.Column('provenance_notes', sa.Text(), nullable=True),
            sa.Column('permissions_level', sa.String(length=32), nullable=False),
            sa.Column('is_animated', sa.Boolean(), nullable=False),
            sa.Column('hash_md5', sa.String(length=32), nullable=True),
            sa.Column('upload_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('last_accessed_timestamp', sa.DateTime(timezone=True), nullable=True),
            sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('status', sa.String(length=32), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('hash_md5'),
            sa.UniqueConstraint('img_graphics_vault_link')
        )
    
    if 'item_sets' not in tables:
        op.create_table('item_sets',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=256), nullable=False),
            sa.Column('turtle_db_url', sa.Text(), nullable=False),
            sa.Column('icon_url', sa.Text(), nullable=True),
            sa.Column('required_level', sa.Integer(), nullable=True),
            sa.Column('set_bonuses_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column('items_in_set_ids', postgresql.ARRAY(sa.Integer()), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
    
    if 'talent_trees' not in tables:
        op.create_table('talent_trees',
            sa.Column('id', sa.String(length=64), nullable=False),
            sa.Column('class', sa.Enum('Warrior', 'Paladin', 'Hunter', 'Rogue', 'Priest', 'Shaman', 'Mage', 'Warlock', 'Druid', name='characterclassenum'), nullable=False),
            sa.Column('name', sa.String(length=64), nullable=False),
            sa.Column('background_image_url', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    if 'items' not in tables:
        op.create_table('items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=256), nullable=False),
            sa.Column('turtle_db_url', sa.Text(), nullable=False),
            sa.Column('icon_url', sa.Text(), nullable=False),
            sa.Column('quality', sa.Enum('Poor', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', name='itemqualityenum'), nullable=False),
            sa.Column('item_type', sa.String(length=64), nullable=False),
            sa.Column('item_subtype', sa.String(length=64), nullable=True),
            sa.Column('inventory_slot', sa.String(length=64), nullable=True),
            sa.Column('item_level', sa.Integer(), nullable=True),
            sa.Column('required_level', sa.Integer(), nullable=True),
            sa.Column('binding', sa.String(length=32), nullable=True),
            sa.Column('armor', sa.Integer(), nullable=True),
            sa.Column('min_damage', sa.Integer(), nullable=True),
            sa.Column('max_damage', sa.Integer(), nullable=True),
            sa.Column('speed', sa.Numeric(precision=4, scale=2), nullable=True),
            sa.Column('durability', sa.Integer(), nullable=True),
            sa.Column('sell_price_copper', sa.Integer(), nullable=True),
            sa.Column('buy_price_copper', sa.Integer(), nullable=True),
            sa.Column('stats_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('use_effect_description', sa.Text(), nullable=True),
            sa.Column('equip_effect_description', sa.Text(), nullable=True),
            sa.Column('set_id', sa.Integer(), nullable=True),
            sa.Column('source_type', sa.String(length=64), nullable=True),
            sa.Column('source_details_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.CheckConstraint('required_level >= 1 AND required_level <= 60', name='item_required_level_range'),
            sa.ForeignKeyConstraint(['set_id'], ['item_sets.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
    
    if 'npcs' not in tables:
        op.create_table('npcs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=256), nullable=False),
            sa.Column('turtle_db_url', sa.Text(), nullable=False),
            sa.Column('creature_type', sa.Enum('Beast', 'Demon', 'Dragonkin', 'Elemental', 'Giant', 'Humanoid', 'Mechanical', 'Undead', 'Critter', 'Totem', 'Other', name='creaturetypeenum'), nullable=False),
            sa.Column('race', sa.String(length=64), nullable=True),
            sa.Column('faction_id', sa.Integer(), nullable=False),
            sa.Column('level', sa.Integer(), nullable=True),
            sa.Column('classification', sa.String(length=64), nullable=True),
            sa.Column('zone', sa.String(length=128), nullable=True),
            sa.Column('coordinates_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('role', sa.String(length=64), nullable=True),
            sa.Column('model_url', sa.Text(), nullable=True),
            sa.Column('abilities_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('is_vendor', sa.Boolean(), nullable=False),
            sa.Column('is_quest_giver', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.CheckConstraint('level >= 1 AND level <= 63', name='npc_level_range'),
            sa.ForeignKeyConstraint(['faction_id'], ['factions.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
    
    if 'talents' not in tables:
        op.create_table('talents',
            sa.Column('id', sa.String(length=128), nullable=False),
            sa.Column('name', sa.String(length=64), nullable=False),
            sa.Column('tree_id', sa.String(length=64), nullable=False),
            sa.Column('tier', sa.Integer(), nullable=False),
            sa.Column('talent_column', sa.Integer(), nullable=True),
            sa.Column('max_rank', sa.Integer(), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('icon_url', sa.Text(), nullable=False),
            sa.Column('prerequisite_id', sa.String(length=128), nullable=True),
            sa.Column('points_req', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.CheckConstraint('max_rank >= 1', name='talent_max_rank_positive'),
            sa.CheckConstraint('talent_column >= 1 AND talent_column <= 4', name='talent_column_range'),
            sa.CheckConstraint('tier >= 1 AND tier <= 7', name='talent_tier_range'),
            sa.ForeignKeyConstraint(['prerequisite_id'], ['talents.id'], ),
            sa.ForeignKeyConstraint(['tree_id'], ['talent_trees.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    if 'quests' not in tables:
        op.create_table('quests',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=256), nullable=False),
            sa.Column('turtle_db_url', sa.Text(), nullable=False),
            sa.Column('quest_type', sa.Enum('Normal', 'Daily', 'Dungeon', 'Raid', 'Profession', 'ClassQuest', 'Legendary', name='questtypeenum'), nullable=False),
            sa.Column('required_level', sa.Integer(), nullable=False),
            sa.Column('zone', sa.String(length=128), nullable=False),
            sa.Column('quest_giver_npc_id', sa.Integer(), nullable=True),
            sa.Column('quest_turnin_npc_id', sa.Integer(), nullable=True),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('objectives_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column('completion_text', sa.Text(), nullable=True),
            sa.Column('xp_reward', sa.Integer(), nullable=False),
            sa.Column('gold_reward_copper', sa.Integer(), nullable=False),
            sa.Column('item_rewards_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('reputation_rewards_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.CheckConstraint('required_level >= 1 AND required_level <= 60', name='quest_required_level_range'),
            sa.ForeignKeyConstraint(['quest_giver_npc_id'], ['npcs.id'], ),
            sa.ForeignKeyConstraint(['quest_turnin_npc_id'], ['npcs.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('title')
        )
    
    if 'spells' not in tables:
        op.create_table('spells',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=128), nullable=False),
            sa.Column('turtle_db_url', sa.Text(), nullable=False),
            sa.Column('icon_url', sa.Text(), nullable=False),
            sa.Column('spell_school', sa.Enum('Physical', 'Arcane', 'Fire', 'Frost', 'Nature', 'Shadow', 'Holy', name='spellschoolenum'), nullable=False),
            sa.Column('spell_type', sa.String(length=64), nullable=True),
            sa.Column('rank', sa.String(length=32), nullable=True),
            sa.Column('cast_time', sa.String(length=64), nullable=False),
            sa.Column('cooldown', sa.String(length=64), nullable=True),
            sa.Column('mana_cost', sa.String(length=64), nullable=True),
            sa.Column('range', sa.String(length=64), nullable=True),
            sa.Column('duration', sa.String(length=64), nullable=True),
            sa.Column('target_type', sa.String(length=64), nullable=True),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('effect_details_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('talent_id', sa.String(length=128), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['talent_id'], ['talents.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    # --- 2. Conditional Logic for Existing Tables ---
    
    # CHARACTERS
    if 'characters' in tables:
        # Legacy schema exists, apply alterations
        op.add_column('characters', sa.Column('discord_user_id', sa.BigInteger(), nullable=False))
        op.add_column('characters', sa.Column('discord_username', sa.String(length=64), nullable=False))
        op.add_column('characters', sa.Column('name', sa.String(length=64), nullable=False))
        op.add_column('characters', sa.Column('roles', postgresql.ARRAY(sa.Enum('Tank', 'Healer', 'DPS', name='characterroleenum')), nullable=False))
        op.add_column('characters', sa.Column('professions', postgresql.ARRAY(sa.String()), nullable=True))
        op.add_column('characters', sa.Column('backstory', sa.Text(), nullable=False))
        op.add_column('characters', sa.Column('personality', sa.Text(), nullable=True))
        op.add_column('characters', sa.Column('quotes', sa.Text(), nullable=True))
        op.add_column('characters', sa.Column('portrait_url', sa.Text(), nullable=True))
        op.add_column('characters', sa.Column('trait_1', sa.String(length=128), nullable=False))
        op.add_column('characters', sa.Column('trait_2', sa.String(length=128), nullable=False))
        op.add_column('characters', sa.Column('trait_3', sa.String(length=128), nullable=False))
        op.add_column('characters', sa.Column('status', sa.Enum('PENDING', 'REGISTERED', 'REJECTED', 'DECEASED', 'BURIED', name='characterstatusenum'), nullable=False))
        op.add_column('characters', sa.Column('is_confirmed', sa.Boolean(), nullable=False))
        op.add_column('characters', sa.Column('request_sdxl', sa.Boolean(), nullable=False))
        op.add_column('characters', sa.Column('recruitment_msg_id', sa.BigInteger(), nullable=True))
        op.add_column('characters', sa.Column('forum_post_id', sa.BigInteger(), nullable=True))
        op.add_column('characters', sa.Column('reviewed_by_user_id', sa.BigInteger(), nullable=True))
        op.add_column('characters', sa.Column('embed_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False))
        op.add_column('characters', sa.Column('death_cause', sa.String(length=256), nullable=True))
        op.add_column('characters', sa.Column('death_story', sa.Text(), nullable=True))
        op.add_column('characters', sa.Column('talents_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        op.add_column('characters', sa.Column('notes', sa.Text(), nullable=True))
        op.alter_column('characters', 'id',
                   existing_type=sa.UUID(),
                   type_=sa.Integer(),
                   existing_nullable=False,
                   autoincrement=True,
                   existing_server_default=sa.text('gen_random_uuid()'),
                   postgresql_using='id::integer')
        op.alter_column('characters', 'race',
                   existing_type=sa.VARCHAR(length=50),
                   type_=sa.Enum('Human', 'Dwarf', 'NightElf', 'Gnome', 'Orc', 'Troll', 'Tauren', 'Undead', 'Goblin', 'HighElf', 'Other', name='characterraceenum'),
                   existing_nullable=False)
        op.alter_column('characters', 'class',
                   existing_type=sa.VARCHAR(length=50),
                   type_=sa.Enum('Warrior', 'Paladin', 'Hunter', 'Rogue', 'Priest', 'Shaman', 'Mage', 'Warlock', 'Druid', name='characterclassenum'),
                   existing_nullable=False)
        op.drop_constraint(op.f('characters_discord_id_key'), 'characters', type_='unique')
        op.create_unique_constraint(None, 'characters', ['forum_post_id'])
        op.create_unique_constraint(None, 'characters', ['name'])
        op.drop_column('characters', 'faction')
        op.drop_column('characters', 'discord_id')
        op.drop_column('characters', 'challenge_mode')
        op.drop_column('characters', 'level')
        op.drop_column('characters', 'story')
        op.drop_column('characters', 'character_name')
    else:
        # Create 'characters' from scratch (Final Schema)
        op.create_table('characters',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('discord_user_id', sa.BigInteger(), nullable=False),
            sa.Column('discord_username', sa.String(length=64), nullable=False),
            sa.Column('name', sa.String(length=64), nullable=False),
            sa.Column('race', sa.Enum('Human', 'Dwarf', 'NightElf', 'Gnome', 'Orc', 'Troll', 'Tauren', 'Undead', 'Goblin', 'HighElf', 'Other', name='characterraceenum'), nullable=False),
            sa.Column('class', sa.Enum('Warrior', 'Paladin', 'Hunter', 'Rogue', 'Priest', 'Shaman', 'Mage', 'Warlock', 'Druid', name='characterclassenum'), nullable=False),
            sa.Column('roles', postgresql.ARRAY(sa.Enum('Tank', 'Healer', 'DPS', name='characterroleenum')), nullable=False),
            sa.Column('professions', postgresql.ARRAY(sa.String()), nullable=True),
            sa.Column('backstory', sa.Text(), nullable=False),
            sa.Column('personality', sa.Text(), nullable=True),
            sa.Column('quotes', sa.Text(), nullable=True),
            sa.Column('portrait_url', sa.Text(), nullable=True),
            sa.Column('trait_1', sa.String(length=128), nullable=False),
            sa.Column('trait_2', sa.String(length=128), nullable=False),
            sa.Column('trait_3', sa.String(length=128), nullable=False),
            sa.Column('status', sa.Enum('PENDING', 'REGISTERED', 'REJECTED', 'DECEASED', 'BURIED', name='characterstatusenum'), nullable=False),
            sa.Column('is_confirmed', sa.Boolean(), nullable=False),
            sa.Column('request_sdxl', sa.Boolean(), nullable=False),
            sa.Column('recruitment_msg_id', sa.BigInteger(), nullable=True),
            sa.Column('forum_post_id', sa.BigInteger(), nullable=True),
            sa.Column('reviewed_by_user_id', sa.BigInteger(), nullable=True),
            sa.Column('embed_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column('death_cause', sa.String(length=256), nullable=True),
            sa.Column('death_story', sa.Text(), nullable=True),
            sa.Column('talents_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'),
            sa.UniqueConstraint('forum_post_id')
        )

    # CHARACTER TALENTS
    if 'character_talents' in tables:
        op.alter_column('character_talents', 'id',
                   existing_type=sa.UUID(),
                   type_=sa.Integer(),
                   existing_nullable=False,
                   autoincrement=True,
                   existing_server_default=sa.text('gen_random_uuid()'),
                   postgresql_using='id::integer')
        op.alter_column('character_talents', 'character_id',
                   existing_type=sa.UUID(),
                   type_=sa.Integer(),
                   existing_nullable=False,
                   postgresql_using='character_id::integer')
        op.drop_constraint(op.f('character_talents_character_id_talent_id_key'), 'character_talents', type_='unique')
        op.create_unique_constraint('uq_character_talent', 'character_talents', ['character_id', 'talent_id'])
    else:
         op.create_table('character_talents',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('character_id', sa.Integer(), nullable=False),
            sa.Column('talent_tree_id', sa.String(length=255), nullable=False),
            sa.Column('talent_id', sa.String(length=255), nullable=False),
            sa.Column('points_spent', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
            sa.UniqueConstraint('character_id', 'talent_id', name='uq_character_talent'),
            sa.CheckConstraint('points_spent >= 0', name='points_spent_positive')
        )

    # GRAVEYARD
    if 'graveyard' in tables:
        op.alter_column('graveyard', 'id',
                   existing_type=sa.UUID(),
                   type_=sa.Integer(),
                   existing_nullable=False,
                   autoincrement=True,
                   existing_server_default=sa.text('gen_random_uuid()'),
                   postgresql_using='id::integer')
        op.alter_column('graveyard', 'character_id',
                   existing_type=sa.UUID(),
                   type_=sa.Integer(),
                   existing_nullable=False,
                   postgresql_using='character_id::integer')
    else:
        op.create_table('graveyard',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('character_id', sa.Integer(), nullable=False),
            sa.Column('death_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('cause_of_death', sa.Text(), nullable=True),
            sa.Column('eulogy', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE')
        )

def downgrade() -> None:
    """Downgrade schema."""
    # Note: Downgrade logic is strictly inverse of upgrade.
    # Conditional downgrades are complex. We typically assume we are downgrading the NEW structure.
    # If the user downgrades, they might be expecting to go back to EMPTY (if we started empty) 
    # or back to LEGACY (if we started legacy).
    # Since Alembic doesn't track *which* branch we took, we can't easily handle this cleanly.
    # For now, we assume we revert to the Legacy state for the core tables, and drop the new tables.
    
    # Drop new tables
    op.drop_table('spells')
    op.drop_table('quests')
    op.drop_table('talents')
    op.drop_table('npcs')
    op.drop_table('items')
    op.drop_table('talent_trees')
    op.drop_table('item_sets')
    op.drop_table('images')
    op.drop_table('factions')

    # Revert 'graveyard'
    # We can try to cast back to UUID, but Integer -> UUID is not trivial if we generated IDs.
    # This downgrade is destructive/impossible if we generated new Integer IDs.
    # For the purpose of "Phase IV", we acknowledge downgrade limitations.
    pass
