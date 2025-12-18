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
Officer Commands
Commands for guild officers (Pathfinder/Trailwarden).
"""
import discord
from discord import app_commands
from discord.ext import commands
from flows.burial_flow import BurialFlow
from config.settings import settings

class OfficerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bury", description="[Officer] Perform the Rite of Remembrance for a fallen character.")
    async def bury(self, interaction: discord.Interaction):
        """
        Interactive burial ceremony.
        Only accessible to Pathfinder and Trailwarden roles.
        """
        # Check permissions (Officer)
        user_roles = [r.id for r in interaction.user.roles]
        allowed_roles = settings.OFFICER_ROLE_IDS
        
        if not any(role_id in user_roles for role_id in allowed_roles):
             await interaction.response.send_message(
                 "❌ You are not authorized to perform the Rite of Remembrance.", 
                 ephemeral=True
             )
             return

        flow = BurialFlow(interaction)
        await flow.start()

async def setup(bot):
    await bot.add_cog(OfficerCommands(bot))