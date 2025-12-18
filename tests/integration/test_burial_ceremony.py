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
from unittest.mock import AsyncMock, MagicMock, patch, ANY

class TestBurialCeremony:
    """
    Tests for the atomic burial ceremony logic (webhook handler side).
    """

    @pytest.mark.asyncio
    async def test_burial_ceremony_steps(self, mock_sheets_client):
        """
        User Story: Officer completes burial and webhook executes final ceremony automatically.

        Flow:
        1. Webhook receives INITIATE_BURIAL trigger for deceased character
        2. Bot fetches character's forum thread from #character-vault
        3. Bot moves forum thread to #cemetery channel
        4. Bot posts death story and ceremony message to thread
        5. Character status updated to BURIED in Google Sheets
        6. All actions execute atomically as single ceremony

        Expected: Complete burial ceremony workflow automated via webhook, forum thread
        relocated, death story posted, status updated to final BURIED state.
        """
        # We need to import the handler logic (services.webhook_handler or similar)
        # Assuming logic is in services.webhook_handler.handle_initiate_burial
        
        from services.webhook_handler import handle_initiate_burial
        
        character_data = {
            "char_name": "Thorgar",
            "status": "DECEASED",
            "forum_post_url": "https://discord.com/channels/1/2/3",
            "discord_id": "12345"
        }
        
        # Mock Discord Client/Bot methods
        mock_bot = MagicMock()
        mock_bot.fetch_channel = AsyncMock()
        mock_thread = AsyncMock()
        
        # Configure get_channel to return None so it awaits fetch_channel
        mock_bot.get_channel.return_value = None
        # Configure fetch_channel to return the mock thread (acts as vault thread AND cemetery channel)
        mock_bot.fetch_channel.return_value = mock_thread
        
        # Setup create_thread return value (ThreadWithMessage mock)
        mock_new_thread_msg = MagicMock()
        mock_new_thread = AsyncMock()
        mock_new_thread_msg.thread = mock_new_thread
        mock_thread.create_thread.return_value = mock_new_thread_msg

        # Mock Sheets Service
        # We patch __init__ to avoid connection, and update_character_status to verify call
        with patch("services.sheets_service.CharacterRegistryService.__init__", return_value=None) as mock_init, \
             patch("services.sheets_service.CharacterRegistryService.update_character_status") as mock_update:
             
             # Need to inject mock_bot into the handler or patch the global 'bot' if used
             with patch("services.webhook_handler.bot", mock_bot):
                 await handle_initiate_burial(character_data)
                 
                 # Verify steps:
                 # 1. Fetch thread
                 
                 # 2. Create new thread in cemetery
                 mock_thread.create_thread.assert_called()

                 # 3. Post death story to NEW thread
                 mock_new_thread.send.assert_called()
                 
                 # 4. Update status to BURIED
                 mock_update.assert_called_with("Thorgar", "BURIED", forum_post_url=ANY, updated_at=ANY)
