from telebot.types import ReplyKeyboardMarkup, KeyboardButton


MAIN_BTN_CREATE = "Создать публикацию"
MAIN_BTN_SCHEDULER = "Планировщик"

def main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(MAIN_BTN_CREATE), KeyboardButton(MAIN_BTN_SCHEDULER))

    return keyboard