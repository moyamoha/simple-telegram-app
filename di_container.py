from dependency_injector import containers, providers
from services.telegram_client import MyTelegramClient

class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yaml"])
    tele_client = providers.Factory(
        MyTelegramClient,
        # session_string to be provided by the caller
        session_string=providers.Dependency(),
        api_id=config.telegram.app_api_id,
        api_hash=config.telegram.app_api_hash
    )

