import os.path
from loguru import logger
from dotenv import load_dotenv


# Functions
load_dotenv()

@logger.catch()
def get_bot_token() -> str:
    """The function for checking the presence and transfer of the token."""

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError('Token not found.')

    return token

# Paths
DATABASE_MAIN_PATH = os.path.abspath(os.path.join('storage/data', 'storage_bot.db'))
LOG_PATH = os.path.abspath(os.path.join('storage/logs', 'debug.log'))

# Commands for handlers
START_COMMAND = 'start'
CONNECT_BOT_COMMAND = 'connect_bot'
CONNECT_CHANNEL_COMMAND = 'connect_channel'
REMOVE_BOT__COMMAND = 'remove_bot'