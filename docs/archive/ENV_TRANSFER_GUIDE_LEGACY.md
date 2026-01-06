# .env Transfer Guide for Fly.io

## Overview
You need to transfer your local .env variables to Fly.io as secrets before deployment.

**IMPORTANT SECURITY NOTE**: The script and this process will NOT read your actual .env values in a way that exposes them to me or logs them. The transfer happens directly from your local .env to Fly.io's secure storage.

---

## Quick Method (Recommended)

### Step 1: Verify Prerequisites

```bash
# Make sure you're in the project root
cd /home/pfunc/data/Kody/the_chronicler

# Check that .env exists and has real values (not placeholders)
grep -v "^#" .env | grep -v "your_" | grep -v "generate_" | grep -v "^$" | head -5

# Check that credentials.json exists
ls -lh credentials.json
```

### Step 2: Run the Deployment Script

**IMPORTANT**: Before running, update the script to fix a bug:

The current `scripts/deploy_secrets_flyio.sh` has an escaped `$` on line 20 that will cause issues:
```bash
value=\$(echo "$value" ...)  # ❌ Wrong - backslash before $
```

It should be:
```bash
value=$(echo "$value" ...)   # ✅ Correct - no backslash
```

**Improved version of the script** (copy this to `scripts/deploy_secrets_flyio.sh`):

```bash
#!/bin/bash
# Deploy secrets from .env to Fly.io
# Improved version with batching and auto-encoding of Google credentials

set -e  # Exit on error

APP_NAME="the-chronicler"

echo "🔐 Deploying secrets from .env to Fly.io app: $APP_NAME"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found in current directory"
    exit 1
fi

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Error: flyctl not found!"
    echo "   Install from: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Check if authenticated
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Error: Not authenticated with Fly.io"
    echo "   Run: flyctl auth login"
    exit 1
fi

echo "✓ .env file found"
echo "✓ flyctl installed and authenticated"
echo ""

# Handle GOOGLE_CREDENTIALS_B64 specially
if [ -f credentials.json ]; then
    echo "📋 Found credentials.json - encoding to base64..."
    GOOGLE_CREDS_B64=$(cat credentials.json | base64 | tr -d '\n')
    echo "✓ Google credentials encoded (${#GOOGLE_CREDS_B64} chars)"
else
    echo "⚠️  Warning: credentials.json not found"
    echo "   Make sure GOOGLE_CREDENTIALS_B64 is already set in .env"
    GOOGLE_CREDS_B64=""
fi
echo ""

# Collect all secrets (batch approach for speed)
declare -a SECRETS=()

echo "🔄 Reading .env file..."
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [[ -z "$key" || "$key" =~ ^#.* ]] && continue

    # Trim whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Remove surrounding quotes
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")

    # Skip placeholder values
    [[ "$value" == "your_"* ]] && continue
    [[ "$value" == "generate_"* ]] && continue
    [[ -z "$value" ]] && continue

    # Skip 0 values for role IDs (placeholders)
    [[ "$value" == "0" ]] && [[ "$key" =~ _ROLE_ID$ ]] && continue

    # Use encoded credentials for GOOGLE_CREDENTIALS_B64
    if [ "$key" == "GOOGLE_CREDENTIALS_B64" ] && [ ! -z "$GOOGLE_CREDS_B64" ]; then
        value="$GOOGLE_CREDS_B64"
    fi

    # Add to secrets array
    SECRETS+=("$key=$value")
    echo "  ✓ Queued: $key"
done < .env

echo ""
echo "🚀 Deploying ${#SECRETS[@]} secrets to Fly.io (batched)..."
echo ""

# Deploy all secrets at once (much faster than one-by-one)
if [ ${#SECRETS[@]} -gt 0 ]; then
    flyctl secrets set "${SECRETS[@]}" --app "$APP_NAME"
    echo ""
    echo "✅ All secrets deployed successfully!"
else
    echo "⚠️  No secrets found to deploy"
fi

echo ""
echo "📝 Next steps:"
echo "   1. Verify: flyctl secrets list --app $APP_NAME"
echo "   2. Deploy: flyctl deploy"
echo ""
```

### Step 3: Make Executable and Run

```bash
chmod +x scripts/deploy_secrets_flyio.sh
./scripts/deploy_secrets_flyio.sh
```

---

## What the Script Does

1. ✅ **Validates environment**: Checks for .env, flyctl, and authentication
2. ✅ **Auto-encodes Google credentials**: Finds `credentials.json` and converts to base64 automatically
3. ✅ **Filters placeholders**: Skips `your_*`, `generate_*`, empty values, and `0` role IDs
4. ✅ **Batches uploads**: Sends all secrets in one command (much faster than one-by-one)
5. ✅ **Secure transfer**: Secrets go directly to Fly.io, not logged or exposed

---

## Improvements Made to Your Original Script

| Feature | Original | Improved |
|---------|----------|----------|
| **Speed** | One secret at a time (slow) | Batched (fast) |
| **Google Creds** | Manual encoding required | Automatic encoding |
| **Validation** | Basic | Checks flyctl, auth, .env |
| **Placeholder Handling** | None | Skips test values |
| **Error Handling** | Basic | Comprehensive checks |
| **Bug Fix** | Escaped `\$` on line 20 | Fixed to `$` |

---

## Verification After Running

```bash
# List all secrets (names only, values are hidden)
flyctl secrets list --app the-chronicler

# Expected output should include:
# - DISCORD_BOT_TOKEN
# - GUILD_ID
# - RECRUITMENT_CHANNEL_ID
# - FORUM_CHANNEL_ID
# - CEMETERY_CHANNEL_ID
# - All role IDs
# - GOOGLE_SHEET_ID
# - GOOGLE_CREDENTIALS_B64 (this is the important one!)
# - WEBHOOK_SECRET
# - etc.
```

---

## Special Note: GOOGLE_CREDENTIALS_B64

The improved script **automatically handles** encoding `credentials.json` to base64 and setting it as `GOOGLE_CREDENTIALS_B64`.

**How it works:**
1. Script finds `credentials.json` in project root
2. Encodes to base64 with no newlines: `cat credentials.json | base64 | tr -d '\n'`
3. Sets as Fly.io secret
4. At runtime, the bot's `config/settings.py` decodes it back to `/tmp/credentials.json`

**Verify it's set correctly:**
```bash
# Check the secret exists (won't show value)
flyctl secrets list --app the-chronicler | grep GOOGLE_CREDENTIALS_B64
```

---

## Troubleshooting

### Error: "flyctl: command not found"
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Add to PATH (add to ~/.bashrc)
export PATH="$HOME/.fly/bin:$PATH"
```

### Error: "Not authenticated with Fly.io"
```bash
flyctl auth login
```

### Error: "App 'the-chronicler' not found"
```bash
# Initialize the app first
flyctl launch --no-deploy
```

### Secrets not taking effect
```bash
# Secrets require redeployment to take effect
flyctl deploy
```

---

## Next Steps After Secrets Are Set

1. **Verify secrets**: `flyctl secrets list --app the-chronicler`
2. **Deploy the app**: `flyctl deploy`
3. **Watch logs**: `flyctl logs --app the-chronicler`
4. **Check health**: `curl https://the-chronicler.fly.dev/health` (should return "OK")


---

## Security Best Practices

✅ **DO:**
- Keep `.env` in `.gitignore` (already done)
- Keep `credentials.json` in `.gitignore` (already done)
- Rotate `WEBHOOK_SECRET` every 90 days
- Use Fly.io secrets for all sensitive data

❌ **DON'T:**
- Commit `.env` to git
- Share `credentials.json` publicly
- Use the same `WEBHOOK_SECRET` across multiple deployments
- Store secrets in code comments or documentation

---

**Ready to deploy! 🚀**

Once secrets are set and verified, proceed with:
```bash
flyctl deploy
```
