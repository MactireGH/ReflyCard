import os
from dotenv import load_dotenv


load_dotenv()

def get_bot_token() -> str:
    """Функция для проверки наличия и передачи токена."""

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError('Token not found')

    return token

# === Константы проекта ===
# == Пути ==
DATABASE_PATH = os.path.abspath(os.path.join('database', 'database.db'))
LOG_PATH = os.path.abspath(os.path.join('logs', 'debug.log'))

# == Команды хэндлера ==
START_COMMAND = 'start'
