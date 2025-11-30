import requests
from telebot import TeleBot
from telebot.types import Message
from datetime import datetime
from loguru import logger
from requests import RequestException

from core.db.client_bots import get_client_token, create_client_bot
from settings import config, messages


def is_valid_token(token: str) -> tuple[bool, dict | None]:
    """Checks the validity of the Telegram bot token using the getMe method"""

    url = f"https://api.telegram.org/bot{token}/getMe"

    try:
        response = requests.get(url, timeout=5).json()
    except (RequestException, ValueError):
        return False, None

    return (True, response["result"]) if response.get("ok") else (False, None)


def register_handler_connect_bot(bot: TeleBot) -> None:
    @bot.message_handler(commands=[config.CONNECT_BOT_COMMAND])
    @logger.catch()
    def handler_connect_bot(message: Message) -> None:
        bot.send_message(message.chat.id, messages.CONNECT_CLIENT_BOT_FIRST_MSG, parse_mode='Markdown')
        bot.register_next_step_handler(message, handler_client_bot_token)

    def handler_client_bot_token(message: Message) -> None:
        """Handles user token input, validates and saves the client bot."""

        user_id = message.from_user.id
        token = message.text

        if not token:
            bot.send_message(message.chat.id, messages.CONNECT_CLIENT_BOT_ERROR_1_MSG)
            return bot.register_next_step_handler(message, handler_client_bot_token)

        token = token.strip().replace(' ', '')

        if ':' not in token:
            bot.send_message(message.chat.id, messages.CONNECT_CLIENT_BOT_ERROR_1_MSG)
            return bot.register_next_step_handler(message, handler_client_bot_token)

        is_valid, info = is_valid_token(token)
        if not is_valid:
            bot.send_message(message.chat.id, messages.CONNECT_CLIENT_BOT_ERROR_2_MSG)
            return bot.register_next_step_handler(message, handler_client_bot_token)

        if get_client_token(token):
            bot.send_message(message.chat.id, messages.CONNECT_CLIENT_BOT_ERROR_3_MSG)
            return bot.register_next_step_handler(message, handler_client_bot_token)

        create_client_bot(bot_id=info['id'],
                          user_id=user_id,
                          bot_name=info.get('first_name', ''),
                          bot_username=info.get("username", ''),
                          bot_token=token,
                          bot_created=str(datetime.now().date()))

        bot.send_message(message.chat.id, f"@{info['username']}")
        bot.send_message(message.chat.id, messages.CONNECT_CLIENT_BOT_SUCCESS_MSG)