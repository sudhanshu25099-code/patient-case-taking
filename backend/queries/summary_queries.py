from sqlalchemy import text
from sqlalchemy.engine import Connection


SUM_COLS = ("summary_id, patient_id, appointment_id, summary_type, summary_text, "
            "generated_by, generated_at, version_no, is_current")


def create_summary(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO medical_summary
            (patient_id, appointment_id, summary_type, summary_text,
             generated_by, version_no, is_current)
        VALUES
            (:patient_id, :appointment_id, :summary_type, :summary_text,
             :generated_by, :version_no, :is_current)
    """), d).lastrowid


def get_summary(conn: Connection, summary_id: int):
    return conn.execute(
        text(f"SELECT {SUM_COLS} FROM medical_summary WHERE summary_id = :id"),
        {"id": summary_id},
    ).mappings().first()


def list_by_patient(conn: Connection, patient_id: int):
    return conn.execute(text(f"""
        SELECT {SUM_COLS} FROM medical_summary
        WHERE patient_id = :p ORDER BY generated_at DESC
    """), {"p": patient_id}).mappings().all()


def link_document(conn: Connection, summary_id: int, document_id: int, notes=None):
    conn.execute(text("""
        INSERT IGNORE INTO summary_document (summary_id, document_id, notes)
        VALUES (:s, :d, :n)
    """), {"s": summary_id, "d": document_id, "n": notes})


def summary_documents(conn: Connection, summary_id: int):
    return [r["document_id"] for r in conn.execute(text("""
        SELECT document_id FROM summary_document WHERE summary_id = :s
    """), {"s": summary_id}).mappings().all()]