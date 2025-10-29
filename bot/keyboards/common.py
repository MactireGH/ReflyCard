from telebot.types import (ReplyKeyboardMarkup,
                           InlineKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardButton)


MAIN_BTN_CREATE = "Создать публикацию"
MAIN_BTN_SCHEDULER = "Планировщик"

# Callback for inline
ACT_PUBLISH_NOW = 'act:publish_now'
ACT_SCHEDULE = 'act:schedule'
ACT_EDIT = 'act:edit'
ACT_CANCEL = 'act:cancel'

def main_menu_keyboard():
    keyboard_reply = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_reply.add(KeyboardButton(MAIN_BTN_CREATE), KeyboardButton(MAIN_BTN_SCHEDULER))

    return keyboard_reply

def post_action_keyboard() -> InlineKeyboardMarkup:
    """Функция для создания инлайн-клавиатуры с предпросмотром поста."""

    keyboard_inline = InlineKeyboardMarkup()
    keyboard_inline.add(InlineKeyboardButton(text="Опубликовать сейчас", callback_data=ACT_PUBLISH_NOW))
    keyboard_inline.add(InlineKeyboardButton(text="Запланировать", callback_data=ACT_SCHEDULE))
    keyboard_inline.add(InlineKeyboardButton(text="Редактировать", callback_data=ACT_EDIT))
    keyboard_inline.add(InlineKeyboardButton(text="Отмена", callback_data=ACT_CANCEL))

    return keyboard_inline