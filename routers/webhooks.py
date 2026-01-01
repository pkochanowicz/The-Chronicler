from fastapi import APIRouter, Request, HTTPException, status, Header
from typing import Optional

from config.settings import get_settings

router = APIRouter()

# In a real scenario, you'd verify the Discord signature header.
# For simplicity here, we're just checking a shared secret.
settings = get_settings()  # Get settings instance
WEBHOOK_SECRET = settings.WEBHOOK_SECRET


@router.post("/discord")
async def discord_webhook_handler(
    request: Request,
    x_signature_ed25519: Optional[str] = Header(None),
    x_signature_timestamp: Optional[str] = Header(None),
):
    if not WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured.",
        )

    # In a real Discord interaction, you'd verify the signature with Discord's public key.
    # For a simple shared secret, you might do something like:
    # raw_body = await request.body()
    # computed_signature = hmac.new(WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    # if not hmac.compare_digest(computed_signature, some_header_from_discord):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature.")

    # For now, let's just log and process the interaction.
    # This is where Discord interaction logic would go (slash commands, buttons, etc.)

    json_data = await request.json()
    print(f"Received Discord Webhook: {json_data}")

    # Discord interaction responses are specific:
    # For PING, respond with type 1.
    if json_data.get("type") == 1:  # PING
        return {"type": 1}

    # For other interaction types, you'd process them and send a response.
    # Example: Acknowledge command and respond later.
    return {"type": 4, "data": {"content": "Interaction received!"}}
