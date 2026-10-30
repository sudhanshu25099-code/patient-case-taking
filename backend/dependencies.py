from typing import Generator
from sqlalchemy.engine import Connection
from database import engine


def get_db_connection() -> Generator[Connection, None, None]:
    with engine.connect() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise