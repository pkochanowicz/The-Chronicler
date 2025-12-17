# Azeroth Bound Bot - Deployment Guide

**Version:** 2.0.0 (Schema Reformation)
**Architecture:** Path B (Webhook-Driven)
**Hosting Options:** Fly.io (recommended) | Render.com (alternative)
**Monthly Cost:** $0.00 (free tier)

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

- ✅ Python 3.10+ bot code ready
- ✅ Google Cloud service account credentials (`credentials.json`)
- ✅ Discord bot token and channel IDs
- ✅ Google Sheets with 27-column schema created
- ✅ `.env` file configured locally and tested
- ✅ Git repository (GitHub, GitLab, or Bitbucket)

---

## Deployment Options

### Fly.io (Recommended)

**Pros:**
- ✅ Free tier: 3 VMs with 256MB RAM each
- ✅ Easy to deploy (flyctl CLI)
- ✅ Built-in health checks
- ✅ Automatic HTTPS
- ✅ Fast global CDN
- ✅ Excellent Python support

**Cons:**
- ❌ Requires credit card (for verification, not charged)
- ❌ Slightly more complex initial setup

**Best for:** Production deployment with high availability

---

### Render.com

**Pros:**
- ✅ Free tier: 750 hours/month
- ✅ No credit card required
- ✅ Web dashboard (easier for beginners)
- ✅ Auto-deploy from Git
- ✅ Built-in logging

**Cons:**
- ❌ Spins down after 15 min of inactivity
- ❌ Slower cold starts (30-60 seconds)
- ❌ Only 1 free service

**Best for:** Testing or low-traffic guilds

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
flyctl auth signup
# OR, if you already have an account:
flyctl auth login
```

**Add payment method:**
- Go to https://fly.io/dashboard/personal/billing
- Add credit card (required for verification, won't be charged on free tier)

---

### Step 3: Prepare Your Repository

**Create `fly.toml` in project root:**

```toml
app = "azeroth-bound-bot"

[build]
  builder = "paketobuildpacks/builder:base"
  buildpacks = ["gcr.io/paketo-buildpacks/python"]

[env]
  PORT = "8080"
  PYTHON_VERSION = "3.10"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20

  [[services.tcp_checks]]
    grace_period = "30s"
    interval = "15s"
    restart_limit = 0
    timeout = "10s"
```

**Create `Procfile` in project root:**

```
web: python main.py
```

**Update `main.py` to include webhook endpoint:**

Ensure your bot serves an HTTP endpoint for webhooks:

```python
from aiohttp import web

async def webhook_handler(request):
    """Handle incoming webhooks from Google Apps Script"""
    # ... (see TECHNICAL.md for full implementation)
    pass

async def start_web_server():
    """Start webhook web server"""
    app = web.Application()
    app.router.add_post('/webhook', webhook_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
    await site.start()

# In your main() function:
bot.loop.create_task(start_web_server())
```

---

### Step 4: Deploy to Fly.io

**Initialize Fly app:**

```bash
flyctl launch
```

**Answer prompts:**
- App name: `azeroth-bound-bot` (or your choice)
- Region: Choose closest to you
- Database: No
- Deploy now: No (we'll set secrets first)

---

### Step 5: Set Environment Secrets

**Set all `.env` variables as Fly secrets:**

```bash
flyctl secrets set DISCORD_BOT_TOKEN="your_discord_bot_token_here"
flyctl secrets set GUILD_ID="your_guild_id_here"
flyctl secrets set RECRUITMENT_CHANNEL_ID="channel_id"
flyctl secrets set FORUM_CHANNEL_ID="forum_id"
flyctl secrets set CEMETERY_CHANNEL_ID="cemetery_id"
flyctl secrets set GUILD_MEMBER_ROLE_IDS="role1,role2,role3,role4"
flyctl secrets set LIFECYCLE_ROLE_IDS="role1,role2"
flyctl secrets set GOOGLE_SHEET_ID="your_sheet_id"
flyctl secrets set WEBHOOK_SECRET="your_random_32_char_secret"
flyctl secrets set DEFAULT_PORTRAIT_URL="https://i.imgur.com/placeholder.png"
flyctl secrets set INTERACTIVE_TIMEOUT_SECONDS="300"
```

**Upload Google credentials:**

Fly doesn't support file uploads directly, so encode `credentials.json` as base64:

```bash
# Encode credentials
cat credentials.json | base64 > credentials_b64.txt

# Set as secret
flyctl secrets set GOOGLE_CREDENTIALS_B64="$(cat credentials_b64.txt)"
```

**Update code to decode credentials:**

In `config/settings.py`:

```python
import os
import base64
import json

# Decode credentials from base64
creds_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
if creds_b64:
    creds_json = base64.b64decode(creds_b64).decode('utf-8')
    creds = json.loads(creds_json)
    # Write to temp file for gspread
    with open('/tmp/credentials.json', 'w') as f:
        json.dump(creds, f)
    GOOGLE_CREDENTIALS_FILE = '/tmp/credentials.json'
else:
    GOOGLE_CREDENTIALS_FILE = 'credentials.json'
```

---

### Step 6: Deploy!

```bash
flyctl deploy
```

**Watch deployment:**

```bash
flyctl logs
```

**Check status:**

```bash
flyctl status
```

**Your bot's webhook URL:**
```
https://azeroth-bound-bot.fly.dev/webhook
```

---

### Step 7: Update Google Apps Script

In your Google Apps Script `webhook.gs`, set:

```javascript
const WEBHOOK_URL = "https://azeroth-bound-bot.fly.dev/webhook";
const WEBHOOK_SECRET = "your_random_32_char_secret"; // Must match Fly secret
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

---

### Step 3: Configure Service

**Name:** `azeroth-bound-bot`

**Environment:** `Python 3`

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

Click **"Environment"** tab, add ALL variables from `.env`:

```
DISCORD_BOT_TOKEN = your_discord_bot_token_here
GUILD_ID = your_guild_id_here
RECRUITMENT_CHANNEL_ID = channel_id
FORUM_CHANNEL_ID = forum_id
CEMETERY_CHANNEL_ID = cemetery_id
GUILD_MEMBER_ROLE_IDS = role1,role2,role3,role4
LIFECYCLE_ROLE_IDS = role1,role2
GOOGLE_SHEET_ID = your_sheet_id
WEBHOOK_SECRET = your_random_32_char_secret
DEFAULT_PORTRAIT_URL = https://i.imgur.com/placeholder.png
INTERACTIVE_TIMEOUT_SECONDS = 300
PORT = 10000
```

**Add Google credentials as base64:**

```bash
# Encode locally
cat credentials.json | base64 > credentials_b64.txt
```

Then add to Render environment:

```
GOOGLE_CREDENTIALS_B64 = <paste base64 string>
```

**Update code** (same as Fly.io Step 5)

---

### Step 5: Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repo
2. Run build command
3. Start the bot

**Your webhook URL:**
```
https://azeroth-bound-bot.onrender.com/webhook
```

---

### Step 6: Keep Bot Awake (Prevent Spin-Down)

Render free tier spins down after 15 min of inactivity. To prevent this:

**Option 1: Use UptimeRobot**
1. Sign up at https://uptimerobot.com (free)
2. Add monitor: `https://azeroth-bound-bot.onrender.com/health`
3. Interval: 5 minutes

**Option 2: Add a health check endpoint**

In `main.py`:

```python
async def health_handler(request):
    return web.Response(text="OK")

app.router.add_get('/health', health_handler)
```

---

## Post-Deployment Setup

### 1. Verify Bot is Online

Check Discord - bot should show as online with green status.

### 2. Test Slash Commands

```
/register_character
```

If command appears, bot is running correctly!

### 3. Test Webhook

In Google Apps Script:

```javascript
function testWebhook() {
  var payload = {
    "secret": "your_webhook_secret",
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
  Logger.log(response.getContentText());
}
```

Run `testWebhook()` - should return `200 OK`.

### 4. Configure Google Apps Script Triggers

See [GOOGLE_APPS_SCRIPT_SETUP.md](./GOOGLE_APPS_SCRIPT_SETUP.md)

### 5. Create Test Character

Use `/register_character` and complete the flow.

Check:
- ✅ Character written to Google Sheets
- ✅ Webhook fired
- ✅ Posted to #recruitment
- ✅ Received DM confirmation

---

## Verification Checklist

### Bot Deployment

- [ ] Bot shows online in Discord
- [ ] Slash commands appear and work
- [ ] Bot can send messages in configured channels
- [ ] Bot has correct permissions (Manage Threads, Send Messages, etc.)

### Webhook System

- [ ] Webhook URL accessible (test with curl or browser)
- [ ] Webhook secret validation working
- [ ] Google Apps Script can POST to webhook successfully
- [ ] Webhooks fire on sheet changes

### Interactive Flows

- [ ] `/register_character` starts 12-step flow
- [ ] All steps validate input correctly
- [ ] Embed preview displays correctly
- [ ] Final inscription writes to sheets

### Data Flow

- [ ] Character data writes to Google Sheets (27 columns)
- [ ] `confirmation=TRUE` + `status=PENDING` triggers recruitment post
- [ ] Officer approval (✅) creates forum post
- [ ] Officer rejection (❌) sends DM to user

### Lifecycle Management

- [ ] `/bury` starts interactive ceremony (officer only)
- [ ] Setting `status=DECEASED` triggers burial webhook
- [ ] Cemetery thread created with ceremonial formatting
- [ ] Character owner receives DM notification

---

## Troubleshooting

### Bot Won't Start

**Check logs:**

**Fly.io:**
```bash
flyctl logs
```

**Render.com:**
- Go to dashboard → Logs tab

**Common errors:**

1. **Missing environment variables**
   - Verify all secrets set with `flyctl secrets list` or Render dashboard

2. **Google credentials invalid**
   - Re-encode `credentials.json` and update secret
   - Verify service account has access to sheets

3. **Discord token invalid**
   - Regenerate token in Discord Developer Portal
   - Update `DISCORD_BOT_TOKEN` secret

---

### Webhooks Not Working

**Test webhook endpoint manually:**

```bash
curl -X POST https://azeroth-bound-bot.fly.dev/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_webhook_secret",
    "trigger": "TEST",
    "character": {},
    "timestamp": "2025-12-16T10:30:00Z"
  }'
```

**Expected response:** `200 OK`

**If 400 Bad Request:**
- Check secret matches between Apps Script and bot
- Verify JSON payload structure

**If 404 Not Found:**
- Webhook endpoint not registered
- Check `main.py` has `app.router.add_post('/webhook', webhook_handler)`

---

### Render.com Bot Spinning Down

**Symptoms:**
- Bot offline every 15+ minutes
- Slash commands disappear

**Solution:**
- Set up UptimeRobot (see Step 6)
- Ping `/health` endpoint every 5 minutes

---

### High Memory Usage

**Fly.io free tier:** 256MB per VM

If bot crashes due to memory:

1. **Optimize code:**
   - Clear old interaction data
   - Limit embed cache
   - Use generators for large lists

2. **Upgrade to paid plan:**
   - $1.94/month for 512MB VM

---

### Google Sheets API Rate Limits

**Free tier limits:**
- 100 requests per 100 seconds per user
- 500 requests per 100 seconds per project

**If exceeded:**
- Bot will raise `APIError`
- Wait 100 seconds and retry

**Prevention:**
- Batch writes when possible
- Cache sheet data locally (refresh every 5 min)

---

## Scaling Beyond Free Tier

### When to upgrade:

- Guild has 100+ active members
- 50+ character registrations per day
- Need 99.9% uptime SLA

### Recommended upgrades:

**Fly.io:**
- $1.94/month: 512MB VM
- $3.88/month: 1GB VM

**Render.com:**
- $7/month: Starter plan (no spin-down)
- $15/month: Standard plan (faster, more reliable)

---

## Support

**Issues with deployment?**

1. Check bot logs for errors
2. Verify all environment variables set correctly
3. Test webhook endpoint manually
4. Review [TECHNICAL.md](./TECHNICAL.md) for architecture details
5. Ask in guild's tech support channel

---

**For Azeroth Bound! For Deployment! For Zero Downtime!** ⚔️

*Last updated: December 16, 2025*
*Version: 2.0.0*
*Status: Production Ready*
