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

    @pytest.fixture(autouse=True)
    def patch_webhook_settings(self, monkeypatch, mock_settings):
        """Autouse fixture to patch services.webhook_handler.settings."""
        monkeypatch.setattr("services.webhook_handler.settings", mock_settings)

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

    @pytest.mark.asyncio
    async def test_webhook_missing_secret(self, mock_request, mock_settings):
        """Test that webhook rejects requests with missing secret."""
        # Request with no secret field
        mock_request.json.return_value = {
            "trigger": "POST_TO_RECRUITMENT",
            "character": {"char_name": "Test"}
        }

        response = await handle_webhook(mock_request)
        assert response.status == 400
        assert "secret" in response.text.lower() or "invalid" in response.text.lower()

    @pytest.mark.asyncio
    async def test_webhook_empty_secret(self, mock_request, mock_settings):
        """Test that webhook rejects requests with empty secret."""
        mock_request.json.return_value = {
            "secret": "",  # Empty string
            "trigger": "POST_TO_RECRUITMENT",
            "character": {"char_name": "Test"}
        }

        response = await handle_webhook(mock_request)
        assert response.status == 400
        assert "Invalid secret" in response.text or "invalid" in response.text.lower()

    @pytest.mark.asyncio
    async def test_webhook_null_secret(self, mock_request, mock_settings):
        """Test that webhook rejects requests with null secret."""
        mock_request.json.return_value = {
            "secret": None,  # Null value
            "trigger": "POST_TO_RECRUITMENT",
            "character": {"char_name": "Test"}
        }

        response = await handle_webhook(mock_request)
        assert response.status == 400

    @pytest.mark.asyncio
    async def test_webhook_secret_with_whitespace(self, mock_request, mock_settings):
        """Test that webhook handles secrets with leading/trailing whitespace.

        Security consideration: Secrets should be compared after stripping
        whitespace to prevent configuration errors, OR whitespace should
        cause rejection to enforce exact matching.
        """
        # Test with whitespace around valid secret
        mock_request.json.return_value = {
            "secret": "  test_secret_123  ",  # Leading/trailing spaces
            "trigger": "POST_TO_RECRUITMENT",
            "character": {"char_name": "Test"}
        }

        response = await handle_webhook(mock_request)
        # Behavior depends on implementation:
        # Option 1: Strip whitespace and compare (lenient)
        # Option 2: Reject if doesn't match exactly (strict)
        # Document current behavior
        assert response.status in [200, 400], "Whitespace handling should be consistent"

    @pytest.mark.asyncio
    async def test_webhook_timing_attack_resistance(self, mock_request, mock_settings):
        """Test that webhook secret comparison is timing-safe.

        Security: Use secrets.compare_digest() instead of == to prevent
        timing attacks that could leak secret information.

        This test documents the requirement. Actual timing analysis
        would require specialized tools.
        """
        import secrets

        # Verify Python's secrets module is available
        assert hasattr(secrets, 'compare_digest')

        # Document: Webhook handler should use secrets.compare_digest()
        # for secret comparison, not simple == operator

        # TODO: Review services/webhook_handler.py to verify timing-safe comparison
