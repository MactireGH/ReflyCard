import os
from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from telebot.custom_filters import StateFilter
from loguru import logger

from settings import config


def create_bot() -> TeleBot:
    """The function creates and returns an instance of a Telegram bot with state support."""

    storage = StateMemoryStorage()
    logger.add(os.path.abspath(config.LOG_PATH), format="{time}, {level}, {message}", level="DEBUG", rotation="1 week", compression="zip")

    return TeleBot(config.get_bot_token(), state_storage=storage, parse_mode='HTML')

def app_running():
    """Launches the Telegram client."""

    bot = create_bot()
    bot.add_custom_filter(StateFilter(bot))
    logger.info('The bot has been launched.')
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    app_running()