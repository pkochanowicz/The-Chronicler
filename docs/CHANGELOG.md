# Changelog

All notable changes to **The Chronicler** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-01-06 "Forum Forgemaster"

### 🐛 Bug Fixes
- **Environment Configuration:** Fixed typo in local `.env` file (`CEMETARY_DEFAULT_TAG_ID` → `CEMETERY_DEFAULT_TAG_ID`)
- **Forum Tag Support:** Verified and validated forum tag application for all three forum channels (Recruitment, Character Sheet Vault, Cemetery)

### 🔧 Configuration & Deployment
- **Production Environment:** Confirmed fly.io secrets contain correct `CEMETERY_DEFAULT_TAG_ID` variable
- **Bot Permissions:** Documented required Discord bot permissions for forum operations (Create Public Threads, Manage Threads, Send Messages in Threads)
- **Bot Intents:** Verified correct configuration of Discord intents (guilds, members, message_content, reactions)

### 📘 Documentation
- **Permission Requirements:** Added comprehensive documentation for Discord bot permission requirements across all forum channels
- **Forum Operations:** Validated forum post creation workflow for `/register_character`, accept/reject character sheets, and `/bury` commands

### 🏗️ Architecture
- **Forum Tag Integration:** Enhanced forum thread creation to properly apply default tags for recruitment and cemetery channels
- **Error Handling:** Improved forum operation error detection and logging capabilities

---

## [1.2.6] - 2025-12-22 "The Singing Steel"

### ⚔️ Major Feature: Guild Bank System
- **Banking Ledger:** Implemented a fully transactional banking system (`GuildBankService`) backed by PostgreSQL.
- **Commands:** Added `/bank deposit`, `/bank withdraw`, `/bank view`, and `/bank mydeposits`.
- **Schema:** Introduced `guild_bank_items` and `guild_bank_transactions` tables via Alembic migration.

### 🛡️ Major Feature: Interactive Discord Flows
- **Registration Ritual:** Refactored the character registration wizard (`/register_character`) to be purely ephemeral and SQL-backed.
- **Officer Control Center:** Implemented `OfficerControlView` attached to recruitment threads, enabling button-based **Approve**, **Reject**, and **Request Edit** actions.
- **Automated Lifecycle:** Approval now automatically promotes characters to the Vault, creates their sheet thread, and archives the application.

### 🏗️ Architecture & Technical Debt
- **PostgreSQL Source of Truth:** Completed the migration from Google Sheets to Supabase/PostgreSQL for all core data (Characters, Bank, Graveyard).
- **Schema Alignment:** rigorously aligned `schemas/db_schemas.py` and `models/pydantic_models.py` with the `docs/architecture_UI_UX.md` specifications.
- **Alembic Migrations:** Established a robust migration pipeline with `release_command` configuration for Fly.io.
- **Legacy Purge:** Completely removed `GoogleSheetsService` and related dependencies (`gspread`, `oauth2client`) from the core runtime path.

### 📘 Documentation
- **Architecture Features:** Published `docs/architecture_features_v2.md` detailing the flow logic.
- **User Guide:** Updated `docs/USER_GUIDE.md` with banking and talent editor instructions.
- **Restoration:** Restored and finalized `docs/architecture_UI_UX.md`.

---
## [1.2.8] - 2025-12-23

### Breaking Changes
- Migrated to external discord-guildmaster-mcp server architecture
- Removed internal MCP server implementation from /mcp directory
- The Chronicler now requires external MCP server for advanced features

### Changed
- Updated all documentation to reflect external MCP dependency
- Restructured tests to mock external MCP server responses
- Simplified codebase by removing MCP server concerns

### Migration Guide
- Deploy discord-guildmaster-mcp server separately
- Configure MCP_SERVER_URL environment variable
- See docs/MCP_DISCORD_TECHNICAL.md for full setup instructions

---

## [1.2.0] - 2025-12-21 "Reformation"

### 🚀 Major Architectural Shift
- **Migration to PostgreSQL (Supabase):** The entire data persistence layer has been migrated from Google Sheets to a relational PostgreSQL database hosted on Supabase.
- **Single Source of Truth:** The database is now the definitive authority for all character, guild bank, and talent data. Discord serves strictly as a frontend interface.
- **FastAPI Gateway:** Introduced a production-grade FastAPI application (`main.py`) to serve as the central gateway for webhooks and health checks, replacing the ad-hoc script execution.
- **Database Schema Management (Alembic):** Integrated Alembic for robust, version-controlled database schema migrations.

### ✨ New Features
- **Talent Validation Engine:** A new validation logic that audits talent builds against Classic+ rules.
- **Fly.io "Always On" Policy:** Deployment configuration updated for high availability.

### 🛠️ Technical Improvements
- **Docker Optimization:** Implemented multi-stage builds with `.dockerignore`.
- **Secret Management:** Standardized environment variables across local `.env` and Fly.io secrets.
- **Testing:** Achieved E2E test passes for the core API layer.

---

## [1.0.0] - 2025-12-15 "Genesis"

### Added
- Initial release of The Chronicler.
- Character registration flow (12-step interactive wizard).
- Basic google sheets integration.
- Burial rite ceremony.
