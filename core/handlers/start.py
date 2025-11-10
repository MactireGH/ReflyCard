from telebot import TeleBot
from telebot.types import Message
from loguru import logger

from settings import config, messages


def register_start_handlers(bot: TeleBot) -> None:
    @bot.message_handler(commands=[config.START_COMMAND])
    @logger.catch()
    def handler_start(message: Message):
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, f"{messages.START_MSG}\n\n{messages.COMMANDS_MSG}")
