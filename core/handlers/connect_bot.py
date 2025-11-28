import requests
from telebot import TeleBot
from telebot.types import Message
from loguru import logger

from settings import config, messages


def is_valid_token(token: str) -> tuple[bool, dict | None]:
    """Checks the validity of the Telegram bot token using the getMe method"""

    url = f"https://api.telegram.org/bot{token}/getMe"

    try:
        response = requests.get(url, timeout=5).json()
    except Exception:
        return False, None

    return (True, response["result"]) if response.get("ok") else (False, None)


def register_handler_connect_bot(bot: TeleBot) -> None:
    @bot.message_handler(commands=[config.CONNECT_BOT_COMMAND])
    @logger.catch()
    def handler_connect_bot(message: Message) -> None:
        bot.send_message(message.chat.id, messages.CONNECT_CLIENT_BOT_FIRST_MSG)