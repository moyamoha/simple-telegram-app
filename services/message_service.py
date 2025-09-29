from typing import Any, Union
from services.telegram_client import MyTelegramClient
from domain.message import Message, MessageReaction


class MessageService:
    def __init__(self, tele_client: MyTelegramClient):
        self.tele_client = tele_client

    async def fetch_unread_messages(self, channel_id: Union[int, str]) -> tuple[Any, list[Message]]:
        channel = await self.tele_client.get_channel_by_username_or_id(channel_id)
        messages_from_telegram = await self.tele_client.get_messages_for_channel(channel)

        # for msg in messages_from_telegram.messages:
        #    data = await self.tele_client.download_message_media(channel, msg.id)
        return channel, [Message(
            id=msg.id,
            sender_id=msg.sender_id,
            message=msg.message,
            date=msg.date,
            media_type=get_media_type(msg),
            link='/messages/media/{}?channel={}'.format(msg.id, channel_id) if hasattr(msg, 'media') else None,
            is_read=msg.unread if hasattr(msg, 'unread') else True,
            reactions=get_simplified_reactions_from_message(msg)
        ) for msg in messages_from_telegram]

    async def react_to_message(self, channel_id: str, message_id: int, reaction: str) -> bool:
        try:
            channel = await self.tele_client.get_channel_by_username_or_id(channel_id)
            await self.tele_client.react_to_message(channel, message_id, reaction)
            return True
        except Exception as e:
            print(f"Error reacting to message: {e}")
            return False

    async def mark_messages_as_read(self, channel: str, message_ids: list[int]) -> bool:
        try:
            await self.tele_client.mark_messages_as_read(channel, message_ids)
            return True
        except Exception as e:
            print(f"Error marking message as read: {e}")
            return False

def get_media_type(message: Any) -> str | None:
    if hasattr(message, 'file') and message.file:
        return message.file.mime_type

def get_simplified_reactions_from_message(message: Any) -> list[MessageReaction]:
    reactions = []
    if not hasattr(message, 'reactions') or not message.reactions: return []
    if not message.reactions.results: return []
    if hasattr(message, 'reactions') and message.reactions:
        for reaction in message.reactions.results:
            if not hasattr(reaction, 'reaction'): continue
            if not hasattr(reaction.reaction, 'emoticon'): continue
            reactions.append(MessageReaction(count=reaction.count, emoticon=reaction.reaction.emoticon))
    return reactions