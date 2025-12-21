# The Chronicler: Test Suite Documentation (v2.0.0.1)

This document outlines the testing strategy for the new FastAPI and Supabase-based architecture. Our goal is to maintain and exceed our previous 98% test coverage.

## 1. Core Testing Philosophy
- **Test-Driven Development (TDD):** Write tests before or alongside implementation.
- **Layered Testing:** Unit, Integration, and End-to-End (E2E) tests for comprehensive coverage.
- **Isolation:** Tests must be isolated from each other and external dependencies (where possible).
- **Reproducibility:** Tests must produce consistent results across environments.

## 2. Testing Environment

Our testing environment is designed for isolation, reproducibility, and efficiency, specifically tailored for FastAPI and Supabase PostgreSQL.

### 2.1 Test Database Setup

A dedicated PostgreSQL test container is crucial for reliable integration and E2E tests.

- **Docker Compose:** We will use `docker-compose` to manage a test PostgreSQL container. This allows for:
    - **Isolation:** Each test run starts with a clean database instance.
    - **Reproducibility:** Consistent database state across all tests.
    - **Schema Migrations:** The test container will be initialized with the latest schema (`sql/schema_v1.sql`) before tests run.
- **Connection:** The FastAPI application and test runners will connect to this local test PostgreSQL instance using environment variables or a specific test configuration.
- **Data Seeding:** Test-specific data will be seeded programmatically within test fixtures or setup routines, ensuring that tests operate on known datasets.

### 2.2 FastAPI Application Testing

The FastAPI application will be tested in two primary modes:

- **Local Server:** For E2E tests, a local instance of the FastAPI application will be spun up. `httpx` will be used to make HTTP requests against this instance.
- **Test Client:** For faster integration tests of specific routers or dependencies, FastAPI's `TestClient` (from `fastapi.testclient`) can be utilized, allowing direct interaction with the application without a running server.

### 2.3 Supabase CLI & Tools

- **Schema Management:** The `supabase` CLI will be used for applying schema migrations (`sql/schema_v1.sql`) to the test PostgreSQL container, ensuring the test database reflects the production schema.
- **RLS Testing:** While RLS policies are primarily configured within Supabase, their effective implementation will be verified directly through integration tests by simulating different user roles and ensuring correct data access.

### 2.4 Async Testing

`pytest-asyncio` is essential for testing asynchronous code, allowing `async def` test functions and fixtures to interact seamlessly with FastAPI endpoints and asynchronous database operations.

## 3. Test Types and Placement

### 3.1 Mocking Strategies

Effective mocking is crucial for unit and integration tests, especially when dealing with external services or complex dependencies.

- **External APIs (e.g., Discord API):** Use `unittest.mock.patch` or `pytest-mock` to mock calls to the Discord API. This ensures tests are fast, deterministic, and don't rely on network access or rate limits.
- **Database Repositories:** For unit testing services, mock the database repository methods. This allows testing business logic without hitting the actual database.
- **Dependency Injection:** FastAPI's dependency injection system facilitates mocking. By overriding dependencies (e.g., `app.dependency_overrides`), we can swap out real database connections or external service clients with mock versions for testing.

### 3.2 Unit Tests:

- Location: `tests/unit/`
- Focus: Isolated testing of individual functions, classes, or modules (e.g., Pydantic model validation, utility functions).
- Tools: `pytest`, `unittest.mock`.

### 3.3 Integration Tests:

- Location: `tests/db/`, `tests/api/`, `tests/services/`
- Focus: Testing the interaction between different components, particularly the data access layer and the API.
- `tests/db/`: Tests for repository layer (`CharacterRepository`, `GraveyardRepository`, etc.) interacting with the test DB container.
- `tests/api/`: Tests for FastAPI routers and services, including E2E flows interacting with the test DB.
- Tools: `pytest`, `pytest-asyncio`, `httpx`, `SQLAlchemy` (or Supabase client library), `psycopg2` (or equivalent for DB interaction), `docker` (for container management).

### 3.4 End-to-End (E2E) Trials:

- Location: `tests/e2e/` (or simulated via MCP as per Stage 5)
- Focus: Simulating user interactions through the system, from Discord to Supabase.
- Tools: `chronicler-mcp` (simulated user), `pytest`.

## 4. Key Testing Areas to Cover
- **Database Layer:**
    - CRUD operations for `characters`, `graveyard`, `character_talents`.
    - Schema integrity and constraints.
    - RLS policy enforcement.
    - Data migrations.
- **API Layer (FastAPI):**
    - Endpoint availability and correct routing.
    - Request validation (Pydantic models).
    - Response serialization.
    - Business logic execution in services.
    - Error handling and response codes.
- **Discord Integration:**
    - Command handling.
    - Interaction responses.
    - Webhook processing.
    - Real-time updates (if applicable via Supabase Realtime).
- **Turtle WoW Specifics:**
    - `challenge_mode` and `story` field handling.
    - Hardcore/Inferno character logic.
    - Talent selection and linking.
- **Security:**
    - RLS policies correctly restricting access.
    - Authentication/Authorization flows.

## 5. Test Suite Maintenance
- Tests must be updated whenever schema, API, or business logic changes.
- Coverage reports will be monitored regularly.