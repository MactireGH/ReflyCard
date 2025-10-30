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

## Callback fo scheduler
ACT_JOB_DEL_PREFIX = 'job_del_'
ACT_JOB_PAGE_PREFIX = 'job_page_'

def main_menu_keyboard():
    """Функция для создания реплай-клавиатуры."""
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

def scheduler_list_keyboards(jobs):
    """Функция для создания инлайн-клавиатуры для планировщика публикаций."""

    keyboard_scheduler = InlineKeyboardMarkup()

    if not jobs:
        return keyboard_scheduler

    for j in jobs:
        view = InlineKeyboardButton(
            text=f"{j['run_at']} — {j['title'][:24]}",
            callback_data=f"{ACT_JOB_PAGE_PREFIX}{j['id']}"
        )
        delete_btn = InlineKeyboardButton(
            text="Удалить",
            callback_data=f"{ACT_JOB_DEL_PREFIX}{j['id']}"
        )

        keyboard_scheduler.row(view, delete_btn)

    return keyboard_scheduler