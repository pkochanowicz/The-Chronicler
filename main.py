# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Azeroth Bound Bot - Entry Point
Main entry point for the Discord bot.
"""
import asyncio
import logging
from config.settings import settings
from services.discord_client import bot
from services.sheets_service import google_sheets_service
from mcp.server import run_mcp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

async def setup_hook():
    """Load extensions on startup."""
    extensions = [
        "commands.character_commands",
        "commands.officer_commands",
        "commands.bank_commands",
        "commands.talent_commands",
        "handlers.reaction_handler"
    ]
    
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logger.info(f"Loaded extension: {ext}")
        except Exception as e:
            logger.error(f"Failed to load extension {ext}: {e}")

def main():
    """Main entry point."""
    try:
        # Set setup_hook
        bot.setup_hook = setup_hook

        # Use global sheets_service
        # sheets_service = CharacterRegistryService() # Removed

        async def run_mcp():
            try:
                await run_mcp_server(bot, google_sheets_service) # Pass global service
            except Exception as e:
                logger.error(f"Failed to start MCP server: {e}")

        async def run_webhook():
            try:
                await start_webhook_server(bot)
            except Exception as e:
                logger.error(f"Failed to start webhook server: {e}")

        # Inject webhook and mcp tasks into setup_hook
        original_setup_hook = bot.setup_hook
        async def combined_setup_hook():
            if original_setup_hook:
                await original_setup_hook()
            bot.loop.create_task(run_webhook())
            bot.loop.create_task(run_mcp())
        
        bot.setup_hook = combined_setup_hook

        # Run the bot
        logger.info("Starting Azeroth Bound Bot...")
        bot.run(settings.DISCORD_BOT_TOKEN)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()