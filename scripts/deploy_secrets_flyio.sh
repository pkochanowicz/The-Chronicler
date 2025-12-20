#!/bin/bash
# Deploy secrets from .env to Fly.io
# Batched version for speed and reliability

set -e  # Exit on error

APP_NAME="the-chronicler"

echo "🔐 Deploying secrets from .env to Fly.io app: $APP_NAME"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found in current directory"
    exit 1
fi

# Check if flyctl is available
if ! command -v flyctl &> /dev/null; then
    echo "❌ Error: flyctl not found!"
    exit 1
fi

# Check authentication
if ! flyctl auth whoami &> /dev/null 2>&1; then
    echo "❌ Error: Not authenticated. Run: flyctl auth login"
    exit 1
fi

echo "✓ Prerequisites verified"
echo ""

# Handle GOOGLE_CREDENTIALS_B64 encoding
GOOGLE_CREDS_B64=""
if [ -f credentials.json ]; then
    echo "📋 Found credentials.json - encoding to base64..."
    GOOGLE_CREDS_B64=$(cat credentials.json | base64 | tr -d '\n')
    echo "✓ Encoded: ${#GOOGLE_CREDS_B64} characters"
    echo ""
else
    echo "⚠️  credentials.json not found - will use value from .env if present"
    echo ""
fi

# Collect secrets into an array (for batching)
declare -a SECRETS_ARRAY=()

echo "🔄 Reading secrets from .env..."

while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [[ -z "$key" || "$key" =~ ^#.* ]] && continue

    # Trim whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Remove surrounding quotes
    value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")

    # Skip placeholder/empty values
    [[ -z "$value" ]] && continue
    [[ "$value" == "your_"* ]] && continue
    [[ "$value" == "generate_"* ]] && continue
    [[ "$value" == "0" ]] && [[ "$key" =~ _ROLE_ID$ ]] && continue

    # Use encoded Google credentials if available
    if [ "$key" == "GOOGLE_CREDENTIALS_B64" ] && [ -n "$GOOGLE_CREDS_B64" ]; then
        value="$GOOGLE_CREDS_B64"
    fi

    # Add to array
    SECRETS_ARRAY+=("$key=$value")
    echo "  ✓ Queued: $key"
done < .env

echo ""
echo "📦 Collected ${#SECRETS_ARRAY[@]} secrets"
echo ""

# Deploy all secrets in ONE batched command
if [ ${#SECRETS_ARRAY[@]} -gt 0 ]; then
    echo "🚀 Deploying all secrets to Fly.io (batched for speed)..."
    echo ""

    # Set all secrets at once - much faster and more reliable
    flyctl secrets set "${SECRETS_ARRAY[@]}" --app "$APP_NAME" --stage

    echo ""
    echo "✅ All secrets staged successfully!"
    echo ""
    echo "📝 Note: Secrets are STAGED and will be applied on first deployment"
    echo "   Run: flyctl deploy"
else
    echo "⚠️  No valid secrets found to deploy"
    exit 1
fi

echo ""
echo "🔍 Verify secrets with:"
echo "   flyctl secrets list --app $APP_NAME"
echo ""
