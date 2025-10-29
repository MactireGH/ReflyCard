from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from settings.config import get_bot_token
from settings import messages as msg
from bot.keyboards.common import (
    main_menu_keyboard,
    post_action_keyboard,
    MAIN_BTN_CREATE,
    MAIN_BTN_SCHEDULER,
    ACT_PUBLISH_NOW,
    ACT_SCHEDULE,
    ACT_EDIT,
    ACT_CANCEL
)

DRAFTS: dict[int, dict] = {}

def app_run():
    bot = TeleBot(get_bot_token(), parse_mode='HTML')

    @bot.message_handler(commands=["start"])
    def handle_start(message: Message):
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, msg.FIRST_RUN_APP, reply_markup=main_menu_keyboard())

    @bot.message_handler(func= lambda x: x.text in {MAIN_BTN_CREATE, MAIN_BTN_SCHEDULER})
    def handler_main_menu(message: Message):
        if message.text == MAIN_BTN_CREATE:
            return flow_create_publication(message)
        if message.text == MAIN_BTN_SCHEDULER:
            return flow_scheduler(message)
        return None

    def flow_create_publication(message: Message):
        bot.send_message(message.chat.id, msg.ASK_PRODUCT_URL)
        bot.register_next_step_handler(message, handle_product_url)

    def handle_product_url(message: Message):
        url = (message.text or '').strip()

        if not (url.startswith('http://') or url.startswith('https://')):
            bot.send_message(message.chat.id, msg.URL_INVALID)
            return flow_create_publication(message)

        draft = build_stub_product(url) # Временная заглушка
        DRAFTS[message.from_user.id] = draft

        caption = render_preview_caption(draft)
        bot.send_photo(message.chat.id, draft['image_url'], caption=f"{msg.PREVIEW_TITLE}\n\n{caption}", reply_markup=post_action_keyboard())

    @bot.callback_query_handler(func=lambda c: c.data in {ACT_PUBLISH_NOW, ACT_SCHEDULE, ACT_EDIT, ACT_CANCEL})
    def handle_preview_actions(call: CallbackQuery):
        user_id = call.from_user.id
        draft = DRAFTS.get(user_id)

        if call.data == ACT_PUBLISH_NOW:
            bot.answer_callback_query(call.id, "Отправляем…")
            bot.send_message(call.message.chat.id, msg.PUBLISHED_NOW)
        elif call.data == ACT_SCHEDULE:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, 'Здесь будет выбор времени.')
        elif call.data == ACT_EDIT:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, 'Здесь будут правки полей.')
        elif call.data == ACT_CANCEL:
            bot.answer_callback_query(call.id, "Отмена")
            DRAFTS.pop(user_id, None)
            bot.send_message(call.message.chat.id, msg.CANCELLED, reply_markup=main_menu_keyboard())

    """Вспомогательные функции для тестирования."""

    def build_stub_product(url: str) -> dict:
        """Возвращает фиктивные данные товара для предпросмотра."""

        return {
            "title": "Универсальные наушники Refly Sound X",
            "image_url": "https://picsum.photos/seed/refly/800/600",
            "rating": 4.7,
            "price_old": 6990,
            "price_new": 4990,
            "sku": "RC-123456",
            "url": url,
            "tags": ["#ReflyCard", "#ЯМаркет"],
        }

    def render_preview_caption(d: dict) -> str:
        """Собирает подпись для поста в HTML-формате (поддерживается parse_mode='HTML')."""
        price_line = (
            f"<s>{d['price_old']} ₽</s> → <b>{d['price_new']} ₽</b>"
            if d.get('price_old') else f"<b>{d['price_new']} ₽</b>"
        )
        rating_line = f"Рейтинг: {d['rating']}⭐" if d.get('rating') else ""
        tags_line = " ".join(d.get("tags", []))

        parts = [
            f"<b>{d['title']}</b>",
            price_line,
            rating_line,
            f"Артикул: <code>{d['sku']}</code>",
            f"Ссылка: {d['url']}",
            tags_line,
        ]
        return "\n".join([p for p in parts if p])

    def flow_scheduler(message: Message):
        bot.send_message(message.chat.id, msg.SCHEDULER_PUBLIC)

    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    app_run()