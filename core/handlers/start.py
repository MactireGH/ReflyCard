from telebot import TeleBot
from telebot.types import Message
from loguru import logger
from datetime import datetime

from core.db.users import get_user, create_user
from settings import config, messages


def register_handler_start(bot: TeleBot) -> None:
    @bot.message_handler(commands=[config.START_COMMAND])
    @logger.catch()
    def handler_start(message: Message) -> None:
        if not get_user(message.from_user.id):
            create_user(user_id=message.from_user.id,
                        username=message.from_user.username.lower().strip(),
                        first_name=message.from_user.first_name.lower().strip(),
                        last_name=message.from_user.last_name.lower().strip(),
                        registered_date=str(datetime.now().date()))
            bot.delete_state(message.from_user.id, message.chat.id)
            bot.send_message(message.chat.id, f"{messages.START_MSG}\n\n{messages.COMMANDS_MSG}")
        else:
            bot.delete_state(message.from_user.id, message.chat.id)
            bot.send_message(message.chat.id, f"{messages.START_MSG}\n\n{messages.COMMANDS_MSG}")