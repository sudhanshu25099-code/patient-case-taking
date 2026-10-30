from sqlalchemy import text
from sqlalchemy.engine import Connection


CONSENT_COLS = ("consent_id, patient_id, hospital_id, consent_type, valid_from, "
                "valid_to, status, purpose, remarks")


def create_consent(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO patient_consent
            (patient_id, hospital_id, consent_type, valid_from, valid_to,
             status, purpose, remarks)
        VALUES
            (:patient_id, :hospital_id, :consent_type, :valid_from, :valid_to,
             :status, :purpose, :remarks)
    """), d).lastrowid


def get_consent(conn: Connection, consent_id: int):
    return conn.execute(
        text(f"SELECT {CONSENT_COLS} FROM patient_consent WHERE consent_id = :id"),
        {"id": consent_id},
    ).mappings().first()


def list_by_patient(conn: Connection, patient_id: int):
    return conn.execute(text(f"""
        SELECT {CONSENT_COLS} FROM patient_consent
        WHERE patient_id = :p ORDER BY consent_id DESC
    """), {"p": patient_id}).mappings().all()


def revoke(conn: Connection, consent_id: int) -> int:
    return conn.execute(text("""
        UPDATE patient_consent SET status = 'Revoked' WHERE consent_id = :id
    """), {"id": consent_id}).rowcount


# ---------- consent_access ----------
def create_access(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO consent_access
            (consent_id, doctor_id, department_id, access_from, access_to, status)
        VALUES
            (:consent_id, :doctor_id, :department_id, :access_from, :access_to, :status)
    """), d).lastrowid


def get_access(conn: Connection, access_id: int):
    return conn.execute(text("""
        SELECT access_id, consent_id, doctor_id, department_id,
               access_from, access_to, status
        FROM consent_access WHERE access_id = :id
    """), {"id": access_id}).mappings().first()


def list_access(conn: Connection, consent_id: int):
    return conn.execute(text("""
        SELECT access_id, consent_id, doctor_id, department_id,
               access_from, access_to, status
        FROM consent_access WHERE consent_id = :c
    """), {"c": consent_id}).mappings().all()