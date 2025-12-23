# handlers/reaction_handler.py
import logging
import discord
from discord.ext import commands
from config.settings import get_settings
from views.officer_view import OfficerControlView

logger = logging.getLogger(__name__)

class ReactionHandler(commands.Cog):
    """
    DEPRECATED: Reaction-based logic is deprecated in v2.0+ favor of Buttons (OfficerControlView).
    This handler is kept only for legacy thread monitoring if absolutely needed, 
    but for now we effectively disable its core logic to enforce the new flows.
    """
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        pass # Disabled for v2.0

async def setup(bot):
    await bot.add_cog(ReactionHandler(bot))
