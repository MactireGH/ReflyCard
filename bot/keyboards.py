from telebot import types


BTN_CREATE = "Создать публикацию"
BTN_SCHEDULE = "Планировщик"

def keyboard_main():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_CREATE, BTN_SCHEDULE)

    return kb