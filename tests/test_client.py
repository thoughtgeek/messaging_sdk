import pytest
import responses
from messaging_sdk.client import MessagingClient
from messaging_sdk.models import Contact, Message
from messaging_sdk.exceptions import (
    AuthenticationError,
    ValidationError,
)


@pytest.fixture
def client():
    return MessagingClient(api_key="test-key", base_url="http://test-api.com")


@responses.activate
def test_create_contact(client):
    responses.add(
        responses.POST,
        f"{client.base_url}/contacts",
        json={
            "id": "contact123",
            "name": "John Doe",
            "phone": "+1234567890",
        },
        status=201
    )

    contact = client.create_contact(name="John Doe", phone="+1234567890")

    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{client.base_url}/contacts"
    assert request.headers['Authorization'] == 'Bearer test-key'
    assert 'application/json' in request.headers['Content-Type']

    assert isinstance(contact, Contact)
    assert contact.id == "contact123"
    assert contact.name == "John Doe"
    assert contact.phone == "+1234567890"


@responses.activate
def test_list_contacts(client):
    responses.add(
        responses.GET,
        f"{client.base_url}/contacts",
        json={
            "contacts": [
                {"id": "contact1", "name": "Alice", "phone": "+1111111111"},
                {"id": "contact2", "name": "Bob", "phone": "+2222222222"},
            ],
            "pageNumber": 1,
            "pageSize": 2,
        },
        status=200
    )

    contacts = client.list_contacts(page=1, limit=10)

    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert 'pageIndex=1' in request.url
    assert 'max=10' in request.url

    assert isinstance(contacts, list)
    assert len(contacts) == 2
    assert contacts[0].name == "Alice"
    assert contacts[1].phone == "+2222222222"


@responses.activate
def test_send_message(client):
    responses.add(
        responses.POST,
        f"{client.base_url}/messages",
        json={
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
        },
        status=201
    )

    message = client.send_message(
        from_number="+1234567890",
        to_contact="contact123",
        content="Hello, John!"
    )

    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{client.base_url}/messages"

    assert isinstance(message, Message)
    assert message.id == "msg123"
    assert message.content == "Hello, John!"
    assert message.status == "queued"


@responses.activate
def test_authentication_error(client):
    responses.add(
        responses.GET,
        f"{client.base_url}/messages",
        json={"message": "Invalid API key"},
        status=401
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.list_messages()
    assert "Invalid API key" in str(exc_info.value)


@responses.activate
def test_validation_error(client):
    responses.add(
        responses.POST,
        f"{client.base_url}/contacts",
        json={"error": "Invalid phone number"},
        status=400
    )

    with pytest.raises(ValidationError) as exc_info:
        client.create_contact(name="John Doe", phone="invalid-phone")
    assert "Phone number must be in E.164 format." in str(exc_info.value)


@responses.activate
def test_update_contact_partial(client):
    contact_id = "contact123"
    responses.add(
        responses.PATCH,
        f"{client.base_url}/contacts/{contact_id}",
        json={
            "id": contact_id,
            "name": "John Doe",
            "phone": "+0987654321",
        },
        status=200
    )

    updated_contact = client.update_contact(
        contact_id=contact_id,
        phone="+0987654321"
    )

    request = responses.calls[0].request
    assert request.url == f"{client.base_url}/contacts/{contact_id}"
    assert '"phone": "+0987654321"' in request.body.decode()
    assert '"name"' not in request.body.decode()
    assert isinstance(updated_contact, Contact)
    assert updated_contact.phone == "+0987654321"


@responses.activate
def test_delete_contact(client):
    contact_id = "contact123"
    responses.add(
        responses.DELETE,
        f"{client.base_url}/contacts/{contact_id}",
        status=204
    )

    result = client.delete_contact(contact_id=contact_id)

    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{client.base_url}/contacts/{contact_id}"
    assert request.method == 'DELETE'
    assert result is None


@responses.activate
def test_list_messages_empty(client):
    responses.add(
        responses.GET,
        f"{client.base_url}/messages",
        json={
            "messages": [],
            "page": 1,
            "quantityPerPage": 0,
        },
        status=200
    )

    messages = client.list_messages(page=1, limit=10)

    assert len(responses.calls) == 1
    assert isinstance(messages, list)
    assert len(messages) == 0
