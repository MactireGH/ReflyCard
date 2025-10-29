import os
from dotenv import load_dotenv


load_dotenv()

def get_bot_token() -> str:
    """Функция для проверки наличия токена."""

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError('Token not found')

    return token