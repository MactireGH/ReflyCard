from telebot import TeleBot
from telebot.types import Message
from loguru import logger

from settings import config, messages
from core import database


def register_start_handlers(bot: TeleBot) -> None:
    @bot.message_handler(commands=[config.START_COMMAND])
    @logger.catch()
    def handler_start(message: Message):
        database.create_database()
        user = database.get_or_create_user(tag_id=message.from_user.id, username=message.from_user.username, full_name=" ".join(filter(None, [message.from_user.first_name, message.from_user.last_name])))
        bot.delete_state(message.from_user.id, message.chat.id)

        status = (
            f"\n\n<b>Статус профиля:</b>\n"
            f"— Бот: {'подключён ✅' if user.has_connected_bot else 'не подключён ❌'}\n"
            f"— Канал: {user.channel_username + ' ✅' if user.channel_username else 'не указан ❌'}"
        )
        bot.send_message(message.chat.id, f"{messages.START_MSG}{status}\n\n{messages.COMMANDS_MSG}")
