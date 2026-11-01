import json
from sqlalchemy import text
from sqlalchemy.engine import Connection


# ---------- NOTIFICATION ----------
def create_notification(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO notification
            (user_id, appointment_id, title, message, type, is_read)
        VALUES
            (:user_id, :appointment_id, :title, :message, :type, :is_read)
    """), d).lastrowid


def get_notification(conn: Connection, notification_id: int):
    return conn.execute(text("""
        SELECT notification_id, user_id, appointment_id, title, message,
               type, is_read, created_at
        FROM notification WHERE notification_id = :id
    """), {"id": notification_id}).mappings().first()


def list_notifications(conn: Connection, user_id: int):
    return conn.execute(text("""
        SELECT notification_id, user_id, appointment_id, title, message,
               type, is_read, created_at
        FROM notification WHERE user_id = :u ORDER BY created_at DESC
    """), {"u": user_id}).mappings().all()


def mark_read(conn: Connection, notification_id: int) -> int:
    return conn.execute(text("""
        UPDATE notification SET is_read = TRUE WHERE notification_id = :id
    """), {"id": notification_id}).rowcount


# ---------- ACCESS LOG ----------
def create_access_log(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO access_log
            (user_id, patient_id, document_id, action_type, ip_address, remarks)
        VALUES
            (:user_id, :patient_id, :document_id, :action_type, :ip_address, :remarks)
    """), d).lastrowid


def get_access_log(conn: Connection, log_id: int):
    return conn.execute(text("""
        SELECT log_id, user_id, patient_id, document_id, action_type,
               action_time, ip_address, remarks
        FROM access_log WHERE log_id = :id
    """), {"id": log_id}).mappings().first()


def list_access_logs(conn: Connection, user_id: int):
    return conn.execute(text("""
        SELECT log_id, user_id, patient_id, document_id, action_type,
               action_time, ip_address, remarks
        FROM access_log WHERE user_id = :u ORDER BY action_time DESC
    """), {"u": user_id}).mappings().all()


# ---------- AUDIT TRAIL ----------
def create_audit(conn: Connection, d: dict) -> int:
    payload = dict(d)
    for k in ("old_value", "new_value"):
        if payload.get(k) is not None and not isinstance(payload[k], str):
            payload[k] = json.dumps(payload[k])
    return conn.execute(text("""
        INSERT INTO audit_trail
            (user_id, table_name, record_id, action_type,
             old_value, new_value, remarks)
        VALUES
            (:user_id, :table_name, :record_id, :action_type,
             :old_value, :new_value, :remarks)
    """), payload).lastrowid


def get_audit(conn: Connection, audit_id: int):
    return conn.execute(text("""
        SELECT audit_id, user_id, table_name, record_id, action_type,
               old_value, new_value, action_time, remarks
        FROM audit_trail WHERE audit_id = :id
    """), {"id": audit_id}).mappings().first()


def list_audit_for_table(conn: Connection, table_name: str):
    return conn.execute(text("""
        SELECT audit_id, user_id, table_name, record_id, action_type,
               old_value, new_value, action_time, remarks
        FROM audit_trail WHERE table_name = :t ORDER BY action_time DESC
    """), {"t": table_name}).mappings().all()