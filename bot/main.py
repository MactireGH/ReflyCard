from telebot import TeleBot

from core.config import BOT_TOKEN
from core.messages_bot import FIRST_RUN_APP, CREATE_PUBLIC, SCHEDULER_PUBLIC
from bot.keyboards import keyboard_main, BTN_CREATE, BTN_SCHEDULE


def app_run():
    if not  BOT_TOKEN:
        raise RuntimeError('BOT_TOKEN не найден. Создай .env и вставь токен.')

    bot = TeleBot(BOT_TOKEN, parse_mode='HTML')

    @bot.message_handler(commands=["start"])
    def handle_start(m):
        bot.send_message(m.chat.id, FIRST_RUN_APP, reply_markup=keyboard_main())

    @bot.message_handler(func=lambda m: m.text == BTN_CREATE)
    def handle_create(m):
        bot.send_message(m.chat.id, CREATE_PUBLIC)

    @bot.message_handler(func=lambda m: m.text == BTN_SCHEDULE)
    def handle_schedule(m):
        bot.send_message(m.chat.id, SCHEDULER_PUBLIC)

    print("Bot is running…")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    app_run()