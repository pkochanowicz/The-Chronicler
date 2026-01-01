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
Main entry point for the Discord bot with FastAPI integration.
"""
import asyncio
import os
import logging
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Configure logging first to capture everything
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Initializing application module...")

try:
    from db.database import init_db
    from services.discord_client import bot
    from config.settings import get_settings
    from routers import characters, webhooks, health
except Exception as e:
    logger.critical(f"Failed to import dependencies: {e}", exc_info=True)
    raise


async def load_extensions():
    """Load Discord bot extensions (cogs)."""
    extensions = [
        "commands.character_commands",
        "commands.officer_commands",
        "commands.bank_commands",
        "commands.talent_commands",
        "handlers.reaction_handler",
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            logger.info(f"Loaded extension: {ext}")
        except Exception as e:
            logger.error(f"Failed to load extension {ext}: {e}", exc_info=True)


async def start_discord_bot():
    """Start the Discord bot in the background."""
    settings = get_settings()
    try:
        async with bot:
            await load_extensions()
            logger.info("Starting Discord bot...")
            await bot.start(settings.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.critical(f"Discord bot task failed: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    try:
        logger.info("Initializing database...")
        await init_db()

        # Start Discord bot task (fire-and-forget)
        logger.info("Initializing Discord bot task...")
        asyncio.create_task(start_discord_bot())

        yield

        # Shutdown event
        logger.info("Shutting down...")
    except Exception as e:
        logger.critical(f"Lifespan error: {e}", exc_info=True)


app = FastAPI(title="The Chronicler", lifespan=lifespan)

# Include routers
try:
    app.include_router(characters.router, prefix="/characters", tags=["characters"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(health.router, prefix="/health", tags=["health"])
except Exception as e:
    logger.error(f"Failed to include routers: {e}", exc_info=True)


@app.get("/")
async def read_root():
    return {"message": "The Chronicler is Online."}


if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Uvicorn on port {port}...")
    try:
        # Run Uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)  # nosec B104
    except Exception as e:
        logger.critical(f"Uvicorn failed: {e}", exc_info=True)
