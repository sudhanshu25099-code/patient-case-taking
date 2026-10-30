from sqlalchemy import text
from sqlalchemy.engine import Connection


APPT_COLS = ("appointment_id, patient_id, hospital_id, doctor_id, "
             "appointment_date, time_slot, reason, pre_visit_notes, "
             "is_follow_up, status, notes, booked_by, created_at")


def create_appointment(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO appointment
            (patient_id, hospital_id, doctor_id, appointment_date, time_slot,
             reason, pre_visit_notes, is_follow_up, status, notes, booked_by)
        VALUES
            (:patient_id, :hospital_id, :doctor_id, :appointment_date, :time_slot,
             :reason, :pre_visit_notes, :is_follow_up, :status, :notes, :booked_by)
    """), d).lastrowid


def get_appointment(conn: Connection, appointment_id: int):
    return conn.execute(
        text(f"SELECT {APPT_COLS} FROM appointment WHERE appointment_id = :id"),
        {"id": appointment_id},
    ).mappings().first()


def update_appointment(conn, id, d): 
    return conn.execute(text("""
        UPDATE appointment SET appointment_date=:appointment_date, time_slot=:time_slot,
          reason=:reason, status=:status WHERE appointment_id=:id
    """), {**d, "id": id}).rowcount

def check_in_appointment(conn, id): 
    return conn.execute(text("""
        UPDATE appointment SET status='Completed' WHERE appointment_id=:id
    """), {"id": id}).rowcount

def list_by_patient(conn: Connection, patient_id: int):
    return conn.execute(text(f"""
        SELECT {APPT_COLS} FROM appointment
        WHERE patient_id = :p ORDER BY appointment_date DESC, time_slot DESC
    """), {"p": patient_id}).mappings().all()


def list_by_doctor(conn: Connection, doctor_id: int):
    return conn.execute(text(f"""
        SELECT {APPT_COLS} FROM appointment
        WHERE doctor_id = :d ORDER BY appointment_date DESC, time_slot DESC
    """), {"d": doctor_id}).mappings().all()


def update_status(conn: Connection, appointment_id: int, status: str) -> int:
    return conn.execute(text("""
        UPDATE appointment SET status = :s WHERE appointment_id = :id
    """), {"s": status, "id": appointment_id}).rowcount


# ---------- SYMPTOMS ----------
def add_symptom(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO appointment_symptom
            (appointment_id, symptom_name, severity, since_date, notes)
        VALUES (:appointment_id, :symptom_name, :severity, :since_date, :notes)
    """), d).lastrowid


def list_symptoms(conn: Connection, appointment_id: int):
    return conn.execute(text("""
        SELECT symptom_id, appointment_id, symptom_name, severity, since_date, notes
        FROM appointment_symptom WHERE appointment_id = :a
    """), {"a": appointment_id}).mappings().all()


# ---------- NOTES ----------
def add_note(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO appointment_note (appointment_id, note_text, added_by)
        VALUES (:appointment_id, :note_text, :added_by)
    """), d).lastrowid


def get_note(conn: Connection, appt_note_id: int):
    return conn.execute(text("""
        SELECT appt_note_id, appointment_id, note_text, added_by, added_at
        FROM appointment_note WHERE appt_note_id = :id
    """), {"id": appt_note_id}).mappings().first()


def list_notes(conn: Connection, appointment_id: int):
    return conn.execute(text("""
        SELECT appt_note_id, appointment_id, note_text, added_by, added_at
        FROM appointment_note WHERE appointment_id = :a ORDER BY added_at
    """), {"a": appointment_id}).mappings().all()