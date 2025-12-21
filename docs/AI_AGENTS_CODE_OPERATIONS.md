# DEPRECATED CONTEXT: This document details AI agent operations and solutions specific to the *previous* Google Sheets-based architecture.
# Please refer to updated documentation for current operational guidelines with the FastAPI/Supabase stack.

# AI Agent Code Operations and Pitfall Management for The Chronicler


**Version:** 2.0.0
**Purpose:** Documented development patterns, architectural decisions, and implementation conventions
**Audience:** Developers, maintainers, future contributors

---

## Table of Contents

1. [Project Philosophy](#project-philosophy)
2. [Architectural Patterns](#architectural-patterns)
3. [Code Organization Principles](#code-organization-principles)
4. [Common Implementation Patterns](#common-implementation-patterns)
5. [Testing Strategies](#testing-strategies)
6. [Documentation Standards](#documentation-standards)
7. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
8. [Future Extensibility](#future-extensibility)

---

## Project Philosophy

### Documentation-Driven Development (DDD)

This project follows a strict Documentation-Driven Development approach:

1. **Documentation First** - All features are fully documented BEFORE implementation
   - docs/MASTER_BLUEPRINT_SCHEMA_REFORMATION.md is the **immutable source of truth**
   - Feature specs written as if the code already exists
   - UI/UX flows described in complete detail

2. **Test Second** - Comprehensive tests written based on documentation
   - Tests validate that implementation matches documentation claims
   - Test-Driven Development (TDD) follows documentation phase
   - Bullet-proof test coverage ensures documentation accuracy

3. **Implementation Last** - Code written to pass tests and match documentation
   - Implementation must satisfy both tests AND documentation
   - No deviation from documented behavior without updating documentation first

**Why This Order?**
- Prevents scope creep
- Ensures complete specifications before coding
- Creates living documentation that never goes stale
- Forces clear thinking about architecture before implementation

---

## Architectural Patterns

### The Hybrid Wisdom Architecture

```
Discord Commands (Immediate UX)
    ↓
Google Sheets (Source of Truth)
    ↓
Google Apps Script Webhooks (Zero Polling)
    ↓
Discord Bot Actions (Instant Response)
```

**Key Principle:** Google Sheets is the database. All state lives there. The bot is stateless and reactive.

### Path B: Webhook-Driven Architecture

**Why webhooks instead of polling?**

| Aspect | Polling (Path A) | Webhooks (Path B) |
|--------|------------------|-------------------|
| Latency | 30-60s average | <1s |
| Resource usage | High (constant requests) | Low (on-demand only) |
| Cost | Scales with users | Free tier sufficient |
| Complexity | Low (simple loop) | Medium (webhook setup) |
| Reliability | Medium (polling failures) | High (Google infrastructure) |

**Chosen:** Path B for production. Path A would work for <10 users but doesn't scale.

### State Machine Design

All character lifecycle states are explicitly modeled:

```
PENDING → REGISTERED → DECEASED → BURIED
            ↓
        REJECTED
```

**Implementation Pattern:**
- Each state transition has a webhook trigger condition
- State changes are atomic (all or nothing)
- Rollback mechanisms for failed transitions
- Logging at every state change

---

## Code Organization Principles

### Directory Structure Philosophy

```
azeroth_bound_bot/
├── commands/           # Discord slash command entry points
├── flows/             # Interactive multi-step flows
├── handlers/          # Event handlers (reactions, webhooks)
├── services/          # External integrations (Sheets, Discord)
├── domain/            # Business logic, models, validators
└── utils/             # Pure functions, helpers
```

**Why this structure?**

1. **Separation of Concerns** - Each directory has one responsibility
2. **Testability** - Pure functions in utils/ are easiest to test
3. **Scalability** - New features fit into existing structure
4. **Clarity** - File location indicates purpose

### The Three-Layer Pattern

Every feature follows three layers:

1. **Presentation Layer** (`commands/`, `flows/`)
   - User-facing interactions
   - Input validation
   - UI/UX concerns
   - No business logic here!

2. **Domain Layer** (`domain/`)
   - Business rules and logic
   - Data models
   - Validation rules
   - Independent of Discord/Sheets

3. **Infrastructure Layer** (`services/`, `handlers/`)
   - External API calls
   - Database operations
   - Webhook handling
   - No business logic here!

**Example: Character Registration**

```python
# commands/character_commands.py (Presentation)
@app_commands.command()
async def register_character(interaction):
    flow = RegistrationFlow(interaction)  # UI logic
    await flow.start()

# flows/registration_flow.py (Presentation)
class RegistrationFlow:
    async def finalize(self):
        character = Character(...)  # Domain model
        registry.log_character(character)  # Infrastructure call

# domain/models.py (Domain)
@dataclass
class Character:
    def validate(self):
        # Business rules here

# services/sheets_service.py (Infrastructure)
class CharacterRegistryService:
    def log_character(self, character):
        # Google Sheets API calls here
```

---

## Common Implementation Patterns

### Pattern 1: Interactive Flows

**Problem:** Slash commands with 10+ parameters are terrible UX

**Solution:** Multi-step interactive flows with validation at each step

```python
class InteractiveFlow:
    def __init__(self, interaction, timeout=300):
        self.interaction = interaction
        self.data = {}
        self.current_step = 0

    async def start(self):
        await self.step_1()

    async def step_1(self):
        # Present UI, wait for response
        # Validate input
        # Store in self.data
        # Advance to step_2

    async def finalize(self):
        # All data collected, perform final action
```

**Why this works:**
- Step-by-step validation prevents bad data
- Users can see progress
- Timeout handling prevents abandoned flows
- Cancel/restart options improve UX

**When to use:**
- Commands with 5+ parameters
- Commands requiring complex validation
- Commands where user needs guidance

---

### Pattern 2: Webhook Trigger Conditions

**Problem:** How do we know when to trigger webhooks?

**Solution:** Explicit state-based conditions in Google Apps Script

```javascript
// webhook.gs
function processRow(row, rowNumber, headers) {
  var status = row[COL_STATUS];
  var confirmation = row[COL_CONFIRMATION];
  var recruitmentMsgId = row[COL_RECRUITMENT_MSG_ID];

  // Trigger 1: User completed registration
  if (confirmation === true && status === "PENDING" && !recruitmentMsgId) {
    sendWebhook("POST_TO_RECRUITMENT", row, rowNumber, headers);
    return;
  }

  // Trigger 2: Officer buried character
  if (status === "DECEASED") {
    sendWebhook("INITIATE_BURIAL", row, rowNumber, headers);
    return;
  }
}
```

**Why this pattern:**
- Conditions are explicit and readable
- Each trigger has a clear purpose
- Early returns prevent multiple triggers
- Easy to add new triggers

**When adding new triggers:**
1. Add condition check in `processRow()`
2. Add handler in bot's `webhook_handler.py`
3. Document in TECHNICAL.md webhook trigger matrix
4. Test with `testWebhook()` function

---

### Pattern 3: Embed JSON as Canonical Source

**Problem:** Discord embeds shown to users might not match database

**Solution:** Store serialized embeds in database, use as single source of truth

```python
# Build embeds
embeds = build_character_embeds(character)

# Serialize IMMEDIATELY
embed_json = serialize_embeds(embeds)

# Store in database
character_data["embed_json"] = embed_json

# Post to Discord (from same embeds)
await channel.send(embeds=embeds)
```

**Why this matters:**
- Future changes to `build_character_embeds()` won't affect old characters
- Character sheets can be reconstructed from database alone
- Export to web dashboard uses same embeds Discord sees
- Historical accuracy preserved

**Common mistake:** Building embeds twice (once for Discord, once for database) → Leads to mismatches

---

### Pattern 4: Schema Validation on Startup

**Problem:** Bot fails at runtime if Google Sheets schema is wrong

**Solution:** Validate schema on initialization, fail fast with clear error

```python
class CharacterRegistryService:
    def __init__(self):
        self.sheet = self._connect_to_sheet()
        self._validate_schema()  # Fail here if schema wrong

    def _validate_schema(self):
        required_columns = [
            "timestamp", "discord_id", "char_name",
            # ... all 27 columns
        ]
        actual_columns = self.sheet.row_values(1)

        missing = set(required_columns) - set(actual_columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
```

**Why fail on startup:**
- Catches configuration errors before they corrupt data
- Clear error messages guide developers to fix
- Prevents partial operations with broken schema

---

## Testing Strategies

### The Three-Phase Testing Approach

Following documentation-driven development:

**Phase 1: Documentation**
- Write complete specs in docs/MASTER_BLUEPRINT_SCHEMA_REFORMATION.md
- Document all edge cases, error conditions, state transitions

**Phase 2: Tests**
- Write tests based on documentation claims
- Tests should fail initially (no implementation yet)
- Cover happy path + all documented edge cases

**Phase 3: Implementation**
- Write code to make tests pass
- Code must also match documentation behavior
- If implementation differs from docs, update docs first

### Test Categories

**1. Unit Tests** (`domain/` and `utils/`)
```python
def test_character_validation():
    character = Character(name="", ...)  # Invalid name
    with pytest.raises(ValidationError):
        character.validate()
```

**2. Integration Tests** (`services/`)
```python
def test_sheets_logging_end_to_end():
    registry = CharacterRegistryService()
    character = Character(...)
    registry.log_character(character)

    # Verify in actual Google Sheets
    rows = registry.sheet.get_all_values()
    assert character.name in rows[-1]
```

**3. Interactive Flow Tests** (`flows/`)
```python
@pytest.mark.asyncio
async def test_registration_flow_happy_path():
    # Mock Discord interaction
    interaction = MockInteraction()
    flow = RegistrationFlow(interaction)

    # Simulate user completing all steps
    await flow.start()
    # ... simulate step completions

    assert flow.data["char_name"] == "Thorgar"
    assert flow.data["status"] == "PENDING"
```

**4. Webhook Tests** (`handlers/`)
```python
@pytest.mark.asyncio
async def test_webhook_post_to_recruitment():
    payload = {
        "secret": "test_secret",
        "trigger": "POST_TO_RECRUITMENT",
        "character": {...}
    }

    response = await handle_webhook(payload)
    assert response.status == 200
    # Verify recruitment post created
```

---

## Documentation Standards

### The Dual-Mode Documentation Principle

This project maintains two documentation styles:

**1. Technical Documentation** (`TECHNICAL.md`, `DEPLOYMENT_GUIDE.md`)
- Audience: Developers
- Voice: Clear, precise, professional
- Content: Architecture, APIs, schemas, deployment
- Goal: Enable developers to build/maintain/deploy

**2. User Documentation** (`USER_GUIDE.md`)
- Audience: Guild members (non-technical)
- Voice: In-character (Chronicler Thaldrin), immersive
- Content: How to use features, troubleshooting
- Goal: Make users ENJOY reading documentation

**Why both?**
- Technical docs become boring for users
- In-character docs confuse developers
- Each audience gets appropriate content

### Documentation Update Workflow

**When adding a feature:**

1. Update `docs/MASTER_BLUEPRINT_SCHEMA_REFORMATION.md` (source of truth)
2. Update `docs/TECHNICAL.md` (technical reference)
3. Update `docs/USER_GUIDE.md` (user-facing guide)
4. Add entry to `docs/CHANGELOG.md`
5. Update `docs/README.md` if navigation changes

**When fixing a bug:**

1. Update `docs/CHANGELOG.md` (under Fixed)
2. Update `docs/TECHNICAL.md` if behavior changes
3. Update `docs/USER_GUIDE.md` if user-visible

**When changing architecture:**

1. Update `docs/MASTER_BLUEPRINT_SCHEMA_REFORMATION.md` FIRST
2. Get approval (architecture changes are major)
3. Update all affected docs
4. Update tests to reflect new architecture
5. Implement changes

---

## Common Pitfalls & Solutions

### Pitfall 1: Google Sheets Column Misalignment

**Symptom:** Data appears in wrong columns after bot writes

**Cause:** Creating row arrays without including ALL columns

**Solution:**
```python
# BAD: Only includes columns with data
row = [timestamp, discord_id, char_name]  # Missing columns!

# GOOD: Creates full row, populates where needed
row = [""] * len(headers)  # All columns
row[col_map["timestamp"]] = timestamp
row[col_map["discord_id"]] = discord_id
```

---

### Pitfall 2: Webhook Secret Mismatch

**Symptom:** Webhooks return 400 Bad Request

**Cause:** `WEBHOOK_SECRET` in bot doesn't match Google Apps Script

**Solution:**
```bash
# Generate once
openssl rand -hex 32

# Set in BOTH places (exact match required)
# 1. Bot's .env file
WEBHOOK_SECRET=abc123...

# 2. Google Apps Script webhook.gs
const WEBHOOK_SECRET = "abc123...";

# Case-sensitive! No extra spaces!
```

---

### Pitfall 3: Interactive Flow State Loss

**Symptom:** Flow data lost between steps

**Cause:** Not storing data in flow instance

**Solution:**
```python
class RegistrationFlow:
    def __init__(self, interaction):
        self.data = {}  # Persistent across steps

    async def step_1(self):
        user_input = await get_input()
        self.data["char_name"] = user_input  # Store here

    async def step_2(self):
        name = self.data["char_name"]  # Access stored data
```

---

### Pitfall 4: Hardcoded Column Indices

**Symptom:** Bot breaks when columns are reordered

**Cause:** Using hardcoded indices instead of column mapping

**Solution:**
```python
# BAD
status = row[15]  # What's column 15?

# GOOD
status_col = headers.index("status")
status = row[status_col]

# BEST (in Google Apps Script)
const COL_STATUS = headers.indexOf("status");
var status = row[COL_STATUS];
```

---

## Future Extensibility

### Adding New Character States

**Current states:** PENDING, REGISTERED, REJECTED, DECEASED, BURIED, RETIRED

**To add new state (e.g., "SUSPENDED"):**

1. Update `domain/models.py` status constants
2. Update state machine diagram in `TECHNICAL.md`
3. Add webhook trigger condition if needed
4. Update `USER_GUIDE.md` with user-facing description
5. Add tests for state transitions
6. Update `CHARACTER.lifecycle_state` enum

---

### Adding New Enum Options

**Example: Adding new race "Blood Elf"**

1. Update `domain/validators.py`:
```python
VALID_RACES = [
    # ... existing races
    "Blood Elf",  # NEW
]
```

2. Update docs/TECHNICAL.md enum list
3. Update docs/USER_GUIDE.md race dropdown example
4. Update interactive flow UI to include new option
5. Test registration with new race

---

### Adding New Webhook Triggers

**Example: Trigger when character reaches level 60**

1. Add new column to Google Sheets schema: `character_level`
2. Update schema validation (now 28 columns)
3. Add trigger condition in `webhook.gs`:
```javascript
if (row[COL_LEVEL] == 60 && row[COL_STATUS] == "REGISTERED") {
    sendWebhook("LEVEL_60_REACHED", row, rowNumber, headers);
}
```

4. Add handler in bot's `webhook_handler.py`:
```python
elif trigger_type == "LEVEL_60_REACHED":
    await handle_level_60(character_data)
```

5. Document in webhook trigger matrix
6. Test end-to-end

---

### Performance Optimization Patterns

**Current bottlenecks:**

1. **Forum thread fetching** - `/bury` iterates all threads
   - Future: Cache thread IDs in memory
   - Future: Index threads by character name

2. **Google Sheets API calls** - Each write is a network round-trip
   - Future: Batch writes when possible
   - Current: Within free tier limits, not urgent

3. **Interactive flow state** - Stored in memory (lost on restart)
   - Future: Persist to Redis for bot restarts
   - Current: 300s timeout prevents issues

---

## Advanced Patterns for AI Assistants

### Pattern: Progressive Enhancement

When implementing new features:

1. **Start minimal** - Get basic functionality working
2. **Add validation** - Ensure data quality
3. **Add error handling** - Graceful failures
4. **Add UX polish** - In-character messages, helpful errors
5. **Add tests** - Prevent regressions

**Example progression:**

```python
# Version 1: Minimal
def register_character(name):
    sheets.append_row([name])

# Version 2: Validation
def register_character(name):
    if not name:
        raise ValueError("Name required")
    sheets.append_row([name])

# Version 3: Error handling
def register_character(name):
    if not name:
        raise ValueError("Name required")
    try:
        sheets.append_row([name])
    except APIError as e:
        log.error(f"Sheets error: {e}")
        raise

# Version 4: UX polish
def register_character(name):
    if not name:
        return create_error_embed(
            "Name Required",
            "The Chroniclers cannot inscribe a nameless hero!"
        )
    try:
        sheets.append_row([name])
        return create_success_embed(
            "Inscribed!",
            f"{name} has been added to the eternal archives!"
        )
    except APIError as e:
        log.error(f"Sheets error: {e}")
        return create_error_embed(
            "Mystical Interference",
            "The arcane energies are disrupted. Try again shortly."
        )
```

---

### Pattern: Consistency in Naming

**File naming:**
- Commands: `{noun}_commands.py` (e.g., `character_commands.py`)
- Flows: `{noun}_flow.py` (e.g., `registration_flow.py`)
- Handlers: `{event}_handler.py` (e.g., `webhook_handler.py`)
- Services: `{integration}_service.py` (e.g., `sheets_service.py`)

**Function naming:**
- Commands: `{verb}_{noun}` (e.g., `register_character`)
- Handlers: `handle_{event}` (e.g., `handle_webhook`)
- Validators: `validate_{noun}` (e.g., `validate_class`)
- Builders: `build_{noun}` (e.g., `build_character_embeds`)

---

### Pattern: The Master Blueprint is Law

**MASTER_BLUEPRINT_SCHEMA_REFORMATION.md is immutable in this phase.**

If you encounter discrepancy between:
- Blueprint says X
- Current code does Y

**Always defer to the Blueprint.** Update code to match, not vice versa.

**Why?**
- Blueprint represents product vision
- Blueprint was carefully designed
- Changing blueprint invalidates documentation phase

**Exception:** If Blueprint has obvious error (typo, impossible requirement), flag it for review before proceeding.

---

## Closing Notes for Future Maintainers

This project is designed for **documentation-driven development**. The documentation is not an afterthought—it IS the specification.

When you work on this codebase:

1. **Read the Blueprint first** - docs/MASTER_BLUEPRINT_SCHEMA_REFORMATION.md
2. **Follow the docs** - TECHNICAL.md describes how things work
3. **Update docs before code** - Documentation changes are product decisions
4. **Test against docs** - Tests verify docs are accurate
5. **Keep the narrative alive** - USER_GUIDE.md should feel like a quest

The Guild Chronicle bot is more than a tool—it's an experience. Technical excellence AND narrative immersion. Precision AND personality.

**For Azeroth Bound! For Documentation! For The Chronicle!** ⚔️📚✨

---

*Documentation maintained by Chronicler Thaldrin, Keeper of Knowledge*
*"What we write today shapes what we build tomorrow."*

---

**Version:** 2.0.0
**Last Updated:** December 16, 2025
**Status:** Production Ready
