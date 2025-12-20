# Azeroth Bound Bot - Technical Documentation

**Version:** 2.0.0 (Schema Reformation & Ascension)
**Architecture:** Path B (Webhook-Driven)
**Last Updated:** December 20, 2025

---

## 1. Architecture Overview

The Azeroth Bound Bot ("The Chronicler") uses a **hybrid architecture**:
- **Discord Bot (Python):** Handles user interactions, interactive flows, and immediate feedback.
- **Google Sheets:** Acts as the primary database (Source of Truth).
- **Webhooks (Google Apps Script):** Pushes updates from Sheets to Discord instantly (Zero Polling).
- **MCP Server:** Provides an API layer for LLM agents to interact with the bot.

---

## 2. Data Schemas

### Character_Submissions Sheet (27 Columns)
Stores character data.
*Columns:* `timestamp`, `discord_id`, `discord_name`, `char_name`, `race`, `class`, `roles`, `professions`, `backstory`, `personality`, `quotes`, `portrait_url`, `trait_1`, `trait_2`, `trait_3`, `status`, `confirmation`, `request_sdxl`, `recruitment_msg_id`, `forum_post_url`, `reviewed_by`, `embed_json`, `death_cause`, `death_story`, `created_at`, `updated_at`, `notes`, `talents_json` (JSON string of talent build).

### Guild_Bank Sheet (12 Columns)
Stores bank transactions and inventory.
*Columns:* `item_id` (UUID), `item_name`, `item_category`, `quantity`, `deposited_by` (Discord ID), `deposited_by_name`, `deposited_at` (ISO timestamp), `withdrawn_by`, `withdrawn_by_name`, `withdrawn_at`, `notes`, `status` (AVAILABLE/WITHDRAWN).

### Talent_Library Sheet (8 Columns)
Stores static talent data for validation.
*Columns:* `Class`, `Tree`, `TalentName`, `MaxRank`, `Level`, `Tier`, `Requires` (JSON list), `RequiredBy` (JSON list).

---

## 3. Core Services

### GoogleSheetsService (`services/sheets_service.py`)
Manages all Google Sheets interactions.
- **Initialization:** Auto-creates missing sheets/headers on startup.
- **Methods:** `log_character`, `log_talent`, `update_character_status`, `get_character_by_name`.
- **Logic:** Handles JSON serialization for complex fields (`talents`, `Requires`).

### GuildBankService (`services/bank_service.py`)
Manages banking logic.
- **Methods:** `deposit_item`, `withdraw_item`, `get_member_deposits`.
- **Logic:** Generates UUIDs for items, tracks ownership history.

### MCP Server (`mcp/`)
Exposes bot functionality to LLMs.
- **Tools:** `get_character_sheet`, `post_image_to_graphics_storage`, `send_discord_message`.
- **Security:** API Key authentication.
- **Graphics:** Handles image uploads to `#graphics-storage` and returns CDN URLs.

---

## 4. Interactive Flows

### /register_character
12-step flow using Discord Modals and Buttons.
- **Image Upload:** Users upload images directly; bot hosts them on `#graphics-storage`.
- **Validation:** Checks race/class combos via `domain/validators.py`.

### /talent audit
Validates a JSON talent build against the `Talent_Library` rules.
- Checks: Max rank, Level requirement, Tier prerequisites, Talent dependencies.

---

## 5. Deployment

Deployed on **Fly.io**.
- **Config:** `fly.toml`
- **Secrets:** Managed via `flyctl secrets` (Discord Token, Sheet ID, Webhook Secret, MCP Key).
- **Process:** `python main.py` runs the Bot, Webhook Server, and MCP Server concurrently.

---

*For detailed setup, see DEPLOYMENT_GUIDE.md*