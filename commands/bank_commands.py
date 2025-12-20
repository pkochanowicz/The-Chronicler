import discord
from discord import app_commands
from services.bank_service import BankService

bank_service = BankService()

class BankCommands(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, name="bank", description="Commands for the guild bank.")

    @app_commands.command(name="deposit", description="Deposit an item into the guild bank.")
    async def deposit(self, interaction: discord.Interaction, item: str, quantity: int, notes: str = ""):
        member = interaction.user.display_name
        if bank_service.log_transaction(member, "deposit", item, quantity, notes):
            await interaction.response.send_message(f"Successfully deposited {quantity}x {item} into the guild bank.", ephemeral=True)
        else:
            await interaction.response.send_message("Failed to deposit item into the guild bank.", ephemeral=True)

    @app_commands.command(name="view", description="View the guild bank's inventory.")
    async def view(self, interaction: discord.Interaction):
        transactions = bank_service.get_all_transactions()
        if not transactions:
            await interaction.response.send_message("The guild bank is empty.", ephemeral=True)
            return

        embed = discord.Embed(title="Guild Bank Inventory", color=discord.Color.gold())
        
        # This is a very simple view, just showing the last 10 transactions.
        # A proper implementation would aggregate the items.
        inventory = {}
        for transaction in transactions:
            item = transaction.get("item")
            quantity = transaction.get("quantity", 0)
            transaction_type = transaction.get("transaction_type")

            if transaction_type == "deposit":
                inventory[item] = inventory.get(item, 0) + quantity
            elif transaction_type == "withdrawal":
                inventory[item] = inventory.get(item, 0) - quantity

        for item, quantity in inventory.items():
            if quantity > 0:
                embed.add_field(
                    name=item,
                    value=f"Quantity: {quantity}",
                    inline=True
                )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    bot.tree.add_command(BankCommands())
