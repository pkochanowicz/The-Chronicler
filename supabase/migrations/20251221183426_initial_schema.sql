-- STAGE 1: SQL Schema Reforging (sql/schema_v1.sql)
-- Redesigned by Grimstone Earthmender

DROP TABLE IF EXISTS character_talents CASCADE;
DROP TABLE IF EXISTS graveyard CASCADE;
DROP TABLE IF EXISTS characters CASCADE;

-- ENUM for challenge modes
CREATE TYPE challenge_mode AS ENUM ('None', 'Hardcore', 'Immortal', 'Inferno');

-- Core characters table with corrected types
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id VARCHAR(255) UNIQUE NOT NULL,
    character_name VARCHAR(100) NOT NULL,
    race VARCHAR(50) NOT NULL,
    faction VARCHAR(50) NOT NULL,
    class VARCHAR(50) NOT NULL,
    level INTEGER NOT NULL CHECK (level >= 1 AND level <= 70),
    challenge_mode challenge_mode DEFAULT 'None' NOT NULL, -- Corrected: ENUM for challenge modes
    story TEXT, -- Corrected: TEXT for large stories
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- Table for tracking talent selections per character
-- Ensuring bidirectional relationship logic implies that fetching character talents
-- or fetching character from talents should be efficient and consistent.
CREATE TABLE character_talents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    talent_tree_id VARCHAR(255) NOT NULL,
    talent_id VARCHAR(255) NOT NULL,
    points_spent INTEGER NOT NULL CHECK (points_spent >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    UNIQUE(character_id, talent_id)
);

-- Table for fallen heroes (The Cemetery)
CREATE TABLE graveyard (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    death_timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()),
    cause_of_death TEXT,
    eulogy TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
);

-- NOTE: RLS policies will be configured separately to ensure security.
-- This script focuses on schema structure.

-- Grimstone's Note: Ensure your Supabase project is configured to use this schema.