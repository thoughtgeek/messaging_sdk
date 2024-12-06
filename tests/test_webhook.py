import pytest
import json
import hmac
import hashlib
from messaging_sdk.client import MessagingClient
from messaging_sdk.webhook import create_webhook_server

@pytest.fixture
def client():
    return MessagingClient(
        api_key="test-key",
        webhook_secret="mySecret"
    )

@pytest.fixture
def app(client):
    return create_webhook_server(client)

def test_webhook_signature_verification(client):
    # Test payload
    payload = {
        "id": "msg123",
        "status": "delivered",
        "delivered_at": "2023-10-20T10:00:00Z"
    }
    body = json.dumps(payload).encode()

    # Generate signature
    signature = hmac.new(
        b"mySecret",
        body,
        hashlib.sha256
    ).hexdigest()

    # Verify signature
    assert client.verify_webhook_signature(signature, body) == True

def test_webhook_endpoint(client, app):
    with app.test_client() as test_client:
        # Test payload
        payload = {
            "id": "msg123",
            "status": "delivered",
            "delivered_at": "2023-10-20T10:00:00Z"
        }
        body = json.dumps(payload).encode()

        # Generate signature
        signature = hmac.new(
            b"mySecret",
            body,
            hashlib.sha256
        ).hexdigest()

        # Send request
        response = test_client.post(
            '/webhooks',
            data=body,
            headers={'Authorization': signature},
            content_type='application/json'
        )

        assert response.status_code == 200
