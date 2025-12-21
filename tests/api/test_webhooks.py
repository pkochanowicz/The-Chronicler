import pytest
from httpx import AsyncClient
from main import app
from fastapi.testclient import TestClient



@pytest.mark.asyncio
async def test_discord_webhook_ping(client: TestClient):
    # Simulate a Discord PING interaction
    payload = {
        "id": "1234567890",
        "token": "a_token",
        "type": 1, # PING type
        "version": 1
    }
    headers = {
        "X-Signature-Ed25519": "dummy_signature", # Placeholder, real signature would be verified by Discord.
        "X-Signature-Timestamp": "1678886400" # Placeholder timestamp
    }
    response = await async_client.post("/webhooks/discord", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"type": 1}

@pytest.mark.asyncio
async def test_discord_webhook_other_interaction(client: TestClient):
    # Simulate another interaction type (e.g., slash command)
    payload = {
        "id": "0987654321",
        "token": "another_token",
        "type": 2, # APPLICATION_COMMAND type
        "version": 1,
        "data": {
            "id": "command_id",
            "name": "my_command",
            "options": []
        }
    }
    headers = {
        "X-Signature-Ed25519": "dummy_signature_2",
        "X-Signature-Timestamp": "1678886500"
    }
    response = await async_client.post("/webhooks/discord", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"type": 4, "data": {"content": "Interaction received!"}}

