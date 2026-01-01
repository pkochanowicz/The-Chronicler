import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_settings():
    mock = MagicMock()
    mock.WEBHOOK_SECRET = "test_secret_123"
    # Ensure all other used settings are present to avoid AttributeErrors
    mock.RECRUITMENT_CHANNEL_ID = 123
    mock.CEMETERY_CHANNEL_ID = 456
    mock.PATHFINDER_ROLE_MENTION = "<@&111>"
    mock.TRAILWARDEN_ROLE_MENTION = "<@&222>"
    mock.APPROVE_EMOJI = "✅"
    mock.REJECT_EMOJI = "❌"
    mock.PORT = 8080
    return mock


@pytest.fixture(autouse=True)
def patch_webhook_settings(monkeypatch, mock_settings):
    """Autouse fixture to patch config.settings.get_settings."""
    monkeypatch.setattr("config.settings.get_settings", lambda: mock_settings)


class TestWebhooks:
    # ... (Tests remain similar, just ensuring the patch works)

    def test_webhook_invalid_secret(self, client):
        # ...
        pass

    # ... (Other tests)
    pass
