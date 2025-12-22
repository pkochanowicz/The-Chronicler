# Deploy secrets from .env to Fly.io
# Improved version with batching

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
