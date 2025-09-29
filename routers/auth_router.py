from fastapi import responses, Cookie, Response
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import RedirectResponse as redirect

from di_container import AppContainer
from dto.auth_dto import SendCodeRequestDTO, VerifyCodeRequestDTO
from services.telegram_client import MyTelegramClient
from models.telegram_session import TelegramSession
from session_management import generate_session_id

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/send-code")
async def send_code(body: SendCodeRequestDTO):
    container = AppContainer()
    tele_client: MyTelegramClient = container.tele_client(session_string=None)

    phone_number = body.phone_number
    tele_session = await TelegramSession.get_or_none(phone_number=phone_number)
    if tele_session and tele_session.session_string:
        response = responses.JSONResponse(content={"message": "Already authenticated"})
        response.set_cookie(
            key="session",
            value=tele_session.app_session_id,
            httponly=True,
            secure=False,
            max_age=7 * 24 * 60 * 60,
        )
        return response

    try:
        phone_code_hash, session_string = await tele_client.send_code(phone_number)
    except Exception as e:
        raise HTTPException(status_code=400, detail={ "error": f"Failed to send code to {phone_number}" })

    await TelegramSession.update_or_create(
        phone_number=body.phone_number,
        defaults={"phone_code_hash": phone_code_hash, "session_string": session_string}
    )

    return responses.JSONResponse(content={"message": f"Code sent to {body.phone_number}"})

@auth_router.post("/verify-code")
async def verify_code(body: VerifyCodeRequestDTO, response: Response):
    container = AppContainer()

    tel_session = await TelegramSession.get_or_none(phone_number=body.phone_number)
    if not tel_session:
        raise HTTPException(status_code=404, detail="Session not found. Please send code first.")

    tele_client: MyTelegramClient = container.tele_client(session_string=tel_session.session_string)

    try:
        session_string = await tele_client.verify_code(
            body.phone_number,
            body.code,
            code_hash=tel_session.phone_code_hash
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to verify code: {e}")

    tel_session.session_string = session_string
    tel_session.phone_code_hash = None
    tel_session.app_session_id = generate_session_id()
    await tel_session.save()

    response = responses.JSONResponse(content={"message": "Phone number verified successfully"})
    response.set_cookie(
        key="session",
        value=tel_session.app_session_id,
        httponly=True,
        secure=False,
        max_age= 7 * 24 * 60 * 60,
    )
    return response