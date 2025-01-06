from dataclasses import dataclass, field

from data.utils import get_new_uuid


@dataclass
class User:
    name: str
    id: str = field(default_factory=get_new_uuid)
