from telebot import TeleBot
from telebot.types import Message
from loguru import logger
from datetime import datetime

from core.db.users import get_user, create_user, update_user, normalize_field
from settings import config, messages


def register_handler_start(bot: TeleBot) -> None:
    @bot.message_handler(commands=[config.START_COMMAND])
    @logger.catch()
    def handler_start(message: Message) -> None:
        user_id = message.from_user.id
        username = normalize_field(message.from_user.username)
        first_name = normalize_field(message.from_user.first_name)
        last_name = normalize_field(message.from_user.last_name)
        date = str(datetime.now().date())

        if not get_user(user_id):
            create_user(user_id=user_id, username=username, first_name=first_name, last_name=last_name, registered_date=date)

        else:
            update_user(user_id=user_id, username=username, first_name=first_name, last_name=last_name)

        bot.delete_state(user_id, message.chat.id)
        bot.send_message(message.chat.id, f"{messages.START_MSG}\n\n{messages.COMMANDS_MSG}")