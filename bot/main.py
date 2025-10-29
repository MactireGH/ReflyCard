from telebot import TeleBot
from telebot.types import Message

from settings.config import get_bot_token
from settings import messages
from bot.keyboards.common import (
    main_menu_keyboard,
    MAIN_BTN_CREATE,
    MAIN_BTN_SCHEDULER,
)

def app_run():
    bot = TeleBot(get_bot_token(), parse_mode='HTML')

    @bot.message_handler(commands=["start"])
    def handle_start(message: Message):
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, messages.FIRST_RUN_APP, reply_markup=main_menu_keyboard())

    @bot.message_handler(func= lambda x: x.text in {MAIN_BTN_CREATE, MAIN_BTN_SCHEDULER})
    def handler_main_menu(message: Message):
        if message.text == MAIN_BTN_CREATE:
            return flow_create_publication(message)
        if message.text == MAIN_BTN_SCHEDULER:
            return flow_scheduler(message)
        return None

    def flow_create_publication(message: Message):
        bot.send_message(message.chat.id, messages.CREATE_PUBLIC)

    def flow_scheduler(message: Message):
        bot.send_message(message.chat.id, messages.SCHEDULER_PUBLIC)

    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    app_run()