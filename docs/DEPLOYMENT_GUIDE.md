# DEPRECATED: This Deployment Guide is for the *previous* Google Sheets-based architecture.
# A new deployment guide for the FastAPI/Supabase stack is required.

# Azeroth Bound Bot - Deployment Guide

**Version:** 2.0.0 (Schema Reformation)  
**Architecture:** Path B (Webhook-Driven)  
**Hosting Options:** Fly.io (recommended) | Render.com (alternative)  
**Monthly Cost:** $0.00 (free tier)  
**Python Version:** 3.11 (recommended for stability)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Option A: Fly.io Deployment (Recommended)](#option-a-flyio-deployment-recommended)
4. [Option B: Render.com Deployment](#option-b-rendercom-deployment)
5. [Post-Deployment Setup](#post-deployment-setup)
6. [Verification Checklist](#verification-checklist)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ **Python 3.11+** bot code ready (3.11 recommended for production stability)
- ✅ **Google Cloud service account** credentials (`credentials.json`)
- ✅ **Discord bot token** and all channel/role IDs
- ✅ **Google Sheets** with 27-column schema created
- ✅ **`.env` file** configured locally and tested
- ✅ **Git repository** (GitHub, GitLab, or Bitbucket)
- ✅ **All tests passing** (`pytest` shows green)

**Verify local setup first:**
```bash
# Test configuration loads
python -c "from config import settings; print('✅ Config OK')"

# Run tests
pytest

# Test bot can start (Ctrl+C to stop)
python main.py
```

---

## Deployment Options

### Fly.io (Recommended)

**Pros:**
- ✅ Free tier: 3 VMs with 256MB RAM each (forever free)
- ✅ Easy deployment via `flyctl` CLI
- ✅ Built-in health checks and auto-restart
- ✅ Automatic HTTPS
- ✅ Fast global CDN
- ✅ Excellent Python support
- ✅ No spin-down (always online)

**Cons:**
- ❌ Requires credit card for verification (won't be charged on free tier)
- ❌ Slightly more complex initial setup than Render

**Best for:** Production deployment with high availability

---

### Render.com (Alternative)

**Pros:**
- ✅ Free tier: 750 hours/month
- ✅ No credit card required
- ✅ Web dashboard (easier for beginners)
- ✅ Auto-deploy from Git
- ✅ Built-in logging

**Cons:**
- ❌ **Spins down after 15 min of inactivity** (cold start delays)
- ❌ Slower cold starts (30-60 seconds)
- ❌ Only 1 free web service
- ❌ May miss webhook triggers during spin-down

**Best for:** Testing or very low-traffic guilds

---

## Option A: Fly.io Deployment (Recommended)

### Step 1: Install Fly CLI

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Verify installation:**
```bash
flyctl version
```

---

### Step 2: Sign Up and Authenticate
```bash
# Sign up (if new user)
flyctl auth signup

# OR login (if existing user)
flyctl auth login
```

**Add payment method (required for free tier):**
- Go to https://fly.io/dashboard/personal/billing
- Add credit card (verification only, won't be charged)
- Free tier includes: 3 VMs (256MB each), 160GB bandwidth/month

---

### Step 3: Initialize Fly App

**From your project root directory:**
```bash
flyctl launch
```

**Answer the prompts:**
- **App name:** `azeroth-bound-bot` (or your choice, must be unique)
- **Region:** Choose closest to your location (e.g., `iad` for US East)
- **Set up PostgreSQL database?** → **NO** (we use Google Sheets)
- **Set up Redis database?** → **NO**
- **Deploy now?** → **NO** (we need to set secrets first)

This creates `fly.toml` in your project root.

---

### Step 4: Configure fly.toml

**Verify/edit `fly.toml`:**
```toml
# fly.toml - Fly.io Configuration

app = "azeroth-bound-bot"  # Your app name
primary_region = "iad"      # Your chosen region

[build]
  # Fly will auto-detect Python and use buildpacks

[env]
  PORT = "8080"
  PYTHONUNBUFFERED = "1"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false  # Keep bot running 24/7
  auto_start_machines = true
  min_machines_running = 1    # Always 1 instance online

[[http_service.checks]]
  interval = "15s"
  timeout = "10s"
  grace_period = "30s"
  method = "GET"
  path = "/health"
```

**Add health check endpoint to `main.py`** (if not already present):
```python
from aiohttp import web

async def health_handler(request):
    """Health check endpoint for Fly.io."""
    return web.Response(text="OK", status=200)

# In your app setup
app.router.add_get('/health', health_handler)
```

---

### Step 5: Set Environment Secrets

**Set ALL environment variables as Fly secrets:**
```bash
# Discord Configuration
flyctl secrets set DISCORD_BOT_TOKEN="your_discord_bot_token_here"
flyctl secrets set GUILD_ID="your_guild_id_here"
flyctl secrets set RECRUITMENT_CHANNEL_ID="your_recruitment_channel_id"
flyctl secrets set FORUM_CHANNEL_ID="your_forum_channel_id"
flyctl secrets set CEMETERY_CHANNEL_ID="your_cemetery_channel_id"

# Guild Member Role IDs (individual, not comma-separated!)
flyctl secrets set WANDERER_ROLE_ID="your_wanderer_role_id"
flyctl secrets set SEEKER_ROLE_ID="your_seeker_role_id"
flyctl secrets set PATHFINDER_ROLE_ID="your_pathfinder_role_id"
flyctl secrets set TRAILWARDEN_ROLE_ID="your_trailwarden_role_id"

# Officer Role Mentions (format: <@&ROLE_ID>)
flyctl secrets set PATHFINDER_ROLE_MENTION="<@&your_pathfinder_role_id>"
flyctl secrets set TRAILWARDEN_ROLE_MENTION="<@&your_trailwarden_role_id>"

# Google Sheets
flyctl secrets set GOOGLE_SHEET_ID="your_google_sheet_id"
flyctl secrets set BACKUP_FOLDER_ID="your_backup_folder_id"

# Webhook Security
flyctl secrets set WEBHOOK_SECRET="your_random_32_char_secret"

# Bot Behavior
flyctl secrets set INTERACTIVE_TIMEOUT_SECONDS="300"
flyctl secrets set POLL_INTERVAL_SECONDS="60"

# Visuals
flyctl secrets set DEFAULT_PORTRAIT_URL="https://i.imgur.com/placeholder.png"
```

**Verify secrets were set:**
```bash
flyctl secrets list
```

---

### Step 6: Upload Google Credentials (Base64)

**Fly.io doesn't support file uploads, so we encode credentials as base64:**
```bash
# Encode credentials
cat credentials.json | base64 > credentials_b64.txt

# Set as secret (single line, no newlines)
flyctl secrets set GOOGLE_CREDENTIALS_B64="$(cat credentials_b64.txt | tr -d '\n')"
```

**How this works:**
- `config/settings.py` automatically detects `GOOGLE_CREDENTIALS_B64`
- Decodes it from base64 at runtime
- Writes to `/tmp/credentials.json` for `gspread` to use
- See `_setup_google_credentials()` method in settings.py

---

### Step 7: Deploy!
```bash
flyctl deploy
```

**This will:**
1. Build your app (install dependencies)
2. Create Docker image
3. Deploy to Fly.io infrastructure
4. Start your bot

**Watch deployment progress:**
```bash
flyctl logs
```

**Check status:**
```bash
flyctl status
```

**Your bot's webhook URL will be:**
```
https://azeroth-bound-bot.fly.dev/webhook
```

---

### Step 8: Configure Google Apps Script

**In your Google Apps Script `webhook.gs`, update:**
```javascript
const WEBHOOK_URL = "https://azeroth-bound-bot.fly.dev/webhook";
const WEBHOOK_SECRET = "your_random_32_char_secret"; // Must match Fly secret
```

**Test the webhook:**
```javascript
function testWebhook() {
  var payload = {
    "secret": WEBHOOK_SECRET,
    "trigger": "TEST",
    "character": {},
    "timestamp": new Date().toISOString()
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  var response = UrlFetchApp.fetch(WEBHOOK_URL, options);
  Logger.log(response.getContentText()); // Should log "OK"
}
```

---

## Option B: Render.com Deployment

### Step 1: Sign Up

1. Go to https://render.com
2. Sign up with GitHub (recommended for auto-deploy)

---

### Step 2: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select the `azeroth_bound_bot` repo
4. Grant Render access to the repo

---

### Step 3: Configure Service

**Name:** `azeroth-bound-bot`

**Environment:** `Python 3`

**Region:** Choose closest to you

**Branch:** `main` (or your deployment branch)

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python main.py
```

**Plan:** `Free`

---

### Step 4: Add Environment Variables

**Click "Environment" tab, add ALL variables:**
```bash
# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_here
RECRUITMENT_CHANNEL_ID=your_recruitment_channel_id
FORUM_CHANNEL_ID=your_forum_channel_id
CEMETERY_CHANNEL_ID=your_cemetery_channel_id

# Guild Member Role IDs (individual!)
WANDERER_ROLE_ID=your_wanderer_role_id
SEEKER_ROLE_ID=your_seeker_role_id
PATHFINDER_ROLE_ID=your_pathfinder_role_id
TRAILWARDEN_ROLE_ID=your_trailwarden_role_id

# Officer Role Mentions
PATHFINDER_ROLE_MENTION=<@&your_pathfinder_role_id>
TRAILWARDEN_ROLE_MENTION=<@&your_trailwarden_role_id>

# Google Sheets
GOOGLE_SHEET_ID=your_google_sheet_id
BACKUP_FOLDER_ID=your_backup_folder_id

# Webhook Security
WEBHOOK_SECRET=your_random_32_char_secret

# Bot Behavior
INTERACTIVE_TIMEOUT_SECONDS=300
POLL_INTERVAL_SECONDS=60

# Visuals
DEFAULT_PORTRAIT_URL=https://i.imgur.com/placeholder.png

# Render-specific (auto-set by Render, but can override)
PORT=10000
```

---

### Step 5: Add Google Credentials (Base64)

**Encode locally:**
```bash
cat credentials.json | base64 > credentials_b64.txt
```

**Add to Render environment:**
1. Click "Add Environment Variable"
2. Key: `GOOGLE_CREDENTIALS_B64`
3. Value: Paste entire base64 string (may be very long, that's OK)

**How this works:**
- Same as Fly.io - `config/settings.py` decodes automatically
- See `_setup_google_credentials()` method

---

### Step 6: Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repo
2. Run build command
3. Start the bot
4. Assign URL

**Your webhook URL:**
```
https://azeroth-bound-bot.onrender.com/webhook
```

---

### Step 7: Keep Bot Awake (Critical!)

**⚠️ Render free tier spins down after 15 min of inactivity!**

**Option 1: Use UptimeRobot (Recommended)**

1. Sign up at https://uptimerobot.com (free, no credit card)
2. Create new monitor:
   - **Type:** HTTP(s)
   - **URL:** `https://azeroth-bound-bot.onrender.com/health`
   - **Interval:** 5 minutes
3. This will ping your bot every 5 minutes, keeping it awake

**Option 2: Cron-job.org Alternative**

1. Sign up at https://cron-job.org
2. Create job to hit `/health` endpoint every 5 minutes

**Without this, your bot will:**
- Go offline after 15 min of inactivity
- Miss webhook triggers from Google Apps Script
- Take 30-60 seconds to wake up when Discord command is used

---

## Post-Deployment Setup

### 1. Verify Bot is Online

**Check Discord:**
- Bot should show as online (green status)
- Bot's "About Me" should show correct info

**If bot is offline:**
```bash
# Fly.io
flyctl logs

# Render.com
# Check Logs tab in dashboard
```

---

### 2. Test Slash Commands

**In Discord, type:**
```
/register_character
```

**Expected result:**
- Command appears in autocomplete
- Clicking it starts the interactive flow

**If command doesn't appear:**
- Wait 1-2 minutes (Discord caches commands)
- Check bot has correct permissions in Discord Developer Portal
- Check bot logs for errors

---

### 3. Test Webhook Endpoint

**Test with curl:**
```bash
curl -X POST https://your-bot-url.fly.dev/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_webhook_secret",
    "trigger": "TEST",
    "character": {},
    "timestamp": "2025-12-17T10:30:00Z"
  }'
```

**Expected response:** `OK`

**If 401 Unauthorized:**
- Secret mismatch between curl and bot

**If 404 Not Found:**
- Webhook endpoint not registered in main.py

---

### 4. Configure Google Apps Script Webhooks

**See:** [GOOGLE_APPS_SCRIPT_SETUP.md](./GOOGLE_APPS_SCRIPT_SETUP.md)

**Quick setup:**
1. Open your Google Sheet
2. Extensions → Apps Script
3. Paste `webhook.gs` code
4. Update `WEBHOOK_URL` and `WEBHOOK_SECRET`
5. Set up `onChange` trigger
6. Test with `testWebhook()` function

---

### 5. Create Test Character

**Complete end-to-end test:**

1. Use `/register_character` in Discord
2. Complete all 12 steps
3. Confirm submission

**Verify:**
- ✅ Character written to Google Sheets (check row appears)
- ✅ Webhook fired (check Apps Script logs)
- ✅ Posted to #recruitment channel
- ✅ You received DM confirmation
- ✅ ✅❌ reactions added to recruitment post

**If any step fails, check logs!**

---

## Verification Checklist

### Bot Deployment ✅

- [ ] Bot shows online in Discord
- [ ] Slash commands appear (`/register_character`, `/bury`)
- [ ] Bot can send messages in all configured channels
- [ ] Bot has correct permissions:
  - Send Messages
  - Manage Threads
  - Add Reactions
  - Create Forum Posts
  - Mention @everyone (in cemetery only)

### Webhook System ✅

- [ ] Webhook URL is accessible (returns 404 or 405 on GET)
- [ ] Webhook accepts POST with valid secret
- [ ] Google Apps Script can POST successfully
- [ ] Webhooks fire when sheet changes

### Interactive Flows ✅

- [ ] `/register_character` starts 12-step flow
- [ ] All steps validate input correctly
- [ ] Dropdowns show correct options (races, classes, roles)
- [ ] Embed preview displays correctly
- [ ] Final inscription writes to sheets

### Data Flow ✅

- [ ] Character data writes to Google Sheets (all 27 columns)
- [ ] `confirmation=TRUE` + `status=PENDING` triggers recruitment post
- [ ] Officer approval (✅) creates forum post in #character-sheet-vault
- [ ] Officer rejection (❌) sends DM to user
- [ ] `status=REGISTERED` updates in sheet after approval

### Lifecycle Management ✅

- [ ] `/bury` starts interactive ceremony (officer only)
- [ ] Non-officers cannot use `/bury`
- [ ] Setting `status=DECEASED` triggers burial webhook
- [ ] Cemetery thread created with ceremonial formatting
- [ ] Character owner receives DM notification
- [ ] Original thread archived

---

## Troubleshooting

### Bot Won't Start

**Check logs:**

**Fly.io:**
```bash
flyctl logs --app azeroth-bound-bot
```

**Render.com:**
- Dashboard → Your Service → Logs tab

**Common errors:**

#### 1. Missing Environment Variables

**Error:** `ValueError: Missing required configuration: DISCORD_BOT_TOKEN`

**Fix:**
```bash
# Fly.io
flyctl secrets set DISCORD_BOT_TOKEN="your_token"

# Render.com
# Add in dashboard Environment tab
```

#### 2. Google Credentials Invalid

**Error:** `Failed to decode GOOGLE_CREDENTIALS_B64`

**Fix:**
```bash
# Re-encode (ensure no newlines!)
cat credentials.json | base64 | tr -d '\n' > credentials_b64.txt

# Update secret
flyctl secrets set GOOGLE_CREDENTIALS_B64="$(cat credentials_b64.txt)"
```

#### 3. Discord Token Invalid

**Error:** `discord.errors.LoginFailure: Improper token`

**Fix:**
1. Go to Discord Developer Portal
2. Bot section → Reset Token
3. Update `DISCORD_BOT_TOKEN` secret

#### 4. Webhook Secret Too Short

**Error:** `ValueError: WEBHOOK_SECRET must be at least 32 characters`

**Fix:**
```bash
# Generate new secret
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Set it
flyctl secrets set WEBHOOK_SECRET="<generated_secret>"
```

---

### Webhooks Not Working

**Symptoms:**
- Character registers but recruitment post never appears
- Burial doesn't trigger cemetery ceremony

**Debug steps:**

#### 1. Test Webhook Endpoint
```bash
curl -X POST https://your-app.fly.dev/webhook \
  -H "Content-Type: application/json" \
  -d '{"secret":"your_secret","trigger":"TEST","character":{},"timestamp":"2025-12-17T10:00:00Z"}'
```

**Expected:** `OK` (200 status)

**If 401:** Secret mismatch
**If 404:** Webhook endpoint not registered
**If 500:** Check bot logs for errors

#### 2. Check Apps Script Logs

In Apps Script editor:
- View → Execution Log
- Look for errors in `onChange` or `sendWebhook`

**Common issues:**
- `WEBHOOK_URL` incorrect
- `WEBHOOK_SECRET` doesn't match bot
- Trigger not configured (Extensions → Triggers)

#### 3. Verify Sheet Schema

Webhook triggers depend on specific columns:
- `confirmation` column exists
- `status` column exists
- Column names exactly match (case-sensitive)

---

### Render.com Bot Spinning Down

**Symptoms:**
- Bot offline every 15+ minutes
- Slash commands disappear
- Webhooks fail during downtime

**Solution:**
- **Set up UptimeRobot** (see Step 7 in Render deployment)
- Pings `/health` endpoint every 5 minutes
- Keeps bot awake 24/7 on free tier

**Alternative:**
- Upgrade to Render Starter plan ($7/month) - no spin-down

---

### High Memory Usage

**Fly.io free tier:** 256MB per VM

**If bot crashes with memory errors:**

**Short-term fixes:**
1. Clear old interaction data periodically
2. Limit embed cache size
3. Use pagination for large queries

**Long-term solution:**
```bash
# Scale to 512MB VM ($1.94/month)
flyctl scale memory 512
```

---

### Google Sheets API Rate Limits

**Free tier limits:**
- 100 requests per 100 seconds per user
- 500 requests per 100 seconds per project

**If exceeded:**
- Bot raises `gspread.exceptions.APIError`
- Wait 100 seconds and retry

**Prevention:**
- Batch writes when possible
- Cache sheet data locally
- Add exponential backoff retry logic

---

## Scaling Beyond Free Tier

### When to upgrade:

- Guild has 100+ active members
- 50+ character registrations per day
- Need 99.9% uptime SLA
- Multiple concurrent interactive flows

### Recommended upgrades:

**Fly.io:**
- **$1.94/month:** 512MB VM (2x memory)
- **$3.88/month:** 1GB VM (4x memory)
- **$5.82/month:** 2 VMs (high availability)

**Render.com:**
- **$7/month:** Starter plan (no spin-down, faster)
- **$15/month:** Standard plan (more reliable, better performance)

---

## Support & Resources

**Having issues?**

1. **Check bot logs first** (most errors are logged)
2. **Verify environment variables** (missing values are #1 cause)
3. **Test webhook endpoint manually** (curl command above)
4. **Review architecture:** [TECHNICAL.md](./TECHNICAL.md)
5. **Check Google Apps Script logs** (see execution history)
6. **Ask in guild tech support channel**

**Useful commands:**
```bash
# Fly.io
flyctl logs              # View recent logs
flyctl status            # Check app status
flyctl secrets list      # List secret names (not values)
flyctl ssh console       # SSH into VM
flyctl scale show        # Show resource allocation

# Test locally
pytest                   # Run test suite
python main.py           # Start bot locally
python -m pytest -v      # Verbose test output
```

---

**For Azeroth Bound! For Deployment! For Zero Downtime!** ⚔️

*Last updated: December 17, 2025*  
*Version: 2.0.0*  
*Status: Production Ready*  
*Tested on: Fly.io (Python 3.11) | Render.com (Python 3.11)*
```

---

## 📊 **TASK C: COMMIT MESSAGE SUMMARY**

*Opens a ledger of all changes since the license discussion*

### **Short Summary for Git Commit:**
```
fix(config,docs): correct settings validation and deployment guides

- Fix config/settings.py: validation methods now properly called in __init__
- Fix environment variable naming: lowercase role IDs changed to UPPERCASE
- Add Google credentials base64 decoding (working for Fly.io/Render.com)
- Fix GUILD_MEMBER_ROLE_IDS and OFFICER_ROLE_IDS as computed properties
- Update .env.example with all required variables (removed invalid comma-separated lists)
- Correct DEPLOYMENT_GUIDE.md: remove Procfile references, add proper Fly.io steps
- Add individual role ID environment variables (WANDERER_ROLE_ID, etc.)
- Add missing env vars: WEBHOOK_SECRET, role mentions, backup folder, portrait URL
- Improve config validation with clear error messages
- Add logging throughout settings initialization

BREAKING CHANGE: Environment variables changed from lowercase to UPPERCASE
(e.g., wanderer_role_id → WANDERER_ROLE_ID). Update .env accordingly.