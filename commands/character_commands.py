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
Character Commands
User-facing commands for character management.
"""

import discord
from discord import app_commands
from discord.ext import commands
from flows.registration_flow import RegistrationFlow
from config.settings import get_settings


class CharacterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = get_settings()

    @app_commands.command(
        name="register_character",
        description="Begin the journey to register a new character.",
    )
    async def register_character(self, interaction: discord.Interaction):
        """
        Interactive character registration.
        Starts the cinematic 12-step flow.
        Available to all Discord server members.
        """
        # CRITICAL: Defer interaction immediately to prevent token expiration
        # The registration flow is long-running, so we acknowledge within 3 seconds
        await interaction.response.defer(ephemeral=True)

        flow = RegistrationFlow(interaction)
        await flow.start()


async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))
