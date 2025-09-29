from fastapi import APIRouter, Cookie, HTTPException, Request, responses
from fastapi.templating import Jinja2Templates
from dto.channel_dto import ChannelResponseDTO
from dto.message_dto import MessageResponseDTO
from models.telegram_session import TelegramSession

from di_container import AppContainer
from services.message_service import MessageService
from services.telegram_client import MyTelegramClient
from session_management import get_session_id_from_request

channels_router = APIRouter(prefix="/channels", tags=["channels"])

templates = Jinja2Templates(directory="templates")

@channels_router.get("/")
async def read_channels(request: Request):

    session_id = get_session_id_from_request(request)
    if not session_id:
        return responses.RedirectResponse(url="/login")

    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)
    if not tel_session or tel_session.session_string is None:
        raise HTTPException(status_code=404, detail="Session not found. Please send code first.")

    tele_client: MyTelegramClient = container.tele_client(session_string=tel_session.session_string)
    channels = await tele_client.get_channels()
    resp = [ChannelResponseDTO.from_telegram_channel(channel).to_dict() for channel in channels]
    return templates.TemplateResponse("channels.html", {"request": request, "channels": resp })

@channels_router.get("/{channel_username}/messages")
async def get_channel_messages(channel_username: str, request: Request):
    session_id = get_session_id_from_request(request)
    if not session_id:
        return responses.RedirectResponse(url="/login")

    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)
    if not tel_session or tel_session.session_string is None:
        raise HTTPException(status_code=404, detail="Session not found. Please send code first.")

    tele_client: MyTelegramClient = container.tele_client(session_string=tel_session.session_string)
    messages_service = MessageService(tele_client)
    channel, messages = await messages_service.fetch_unread_messages(channel_username)

    resp = [message.to_dict() for message in messages]
    return templates.TemplateResponse("channel.html", {"request": request, "channel": channel, "messages": resp, })