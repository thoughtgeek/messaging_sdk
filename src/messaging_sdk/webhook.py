import logging
from flask import Flask, request, Response
from .client import MessagingClient
from .models import WebhookEvent

def create_webhook_server(client: MessagingClient, host: str = 'localhost', port: int = 3010) -> Flask:
    """Create a Flask server to handle webhook events.

    Args:
        client: MessagingClient instance for signature verification
        host: Host to bind the server to
        port: Port to listen on

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    @app.route('/webhooks', methods=['POST'])
    def handle_webhook():
        # Get signature from Authorization header
        signature = request.headers.get('Authorization')

        if not signature:
            return Response('Missing signature', status=401)

        # Verify signature
        if not client.verify_webhook_signature(signature, request.get_data()):
            return Response('Invalid signature', status=401)

        # Parse and handle the event
        event_data = request.get_json()
        event = WebhookEvent(**event_data)
        print(f"Received webhook event: {event}")

        return Response(status=200)

    return app
