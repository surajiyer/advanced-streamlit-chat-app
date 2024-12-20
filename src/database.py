from functools import wraps
import sqlite3
from typing import Optional, List, Dict, Callable

import globals as g


def db_connection(func: Callable):
    @wraps(func)
    def with_connection(*args, **kwargs):
        conn = sqlite3.connect(g.DB_PATH)
        try:
            result = func(*args, conn=conn, **kwargs)
            conn.commit()
        finally:
            conn.close()
        return result
    return with_connection


class Database:
    def __init__(self):
        self.init_db()

    @db_connection
    def init_db(self, conn=None):
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS conversations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, character TEXT)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS messages
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id INTEGER, role TEXT, content TEXT,
                      FOREIGN KEY(conversation_id) REFERENCES conversations(id))"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS characters
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, image TEXT)"""
        )
        # Insert default character if not exists
        c.execute("SELECT COUNT(*) FROM characters WHERE name = ?", (g.DEFAULT_CHARACTER,))
        if c.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO characters (name, description) VALUES (?, ?)",
                (g.DEFAULT_CHARACTER, "Default character for the chatbot"),
            )

    @db_connection
    def save_conversation(self, user: str, character: str, conn=None) -> int:
        c = conn.cursor()
        c.execute("INSERT INTO conversations (user, character) VALUES (?, ?)", (user, character))
        return c.lastrowid

    @db_connection
    def save_message(self, conversation_id: int, role: str, content: str, conn=None):
        c = conn.cursor()
        c.execute("INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)", (conversation_id, role, content))

    @db_connection
    def get_conversations(self, user: str, conn=None) -> List[Dict]:
        c = conn.cursor()
        c.execute("SELECT id, character FROM conversations WHERE user = ?", (user,))
        rows = c.fetchall()
        return [{"id": row[0], "character": row[1]} for row in rows]

    @db_connection
    def get_messages(self, conversation_id: int, conn=None) -> List[Dict]:
        c = conn.cursor()
        c.execute("SELECT role, content FROM messages WHERE conversation_id = ?", (conversation_id,))
        rows = c.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]

    @db_connection
    def save_character(self, name: str, description: str, image_bytes: Optional[bytes] = None, conn=None):
        c = conn.cursor()
        c.execute("INSERT INTO characters (name, description, image) VALUES (?, ?, ?)", (name, description, image_bytes))

    @db_connection
    def get_all_characters(self, conn=None) -> List[Dict]:
        c = conn.cursor()
        c.execute("SELECT id, name, image FROM characters")
        rows = c.fetchall()
        return [{"id": row[0], "name": row[1], "image": row[2]} for row in rows]
