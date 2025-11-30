import sqlite3
from contextlib import closing
from typing import cast
from core.db.create_database import ClientBot
from core.db.create_database import get_connection, row_to_class


def get_client_bot(user_id: int) -> ClientBot | None:
    """Searches for and returns the client bot if found in the database."""

    with closing(get_connection()) as connection, closing(connection.cursor) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)

        cursor.execute("""SELECT bot_id, user_id, bot_name, bot_username, bot_token, bot_created
                          FROM client_bots
                          WHERE user_id = ?""", (user_id,))

        bot = cursor.fetchone()
        return row_to_class(ClientBot, bot) if bot else None


def get_client_token(token: str) -> bool:
    """Searches for the token in the database."""

    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)

        cursor.execute("""SELECT 1 
                          FROM client_bots 
                          WHERE bot_token=? 
                          LIMIT 1""", (token,))

        return cursor.fetchone() is not None


def create_client_bot(bot_id: int, user_id: int, bot_name: str, bot_username: str, bot_token: str, bot_created: str) -> ClientBot:
    """Creates and saves new client bot to the database."""

    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)

        cursor.execute("""INSERT INTO client_bots (bot_id, user_id, bot_name, bot_username, bot_token, bot_created)
                          VALUES (?, ?, ?, ?, ?, ?)""",
                       (bot_id, user_id, bot_name, bot_username, bot_token, bot_created))

        connection.commit()
        bot_id = cursor.lastrowid

        return ClientBot(bot_id=bot_id,
                         user_id=user_id,
                         bot_name=bot_name,
                         bot_username=bot_username,
                         bot_token=bot_token,
                         bot_created=bot_created)
