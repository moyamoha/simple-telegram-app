from domain.chat import Chat, ChatParticipant
from services.telegram_client import MyTelegramClient


class ChatService:
    def __init__(self, tele_client: MyTelegramClient):
        self.tele_client = tele_client

    async def get_my_chats(self):
        result = []
        async with self.tele_client.client:
            me = await self.tele_client.client.get_me()
            dialogs = await self.tele_client.client.get_dialogs()
            for dialog in dialogs:
                if dialog.is_group:
                    chat = Chat(dialog.id, dialog.name, [])
                    participants_resp = await self.tele_client.client.get_participants(dialog.entity)
                    for p in participants_resp:
                        chat.add_participant(ChatParticipant(p.id, f'{p.first_name} {p.last_name}', p.username))
                    result.append(chat)
                elif dialog.is_user:
                    if dialog.entity.bot or dialog.entity.deleted:
                        continue
                    chat = Chat(dialog.id, dialog.name, [])
                    chat.add_participant(ChatParticipant(me.id, f'{me.first_name} {me.last_name}', me.username))
                    chat.add_participant(ChatParticipant(dialog.entity.id, f'{dialog.entity.first_name} {dialog.entity.last_name}' , dialog.entity.username))
                    result.append(chat)
        return result