# Architecture Supplement: Discord Flows & Banking (v2.1)

This document serves as the **authoritative extension** to `architecture_UI_UX.md`, detailing the specific implementation of Discord interactive flows, the Guild Bank system, and the Talent Tree validation logic. It is the "Source of Truth" for these specific domains until a future merger.

## 1. Discord Channel Topology

The Chronicler operates across **10 distinct channels**, each mapped to specific automation triggers.

| Channel Name | Type | Access | Purpose | Triggers / Automation |
| :--- | :--- | :--- | :--- | :--- |
| `#bot-commands` | Text | Public | General interactions, `/roll`, `/help`. | `/db_search` |
| `#guild-news` | Text | Public | Announcements. | Manual Officer Posts |
| `#talent-builder` | Text | Public | Talent discussions. | `/talent editor`, `/talent audit` |
| `#officer-chat` | Text | Officer | Internal command center. | `/bank withdraw` (override), Admin Alerts |
| `#recruitment` | Forum | Public | New applications. | `/register_character` -> **New Thread** |
| `#character_sheet_vault` | Forum | Public | Approved character sheets (ReadOnly). | Officer Approval -> **New Thread** |
| `#cemetery` | Forum | Public | Memorials for fallen heroes. | `/bury` -> **New Thread** |
| `#vault` | Forum | Public | Rare items, lore artifacts. | Manual / Auto-promoted Items |
| `#journal` | Forum | Public | Database search results. | `/db_search` -> **New Thread** |
| ~~`#graphics_vault`~~ | ~~Forum~~ | ~~Hidden~~ | **DEPRECATED:** Image storage now handled by Cloudflare R2. | See `services/image_storage.py` |

## 2. Interactive Flows

### A. Character Registration Flow (The Ritual)
**Trigger:** `/register_character`
**Type:** Ephemeral Interaction -> Forum Thread

1.  **State 1: Ephemeral Collection**
    *   User invokes command.
    *   Bot responds with an ephemeral "Wizard" interface (stepped modal or select menus) collecting:
        *   `Name`, `Race` (Enum), `Class` (Enum)
        *   `Roles` (Multi-select), `Professions` (Multi-select)
        *   `Backstory` (Modal Text Input)
        *   `Portrait` (Attachment Upload)
2.  **State 2: Thread Creation (PENDING)**
    *   Bot creates a **New Thread** in `#recruitment`.
    *   **Title:** `[PENDING] Character Name (Class)`
    *   **Content:** Rich Embed with all data + Image.
    *   **View:** `OfficerControlView` attached to the message.
        *   `[Approve]` (Green, Officer Only)
        *   `[Reject]` (Red, Officer Only)
        *   `[Request Edit]` (Grey, Officer Only)

### B. Officer Approval Flow
**Trigger:** Button Click on `#recruitment` thread.

1.  **Approval:**
    *   **Action:**
        *   DB Update: `status` -> `REGISTERED`.
        *   Discord: Create New Thread in `#character_sheet_vault`.
        *   Discord: Lock/Archive `#recruitment` thread.
        *   Discord: Send DM to User ("Welcome to Azeroth Bound...").
2.  **Rejection:**
    *   **Action:** Opens Modal for `Reason`.
    *   **Outcome:**
        *   DB Update: `status` -> `REJECTED`.
        *   Discord: Archive `#recruitment` thread.
        *   Discord: Send DM to User ("Your application was declined: [Reason]").

### C. The Rite of Remembrance (Burial)
**Trigger:** `/bury <character_name>` (Officer Only)

1.  **Selection:** Autocomplete search for `REGISTERED` characters.
2.  **Details:** Modal prompts for:
    *   `Cause of Death` (Short text)
    *   `Eulogy` (Long text)
    *   `Final Image` (Optional URL)
3.  **Execution:**
    *   DB Update: `status` -> `BURIED`.
    *   Discord: Lock `#character_sheet_vault` thread.
    *   Discord: Create New Thread in `#cemetery`.
        *   **Title:** `[RIP] Character Name`
        *   **Content:** Solemn Embed (Black/Grey color) with Eulogy.

## 3. Guild Bank Architecture

The Guild Bank uses a **ledger-based** system backed by the `guild_bank_items` and `guild_bank_transactions` tables.

### Data Schema (Supplement to `db_schemas.py`)

**Table: `guild_bank_items`**
*   `id` (PK)
*   `item_id` (FK -> `items.id`)
*   `count` (Integer, >= 0)
*   `category` (String)
*   `location` (String)

**Table: `guild_bank_transactions`**
*   `id` (PK)
*   `item_id` (FK -> `items.id`)
*   `user_id` (BigInteger, Discord ID)
*   `transaction_type` (Enum: `DEPOSIT`, `WITHDRAWAL`)
*   `quantity` (Integer)
*   `timestamp` (DateTime)
*   `notes` (Text)

### Commands
*   **`/bank deposit <item_name> <qty>`**
    *   Matches `item_name` against `items` table (fuzzy search).
    *   If ambiguous, asks for clarification.
    *   Updates `guild_bank_items`.
    *   Inserts row into `guild_bank_transactions`.
*   **`/bank withdraw <item_id>`**
    *   Checks availability in `guild_bank_items`.
    *   Updates `guild_bank_items` (decrement).
    *   Inserts row into `guild_bank_transactions`.
*   **`/bank view`**
    *   Returns a paginated Embed of available items, grouped by Category.

## 4. Talent Tree Editor & Validation

**Trigger:** `/talent editor` or `/talent audit`

### Validation Logic
The system enforces Classic+ (Turtle WoW 1.18.1) rules:
1.  **Points Check:** `Total Points <= Level - 9`.
2.  **Tier Check:** To spend points in Tier N, `(N-1) * 5` points must be spent in previous tiers of *that tree*.
3.  **Max Rank:** Points in talent <= `max_rank`.
4.  **Prerequisites:** Required talent must be maxed.

### Data Storage
*   Talents are stored in `characters.talents_json` as a simple Dict: `{"talent_id": rank}`.
*   This JSON is validated against the canonical `talents` table before saving.
