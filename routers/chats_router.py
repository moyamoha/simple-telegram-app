from fastapi import APIRouter, HTTPException, Request, responses
from fastapi.templating import Jinja2Templates

from di_container import AppContainer
from models.telegram_session import TelegramSession
from services.chat_service import ChatService
from session_management import get_session_id_from_request
from dataclasses import asdict


chats_router = APIRouter(prefix="/chats", tags=["chats"])
templates = Jinja2Templates(directory="templates")

@chats_router.get("/")
async def read_chats(request: Request):
    session_id = get_session_id_from_request(request)
    if not session_id:
        return responses.RedirectResponse(url="/login")
    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)
    if not tel_session:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    tele_client = container.tele_client(session_string=tel_session.session_string)

    chat_service = ChatService(tele_client=tele_client)
    my_chats = await chat_service.get_my_chats()
    return templates.TemplateResponse("chats.html", {"request": request, "chats": [asdict(chat) for chat in my_chats]})

@chats_router.get("/{chat_id}/messages")
async def get_chat_messages(chat_id: int, request: Request):
    session_id = get_session_id_from_request(request)
    if not session_id:
        return responses.RedirectResponse(url="/login")
    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)
    if not tel_session:
        raise HTTPException(status_code=404, detail="Telegram session not found")

    tele_client = container.tele_client(session_string=tel_session.session_string)

    async with tele_client.client:
        entity = await tele_client.client.get_entity(chat_id)
        messages = await tele_client.client.get_messages(entity, limit=20)
        resp = [{"id": msg.id, "sender_id": msg.sender_id, "message": msg.message} for msg in messages]
        return templates.TemplateResponse("chat_messages.html", {"request": request, "messages": resp, "chat_id": chat_id})
    return {"message": f"Messages for chat {chat_id} will be here"}

@chats_router.get("/test")
async def get_test_chat_page(request: Request):
    return templates.TemplateResponse("chat_page.html", { "request": request })