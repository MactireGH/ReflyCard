import threading
import time

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from datetime import datetime

from settings.config import get_bot_token
from settings import messages as msg
from bot.keyboards.common import (
    main_menu_keyboard,
    post_action_keyboard,
    scheduler_list_keyboards,
    MAIN_BTN_CREATE,
    MAIN_BTN_SCHEDULER,
    ACT_PUBLISH_NOW,
    ACT_SCHEDULE,
    ACT_EDIT,
    ACT_CANCEL,
    ACT_JOB_DEL_PREFIX,
    ACT_JOB_PAGE_PREFIX,
)

# Global in memory storage
DRAFTS: dict[int, dict] = {}
USER_STATE: dict[int, dict] = {}
JOBS: dict[int, list[dict]] = {}
JOB_SEQ = 0
LOCK = threading.Lock()

# Utility datetime parser
_DT_FORMATS = ["%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M",]

def app_run():
    bot = TeleBot(get_bot_token(), parse_mode='HTML')

    def parse_local_dt(text: str) -> datetime | None:
        for fmt in _DT_FORMATS:
            try:
                return datetime.strptime(text.strip(), fmt)
            except ValueError:
                continue
        return None

    def scheduler_loop(bot: TeleBot):
        while True:
            now = datetime.now()
            due: list[tuple[int, dict]] = []

            with LOCK:
                for uid, items in list(JOBS.items()):
                    keep = []

                    for job in items:
                        if job["run_at"] <= now:
                            due.append((uid, job))
                        else:
                            keep.append(job)
                    JOBS[uid] = keep
            for uid, job in due:
                try:
                    d = job["draft"]
                    chat_id = job["chat_id"]
                    caption = render_preview_caption(d)
                    bot.send_photo(chat_id, d['image_url'], caption=caption, parse_mode='HTML')
                    bot.send_message(chat_id, msg.PUBLISH_DONE_SCHEDULED)
                except Exception as e:
                    # Логировать/уведомить можно по желанию
                    pass
            time.sleep(5)

    threading.Thread(target=scheduler_loop, args=(bot,), daemon=True).start()

    @bot.callback_query_handler(func=lambda c: c.data == ACT_SCHEDULE)
    def cb_schedule(q: CallbackQuery):
        uid = q.from_user.id
        if uid not in DRAFTS:
            bot.answer_callback_query(q.id, "Нет черновика для планирования.")
            return
        USER_STATE[uid] = {"mode": "await_datetime"}
        bot.answer_callback_query(q.id)
        bot.send_message(q.message.chat.id, msg.SCHEDULE_PROMPT_DATETIME)

    # === NEW: приём даты-времени от пользователя ===
    @bot.message_handler(func=lambda m: USER_STATE.get(m.from_user.id, {}).get("mode") == "await_datetime")
    def handle_dt_input(message: Message):
        uid = message.from_user.id
        dt = parse_local_dt(message.text)
        if not dt:
            bot.send_message(message.chat.id, msg.SCHEDULE_PARSE_ERROR)
            return
        global JOB_SEQ
        with LOCK:
            JOB_SEQ += 1
            job_id = JOB_SEQ
            JOBS.setdefault(uid, []).append({
                "id": job_id,
                "chat_id": message.chat.id,
                "run_at": dt,
                "title": DRAFTS[uid].get("title", "Публикация"),
                "draft": DRAFTS[uid].copy(),
            })
        USER_STATE.pop(uid, None)
        bot.send_message(message.chat.id, msg.SCHEDULE_SAVED.format(dt=dt.strftime('%Y-%m-%d %H:%M')))

    # === NEW: раздел «Планировщик» — показать список задач ===
    @bot.message_handler(func=lambda m: m.text == MAIN_BTN_SCHEDULER)
    def open_scheduler(message: Message):
        uid = message.from_user.id
        tasks = JOBS.get(uid, [])
        if not tasks:
            bot.send_message(message.chat.id, f"<b>{msg.SCHEDULER_TITLE}</b>\n\n{msg.SCHEDULER_EMPTY}",
                             parse_mode='HTML')
            return
        # Сортировка по времени
        tasks_sorted = sorted(tasks, key=lambda x: x['run_at'])
        view = [f"🗂 <b>{msg.SCHEDULER_TITLE}</b>", ""]
        for t in tasks_sorted:
            view.append(f"• #{t['id']} — {t['run_at'].strftime('%Y-%m-%d %H:%M')} — {t['title']}")
        kb = scheduler_list_keyboards([
            {
                "id": t['id'],
                "run_at": t['run_at'].strftime('%Y-%m-%d %H:%M'),
                "title": t['title'],
            }
            for t in tasks_sorted
        ])
        bot.send_message(message.chat.id, "\n".join(view), reply_markup=kb, parse_mode='HTML')

    # === NEW: удаление задачи по кнопке ===
    @bot.callback_query_handler(func=lambda c: c.data.startswith(ACT_JOB_DEL_PREFIX))
    def cb_job_delete(q: CallbackQuery):
        uid = q.from_user.id
        try:
            job_id = int(q.data[len(ACT_JOB_DEL_PREFIX):])
        except ValueError:
            bot.answer_callback_query(q.id, msg.SCHEDULER_ITEM_NOT_FOUND, show_alert=True)
            return
        deleted = False
        with LOCK:
            items = JOBS.get(uid, [])
            keep = []
            for it in items:
                if it['id'] == job_id:
                    deleted = True
                else:
                    keep.append(it)
            JOBS[uid] = keep
        if deleted:
            bot.answer_callback_query(q.id)
            bot.send_message(q.message.chat.id, msg.SCHEDULER_ITEM_DELETED)
        else:
            bot.answer_callback_query(q.id, msg.SCHEDULER_ITEM_NOT_FOUND, show_alert=True)

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