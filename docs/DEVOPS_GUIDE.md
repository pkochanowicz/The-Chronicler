# Azeroth Bound Bot - DevOps Guide

**Consulted Agents:** @Tdci, @MasterBorrin, @Hyena, @Amelre

This guide covers the infrastructure, dependency management, and containerization strategies for the Azeroth Bound Bot.

---

## 🏗️ Dependency Management

We support multiple package managers. The project metadata is defined in `pyproject.toml` (standardized) and `requirements.txt` (legacy compatibility).

### Using Poetry (Recommended)

**Prerequisites:** [Poetry](https://python-poetry.org/)

1.  **Install dependencies:**
    ```bash
    poetry install
    ```
2.  **Run bot:**
    ```bash
    poetry run python main.py
    ```
3.  **Run tests:**
    ```bash
    poetry run pytest
    ```

### Using uv (High Performance)

**Prerequisites:** [uv](https://github.com/astral-sh/uv)

1.  **Install dependencies:**
    ```bash
    uv pip install -r pyproject.toml
    ```
    *Or sync venv:*
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip sync pyproject.toml
    ```

### Using pip (Standard)

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🐳 Containerization

We provide multiple Docker strategies for different environments.

### Strategy A: Production (Standard)
**File:** `Dockerfile`
Optimized for size using multi-stage builds.

```bash
docker build -t azeroth-bot:prod -f Dockerfile .
docker run --env-file .env azeroth-bot:prod
```

### Strategy B: Development (Compose)
**File:** `docker-compose.yml`
Mounts volumes for live editing and credentials.

```bash
docker-compose up --build
```

### Strategy C: Poetry-Native
**File:** `Dockerfile.poetry`
Uses Poetry to install dependencies inside the container.

```bash
docker build -t azeroth-bot:poetry -f Dockerfile.poetry .
```

### Strategy D: uv-Native
**File:** `Dockerfile.uv`
Uses `uv` for extremely fast build times.

```bash
docker build -t azeroth-bot:uv -f Dockerfile.uv .
```

---

## 🔐 Security & Permissions

**Agent @Hyena's Hardening Protocol:**

*   **Sensitive Files:** `.env`, `credentials.json` must be `600` (Read/Write Owner ONLY).
*   **Source Code:** `644` (Read/Write Owner, Read Group/Other).
*   **Scripts:** `755` (Execute enabled).

**Audit Command:**
```bash
find . -type f -perm -004 -name ".env*" -o -name "credentials.json"
# Should return nothing.
```

---

## 🧪 Testing Infrastructure

Run the full compatibility suite:

1.  **Local:** `pytest`
2.  **Lint:** `flake8`
3.  **Type Check:** `mypy .`

---

*Documentation maintained by the Guild DevOps Team.*
