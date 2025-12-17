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
from unittest.mock import AsyncMock, patch, MagicMock
from services.webhook_handler import handle_webhook

class TestWebhooks:
    """
    Tests for Webhook Handler endpoint and trigger logic.
    """

    @pytest.fixture
    def mock_request(self):
        req = MagicMock()
        req.json = AsyncMock()
        return req

    @pytest.mark.asyncio
    async def test_webhook_invalid_secret(self, mock_request, mock_settings):
        """Test 400 response on invalid secret."""
        mock_request.json.return_value = {"secret": "wrong_secret"}
        
        response = await handle_webhook(mock_request)
        assert response.status == 400
        assert "Invalid secret" in response.text

    @pytest.mark.asyncio
    async def test_trigger_post_to_recruitment(self, mock_request, mock_settings):
        """Test POST_TO_RECRUITMENT trigger."""
        payload = {
            "secret": "test_secret_123", # Matches mock_settings
            "trigger": "POST_TO_RECRUITMENT",
            "character": {"char_name": "Thorgar", "status": "PENDING"}
        }
        mock_request.json.return_value = payload
        
        with patch("services.webhook_handler.handle_post_to_recruitment", new_callable=AsyncMock) as mock_handler:
            response = await handle_webhook(mock_request)
            assert response.status == 200
            mock_handler.assert_called_once_with(payload["character"])

    @pytest.mark.asyncio
    async def test_trigger_initiate_burial(self, mock_request, mock_settings):
        """Test INITIATE_BURIAL trigger."""
        payload = {
            "secret": "test_secret_123",
            "trigger": "INITIATE_BURIAL",
            "character": {"char_name": "Thorgar", "status": "DECEASED"}
        }
        mock_request.json.return_value = payload
        
        with patch("services.webhook_handler.handle_initiate_burial", new_callable=AsyncMock) as mock_handler:
            response = await handle_webhook(mock_request)
            assert response.status == 200
            mock_handler.assert_called_once_with(payload["character"])

    @pytest.mark.asyncio
    async def test_unknown_trigger(self, mock_request, mock_settings):
        """Test 400 response on unknown trigger."""
        payload = {
            "secret": "test_secret_123",
            "trigger": "UNKNOWN_TRIGGER"
        }
        mock_request.json.return_value = payload
        
        response = await handle_webhook(mock_request)
        assert response.status == 400
        assert "Unknown trigger" in response.text
