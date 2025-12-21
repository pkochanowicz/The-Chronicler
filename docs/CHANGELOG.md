### 2.0.0-alpha.5 - 2025-12-20 - "The Cycle of Life and Death" (Refined)

**Architectural Updates:**
- **Character Lifecycle Coherence (Zone V Complete):**
  - Designed the comprehensive character lifecycle workflow, detailing transitions for `/register_character` to `#recruitment`, Promotion to `#character_sheet_vault`, and `/bury` to `#cemetery`.
  - **Refined Officer Workflow:** Transitioned character approval/rejection from emote-triggered to a more intuitive, button-driven mechanism attached to pending character sheets in `#recruitment`. This significantly enhances user experience and clarity for officers.
  - Emphasized strict object reuse by referencing canonical `characters.id` and `items.id` throughout all workflows.
  - Mandated consistent application of enum/variable naming as defined in `architecture_UI_UX.md`.
  - Assessed the architectural readiness of the `/bury` command at 95%, leveraging PostgreSQL event triggers and the Chronicler Gateway Service.
- **Character Schema Refinement:**
  - Refactored the `characters` table schema in `architecture_UI_UX.md`.
  - Consolidated `backstory`, `personality`, and `quotes` into a single `biography_parts` field (TEXT[]), supporting up to 5 multi-part text fields for richer, yet manageable, character narratives.
  - Updated Discord frontend reflection for `biography_parts` to handle multi-part display intuitively, ensuring readability and aesthetic consistency across character sheets.

**Agent Integration:**
- Summoned a new agent, **MemoryWeaver (Undead Priest)**, specializing in Knowledge Management & Contextual Recall, to instinctively update, discard, and look up memories. This agent's persona and responsibilities have been documented in `agents/MemoryWeaver.json`.

**Documentation:**
- `docs/architecture_UI_UX.md` has been updated with the detailed character lifecycle workflow, including command flows, object reuse principles, the new button-driven officer workflow, and the revised `characters` table schema.
- `agents/MemoryWeaver.json` has been created, detailing the new agent's persona and responsibilities.

### 2.0.0-alpha.3 - 2025-12-20 - "The Journal of Knowledge" (Architectural Refinement)

**Architectural Updates:**
- **Knowledge Retrieval (Zone III Complete):**
  - Designed the comprehensive `/db_search` command functionality, enabling intuitive querying for Items, Item Sets, NPCs, Quests, Spells, and Factions.
  - Defined a structured command syntax: `/db_search <entity_type> <query_term> [filters...]` with autocompletion and filter support based on PostgreSQL schema attributes.
  - Outlined the "First DB Lookup, then Conditional Scrape (Planned)" search logic, prioritizing database efficiency with a future-proof scraping fallback.
  - Designed the `#journal` as a Discord Forum Channel dedicated to displaying `/db_search` results.
  - Established protocols for dynamic thread creation and titles (e.g., `[ITEM_12345] Obsidian Edge`), reflecting the search result's identity.
  - Detailed the rich Discord embed presentation for initial posts in `#journal` threads, leveraging thematic coloring, iconography (from `#graphics_vault`), and detailed schema fields.
  - Incorporated accessibility considerations (alt text, clear labels) and external linking (`turtle_db_url`) for comprehensive embed design.
  - Ensured adherence to TurtleCraft categorization principles in both search logic and result display.
- **Backend Architecture Clarification & Google Sheets Purge:**
  - **Introduced 'Chronicler Gateway Service':** A dedicated, non-LLM production Python/FastAPI application for robust PostgreSQL Event Trigger-driven Discord synchronization. This service will operate in production without any direct LLM dependencies or external LLM API key requirements.
  - **Refined 'MCP Platform' Role:** The 'MCP server' is now explicitly defined as a development/testing environment for LLM-driven features (e.g., 'Portrait Forge') and Trailwarden-orchestrated operations, separate from the production Chronicler Gateway Service. This ensures control over LLM token consumption and safeguards API keys.
  - **Purged Google Sheets Remnants:** Removed all remaining explicit references to Google Sheets as an active data source or blueprint from `architecture_UI_UX.md`, cementing PostgreSQL as the singular source of truth.

**Documentation:**
- `docs/architecture_UI_UX.md` has been updated with the detailed design of the `/db_search` command and the `#journal` Forum channel functionality, and further refined to clarify backend component roles and remove outdated context.

### 2.0.0-alpha.2 - 2025-12-20 - "The Vault of Images" (Enhanced)

**Architectural Updates:**
- **Image Management (Zone II Complete & Enhanced):**
  - Designed a comprehensive `images` table schema within `architecture_UI_UX.md`, making images first-class citizens with robust grouping and origin tracking.
  - Enhanced columns for `images` table include:
    - **`source_system`**: Tracks image origin (e.g., 'PlayerUpload', 'WebScrape', 'SystemGenerated').
    - **`category_tags`**: Flexible `TEXT[]` for multi-dimensional grouping (e.g., `{'portrait', 'human', 'warrior'}`).
    - Refined `ownership_context`, `usage_context`, `entity_type`, `entity_id`, `provenance_notes`, `permissions_level`, `is_animated`, `hash_md5`, `upload_timestamp`, `last_accessed_timestamp`, `metadata_json`, `status`.
  - Planned the `#graphics_vault` as a Discord Forum Channel, where each thread represents a unique image object.
  - Established protocols for dynamic thread titles, rich embed content (displaying enhanced image metadata), and replies for usage tracking, versioning, and discussion within the `#graphics_vault`.
  - **Implemented dynamic Discord Forum Tagging:** Tags are automatically applied to image threads based on `source_system`, `ownership_context`, `usage_context`, and `category_tags` from the `images` table, significantly enhancing discoverability and organization.

**Documentation:**
- `docs/architecture_UI_UX.md` has been updated with the enhanced `images` table schema and the refined `#graphics_vault` Forum channel plan, reflecting a foresightful approach to image asset management.

### 2.0.0-alpha.1 - 2025-12-20 - "The Living Architecture" (Finalized)

**Architectural Updates:**
- **Discord Frontend (Zone I Complete):**
  - Established a definitive Discord frontend architecture, leveraging Forum channels for structured data.
  - Channels `#character_sheet_vault`, `#cemetery`, `#vault`, `#recruitment`, and `#journal` are designated as Forum Channels.
  - Defined strict mapping between Discord Forum threads (parent posts) and PostgreSQL database records (`DB_ID` in titles, `forum_post_id` in tables).
  - Established protocols for dynamic thread titles and rich embed content, auto-populated from database records using detailed schema.
  - Detailed the use of replies for event-driven updates within Forum threads, maintaining context and history.
- **Data Synchronization:**
  - Confirmed PostgreSQL Database Event Triggers as the primary, robust, and real-time mechanism for data propagation from the database to Discord.
  - Designed a safe update strategy incorporating batching and debouncing within the MCP server to mitigate Discord API rate limits.
- **Data-Driven Design:**
  - Integrated a comprehensive web scraping strategy (`https://database.turtlecraft.gg/` using Playwright/BeautifulSoup) into the architecture to inform precise PostgreSQL data schemas, column definitions, relationships, and validation rules.
  - Outlined how scraped data (including multi-level categorization, visual cues like icon URLs and quality enums, and thematic color hexes) will directly shape Discord embed colors, icons, and dynamic content.
- **Detailed PostgreSQL Data Schemas:**
  - **Comprehensive blueprint for core entities now included in `architecture_UI_UX.md`:** `characters`, `talents`, `talent_trees`, `items`, `item_sets`, `npcs`, `quests`, `spells`, `factions`.
  - Defined common PostgreSQL ENUMs (`item_quality_enum`, `character_race`, `character_class`, `character_role`, `character_status`, `creature_type`, `spell_school`, `faction_alignment`, `quest_type`).
  - For each table: explicitly defined columns (name, type, nullability, default), primary keys, foreign key relationships, detailed constraints/validations, and explicit mapping to Discord frontend reflection (embed fields, colors, icons, categorization).
- **MCP Server Role Refinement:**
  - Designated the MCP server as a dedicated, robust testing crucible for all architectural components, explicitly not for production deployment at this stage, enabling LLM-driven testing workflows.

**Documentation:**
- `docs/architecture_UI_UX.md` has been *comprehensively revised and expanded* to reflect these foundational architectural decisions and detailed data schemas, serving as the binding law for the project.

# Azeroth Bound Bot - Changelog

All notable changes to the **Azeroth Bound** project (also known as *The Chronicle*) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachang-elog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-12-20

### 🚀 Major Release: The Schema Reformation & Ascension

This release marks the transition to a fully webhook-driven architecture (Path B), a comprehensive 27-column character schema, and the introduction of major gameplay systems.

### Fixed
- **Fly.io Deployment:** Resolved critical startup errors on Fly.io by setting missing environment variables: `MCP_API_KEY`, `GRAPHICS_STORAGE_CHANNEL_ID`, and `WEBHOOK_SECRET`.

### Added
- **Schema Auto-Formatting:** Implemented a robust schema validation system on application startup. If a Google Sheet schema is invalid, the bot will log a detailed error and halt. The user can then set the `AUTOFORMAT_SHEETS_ON_STARTUP=TRUE` environment variable to trigger a one-time, destructive auto-formatting of the sheets on the next boot, preventing startup failures due to schema drift.
- **Guild Bank System:**
  - New `GuildBankService` handling a one-member-to-many-items relationship.
  - New Google Sheet tab `Guild_Bank` with 12-column schema.
  - New commands: `/bank deposit`, `/bank withdraw`, `/bank view`, `/bank mydeposits`.
- **Talent System & Validation:**
  - New `Talent_Library` Google Sheet for dynamic talent data.
  - Comprehensive `TALENT_DATA` structure for all 9 classes (Classic+).
  - New command: `/talent audit` to validate builds against rules.
  - `validate_talents` logic checking ranks, levels, and prerequisites.
  - **Talent Data Acquisition:** Automated scraping of Turtle WoW talent information (names, descriptions, ranks, positional data) from `talent-builder.haaxor1689.dev` and associated background images from `imgur.com`, providing robust schemas for individual talents and talent tree metadata.
- **Portrait Forge:**
  - AI prompt generation for characters without custom portraits.
- **Graphics Storage Integration:**
  - `post_image_to_graphics_storage` MCP tool to host images on Discord.
  - Automated image uploading for `/register_character` flow.
- **MCP Server Integration:**
  - Dedicated internal MCP server for LLM-based interactions.
  - Tools for sheet access, messaging, and channel management.
- **Architecture:**
  - `GoogleSheetsService` refactor to manage multiple sheet tabs dynamically.
  - Auto-creation of missing sheets (`Guild_Bank`, `Talent_Library`) on startup.

### Changed
- **Character Schema:** Expanded to 27 columns (added `death_cause`, `death_story`, `talents_json`, etc.).
- **Registration Flow:** Now supports direct image uploads via Discord attachments.
- **Documentation:** Complete overhaul of README, TECHNICAL, and USER guides for v2.0.

---

## [1.1.9] - 2025-12-20
*Merged into 2.0.0*

---

## [1.1.8] - 2025-12-20
*Merged into 2.0.0*

---

## [1.1.7] - 2025-12-20

### Fixed
- **Deprecation Warnings:** Replaced all instances of the deprecated `datetime.datetime.utcnow()` with the timezone-aware `datetime.datetime.now(datetime.UTC)`. This resolves all `DeprecationWarning`s during tests and ensures future compatibility.

### Added
- **Deployment Checklist:** Created `docs/DEPLOYMENT_CHECKLIST.md` to provide a comprehensive checklist for verifying deployments.
- **Testing Results:** Updated `TESTING_RESULTS.md` with the full report from the "QUEST II: BATTLE HARDENING" deployment and verification.

### Changed
- **Deployment:** The application was successfully deployed to Fly.io, and the webhook is confirmed to be live and secure.

---

## [1.1.6] - 2025-12-20

### Deployment
- Successfully deployed the application to fly.io.

### Changed
- **fly.toml**: Changed `primary_region` from `waw` to `arn` to resolve deployment errors due to the deprecation of the `waw` region.

### Fixed
- **Dockerfile.uv**: Modified the Dockerfile to copy `README.md` and `poetry.lock` before installing dependencies, fixing a `FileNotFoundError` during the build process.

### Added
- **fly.toml**: Modified the build configuration to use `Dockerfile.uv` for deployments, switching from a buildpack-based to a Dockerfile-based deployment strategy.
- **TESTING_RESULTS.md**: Comprehensive report of the end-to-end testing suite execution (77 tests passed), verifying:
  - Full 12-step `/register_character` interactive flow
  - `/bury` ceremony and cemetery functionality
  - Webhook security and trigger logic
  - Error handling and recovery strategies