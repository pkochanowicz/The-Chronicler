# Data Architecture Decision Record

**Date:** 2025-12-30
**Status:** DECISION REQUIRED
**Context:** Database scope rationalization for The Chronicler

---

## Executive Summary

**RECOMMENDATION:** Remove or depopulate game data tables (`items`, `npcs`, `quests`, `spells`, `factions`) from The Chronicler database. Use external APIs or pfUI data sources instead.

**Rationale:** The Chronicler should focus on **guild-specific data**, not duplicate the entire Turtle WoW game database.

---

## Current Database Schema Analysis

### Guild-Specific Tables (✅ KEEP)
These tables store unique guild data that cannot be sourced elsewhere:

| Table | Purpose | Status |
|-------|---------|--------|
| `characters` | Player character registry | ✅ Essential |
| `character_talents` | Talent allocations | ✅ Essential |
| `graveyard` | Death records | ✅ Essential |
| `guild_bank_items` | Bank inventory | ✅ Essential |
| `guild_bank_transactions` | Transaction history | ✅ Essential |
| `images` | Uploaded image metadata | ✅ Essential |

**Recommendation:** **KEEP ALL** — These are the core of The Chronicler's functionality.

---

### Game Data Tables (⚠️ BLOAT RISK)

Currently defined in `schemas/db_schemas.py`:

| Table | Purpose | Risk Assessment |
|-------|---------|-----------------|
| `items` | WoW items database | ⚠️ **BLOAT** — 10,000+ items in Turtle WoW |
| `item_sets` | Item set bonuses | ⚠️ **BLOAT** — Hundreds of sets |
| `npcs` | NPC database | ⚠️ **BLOAT** — Thousands of NPCs |
| `quests` | Quest database | ⚠️ **BLOAT** — 5,000+ quests |
| `spells` | Spell database | ⚠️ **BLOAT** — 10,000+ spells |
| `factions` | Faction data | ⚠️ **BLOAT** — Hundreds of factions |
| `talent_trees` | Class talent trees | ✅ **KEEP** — Only ~27 trees (9 classes × 3 trees) |
| `talents` | Individual talents | ✅ **KEEP** — Only ~500 total talents |

**Key Questions:**
1. Are these tables currently populated?
2. Where would data come from?
3. Do we actually need this data stored locally?

---

## pfUI-turtle Analysis

### Repository Investigation

**Cloned & Analyzed:**
- `https://github.com/shagu/pfUI` (base UI mod)
- `https://github.com/doorknob6/pfUI-turtle` (Turtle WoW fork)

**Findings:**
```bash
# Repository contents
/tmp/pfUI-turtle/
├── skins/          # UI skin customization (transmog, honor, guild bank UI)
├── modules/        # UI modules (energy tick, auto-shift, champion indicators)
├── tests/          # Test files
└── init/           # Initialization scripts

# No game data found:
- ❌ No item database
- ❌ No NPC database
- ❌ No quest database
- ❌ No spell database
```

**Conclusion:** pfUI-turtle is a **UI customization mod**, not a game data source. It does not contain structured item/NPC/quest databases that we could parse.

---

## External Data Source Options

### Option 1: Turtle WoW Database API (PREFERRED)

**Check for official Turtle WoW database:**
- Website: https://turtle-wow.org/
- Potential API: https://database.turtle-wow.org/ (if exists)
- Community tools: Check Discord/Forums for data dumps

**Advantages:**
- ✅ Always up-to-date with server patches
- ✅ No local storage overhead
- ✅ Single source of truth
- ✅ Reduced maintenance burden

**Disadvantages:**
- ⚠️ Dependency on external service availability
- ⚠️ Rate limits may apply
- ⚠️ Requires caching for performance

### Option 2: Classicdb.ch / WoWhead Classic

**Use generic Classic WoW databases:**
- https://classicdb.ch/
- https://classic.wowhead.com/

**Advantages:**
- ✅ Comprehensive, mature APIs
- ✅ Well-documented
- ✅ High availability

**Disadvantages:**
- ❌ **Does not include Turtle WoW custom content**
- ❌ Missing custom items/quests/NPCs unique to Turtle WoW

### Option 3: Local Data Dump (NOT RECOMMENDED)

**Import static data from community sources:**

**Advantages:**
- ✅ No external API dependency
- ✅ Fast lookups

**Disadvantages:**
- ❌ Requires manual updates with each patch
- ❌ Database bloat (10GB+ for full game data)
- ❌ Maintenance nightmare
- ❌ Outdated data after server updates

---

## Recommendation: Hybrid Approach

### Phase 1: Immediate (Do Now)

**1. Keep Talent System Local** ✅
- `talent_trees` and `talents` tables: **KEEP**
- These are static (~500 talents total) and essential for `/talent audit`
- Changes infrequently (only with major patches)
- **Action:** Populate from Google Sheets as currently done

**2. Remove/Depopulate Game Data Tables** ⚠️
- `items`, `npcs`, `quests`, `spells`, `factions`: **REMOVE or leave empty**
- **Action:** Create migration to drop foreign keys and empty these tables
- Keep schema definitions for future use if needed

**3. Implement Lookup Service**
```python
# chronicler/services/game_data_lookup.py

class GameDataLookup:
    """
    External lookup service for Turtle WoW game data.

    Strategy:
    1. Check cache (Redis or in-memory with TTL)
    2. Query external API (Turtle WoW DB or fallback)
    3. Cache result for 24 hours
    """

    async def lookup_item(self, item_id: int) -> dict:
        """Lookup item by ID from external source."""
        ...

    async def lookup_npc(self, npc_id: int) -> dict:
        """Lookup NPC by ID."""
        ...

    async def search_items(self, query: str) -> list[dict]:
        """Search items by name."""
        ...
```

**4. Update Guild Bank**
- Currently references `items.id` foreign key
- **Change:** Store item as `item_id` (integer) + `item_name` (string)
- Remove FK constraint to `items` table
- Fetch item details on-demand when displaying bank inventory

---

### Phase 2: Future Enhancement

**Implement Intelligent Caching**
```python
# Cache frequently accessed items/NPCs in Redis
# TTL: 7 days for items, 30 days for NPCs (change rarely)

class CachedGameData:
    """Redis-backed cache for game data lookups."""

    async def get_item(self, item_id: int) -> dict:
        # Check Redis cache
        # If miss, fetch from API
        # Cache for 7 days
        ...
```

**Add Popular Items to Local DB**
```sql
-- Only cache top 100 most-referenced items/NPCs
-- Auto-populated from guild bank transactions
CREATE TABLE cached_items (
    item_id BIGINT PRIMARY KEY,
    name VARCHAR(256),
    icon_url TEXT,
    quality VARCHAR(32),
    cached_at TIMESTAMP DEFAULT NOW(),
    cache_hits INT DEFAULT 0
);
```

---

## Migration Plan

### Step 1: Assess Current State

```sql
-- Check if game data tables are populated
SELECT COUNT(*) FROM items;       -- Expected: 0 or very few
SELECT COUNT(*) FROM npcs;        -- Expected: 0
SELECT COUNT(*) FROM quests;      -- Expected: 0
SELECT COUNT(*) FROM spells;      -- Expected: 0

-- Check foreign key dependencies
SELECT COUNT(*) FROM guild_bank_items WHERE item_id IS NOT NULL;
```

### Step 2: Decouple Guild Bank

```python
# Migration: alembic/versions/xxx_decouple_guild_bank_from_items.py

def upgrade():
    # Add item_name column to guild_bank_items
    op.add_column('guild_bank_items', sa.Column('item_name', sa.String(256)))

    # Populate item_name from items table (if any data exists)
    op.execute("""
        UPDATE guild_bank_items gbi
        SET item_name = items.name
        FROM items
        WHERE gbi.item_id = items.id
    """)

    # Drop foreign key constraint
    op.drop_constraint('guild_bank_items_item_id_fkey', 'guild_bank_items')

    # item_id now just stores the game's item ID (no FK)
```

### Step 3: Remove/Depopulate Tables

```python
def upgrade():
    # Option A: Drop tables entirely
    op.drop_table('items')
    op.drop_table('item_sets')
    op.drop_table('npcs')
    op.drop_table('quests')
    op.drop_table('spells')
    op.drop_table('factions')

    # Option B: Keep schema, truncate data (more flexible)
    op.execute('TRUNCATE TABLE items CASCADE')
    # ... etc
```

### Step 4: Implement Lookup Service

```python
# chronicler/services/game_data_lookup.py

import aiohttp
from typing import Optional

class TurtleWoWDataLookup:
    """
    Lookup service for Turtle WoW game data.

    TODO: Replace with actual Turtle WoW API once discovered.
    Fallback: Scrape turtle-wow.org database pages.
    """

    BASE_URL = "https://database.turtle-wow.org"  # Hypothetical

    async def lookup_item(self, item_id: int) -> Optional[dict]:
        """
        Lookup item by ID.

        Returns:
            {
                "id": 12345,
                "name": "Thunderfury, Blessed Blade of the Windseeker",
                "quality": "Legendary",
                "icon_url": "https://...",
                "item_level": 80,
                ...
            }
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/item/{item_id}") as resp:
                if resp.status == 200:
                    # Parse JSON or HTML
                    return await resp.json()
        return None

    async def search_items(self, query: str) -> list[dict]:
        """Search items by name."""
        # Implement search API call
        ...
```

---

## Database Size Comparison

### Current Schema (if fully populated):

| Table | Estimated Rows | Storage Size |
|-------|----------------|--------------|
| items | ~15,000 | ~50 MB |
| npcs | ~8,000 | ~30 MB |
| quests | ~6,000 | ~25 MB |
| spells | ~12,000 | ~40 MB |
| **TOTAL** | ~41,000 | ~145 MB |

### Recommended Schema:

| Table | Estimated Rows | Storage Size |
|-------|----------------|--------------|
| characters | ~200 | <1 MB |
| guild_bank_items | ~500 | <1 MB |
| talent_trees | 27 | <1 KB |
| talents | ~500 | <100 KB |
| **TOTAL** | ~1,227 | ~2 MB |

**Savings:** ~143 MB (98% reduction) + eliminated maintenance burden

---

## Decision Matrix

| Factor | Local DB | External API + Cache | Hybrid (Rec.) |
|--------|----------|---------------------|---------------|
| **Data Freshness** | ❌ Manual updates | ✅ Always current | ✅ Current |
| **Performance** | ✅ Fast | ⚠️ Network latency | ✅ Fast (cached) |
| **Storage** | ❌ 145 MB+ | ✅ Minimal | ✅ ~5 MB |
| **Maintenance** | ❌ High | ✅ Low | ✅ Low |
| **Availability** | ✅ Always | ⚠️ Depends on API | ✅ Cached fallback |
| **Turtle WoW Custom Content** | ⚠️ Manual import | ✅ Included | ✅ Included |

**Winner:** Hybrid approach (external API + intelligent caching)

---

## Implementation Checklist

- [ ] Research Turtle WoW database API availability
- [ ] Implement `TurtleWoWDataLookup` service
- [ ] Add Redis caching layer (or in-memory cache with TTL)
- [ ] Create Alembic migration to decouple guild bank from items table
- [ ] Update guild bank commands to use lookup service
- [ ] Remove/truncate game data tables
- [ ] Update `/talent audit` to continue using local talent data
- [ ] Test guild bank functionality with external lookups
- [ ] Document API rate limits and caching strategy
- [ ] Add fallback behavior if external API is unavailable

---

## Long-Term Vision

### Use Cases for Game Data

**Current features that might need game data:**
1. **Guild Bank:** Item names, icons, quality (for display)
2. **Talent Validation:** Talent definitions (**already local**)
3. **Future: Character Gear Lookup?** (Not yet implemented)
4. **Future: Quest Tracking?** (Not yet implemented)

**Conclusion:** Only Guild Bank needs item data, and only for display purposes. External API + caching is sufficient.

---

## Alternatives Considered

### Alternative 1: Keep Local DB, Import pfUI Data

**Rejected because:**
- pfUI-turtle does NOT contain game data
- Would need to find another data source anyway
- Still requires manual updates

### Alternative 2: Scrape Turtle WoW Website

**Possible but not recommended:**
- Legal/ethical concerns
- Fragile (breaks when website changes)
- Slower than API
- Could be blocked

### Alternative 3: Ask Turtle WoW Devs for API Access

**Best long-term solution:**
- Reach out to Turtle WoW team
- Request official API or data dump
- Offer to help maintain/document it

---

## Final Recommendation

**DECISION:** Remove game data tables from production database. Implement external lookup service with caching.

**Rationale:**
1. pfUI-turtle is a UI mod, not a data source
2. Turtle WoW likely has a database website we can query
3. Storing 41,000+ game records is overkill for a 200-member guild bot
4. External API keeps data fresh automatically
5. Caching ensures performance and availability

**Next Steps:**
1. Check https://database.turtle-wow.org/ or similar for API
2. Implement lookup service prototype
3. Create migration to decouple guild bank
4. Test with production guild bank data
5. Deploy

---

*Decision Record — Awaiting Implementation*
*Recommended by Claude Code on 2025-12-30*
