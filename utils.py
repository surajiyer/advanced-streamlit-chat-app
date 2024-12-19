import json
from typing import Optional, List, Dict
import requests
import sqlite3
import streamlit as st
import globals as g


def get_api_key():
    return st.secrets["wartsila_gpt_api_key"]


def complete_chat(model="gpt-3.5-turbo", messages=None) -> Optional[dict]:
    valid_models = ["gpt-35-turbo-16k", "gpt-4", "gpt-4o"]
    if model not in valid_models:
        raise ValueError(f"Invalid model: {model}. Choose from {valid_models}")

    if messages is None:
        return

    url = "https://api.wartsila.com/int/wartsila-gpt/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": get_api_key(),
        "model": model,
    }
    data = json.dumps({"messages": messages})
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Request failed with status code {response.status_code}")


def init_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS chat_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, character TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, log_id INTEGER, role TEXT, content TEXT,
                  FOREIGN KEY(log_id) REFERENCES chat_logs(id))"""
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
    conn.commit()
    conn.close()


def save_chat_log(user: str, character: str) -> int:
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat_logs (user, character) VALUES (?, ?)", (user, character))
    log_id = c.lastrowid
    conn.commit()
    conn.close()
    return log_id


def save_message(log_id: int, role: str, content: str):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (log_id, role, content) VALUES (?, ?, ?)", (log_id, role, content))
    conn.commit()
    conn.close()


def get_chat_logs(user: str) -> List[Dict]:
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT id, character FROM chat_logs WHERE user = ?", (user,))
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "character": row[1]} for row in rows]


def get_messages(log_id: int) -> List[Dict]:
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE log_id = ?", (log_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]


def save_character(name: str, description: str, image_bytes: Optional[bytes] = None):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO characters (name, description, image) VALUES (?, ?, ?)", (name, description, image_bytes))
    conn.commit()
    conn.close()


def get_all_characters() -> List[Dict]:
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT id, name, image FROM characters")
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "image": row[2]} for row in rows]
