import pytest
from unittest.mock import AsyncMock, MagicMock
import discord

@pytest.fixture
def mock_interaction():
    """
    Creates a mock discord.Interaction object with all necessary attributes
    mocked for testing interactive flows.
    """
    interaction = AsyncMock(spec=discord.Interaction)
    interaction.response = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.user = MagicMock(spec=discord.User)
    interaction.user.id = 123456789
    interaction.user.name = "TestUser"
    interaction.user.discriminator = "0000"
    interaction.user.display_name = "Test User"
    interaction.guild = MagicMock(spec=discord.Guild)
    interaction.guild.id = 987654321
    interaction.channel = MagicMock(spec=discord.TextChannel)
    interaction.channel.id = 555555555
    
    # Mock client (bot)
    interaction.client = AsyncMock()
    
    return interaction

@pytest.fixture
def mock_discord_context():
    """
    Creates a mock commands.Context object.
    """
    ctx = AsyncMock()
    ctx.author.id = 123456789
    ctx.author.name = "TestUser"
    ctx.send = AsyncMock()
    return ctx
