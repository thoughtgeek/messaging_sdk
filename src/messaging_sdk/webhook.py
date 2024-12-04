import hmac
import hashlib
from typing import Union

from fastapi import FastAPI, Request, HTTPException

from .models import WebhookEvent

class WebhookHandler:
    def __init__(self, webhook_secret: str):
        """Initialize the webhook handler.

        Args:
            webhook_secret: The secret used to verify webhook signatures
        """
        self.webhook_secret = webhook_secret

    def verify_signature(self, signature: str, payload: Union[str, bytes]) -> bool:
        """Verify the webhook signature.

        Args:
            signature: The signature from the Authorization header
            payload: The raw request payload

        Returns:
            bool: True if the signature is valid
        """
        if isinstance(payload, str):
            payload = payload.encode()

        computed = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed, signature)

def create_webhook_app(webhook_secret: str) -> FastAPI:
    """Create a FastAPI application for handling webhooks.

    Args:
        webhook_secret: The secret used to verify webhook signatures

    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI()
    handler = WebhookHandler(webhook_secret)

    @app.post("/webhooks")
    async def handle_webhook(request: Request):
        signature = request.headers.get("Authorization")
        if not signature:
            raise HTTPException(status_code=401, detail="No signature provided")

        body = await request.body()
        if not handler.verify_signature(signature, body):
            raise HTTPException(status_code=401, detail="Invalid signature")

        event = WebhookEvent.model_validate_json(body)
        print(f"Received webhook event: {event.model_dump_json()}")
        return {"status": "ok"}

    return app
