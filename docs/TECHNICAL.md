# Azeroth Bound Bot - Technical Documentation

**Version:** 2.0.0 (Schema Reformation)
**Architecture:** Path B (Webhook-Driven)
**Last Updated:** December 16, 2025

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Schema Reformation: What Changed](#schema-reformation-what-changed)
3. [Project Structure](#project-structure)
4. [Data Schema: 27-Column Architecture](#data-schema-27-column-architecture)
5. [Enum Definitions](#enum-definitions)
6. [Character Lifecycle State Machine](#character-lifecycle-state-machine)
7. [Interactive Flow System](#interactive-flow-system)
8. [Webhook Architecture (Path B)](#webhook-architecture-path-b)
9. [Commands Reference](#commands-reference)
10. [Core Services](#core-services)
11. [Embed Utilities](#embed-utilities)
12. [Data Models](#data-models)
13. [Environment Configuration](#environment-configuration)
14. [Development Setup](#development-setup)
15. [Testing Strategy](#testing-strategy)
16. [Deployment](#deployment)
17. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The Azeroth Bound Bot is a Discord bot for World of Warcraft Classic+ guild management, handling character registration, approval workflows, and lifecycle management through a **webhook-driven architecture** (Path B).

### The Hybrid Wisdom Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA FLOW DIAGRAM                         │
└─────────────────────────────────────────────────────────────────┘

USER ACTIONS (Discord)
    ↓
DISCORD BOT COMMANDS (/register_character, /bury)
    ↓
IMMEDIATE VALIDATION & INTERACTIVE FLOW
    ↓
WRITE TO GOOGLE SHEETS (Source of Truth)
    ↓
GOOGLE APPS SCRIPT WEBHOOK TRIGGERS
    ↓
SENDS HTTP POST TO BOT'S /webhook ENDPOINT
    ↓
BOT PROCESSES TRIGGER & TAKES DISCORD ACTIONS
    ↓
BOT UPDATES GOOGLE SHEETS WITH RESULTS
    ↓
CYCLE COMPLETES ✅
```

###Key Architectural Principles

1. **Google Sheets = Source of Truth** - All state lives here
2. **Discord Commands = Instant UX** - User sees immediate feedback
3. **Webhooks = Zero Polling** - Instant sheet changes → Discord actions
4. **Bot Writes, Webhooks Read** - Clean separation of concerns
5. **Atomic Operations** - State changes are transactional

### System Components

```
┌──────────────────────────────────────────────────────────┐
│               Discord Bot (Python 3.10+)                 │
│         (discord.py 2.3.2 • Interactive Flows)          │
└───────────┬──────────────────────────┬───────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────────┐    ┌──────────────────────────┐
│  Interactive Commands │    │   Webhook Handler        │
│  • /register_character│    │   • /webhook endpoint    │
│    (12-step flow)     │    │   • Secret validation    │
│  • /bury              │    │   • Trigger routing      │
│    (6-step ceremony)  │    │                          │
└───────────┬───────────┘    └────────────┬─────────────┘
            │                             │
            ▼                             ▼
┌─────────────────────────────────────────────────────────┐
│              Character Registry Service                 │
│  • 27-column schema operations                          │
│  • Field mapping & validation                           │
│  • Lifecycle state management                           │
└───────────┬─────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│          Google Sheets (Database of Record)             │
│  • Character_Submissions (27 columns)                   │
│  • Automated daily backups (7-day retention)            │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│         Google Apps Script (Webhook Trigger)            │
│  • onChange trigger → webhook.gs                        │
│  • Daily backup → backup.gs (2 AM)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Schema Reformation: What Changed

### Major Changes from 1.x to 2.0

| Aspect | Old (1.x) | New (2.0 Schema Reformation) |
|--------|-----------|------------------------------|
| **Architecture** | Polling-based (60s interval) | Webhook-driven (instant) |
| **Schema** | 22 columns | **27 columns** |
| **Character Registration** | Single slash command | **Interactive 12-step flow** |
| **Burial Command** | Simple /bury | **Interactive 6-step ceremony** |
| **Races** | Generic (no enforcement) | **11 defined options** |
| **Classes** | 9 Classic WoW | 9 Classic WoW (unchanged) |
| **Roles** | Single string | **Multi-select (5 options, min 1)** |
| **Professions** | Comma-separated | **Multi-select (12+ options, optional)** |
| **Approval** | Polling Google Sheets | **Webhook triggers** |
| **Deployment** | Railway.com (no longer free) | **Fly.io or Render.com (free)** |
| **Backups** | Manual | **Automated daily (7-day retention)** |

### New Schema Fields (27 Columns)

Five new columns added:

1. **death_cause** - Brief death description (e.g., "Fell defending Southshore")
2. **death_story** - IC death narrative (max 1024 chars)
3. **created_at** - Row creation timestamp (auto)
4. **updated_at** - Last modification timestamp (auto)
5. **notes** - Admin-only notes (manual)

---

## Project Structure

```
azeroth_bound_bot/
├── main.py                      # Entry point, bot initialization
├── config/
│   └── settings.py              # Environment configuration
├── services/
│   ├── discord_client.py        # Bot setup, cog loading
│   ├── sheets_service.py        # Google Sheets (27-col schema)
│   └── webhook_handler.py       # Webhook endpoint & routing
├── commands/
│   ├── character_commands.py    # /register_character (interactive)
│   └── officer_commands.py      # /bury (interactive ceremony)
├── flows/
│   ├── registration_flow.py     # 12-step registration flow
│   └── burial_flow.py           # 6-step burial ceremony
├── handlers/
│   ├── reaction_handler.py      # Approval/rejection reactions
│   └── webhook_triggers.py      # Trigger-specific handlers
├── domain/
│   ├── models.py                # Character, enums, ClassMetadata
│   ├── approval.py              # Approval workflow logic
│   └── validators.py            # Enum & field validation
├── utils/
│   └── embed_parser.py          # Embed serialization/deserialization
├── docs/                        # Documentation
│   ├── TECHNICAL.md             # This file
│   ├── USER_GUIDE.md            # Player-facing guide
│   ├── OFFICER_GUIDE.md         # Officer manual
│   ├── DEPLOYMENT_GUIDE.md      # Hosting setup
│   ├── GOOGLE_APPS_SCRIPT_SETUP.md  # Webhook & backup setup
│   ├── TESTING_GUIDE.md         # QA procedures
│   └── CLAUDE_CODE_OPERATIONS.md    # Development patterns
├── google_apps_script/
│   ├── webhook.gs               # onChange trigger script
│   └── backup.gs                # Daily backup script
├── .env                         # Environment variables (not in git)
├── .env.example                 # Template
├── credentials.json             # Google service account (not in git)
└── requirements.txt             # Python dependencies
```

---

## Data Schema: 27-Column Architecture

### Character_Submissions Sheet

| # | Column Name | Type | Required | Default | Source | Notes |
|---|-------------|------|----------|---------|--------|-------|
| 1 | timestamp | datetime | Yes | AUTO | Auto-generated | ISO 8601 format |
| 2 | discord_id | string | Yes | AUTO/PARAM | From user OR parameter | User's Discord ID |
| 3 | discord_name | string | No | AUTO | Discord API | username#discriminator |
| 4 | char_name | string | Yes | PARAM | User input | Character's name |
| 5 | race | enum | Yes | PARAM | User selection | 11 options (see below) |
| 6 | class | enum | Yes | PARAM | User selection | 9 Classic WoW classes |
| 7 | roles | string | Yes | PARAM | Multi-select | Comma-separated, min 1 |
| 8 | professions | string | No | PARAM | Multi-select | Comma-separated, optional |
| 9 | backstory | text | Yes | PARAM | User input | Max 1024 chars |
| 10 | personality | text | No | PARAM | User input | Max 1024 chars, optional |
| 11 | quotes | text | No | PARAM | User input | Max 1024 chars, optional |
| 12 | portrait_url | string | No | DEFAULT | User input or default | Falls back to config |
| 13 | trait_1 | string | Yes | PARAM | Extracted from personality | First visible trait |
| 14 | trait_2 | string | Yes | PARAM | Extracted from personality | Second visible trait |
| 15 | trait_3 | string | Yes | PARAM | Extracted from personality | Third visible trait |
| 16 | status | enum | Yes | PENDING | Bot logic | See lifecycle states |
| 17 | confirmation | bool | Yes | FALSE | User confirms | TRUE = confirmed |
| 18 | request_sdxl | bool | Yes | FALSE | User requests | AI portrait flag |
| 19 | recruitment_msg_id | snowflake | No | AUTO | Bot writes | Discord message ID |
| 20 | forum_post_url | string | No | AUTO | Bot writes | URL to forum thread |
| 21 | reviewed_by | snowflake | No | AUTO | Officer action | Officer's Discord ID |
| 22 | embed_json | json | Yes | AUTO | Bot writes | Canonical embed source |
| 23 | death_cause | string | No | PARAM | /bury input | Brief death description |
| 24 | death_story | text | No | PARAM | /bury input | IC death narrative |
| 25 | created_at | datetime | Yes | AUTO | Row creation | Timestamp |
| 26 | updated_at | datetime | Yes | AUTO | Row modification | Timestamp |
| 27 | notes | text | No | MANUAL | Admin writes | Admin-only notes |

### Schema Validation

On initialization, the `CharacterRegistryService` validates:

- All 27 columns present in correct order
- Column headers match expected names exactly
- No duplicate column names

**If validation fails:** Bot refuses to start with clear error message.

---

## Enum Definitions

### Valid Races (11 Options)

```python
VALID_RACES = [
    # Alliance
    "Human",
    "Dwarf",
    "Night Elf",
    "Gnome",
    "High Elf",

    # Horde
    "Orc",
    "Undead",
    "Tauren",
    "Troll",
    "Goblin",

    # Special/Rare
    "Other"
]
```

### Valid Classes (9 Classic WoW)

```python
VALID_CLASSES = [
    "Warrior",
    "Paladin",
    "Hunter",
    "Rogue",
    "Priest",
    "Shaman",
    "Mage",
    "Warlock",
    "Druid"
]
```

### Valid Roles (5 Options, Multi-Select, Min 1)

```python
VALID_ROLES = [
    "Tank",
    "Healer",
    "Melee DPS",
    "Ranged DPS",
    "Support"
]
```

**Validation:**
- User must select at least 1 role
- Multiple roles allowed (e.g., "Tank, Melee DPS")
- Stored as comma-separated string in `roles` column

### Valid Professions (12 Options, Multi-Select, Optional)

```python
VALID_PROFESSIONS = [
    "Alchemy",
    "Blacksmithing",
    "Enchanting",
    "Engineering",
    "Herbalism",
    "Leatherworking",
    "Mining",
    "Skinning",
    "Tailoring",
    "Jewelcrafting",
    "First Aid",
    "Cooking",
    "Fishing",
    "Survival"
]
```

**Validation:**
- Optional (can be empty)
- Maximum 2 main professions + 4 secondary (standard WoW rules)
- Stored as comma-separated string

### Status Enum

```python
STATUS_PENDING = "PENDING"       # Awaiting officer approval
STATUS_REGISTERED = "REGISTERED" # Active in #character-sheet-vault
STATUS_REJECTED = "REJECTED"     # Officer rejected
STATUS_DECEASED = "DECEASED"     # Triggers burial workflow
STATUS_BURIED = "BURIED"         # Final state, in #cemetery
STATUS_RETIRED = "RETIRED"       # Hit 60, earned "Immortal" title
```

---

## Character Lifecycle State Machine

```
    [User uses /register_character]
                ↓
    ┌───────────────────────┐
    │ Interactive Flow      │
    │ (12 steps)            │
    │ confirmation: FALSE   │
    └───────────────────────┘
                ↓
    [User completes flow & confirms]
                ↓
    ┌───────────────────────┐
    │ Google Sheets Entry   │
    │ Status: PENDING       │
    │ Confirmation: TRUE    │ ← Webhook Trigger #1
    └───────────────────────┘
                ↓
    [Bot posts to #recruitment with @Pathfinder @Trailwarden]
                ↓
         ┌──────────┴──────────┐
         ↓                     ↓
    [Officer ✅]          [Officer ❌]
         ↓                     ↓
    ┌─────────────┐      ┌─────────────┐
    │ REGISTERED  │      │ REJECTED    │
    │ Creates     │      │ DM sent     │
    │ forum post  │      │ No forum    │
    └─────────────┘      └─────────────┘
         ↓
    [Character lives in #character-sheet-vault]
         ↓
    [Officer uses /bury command]
         ↓
    ┌───────────────────────┐
    │ Status: DECEASED      │ ← Webhook Trigger #2
    └───────────────────────┘
         ↓
    [Bot atomically performs burial ceremony]
         ↓
    ┌───────────────────────┐
    │ Status: BURIED        │
    │ Forum post in         │
    │ #cemetery             │
    └───────────────────────┘
```

---

## Interactive Flow System

### Design Philosophy

All user-facing commands use **interactive flows** for maximum UX quality:

- **Step-by-step guidance** with validation at each step
- **In-character narration** by Chronicler Thaldrin
- **Discord UI components**: buttons, dropdowns, text modals
- **Timeout handling**: Flows expire after configured time (default: 300s)
- **Cancel/restart**: Users can abort and start over

### Flow Architecture

```python
class InteractiveFlow:
    """Base class for all interactive flows"""

    def __init__(self, interaction, timeout=300):
        self.interaction = interaction
        self.timeout = timeout
        self.current_step = 0
        self.data = {}

    async def start(self):
        """Begin the flow"""

    async def next_step(self):
        """Advance to next step"""

    async def validate_step(self, user_input):
        """Validate current step input"""

    async def handle_timeout(self):
        """Handle flow timeout"""

    async def finalize(self):
        """Complete the flow and write to sheets"""
```

### Registration Flow (12+ Steps)

See [Interactive Flow Design](#interactive-flow-design-registercharacter) section below for complete walkthrough.

**Key Features:**
- IC narration by Chronicler Thaldrin
- Class-specific responses (e.g., dwarf reacts differently to "Dwarf" race)
- Portrait options (URL, default, or request AI generation)
- Live embed preview before final confirmation
- Full validation chain

### Burial Flow (6+ Steps)

See [Interactive Flow Design](#interactive-flow-design-bury) section below for complete ceremonial walkthrough.

**Key Features:**
- Solemn, ceremonial IC tone
- Character search and verification
- Death cause and eulogy input
- Final confirmation with summary
- Atomic execution (all or nothing)

---

## Webhook Architecture (Path B)

### Why Webhooks?

**Path B Benefits:**
1. **Zero polling** = Lower resource usage
2. **Instant updates** = Better UX (sub-second responses)
3. **Sheets = Admin interface** = Easy bulk edits/audits
4. **All free tier limits satisfied** ✅

**Total Monthly Cost: $0.00** (with Fly.io or Render.com)

### Webhook Trigger Matrix

| Trigger Condition | Bot Action | Updates to Sheets |
|-------------------|------------|-------------------|
| `confirmation=TRUE` + `status=PENDING` | Post to #recruitment, add ✅❌ reactions, mention @Pathfinder @Trailwarden, DM user | Sets `recruitment_msg_id` |
| Officer reacts ✅ on recruitment msg | Create #character-sheet-vault forum post, update status to REGISTERED, DM user approval | Sets `status=REGISTERED`, `forum_post_url`, `reviewed_by` |
| Officer reacts ❌ on recruitment msg | Update status to REJECTED, DM user rejection notice | Sets `status=REJECTED`, `reviewed_by` |
| `status=DECEASED` (from REGISTERED) | Move forum post to #cemetery, apply IC formatting, post death_story, notify owner via DM, notify @everyone in cemetery | Sets `status=BURIED`, updates `forum_post_url`, `updated_at` |

### Webhook Endpoint: /webhook

**URL Format:** `https://your-bot-domain.fly.dev/webhook`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Payload:**
```json
{
  "secret": "your_webhook_secret_here",
  "trigger": "POST_TO_RECRUITMENT",
  "row_number": 5,
  "character": {
    "timestamp": "2025-12-16T10:30:00Z",
    "discord_id": "123456789",
    "char_name": "Thorgar",
    "class": "Warrior",
    "status": "PENDING",
    "confirmation": true,
    "embed_json": "[...]",
    ...
  },
  "timestamp": "2025-12-16T10:30:05Z"
}
```

**Response:**
- `200 OK` - Webhook processed successfully
- `400 Bad Request` - Invalid payload or secret
- `500 Internal Server Error` - Processing failed

### Security

**Webhook Secret Validation:**

All webhook requests must include a secret that matches `WEBHOOK_SECRET` in bot's `.env`:

```python
async def handle_webhook(request):
    data = await request.json()

    if data.get("secret") != settings.WEBHOOK_SECRET:
        return web.Response(status=400, text="Invalid secret")

    # Process webhook...
```

**Best Practices:**
- Generate random 32+ character secret
- Never commit to git
- Match exactly between bot .env and Google Apps Script
- Rotate periodically (every 90 days recommended)

---

## Commands Reference

### /register_character (Interactive Flow)

**Version:** 2.0 (Schema Reformation)
**Flow Steps:** 12+
**Estimated Time:** 5-10 minutes

**Permissions Required:**
- Wanderer, Seeker, Pathfinder, or Trailwarden role

**Usage:**
```
/register_character
```

**No parameters** - All input gathered through interactive flow!

#### Flow Overview

1. **Introduction** - Chronicler Thaldrin introduces himself, confirms Discord identity
2. **The Name** - Character's full name (1-100 chars)
3. **The Bloodline** - Race selection (dropdown, 11 options)
4. **The Calling** - Class selection (dropdown, 9 options)
5. **The Roles** - Role selection (multi-select checkboxes, min 1)
6. **The Crafts** - Profession selection (multi-select, optional)
7. **The Three Traits** - External visible traits (3 inputs)
8. **The Tale** - Backstory (text area, max 1024 chars)
9. **The Soul** - Personality (text area, optional, max 1024 chars)
10. **The Words** - Memorable quotes (text area, optional, max 1024 chars)
11. **The Visage** - Portrait URL, default, or request AI (3 buttons)
12. **The Preview** - Shows actual embed preview, confirm/restart/cancel
13. **The Inscription** - Final confirmation, writes to sheets, triggers workflow

#### Example Interaction

**Step 1 (Introduction):**
```
🏛️ A massive tome materializes before you, its pages shimmering
   with arcane energy. An elderly dwarf with a magnificent beard
   looks up from his writing desk.

   Greetings, brave soul! I am Chronicler Thaldrin, Keeper of
   Knowledge from the Grand Library of Ironforge.

   May I record your Discord identity for our records?

   Your Discord ID: @User#1234

   [✅ Yes, record my identity]  [❌ No, remain anonymous]
```

**Step 3 (Bloodline):**
```
⚔️ CHAPTER TWO: THE BLOODLINE

   From which people dost thou hail, User? The blood of your
   ancestors flows through your veins—whose legacy do you carry?

   Choose your heritage:

   [Dropdown:]
   🦁 Human (Stormwind's versatile champions)
   ⛰️ Dwarf (Ironforge's stout-hearted warriors)
   🌙 Night Elf (Kalimdor's ancient guardians)
   ⚙️ Gnome (Gnomeregan's ingenious tinkers)
   ✨ High Elf (Quel'Thalas's noble descendants)
   ─────────
   🔥 Orc (Durotar's honorable warriors)
   💀 Undead (Forsaken souls of free will)
   🐂 Tauren (Thunder Bluff's noble nomads)
   🗿 Troll (Darkspear's cunning survivors)
   💰 Goblin (Horde-joined shrewd merchants)
   ─────────
   ❓ Other (Unique or mixed heritage)
```

**Step 12 (Preview):**
```
📋 THE CHRONICLE PREVIEW

   *The tome's pages shimmer and reorganize themselves, revealing
   your completed character sheet*

   Behold! This is how your legend shall appear in our eternal archives:

   [ACTUAL EMBED PREVIEW DISPLAYED]

   Does this look correct?

   [✅ Yes, inscribe this into legend!]
   [🔄 No, let me start over]
   [❌ Cancel registration]
```

#### Validation

Each step validates input before proceeding:

- **Name:** 1-100 characters
- **Race:** Must be in VALID_RACES enum
- **Class:** Must be in VALID_CLASSES enum
- **Roles:** At least 1 selected
- **Professions:** Max 2 main + 4 secondary (standard WoW limits)
- **Traits:** 3 required
- **Backstory:** Required, max 1024 chars
- **Personality:** Optional, max 1024 chars
- **Quotes:** Optional, max 1024 chars
- **Portrait URL:** Must start with http:// or https://, or use default

#### Error Handling

- **Timeout (300s):** Flow expires, user must restart
- **Invalid input:** Re-prompt with guidance
- **Cancel:** Gracefully abort, no data saved
- **Restart:** Clear data, begin from step 1

#### Final Actions

Upon confirmation (✅):

1. **Write to Google Sheets** with all 27 columns
2. **Set status=PENDING, confirmation=TRUE**
3. **Trigger webhook** (POST_TO_RECRUITMENT)
4. **DM user** with confirmation message
5. **Post ephemeral response** in command channel

---

### /bury (Interactive Ceremony)

**Version:** 2.0 (Schema Reformation)
**Flow Steps:** 6+
**Estimated Time:** 3-5 minutes

**Permissions Required:**
- Pathfinder or Trailwarden role

**Usage:**
```
/bury
```

**No parameters** - All input gathered through interactive flow!

#### Flow Overview

1. **Solemn Introduction** - Chronicler's somber tone, explains ceremony
2. **Character Search** - Input name or forum post ID
3. **Verification** - Confirm correct character with preview
4. **Death Circumstances** - Brief death cause (1-2 sentences)
5. **The Eulogy** - Optional IC death story (max 1024 chars)
6. **Final Confirmation** - Summary of actions, confirm/cancel
7. **The Rite** - Atomic execution: cemetery thread, updates sheets, notifications

#### Example Interaction

**Step 1 (Introduction):**
```
⚰️ *The chronicler's expression grows somber. He reaches for a
   black-bound tome adorned with silver runes.*

   Officer... you invoke the Rite of Remembrance.

   This is a sacred duty—to record the fall of a hero and ensure
   their deeds are never forgotten.

   Which hero has fallen?

   Provide the character's name OR forum post ID:

   [Text Input]

   [Continue]  [Cancel ceremony]
```

**Step 3 (Verification):**
```
*The pages flip on their own, revealing a record*

⚔️ THORGAR IRONFORGE
Race: Dwarf • Class: Warrior • Status: REGISTERED
Registered: 2025-12-10
Forum post: #character-sheet-vault/thread-12345

Is this the fallen hero?

[✅ Yes, this is correct]  [🔍 No, search again]
```

**Step 6 (Final Confirmation):**
```
⚰️ THE RITE OF REMEMBRANCE - FINAL CONFIRMATION

You are about to perform the following:

📋 Summary:
• Character: Thorgar Ironforge (Dwarf Warrior)
• Death cause: Fell defending Southshore, level 42
• Eulogy: [shows preview]

🔄 What will happen:
1. Character status set to DECEASED in archives
2. Forum post moved: Character Vault → Cemetery
3. Ceremonial formatting applied (silver borders, tombstone)
4. Death story posted under memorial
5. Character's owner (discord_id) notified via DM
6. @everyone notification in cemetery
7. Status marked as BURIED

⚠️ This action cannot be undone.

Proceed with the burial rite?

[⚰️ Yes, proceed with burial]  [❌ Cancel ceremony]
```

#### Atomic Execution

Upon final confirmation, the bot performs ALL actions atomically:

1. **Update sheets:** status=DECEASED
2. **Trigger webhook:** INITIATE_BURIAL
3. **Create cemetery thread** with ceremonial embed
4. **Copy original embeds** to cemetery
5. **Update sheets:** status=BURIED, forum_post_url (cemetery)
6. **Archive original thread**
7. **DM character owner**
8. **Notify @everyone in cemetery**

**If ANY step fails:** Rollback all changes, report error to officer.

---

## Core Services

### CharacterRegistryService (27-Column)

**File:** `services/sheets_service.py`

Handles all Google Sheets operations with 27-column schema.

#### Initialization

```python
from services.sheets_service import CharacterRegistryService

registry = CharacterRegistryService()
```

**On init:**
1. Connects to Google Sheets API
2. Reads row 1 as schema (27 columns)
3. Builds column mapping: `name → index`
4. Validates all required columns present
5. Logs schema info

**Throws:** `ValueError` if required columns missing or schema invalid

#### Core Methods

**log_character(character_data: dict) → bool**

Appends character to sheet with all 27 columns.

```python
success = registry.log_character({
    # Identity (3)
    "timestamp": "2025-12-16T10:30:00Z",
    "discord_id": "123456789",
    "discord_name": "User#1234",

    # Character Data (9)
    "char_name": "Thorgar",
    "race": "Dwarf",
    "class": "Warrior",
    "roles": "Tank, Melee DPS",
    "professions": "Mining, Blacksmithing",
    "backstory": "Born in the depths...",
    "personality": "Stoic, Loyal, Fearless",
    "quotes": "For Khaz Modan!|No dwarf left behind",
    "portrait_url": "https://...",

    # Traits (3)
    "trait_1": "Stoic",
    "trait_2": "Loyal",
    "trait_3": "Fearless",

    # Lifecycle (4)
    "status": "PENDING",
    "confirmation": "TRUE",
    "request_sdxl": "FALSE",
    "embed_json": serialize_embeds(embeds),

    # Approval (3)
    "recruitment_msg_id": "",
    "forum_post_url": "",
    "reviewed_by": "",

    # Death (2)
    "death_cause": "",
    "death_story": "",

    # Timestamps (2)
    "created_at": "2025-12-16T10:30:00Z",
    "updated_at": "2025-12-16T10:30:00Z",

    # Admin (1)
    "notes": ""
})
```

**update_character_status(char_name: str, new_status: str, **kwargs) → bool**

Updates character status and optional fields.

```python
registry.update_character_status(
    "Thorgar",
    "BURIED",
    death_cause="Fell defending Southshore",
    death_story="In the twilight of his 42nd season...",
    forum_post_url="https://discord.com/channels/.../cemetery/...",
    updated_at="2025-12-16T15:45:00Z"
)
```

**get_character_by_name(char_name: str) → dict**

Retrieves character data by name.

```python
character = registry.get_character_by_name("Thorgar")
# Returns dict with all 27 columns
```

**get_characters_by_user(discord_id: str) → List[dict]**

Retrieves all characters for a Discord user.

```python
user_chars = registry.get_characters_by_user("123456789")
# Returns list of character dicts
```

#### Field Mapping

The service maps intuitive field names to sheet column names:

```python
FIELD_MAPPING = {
    "name": "char_name",
    "role": "roles",
    "class": "class",
    "discord_id": "discord_id",
    # ... etc
}
```

This allows code to use readable names while respecting sheet schema.

---

### WebhookHandler

**File:** `services/webhook_handler.py`

Handles incoming webhooks from Google Apps Script.

#### Initialization

```python
from services.webhook_handler import WebhookHandler

handler = WebhookHandler(bot)
```

#### Webhook Routing

```python
async def handle_webhook(request):
    """Main webhook endpoint"""
    data = await request.json()

    # Validate secret
    if data.get("secret") != settings.WEBHOOK_SECRET:
        return web.Response(status=400, text="Invalid secret")

    # Route to trigger handler
    trigger_type = data.get("trigger")
    character_data = data.get("character")

    if trigger_type == "POST_TO_RECRUITMENT":
        await handle_post_to_recruitment(character_data)
    elif trigger_type == "INITIATE_BURIAL":
        await handle_initiate_burial(character_data)
    else:
        return web.Response(status=400, text="Unknown trigger")

    return web.Response(status=200, text="OK")
```

#### Trigger Handlers

**handle_post_to_recruitment(character_data: dict)**

Triggered when `confirmation=TRUE` + `status=PENDING`.

Actions:
1. Parse embed_json from character_data
2. Post to #recruitment channel
3. Add ✅ and ❌ reactions
4. Mention @Pathfinder @Trailwarden
5. DM user confirmation
6. Update sheets with recruitment_msg_id

**handle_initiate_burial(character_data: dict)**

Triggered when `status=DECEASED`.

Actions:
1. Fetch character's forum post
2. Create cemetery thread
3. Post ceremonial embed
4. Copy original embeds
5. Update sheets: status=BURIED
6. Archive original thread
7. DM character owner
8. Notify @everyone in cemetery

---

## Embed Utilities

**File:** `utils/embed_parser.py`

Unchanged from 1.x - see existing documentation.

Key functions:
- `serialize_embeds(embeds)` → JSON string
- `parse_embed_json(json_str)` → List[discord.Embed]
- `build_character_embeds(character)` → List[discord.Embed]
- `build_cemetery_embed(name, char_class)` → discord.Embed

---

## Data Models

### Character (Updated for 2.0)

```python
@dataclass
class Character:
    # Identity
    discord_user_id: str
    discord_name: str

    # Character Data
    name: str
    race: str  # Must be in VALID_RACES
    char_class: str  # Must be in VALID_CLASSES
    roles: str  # Comma-separated, min 1
    professions: str  # Comma-separated, optional
    backstory: str
    personality: str  # Optional
    quotes: str  # Optional
    portrait_url: str

    # Traits
    trait_1: str
    trait_2: str
    trait_3: str

    # Lifecycle
    status: str  # Status enum
    confirmation: bool
    request_sdxl: bool

    # Timestamps
    registered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### ClassMetadata

Unchanged from 1.x.

```python
CLASS_DATA: Dict[str, ClassMetadata] = {
    "Warrior": ClassMetadata("Warrior", "⚔️", "#C69B6D"),
    "Paladin": ClassMetadata("Paladin", "🛡️", "#F48CBA"),
    # ... etc
}
```

---

## Environment Configuration

### New Variables (Schema Reformation)

Add to `.env`:

```bash
# ============================================
# SCHEMA REFORMATION - NEW VARIABLES
# ============================================

# Default portrait placeholder (when user doesn't provide one)
DEFAULT_PORTRAIT_URL=https://i.imgur.com/default_placeholder.png

# Webhook secret (generate random string, match in Apps Script)
WEBHOOK_SECRET=your_random_webhook_secret_here_min_32_chars

# Interactive flow timeout (seconds)
INTERACTIVE_TIMEOUT_SECONDS=300

# Officer role mentions (for #recruitment posts)
PATHFINDER_ROLE_MENTION=<@&pathfinder_role_id>
TRAILWARDEN_ROLE_MENTION=<@&trailwarden_role_id>

# Google Drive backup folder ID (for daily backups)
BACKUP_FOLDER_ID=your_google_drive_folder_id_here
```

### Complete .env Template

See `.env.example` for full template with all variables.

---

## Development Setup

### Prerequisites

- Python 3.10+
- Google Cloud service account with Sheets API + Drive API access
- Discord bot with appropriate permissions
- Fly.io or Render.com account (for deployment)

### Local Development

1. **Clone repository**
2. **Create virtual environment:** `python3 -m venv venv && source venv/bin/activate`
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Configure .env:** Copy `.env.example` to `.env` and fill in all variables
5. **Set up Google Sheets credentials:** Download service account JSON as `credentials.json`
6. **Create Google Sheets:** Create Character_Submissions sheet with 27 columns
7. **Run bot:** `python main.py`

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production deployment.

---

## Testing Strategy

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for comprehensive testing procedures.

**Quick Test:**
```bash
./venv/bin/python3 ./sanity_check.py
```

---

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete deployment instructions for:

- **Fly.io** (recommended, 3 free VMs)
- **Render.com** (alternative, 750 hours/month free)

**Quick Deploy (Fly.io):**
```bash
flyctl launch
flyctl secrets set DISCORD_BOT_TOKEN=...
flyctl deploy
```

---

## Troubleshooting

### Common Issues

**Issue:** Webhook not triggering

**Check:**
- Is `onChange` trigger set up in Google Apps Script?
- Is WEBHOOK_URL correct in script?
- Is WEBHOOK_SECRET matching between bot and script?
- Is bot's /webhook endpoint accessible?

**Solution:** Test with `testWebhook()` function in Google Apps Script.

---

**Issue:** Interactive flow not starting

**Check:**
- Does user have required role?
- Is bot online?
- Check bot logs for errors

**Solution:** Verify permissions, restart bot if needed.

---

**Issue:** Schema validation failing

**Error:** `Required columns missing from sheet: death_cause, death_story, created_at, updated_at, notes`

**Solution:** Add the 5 new columns to Character_Submissions sheet. Full 27-column list:

```
timestamp, discord_id, discord_name, char_name, race, class, roles,
professions, backstory, personality, quotes, portrait_url, trait_1,
trait_2, trait_3, status, confirmation, request_sdxl, recruitment_msg_id,
forum_post_url, reviewed_by, embed_json, death_cause, death_story,
created_at, updated_at, notes
```

---

For additional troubleshooting, see [USER_GUIDE.md](./USER_GUIDE.md) and [OFFICER_GUIDE.md](./OFFICER_GUIDE.md).

---

## Appendix

### Version History

- **1.0.0** - Initial release (22 columns, polling)
- **1.1.0** - Added lifecycle fields, embed_json canonical source
- **2.0.0** - Schema Reformation (27 columns, webhooks, interactive flows)

### Migration from 1.x to 2.0

1. **Backup existing Google Sheets**
2. **Add 5 new columns:** death_cause, death_story, created_at, updated_at, notes
3. **Update .env with new variables**
4. **Set up Google Apps Script** (webhook.gs, backup.gs)
5. **Deploy bot to Fly.io or Render.com**
6. **Test interactive flows**
7. **Verify webhooks working**

### Contributors

- Chronicler Thaldrin, Keeper of Knowledge
- The Development Team
- The Community

---

**For Azeroth Bound! For Excellence! For The Chronicle!** ⚔️

*Last updated: December 16, 2025*
*Version: 2.0.0*
*Status: Production Ready*
