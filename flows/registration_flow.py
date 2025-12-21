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
Interactive Registration Flow
The 12-step cinematic character creation process.
"""
import logging
import asyncio
import discord
from discord.ui import View, Button, Select, Modal, TextInput
from flows.base_flow import InteractiveFlow
from domain.models import Character, STATUS_PENDING, CLASS_DATA
from domain.validators import (
    VALID_RACES, VALID_CLASSES, VALID_ROLES, VALID_PROFESSIONS,
    validate_race, validate_class, validate_roles, validate_professions, validate_url
)
from services.sheets_service import GoogleSheetsService
from services.webhook_handler import handle_post_to_recruitment # Or trigger mechanism
from utils.embed_parser import build_character_embeds, serialize_embeds
from config.settings import settings

logger = logging.getLogger(__name__)

# Profession validation (WoW rules: max 2 main + 4 secondary)
MAIN_PROFESSIONS = [
    "Alchemy", "Blacksmithing", "Enchanting", "Engineering",
    "Herbalism", "Inscription", "Jewelcrafting", "Leatherworking",
    "Mining", "Skinning", "Tailoring"
]
SECONDARY_PROFESSIONS = ["Cooking", "First Aid", "Fishing", "Archaeology"]

class RegistrationFlow(InteractiveFlow):
    """
    Handles the interactive character registration process.
    """

    async def start(self):
        """Start the 12-step journey."""
        try:
            # Step 1: Introduction & Consent
            await self.step_introduction()
            if not self.data.get("consent"):
                return # User cancelled

            # Step 2: Name
            await self.step_name()

            # Step 3: Race
            await self.step_race()

            # Step 4: Class
            await self.step_class()

            # Step 5: Roles
            await self.step_roles()

            # Step 6: Professions
            await self.step_professions()

            # Step 7: Traits
            await self.step_traits()

            # Step 8: Backstory
            await self.step_backstory()

            # Step 9: Personality
            await self.step_personality()

            # Step 10: Quotes
            await self.step_quotes()

            # Step 11: Portrait
            await self.step_portrait()

            # Step 12: Preview & Confirmation
            await self.step_preview()
            
            # Finalize if confirmed
            if self.data.get("confirmed"):
                await self.finalize()

        except asyncio.TimeoutError:
            await self.handle_timeout()
        except Exception as e:
            logger.error(f"Error in registration flow: {e}")
            await self.interaction.followup.send("⚠️ An error occurred during registration. The Chroniclers are confused.", ephemeral=True)

    async def step_introduction(self):
        """Step 1: Introduction and Consent."""
        embed = discord.Embed(
            title="🏛️ The Chronicles of Azeroth",
            description=(
                "*A massive tome materializes before you, its pages shimmering with arcane energy. "
                "An elderly dwarf with a magnificent beard looks up from his writing desk.*\n\n"
                "Greetings, brave soul! I am **Chronicler Thaldrin**, Keeper of Knowledge.\n"
                "You seek to inscribe your legend into our eternal archives? Splendid!\n\n"
                "But first—a formality. May I record your Discord identity for our records?\n\n"
                "*This conversation is private - only you can see it.*"
            ),
            color=0xC0C0C0
        )

        view = View()
        yes_btn = Button(label="Yes, record my identity", style=discord.ButtonStyle.green, emoji="✅")
        no_btn = Button(label="No, remain anonymous", style=discord.ButtonStyle.red, emoji="❌")

        async def yes_callback(interaction):
            # Validate user object
            if not self.user or not self.user.id:
                logger.error("Invalid user object in registration flow")
                await interaction.response.send_message(
                    "❌ Error: Invalid user session. Please try again.",
                    ephemeral=True
                )
                self.data["consent"] = False
                view.stop()
                return

            self.data["consent"] = True
            self.data["discord_id"] = str(self.user.id)
            self.data["discord_name"] = str(self.user)
            await interaction.response.defer()
            view.stop()

        async def no_callback(interaction):
            self.data["consent"] = False
            await interaction.response.send_message("Very well. The archives require an identity. Perhaps another time.", ephemeral=True)
            view.stop()

        yes_btn.callback = yes_callback
        no_btn.callback = no_callback
        view.add_item(yes_btn)
        view.add_item(no_btn)

        await self.send_or_update(embed=embed, view=view, ephemeral=True)
        await view.wait()

    async def step_name(self):
        """Step 2: Character Name."""
        await self.interaction.followup.send(
            "📜 **CHAPTER ONE: THE NAME**\n\n"
            "Every legend begins with a name. **What shall the bards call your hero?**\n"
            "*(Type your character's full name)*",
            ephemeral=True
        )

        msg = await self.wait_for_message()
        name = msg.content.strip()

        if len(name) > 100:
            await self.interaction.followup.send("That name is too long! The tome cannot contain it. Try again.", ephemeral=True)
            await self.step_name() # Retry
            return

        self.data["char_name"] = name
        await self.interaction.followup.send(
            f"*The quill dances across the parchment, etching '{name.upper()}' in bold runes.*",
            ephemeral=True
        )

    async def step_race(self):
        """Step 3: Race Selection."""
        # Using a Select Menu
        options = [discord.SelectOption(label=race, value=race) for race in VALID_RACES]
        
        view = View()
        select = Select(placeholder="Choose your heritage...", options=options)
        
        async def callback(interaction):
            self.data["race"] = select.values[0]
            await interaction.response.defer()
            view.stop()
            
        select.callback = callback
        view.add_item(select)
        
        await self.interaction.followup.send(
            "⚔️ **CHAPTER TWO: THE BLOODLINE**\n\n"
            "From which people dost thou hail? Choose your heritage:",
            view=view,
            ephemeral=True
        )
        await view.wait()

        # Flavor text
        await self.interaction.followup.send(
            f"Ahh, a {self.data['race']}! The ancestors smile upon you.",
            ephemeral=True
        )

    async def step_class(self):
        """Step 4: Class Selection."""
        options = [
            discord.SelectOption(
                label=cls_name, 
                emoji=meta.emoji, 
                value=cls_name
            ) 
            for cls_name, meta in CLASS_DATA.items()
        ]
        
        view = View()
        select = Select(placeholder="Choose your path...", options=options)
        
        async def callback(interaction):
            self.data["class"] = select.values[0]
            await interaction.response.defer()
            view.stop()
            
        select.callback = callback
        view.add_item(select)
        
        await self.interaction.followup.send(
            "🔮 **CHAPTER THREE: THE CALLING**\n\n"
            "What path has fate woven for thee? Choose your class:",
            view=view,
            ephemeral=True
        )
        await view.wait()

        await self.interaction.followup.send(
            f"⚔️ A {self.data['class']}! Steel and fury!",
            ephemeral=True
        )

    async def step_roles(self):
        """Step 5: Role Selection (Multi-select)."""
        options = [discord.SelectOption(label=role, value=role) for role in VALID_ROLES]
        
        view = View()
        select = Select(
            placeholder="Select your combat roles (Max 3)...", 
            options=options, 
            min_values=1, 
            max_values=min(3, len(options))
        )
        
        async def callback(interaction):
            self.data["roles"] = ", ".join(select.values)
            await interaction.response.defer()
            view.stop()
            
        select.callback = callback
        view.add_item(select)
        
        await self.interaction.followup.send(
            "🎭 **CHAPTER FOUR: THE MANY MASKS**\n\n"
            "What roles do you fulfill when battle calls? (Select at least 1):",
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def step_professions(self):
        """Step 6: Professions (Optional)."""
        options = [discord.SelectOption(label=prof, value=prof) for prof in VALID_PROFESSIONS]
        
        view = View()
        select = Select(
            placeholder="Select professions (Optional)...", 
            options=options, 
            min_values=0, 
            max_values=6 
        )
        
        skip_btn = Button(label="Skip (No professions)", style=discord.ButtonStyle.secondary)
        
        async def select_callback(interaction):
            selected = select.values

            # Validate WoW profession rules: max 2 main + 4 secondary
            main_count = sum(1 for p in selected if p in MAIN_PROFESSIONS)
            secondary_count = sum(1 for p in selected if p in SECONDARY_PROFESSIONS)

            if main_count > 2:
                await interaction.response.send_message(
                    f"❌ You can only have 2 main professions (you selected {main_count})!\n"
                    f"Please try again.",
                    ephemeral=True
                )
                # Don't stop view - user can select again
                return

            if secondary_count > 4:
                await interaction.response.send_message(
                    f"❌ You can only have 4 secondary professions (you selected {secondary_count})!\n"
                    f"Please try again.",
                    ephemeral=True
                )
                # Don't stop view - user can select again
                return

            self.data["professions"] = ", ".join(selected)
            await interaction.response.defer()
            view.stop()
            
        async def skip_callback(interaction):
            self.data["professions"] = ""
            await interaction.response.defer()
            view.stop()
            
        select.callback = select_callback
        skip_btn.callback = skip_callback
        view.add_item(select)
        view.add_item(skip_btn)
        
        await self.interaction.followup.send(
            "🔨 **CHAPTER FIVE: THE CRAFTS**\n\n"
            "Do you practice any trades? (Optional):",
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def step_traits(self):
        """Step 7: The Three Traits."""
        # Using messages since Modal requires Interaction response, but we are in followup flow.
        # Can we send a Modal in followup? NO. Modals respond to Interactions.
        # We can send a button "Enter Traits" that triggers a Modal.

        view = View()
        btn = Button(label="Inscribe Traits", style=discord.ButtonStyle.primary, emoji="⚡")

        async def btn_callback(interaction):
            # This interaction opens the Modal
            modal = TraitsModal(title="The Three Traits")
            await interaction.response.send_modal(modal)
            await modal.wait()

            self.data["trait_1"] = modal.trait1.value
            self.data["trait_2"] = modal.trait2.value
            self.data["trait_3"] = modal.trait3.value

            view.stop()

        btn.callback = btn_callback
        view.add_item(btn)

        await self.interaction.followup.send(
            "⚡ **CHAPTER SIX: THE THREE TRAITS**\n\n"
            "Inscribe three words that define your hero's outer nature (e.g. Brave, Loyal, Stubborn).",
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def step_backstory(self):
        """Step 8: Backstory."""
        # Similar pattern: Button -> Modal
        view = View()
        btn = Button(label="Write My Tale", style=discord.ButtonStyle.primary, emoji="📖")

        async def btn_callback(interaction):
            modal = LongTextModal(title="Your Tale", label="Backstory", placeholder="Once upon a time...")
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["backstory"] = modal.text_input.value
            view.stop()

        btn.callback = btn_callback
        view.add_item(btn)

        await self.interaction.followup.send(
            "📖 **CHAPTER SEVEN: THE TALE**\n\n"
            "Where do you come from? What shaped you?",
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def step_personality(self):
        """Step 9: Personality (Optional)."""
        view = View()
        btn = Button(label="Describe Personality", style=discord.ButtonStyle.primary)
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary)

        async def btn_callback(interaction):
            modal = LongTextModal(title="Inner Soul", label="Personality", placeholder="I am...")
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["personality"] = modal.text_input.value
            view.stop()

        async def skip_callback(interaction):
            self.data["personality"] = ""
            await interaction.response.defer()
            view.stop()

        btn.callback = btn_callback
        skip.callback = skip_callback
        view.add_item(btn)
        view.add_item(skip)

        await self.interaction.followup.send(
            "💭 **CHAPTER EIGHT: THE INNER SOUL** (Optional)\n"
            "Describe your inner thoughts and nature.",
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def step_quotes(self):
        """Step 10: Quotes (Optional)."""
        view = View()
        btn = Button(label="Record Quotes", style=discord.ButtonStyle.primary)
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary)

        async def btn_callback(interaction):
            modal = LongTextModal(title="Famous Words", label="Quotes", placeholder="For the Alliance!|Victory or Death!")
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["quotes"] = modal.text_input.value
            view.stop()

        async def skip_callback(interaction):
            self.data["quotes"] = ""
            await interaction.response.defer()
            view.stop()

        btn.callback = btn_callback
        skip.callback = skip_callback
        view.add_item(btn)
        view.add_item(skip)

        await self.interaction.followup.send(
            "💬 **CHAPTER NINE: THE WORDS** (Optional)\n"
            "Battle cries or catchphrases? (Separate multiple with |)",
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def step_portrait(self):
        """Step 11: Portrait."""
        view = View()
        
        btn_upload = Button(label="Upload Image", style=discord.ButtonStyle.primary, emoji="🖼️")
        btn_url = Button(label="Enter Image URL", style=discord.ButtonStyle.secondary) # Changed to secondary
        btn_default = Button(label="Use Placeholder", style=discord.ButtonStyle.secondary)
        btn_ai = Button(label="Request AI Portrait", style=discord.ButtonStyle.success)

        async def upload_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Please upload your image directly to this chat within the next 60 seconds. Make sure it's an image file!", ephemeral=True)
            view.stop() # Stop the current view so we can wait for a message

            try:
                # Listen for messages from the specific user in the specific channel/DM
                def check(m):
                    return m.author == self.user and m.channel == interaction.channel and m.attachments

                msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                
                if msg.attachments:
                    attachment = msg.attachments[0] # Take the first attachment
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        # Call MCP tool to store image
                        # MCPTools instance needs settings, discord_client.
                        # We can't directly instantiate MCPTools here as it requires a sheets_service.
                        # Instead, we will directly call the function from mcp.tools,
                        # passing the necessary settings and bot instance.
                        from mcp.tools import MCPTools # Import locally to avoid circular
                        mcp_tools_instance = MCPTools(settings, self.bot, None) # sheets_service not needed here
                        
                        thread_name = f"Portrait: {self.data['char_name']} ({self.data['discord_id']})"
                        response = await mcp_tools_instance.post_image_to_graphics_storage(attachment.url, attachment.filename, thread_name=thread_name)


                        if response["success"]:
                            self.data["portrait_url"] = response["cdn_url"]
                            self.data["request_sdxl"] = False
                            await interaction.followup.send("✅ Image uploaded and stored successfully! Your portrait URL has been updated.", ephemeral=True)
                        else:
                            await interaction.followup.send(f"❌ Failed to store image: {response['error']}\nUsing default placeholder instead.", ephemeral=True)
                            self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                            self.data["request_sdxl"] = False
                    else:
                        await interaction.followup.send("❌ That was not an image file. Using default placeholder instead.", ephemeral=True)
                        self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                        self.data["request_sdxl"] = False
                else:
                    await interaction.followup.send("❌ No image attached. Using default placeholder instead.", ephemeral=True)
                    self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                    self.data["request_sdxl"] = False

            except asyncio.TimeoutError:
                await interaction.followup.send("⏰ You took too long to upload an image. Using default placeholder instead.", ephemeral=True)
                self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                self.data["request_sdxl"] = False
            except Exception as e:
                logger.error(f"Error during image upload in registration flow: {e}")
                await interaction.followup.send("❌ An unexpected error occurred during image upload. Using default placeholder instead.", ephemeral=True)
                self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                self.data["request_sdxl"] = False
            
            # The flow continues after image handling
            # Ensure the step_portrait method fully completes its execution
            # The view.stop() already called will handle the waiting part.

        async def url_callback(interaction):
            modal = SingleInputModal(title="Portrait URL", label="URL", placeholder="https://...")
            await interaction.response.send_modal(modal)
            await modal.wait()
            url = modal.text_input.value
            # Validate URL
            try:
                validate_url(url)
                self.data["portrait_url"] = url
                self.data["request_sdxl"] = False
                view.stop()
            except Exception as e:
                # Notify user of validation failure
                await interaction.followup.send(
                    f"❌ Invalid URL: {str(e)}\n\nUsing default placeholder instead.",
                    ephemeral=True
                )
                self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                self.data["request_sdxl"] = False
                view.stop()

        async def default_callback(interaction):
            self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
            self.data["request_sdxl"] = False
            await interaction.response.defer()
            view.stop()

        async def ai_callback(interaction):
            self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL  # Will be replaced by AI later
            self.data["request_sdxl"] = True
            await interaction.response.defer()
            view.stop()

        btn_upload.callback = upload_callback
        btn_url.callback = url_callback
        btn_default.callback = default_callback
        btn_ai.callback = ai_callback

        view.add_item(btn_upload)
        view.add_item(btn_url)
        view.add_item(btn_default)
        view.add_item(btn_ai)

        await self.interaction.followup.send(
            "🎨 **CHAPTER TEN: THE VISAGE** (Optional)\n"
            "Provide a portrait for your character.",
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def step_preview(self):
        """Step 12: Preview."""
        # Create Character object for preview
        char = Character(
            discord_user_id=self.data["discord_id"],
            discord_name=self.data["discord_name"],
            name=self.data["char_name"],
            race=self.data["race"],
            char_class=self.data["class"],
            roles=self.data["roles"],
            professions=self.data["professions"],
            backstory=self.data["backstory"],
            personality=self.data.get("personality", ""),
            quotes=self.data.get("quotes", ""),
            portrait_url=self.data.get("portrait_url", ""),
            trait_1=self.data["trait_1"],
            trait_2=self.data["trait_2"],
            trait_3=self.data["trait_3"],
            status=STATUS_PENDING,
            confirmation=False,
            request_sdxl=self.data.get("request_sdxl", False)
        )
        
        embeds = build_character_embeds(char)
        self.data["preview_embeds"] = embeds # Store for finalization
        
        view = View()
        confirm = Button(label="Inscribe into Legend!", style=discord.ButtonStyle.green, emoji="✅")
        cancel = Button(label="Cancel", style=discord.ButtonStyle.red)
        
        async def confirm_callback(interaction):
            self.data["confirmed"] = True
            await interaction.response.defer()
            view.stop()
            
        async def cancel_callback(interaction):
            self.data["confirmed"] = False
            await interaction.response.send_message("Registration cancelled.", ephemeral=True)
            view.stop()
            
        confirm.callback = confirm_callback
        cancel.callback = cancel_callback
        view.add_item(confirm)
        view.add_item(cancel)
        
        await self.interaction.followup.send(
            "📋 **THE CHRONICLE PREVIEW**\n"
            "Does this look correct?",
            embeds=embeds,
            view=view,
            ephemeral=True
        )
        await view.wait()

    async def finalize(self):
        """Finalize registration."""
        # Write to sheets
        try:
            embed_json = serialize_embeds(self.data["preview_embeds"])

            char_data = {
                "discord_id": self.data["discord_id"],
                "discord_name": self.data["discord_name"],
                "char_name": self.data["char_name"],
                "race": self.data["race"],
                "class": self.data["class"],
                "roles": self.data["roles"],
                "professions": self.data["professions"],
                "trait_1": self.data["trait_1"],
                "trait_2": self.data["trait_2"],
                "trait_3": self.data["trait_3"],
                "backstory": self.data["backstory"],
                "personality": self.data.get("personality", ""),
                "quotes": self.data.get("quotes", ""),
                "portrait_url": self.data.get("portrait_url", ""),
                "status": STATUS_PENDING,
                "confirmation": True,
                "request_sdxl": self.data.get("request_sdxl", False),
                "embed_json": embed_json
            }

            registry = GoogleSheetsService()
            success = registry.log_character(char_data)

            if success:
                await self.interaction.followup.send(
                    "✨ **THE INSCRIPTION IS COMPLETE!** ✨\n\n"
                    "Your character has been submitted for review. Watch for a DM!",
                    ephemeral=True
                )
                # Trigger webhook logic locally if needed, or rely on Google Script to trigger it?
                # The BLUEPRINT says:
                # [AT THIS MOMENT:] -> Google Sheets row created -> Webhook triggers
                # So we just write to sheet. The Google Script triggers the bot's webhook endpoint.
                # Bot doesn't need to call handle_post_to_recruitment directly here.
                # Wait, local testing environment doesn't have Google Script trigger.
                # But in production, it's Path B.
                # So we are done.
            else:
                await self.interaction.followup.send("❌ Failed to write to archives. Please alert the officers.", ephemeral=True)

        except Exception as e:
            logger.error(f"Finalization error: {e}")
            await self.interaction.followup.send("❌ Critical error during inscription.", ephemeral=True)

    async def handle_timeout(self):
        if self.message:
            await self.message.reply("⏳ The ink has dried. Registration timed out.")
        else:
            await self.interaction.followup.send("⏳ Registration timed out.")

# Helper Modals
class TraitsModal(Modal):
    trait1 = TextInput(label="Trait 1", max_length=50, required=True)
    trait2 = TextInput(label="Trait 2", max_length=50, required=True)
    trait3 = TextInput(label="Trait 3", max_length=50, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        """Acknowledge modal submission to prevent Discord timeout errors."""
        await interaction.response.defer()

class LongTextModal(Modal):
    def __init__(self, title, label, placeholder):
        super().__init__(title=title)
        self.text_input = TextInput(label=label, style=discord.TextStyle.paragraph, max_length=1024, placeholder=placeholder, required=True)
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        """Acknowledge modal submission to prevent Discord timeout errors."""
        await interaction.response.defer()

class SingleInputModal(Modal):
    def __init__(self, title, label, placeholder):
        super().__init__(title=title)
        self.text_input = TextInput(label=label, max_length=200, placeholder=placeholder, required=True)
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        """Acknowledge modal submission to prevent Discord timeout errors."""
        await interaction.response.defer()
