import datetime


class MessageReaction:
    count: int
    emoticon: str | None

    def __init__(self, count: int, emoticon: str | None):
        self.count = count
        self.emoticon = emoticon

class Message:
    id: int
    sender_id: int
    message: str
    date: str
    media_type: str | None
    link: str | None
    is_read: bool
    reactions: list[MessageReaction] = []

    def __init__(self, id: int, sender_id: int, message: str, date: str, media_type: str | None, link: str | None, is_read: bool, reactions: list[MessageReaction] = []):
        self.id = id
        self.sender_id = sender_id
        self.message = message
        self.date = date
        self.media_type = media_type
        self.link = link
        self.is_read = is_read
        self.reactions = reactions
    
    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "message": self.message,
            "date": str(self.date),
            "media_type": self.media_type,
            "link": self.link,
            "is_read": self.is_read,
            "reactions": [ {"count": r.count, "emoticon": r.emoticon} for r in self.reactions ]
        }