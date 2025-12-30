# 🏛️ MASTER BLUEPRINT: v2.0.0 — The Ascension

**Azeroth Bound Discord Bot — The Complete Architectural Vision**

*Inscribed by Chronicler Thaldrin, Keeper of Knowledge*
*Date: December 20, 2025*

---

## 📜 Executive Summary

This blueprint defines the architecture of **The Chronicler v2.0**, a comprehensive, webhook-driven system for World of Warcraft Classic+ guild management. It unifies character tracking, banking, talent validation, and roleplay immersion into a single, cohesive platform.

**Mission Status:** ✅ **MISSION ACCOMPLISHED**

---

## 🏗️ Part 1: Core Architecture (Path B)

The system relies on a **Zero-Polling / Event-Driven** architecture:

1.  **Source of Truth:** Google Sheets (`Character_Submissions`, `Guild_Bank`, `Talent_Library`).
2.  **Interface:** Discord Bot (Python `discord.py`).
3.  **Bridge:** Google Apps Script Webhooks (push updates to bot).
4.  **Intelligence:** MCP Server (API for LLM agents).

**Infrastructure:**
- **Hosting:** Fly.io (Dockerized)
- **Database:** Google Sheets
- **Storage:** Discord Channels (`#graphics-storage`)

---

## 💎 Part 2: Feature Systems

### 2.1 Character Lifecycle
- **Registration:** Cinematic 12-step interactive flow.
- **Image Hosting:** Direct upload to `#graphics-storage`, CDN link stored.
- **State Machine:** `PENDING` → `REGISTERED` → `DECEASED` → `BURIED`.
- **Burial:** Solemn ceremony moving records to `#cemetery`.

### 2.2 The Guild Bank
- **Relationship:** One Member → Many Items.
- **Schema:** 12 columns tracking Item ID, Owner, Depositor, timestamps, and status.
- **Commands:** Deposit, Withdraw, View, MyDeposits.
- **Safety:** Transactions are appended; history is preserved.

### 2.3 Talent System
- **Library:** `Talent_Library` sheet stores metadata for all 9 classes.
- **Structure:** Tree, Tier, Max Rank, Level, Prerequisites (`Requires`, `RequiredBy`).
- **Validation:** `/talent audit` command checks builds against game rules.
- **Extraction:** Automated extraction scripts populate the library.

### 2.4 Model Context Protocol (MCP)
- **Server:** Running on port 8081.
- **Auth:** API Key protected.
- **Capabilities:**
    - Read Sheets (`get_character_sheet`)
    - Control Discord (`send_discord_message`)
    - Manage Assets (`post_image_to_graphics_storage`)

---

## 📊 Part 3: Data Schemas

### Character Sheet (27 Cols)
`timestamp`, `discord_id`, `char_name`, `race`, `class`, `roles`, `professions`, `backstory`, `portrait_url`, `status`, `talents_json`, ...

### Bank Sheet (12 Cols)
`item_id`, `item_name`, `quantity`, `deposited_by`, `status`, ...

### Talent Sheet (8 Cols)
`Class`, `Tree`, `TalentName`, `MaxRank`, `Tier`, `Requires`, ...

---

## 🚀 Part 4: Operations & Deployment

### Deployment Checklist
1. **Environment:** Verify `.env` has `GRAPHICS_STORAGE_CHANNEL_ID`, `MCP_API_KEY`, `WEBHOOK_SECRET`.
2. **Secrets:** Push secrets to Fly.io (`flyctl secrets set ...`).
3. **Deploy:** `flyctl deploy`.
4. **Init:** Bot auto-creates missing sheets on startup.

### Maintenance
- **Backups:** Automated Google Apps Script triggers daily backups.
- **Logs:** Monitor Fly.io logs for errors.
- **Updates:** Update `Talent_Library` via script or manual entry if game patches change.

---

**For Azeroth Bound! For the Code!** ⚔️