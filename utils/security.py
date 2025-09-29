from fastapi import HTTPException, Request, responses

from di_container import AppContainer
from models.telegram_session import TelegramSession
from session_management import get_session_id_from_request


async def get_telegram_session_from_request(request: Request):
    session_id = get_session_id_from_request(request)
    if not session_id:
        return { "success": False, "result": responses.RedirectResponse(url="/login") }

    container = AppContainer()
    tel_session = await TelegramSession.get_or_none(app_session_id=session_id)
    if not tel_session or tel_session.session_string is None:
        return { "success": False, "result": responses.RedirectResponse(url="/login") }
    return { "success": True, "result": tel_session }
