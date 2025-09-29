from datetime import datetime
from typing import Any
from pydantic import BaseModel


class MessageResponseDTO(BaseModel):
    id: int
    sender_id: int
    message: str
    date: datetime
    media_type: str | None = None
    media_link: str | None = None
    is_read: bool

    @classmethod
    def from_telegram_message(cls, message, link: str | None = None) -> "MessageResponseDTO":
        return cls(
            id=message.id,
            sender_id=message.sender_id,
            message=message.message,
            date=message.date,
            media_type=message.media.type if hasattr(message, 'media') else None,
            media_link=message.media if hasattr(message, 'media') else None,
            is_read=not message.unread if hasattr(message, 'unread') else True,
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "message": self.message,
            "date": self.date.isoformat(),
            "media_type": self.media_type,
            "media_link": self.media_link,
            "is_read": self.is_read
        }
    

class MarkMessagesAsReadDTO(BaseModel):
    channel_username: str
    messages: list[int] = []