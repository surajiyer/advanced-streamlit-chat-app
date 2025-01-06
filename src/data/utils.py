from functools import wraps
import sqlite3
from typing import Callable
import uuid

import globals as g


def get_new_uuid() -> str:
    return str(uuid.uuid4())


def db_connection(func: Callable):
    @wraps(func)
    def with_connection(*args, **kwargs):
        conn = sqlite3.connect(g.DB_PATH)
        try:
            if "conn" not in kwargs:
                kwargs["conn"] = conn
            result = func(*args, **kwargs)
            conn.commit()
        finally:
            conn.close()
        return result

    return with_connection
