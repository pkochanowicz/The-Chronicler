import discord
from discord import app_commands
from services.bank_service import guild_bank_service

class BankCommands(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, name="bank", description="Commands for the guild bank.")

    @app_commands.command(name="deposit", description="Deposit an item into the guild bank.")
    async def deposit(self, interaction: discord.Interaction, item: str, quantity: int, category: str = "Other", notes: str = ""):
        await interaction.response.defer(ephemeral=True)
        
        depositor_id = str(interaction.user.id)
        depositor_name = interaction.user.display_name
        
        if guild_bank_service.deposit_item(item, quantity, depositor_id, depositor_name, category, notes):
            await interaction.followup.send(f"✅ Successfully deposited **{quantity}x {item}** into the guild bank.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Failed to deposit item into the guild bank.", ephemeral=True)

    @app_commands.command(name="withdraw", description="Withdraw an item from the guild bank (by Item ID).")
    async def withdraw(self, interaction: discord.Interaction, item_id: str):
        await interaction.response.defer(ephemeral=True)
        
        withdrawer_id = str(interaction.user.id)
        withdrawer_name = interaction.user.display_name
        
        if guild_bank_service.withdraw_item(item_id, withdrawer_id, withdrawer_name):
             await interaction.followup.send(f"✅ Successfully withdrawn item ID `{item_id}`.", ephemeral=True)
        else:
             await interaction.followup.send(f"❌ Failed to withdraw item `{item_id}`. Check if ID exists and is available.", ephemeral=True)

    @app_commands.command(name="view", description="View available items in the guild bank.")
    async def view(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        items = guild_bank_service.get_available_items()
        
        if not items:
            await interaction.followup.send("The guild bank is empty.", ephemeral=True)
            return

        # Simple aggregation for view
        inventory = {}
        for item in items:
            name = item.get("item_name")
            qty = int(item.get("quantity", 0))
            inventory[name] = inventory.get(name, 0) + qty

        embed = discord.Embed(title="🏦 Guild Bank Inventory", color=discord.Color.gold())
        description = ""
        for name, qty in inventory.items():
            description += f"• **{name}**: {qty}\n"
        
        if len(description) > 4000:
            description = description[:3900] + "... (truncated)"
            
        embed.description = description
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    @app_commands.command(name="mydeposits", description="View items you have deposited.")
    async def mydeposits(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        items = guild_bank_service.get_member_deposits(str(interaction.user.id))
        
        if not items:
             await interaction.followup.send("You haven't deposited any items.", ephemeral=True)
             return
             
        embed = discord.Embed(title=f"📦 Deposits by {interaction.user.display_name}", color=discord.Color.blue())
        desc = ""
        for item in items[:20]: # Limit to last 20
             status_icon = "✅" if item.get("status") == "AVAILABLE" else "❌"
             desc += f"{status_icon} **{item.get('quantity')}x {item.get('item_name')}** (ID: `{item.get('item_id')}`)\n"
        
        embed.description = desc
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    bot.tree.add_command(BankCommands())