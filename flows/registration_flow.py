# flows/registration_flow.py
import logging
import asyncio
import discord
from discord.ui import View, Button, Select, Modal, TextInput
from flows.base_flow import InteractiveFlow
from models.pydantic_models import CharacterCreate
from schemas.db_schemas import CharacterRaceEnum, CharacterClassEnum, CharacterRoleEnum
from services.character_service import CharacterService
from services.webhook_handler import handle_post_to_recruitment
from utils.embed_parser import build_character_embeds
from config.settings import get_settings
from db.database import get_engine_and_session_maker
from domain.validators import VALID_RACES, VALID_ROLES, VALID_PROFESSIONS
from domain.game_data import CLASS_DATA

logger = logging.getLogger(__name__)

# Profession validation
MAIN_PROFESSIONS = [
    "Alchemy",
    "Blacksmithing",
    "Enchanting",
    "Engineering",
    "Herbalism",
    "Inscription",
    "Jewelcrafting",
    "Leatherworking",
    "Mining",
    "Skinning",
    "Tailoring",
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
                return  # User cancelled

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
            logger.error(f"Error in registration flow: {e}", exc_info=True)
            await self.interaction.followup.send(
                "⚠️ An error occurred during registration. The Chroniclers are confused.",
                ephemeral=True,
            )

    # ... [Steps 1-11 remain largely the same, but we ensure data format matches Enums] ...

    async def step_introduction(self):
        """Step 1: Introduction and Consent."""
        embed = discord.Embed(
            title="🏛️ The Chronicles of Azeroth",
            description=(
                "*A massive tome materializes before you...*\n\n"
                "Greetings! I am **Chronicler Thaldrin**.\n"
                "May I record your Discord identity for our records?\n"
            ),
            color=0xC0C0C0,
        )
        view = View()
        yes_btn = Button(
            label="Yes, record my identity", style=discord.ButtonStyle.green, emoji="✅"
        )
        no_btn = Button(
            label="No, remain anonymous", style=discord.ButtonStyle.red, emoji="❌"
        )

        async def yes_callback(interaction):
            self.data["consent"] = True
            self.data["discord_id"] = interaction.user.id  # INT
            self.data["discord_name"] = interaction.user.name
            await interaction.response.defer()
            view.stop()

        async def no_callback(interaction):
            self.data["consent"] = False
            await interaction.response.send_message(
                "Very well. Perhaps another time.", ephemeral=True
            )
            view.stop()

        yes_btn.callback = yes_callback
        no_btn.callback = no_callback
        view.add_item(yes_btn)
        view.add_item(no_btn)
        await self.send_or_update(embed=embed, view=view, ephemeral=True)
        await view.wait()

    async def step_name(self):
        await self.interaction.followup.send(
            "📜 **CHAPTER ONE: THE NAME**\nType your character's full name:",
            ephemeral=True,
        )
        msg = await self.wait_for_message()
        self.data["char_name"] = msg.content.strip()
        await self.interaction.followup.send(
            f"Recorded: **{self.data['char_name']}**", ephemeral=True
        )

    async def step_race(self):
        options = [discord.SelectOption(label=race, value=race) for race in VALID_RACES]
        view = View()
        select = Select(placeholder="Choose your heritage...", options=options)

        async def callback(interaction):
            self.data["race"] = select.values[0]  # String matching Enum value
            await interaction.response.defer()
            view.stop()

        select.callback = callback
        view.add_item(select)
        await self.interaction.followup.send(
            "⚔️ **CHAPTER TWO: THE BLOODLINE**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_class(self):
        options = [
            discord.SelectOption(label=cls_name, emoji=meta.emoji, value=cls_name)
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
            "🔮 **CHAPTER THREE: THE CALLING**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_roles(self):
        options = [discord.SelectOption(label=role, value=role) for role in VALID_ROLES]
        view = View()
        select = Select(
            placeholder="Select roles...", options=options, min_values=1, max_values=3
        )

        async def callback(interaction):
            self.data["roles"] = select.values  # LIST of strings
            await interaction.response.defer()
            view.stop()

        select.callback = callback
        view.add_item(select)
        await self.interaction.followup.send(
            "🎭 **CHAPTER FOUR: ROLES**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_professions(self):
        options = [
            discord.SelectOption(label=prof, value=prof) for prof in VALID_PROFESSIONS
        ]
        view = View()
        select = Select(
            placeholder="Select professions...",
            options=options,
            min_values=0,
            max_values=6,
        )
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary)

        async def callback(interaction):
            self.data["professions"] = select.values  # List of strings
            await interaction.response.defer()
            view.stop()

        async def skip_callback(interaction):
            self.data["professions"] = []
            await interaction.response.defer()
            view.stop()

        select.callback = callback
        skip.callback = skip_callback
        view.add_item(select)
        view.add_item(skip)
        await self.interaction.followup.send(
            "🔨 **CHAPTER FIVE: CRAFTS**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_traits(self):
        view = View()
        btn = Button(label="Enter Traits", style=discord.ButtonStyle.primary)

        async def cb(interaction):
            modal = TraitsModal(title="Traits")
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["trait_1"] = modal.trait1.value
            self.data["trait_2"] = modal.trait2.value
            self.data["trait_3"] = modal.trait3.value
            view.stop()

        btn.callback = cb
        view.add_item(btn)
        await self.interaction.followup.send(
            "⚡ **CHAPTER SIX: TRAITS**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_backstory(self):
        view = View()
        btn = Button(label="Write Backstory", style=discord.ButtonStyle.primary)

        async def cb(interaction):
            modal = LongTextModal(
                title="Backstory",
                label="Backstory",
                placeholder="Once upon a time...",
                max_length=2048,
            )
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["backstory"] = modal.text_input.value
            view.stop()

        btn.callback = cb
        view.add_item(btn)
        await self.interaction.followup.send(
            "📖 **CHAPTER SEVEN: TALE**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_personality(self):
        # ... (Simplified for brevity, same pattern) ...
        view = View()
        btn = Button(label="Write Personality", style=discord.ButtonStyle.primary)
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary)

        async def cb(interaction):
            modal = LongTextModal(
                title="Personality", label="Personality", placeholder="..."
            )
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["personality"] = modal.text_input.value
            view.stop()

        async def sk(interaction):
            self.data["personality"] = None
            await interaction.response.defer()
            view.stop()

        btn.callback = cb
        skip.callback = sk
        view.add_item(btn)
        view.add_item(skip)
        await self.interaction.followup.send(
            "💭 **CHAPTER EIGHT: PERSONALITY**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_quotes(self):
        # ...
        view = View()
        btn = Button(label="Write Quotes", style=discord.ButtonStyle.primary)
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary)

        async def cb(interaction):
            modal = LongTextModal(title="Quotes", label="Quotes", placeholder="...")
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["quotes"] = modal.text_input.value
            view.stop()

        async def sk(interaction):
            self.data["quotes"] = None
            await interaction.response.defer()
            view.stop()

        btn.callback = cb
        skip.callback = sk
        view.add_item(btn)
        view.add_item(skip)
        await self.interaction.followup.send(
            "💬 **CHAPTER NINE: QUOTES**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_portrait(self):
        """Step 11: Portrait Upload/URL"""
        settings = get_settings()
        view = View()
        btn_upload = Button(
            label="Upload Image", style=discord.ButtonStyle.primary, emoji="🖼️"
        )
        btn_url = Button(label="Enter Image URL", style=discord.ButtonStyle.secondary)
        btn_default = Button(
            label="Use Placeholder", style=discord.ButtonStyle.secondary
        )
        btn_ai = Button(label="Request AI Portrait", style=discord.ButtonStyle.success)

        async def upload_callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                "📸 **Upload your character portrait:**\n\n"
                "• Click the **+** button (or 📎 paperclip icon) next to the message box\n"
                "• Select **Upload a File** and choose your image\n"
                "• Send the message with the image\n\n"
                "⏱️ You have **60 seconds**. Drag & drop is not supported in ephemeral chats.\n"
                "Make sure it's an image file (PNG, JPG, etc.)!",
                ephemeral=True,
            )

            try:

                def check(m):
                    return (
                        m.author.id == self.user.id
                        and m.channel.id == interaction.channel_id
                        and m.attachments
                    )

                msg = await self.bot.wait_for("message", check=check, timeout=60.0)

                if msg.attachments:
                    attachment = msg.attachments[0]
                    if attachment.content_type and attachment.content_type.startswith(
                        "image/"
                    ):
                        # TODO: Replace with a call to the external MCP server client
                        self.data["portrait_url"] = attachment.url
                        self.data["request_sdxl"] = False
                        await interaction.followup.send(
                            "✅ Image URL captured! It will be processed later.",
                            ephemeral=True,
                        )
                    else:
                        await interaction.followup.send(
                            "❌ That was not an image file. Using default placeholder instead.",
                            ephemeral=True,
                        )
                        self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                        self.data["request_sdxl"] = False
                else:
                    await interaction.followup.send(
                        "❌ No image attached. Using default placeholder instead.",
                        ephemeral=True,
                    )
                    self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                    self.data["request_sdxl"] = False

            except asyncio.TimeoutError:
                await interaction.followup.send(
                    "⏰ You took too long to upload an image. Using default placeholder instead.",
                    ephemeral=True,
                )
                self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                self.data["request_sdxl"] = False
            except Exception as e:
                logger.error(f"Error during image upload in registration flow: {e}")
                await interaction.followup.send(
                    "❌ An unexpected error occurred during image upload. Using default placeholder instead.",
                    ephemeral=True,
                )
                self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
                self.data["request_sdxl"] = False
            finally:
                # Only stop the view after upload process completes
                view.stop()

        async def url_callback(interaction):
            modal = SingleInputModal(
                title="Portrait URL", label="URL", placeholder="https://..."
            )
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.data["portrait_url"] = modal.text_input.value
            self.data["request_sdxl"] = False
            view.stop()

        async def default_callback(interaction):
            self.data["portrait_url"] = settings.DEFAULT_PORTRAIT_URL
            self.data["request_sdxl"] = False
            await interaction.response.defer()
            view.stop()

        async def ai_callback(interaction):
            self.data["portrait_url"] = None
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
            "🎨 **CHAPTER TEN: PORTRAIT**", view=view, ephemeral=True
        )
        await view.wait()

    async def step_preview(self):
        # Create a dummy Pydantic object just for the embed builder if needed,
        # or just pass a dict if build_character_embeds supports it.
        # Actually build_character_embeds expects a 'Character' object (SQL/Pydantic).
        # Let's mock a simple object or dict.
        # Ideally, we should construct the Pydantic model here to validate before preview.

        try:
            # Convert roles string list to Enums
            roles_enums = [CharacterRoleEnum(r) for r in self.data["roles"]]

            char_create = CharacterCreate(
                discord_user_id=self.data["discord_id"],
                discord_username=self.data["discord_name"],
                name=self.data["char_name"],
                race=CharacterRaceEnum(self.data["race"]),
                class_name=CharacterClassEnum(self.data["class"]),
                roles=roles_enums,
                professions=self.data["professions"],
                backstory=self.data["backstory"],
                personality=self.data.get("personality"),
                quotes=self.data.get("quotes"),
                portrait_url=self.data.get("portrait_url"),
                trait_1=self.data["trait_1"],
                trait_2=self.data["trait_2"],
                trait_3=self.data["trait_3"],
                request_sdxl=False,
            )
            self.data["valid_model"] = char_create

            # TODO: Update build_character_embeds to accept Pydantic model
            # For now, we can rely on attributes matching
            embeds = build_character_embeds(char_create)
            self.data["preview_embeds"] = embeds

            view = View()
            confirm = Button(label="Submit", style=discord.ButtonStyle.green)
            cancel = Button(label="Cancel", style=discord.ButtonStyle.red)

            async def ok(interaction):
                self.data["confirmed"] = True
                await interaction.response.defer()
                view.stop()

            async def no(interaction):
                self.data["confirmed"] = False
                await interaction.response.send_message("Cancelled.", ephemeral=True)
                view.stop()

            confirm.callback = ok
            cancel.callback = no
            view.add_item(confirm)
            view.add_item(cancel)

            await self.interaction.followup.send(
                "📋 **PREVIEW**", embeds=embeds, view=view, ephemeral=True
            )
            await view.wait()

        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            await self.interaction.followup.send(
                f"❌ Validation Error: {e}", ephemeral=True
            )
            self.data["confirmed"] = False

    async def finalize(self):
        """Finalize registration using SQL Service."""
        try:
            char_create = self.data["valid_model"]
            embed_json = [e.to_dict() for e in self.data["preview_embeds"]]

            _, session_maker = get_engine_and_session_maker()
            async with session_maker() as session:
                service = CharacterService(session)
                created_char = await service.create_character(char_create)

                # Update the embed_json
                from schemas.db_schemas import Character
                from sqlalchemy import update

                await session.execute(
                    update(Character)
                    .where(Character.id == created_char.id)
                    .values(embed_json=embed_json)
                )
                await session.commit()

                # Trigger Discord Thread creation via Webhook Logic
                char_dict = created_char.model_dump()
                char_dict["embed_json"] = embed_json
                char_dict["char_name"] = created_char.name
                char_dict["discord_name"] = created_char.discord_username

                await handle_post_to_recruitment(char_dict, discord_bot=self.bot)

            await self.interaction.followup.send(
                "✨ **SUBMITTED!** Check #recruitment.", ephemeral=True
            )

        except Exception as e:
            logger.error(f"Finalization error: {e}", exc_info=True)
            await self.interaction.followup.send(
                "❌ Critical error during submission.", ephemeral=True
            )

    async def handle_timeout(self):
        if self.message:
            await self.message.reply("⏳ Timed out.")
        else:
            await self.interaction.followup.send("⏳ Timed out.")


# --- Helper Modals ---
class TraitsModal(Modal):
    trait1 = TextInput(label="Trait 1", max_length=50, required=True)
    trait2 = TextInput(label="Trait 2", max_length=50, required=True)
    trait3 = TextInput(label="Trait 3", max_length=50, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class LongTextModal(Modal):
    def __init__(self, title, label, placeholder, max_length=1024):
        super().__init__(title=title)
        self.text_input = TextInput(
            label=label,
            style=discord.TextStyle.paragraph,
            max_length=max_length,
            placeholder=placeholder,
            required=True,
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class SingleInputModal(Modal):
    def __init__(self, title, label, placeholder):
        super().__init__(title=title)
        self.text_input = TextInput(
            label=label, max_length=200, placeholder=placeholder, required=True
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
