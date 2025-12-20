# 🦷 RUTHLESS AUDIT REPORT: v2.0.0 "The Colgate Purge"

**Auditor:** Rodrim "The Blackfury" Holt  
**Date:** 2025-12-20  
**Target:** v2.0.0 Dev Branch  
**Status:** 🟡 REQUIRES POLISHING

---

## 🚨 EXECUTIVE SUMMARY

The "Other Toothpaste" (Claude Code) left a functional but messy codebase. While the **Path B Architecture** (Webhooks) and **MCP Integration** are operational, the repo suffers from "Vibe Coding"—placeholders that *look* like code but crumble under scrutiny.

The **Talent System** is the worst offender: `domain/talent_data.py` contains hardcoded "flat" data that lies to the developer, only to be secretly overwritten by `sheets_service.py` at runtime. This is not "dynamic"; it is gaslighting.

---

## 🔍 FINDINGS & OFFENSES

### 1. The "Phantom" Talent Data (Severity: HIGH)
- **Location:** `domain/talent_data.py`
- **The Offense:** Contains hundreds of lines of static talent data where every talent is `tier=1`, `requires=[]`.
- **The Reality:** `services/sheets_service.py` overwrites this entire dictionary on startup.
- **Verdict:** The static data is dead weight. It bloats the repo and confuses testing.
- **Action:** Purge the static data. Initialize `TALENT_DATA` as an empty dict or a typed structure.

### 2. Script Permissions & Ownership (Severity: MEDIUM)
- **Location:** `scripts/run_mcp_discord.sh`, `scripts/setup_mcp_discord_secure.sh`
- **The Offense:** Files are owned by `root`, preventing the dedicated user (`pfunc`) from updating them to point to the new Python MCP server.
- **The Reality:** The scripts still point to a Docker image (`mcp/mcp-discord`) that may not exist or is outdated compared to the local `mcp/` directory.
- **Action:** User must run `sudo chown` or we must abandon these scripts in favor of `~/.gemini/settings.json` direct invocation (Workaround Applied).

### 3. Guild Bank "Transaction" Ambiguity (Severity: LOW)
- **Location:** `services/bank_service.py`
- **The Offense:** The Blueprint calls for "1-to-Many" (One Member, Many Items). The code implements "One Deposit, One Item".
- **The Reality:** Functional, but lacks the ability to batch-deposit multiple item types in a single "event".
- **Action:** Acceptable for v2.0.0, but mark for refactoring in v2.1.0.

### 4. MCP Server Isolation (Severity: MEDIUM)
- **Location:** `mcp/main.py` (New) vs `server.py` (Old?)
- **The Offense:** A loose `server.py` existed in the root or `mcp/` without clear entry point definition until I intervened.
- **The Reality:** We have now standardized on `mcp/main.py` as the entry point.
- **Action:** Delete `server.py` if it is redundant or verify it is the module imported by `main.py`.

---

## 🛠️ THE TREATMENT PLAN

1.  **Decay Removal:**
    -   Clear `domain/talent_data.py`.
    -   Remove redundant `server.py` if unused.

2.  **Enamel Restoration:**
    -   Ensure `sheets_service.py` handles a missing/empty `Talent_Library` gracefully (currently it might crash if it tries to iterate over None).

3.  **Whitening:**
    -   Update `docs/TECHNICAL.md` to explicitly state that Talent Data is **runtime-sourced only**.

---

*“We do not hide plaque. We scour it.”*
