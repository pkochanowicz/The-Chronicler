# 🔧 The Chronicler Emergency Repair Mission

**Mission Briefing:** The Chronicler has been deployed to fly.io but is experiencing two critical issues that need immediate attention.

---

## 🚨 Issue #1: Health Check Failure (CRITICAL)

**Symptom:** Fly.io health checks to `/health` endpoint are failing. Machines start but the endpoint doesn't respond.

**Potential Causes:**
1. FastAPI app not binding to port 8080 (fly.io expects this)
2. Health endpoint route not registered
3. Bot startup blocking the webhook server
4. Lifespan context manager failing silently

**Diagnostic Steps:**
```bash
# 1. Check what port the app is configured to bind to
grep -r "8080\|port" main.py config/settings.py fly.toml

# 2. Verify /health endpoint exists
grep -rn "health" main.py --include="*.py"

# 3. Check the fly.toml health check configuration
cat fly.toml | grep -A5 "http_checks"

# 4. Check for any startup errors in recent logs
fly logs --app the-chronicler | head -100
```

**Expected Fix Location:** `main.py` - ensure:
- FastAPI app binds to `0.0.0.0:8080`
- `/health` endpoint is defined and returns 200
- Uvicorn starts without blocking issues

---

## 🚨 Issue #2: Missing Discord Commands

**Currently Working:**
- `/bank deposit`
- `/bank mydeposits`
- `/bank view`
- `/bank withdraw`
- `/talent audit`

**Missing (documented in `docs/USER_GUIDE.md`):**
- `/register_character` - Character registration wizard
- `/talent editor` - Interactive talent builder
- `/db_search [type] [query]` - Database search (item, quest, npc, spell)
- `/bury` - Officer-only burial ceremony

**Diagnostic Steps:**
```bash
# 1. Find all slash command definitions
grep -rn "@app_commands\|@bot.tree\|\.command\|@commands\.hybrid" commands/ --include="*.py"

# 2. Check which cogs are being loaded in main.py
grep -n "load_extension\|add_cog\|setup_hook" main.py

# 3. Find register_character implementation
find . -name "*.py" -exec grep -l "register_character" {} \;

# 4. Find db_search implementation
find . -name "*.py" -exec grep -l "db_search" {} \;

# 5. Find talent editor implementation
grep -rn "talent.*editor\|editor.*talent" --include="*.py"

# 6. Find bury command implementation
grep -rn "def bury\|async def bury\|name=\"bury\"" --include="*.py"

# 7. Check if commands exist but aren't registered
cat commands/__init__.py
ls -la commands/
```

---

## 📋 Implementation Checklist

### For Health Check:

1. [ ] Verify `main.py` has a `/health` endpoint:
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "service": "the-chronicler"}
   ```

2. [ ] Verify Uvicorn binds to correct host/port:
   ```python
   uvicorn.run(app, host="0.0.0.0", port=8080)
   ```

3. [ ] Verify `fly.toml` has correct internal port:
   ```toml
   [[services]]
     internal_port = 8080
   ```

4. [ ] Check lifespan doesn't fail silently - add try/catch logging

### For Missing Commands:

For each missing command, check:
1. [ ] Command file exists in `commands/` directory
2. [ ] Command is properly decorated with `@app_commands.command()`
3. [ ] Cog is loaded via `bot.load_extension()` in `main.py` or setup hook
4. [ ] Command is synced to Discord (may need `bot.tree.sync()`)

**Command Locations (per architecture docs):**
- `/register_character` → `flows/registration_flow.py` (should have command trigger)
- `/talent editor` → `commands/talent_commands.py`
- `/db_search` → Should be in `commands/` or `commands/search_commands.py`
- `/bury` → `commands/officer_commands.py` (per CLEANUP_REPORT)

---

## 🎯 Action Plan

### Phase 1: Health Check Fix
```bash
# Inspect and fix the health endpoint issue first
# This is blocking production functionality
```

### Phase 2: Command Audit
```bash
# Create a report of:
# - All defined commands in codebase
# - All loaded cogs in main.py
# - Gap analysis vs USER_GUIDE.md
```

### Phase 3: Implement Missing Commands

**Priority Order:**
1. `/register_character` - Core guild functionality
2. `/bury` - Officer workflow (already in officer_commands.py per report)
3. `/db_search` - User utility
4. `/talent editor` - Enhancement feature

### Phase 4: Deploy & Verify
```bash
# After fixes:
fly deploy --app the-chronicler
fly logs --app the-chronicler

# Test each command in Discord
```

---

## 📁 Key Files to Examine

```
main.py                          # FastAPI app + bot startup
fly.toml                         # Fly.io configuration
config/settings.py               # Port and environment config
commands/__init__.py             # Cog registration
commands/talent_commands.py      # Talent audit (working) + editor (missing?)
commands/officer_commands.py     # Bury command location
commands/bank_commands.py        # Bank commands (working - reference)
flows/registration_flow.py       # Registration wizard flow
docs/USER_GUIDE.md              # Canonical command documentation
docs/architecture_features_v2.md # Command specifications
```

---

## ⚠️ Important Notes

1. **Don't break working commands** - Bank and talent audit work, preserve their patterns
2. **Check Discord sync** - Commands need `bot.tree.sync()` after changes
3. **Environment variables** - Ensure all required vars are set on fly.io (26 secrets confirmed)
4. **Test locally first** if possible before deploying

---

## 🎬 Start Here

Begin by running the diagnostic commands above, then report:
1. What's in the health endpoint configuration
2. Which command files exist vs. which are loaded
3. Whether missing commands are partially implemented or completely absent

Let's get The Chronicler fully operational! ⚔️
