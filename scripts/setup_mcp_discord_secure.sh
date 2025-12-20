  /home/pfunc/data/Kody/the_chronicler/scripts/setup_mcp_discord_secure.sh
   > /dev/null << 'EOF'
  #!/bin/bash
  # Secure MCP Discord Setup Script
  # Loads tokens from .env without exposing them
  # Supports: DISCORD_BOT_TOKEN, GUILD_ID, and optional
  DISCORD_APPLICATION_ID

  set -e

  # Colors
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  RED='\033[0;31m'
  NC='\033[0m'

  echo -e "${YELLOW}🔒 Secure MCP Discord Setup${NC}"
  echo ""

  # Navigate to project root
  cd "$(dirname "$0")/.." || exit 1

  # Check .env exists
  if [ ! -f .env ]; then
      echo -e "${RED}❌ Error: .env file not found!${NC}"
      exit 1
  fi

  # Load .env (securely)
  set -a
  source .env > /dev/null 2>&1
  set +a

  # Verify required tokens
  if [ -z "$DISCORD_BOT_TOKEN" ]; then
      echo -e "${RED}❌ DISCORD_BOT_TOKEN not found in .env${NC}"
      exit 1
  fi

  echo -e "${GREEN}✅ DISCORD_BOT_TOKEN loaded${NC}"

  # Check optional tokens
  if [ -n "$GUILD_ID" ]; then
      echo -e "${GREEN}✅ GUILD_ID loaded${NC}"
  fi

  if [ -n "$DISCORD_APPLICATION_ID" ]; then
      echo -e "${GREEN}✅ DISCORD_APPLICATION_ID loaded${NC}"
  else
      echo -e "${YELLOW}ℹ️  DISCORD_APPLICATION_ID not set
  (optional)${NC}"
  fi

  # Stop existing container
  if docker ps -a --format '{{.Names}}' | grep -q "^mcp-discord$"; then
      echo "🛑 Stopping existing mcp-discord container..."
      docker stop mcp-discord > /dev/null 2>&1 || true
      docker rm mcp-discord > /dev/null 2>&1 || true
  fi

  # Build docker run command
  DOCKER_CMD="docker run -d \
      --name mcp-discord \
      --restart unless-stopped \
      -p 8080:8080 \
      -e DISCORD_BOT_TOKEN=\"$DISCORD_BOT_TOKEN\""

  # Add optional env vars if present
  if [ -n "$GUILD_ID" ]; then
      DOCKER_CMD="$DOCKER_CMD -e DISCORD_GUILD_ID=\"$GUILD_ID\""
  fi

  if [ -n "$DISCORD_APPLICATION_ID" ]; then
      DOCKER_CMD="$DOCKER_CMD -e
  DISCORD_APPLICATION_ID=\"$DISCORD_APPLICATION_ID\""
  fi

  DOCKER_CMD="$DOCKER_CMD mcp/mcp-discord"

  # Start container
  echo "🚀 Starting mcp-discord container..."
  eval $DOCKER_CMD > /dev/null 2>&1

  if [ $? -eq 0 ]; then
      echo -e "${GREEN}✅ MCP Discord started successfully!${NC}"
      echo ""
      echo "Container will auto-restart on reboot."
      echo ""
      sleep 2
      docker ps --filter "name=mcp-discord" --format "table
  {{.Names}}\t{{.Status}}\t{{.Ports}}"
      echo ""
      echo "Commands:"
      echo "  - View logs: docker logs mcp-discord"
      echo "  - Stop: docker stop mcp-discord"
      echo "  - Restart: docker restart mcp-discord"
  else
      echo -e "${RED}❌ Failed to start container${NC}"
      exit 1
  fi
