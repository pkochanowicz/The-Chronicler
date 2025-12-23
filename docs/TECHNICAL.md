# Azeroth Bound Bot - Technical Documentation

**Version:** 1.2.0 (Schema Reformation & Ascension)
**Architecture:** Path B (Webhook-Driven)
**Last Updated:** December 21, 2025

---

## 1. Architecture Overview

The Azeroth Bound Bot ("The Chronicler") uses a **robust, event-driven architecture**:
- **Discord Bot (Python):** Handles user interactions, interactive flows, and immediate feedback.
- **Supabase PostgreSQL:** Acts as the primary database (Source of Truth).
- **FastAPI Gateway:** A production-grade web service handling webhooks, health checks, and acting as the bridge between database events and Discord.
- **MCP Platform:** A separate development/testing environment for LLM-driven features and complex operations.

---

## 2. Data Schemas (PostgreSQL)

### `characters` Table
The definitive record for all guild members.
*Key Columns:*
- `id` (UUID): Primary Key.
- `discord_id` (BigInt): Link to Discord user.
- `name` (Text): Character name (Unique).
- `status` (Enum): `PENDING`, `REGISTERED`, `DECEASED`, `BURIED`.
- `attributes` (JSONB): Flexible storage for `race`, `class`, `roles`, `professions`.
- `biography` (JSONB): Stores `backstory`, `personality`, `quotes`, `traits`.
- `talents` (JSONB): Full talent build data.
- `meta` (JSONB): `portrait_url`, `forum_post_id`, `recruitment_msg_id`.

### `guild_bank` Table
Tracks every item and transaction.
*Key Columns:*
- `id` (UUID): Transaction ID.
- `item_name` (Text): Name of the item.
- `quantity` (Integer): Amount.
- `depositor_id` (BigInt): Discord ID of depositor.
- `status` (Enum): `AVAILABLE`, `WITHDRAWN`.
- `transaction_history` (JSONB): Audit log of ownership.

### `talent_library` Table
Static data for validation, populated via scraping.
*Key Columns:*
- `id` (Text): Unique slug (e.g., `warrior_arms_mortalstrike`).
- `tree` (Text): Talent tree name.
- `max_rank` (Int): Validation rule.
- `prerequisites` (JSONB): Dependency logic.

---

## 3. Core Services

### CharacterService (`services/character_service.py`)
The primary interface for character logic.
- **Backend:** Uses `CharacterRepository` (SQLAlchemy) to interact with Supabase.
- **Methods:** `create_character`, `get_by_discord_id`, `update_status`, `bury`.
- **Validation:** Enforces Pydantic models before DB writes.

### GuildBankService (`services/bank_service.py`)
Manages banking transactions.
- **Backend:** Uses `BankRepository` (SQLAlchemy).
- **Logic:** Ensures atomic transactions for deposits and withdrawals.

### Chronicler Gateway (`main.py`)
The FastAPI application entry point.
- **Routes:** `/webhooks/discord`, `/health`.
- **Lifespan:** Manages database connection pools and bot startup/shutdown.

---

## 4. Interactive Flows

### /register_character
12-step flow using Discord Modals and Buttons.
- **State Management:** Temporary state stored in memory (Redis planned).
- **Finalization:** Calls `CharacterService.create_character` to persist to PostgreSQL.
- **Image Upload:** Uploads to Discord CDN, URL stored in `characters` table.

### /bury
Ceremonial flow for handling character death.
- **Logic:** Updates `status` to `DECEASED`.
- **Trigger:** Database update fires event -> Gateway posts to `#cemetery`.

### /talent audit
Validates a JSON talent build against the `talent_library` table.
- **Logic:** Recursive check of prerequisites and point limits.

---

## 5. Deployment

Deployed on **Fly.io** with high availability.
- **Config:** `fly.toml`
- **Secrets:** `DISCORD_TOKEN`, `DATABASE_URL` (Supabase), `WEBHOOK_SECRET`.
- **Process:** Single container running FastAPI (`uvicorn`) + Discord Bot (`asyncio.create_task`).
- **Restart Policy:** `always` (ensures bot survives transient failures).

---

*For detailed setup, see DEPLOYMENT_GUIDE.md*
