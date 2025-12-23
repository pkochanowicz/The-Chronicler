# The Chronicler: The Grand Test Doctrine (v2.1)

**Status:** The Immutable Law of Verification  
**Architecture:** FastAPI + Supabase (PostgreSQL) + Discord Bot  
**Mandate:** "Tests do not protect code. They protect truth."

---

## 🏗️ I. The Hierarchy of Verification

We adhere to a strict testing pyramid. Leaking abstractions between layers is a violation of protocol.

### 0. 🏛️ Schema Definition & Migration Tests (The Blueprint)
*   **Scope:** Verification that the live database schema matches `schemas/db_schemas.py`.
*   **Dependencies:** Testcontainers (Postgres).
*   **Location:** `tests/schema/`
*   **Key Doctrine:**
    *   **Truth from Models:** SQLAlchemy models are the source of truth.
    *   **Alembic Compliance:** Migrations must reflect models exactly.
    *   **Migration Idempotency:** Upgrades must be repeatable without error.

### 1. 🛡️ Unit Tests (The Foundation)
*   **Scope:** Pure logic, isolated functions, Pydantic models, validators.
*   **Dependencies:** ZERO. No DB, no Discord, no Network.
*   **Speed:** < 10ms per test.
*   **Location:** `tests/unit/`
*   **Key Doctrine:**
    *   All regex patterns for scraping must have unit tests.
    *   All `domain/validators.py` logic must be exhaustively tested.
    *   Talent validation logic must be tested with edge cases (tier skipping, prereq missing).

### 2. ⚙️ Service Integration Tests (The Engine)
*   **Scope:** `CharacterService`, `GuildBankService`, `WebhookHandler`.
*   **Dependencies:** Test Database (Testcontainers). **NO** External APIs.
*   **Speed:** < 500ms per test.
*   **Location:** `tests/integration/`
*   **Key Doctrine:**
    *   **Transaction Guarantee:** DB operations must be atomic.
    *   **Bank Ledger:** Bank transactions must balance. Deposits increase count, Withdrawals decrement.

### 3. 🌐 API Contract Tests (The Gateway)
*   **Scope:** FastAPI Routes (`/webhooks`, `/health`, `/api`).
*   **Dependencies:** Test Database, Mocked Discord Gateway.
*   **Location:** `tests/api/`
*   **Key Doctrine:**
    *   Webhooks must validate `X-Signature-Ed25519` (logic verified).
    *   Endpoints return correct HTTP Status Codes.

### 4. 🎭 Discord & Interactive Flows (The Stage)
*   **Scope:** User interactions, Button clicks, Modals, Commands.
*   **Dependencies:** Mocked Discord Interaction Objects (Pytest) OR Live Test Server (E2E).
*   **Location:** `tests/discord/` (New)
*   **Key Doctrine:**
    *   **Flow Determinism:** `/register` must ALWAYS trigger the ephemeral wizard.
    *   **Button Logic:** `Approve` button must trigger the correct DB update and Channel move.
    *   **Permission Enforcement:** Non-officers clicking `Approve` must be rejected.

---

## 🌌 III. The MCP "War Games" (E2E Doctrine)

We do not manually click buttons. We summon agents to do it for us.

### 1. The Actor Model
The test suite utilizes the `chronicler-mcp` to act as a Virtual User (VU).

### 2. War Game Scenarios

#### ⚔️ Scenario A: The Sacred Ritual (Registration)
*   **Objective:** Verify the 12-step state machine without data loss.
*   **Sequence:**
    1.  VU invokes `/register_character`.
    2.  VU fills Modal.
    3.  VU uploads Image.
    4.  **Verification:** Thread created in `#recruitment`.
    5.  Officer VU clicks `[Approve]`.
    6.  **Verification:** Thread moved/created in `#character_sheet_vault`. Status = `REGISTERED`.

#### ⚰️ Scenario B: The Rite of Remembrance (Burial)
*   **Objective:** Verify data movement and state change.
*   **Sequence:**
    1.  Officer VU invokes `/bury`.
    2.  Selects character.
    3.  Fills Eulogy.
    4.  **Verification:** Thread created in `#cemetery`. DB Status = `BURIED`.

#### 🏦 Scenario C: The Economy (Bank)
*   **Objective:** Verify atomic transactions.
*   **Sequence:**
    1.  VU invokes `/bank deposit`.
    2.  **Verification:** Item count increases. Transaction logged.
    3.  VU invokes `/bank withdraw`.
    4.  **Verification:** Item count decreases. Transaction logged.

---

## 📊 V. Pre-Commit Guarantees

1.  **Static Analysis:** `ruff check .`
2.  **Type Safety:** `mypy .`
3.  **Unit Tests:** `pytest tests/unit`
4.  **Schema Check:** `alembic check`

---

**"The Ink Must Not Fade."**
