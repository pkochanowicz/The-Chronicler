# The Chronicler: Test Suite & Quality Assurance (v2.0.0 "Reformation")

**Status:** Living Document  
**Architecture:** FastAPI + Supabase (PostgreSQL) + Discord Bot  
**Coverage Target:** 100% Core Logic / 95% Overall

---

## 1. The Philosophy of Verification

We do not hope code works; we **prove** it works.
The test suite is the first line of defense against the corruption of our archives.

### 1.1 The Testing Pyramid
1.  **Unit Tests (Fast):** Verify individual functions, validators, and models in isolation.
2.  **Integration Tests (Medium):** Verify interactions between Services, Repositories, and the Database.
3.  **End-to-End (E2E) Trials (Slow):** Simulate full user flows from Discord command to Database persistence.

### 1.2 The "Split Brain" Prevention Protocol
A specific subset of tests is dedicated to ensuring **NO** logic accidentally reverts to legacy Google Sheets paths.
- **Rule:** If a test attempts to import `gspread`, it fails.
- **Rule:** If a test attempts to connect to `sheets.googleapis.com`, it fails.

---

## 2. Test Environment Configuration

### 2.1 Technology Stack
- **Runner:** `pytest`
- **AsyncIO:** `pytest-asyncio` (Strict mode)
- **Database:** `testcontainers` (PostgreSQL) or Local Docker
- **HTTP Client:** `httpx` (Async)
- **Mocking:** `pytest-mock`

### 2.2 Database Isolation
Every test run must operate on a **clean, ephemeral database**.
- **Schema:** Automatically applied from `sql/schema_v1.sql`.
- **Seeding:** `tests/conftest.py` provides fixtures for:
  - `active_user_id` (Discord ID)
  - `mock_character` (Level 60 Warrior)
  - `mock_guild_bank_item` (Obsidian Edged Blade)

---

## 3. Comprehensive Test Scenarios

### 3.1 🛡️ Domain Layer (Unit Tests)
*Location: `tests/unit/`*

#### `test_validators.py`
- [ ] **Race/Class Compatibility:** Verify `validate_race_class("Orc", "Paladin")` raises `ValueError`.
- [ ] **Talent Math:** Verify `validate_talent_points` rejects builds with >51 points in a tree.
- [ ] **Name Sanitization:** Verify names with special characters are rejected or cleaned.

#### `test_models.py`
- [ ] **Pydantic Validation:** Ensure `CharacterCreate` model rejects missing required fields.
- [ ] **Enum Integrity:** Ensure `status` field accepts only valid enum values (PENDING, REGISTERED, etc.).

### 3.2 ⚙️ Service Layer (Integration Tests)
*Location: `tests/integration/`*

#### `test_character_service.py`
- [ ] **Create Character:**
  - Input: Valid `CharacterCreate` DTO.
  - Action: `service.create_character()`.
  - Assert: Record exists in DB, UUID generated, timestamps set.
- [ ] **Duplicate Prevention:**
  - Action: Create character with same name twice.
  - Assert: `IntegrityError` or Custom Exception handling.
- [ ] **Soft Delete/Archive:**
  - Action: `service.delete_character()`.
  - Assert: Character not returned in `get_all`, but exists in audit logs (if implemented).

#### `test_bank_service.py`
- [ ] **Deposit Item:**
  - Action: Deposit "Linen Cloth" x20.
  - Assert: New `bank_items` row, status='AVAILABLE'.
- [ ] **Withdraw Item:**
  - Action: Withdraw item UUID.
  - Assert: Status changes to 'WITHDRAWN', `withdrawn_by` field populated.
- [ ] **Concurrency:**
  - Action: Two users try to withdraw same item simultaneously.
  - Assert: Only one succeeds (Database Locking check).

### 3.3 🌐 API Gateway (FastAPI Tests)
*Location: `tests/api/`*

#### `test_webhooks.py`
- [ ] **Signature Verification:**
  - Action: POST to `/webhooks/discord` with invalid signature/secret.
  - Assert: 401 Unauthorized.
- [ ] **Payload Parsing:**
  - Action: POST valid payload.
  - Assert: Background task spawned, 200 OK returned immediately.

#### `test_health.py`
- [ ] **Liveness:** GET `/health` returns 200.
- [ ] **Readiness:** GET `/health?check=db` verifies DB connection.

### 3.4 🤖 Discord Bot (Mocked Integration)
*Location: `tests/bot/`*

#### `test_registration_flow.py`
- [ ] **Step Traversal:** Simulate user interaction through all 12 steps.
- [ ] **Timeout Handling:** Simulate user inactivity > 300s. Assert flow cancellation.
- [ ] **Finalization:** Ensure `Finish` button triggers `CharacterService.create_character`.

#### `test_burial_flow.py`
- [ ] **Search:** Simulate searching for non-existent character. Assert error message.
- [ ] **Burial:** Simulate completing burial. Assert `GraveyardRepository` entry created and Character status = `DECEASED`.

---

## 4. The "Migration Audit" Suite
*Specialized tests to ensure v2.0.0 compliance.*

- [ ] **No-Gspread Check:** Scan all loaded modules during test execution. Fail if `gspread` is present.
- [ ] **Env Var Check:** Fail if `GOOGLE_SHEET_ID` is accessed by any runtime service.
- [ ] **DB Connection Check:** Fail if `DATABASE_URL` is not set.

---

## 5. Execution Guide

### Running the Suite
```bash
# Run all tests
pytest

# Run only "Fast" unit tests
pytest tests/unit

# Run full integration suite with Docker DB
pytest tests/integration --run-slow
```

### Continuous Integration (CI)
Github Actions pipeline must:
1.  Lint (`ruff`).
2.  Type Check (`mypy`).
3.  Run `pytest`.
4.  Build Docker Image.
5.  Deploy to Fly.io (only on `main`).

---

**"Trust, but verify. Then verify again."**
*-- Thaldrin the Chronicler*
