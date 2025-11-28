import sqlite3
from typing import cast
from contextlib import closing
from core.db.create_database import User
from core.db.create_database import get_connection, row_to_class


def normalize_field(value: str | None) -> str | None:
    """Normalize a string value by trimming whitespace and converting it to lowercase."""

    return value.strip().lower() if value else None

def get_user(user_id: int) -> User | None:
    """Searches for and returns the user if found in the database"""
    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)
        cursor.execute("""SELECT user_id, username, first_name, last_name, registered_date
                          FROM users
                          WHERE user_id = ?
                       """, (user_id,)
                       )

        person = cursor.fetchone()
        return row_to_class(User, person) if person else None


def create_user(user_id: int, username: str, first_name: str, last_name: str, registered_date: str) -> User:
    """Creates and saves new users to the database."""

    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)
        cursor.execute("""INSERT INTO users (user_id, username, first_name, last_name, registered_date)
                          VALUES (?, ?, ?, ?, ?)""",
                       (user_id, username, first_name, last_name, registered_date))

        connection.commit()
        return User(user_id, username, first_name, last_name, registered_date)


def update_user(user_id: int, **fields) -> bool | None:
    """Update and saves current users to the database."""

    if not fields:
        return False

    columns = ', '.join(f"{key}=?" for key in fields.keys())
    values = list(fields.values()) + [user_id]

    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)
        cursor.execute(f"""UPDATE users SET {columns} WHERE user_id=?""", values)

        connection.commit()
        return cursor.rowcount > 0