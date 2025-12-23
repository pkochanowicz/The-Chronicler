# ⚔️ THE CHRONICLER: OPERATIONAL CORE (v1.2.0)

**Architecture:** FastAPI (Gateway) + Supabase (DB) + Discord (UI) + Fly.io (Host)
**Source of Truth:** `docs/architecture_UI_UX.md`
**Status:** 🛡️ Phase IV: Test-Driven Implementation

## 🛑 THE 5 COMMANDMENTS
1.  **Truth:** Docs dictate Code. Supabase is State. Discord is View.
2.  **Legacy:** Google Sheets/`gspread` = **BANNED**. Usage = CI Fail.
3.  **Tests:** No code without tests. Red -> Green -> Refactor.
4.  **Tokens:** Conserve. Read selectively. Summarize.
5.  **Model Doctrine:**
    *   **Pro:** Logic, Coding, Planning.
    *   **Flash-Lite:** Reads, Scans, Logs.
    *   **Flash:** 🚫 **DO NOT USE** (Quota).
    *   **3.0-Preview:** Oracle (Complex Arch only).

## 🧪 TESTING PROTOCOL (The Pyramid)
| Level | Scope | Path | Rules |
| :--- | :--- | :--- | :--- |
| **1. Audit** | Security/Legacy | `tests/audit/` | No `gspread`. Config isolation. |
| **2. Unit** | Logic/Models | `tests/unit/` | **CURRENT PHASE**. No DB/Net. <10ms. |
| **3. Integration**| Services/DB | `tests/integration/`| DB allowed. Atomic transactions. |
| **4. E2E** | Full Flows | `tests/e2e/` | MCP Agents as Users. |

## 📂 CRITICAL PATHS
*   **Gateway:** `main.py`
*   **Services:** `services/character_service.py`, `services/bank_service.py`
*   **DB:** `db/database.py`
*   **Docs:** `docs/architecture_UI_UX.md`, `docs/TEST_SUITE.md`

## ⚔️ TOKEN WARFARE
*   **Context:** Load only what is needed.
*   **Memory:** Use `save_memory` for user facts ONLY.
*   **Output:** Concise. Code > Prose.

**"Memory is weight. Discipline is speed."**
