from pydantic import BaseModel


class SendCodeRequestDTO(BaseModel):
    phone_number: str


class VerifyCodeRequestDTO(BaseModel):
    phone_number: str
    code: str