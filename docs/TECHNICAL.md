# Azeroth Bound Bot - Technical Documentation

**Version:** 2.0.0 (Schema Reformation & Ascension)
**Architecture:** Hybrid (Discord Bot + External MCP Server)
**Last Updated:** December 23, 2025

---

## 1. Architecture Overview

The Azeroth Bound Bot ("The Chronicler") uses a **hybrid architecture**:
- **Discord Bot (Python):** Handles user interactions, interactive flows, and immediate feedback.
- **PostgreSQL Database:** Acts as the primary database (Source of Truth), managed via `Alembic` migrations.
- **External MCP Server:** Provides an API layer for LLM agents to interact with the bot.

---

## 2. Data Schemas

Character, Guild Bank, and Talent data are stored in a PostgreSQL database. The schema is defined in `schemas/db_schemas.py` and managed with Alembic migrations.

Please refer to `docs/architecture_UI_UX.md` for the canonical schema definition.

---

## 3. Core Services

### Database Service (`db/database.py`)
Manages all PostgreSQL interactions via SQLAlchemy.

### GuildBankService (`services/bank_service.py`)
Manages banking logic against the database.
- **Methods:** `deposit_item`, `withdraw_item`, `get_member_deposits`.
- **Logic:** Tracks item ownership and transaction history.

### External MCP Server
Exposes bot functionality to LLMs via an external REST API.
- **Repository:** [discord-guildmaster-mcp](https://github.com/pkochanowicz/discord-guildmaster-mcp)
- **Functionality:** `get_character_sheet`, `post_image_to_graphics_storage`, `send_discord_message`.
- **Security:** API Key authentication.
- **Graphics:** Handles image uploads to `#graphics-storage` and returns CDN URLs.

---

## 4. Interactive Flows

### /register_character
12-step flow using Discord Modals and Buttons.
- **Image Upload:** Users upload images directly; bot hosts them on `#graphics-storage`.
- **Validation:** Checks race/class combos via `domain/validators.py`.

### /talent audit
Validates a JSON talent build against the `talents` and `talent_trees` tables in the database.
- Checks: Max rank, Level requirement, Tier prerequisites, Talent dependencies.

---

## 5. Deployment

Deployed on **Fly.io**.
- **Config:** `fly.toml`
- **Secrets:** Managed via `flyctl secrets` (Discord Token, Database URL, Webhook Secret, MCP Key).
- **Process:** `python main.py` runs the Bot and a Webhook listener. The MCP Server is a separate deployment.

---

*For detailed setup, see DEPLOYMENT_GUIDE.md*