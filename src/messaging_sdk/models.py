from typing import Union, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class Contact(BaseModel):
    id: Optional[str] = None
    name: str
    phone: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "phone": "+1234567890"
            }
        }
    )

class MessageStatus(BaseModel):
    id: str
    status: str
    created_at: datetime
    delivered_at: Optional[datetime] = None


class Message(BaseModel):
    id: Optional[str] = None
    from_: str = Field(alias="from")
    to: dict
    content: str
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "from": "+1234567890",
                "to": "fa942602-25ca-4ab3-ae65-6f744467e856",
                "content": "Hello, World!"
            }
        }
    )

class WebhookEvent(BaseModel):
    id: str
    status: str
    delivered_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
