from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from routers.channels_router import channels_router
from routers.chats_router import chats_router
from routers.auth_router import auth_router
from routers.messages_router import messages_router
from session_management import get_session_id_from_request


def create_app():
    load_dotenv()
    app = FastAPI(openapi_url="/api/openapi.json", docs_url="/api/docs", redoc_url="/api/redoc", default_response_class=HTMLResponse)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(auth_router)
    app.include_router(channels_router)
    app.include_router(messages_router)
    app.include_router(chats_router)
    register_tortoise(
        app,
        db_url=os.getenv('DB_URL'),
        modules={"models": ["models.telegram_session"]},
        generate_schemas=True,  # Set to True if you want Tortoise to create tables automatically
        add_exception_handlers=True,
    )
    return app

app = create_app()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    session_id = get_session_id_from_request(request)
    if session_id:
        return Response(status_code=302, headers={"Location": "/channels"})
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/verify")
async def verify_page(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})

@app.get("/test")
async def verify_code(request: Request):
    session_id = get_session_id_from_request(request)
    return PlainTextResponse(content=f"Session ID from cookie: {session_id}")
