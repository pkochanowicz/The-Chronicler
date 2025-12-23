# Azeroth Bound Bot - Changelog

All notable changes to the **Azeroth Bound** project (also known as *The Chronicle*) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [2.0.0] - 2025-12-20

### 🚀 Major Release: The Schema Reformation & Ascension

This release marks the transition to a fully webhook-driven architecture (Path B), a comprehensive 27-column character schema, and the introduction of major gameplay systems.

### Added
- **Guild Bank System:**
  - New `GuildBankService` handling a one-member-to-many-items relationship.
  - New Google Sheet tab `Guild_Bank` with 12-column schema.
  - New commands: `/bank deposit`, `/bank withdraw`, `/bank view`, `/bank mydeposits`.
- **Talent System & Validation:**
  - New `Talent_Library` Google Sheet for dynamic talent data.
  - Comprehensive `TALENT_DATA` structure for all 9 classes (Classic+).
  - New command: `/talent audit` to validate builds against rules.
  - `validate_talents` logic checking ranks, levels, and prerequisites.
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
