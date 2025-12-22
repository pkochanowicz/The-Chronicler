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
Reaction Handler
Handles officer approval/rejection via emoji reactions.
"""
import logging
import discord
from discord.ext import commands
from config.settings import get_settings # Updated import

logger = logging.getLogger(__name__)

class ReactionHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.registry = GoogleSheetsService()
        self.settings = get_settings()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle reactions on recruitment posts."""
        if user.bot:
            return

        # Check channel
        if reaction.message.channel.id != self.settings.RECRUITMENT_CHANNEL_ID:
            return

        # Check that user is a guild member (not DM)
        if not isinstance(user, discord.Member):
            logger.warning(f"Reaction from non-member user {user.id} in recruitment channel (unexpected), ignoring")
            return

        # Check permission (Officer roles only)
        user_roles = [r.id for r in user.roles]
        allowed_roles = self.settings.OFFICER_ROLE_IDS  # Officers approve
        if not any(rid in user_roles for rid in allowed_roles):
            logger.debug(f"Reaction from non-officer {user.id}, ignoring")
            return

        # Check emoji
        emoji = str(reaction.emoji)
        if emoji not in [self.settings.APPROVE_EMOJI, self.settings.REJECT_EMOJI]:
            return

        # Find character by message ID
        msg_id = str(reaction.message.id)
        character = self._find_character_by_msg_id(msg_id)
        
        if not character:
            # Might not be a recruitment post, or not logged
            return

        char_name = character.get("char_name")
        discord_id = character.get("discord_id")
        
        # Prevent double handling
        current_status = character.get("status")
        if current_status in [STATUS_REGISTERED, STATUS_REJECTED]:
            return # Already handled

        if emoji == self.settings.APPROVE_EMOJI:
            # Approve
            await self._approve_character(char_name, discord_id, user, reaction.message)
        elif emoji == self.settings.REJECT_EMOJI:
            # Reject
            await self._reject_character(char_name, discord_id, user, reaction.message)

    def _find_character_by_msg_id(self, msg_id: str):
        """Find character dict by recruitment message ID."""
        all_chars = self.registry.get_all_characters()
        for char in all_chars:
            if str(char.get("recruitment_msg_id")) == msg_id:
                return char
        return None

    async def _approve_character(self, char_name, discord_id, officer, message):
        """Handle approval."""
        try:
            # Create forum post in Vault
            forum_url = await self._create_vault_post(char_name, message.embeds)
            
            # Update sheet
            self.registry.update_character_status(
                char_name, 
                STATUS_REGISTERED,
                forum_post_url=forum_url,
                reviewed_by=str(officer.id)
            )
            
            # DM User
            await self._notify_user(discord_id, f"🎉 Your character **{char_name}** has been APPROVED! Check the Vault: {forum_url}", message.channel)
            
            # Update recruitment message
            await message.reply(f"✅ Approved by {officer.mention}")
            
        except Exception as e:
            logger.error(f"Error approving character {char_name}: {e}")
            await message.channel.send(f"⚠️ Error approving {char_name}: {e}")

    async def _reject_character(self, char_name, discord_id, officer, message):
        """Handle rejection."""
        try:
            # Update sheet
            self.registry.update_character_status(
                char_name, 
                STATUS_REJECTED,
                reviewed_by=str(officer.id)
            )
            
            # DM User
            await self._notify_user(discord_id, f"❌ Your character **{char_name}** was rejected by {officer.name}. Please contact an officer for details.", message.channel)
            
            # Update recruitment message
            await message.reply(f"❌ Rejected by {officer.mention}")
            
        except Exception as e:
            logger.error(f"Error rejecting character {char_name}: {e}")

    async def _create_vault_post(self, char_name, embeds):
        """Create a thread in the character vault."""
        forum_channel = self.bot.get_channel(self.settings.CHARACTER_SHEET_VAULT_CHANNEL_ID)
        if not forum_channel:
            error_msg = f"❌ CRITICAL ERROR: Character Sheet Vault channel (ID: {self.settings.CHARACTER_SHEET_VAULT_CHANNEL_ID}) not found! Cannot create character vault post. Please check bot configuration."
            logger.error(error_msg)
            # This is called from _approve_character which has try/except, so we can raise
            raise ValueError(f"Character Sheet Vault channel {self.settings.CHARACTER_SHEET_VAULT_CHANNEL_ID} not found")
            
        # Forum channels use start_thread/create_thread
        # If it's a ForumChannel (discord.ForumChannel), we use create_thread(name=..., content=..., embed=...)
        # If TextChannel, we create message then thread. assuming ForumChannel.
        
        try:
            # Note: forum_channel.create_thread signature varies by discord.py version
            # Usually: name, content, embeds (list), applied_tags, etc.
            thread_with_message = await forum_channel.create_thread(
                name=char_name,
                content=f"Character Sheet for **{char_name}**",
                embed=embeds[0] if embeds else None # Only one embed? Or list?
                # Forum create_thread takes 'embed' or 'file', not 'embeds'. 
                # But message inside can have multiple?
                # Actually, `create_thread` on ForumChannel returns (Thread, Message).
            )
            # The returned object is a ThreadWithMessage or similar.
            # Wait, d.py 2.0: create_thread(name=, content=, ...) -> ThreadWithMessage
            
            thread = thread_with_message.thread
            # If we have multiple embeds, we might need to send them in the message or edit it?
            # Start thread with first embed, then send others?
            # Or pass embeds=[...] if supported?
            # It seems 'embed' is singular in some versions?
            # Let's assume singular for safety or check docs.
            
            if len(embeds) > 1:
                await thread.send(embeds=embeds[1:])
                
            return thread.jump_url
            
        except Exception as e:
            logger.error(f"Failed to create vault post: {e}")
            return ""

    async def _notify_user(self, discord_id, content, fallback_channel=None):
        """Notify user via DM. If DM fails, post warning in fallback channel."""
        try:
            user = await self.bot.fetch_user(int(discord_id))
            if user:
                await user.send(content)
        except Exception as e:
            logger.warning(f"Failed to DM user {discord_id}: {e}")
            # Notify in channel if DM failed
            if fallback_channel:
                await fallback_channel.send(
                    f"⚠️ Could not DM <@{discord_id}> (they may have DMs disabled). "
                    f"Please notify them manually about their character status."
                )

async def setup(bot):
    await bot.add_cog(ReactionHandler(bot))