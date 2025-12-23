import pytest
# from httpx import AsyncClient # No longer needed

@pytest.mark.asyncio
async def test_discord_webhook_ping(client):
    """Test that the webhook endpoint correctly handles Discord PING events."""
    # async_client = await async_client_fixture # No longer needed
    payload = {
        "id": "1234567890",
        "token": "a_token",
        "type": 1, # PING type
        "version": 1
    }
    # Mock headers (in a real scenario, middleware would validate signature)
    headers = {
        "X-Signature-Ed25519": "dummy_signature",
        "X-Signature-Timestamp": "1678886400"
    }
    
    response = client.post("/webhooks/discord", json=payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {"type": 1}

@pytest.mark.asyncio
async def test_discord_webhook_other_interaction(client):
    """Test that the webhook endpoint acknowledges other interaction types."""
    # async_client = await async_client_fixture # No longer needed
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
    
    response = client.post("/webhooks/discord", json=payload, headers=headers)
    
    assert response.status_code == 200
    # Currently just acknowledges
    assert response.json() == {"type": 4, "data": {"content": "Interaction received!"}}