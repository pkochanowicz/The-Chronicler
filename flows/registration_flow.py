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


class FlowCancelled(Exception):
    """Exception raised when user cancels the flow."""

    pass


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

    def _create_cancel_callback(self, view: View):
        """Helper to create a cancel callback that raises FlowCancelled."""

        async def cancel_callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                "❌ **Registration Cancelled**\n\nThe registration process has been cancelled. "
                "You can start over anytime with `/register_character`.",
                ephemeral=True,
            )
            view.stop()
            raise FlowCancelled("User cancelled the registration flow")

        return cancel_callback

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

        except FlowCancelled:
            logger.info(
                f"Registration flow cancelled by user {self.interaction.user.name}"
            )
            # User already received cancellation message, no need to send another
            return
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
                "Greetings! I am **Chronicler Thaldrin**.\n\n"
                "📜 **Before We Begin - Preparation Checklist**\n\n"
                "This process creates your character sheet, compatible with **TurtleRP Addon**:\n"
                "🔗 https://github.com/tempranova/turtlerp/releases/latest\n\n"
                "**Required fields:**\n"
                "• Character Name (max 64 chars)\n"
                "• Race & Class\n"
                "• 3 Traits (max 128 chars each)\n"
                "• Backstory/Story (max 2048 chars)\n\n"
                "**Optional fields:**\n"
                "• Personality description (max 1024 chars)\n"
                "• Notable quotes (max 1024 chars)\n"
                "• Professions (up to 2 primary + secondaries)\n"
                "• Portrait image (upload, URL, default, or AI-generated)\n\n"
                "⚠️ **Tip:** The backstory field can take time to write! Consider drafting in a text editor first, then paste when prompted.\n\n"
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
        view = View()
        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

        await self.interaction.followup.send(
            "📜 **CHAPTER ONE: THE NAME**\nType your character's full name (max 64 characters):",
            view=view,
            ephemeral=True,
        )

        msg = await self.wait_for_message()
        self.data["char_name"] = msg.content.strip()
        view.stop()
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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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
                "⏱️ You have **30 minutes**. Drag & drop is not supported in ephemeral chats.\n"
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

                msg = await self.bot.wait_for(
                    "message", check=check, timeout=self.timeout
                )

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

        cancel_btn = Button(
            label="Cancel Registration",
            style=discord.ButtonStyle.danger,
            emoji="❌",
        )
        cancel_btn.callback = self._create_cancel_callback(view)
        view.add_item(cancel_btn)

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
            settings = get_settings()

            _, session_maker = get_engine_and_session_maker()
            async with session_maker() as session:
                service = CharacterService(session)

                # Check if character with this name already exists
                existing_char = await service.get_character_by_name(char_create.name)

                if existing_char:
                    # Check if user is owner or officer
                    user_roles = [r.id for r in self.interaction.user.roles]
                    is_officer = any(
                        role_id in user_roles for role_id in settings.OFFICER_ROLE_IDS
                    )
                    is_owner = existing_char.discord_user_id == self.interaction.user.id

                    if is_owner or is_officer:
                        # Update existing character
                        from models.pydantic_models import CharacterUpdate

                        update_data = CharacterUpdate(
                            discord_user_id=char_create.discord_user_id,
                            discord_username=char_create.discord_username,
                            race=char_create.race,
                            class_name=char_create.class_name,
                            roles=char_create.roles,
                            professions=char_create.professions,
                            backstory=char_create.backstory,
                            personality=char_create.personality,
                            quotes=char_create.quotes,
                            portrait_url=char_create.portrait_url,
                            trait_1=char_create.trait_1,
                            trait_2=char_create.trait_2,
                            trait_3=char_create.trait_3,
                            embed_json=embed_json,
                        )

                        created_char = await service.update_character(
                            existing_char.id, update_data
                        )
                        await session.commit()

                        # Update or create the recruitment message
                        if (
                            existing_char.recruitment_msg_id
                            and existing_char.forum_post_id
                        ):
                            # Update existing recruitment post
                            logger.info(
                                f"Updating existing recruitment post for {char_create.name} "
                                f"(msg_id={existing_char.recruitment_msg_id}, forum_id={existing_char.forum_post_id})"
                            )
                            try:
                                settings = get_settings()
                                channel = self.bot.get_channel(
                                    settings.RECRUITMENT_CHANNEL_ID
                                ) or await self.bot.fetch_channel(
                                    settings.RECRUITMENT_CHANNEL_ID
                                )

                                if isinstance(channel, discord.ForumChannel):
                                    # Get the forum post thread
                                    thread = self.bot.get_channel(
                                        existing_char.forum_post_id
                                    ) or await self.bot.fetch_channel(
                                        existing_char.forum_post_id
                                    )
                                    if thread:
                                        # Update the starter message with new embeds
                                        starter_message = await thread.fetch_message(
                                            existing_char.recruitment_msg_id
                                        )
                                        if starter_message:
                                            # Convert embed_json dicts to Embed objects
                                            embeds_to_send = [
                                                discord.Embed.from_dict(e)
                                                for e in embed_json
                                            ]
                                            await starter_message.edit(
                                                embeds=embeds_to_send
                                            )
                                            logger.info(
                                                f"Successfully updated recruitment post for {char_create.name}"
                                            )
                                    else:
                                        logger.warning(
                                            f"Could not find forum thread {existing_char.forum_post_id}, creating new post"
                                        )
                                        # Forum thread not found, create new post
                                        char_dict = created_char.model_dump()
                                        char_dict["embed_json"] = embed_json
                                        char_dict["char_name"] = created_char.name
                                        char_dict[
                                            "discord_name"
                                        ] = created_char.discord_username
                                        await handle_post_to_recruitment(
                                            char_dict, discord_bot=self.bot
                                        )
                            except Exception as e:
                                logger.error(
                                    f"Failed to update recruitment message: {e}",
                                    exc_info=True,
                                )
                                logger.info("Creating new recruitment post instead")
                                # If update fails, create new post
                                char_dict = created_char.model_dump()
                                char_dict["embed_json"] = embed_json
                                char_dict["char_name"] = created_char.name
                                char_dict[
                                    "discord_name"
                                ] = created_char.discord_username
                                await handle_post_to_recruitment(
                                    char_dict, discord_bot=self.bot
                                )
                        else:
                            # No existing recruitment post, create new one
                            logger.info(
                                f"No existing recruitment post for {char_create.name}, creating new one"
                            )
                            char_dict = created_char.model_dump()
                            char_dict["embed_json"] = embed_json
                            char_dict["char_name"] = created_char.name
                            char_dict["discord_name"] = created_char.discord_username
                            await handle_post_to_recruitment(
                                char_dict, discord_bot=self.bot
                            )

                        await self.interaction.followup.send(
                            f"✨ **UPDATED!** Character '{char_create.name}' has been updated.",
                            ephemeral=True,
                        )
                    else:
                        # Not owner and not officer - show error
                        await self.interaction.followup.send(
                            f"❌ A character named '{char_create.name}' already exists and belongs to another user. "
                            f"Please choose a different name.",
                            ephemeral=True,
                        )
                        return
                else:
                    # Create new character
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

                    await self.interaction.followup.send(
                        "✨ **SUBMITTED!** Your character is being posted to recruitment.",
                        ephemeral=True,
                    )

                    # Trigger Discord Thread creation via Webhook Logic (only for new characters)
                    char_dict = created_char.model_dump()
                    char_dict["embed_json"] = embed_json
                    char_dict["char_name"] = created_char.name
                    char_dict["discord_name"] = created_char.discord_username

                    logger.info(
                        f"Calling handle_post_to_recruitment for character: {created_char.name} (ID: {created_char.id})"
                    )
                    await handle_post_to_recruitment(char_dict, discord_bot=self.bot)
                    logger.info(
                        f"Returned from handle_post_to_recruitment for character: {created_char.name}"
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
    trait1 = TextInput(label="Trait 1", max_length=128, required=True)
    trait2 = TextInput(label="Trait 2", max_length=128, required=True)
    trait3 = TextInput(label="Trait 3", max_length=128, required=True)

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
