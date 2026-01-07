import discord
from discord import app_commands
from services.bank_service import GuildBankService
from db.database import get_engine_and_session_maker
import logging

logger = logging.getLogger(__name__)


class BankCommands(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, **kwargs, name="bank", description="Commands for the guild bank."
        )
        self.session_maker = None

    def _get_session_maker(self):
        if not self.session_maker:
            _, self.session_maker = get_engine_and_session_maker()
        return self.session_maker

    @app_commands.command(
        name="deposit", description="Deposit an item into the guild bank."
    )
    @app_commands.describe(
        item="The exact name of the item",
        quantity="Amount to deposit",
        category="Category (e.g. Materials, Consumables)",
        notes="Optional notes",
    )
    async def deposit(
        self,
        interaction: discord.Interaction,
        item: str,
        quantity: int,
        category: str = "General",
        notes: str = "",
    ):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        session_maker = self._get_session_maker()

        async with session_maker() as session:
            service = GuildBankService(session)
            try:
                success = await service.deposit_item(
                    user_id, item, quantity, category, notes
                )
                if success:
                    await interaction.followup.send(
                        f"✅ Successfully deposited **{quantity}x {item}** into the guild bank.",
                        ephemeral=True,
                    )
            except ValueError as e:
                await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
            except Exception as e:
                logger.error(f"Unexpected error in deposit command: {e}", exc_info=True)
                await interaction.followup.send(
                    "❌ An unexpected error occurred.", ephemeral=True
                )

    @app_commands.command(
        name="withdraw",
        description="Withdraw an item from the guild bank (by Item ID).",
    )
    @app_commands.describe(item_id="The numeric ID of the item to withdraw")
    async def withdraw(self, interaction: discord.Interaction, item_id: int):
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        session_maker = self._get_session_maker()

        async with session_maker() as session:
            service = GuildBankService(session)
            try:
                success = await service.withdraw_item(
                    user_id, item_id, 1
                )  # Default to 1 for now or add quantity param
                if success:
                    await interaction.followup.send(
                        f"✅ Successfully withdrawn 1x Item `{item_id}`.",
                        ephemeral=True,
                    )
            except ValueError as e:
                await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
            except Exception as e:
                logger.error(
                    f"Unexpected error in withdraw command: {e}", exc_info=True
                )
                await interaction.followup.send(
                    "❌ An unexpected error occurred.", ephemeral=True
                )

    @app_commands.command(
        name="view", description="View available items in the guild bank."
    )
    async def view(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        session_maker = self._get_session_maker()

        async with session_maker() as session:
            service = GuildBankService(session)
            items = await service.get_all_items()

            if not items:
                await interaction.followup.send(
                    "The guild bank is empty.", ephemeral=True
                )
                return

            embed = discord.Embed(
                title="🏦 Guild Bank Inventory", color=discord.Color.gold()
            )

            # Aggregate by category
            categories = {}
            for bank_item, item_obj in items:
                cat = bank_item.category
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(
                    f"• **{item_obj.name}**: {bank_item.count} (ID: {bank_item.item_id})"
                )

            for cat, lines in categories.items():
                # naive chunking
                chunk = "\n".join(lines)
                if len(chunk) > 1024:
                    chunk = chunk[:1020] + "..."
                embed.add_field(name=cat, value=chunk, inline=False)

            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="mydeposits", description="View your recent deposits.")
    async def mydeposits(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        session_maker = self._get_session_maker()

        async with session_maker() as session:
            service = GuildBankService(session)
            deposits = await service.get_member_deposits(interaction.user.id)

            if not deposits:
                await interaction.followup.send(
                    "You haven't deposited any items recently.", ephemeral=True
                )
                return

            embed = discord.Embed(
                title=f"📦 Recent Deposits by {interaction.user.display_name}",
                color=discord.Color.blue(),
            )
            desc = ""
            for tx, item_obj in deposits:
                desc += f"✅ **{tx.quantity}x {item_obj.name}** at {tx.timestamp.strftime('%Y-%m-%d %H:%M')}\n"

            embed.description = desc
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    bot.tree.add_command(BankCommands())
