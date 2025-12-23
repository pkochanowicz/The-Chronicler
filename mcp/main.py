import asyncio
import logging
from dotenv import load_dotenv
from config.settings import settings
# from services.sheets_service import google_sheets_service # Temporarily commented out
from mcp.server import run_mcp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file for standalone mode
load_dotenv()

class MockDiscordClient:
    """
    A mock Discord client for running the MCP server in standalone mode
    (e.g. for CLI integration or local testing without a bot connection).
    """
    def __init__(self):
        self.guilds = []
        self.user = type('obj', (object,), {'name': 'MockBot', 'id': 12345})

    def get_channel(self, channel_id):
        logger.warning(f"MockDiscordClient: get_channel({channel_id}) called. Returning None.")
        return None

    def get_guild(self, guild_id):
        logger.warning(f"MockDiscordClient: get_guild({guild_id}) called. Returning None.")
        return None

async def main():
    """Run the MCP server standalone."""
    logger.info("Starting MCP Server in standalone mode...")
    
    # Initialize mock client
    mock_client = MockDiscordClient()
    
    # Run server
    # Note: run_mcp_server starts the site but doesn't block forever if it just awaits site.start().
    # We need to keep the loop alive.
    
    # However, mcp.server.run_mcp_server does:
    # app = create_mcp_app(...)
    # runner = web.AppRunner(app)
    # await runner.setup()
    # site = web.TCPSite(runner, ...)
    # await site.start()
    
    # So we need to sleep forever.
    await run_mcp_server(mock_client, None)
    
    # Keep alive
    logger.info("MCP Server is running. Press Ctrl+C to stop.")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopping MCP Server...")
