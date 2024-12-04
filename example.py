# example.py

import asyncio
from messaging_sdk.client import MessagingClient
from messaging_sdk.models import Contact, Message
from messaging_sdk.webhook import create_webhook_app
import uvicorn
import threading
import time

def run_webhook_server():
    """Run the webhook server in a separate thread"""
    app = create_webhook_app(webhook_secret="mySecret")
    uvicorn.run(app, host="localhost", port=3010)

def main():
    # Initialize the client
    client = MessagingClient(
        api_key="there-is-no-key",
        base_url="http://localhost:3000"
    )

    try:
        # 1. Create a contact
        print("Creating contact...")
        contact = client.create_contact(
            name="John Doe",
            phone="+1234567890"
        )
        print(f"Created contact: {contact}")

        # 2. List all contacts
        print("\nListing contacts...")
        contacts = client.list_contacts(page=1, limit=10)
        print(f"Found {len(contacts)} contacts")
        for c in contacts:
            print(f"- Contact {c.id}: {c.name} ({c.phone})")

        # 3. Get the created contact by ID
        print("\nRetrieving contact by ID...")
        retrieved_contact = client.get_contact(contact_id=contact.id)
        print(f"Retrieved contact: {retrieved_contact}")

        # 4. Update the contact
        print("\nUpdating contact...")
        updated_contact = client.update_contact(
            contact_id=contact.id,
            name="Jane Doe",
            phone="+0987654321"
        )
        print(f"Updated contact: {updated_contact}")

        # 5. Send a message to the contact
        print("\nSending message...")
        message = client.send_message(
            from_number="+1122334455",
            to_contact=contact.id,  # Using contact ID as a string
            content="Hello from the extended SDK example!"
        )
        print(f"Sent message: {message}")

        # 6. List all messages
        print("\nListing messages...")
        messages = client.list_messages(page=1, limit=10)
        print(f"Found {len(messages)} messages")
        for msg in messages:
            print(f"- Message {msg.id}: {msg.content} (To: {msg.to}, Status: {msg.status})")

        # 7. Get the sent message by ID
        print("\nRetrieving message by ID...")
        retrieved_message = client.get_message(message_id=message.id)
        print(f"Retrieved message: {retrieved_message}")

        # 8. Delete the contact
        print("\nDeleting contact...")
        client.delete_contact(contact_id=contact.id)
        print("Contact deleted successfully")

        # 9. Attempt to get the deleted contact (should raise NotFoundError)
        print("\nAttempting to retrieve deleted contact...")
        try:
            client.get_contact(contact_id=contact.id)
        except Exception as e:
            print(f"Expected error occurred: {e}")

        # Additional: Note on webhook handling
        print("\nWebhook server is running to handle message delivery status updates.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Start webhook server in a separate thread
    webhook_thread = threading.Thread(target=run_webhook_server)
    webhook_thread.daemon = True
    webhook_thread.start()

    # Run main program
    main()