from pydantic import BaseModel


class ChannelResponseDTO(BaseModel):
    id: int
    title: str
    username: str | None
    unread_count: int | None = 0
    status: str = 'active'

    @classmethod
    def from_telegram_channel(cls, channel) -> "ChannelResponseDTO":
        return cls(
            id=channel.id,
            title=channel.title,
            username=channel.entity.username if channel.entity and hasattr(channel.entity, 'username') else None,
            unread_count=channel.unread_count if hasattr(channel, 'unread_count') else 0,
            status=get_channel_status(channel)
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "username": self.username,
            "unread_count": self.unread_count,
            "status": self.status
        }
    
def get_channel_status(channel) -> str:
    # Placeholder logic for determining channel status
    if channel.pinned == True:
        return 'pinned'
    if channel.archived == True:
        return 'archived'
    return 'active'