# Azeroth Bound Bot - Deployment Guide (v2.1)

**Version:** 2.1.0 (Schema Reformation)
**Architecture:** FastAPI + Supabase (PostgreSQL) + Discord Bot
**Hosting:** Fly.io (Primary)
**Migration Strategy:** Alembic (Release Command)

---

## 🏗️ 1. Architecture Overview

This deployment uses a "GitOps-lite" workflow.
1.  **Code** is pushed to GitHub.
2.  **Fly.io** builds the Docker image.
3.  **Release Command** runs `alembic upgrade head` to sync the DB schema.
4.  **Application** starts only if migrations succeed.

## 🔑 2. Prerequisites

- **Fly.io Account** & CLI installed (`flyctl`).
- **Supabase Project** (PostgreSQL Database).
- **Discord Bot Application** (Token + Application ID).
- **Google Cloud Service Account** (Legacy support, if needed).

## 🚀 3. Fly.io Configuration

### `fly.toml` Specification

The `fly.toml` file is the source of truth for deployment configuration. Key sections:

```toml
[deploy]
  release_command = "alembic upgrade head"

[env]
  PYTHONUNBUFFERED = "1"
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
```

**Crucial Doctrine:** The `release_command` ensures that code and schema are *always* synchronized. If `alembic upgrade head` fails, the deployment aborts, preventing broken code from running against an old schema.

## 🔐 4. Environment Secrets

Set these secrets on Fly.io using `flyctl secrets set KEY=VALUE`.

### Database (Supabase)
*   `DATABASE_URL`: `postgresql+asyncpg://user:pass@host:5432/postgres` (Must be the **Transaction Pooler** URL for production, or Session URL for migration if pooler doesn't support prepared statements).
*   `SUPABASE_URL`: Your Supabase project URL.
*   `SUPABASE_KEY`: Your Supabase `service_role` key (for admin tasks).

### Discord
*   `DISCORD_BOT_TOKEN`: The bot's token.
*   `GUILD_ID`: ID of the Azeroth Bound guild.
*   `RECRUITMENT_CHANNEL_ID`: ID for `#recruitment`.
*   `CEMETERY_CHANNEL_ID`: ID for `#cemetery`.
*   `CHARACTER_SHEET_VAULT_CHANNEL_ID`: ID for `#character_sheet_vault`.

### Role IDs
*   `WANDERER_ROLE_ID`
*   `SEEKER_ROLE_ID`
*   `PATHFINDER_ROLE_ID`
*   `TRAILWARDEN_ROLE_ID`

### Application
*   `WEBHOOK_SECRET`: 32+ char string for validating incoming webhooks.
*   `ENV`: `production`

## 🛠️ 5. Deployment Commands

### Initial Setup
```bash
fly launch --no-deploy
```

### Deploying Changes
```bash
fly deploy
```

### Monitoring
```bash
fly logs
fly status
```

## 🔄 6. Database Migrations (Alembic)

**Never** run migrations manually in production. Let the `release_command` handle it.

### Creating a New Migration (Local Dev)
1.  Modify `schemas/db_schemas.py`.
2.  Run: `alembic revision --autogenerate -m "describe_change"`
3.  Inspect the generated file in `alembic/versions/`.
4.  Commit the file.

### Emergency Rollback
If a bad migration is deployed:
1.  SSH into the Fly instance: `fly ssh console`
2.  Downgrade: `alembic downgrade -1`
3.  *Note:* This is a last resort. Prefer reverting the code and deploying a fix.

## 🧪 7. Verification

After deployment:
1.  Check logs: `fly logs` (Look for "Running upgrade...")
2.  Verify `/health` endpoint returns 200 OK.
3.  Test `/db_search` to verify DB connectivity.

---
**"The Schema is the Law."**
