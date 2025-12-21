# Changelog

All notable changes to **The Chronicler** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-21 "Reformation"

### 🚀 Major Architectural Shift
- **Migration to PostgreSQL (Supabase):** The entire data persistence layer has been migrated from Google Sheets to a relational PostgreSQL database hosted on Supabase.
- **Single Source of Truth:** The database is now the definitive authority for all character, guild bank, and talent data. Discord serves strictly as a frontend interface.
- **FastAPI Gateway:** Introduced a production-grade FastAPI application (`main.py`) to serve as the central gateway for webhooks and health checks, replacing the ad-hoc script execution.
- **Lazy Loading Strategy:** Implemented lazy initialization for heavy services (like Google Sheets legacy adapters) to prevent startup timeouts on Fly.io.

### ✨ New Features
- **Guild Bank 2.0:** A completely rewritten banking system with robust transaction tracking (`deposit`, `withdraw`, `view`, `mydeposits`).
- **Talent Validation Engine:** A new validation logic that audits talent builds against Classic+ rules, ensuring legal point distribution.
- **Fly.io "Always On" Policy:** Deployment configuration updated to `vm.restart.policy = "always"` to ensure high availability.

### 🛠️ Technical Improvements
- **Docker Optimization:**
  - Implemented `.dockerignore` to reduce build context from >300MB to <2MB.
  - Switched to multi-stage builds with `uv` for faster dependency resolution.
- **Secret Management:**
  - Standardized environment variables across local `.env` and Fly.io secrets.
  - Added automated scripts for secure secret deployment.
- **Logging Reformation:** Enhanced logging throughout the application to capture startup phases and critical failures without silent crashes.

### 🔥 Removed / Deprecated
- **Google Sheets as Database:** Removed the concept of Sheets as the primary data store. (Sheets service retained only for legacy import/export utilities).
- **Google Apps Script:** The Apps Script webhook relay has been deprecated in favor of direct database event triggers (architecture planned).
- **Legacy Documentation:** Purged `MASTER_BLUEPRINT_V2.md`, `GOOGLE_APPS_SCRIPT_SETUP.md`, and `AI_AGENTS_CODE_OPERATIONS.md` to eliminate confusion.

---

## [1.0.0] - 2025-12-15 "Genesis"

### Added
- Initial release of The Chronicler.
- Character registration flow (12-step interactive wizard).
- Basic google sheets integration.
- Burial rite ceremony.
