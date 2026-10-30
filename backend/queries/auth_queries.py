from sqlalchemy import text
from sqlalchemy.engine import Connection

def get_user_by_username(conn: Connection, username: str):
    return conn.execute(text("""
        SELECT user_id, person_id, username, email, password_hash, is_active
        FROM user_account WHERE username = :u
    """), {"u": username}).mappings().first()