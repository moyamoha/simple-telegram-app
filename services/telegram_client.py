from typing import Any, Union
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest, SendReactionRequest
from telethon import types

from utils.funcs import is_str_digit_like

class MyTelegramClient:

    def __init__(self, session_string: str | None, api_id: int, api_hash: str):
        self.session_string = session_string
        self.client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash
        )

    async def connect(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise Exception("Client is not authorized. Please send code first.")

    async def send_code(self, phone_number: str) -> tuple[str, str]:
        await self.connect()
        sent_code = await self.client.send_code_request(phone_number)
        self.session_string = self.client.session.save()
        await self.client.disconnect()
        return sent_code.phone_code_hash, self.session_string

    async def verify_code(self, phone_number: str, code: str, code_hash: str | None = None):
        await self.connect()
        await self.client.sign_in(phone_number, code, phone_code_hash=code_hash)
        self.session_string = self.client.session.save()
        await self.client.disconnect()
        return self.session_string
    
    async def get_channels(self):
        async with self.client:
            dialogs = await self.client.get_dialogs()
            channels = [dialog for dialog in dialogs if dialog.is_channel]
        return channels

    async def get_channel_by_username_or_id(self, username_or_id: Union[str, int]):
        if (isinstance(username_or_id, str) and is_str_digit_like(username_or_id)) or isinstance(username_or_id, int):
            username_or_id = int(username_or_id)
        async with self.client:
            return await self.client.get_entity(username_or_id)

    async def get_messages_for_channel(self, channel_object: Any):
        async with self.client:
            
            dialogs = await self.client.get_dialogs()
            target_dialog = next((d for d in dialogs if d.entity.id == channel_object.id), None)
            if not target_dialog:
                print('No dialog found for the specified channel.')
                return []
            
            unread_count = target_dialog.unread_count
            if unread_count == 0:
                return []

            messages = await self.client(GetHistoryRequest(
                peer=channel_object,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=unread_count,
                max_id=0,
                min_id=0, hash=0
            ))

            return messages.messages
    
    async def react_to_message(self, channel_object: Any, message_id: int, reaction: str):
        async with self.client:
            await self.client(
                SendReactionRequest(
                    peer=channel_object,
                    msg_id=message_id,
                    reaction=types.ReactionEmoji(emoticon=reaction)
                )
            )

    async def get_session_string(self) -> str:
        return self.client.session.save()
    
    async def download_message_media(self, peer: Any, message_id: int) -> bytes | None:
        try:
            async with self.client:
                message = await self.client.get_messages(peer, ids=message_id)
                if message and message.media:
                    media_bytes = await self.client.download_media(message.media, file=bytes)
                    return media_bytes
                return None
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None
    
    async def mark_messages_as_read(self, channel_username_or_id: Union[int, str], message_ids: list[int]):
        if (isinstance(channel_username_or_id, str) and is_str_digit_like(channel_username_or_id)) or isinstance(channel_username_or_id, int):
            channel_username_or_id = int(channel_username_or_id)
        async with self.client:
            if type(channel_username_or_id) is int:
                channel = await self.client.get_entity(types.PeerChannel(channel_username_or_id))
            else:
                channel = await self.client.get_entity(channel_username_or_id)
            messages = await self.client.get_messages(channel, ids=message_ids)
            await self.client.send_read_acknowledge(channel, message=messages)

