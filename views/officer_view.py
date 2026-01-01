import discord
from discord.ui import View, Button
from services.character_service import CharacterService
from schemas.db_schemas import CharacterStatusEnum
from config.settings import get_settings
from db.database import get_engine_and_session_maker
import logging

logger = logging.getLogger(__name__)


class ReasonModal(discord.ui.Modal):
    def __init__(self, action: str):
        super().__init__(title=f"{action} Reason")
        self.reason = discord.ui.TextInput(
            label="Reason", style=discord.TextStyle.paragraph, required=True
        )
        self.add_item(self.reason)
        self.action = action
        self.reason_value = None

    async def on_submit(self, interaction: discord.Interaction):
        self.reason_value = self.reason.value
        await interaction.response.defer()


class OfficerControlView(View):
    def __init__(self, bot, character_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.character_id = character_id
        self.settings = get_settings()

    async def check_permissions(self, interaction: discord.Interaction) -> bool:
        user_roles = [r.id for r in interaction.user.roles]
        allowed_roles = self.settings.OFFICER_ROLE_IDS
        if not any(rid in user_roles for rid in allowed_roles):
            await interaction.response.send_message(
                "❌ Only officers can perform this action.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(
        label="Approve", style=discord.ButtonStyle.green, custom_id="officer_approve"
    )
    async def approve_button(self, interaction: discord.Interaction, button: Button):
        await self.approve_logic(interaction)

    async def approve_logic(self, interaction: discord.Interaction):
        if not await self.check_permissions(interaction):
            return

        await interaction.response.defer()

        _, session_maker = get_engine_and_session_maker()
        async with session_maker() as session:
            service = CharacterService(session)

            from models.pydantic_models import CharacterUpdate

            char_update = CharacterUpdate(status=CharacterStatusEnum.REGISTERED)

            updated_char = await service.update_character(
                self.character_id, char_update
            )

            if not updated_char:
                await interaction.followup.send(
                    "❌ Character not found in DB.", ephemeral=True
                )
                return

            vault_channel_id = self.settings.CHARACTER_SHEET_VAULT_CHANNEL_ID
            vault_channel = self.bot.get_channel(
                vault_channel_id
            ) or await self.bot.fetch_channel(vault_channel_id)

            if not vault_channel:
                await interaction.followup.send(
                    "❌ Vault channel not found.", ephemeral=True
                )
                return

            embeds = interaction.message.embeds if interaction.message else []

            thread_name = (
                interaction.channel.name.replace("[PENDING]", "[REGISTERED]")
                if interaction.channel
                else f"Character {updated_char.name}"
            )

            vault_thread_msg = await vault_channel.create_thread(
                name=thread_name,
                content=f"Approved by {interaction.user.mention}",
                embeds=embeds,
            )

            char_update_2 = CharacterUpdate(forum_post_id=vault_thread_msg.thread.id)
            await service.update_character(self.character_id, char_update_2)

            if interaction.channel:
                await interaction.channel.edit(
                    locked=True, archived=True, name=f"[APPROVED] {updated_char.name}"
                )

            try:
                user = self.bot.get_user(
                    updated_char.discord_user_id
                ) or await self.bot.fetch_user(updated_char.discord_user_id)
                await user.send(
                    f"🎉 Your character **{updated_char.name}** has been APPROVED! Welcome to Azeroth Bound.\nSheet: {vault_thread_msg.thread.jump_url}"
                )
            except Exception as e:
                logger.warning(f"Failed to DM user: {e}")

    @discord.ui.button(
        label="Reject", style=discord.ButtonStyle.red, custom_id="officer_reject"
    )
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        if not await self.check_permissions(interaction):
            return

        modal = ReasonModal(action="Reject")
        await interaction.response.send_modal(modal)
        await modal.wait()

        reason = modal.reason_value
        if not reason:
            return

        await self.reject_logic(interaction, reason)

    async def reject_logic(self, interaction: discord.Interaction, reason: str):
        _, session_maker = get_engine_and_session_maker()
        async with session_maker() as session:
            service = CharacterService(session)

            from models.pydantic_models import CharacterUpdate

            char_update = CharacterUpdate(status=CharacterStatusEnum.REJECTED)
            updated_char = await service.update_character(
                self.character_id, char_update
            )

            if not updated_char:
                return

            if interaction.channel:
                await interaction.channel.edit(
                    locked=True, archived=True, name=f"[REJECTED] {updated_char.name}"
                )

            try:
                user = self.bot.get_user(
                    updated_char.discord_user_id
                ) or await self.bot.fetch_user(updated_char.discord_user_id)
                await user.send(
                    f"❌ Your character **{updated_char.name}** was REJECTED.\nReason: {reason}"
                )
            except Exception as e:
                logger.warning(f"Failed to DM user: {e}")

    @discord.ui.button(
        label="Request Edit",
        style=discord.ButtonStyle.secondary,
        custom_id="officer_request_edit",
    )
    async def request_edit_button(
        self, interaction: discord.Interaction, button: Button
    ):
        if not await self.check_permissions(interaction):
            return

        modal = ReasonModal(action="Request Edit")
        await interaction.response.send_modal(modal)
        await modal.wait()

        reason = modal.reason_value
        if not reason:
            return

        await self.request_edit_logic(interaction, reason)

    async def request_edit_logic(self, interaction: discord.Interaction, reason: str):
        _, session_maker = get_engine_and_session_maker()
        async with session_maker() as session:
            service = CharacterService(session)
            char = await service.get_character_by_id(self.character_id)
            if not char:
                return

            try:
                user = self.bot.get_user(
                    char.discord_user_id
                ) or await self.bot.fetch_user(char.discord_user_id)
                await user.send(
                    f"📝 Officers have requested edits for **{char.name}**.\nFeedback: {reason}\n\nPlease verify changes in the recruitment thread or re-submit if required."
                )
                if interaction.channel:
                    await interaction.channel.send(
                        f"📝 Edit requested by {interaction.user.mention}: {reason}"
                    )
            except Exception as e:
                logger.warning(f"Failed to DM user: {e}")
