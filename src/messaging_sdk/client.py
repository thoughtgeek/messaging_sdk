from typing import Optional, List, Dict, Any
import requests

from .models import Contact, Message
from .exceptions import (
    MessagingError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
)


class MessagingClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:3000"):
        """Initialize the messaging client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL of the API (default: http://localhost:3000)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def _handle_response(
            self,
            response: requests.Response
    ) -> Optional[Dict[str, Any]]:

        """Handle API response and errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 403:
            raise AuthenticationError(
                "Forbidden: You don't have permission to access this resource."
            )
        elif response.status_code == 400:
            raise ValidationError(response.json().get(
                "error", "Validation error"
            ))
        elif response.status_code == 404:
            raise NotFoundError(response.json().get(
                "message", "Resource not found"
            ))
        elif response.status_code >= 500:
            raise ServerError(response.json().get("message", "Server error"))
        elif response.status_code in (200, 201):
            return response.json() if response.content else {}
        elif response.status_code == 204:
            # No content to return; indicate success
            return None
        else:
            raise MessagingError(
                f"Unexpected status code: {response.status_code}"
            )

    def send_message(
            self,
            from_number: str,
            to_contact: str,
            content: str
    ) -> Message:

        """Send a new message.

        Args:
            from_number: The sender's phone number
            to_contact: Either a Contact object or a contact ID
            content: The message content

        Returns:
            Message: The created message
        """
        # Prepare the payload
        payload = {
            "from": from_number,
            "content": content,
            "to": {"id": to_contact}
        }

        response = self.session.post(f"{self.base_url}/messages", json=payload)
        data = self._handle_response(response)
        return Message(**data)

    def list_messages(
        self, page: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Message]:
        """List sent messages with pagination."""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        response = self.session.get(f"{self.base_url}/messages", params=params)
        data = self._handle_response(response)
        return [Message(**msg) for msg in data.get("messages", [])]

    def get_message(self, message_id: str) -> Message:
        """Get a specific message by ID."""
        response = self.session.get(f"{self.base_url}/messages/{message_id}")
        data = self._handle_response(response)
        return Message(**data)

    def create_contact(self, name: str, phone: str) -> Contact:
        """Create a new contact."""
        payload = {"name": name, "phone": phone}
        response = self.session.post(f"{self.base_url}/contacts", json=payload)
        data = self._handle_response(response)
        return Contact(**data)

    def list_contacts(
        self, page: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Contact]:
        """List contacts with pagination."""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        response = self.session.get(f"{self.base_url}/contacts", params=params)
        data = self._handle_response(response)
        return [Contact(**contact) for contact in data.get("contacts", [])]

    def get_contact(self, contact_id: str) -> Contact:
        """Get a specific contact by ID."""
        response = self.session.get(f"{self.base_url}/contacts/{contact_id}")
        data = self._handle_response(response)
        return Contact(**data)

    def update_contact(
        self,
        contact_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Contact:
        """Update a contact."""
        payload = {}
        if name is not None:
            payload["name"] = name
        if phone is not None:
            payload["phone"] = phone

        response = self.session.patch(
            f"{self.base_url}/contacts/{contact_id}", json=payload
        )
        data = self._handle_response(response)
        return Contact(**data)

    def delete_contact(self, contact_id: str) -> None:
        """Delete a contact."""
        response = self.session.delete(
            f"{self.base_url}/contacts/{contact_id}"
        )
        self._handle_response(response)
