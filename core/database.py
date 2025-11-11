import sqlite3
from contextlib import closing
from dataclasses import dataclass

from settings.config import DATABASE_PATH


def create_database():
    """Функция для создания таблицы users, если её ешё нет."""

    with closing(sqlite3.connect(DATABASE_PATH)) as connect, closing(connect.cursor()) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                has_connected_bot INTEGER DEFAULT 0,
                channel_username TEXT
            )
        """)
        connect.commit()

@dataclass
class User:
    tag_id: int
    username: str | None
    full_name: str | None
    has_connected_bot: bool
    channel_username: str | None

def _row_to_user(row) -> User:
    return User(row[0], row[1], row[2], bool(row[3]), row[4])

def get_or_create_user(tag_id: int, username: str | None, full_name: str | None) -> User:
    """Функция проверяет есть ли пользователь в базе данных, если нет создаёт его."""

    with closing(sqlite3.connect(DATABASE_PATH)) as connection,  closing(connection.cursor()) as cursor:
        cursor.execute("SELECT tag_id, username, full_name, has_connected_bot, channel_username FROM users WHERE tag_id=?", (tag_id,))
        result = cursor.fetchone()

        if result:
            return _row_to_user(result)

        cursor.execute("INSERT INTO users (tag_id, username, full_name) VALUES (?, ?, ?)", (tag_id, username, full_name))
        connection.commit()

        return User(tag_id, username, full_name, False, None)

def get_user(tag_id: int) -> User | None:
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, closing(connection.cursor()) as cursor:
        cursor.execute("SELECT tag_id, username, full_name, has_connected_bot, channel_username FROM users WHERE tag_id=?", (tag_id,))
        result = cursor.fetchone()

        return _row_to_user(result) if result else None

def update_user(tag_id: int, **fields):
    """Обновляет нужные поля профиля (гибко: можно передать любые колонки)."""

    if not fields:
        return

    cols = ", ".join(f"{k}=?" for k in fields.keys())
    vals = list(fields.values()) + [tag_id]

    with closing(sqlite3.connect(DATABASE_PATH)) as conn, closing(conn.cursor()) as cur:
        cur.execute(f"UPDATE users SET {cols} WHERE tag_id=?", vals)
        conn.commit()
