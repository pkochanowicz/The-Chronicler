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
Base Interactive Flow
Common logic for multi-step interactive commands.
"""
import asyncio
import discord
from config.settings import settings

class InteractiveFlow:
    """Base class for interactive flows."""
    
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.user = interaction.user
        self.bot = interaction.client
        self.timeout = settings.INTERACTIVE_TIMEOUT_SECONDS
        self.data = {}
        self.message = None # The message we are updating/using for UI

    async def start(self):
        """Start the flow."""
        raise NotImplementedError

    async def send_or_update(self, **kwargs):
        """Send a new message or update existing one."""
        # If we have a message, try to edit it. If that fails or we don't have one, send new.
        # But for "chatty" flow, we might want new messages.
        # The blueprint shows a conversation.
        # "Bot: ... [User types] ... Bot: ..."
        # So we should send NEW messages for each step narration.
        # But for UI components (Dropdowns), we might attach them to the bot message.
        
        # We generally use followup.send for the first message (since interaction is deferred or initially responded).
        if not self.interaction.response.is_done():
            await self.interaction.response.send_message(**kwargs)
            self.message = await self.interaction.original_response()
        else:
            self.message = await self.interaction.followup.send(**kwargs, wait=True)
        return self.message

    async def wait_for_message(self, timeout=None):
        """Wait for a text message from the user."""
        def check(m):
            return m.author.id == self.user.id and m.channel.id == self.interaction.channel_id
        
        return await self.bot.wait_for('message', check=check, timeout=timeout or self.timeout)

    async def wait_for_component(self, component_type=None, timeout=None):
        """Wait for a component interaction (button/select)."""
        def check(i):
            is_user = i.user.id == self.user.id
            is_msg = i.message.id == self.message.id
            return is_user and is_msg
        
        return await self.bot.wait_for('interaction', check=check, timeout=timeout or self.timeout)
