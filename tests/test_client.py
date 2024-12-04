import pytest
from unittest.mock import Mock, patch

from messaging_sdk.client import MessagingClient
from messaging_sdk.models import Contact, Message
from messaging_sdk.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
)

# Fixture for the client instance
@pytest.fixture
def client():
    return MessagingClient(api_key="test-key", base_url="http://test-api.com")

# Helper function to create a mock response
def mock_response(status_code=200, content=None, json_data=None):
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.content = content
    if json_data is not None:
        mock_resp.json.return_value = json_data
        mock_resp.content = b'json'  # Simulate content existence
    else:
        mock_resp.json.return_value = None
    return mock_resp
# Test create_contact method
def test_create_contact(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=201,
            json_data={
                "id": "contact123",
                "name": "John Doe",
                "phone": "+1234567890",
            }
        )
        mock_session.post.return_value = mock_resp

        contact = client.create_contact(name="John Doe", phone="+1234567890")

        assert isinstance(contact, Contact)
        assert contact.id == "contact123"
        assert contact.name == "John Doe"
        assert contact.phone == "+1234567890"

# Test list_contacts method
def test_list_contacts(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "contacts": [
                    {"id": "contact1", "name": "Alice", "phone": "+1111111111"},
                    {"id": "contact2", "name": "Bob", "phone": "+2222222222"},
                ],
                "pageNumber": 1,
                "pageSize": 2,
            }
        )
        mock_session.get.return_value = mock_resp

        contacts = client.list_contacts(page=1, limit=10)

        assert isinstance(contacts, list)
        assert len(contacts) == 2
        assert contacts[0].name == "Alice"
        assert contacts[1].phone == "+2222222222"

# Test get_contact method
def test_get_contact(client):
    with patch.object(client, 'session') as mock_session:
        contact_id = "contact123"
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "id": contact_id,
                "name": "John Doe",
                "phone": "+1234567890",
            }
        )
        mock_session.get.return_value = mock_resp

        contact = client.get_contact(contact_id=contact_id)

        assert isinstance(contact, Contact)
        assert contact.id == contact_id
        assert contact.name == "John Doe"

# Test update_contact method
def test_update_contact(client):
    with patch.object(client, 'session') as mock_session:
        contact_id = "contact123"
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "id": contact_id,
                "name": "Jane Doe",
                "phone": "+0987654321",
            }
        )
        mock_session.patch.return_value = mock_resp

        updated_contact = client.update_contact(
            contact_id=contact_id,
            name="Jane Doe",
            phone="+0987654321"
        )

        assert isinstance(updated_contact, Contact)
        assert updated_contact.name == "Jane Doe"
        assert updated_contact.phone == "+0987654321"

# Test delete_contact method
def test_delete_contact(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(status_code=204)
        mock_session.delete.return_value = mock_resp

        result = client.delete_contact(contact_id="contact123")

        assert result is None

# Test send_message method with Contact ID
def test_send_message_with_contact_id(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=201,
            json_data={
                "id": "msg123",
                "from": "+1234567890",
                "to": {
                    "id": "contact123",
                    "name": "John Doe",
                    "phone": "+0987654321",
                },
                "content": "Hello, John!",
                "status": "queued",
                "createdAt": "2023-10-01T12:00:00Z",
            }
        )
        mock_session.post.return_value = mock_resp

        message = client.send_message(
            from_number="+1234567890",
            to_contact="contact123",
            content="Hello, John!"
        )

        assert isinstance(message, Message)
        assert message.id == "msg123"
        assert message.content == "Hello, John!"
        assert message.status == "queued"
        assert message.to == "contact123"
# Test list_messages method
def test_list_messages(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "messages": [
                    {
                        "id": "msg1",
                        "from": "+1234567890",
                        "to": {
                            "id": "contact1",
                            "name": "Alice",
                            "phone": "+1111111111",
                        },
                        "content": "Hi Alice!",
                        "status": "delivered",
                        "createdAt": "2023-10-01T12:00:00Z",
                    },
                    {
                        "id": "msg2",
                        "from": "+1234567890",
                        "to": {
                            "id": "contact2",
                            "name": "Bob",
                            "phone": "+2222222222",
                        },
                        "content": "Hi Bob!",
                        "status": "queued",
                        "createdAt": "2023-10-01T12:05:00Z",
                    },
                ],
                "page": 1,
                "quantityPerPage": 2,
            }
        )
        mock_session.get.return_value = mock_resp

        messages = client.list_messages(page=1, limit=10)

        assert isinstance(messages, list)
        assert len(messages) == 2
        assert messages[0].id == "msg1"
        assert messages[1].to == "contact2"

# Test get_message method
def test_get_message(client):
    with patch.object(client, 'session') as mock_session:
        message_id = "msg123"
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "id": message_id,
                "from": "+1234567890",
                "to": {
                    "id": "contact123",
                    "name": "John Doe",
                    "phone": "+0987654321",
                },
                "content": "Hello, John!",
                "status": "queued",
                "createdAt": "2023-10-01T12:00:00Z",
                "deliveredAt": None,
            }
        )
        mock_session.get.return_value = mock_resp

        message = client.get_message(message_id=message_id)

        assert isinstance(message, Message)
        assert message.id == message_id
        assert message.content == "Hello, John!"
        assert message.status == "queued"

# Test error handling for authentication error
def test_authentication_error(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=401,
            json_data={"message": "Invalid API key"}
        )
        mock_session.get.return_value = mock_resp

        with pytest.raises(AuthenticationError) as exc_info:
            client.list_messages()

        assert "Invalid API key" in str(exc_info.value)

# Test error handling for validation error
def test_validation_error(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=400,
            json_data={"error": "Invalid phone number"}
        )
        mock_session.post.return_value = mock_resp

        with pytest.raises(ValidationError) as exc_info:
            client.create_contact(name="John Doe", phone="invalid-phone")

        assert "Invalid phone number" in str(exc_info.value)

# Test error handling for not found error
def test_not_found_error(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=404,
            json_data={"message": "Resource not found"}
        )
        mock_session.get.return_value = mock_resp

        with pytest.raises(NotFoundError) as exc_info:
            client.get_contact(contact_id="nonexistent-id")

        assert "Resource not found" in str(exc_info.value)

# Test error handling for server error
def test_server_error(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=500,
            json_data={"message": "Server error"}
        )
        mock_session.post.return_value = mock_resp

        with pytest.raises(ServerError) as exc_info:
            client.send_message(
                from_number="+1234567890",
                to_contact="contact123",
                content="Hello!"
            )

        assert "Server error" in str(exc_info.value)

# Test send_message with Contact object
def test_send_message_with_contact_object(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=201,
            json_data={
                "id": "msg124",
                "from": "+1234567890",
                "to": {
                    "id": "contact124",
                    "name": "Jane Doe",
                    "phone": "+0987654321",
                },
                "content": "Hi Jane!",
                "status": "queued",
                "createdAt": "2023-10-01T12:10:00Z",
            }
        )
        mock_session.post.return_value = mock_resp

        contact = Contact(id="contact124", name="Jane Doe", phone="+0987654321")
        message = client.send_message(
            from_number="+1234567890",
            to_contact=contact.id,
            content="Hi Jane!"
        )

        assert isinstance(message, Message)
        assert message.id == "msg124"
        assert message.to == "contact124"

# Test delete_contact with NotFoundError
def test_delete_contact_not_found(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=404,
            json_data={"message": "Contact not found"}
        )
        mock_session.delete.return_value = mock_resp

        with pytest.raises(NotFoundError) as exc_info:
            client.delete_contact(contact_id="nonexistent-id")

        assert "Contact not found" in str(exc_info.value)

# Test get_message with message not found
def test_get_message_not_found(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=404,
            json_data={"message": "Message not found"}
        )
        mock_session.get.return_value = mock_resp

        with pytest.raises(NotFoundError) as exc_info:
            client.get_message(message_id="nonexistent-id")

        assert "Message not found" in str(exc_info.value)

# Test update_contact with partial data
def test_update_contact_partial(client):
    with patch.object(client, 'session') as mock_session:
        contact_id = "contact123"
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "id": contact_id,
                "name": "John Doe",
                "phone": "+0987654321",
            }
        )
        mock_session.patch.return_value = mock_resp

        updated_contact = client.update_contact(
            contact_id=contact_id,
            phone="+0987654321"  # Only updating the phone
        )

        assert isinstance(updated_contact, Contact)
        assert updated_contact.name == "John Doe"
        assert updated_contact.phone == "+0987654321"

# Test list_messages with empty response
def test_list_messages_empty(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "messages": [],
                "page": 1,
                "quantityPerPage": 0,
            }
        )
        mock_session.get.return_value = mock_resp

        messages = client.list_messages(page=1, limit=10)

        assert isinstance(messages, list)
        assert len(messages) == 0

# Test list_contacts with empty response
def test_list_contacts_empty(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=200,
            json_data={
                "contacts": [],
                "pageNumber": 1,
                "pageSize": 0,
            }
        )
        mock_session.get.return_value = mock_resp

        contacts = client.list_contacts(page=1, limit=10)

        assert isinstance(contacts, list)
        assert len(contacts) == 0

# Test send_message with invalid contact ID
def test_send_message_invalid_contact(client):
    with patch.object(client, 'session') as mock_session:
        mock_resp = mock_response(
            status_code=400,
            json_data={"error": "Invalid contact ID"}
        )
        mock_session.post.return_value = mock_resp

        with pytest.raises(ValidationError) as exc_info:
            client.send_message(
                from_number="+1234567890",
                to_contact="invalid-contact-id",
                content="Hello!"
            )

        assert "Invalid contact ID" in str(exc_info.value)
