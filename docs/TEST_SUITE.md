# The Chronicler: The Grand Test Doctrine (v2.0.0)

**Status:** The Immutable Law of Verification  
**Architecture:** FastAPI + Supabase (PostgreSQL) + Discord Bot  
**Mandate:** "Tests do not protect code. They protect truth."

---

## 🏗️ I. The Hierarchy of Verification

We adhere to a strict testing pyramid. Leaking abstractions between layers is a violation of protocol.

### 1. 🛡️ Unit Tests (The Foundation)
*   **Scope:** Pure logic, isolated functions, Pydantic models, validators.
*   **Dependencies:** ZERO. No DB, no Discord, no Network.
*   **Speed:** < 10ms per test.
*   **Location:** `tests/unit/`
*   **Key Doctrine:**
    *   All regex patterns for scraping must have unit tests with HTML snippets.
    *   All `domain/validators.py` logic must be exhaustively tested.
    *   All Pydantic models must verify field constraints (max_length, regex).

### 2. ⚙️ Service Integration Tests (The Engine)
*   **Scope:** `CharacterService`, `GuildBankService`, `WebhookHandler`.
*   **Dependencies:** Test Database (Docker/Testcontainers). **NO** External APIs (Discord/Sheets).
*   **Speed:** < 500ms per test.
*   **Location:** `tests/integration/`
*   **Key Doctrine:**
    *   **The Transaction Guarantee:** All DB operations within a service method must be atomic. Testing must verify rollbacks on failure.
    *   **The Repository Pattern:** Services never speak SQL; they speak to Repositories. Tests verify this boundary.

### 3. 🌐 API Contract Tests (The Gateway)
*   **Scope:** FastAPI Routes (`/webhooks`, `/health`, `/api`).
*   **Dependencies:** Test Database, Mocked Discord Gateway.
*   **Location:** `tests/api/`
*   **Key Doctrine:**
    *   All endpoints must return correct HTTP Status Codes (200, 201, 400, 401, 404, 500).
    *   Webhooks must validate `X-Signature-Ed25519` (mocked in test, but logic verified).

### 4. 🌌 MCP-Orchestrated End-to-End (E2E) Trials (The World)
*   **Scope:** Full user journeys simulating Discord interactions via MCP.
*   **Dependencies:** Test Database, Simulated Discord Environment (or specific test channels).
*   **Location:** `tests/e2e/`
*   **Key Doctrine:** See Section III.

---

## 🚫 II. The "Split Brain" Firewall Protocol

To prevent regression to the v1.0.0 Google Sheets architecture, the following **Negative Tests** are mandatory.

### 1. The Gspread Ban
A pipeline scanner must verify that no *runtime* code imports `gspread` or `oauth2client` unless explicitly flagged as a legacy migration utility.
*   **Test:** `tests/audit/test_no_legacy_imports.py`
*   **Assertion:** `import gspread` triggers failure in core services.

### 2. The Configuration Quarantine
*   **Test:** `tests/audit/test_config_isolation.py`
*   **Assertion:** The application must start successfully even if `GOOGLE_SHEET_ID` is unset or invalid (verifying Lazy Loading and optional dependency).

---

## 🌌 III. The MCP "War Games" (E2E Doctrine)

We do not manually click buttons. We summon agents to do it for us. The **MCP Platform** serves as the test conductor.

### 1. The Actor Model
The test suite utilizes the `chronicler-mcp` to act as a Virtual User.

*   **Virtual User (VU):** An LLM agent (or scripted equivalent) configured with specific Discord permissions (Wanderer, Officer, Admin).
*   **Simulated Interface:** A mock object that replicates the Discord Gateway `Interaction` payload.

### 2. War Game Scenarios

#### ⚔️ Scenario A: The Sacred Ritual (Registration)
*   **Objective:** Verify the 12-step state machine without data loss.
*   **Sequence:**
    1.  VU invokes `/register_character`.
    2.  System responds with Embed + View (Introduction).
    3.  VU clicks "Confirm Identity".
    4.  ... (Steps 2-11) ...
    5.  VU uploads image (Simulated Attachment URL).
    6.  VU confirms.
*   **Verifications:**
    *   **DB:** Row created in `characters` table with `status='PENDING'`.
    *   **DB:** `meta->portrait_url` matches uploaded URL.
    *   **Logic:** `created_at` timestamp is set.

#### ⚰️ Scenario B: The Rite of Remembrance (Burial)
*   **Objective:** Verify data movement and irreversible state change.
*   **Prerequisite:** A character in `REGISTERED` state exists.
*   **Sequence:**
    1.  VU (Officer) invokes `/bury`.
    2.  VU searches for character name.
    3.  System returns Match.
    4.  VU provides `death_cause` and `death_story`.
    5.  VU confirms.
*   **Verifications:**
    *   **DB:** `characters.status` UPDATE to `'DECEASED'`.
    *   **Event:** `POST_TO_CEMETERY` webhook triggered (mocked assertion).
    *   **Logic:** Cannot bury an already buried character (Idempotency).

#### 🏦 Scenario C: The Economy (Bank)
*   **Objective:** Verify atomic transactions and audit trails.
*   **Sequence:**
    1.  VU invokes `/bank deposit item:"Black Lotus" qty:1`.
    2.  **DB Check:** `guild_bank` count = 1.
    3.  VU invokes `/bank withdraw item_id:<UUID>`.
    4.  **DB Check:** `guild_bank` status = 'WITHDRAWN', `withdrawn_by` = VU ID.
*   **Chaos Injection:** Two VUs try to withdraw the same UUID simultaneously. Database locking must prevent double-spend.

---

## 🔍 IV. The "Missing Cases" Hunt (Edge & Chaos)

The following scenarios are explicitly required to address the "Skeptic" agent's concerns.

### 1. The "Ghost in the Machine" (Partial Failures)
*   **Scenario:** Database write succeeds, but Discord Webhook fails (500/Timeout).
*   **Requirement:** The system must log the failure but *not* roll back the DB commit (Eventual Consistency) OR implementation of a retry queue. *Decision: v2.0 implements logging; v2.1 will implement retry queue.*

### 2. The "Forbidden Knowledge" (Injection Attacks)
*   **Scenario:** User inputs SQL injection or Discord Markdown injection in `backstory`.
*   **Requirement:** Pydantic validators must sanitize inputs. Discord messages must escape user content.

### 3. The "Image Void" (CDN Failures)
*   **Scenario:** User uploads an image, but the Discord CDN link is broken or 403.
*   **Requirement:** The `post_image_to_graphics_storage` tool must verify image accessibility before confirming the step. If fail, fallback to `DEFAULT_PORTRAIT_URL`.

### 4. The "Race of the Officers"
*   **Scenario:** Two officers click "Approve" on the same recruitment thread at the exact same second.
*   **Requirement:** Database constraint or application logic must handle the race condition. Only one should succeed; the second should receive "Already processed".

### 5. The "Zombie" (Recovery after Crash)
*   **Scenario:** Bot crashes during Step 6 of registration.
*   **Requirement:** Upon restart, the state is lost (in-memory) but the partial DB record (if any) must not block a new attempt.
*   **Test:** Simulate crash, then restart registration for same user.

---

## 📊 V. Pre-Commit Guarantees

Before any `git commit` is accepted, the **Local Sentinel** must pass:

1.  **Static Analysis:** `ruff check .` (Zero errors)
2.  **Type Safety:** `mypy .` (Strict mode)
3.  **Unit Tests:** `pytest tests/unit` (100% Pass)
4.  **Schema Check:** `alembic check` (DB models match migration files)

---

**"The Ink Must Not Fade."**
*Documentation driven by the necessities of the v2.0.0 Reformation.*