import sqlite3
from contextlib import closing
from typing import cast

from core.db.create_database import get_connection
from core.db.create_database import Channel


def is_connect_channel(channel_id: str) -> bool:
    """Searches for the channel in the database."""

    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)

        cursor.execute("""SELECT 1 
                          FROM channels 
                          WHERE channel_id=? 
                          LIMIT 1""", (channel_id,))

        return cursor.fetchone() is not None

def connect_channel(channel_id, user_id, bot_id, channel_name, channel_added) -> Channel:
    """Creates and saves new channel to the database."""

    with closing(get_connection()) as connection, closing(connection.cursor()) as cursor:
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)

        cursor.execute("""INSERT INTO channels (channel_id, user_id, bot_id, channel_name, channel_added)
                          VALUES (?, ?, ?, ?, ?)""", (channel_id, user_id, bot_id, channel_name, channel_added))

        connection.commit()
        return Channel(channel_id, user_id, bot_id, channel_name, channel_added)