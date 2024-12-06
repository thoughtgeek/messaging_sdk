# Messaging SDK

A Python SDK for interacting with the Messaging API. This SDK provides a simple interface for sending messages, managing contacts, and handling webhook events.

## Installation

```bash
pip install messaging-sdk
```
## Quick Start


```python
from messaging_sdk.client import MessagingClient
from messaging_sdk.webhook import create_webhook_server

# Initialize the client
client = MessagingClient(
    api_key="your-api-key",
    webhook_secret="mySecret",
    base_url="http://localhost:3000"
)

# Create a contact
contact = client.create_contact(
    name="John Doe",
    phone="+1234567890"
)

# Send a message
message = client.send_message(
    from_number="+1122334455",
    to_contact=contact.id,
    content="Hello from the Messaging SDK!"
)

# Set up webhook server
app = create_webhook_server(client)
app.run(host='0.0.0.0', port=3010)
```

## Managing contacts

```python
# Create a contact
contact = client.create_contact(
    name="Alice Smith",
    phone="+1234567890"
)

# List contacts with pagination
contacts = client.list_contacts(pageIndex=1, max=10)

# Get a specific contact
contact = client.get_contact(contact_id="contact123")

# Update a contact
updated = client.update_contact(
    contact_id="contact123",
    name="Alice Johnson"
)

# Delete a contact
client.delete_contact(contact_id="contact123")
```

## Sending messages

```python
# Send to a contact by ID
message = client.send_message(
    from_number="+1122334455",
    to_contact="contact123",
    content="Hello!"
)

# Send to a new contact directly
message = client.send_message(
    from_number="+1122334455",
    to_contact={
        "name": "Bob",
        "phone": "+1234567890"
    },
    content="Hello new contact!"
)

# List messages with pagination
messages = client.list_messages(page=1, limit=10)

# Get a specific message
message = client.get_message(message_id="msg123")
```

## Handling webhook events

```python
from messaging_sdk.webhook import create_webhook_server

def run_webhook_server():
    client = MessagingClient(
        api_key="your-api-key",
        webhook_secret="mySecret"
    )
    
    app = create_webhook_server(client)
    app.run(host='0.0.0.0', port=3010)

# Run in a separate thread or process
run_webhook_server()
```
Verifying webhook signatures

```python
# Verify a webhook signature
client = MessagingClient(
    api_key="your-api-key",
    webhook_secret="mySecret"
)

# Example webhook payload
webhook_body = {
    "id": "msg123",
    "status": "delivered",
    "delivered_at": "2023-10-20T10:00:00Z"
}

# Example signature from Authorization header
signature = "Signature 730024e1e304078f29747bc54a02271bfcf1e9f50b58e29154116daf2bd7a967"

# Verify the signature
is_valid = client.verify_webhook_signature(signature, webhook_body)
if is_valid:
    print("Webhook signature is valid")
else:
    print("Invalid webhook signature")

```