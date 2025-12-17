# Azeroth Bound Discord Bot
# Copyright (C) 2025 [Paweł Kochanowicz - <github.com/pkochanowicz> ]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest
import datetime
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_settings(mocker):
    """Mock configuration settings"""
    # Patch the singleton instance attributes
    mocker.patch("config.settings.settings.WEBHOOK_SECRET", "test_secret_123")
    mocker.patch("config.settings.settings.DEFAULT_PORTRAIT_URL", "https://example.com/default.png")
    return mocker

@pytest.fixture
def sample_character_data():
    """Returns a dictionary with valid sample character data (27 columns)"""
    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "discord_id": "123456789",
        "discord_name": "TestUser#1234",
        "char_name": "Thorgar",
        "race": "Dwarf",
        "class": "Warrior",
        "roles": "Tank, Melee DPS",
        "professions": "Mining, Blacksmithing",
        "backstory": "A brave warrior from the mountains.",
        "personality": "Stubborn but loyal.",
        "quotes": "For Khaz Modan!",
        "portrait_url": "https://example.com/thorgar.png",
        "trait_1": "Brave",
        "trait_2": "Loyal",
        "trait_3": "Stubborn",
        "status": "PENDING",
        "confirmation": True,
        "request_sdxl": False,
        "recruitment_msg_id": "987654321",
        "forum_post_url": "https://discord.com/channels/1/2/3",
        "reviewed_by": "999888777",
        "embed_json": '[{"title": "Thorgar"}]',
        "death_cause": None,
        "death_story": None,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat(),
        "notes": "Test notes"
    }

@pytest.fixture
def mock_discord_interaction():
    """Mocks a Discord interaction object"""
    interaction = AsyncMock()
    interaction.user.id = 123456789
    interaction.user.name = "TestUser"
    interaction.user.discriminator = "1234"
    interaction.user.mention = "<@123456789>"
    interaction.guild.id = 555555
    interaction.channel_id = 444444
    
    # Mock response
    interaction.response = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()
    
    return interaction

@pytest.fixture
def mock_sheets_client():
    """Mocks the Google Sheets client"""
    client = MagicMock()
    sheet = MagicMock()
    client.open_by_key.return_value.sheet1 = sheet
    return client

@pytest.fixture
def valid_races():
    return [
        "Human", "Dwarf", "Night Elf", "Gnome", "High Elf",
        "Orc", "Undead", "Tauren", "Troll", "Goblin",
        "Other"
    ]

@pytest.fixture
def valid_classes():
    return [
        "Warrior", "Paladin", "Hunter", "Rogue", "Priest",
        "Shaman", "Mage", "Warlock", "Druid"
    ]

@pytest.fixture
def valid_roles():
    return ["Tank", "Healer", "Melee DPS", "Ranged DPS", "Support"]
