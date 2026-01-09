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
    def __init__(self, bot, character_id: int = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.character_id = character_id  # Can be None for registered persistent views
        self.settings = get_settings()

    async def _get_character_id_from_context(
        self, interaction: discord.Interaction
    ) -> int:
        """
        Get character_id from interaction context.
        For persistent views after bot restart, character_id comes from the thread/message.
        """
        # If character_id was passed during init (normal flow), use it
        if self.character_id:
            return self.character_id

        # Otherwise, look it up from the recruitment thread/message
        from db.database import get_engine_and_session_maker
        from services.character_service import CharacterService

        _, session_maker = get_engine_and_session_maker()
        async with session_maker() as session:
            service = CharacterService(session)

            # Try to find character by recruitment_msg_id (which is the thread ID for forum posts)
            if interaction.channel:
                char = await service.get_character_by_recruitment_msg_id(
                    interaction.channel.id
                )
                if char:
                    return char.id

            # Fallback: try interaction.message.id
            if interaction.message:
                char = await service.get_character_by_recruitment_msg_id(
                    interaction.message.id
                )
                if char:
                    return char.id

        raise ValueError("Could not determine character_id from interaction context")

    async def check_permissions(self, interaction: discord.Interaction) -> bool:
        user_roles = [r.id for r in interaction.user.roles]
        allowed_roles = self.settings.OFFICER_ROLE_IDS

        # If roles are configured (any non-zero role ID), enforce the check
        # If all roles are 0 or empty (not configured), allow @everyone
        roles_configured = any(role_id != 0 for role_id in allowed_roles)

        if roles_configured and not any(rid in user_roles for rid in allowed_roles):
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

        try:
            await interaction.response.defer()
        except discord.errors.InteractionResponded:
            logger.warning("Interaction already responded to, using followup instead")
            # Interaction already responded, this is fine - continue with followup
        except Exception as e:
            logger.error(f"Failed to defer interaction: {e}", exc_info=True)
            return

        try:
            # Get character_id from context (supports persistent views after bot restart)
            character_id = await self._get_character_id_from_context(interaction)

            _, session_maker = get_engine_and_session_maker()
            async with session_maker() as session:
                service = CharacterService(session)

                from models.pydantic_models import CharacterUpdate

                char_update = CharacterUpdate(status=CharacterStatusEnum.REGISTERED)

                updated_char = await service.update_character(character_id, char_update)
                await session.commit()

                if not updated_char:
                    await interaction.followup.send(
                        "❌ Character not found in DB.", ephemeral=True
                    )
                    return

                logger.info(
                    f"Character {updated_char.name} (ID: {character_id}) approved by {interaction.user.name}"
                )

                vault_channel_id = self.settings.CHARACTER_SHEET_VAULT_CHANNEL_ID
                vault_channel = self.bot.get_channel(
                    vault_channel_id
                ) or await self.bot.fetch_channel(vault_channel_id)

                if not vault_channel:
                    await interaction.followup.send(
                        "❌ Vault channel not found.", ephemeral=True
                    )
                    return

                # Collect ALL embeds from the recruitment thread, not just the starter message
                all_embeds = []
                if interaction.channel:
                    # Fetch all messages in the thread to get all embeds
                    async for message in interaction.channel.history(limit=100):
                        if message.embeds:
                            all_embeds.extend(message.embeds)
                    # Reverse to get original order (history gives newest first)
                    all_embeds.reverse()

                # Fallback to starter message embeds if thread fetch fails
                if not all_embeds and interaction.message:
                    all_embeds = interaction.message.embeds

                thread_name = (
                    interaction.channel.name.replace("[PENDING]", "[REGISTERED]")
                    if interaction.channel
                    else f"Character {updated_char.name}"
                )

                # Post all embeds to vault - first embed in thread creation, rest as follow-up
                if all_embeds:
                    vault_thread_msg = await vault_channel.create_thread(
                        name=thread_name,
                        content=f"Approved by {interaction.user.mention}",
                        embed=all_embeds[0] if len(all_embeds) > 0 else None,
                    )
                    # Post remaining embeds as follow-up messages
                    if len(all_embeds) > 1:
                        await vault_thread_msg.thread.send(embeds=all_embeds[1:])
                else:
                    vault_thread_msg = await vault_channel.create_thread(
                        name=thread_name,
                        content=f"Approved by {interaction.user.mention}",
                    )

                char_update_2 = CharacterUpdate(
                    forum_post_id=vault_thread_msg.thread.id
                )
                await service.update_character(character_id, char_update_2)
                await session.commit()

                logger.info(
                    f"Posted {len(all_embeds)} embeds to character-sheet-vault for {updated_char.name}"
                )

                # Remove buttons from the recruitment message
                if interaction.message:
                    await interaction.message.edit(view=None)
                    logger.info(
                        f"Removed buttons from recruitment message for {updated_char.name}"
                    )

                # Lock and archive the recruitment thread
                if interaction.channel:
                    await interaction.channel.edit(
                        locked=True,
                        archived=True,
                        name=f"[APPROVED] {updated_char.name}",
                    )
                    logger.info(
                        f"Locked and archived recruitment thread for {updated_char.name}"
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
        except Exception as e:
            logger.error(f"Error in approve_logic: {e}", exc_info=True)
            try:
                await interaction.followup.send(
                    f"❌ An error occurred during approval: {str(e)}", ephemeral=True
                )
            except Exception:
                logger.error("Failed to send error message to user")

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
        # Get character_id from context (supports persistent views after bot restart)
        character_id = await self._get_character_id_from_context(interaction)

        _, session_maker = get_engine_and_session_maker()
        async with session_maker() as session:
            service = CharacterService(session)

            from models.pydantic_models import CharacterUpdate

            char_update = CharacterUpdate(status=CharacterStatusEnum.REJECTED)
            updated_char = await service.update_character(character_id, char_update)
            await session.commit()

            if not updated_char:
                return

            logger.info(
                f"Character {updated_char.name} (ID: {character_id}) rejected by {interaction.user.name}. Reason: {reason}"
            )

            # Remove buttons from the recruitment message
            if interaction.message:
                await interaction.message.edit(view=None)
                logger.info(
                    f"Removed buttons from recruitment message for {updated_char.name}"
                )

            # Lock and archive the recruitment thread
            if interaction.channel:
                await interaction.channel.edit(
                    locked=True, archived=True, name=f"[REJECTED] {updated_char.name}"
                )
                logger.info(
                    f"Locked and archived recruitment thread for {updated_char.name}"
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
        # Get character_id from context (supports persistent views after bot restart)
        character_id = await self._get_character_id_from_context(interaction)

        _, session_maker = get_engine_and_session_maker()
        async with session_maker() as session:
            service = CharacterService(session)
            char = await service.get_character_by_id(character_id)
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
