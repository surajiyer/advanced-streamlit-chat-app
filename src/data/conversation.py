from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional

from data.utils import db_connection, get_new_uuid
from data.user import User
from data.character import Character


@dataclass
class Conversation:
    user: User
    character: Character
    title: str
    messages: list[dict] = field(default_factory=list)
    id: str = field(default_factory=get_new_uuid)

    @classmethod
    @db_connection
    def new(cls, user: User, character: Character, title: Optional[str] = None, conn=None) -> "Conversation":
        assert isinstance(user, User)
        assert isinstance(character, Character)

        c = conn.cursor()
        if title is None:
            title = f"{character.name}: Untitled Conversation"
        conversation = cls(user=user, character=character, title=title)
        now = datetime.now(UTC)
        c.execute(
            "INSERT INTO conversations (id, user, character, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (conversation.id, user.id, character.name, title, now, now),
        )
        return conversation

    @db_connection
    def save(self, user: Optional[User], character: Optional[Character], title: Optional[str] = None, conn=None):
        assert isinstance(user, User)
        assert isinstance(character, Character)

        c = conn.cursor()
        if user is not None:
            self.user = user
        if character is not None:
            self.character = character
        if title is not None:
            self.title = title
        now = datetime.now(UTC)
        c.execute(
            "UPDATE conversations SET user = ?, character = ?, title = ?, updated_at = ? WHERE id = ?",
            (self.user.id, self.character.name, self.title, now, self.id),
        )

    @db_connection
    def save_message(self, role: str, content: str, conn=None):
        c = conn.cursor()
        now = datetime.now(UTC)
        c.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (self.id, role, content, now, now),
        )
        self.messages.append({"role": role, "content": content})

    @db_connection
    def get_messages(self, conn=None) -> list[dict]:
        c = conn.cursor()
        c.execute("SELECT role, content FROM messages WHERE conversation_id = ?", (self.id,))
        rows = c.fetchall()
        for row in rows:
            self.messages.append({"role": row[0], "content": row[1]})

    @classmethod
    @db_connection
    def get_all(cls, user: User, conn=None) -> list["Conversation"]:
        assert isinstance(user, User)

        c = conn.cursor()
        c.execute("SELECT id, character, title FROM conversations WHERE user = ?", (user.id,))
        rows = c.fetchall()
        conversations = []
        for row in rows:
            character = Character.get_by_name(row[1])
            conversation = cls(
                id=row[0],
                user=user,
                character=character,
                title=row[2],
            )
            conversations.append(conversation)
        return conversations
