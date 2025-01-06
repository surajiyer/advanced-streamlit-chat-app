from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional

from data.utils import db_connection, get_new_uuid


@dataclass
class Character:
    name: str
    description: str
    image: Optional[bytes] = None
    id: int = field(default_factory=get_new_uuid)

    @classmethod
    @db_connection
    def new(cls, name: str, description: str, image: Optional[bytes] = None, conn=None) -> "Character":
        c = conn.cursor()
        character = cls(name, description, image)
        now = datetime.now(UTC)
        c.execute(
            "INSERT INTO characters (name, description, image, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (character.name, character.description, character.image, now, now),
        )
        return character

    @db_connection
    def save(
        self, name: Optional[str] = None, description: Optional[str] = None, image: Optional[bytes] = None, conn=None
    ):
        c = conn.cursor()
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if image is not None:
            self.image = image
        now = datetime.now(UTC)
        c.execute(
            "UPDATE characters SET name = ?, description = ?, image = ?, updated_at = ? WHERE id = ?",
            (self.name, self.description, self.image, now, self.id),
        )

    @db_connection
    def delete(self, conn=None):
        c = conn.cursor()
        c.execute("DELETE FROM characters WHERE id = ?", (self.id,))

    @classmethod
    @db_connection
    def get_by_id(cls, character_id: int, conn=None) -> "Character":
        c = conn.cursor()
        c.execute("SELECT id, name, description, image FROM characters WHERE id = ?", (character_id,))
        row = c.fetchone()
        return cls(id=row[0], name=row[1], description=row[2], image=row[3])

    @classmethod
    @db_connection
    def get_by_name(cls, name: str, conn=None) -> "Character":
        c = conn.cursor()
        c.execute("SELECT id, name, description, image FROM characters WHERE name = ?", (name,))
        row = c.fetchone()
        return cls(id=row[0], name=row[1], description=row[2], image=row[3])

    @classmethod
    @db_connection
    def get_all(cls, conn=None) -> list["Character"]:
        c = conn.cursor()
        c.execute("SELECT id, name, description, image FROM characters")
        rows = c.fetchall()
        return [cls(id=row[0], name=row[1], description=row[2], image=row[3]) for row in rows]
