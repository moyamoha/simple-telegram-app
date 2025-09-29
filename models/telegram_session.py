from tortoise.models import Model
from tortoise import fields

class TelegramSession(Model):
    id = fields.IntField(primary_key=True)
    phone_number = fields.CharField(max_length=30, unique=True)
    session_string = fields.TextField(null=True)
    phone_code_hash = fields.CharField(max_length=255, null=True)
    app_session_id = fields.CharField(max_length=255, unique=True, null=True)

    class Meta:
        table = "telegram_session"