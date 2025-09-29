import os
import secrets
from fastapi import Request

def generate_session_id():
    return secrets.token_hex(64)

def get_session_id_from_request(request: Request):
    cookies = request.cookies
    return cookies.get("session")