import sqlite3
from contextlib import closing
from dataclasses import dataclass, fields
from typing import cast

from settings.config import DATABASE_MAIN_PATH

def get_connection():
    """Creates a database connection with foreign key support"""

    connection = sqlite3.connect(DATABASE_MAIN_PATH)
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection


def create_tables():
    """Creates tables to store user, bots, channels, posts if it does not exist."""

    with (closing(get_connection()) as connection, closing(connection.cursor()) as cursor):
        connection, cursor = cast(sqlite3.Connection, connection), cast(sqlite3.Cursor, cursor)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id         INTEGER PRIMARY KEY,
                           username        TEXT UNIQUE,
                           first_name      TEXT,
                           last_name       TEXT,
                           registered_date TEXT NOT NULL
                       )
                       """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS client_bots
                          (
                              bot_id       INTEGER PRIMARY KEY,
                              user_id      INTEGER NOT NULL,
                              bot_name     TEXT,
                              bot_username TEXT    NOT NULL UNIQUE,
                              bot_token    TEXT    NOT NULL UNIQUE,
                              bot_created  TEXT    NOT NULL,

                              FOREIGN KEY (user_id) REFERENCES users (user_id)
                                  ON DELETE CASCADE ON UPDATE CASCADE
                          )
                       """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS channels
                          (
                              channel_id    INTEGER PRIMARY KEY,
                              user_id       INTEGER NOT NULL,
                              bot_id        INTEGER NOT NULL,
                              channel_tg_id INTEGER NOT NULL UNIQUE,
                              channel_name  TEXT    NOT NULL,
                              channel_added TEXT    NOT NULL,

                              FOREIGN KEY (user_id) REFERENCES users (user_id)
                                  ON DELETE CASCADE ON UPDATE CASCADE,
                              FOREIGN KEY (bot_id) REFERENCES client_bots (bot_id)
                                  ON DELETE CASCADE ON UPDATE CASCADE
                          )""")

        connection.commit()

@dataclass()
class User:
    user_id: int
    username: str
    first_name: str
    last_name: str
    registered_date: str


@dataclass()
class ClientBot:
    bot_id: int
    user_id: int
    bot_name: str
    bot_username: str
    bot_token: str
    bot_created: str


@dataclass()
class Channel:
    channel_id: int
    user_id: int
    bot_id: int
    channel_tg_id: int
    channel_username: str
    channel_name: str
    channel_added: str

def row_to_class(cls, request: tuple):
    """Universal mapping."""

    values = dict(zip((element.name for element in fields(cls)), request))

    return cls(**values)

