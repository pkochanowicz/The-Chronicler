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
Interactive Burial Flow
The ceremonial process for burying a character.
"""
import logging
import asyncio
import discord
from discord.ui import View, Button, Select, Modal, TextInput
from flows.base_flow import InteractiveFlow
from services.sheets_service import GoogleSheetsService
from utils.embed_parser import build_character_embeds, parse_embed_json
from domain.models import Character, STATUS_DECEASED

logger = logging.getLogger(__name__)

class BurialFlow(InteractiveFlow):
    """
    Handles the character burial ceremony.
    """

    async def start(self):
        """Start the burial rite."""
        try:
            # Step 1: Introduction
            await self.step_introduction()
            if not self.data.get("proceed"):
                return

            # Step 2: Search
            await self.step_search()
            if not self.data.get("character_found"):
                return

            # Step 3: Verification
            await self.step_verification()
            if not self.data.get("verified"):
                return

            # Step 4: Death Cause
            await self.step_death_cause()

            # Step 5: Eulogy
            await self.step_eulogy()

            # Step 6: Confirmation
            await self.step_confirmation()
            
            # Execute if confirmed
            if self.data.get("confirmed"):
                await self.execute_burial()

        except asyncio.TimeoutError:
            await self.handle_timeout()
        except Exception as e:
            logger.error(f"Error in burial flow: {e}")
            await self.interaction.followup.send("❌ The rite was interrupted by a disturbance.", ephemeral=True)

    async def step_introduction(self):
        """Step 1: Introduction."""
        embed = discord.Embed(
            title="⚰️ The Rite of Remembrance",
            description=(
                "*The chronicler's expression grows somber. He reaches for a black-bound tome adorned with silver runes.*\n\n"
                "Officer... you invoke the Rite of Remembrance.\n"
                "This is a sacred duty—to record the fall of a hero and ensure their deeds are never forgotten.\n\n"
                "**Shall we begin?**"
            ),
            color=0x4A4A4A # Dark Gray
        )
        
        view = View()
        yes_btn = Button(label="Begin Rite", style=discord.ButtonStyle.primary, emoji="⚰️")
        cancel_btn = Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        async def yes_callback(interaction):
            self.data["proceed"] = True
            await interaction.response.defer()
            view.stop()
            
        async def cancel_callback(interaction):
            self.data["proceed"] = False
            await interaction.response.send_message("The rite is postponed.", ephemeral=True)
            view.stop()
            
        yes_btn.callback = yes_callback
        cancel_btn.callback = cancel_callback
        view.add_item(yes_btn)
        view.add_item(cancel_btn)
        
        await self.send_or_update(embed=embed, view=view)
        await view.wait()

    async def step_search(self):
        """Step 2: Search Character."""
        await self.interaction.followup.send(
            "🔍 **THE FALLEN HERO**\n\n"
            "Which hero has fallen?\n"
            "*(Type the character's exact name)*"
        )
        
        msg = await self.wait_for_message()
        search_name = msg.content.strip()
        
        registry = GoogleSheetsService()
        char_data = registry.get_character_by_name(search_name)
        
        if not char_data:
            await self.interaction.followup.send(f"❌ Could not find a record for '{search_name}'.")
            self.data["character_found"] = False
            return
            
        self.data["character_found"] = True
        self.data["character_data"] = char_data
        
        await self.interaction.followup.send("*The pages flip on their own, revealing a record...*")

    async def step_verification(self):
        """Step 3: Verify Character."""
        char_data = self.data["character_data"]
        
        # Parse existing embeds to show preview
        embed_json = char_data.get("embed_json", "[]")
        try:
            embeds = parse_embed_json(embed_json)
            preview_embed = embeds[0] if embeds else None
        except:
            preview_embed = None
            
        content = (
            f"**{char_data.get('char_name')}**\n"
            f"Race: {char_data.get('race')} • Class: {char_data.get('class')}\n"
            f"Status: {char_data.get('status')}\n\n"
            "**Is this the fallen hero?**"
        )
        
        view = View()
        yes_btn = Button(label="Yes, this is correct", style=discord.ButtonStyle.green, emoji="✅")
        no_btn = Button(label="No, search again", style=discord.ButtonStyle.secondary)
        
        async def yes_callback(interaction):
            self.data["verified"] = True
            await interaction.response.defer()
            view.stop()
            
        async def no_callback(interaction):
            self.data["verified"] = False
            await interaction.response.send_message("Search cancelled.", ephemeral=True)
            view.stop()
            
        yes_btn.callback = yes_callback
        no_btn.callback = no_callback
        view.add_item(yes_btn)
        view.add_item(no_btn)
        
        await self.interaction.followup.send(content=content, embed=preview_embed, view=view)
        await view.wait()

    async def step_death_cause(self):
        """Step 4: Death Cause."""
        await self.interaction.followup.send(
            "💔 **THE FINAL BATTLE**\n\n"
            "Where and how did they fall? (Brief description, e.g. 'Fell to Ragnaros')\n"
            "*(Type the cause)*"
        )
        
        msg = await self.wait_for_message()
        self.data["death_cause"] = msg.content.strip()

    async def step_eulogy(self):
        """Step 5: Eulogy (Optional)."""
        view = View()
        btn = Button(label="Compose Eulogy", style=discord.ButtonStyle.primary, emoji="📜")
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary)
        
        async def btn_callback(interaction):
            modal = LongTextModal(title="The Final Words", label="Death Story", placeholder="They fought bravely...")
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["death_story"] = modal.text_input.value
            view.stop()
            
        async def skip_callback(interaction):
            self.data["death_story"] = ""
            await interaction.response.defer()
            view.stop()
            
        btn.callback = btn_callback
        skip.callback = skip_callback
        view.add_item(btn)
        view.add_item(skip)
        
        await self.interaction.followup.send(
            "📜 **THE FINAL WORDS** (Optional)\n"
            "Would you like to compose an in-character eulogy/death story?",
            view=view
        )
        await view.wait()

    async def step_confirmation(self):
        """Step 6: Final Confirmation."""
        embed = discord.Embed(
            title="⚰️ Confirm Burial",
            description=(
                f"**Character:** {self.data['character_data'].get('char_name')}\n"
                f"**Cause:** {self.data['death_cause']}\n"
                f"**Eulogy:** {self.data['death_story'][:100]}...\n\n"
                "⚠️ **This action cannot be undone.**\n"
                "The character will be marked DECEASED and moved to the Cemetery."
            ),
            color=0x000000
        )
        
        view = View()
        confirm = Button(label="Proceed with Burial", style=discord.ButtonStyle.danger, emoji="⚰️")
        cancel = Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        async def confirm_callback(interaction):
            self.data["confirmed"] = True
            await interaction.response.defer()
            view.stop()
            
        async def cancel_callback(interaction):
            self.data["confirmed"] = False
            await interaction.response.send_message("Burial cancelled.", ephemeral=True)
            view.stop()
            
        confirm.callback = confirm_callback
        cancel.callback = cancel_callback
        view.add_item(confirm)
        view.add_item(cancel)
        
        await self.interaction.followup.send(embed=embed, view=view)
        await view.wait()

    async def execute_burial(self):
        """Execute burial by updating sheet."""
        try:
            char_name = self.data["character_data"].get("char_name")
            
            registry = GoogleSheetsService()
            success = registry.update_character_status(
                char_name,
                STATUS_DECEASED, # Triggers webhook
                death_cause=self.data["death_cause"],
                death_story=self.data["death_story"]
            )
            
            if success:
                await self.interaction.followup.send(
                    "⚰️ **THE RITE IS COMPLETE.**\n\n"
                    f"{char_name} rests now in the Cemetery of Heroes."
                )
            else:
                await self.interaction.followup.send("❌ Failed to record burial. Please check the archives manually.")
                
        except Exception as e:
            logger.error(f"Burial execution error: {e}")
            await self.interaction.followup.send("❌ Critical error during burial.")

    async def handle_timeout(self):
        await self.interaction.followup.send("⏳ The candles have burned out. Burial ceremony timed out.")

class LongTextModal(Modal):
    def __init__(self, title, label, placeholder):
        super().__init__(title=title)
        self.text_input = TextInput(label=label, style=discord.TextStyle.paragraph, max_length=1024, placeholder=placeholder, required=True)
        self.add_item(self.text_input)