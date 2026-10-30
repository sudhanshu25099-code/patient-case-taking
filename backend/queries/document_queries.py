from sqlalchemy import text
from sqlalchemy.engine import Connection


def create_doc_type(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO document_type (name, description)
        VALUES (:name, :description)
    """), d).lastrowid


def list_doc_types(conn: Connection):
    return conn.execute(text("""
        SELECT document_type_id, name, description
        FROM document_type ORDER BY document_type_id
    """)).mappings().all()


def create_tag(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO document_tag (name, description)
        VALUES (:name, :description)
    """), d).lastrowid


def list_tags(conn: Connection):
    return conn.execute(text("""
        SELECT tag_id, name, description FROM document_tag ORDER BY tag_id
    """)).mappings().all()


DOC_COLS = ("document_id, patient_id, visit_id, document_type_id, test_result_id, "
            "title, description, file_path, file_size, mime_type, document_date, "
            "ocr_status, verification_status, uploaded_by, uploaded_at")


def create_document(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO medical_document
            (patient_id, visit_id, document_type_id, test_result_id, title,
             description, file_path, file_size, mime_type, document_date,
             ocr_text, ocr_status, verification_status, uploaded_by)
        VALUES
            (:patient_id, :visit_id, :document_type_id, :test_result_id, :title,
             :description, :file_path, :file_size, :mime_type, :document_date,
             :ocr_text, :ocr_status, :verification_status, :uploaded_by)
    """), d).lastrowid


def get_document(conn: Connection, document_id: int):
    return conn.execute(
        text(f"SELECT {DOC_COLS} FROM medical_document WHERE document_id = :id"),
        {"id": document_id},
    ).mappings().first()


def list_documents_by_patient(conn: Connection, patient_id: int):
    return conn.execute(text(f"""
        SELECT {DOC_COLS} FROM medical_document
        WHERE patient_id = :p ORDER BY uploaded_at DESC
    """), {"p": patient_id}).mappings().all()


def link_tag(conn: Connection, document_id: int, tag_id: int):
    conn.execute(text("""
        INSERT IGNORE INTO document_tag_mapping (document_id, tag_id)
        VALUES (:d, :t)
    """), {"d": document_id, "t": tag_id})


def doc_tags(conn: Connection, document_id: int):
    return [r["tag_id"] for r in conn.execute(text("""
        SELECT tag_id FROM document_tag_mapping WHERE document_id = :d
    """), {"d": document_id}).mappings().all()]