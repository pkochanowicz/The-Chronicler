# commands/talent_commands.py
import discord
from discord import app_commands
from services.sheets_service import google_sheets_service

# Instantiate the service
sheets_service = google_sheets_service

class TalentCommands(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, name="talent", description="Commands for talent management and auditing.")

    @app_commands.command(name="audit", description="Audit a character's talent build.")
    async def audit(self, interaction: discord.Interaction, character_name: str, level: int, talents_json: str):
        await interaction.response.defer(ephemeral=True)

        try:
            # Retrieve character from sheets to get its class
            character_data = sheets_service.get_character_by_name(character_name)
            if not character_data:
                await interaction.followup.send(f"Character '{character_name}' not found.", ephemeral=True)
                return
            
            char_class = character_data.get("class")
            if not char_class:
                await interaction.followup.send(f"Could not determine class for character '{character_name}'.", ephemeral=True)
                return

            # Parse talents_json input
            try:
                talents_dict = json.loads(talents_json)
                if not isinstance(talents_dict, dict):
                    raise ValueError("Talents must be a JSON object (dictionary).")
                # Ensure ranks are integers
                for talent, ranks in talents_dict.items():
                    if not isinstance(ranks, int) or ranks <= 0:
                        raise ValueError(f"Ranks for talent '{talent}' must be a positive integer.")

            except (json.JSONDecodeError, ValueError) as e:
                await interaction.followup.send(f"Invalid talents_json format: {e}. Please provide talents as a JSON object, e.g., '{{\"Improved Heroic Strike\": 3, \"Tactical Mastery\": 5}}'.", ephemeral=True)
                return
            
            # Perform validation
            validate_talents(char_class, level, talents_dict)

            # If validation passes
            embed = discord.Embed(
                title=f"Talent Audit for {character_name} ({char_class}, Lvl {level})",
                description="✅ Your talent build is valid!",
                color=discord.Color.green()
            )
            for talent_name, ranks in talents_dict.items():
                embed.add_field(name=talent_name, value=f"Ranks: {ranks}", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)

        except ValidationError as e:
            await interaction.followup.send(f"❌ Talent Validation Error: {e}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An unexpected error occurred during audit: {e}", ephemeral=True)

async def setup(bot):
    bot.tree.add_command(TalentCommands())
