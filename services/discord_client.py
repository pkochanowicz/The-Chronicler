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
Discord Client Setup
Configures the Discord bot client.
"""

import logging
import discord
from discord.ext import commands
from views.officer_view import OfficerControlView

logger = logging.getLogger(__name__)


def create_bot():
    # Configure intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    intents.guilds = True
    intents.members = True

    # Create bot instance
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Bot logged in as {bot.user.name} (ID: {bot.user.id})")

        # Register persistent views (timeout=None) so they work after bot restarts
        # This allows buttons on old messages to still function
        try:
            # Register OfficerControlView with a dummy character_id
            # The actual character_id is stored in the button's custom_id
            bot.add_view(OfficerControlView(bot, 0))
            logger.info("Registered persistent view: OfficerControlView")
        except Exception as e:
            logger.error(f"Failed to register persistent views: {e}")

        # Sync slash commands
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

    return bot


bot = create_bot()
