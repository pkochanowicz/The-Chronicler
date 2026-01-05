# flows/burial_flow.py
import logging
import asyncio
import discord
from discord.ui import View, Button, Modal, TextInput
from flows.base_flow import InteractiveFlow
from services.character_service import CharacterService
from services.webhook_handler import handle_initiate_burial
from schemas.db_schemas import CharacterStatusEnum
from db.database import get_engine_and_session_maker
from models.pydantic_models import CharacterUpdate

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
            await self.interaction.followup.send(
                "❌ The rite was interrupted by a disturbance.", ephemeral=True
            )

    async def step_introduction(self):
        embed = discord.Embed(
            title="⚰️ The Rite of Remembrance",
            description=(
                "*The chronicler's expression grows somber...*\n\n"
                "Officer... you invoke the Rite of Remembrance.\n"
                "**Shall we begin?**"
            ),
            color=0x4A4A4A,
        )
        view = View()
        yes_btn = Button(
            label="Begin Rite", style=discord.ButtonStyle.primary, emoji="⚰️"
        )
        cancel_btn = Button(label="Cancel", style=discord.ButtonStyle.secondary)

        async def yes_callback(interaction):
            self.data["proceed"] = True
            await interaction.response.defer()
            view.stop()

        async def cancel_callback(interaction):
            self.data["proceed"] = False
            await interaction.response.send_message(
                "The rite is postponed.", ephemeral=True
            )
            view.stop()

        yes_btn.callback = yes_callback
        cancel_btn.callback = cancel_callback
        view.add_item(yes_btn)
        view.add_item(cancel_btn)
        await self.send_or_update(embed=embed, view=view)
        await view.wait()

    async def step_search(self):
        await self.interaction.followup.send(
            "🔍 **THE FALLEN HERO**\nWhich hero has fallen?\n*(Type the character's exact name)*"
        )
        msg = await self.wait_for_message()
        search_name = msg.content.strip()

        # Use CharacterService to find
        _, session_maker = get_engine_and_session_maker()
        async with session_maker() as session:
            service = CharacterService(session)
            char = await service.get_character_by_name(search_name)

            if not char:
                await self.interaction.followup.send(
                    f"❌ Could not find a record for '{search_name}'."
                )
                self.data["character_found"] = False
                return

            # Store Pydantic model in data
            self.data["character_found"] = True
            self.data["character_model"] = char

        await self.interaction.followup.send("*The pages flip on their own...*")

    async def step_verification(self):
        char = self.data["character_model"]

        # Parse existing embeds to show preview
        # embed_json is List[Dict] or List[Embed]
        preview_embed = None
        if char.embed_json:
            # Assume it's list of dicts
            import discord

            try:
                if isinstance(char.embed_json, list) and char.embed_json:
                    preview_embed = discord.Embed.from_dict(char.embed_json[0])
            except Exception:  # nosec B110
                pass  # Silently ignore embed parsing errors

        content = (
            f"**{char.name}**\n"
            f"Race: {char.race.value} • Class: {char.class_name.value}\n"
            f"Status: {char.status.value}\n\n"
            "**Is this the fallen hero?**"
        )

        view = View()
        yes_btn = Button(
            label="Yes, this is correct", style=discord.ButtonStyle.green, emoji="✅"
        )
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
        await self.interaction.followup.send(
            content=content, embed=preview_embed, view=view
        )
        await view.wait()

    async def step_death_cause(self):
        await self.interaction.followup.send(
            "💔 **THE FINAL BATTLE**\nWhere and how did they fall?\n*(Type the cause)*"
        )
        msg = await self.wait_for_message()
        self.data["death_cause"] = msg.content.strip()

    async def step_eulogy(self):
        view = View()
        btn = Button(
            label="Compose Eulogy", style=discord.ButtonStyle.primary, emoji="📜"
        )
        skip = Button(label="Skip", style=discord.ButtonStyle.secondary)

        async def btn_callback(interaction):
            modal = LongTextModal(
                title="The Final Words",
                label="Death Story",
                placeholder="They fought bravely...",
            )
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
            "📜 **THE FINAL WORDS** (Optional)", view=view
        )
        await view.wait()

    async def step_confirmation(self):
        embed = discord.Embed(
            title="⚰️ Confirm Burial",
            description=(
                f"**Character:** {self.data['character_model'].name}\n"
                f"**Cause:** {self.data['death_cause']}\n"
                f"**Eulogy:** {self.data['death_story'][:100]}...\n\n"
                "⚠️ **This action cannot be undone.**"
            ),
            color=0x000000,
        )
        view = View()
        confirm = Button(label="Proceed", style=discord.ButtonStyle.danger, emoji="⚰️")
        cancel = Button(label="Cancel", style=discord.ButtonStyle.secondary)

        async def confirm_callback(interaction):
            self.data["confirmed"] = True
            await interaction.response.defer()
            view.stop()

        async def cancel_callback(interaction):
            self.data["confirmed"] = False
            await interaction.response.send_message("Cancelled.", ephemeral=True)
            view.stop()

        confirm.callback = confirm_callback
        cancel.callback = cancel_callback
        view.add_item(confirm)
        view.add_item(cancel)
        await self.interaction.followup.send(embed=embed, view=view)
        await view.wait()

    async def execute_burial(self):
        """Execute burial by updating SQL."""
        try:
            char_model = self.data["character_model"]

            _, session_maker = get_engine_and_session_maker()
            async with session_maker() as session:
                service = CharacterService(session)

                # 1. Create Graveyard Entry
                # Note: bury_character method in service handles creating graveyard entry
                await service.bury_character(
                    character_id=char_model.id,
                    cause_of_death=self.data["death_cause"],
                    eulogy=self.data["death_story"],
                )

                # 2. Update Character Status
                update_data = CharacterUpdate(
                    status=CharacterStatusEnum.DECEASED,
                    death_cause=self.data["death_cause"],
                    death_story=self.data["death_story"],
                )
                updated_char = await service.update_character(
                    char_model.id, update_data
                )

                if updated_char:
                    # 3. Trigger Discord Notification via Handler
                    # We pass a dict representation
                    char_dict = updated_char.model_dump()
                    # Add extra fields needed by handler
                    char_dict["char_name"] = updated_char.name

                    # Handler expects forum_post_url to extract thread_id
                    # Handler logic: `thread_id = int(url.split("/")[-1])`. So passing "dummy/123" works.
                    char_dict["forum_post_url"] = f"dummy/{updated_char.forum_post_id}"

                    # Ensure discord_user_id is included for DM notification
                    char_dict["discord_user_id"] = updated_char.discord_user_id

                    logger.info(
                        f"Initiating burial for {updated_char.name}, forum_post_id={updated_char.forum_post_id}, embed_json present: {bool(updated_char.embed_json)}"
                    )

                    # Pass the bot instance from the interaction client
                    await handle_initiate_burial(char_dict, self.interaction.client)

                    await self.interaction.followup.send("⚰️ **THE RITE IS COMPLETE.**")
                else:
                    await self.interaction.followup.send("❌ Database update failed.")

        except Exception as e:
            logger.error(f"Burial execution error: {e}")
            await self.interaction.followup.send("❌ Critical error during burial.")

    async def handle_timeout(self):
        await self.interaction.followup.send("⏳ Timed out.")


class LongTextModal(Modal):
    def __init__(self, title, label, placeholder):
        super().__init__(title=title)
        self.text_input = TextInput(
            label=label,
            style=discord.TextStyle.paragraph,
            max_length=1024,
            placeholder=placeholder,
            required=False,
        )
        self.add_item(self.text_input)
