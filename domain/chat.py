from typing import Union
from dataclasses import dataclass, asdict

@dataclass
class ChatParticipant:
    id: int
    name: str
    username: str

@dataclass
class ChatMessage:
    id: int
    sender_id: int
    content: str
    has_media: str
    is_self: bool


@dataclass
class Chat:
    id: Union[str, int]
    name: str
    participants: list[ChatParticipant]

    def add_participant(self, participant: ChatParticipant):
        self.participants.append(participant)