# Test-Driven Development (TDD) Workflow
**Date:** 2025-12-31
**Status:** ✅ Established
**Test Pass Rate:** 95.8% (115/120 tests passing)

---

## 🎯 TDD Philosophy for The Chronicler

**Core Principle:** Write tests FIRST, then implement code to pass them.

This ensures:
- ✅ Tests define behavior (not the other way around)
- ✅ 100% test coverage for new features
- ✅ Regression prevention
- ✅ Living documentation of expected behavior

---

## 📋 TDD Cycle (Red-Green-Refactor)

### **1. RED - Write a Failing Test**

Before writing ANY production code, write a test that describes the expected behavior.

```python
# Example: tests/services/test_new_feature.py
import pytest
from services.my_service import MyService

@pytest.mark.asyncio
async def test_new_feature_returns_expected_value():
    """Test that new feature returns correct value for valid input."""
    # Arrange
    service = MyService()
    input_data = {"key": "value"}

    # Act
    result = await service.new_feature(input_data)

    # Assert
    assert result["status"] == "success"
    assert result["data"] == "expected_output"
```

**Run the test - it MUST fail** (because the feature doesn't exist yet).

```bash
poetry run pytest tests/services/test_new_feature.py -v
# Expected: FAILED (MyService has no attribute 'new_feature')
```

---

### **2. GREEN - Write Minimum Code to Pass**

Implement ONLY enough code to make the test pass. No extra features.

```python
# services/my_service.py
class MyService:
    async def new_feature(self, input_data: dict) -> dict:
        """New feature implementation."""
        return {
            "status": "success",
            "data": "expected_output"
        }
```

**Run the test - it MUST pass now.**

```bash
poetry run pytest tests/services/test_new_feature.py -v
# Expected: PASSED
```

---

### **3. REFACTOR - Clean Up Code**

Now that tests pass, refactor for clarity, performance, or maintainability.

```python
# services/my_service.py
from typing import Dict, Any

class MyService:
    async def new_feature(self, input_data: Dict[str, Any]) -> Dict[str, str]:
        """Process input and return structured response.

        Args:
            input_data: Dictionary containing request data

        Returns:
            Dictionary with status and data fields
        """
        # Validate input
        if not input_data or "key" not in input_data:
            raise ValueError("Invalid input: 'key' is required")

        # Process (business logic here)
        processed_value = self._process_data(input_data["key"])

        return {
            "status": "success",
            "data": processed_value
        }

    def _process_data(self, value: str) -> str:
        """Internal processing logic."""
        return "expected_output"  # Replace with actual logic
```

**Run tests again - they should still pass.**

```bash
poetry run pytest tests/services/test_new_feature.py -v
# Expected: PASSED
```

---

## 🏗️ Test Structure Standards

### **Test File Organization**

```
tests/
├── unit/              # Pure functions, no I/O
│   ├── test_validators.py
│   └── domain/
│       └── test_game_data.py
├── integration/       # Multiple components together
│   ├── services/
│   │   └── test_character_service.py
│   └── test_webhooks.py
├── db/                # Database repository tests
│   ├── test_character_repository.py
│   └── test_graveyard_repository.py
├── services/          # Service layer tests
│   └── test_image_storage.py
├── integrations/      # External API tests
│   └── test_mcp_client.py
├── discord/           # Discord bot command tests
│   ├── test_registration_flow.py
│   └── test_officer_approval.py
└── e2e/               # Full end-to-end flows
    └── test_registration_full_flow.py
```

---

### **Test Naming Conventions**

**File:** `test_<module_name>.py`
**Class:** `Test<FeatureName>` (optional grouping)
**Function:** `test_<action>_<expected_result>`

```python
# Good examples:
test_create_character_with_valid_data_succeeds()
test_upload_image_too_large_raises_error()
test_trigger_workflow_connection_error_returns_failure()

# Bad examples:
test_character()  # Too vague
test_1()          # No meaning
test_everything() # Too broad
```

---

### **Test Structure (AAA Pattern)**

Every test should follow **Arrange-Act-Assert**:

```python
@pytest.mark.asyncio
async def test_create_character_with_valid_data_succeeds():
    """Test character creation with complete valid data."""
    # ARRANGE - Set up test data and dependencies
    character_data = CharacterCreate(
        discord_user_id=123456,
        discord_username="TestUser",
        name="Thorgar",
        race="Orc",
        class_name="Warrior",
        roles=[],
        professions=["Mining"],
        backstory="A brave warrior.",
        trait_1="Strong",
        trait_2="Loyal",
        trait_3="Brave"
    )
    repo = CharacterRepository(async_session)

    # ACT - Perform the action being tested
    result = await repo.create_character(character_data)

    # ASSERT - Verify expected outcomes
    assert result.id is not None
    assert result.name == "Thorgar"
    assert result.race == "Orc"
```

---

## 🧪 Testing Current Architecture

### **PostgreSQL Database Tests**

```python
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

@pytest_asyncio.fixture
async def character_repo(async_session: AsyncSession):
    """Fixture providing character repository with test DB session."""
    return CharacterRepository(async_session)

@pytest.mark.asyncio
async def test_database_operation(character_repo: CharacterRepository):
    """Test interacting with PostgreSQL."""
    # Test uses real test database (via testcontainers)
    result = await character_repo.get_all_characters()
    assert isinstance(result, list)
```

**Note:** Use `@pytest_asyncio.fixture` for async fixtures (not `@pytest.fixture`).

---

### **Cloudflare R2 (Image Storage) Tests**

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_r2_client():
    """Mock boto3 S3 client for R2."""
    with patch('services.image_storage.boto3.client') as mock_client:
        yield mock_client.return_value

@pytest.mark.asyncio
async def test_upload_image_to_r2_success(mock_r2_client):
    """Test successful image upload to R2."""
    # Mock the R2 response
    mock_r2_client.put_object = MagicMock()

    storage = ImageStorage(...)
    result = await storage.upload(image_bytes, "test.png")

    assert result.url.startswith("https://")
    mock_r2_client.put_object.assert_called_once()
```

---

### **External MCP Server Tests**

```python
def create_mock_response(status=200, json_data=None):
    """Helper to create aiohttp response mock with context manager support."""
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=json_data)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock()
    return mock_response

@pytest.mark.asyncio
async def test_mcp_workflow_trigger_success():
    """Test successful MCP workflow trigger."""
    mock_response = create_mock_response(
        status=200,
        json_data={"workflow_id": "wf_123", "status": "triggered"}
    )

    mock_session = AsyncMock()
    # Use MagicMock (not AsyncMock) for .request() to return context manager
    mock_session.request = MagicMock(return_value=mock_response)

    client = MCPWorkflowTrigger()
    client.session = mock_session

    result = await client.trigger_workflow(data)

    assert result.success is True
    assert result.workflow_id == "wf_123"
```

---

## 🚨 Common Testing Pitfalls (Lessons Learned)

### **1. Field Name Mismatches**

**Problem:**
```python
CharacterCreate(
    character_name="Test",  # ❌ Wrong! Field is 'name'
    discord_id=123          # ❌ Wrong! Field is 'discord_user_id'
)
```

**Solution:** Always check the Pydantic model definition first.

```python
CharacterCreate(
    name="Test",            # ✅ Correct
    discord_user_id=123     # ✅ Correct
)
```

---

### **2. Async Fixture Decorators**

**Problem:**
```python
@pytest.fixture  # ❌ Wrong for async fixtures
async def my_repo(session):
    return MyRepository(session)
```

**Solution:**
```python
@pytest_asyncio.fixture  # ✅ Correct
async def my_repo(session):
    return MyRepository(session)
```

---

### **3. Mocking Async Context Managers**

**Problem:**
```python
mock_session.request = AsyncMock(return_value=response)
# ❌ Causes: 'coroutine' object does not support async context manager protocol
```

**Solution:**
```python
# Use MagicMock for the method that returns a context manager
mock_session.request = MagicMock(return_value=response)
# response itself needs __aenter__ and __aexit__
response.__aenter__ = AsyncMock(return_value=response)
response.__aexit__ = AsyncMock()
```

---

### **4. Fixture Name Mismatches**

**Problem:**
```python
@pytest.fixture
def mock_discord_interaction():  # Defined with this name
    ...

async def test_something(mock_interaction):  # ❌ Wrong name
    ...
```

**Solution:** Use the exact fixture name defined in conftest.py.

```python
async def test_something(mock_discord_interaction):  # ✅ Matches fixture
    ...
```

---

## 📊 Test Coverage Goals

| Layer | Target Coverage | Current Status |
|-------|----------------|----------------|
| **Unit Tests** | 90%+ | ✅ Good coverage |
| **Integration Tests** | 80%+ | ✅ Good coverage |
| **Database Tests** | 95%+ | ✅ 100% (7/7 passing) |
| **Service Tests** | 90%+ | ✅ Good coverage |
| **Discord Command Tests** | 85%+ | ✅ Good coverage |
| **E2E Tests** | 70%+ | ⚠️ Needs expansion |

---

## 🔄 Continuous Testing Workflow

### **Before Committing Code**

```bash
# 1. Run affected tests
poetry run pytest tests/services/test_my_feature.py -v

# 2. Run full test suite
poetry run pytest tests/ -v

# 3. Check coverage (optional)
poetry run pytest tests/ --cov=. --cov-report=term-missing

# 4. Run linting
ruff check .
```

### **During Development**

```bash
# Watch mode (re-run tests on file changes)
poetry run pytest tests/ -f

# Run tests matching pattern
poetry run pytest tests/ -k "character" -v

# Stop on first failure (fast feedback)
poetry run pytest tests/ -x
```

---

## 📝 Example: Adding a New Feature (TDD)

### **Feature Request:** Add character search by name

#### **Step 1: Write Failing Test**

```python
# tests/db/test_character_repository.py

@pytest.mark.asyncio
async def test_search_characters_by_name_partial_match(character_repo):
    """Test searching characters by partial name match."""
    # Arrange
    await character_repo.create_character(CharacterCreate(
        name="Thorgar", discord_user_id=1, discord_username="user1",
        race="Orc", class_name="Warrior", roles=[], professions=[],
        backstory="Warrior", trait_1="A", trait_2="B", trait_3="C"
    ))
    await character_repo.create_character(CharacterCreate(
        name="Thorgrim", discord_user_id=2, discord_username="user2",
        race="Dwarf", class_name="Paladin", roles=[], professions=[],
        backstory="Paladin", trait_1="D", trait_2="E", trait_3="F"
    ))

    # Act
    results = await character_repo.search_by_name("Thor")

    # Assert
    assert len(results) == 2
    assert all("Thor" in char.name for char in results)
```

**Run:** `poetry run pytest tests/db/test_character_repository.py::test_search_characters_by_name_partial_match -v`
**Expected:** ❌ FAILED (method doesn't exist)

---

#### **Step 2: Implement Feature**

```python
# db/repositories.py

class CharacterRepository:
    async def search_by_name(self, query: str) -> List[Character]:
        """Search characters by partial name match (case-insensitive)."""
        async with self.session.begin():
            result = await self.session.execute(
                select(Character)
                .where(Character.name.ilike(f"%{query}%"))
                .order_by(Character.name)
            )
            return list(result.scalars().all())
```

**Run:** `poetry run pytest tests/db/test_character_repository.py::test_search_characters_by_name_partial_match -v`
**Expected:** ✅ PASSED

---

#### **Step 3: Add Edge Case Tests**

```python
@pytest.mark.asyncio
async def test_search_characters_by_name_no_results(character_repo):
    """Test search returns empty list when no matches."""
    results = await character_repo.search_by_name("NonExistent")
    assert results == []

@pytest.mark.asyncio
async def test_search_characters_by_name_case_insensitive(character_repo):
    """Test search is case-insensitive."""
    await character_repo.create_character(CharacterCreate(
        name="Arthas", ...
    ))

    results = await character_repo.search_by_name("ARTHAS")
    assert len(results) == 1
```

**Run all tests:** `poetry run pytest tests/db/ -v`
**Expected:** All pass ✅

---

## 🎓 TDD Best Practices

1. **Test Behavior, Not Implementation**
   - ✅ `test_character_creation_stores_data_correctly()`
   - ❌ `test_character_uses_sqlalchemy_insert()`

2. **One Assertion Per Concept**
   - Group related assertions, but keep focused
   - Use multiple tests for different scenarios

3. **Use Descriptive Test Names**
   - Test name should explain what's being tested and expected outcome
   - Someone reading the test list should understand the feature

4. **Keep Tests Fast**
   - Use mocks for external services
   - Minimize database operations
   - Run slow tests separately

5. **Tests Should Be Independent**
   - Each test should set up its own data
   - No test should depend on another test's side effects
   - Tests should pass in any order

6. **Update Tests When Requirements Change**
   - Failing tests are your early warning system
   - Don't delete tests just to make CI green
   - Fix tests or fix code - both should align with requirements

---

## 🚀 Next Steps

### **Immediate**
- ✅ TDD workflow established
- ✅ 95.8% test pass rate achieved
- ⚠️ Fix remaining 5 tests (4 MCP edge cases, 1 E2E)

### **Short-term**
- Add tests for new features before implementation
- Expand E2E test coverage
- Set up pre-commit hooks for automatic testing

### **Long-term**
- Achieve 100% test pass rate
- Add mutation testing
- Set up CI/CD pipeline with automated test runs
- Performance benchmarking tests

---

**For Azeroth Bound! For Clean Code! For the Tests!** ⚔️🧪
