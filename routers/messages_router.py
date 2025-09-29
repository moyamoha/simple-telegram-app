import os
from fastapi import APIRouter, Depends, HTTPException, Request, responses
from dto.message_dto import MarkMessagesAsReadDTO
from models.telegram_session import TelegramSession
from di_container import AppContainer
from services.message_service import MessageService
from services.telegram_client import MyTelegramClient
from session_management import get_session_id_from_request   

messages_router = APIRouter(prefix="/messages", tags=["messages"])

@messages_router.get("/get-unread")
async def read_unread_messages(channel_id: int, request: Request):

    session_id = get_session_id_from_request(request)
    if not session_id:
        return responses.RedirectResponse(url="/login")

    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)

    if not tel_session:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    tele_client = container.tele_client(session_string=tel_session.session_string)
    unread_messages, channel = await tele_client.get_unread_messages(channel_id)
    resp = [{"id": msg.id, "sender_id": msg.sender_id, "message": msg.message} for msg in unread_messages]
    return {"status": "success", "unread_messages": resp, "channel": channel}


@messages_router.get("/media/{message_id}")
async def get_message_media(message_id: int, channel: str, request: Request, cache: bool = True):
    session_id = get_session_id_from_request(request)
    if not session_id:
        return responses.RedirectResponse(url="/login")
    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)
    if not tel_session:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    tele_client = container.tele_client(session_string=tel_session.session_string)
    channel_obj = await tele_client.get_channel_by_username_or_id(channel)
    bytes_data = await tele_client.download_message_media(channel_obj, message_id)

    if not bytes_data:
        raise HTTPException(status_code=404, detail="Media not found")
    return responses.Response(content=bytes_data, media_type="application/octet-stream")

@messages_router.post("/mark-read")
async def mark_messages_as_read(body: MarkMessagesAsReadDTO, request: Request):
    session_id = get_session_id_from_request(request)
    if not session_id:
        return responses.RedirectResponse(url="/login")

    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)
    if not tel_session or tel_session.session_string is None:
        raise HTTPException(status_code=404, detail="Session not found. Please send code first.")

    tele_client: MyTelegramClient = container.tele_client(session_string=tel_session.session_string)
    messages_service = MessageService(tele_client)
    
    try:
        await messages_service.mark_messages_as_read(body.channel_username, body.messages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to mark messages as read: {e}")

    return responses.JSONResponse(content={"success": True, "message": "Messages marked as read"})