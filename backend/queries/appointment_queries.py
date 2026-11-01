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
    return conn.execute(text("""
        SELECT a.appointment_id, a.patient_id, a.hospital_id, a.doctor_id,
               a.appointment_date, a.time_slot, a.reason, a.pre_visit_notes,
               a.is_follow_up, a.status, a.notes, a.booked_by, a.created_at,
               p_pat.full_name as patient_name,
               p_doc.full_name as doctor_name,
               d.specialization as doctor_specialization,
               h.name as hospital_name
        FROM appointment a
        JOIN patient_profile pt ON a.patient_id = pt.patient_id
        JOIN person p_pat ON pt.person_id = p_pat.person_id
        JOIN doctor_profile d ON a.doctor_id = d.doctor_id
        JOIN person p_doc ON d.person_id = p_doc.person_id
        JOIN hospital h ON a.hospital_id = h.hospital_id
        WHERE a.appointment_id = :id
    """), {"id": appointment_id}).mappings().first()


def list_all(conn: Connection):
    return conn.execute(text("""
        SELECT a.appointment_id, a.patient_id, a.hospital_id, a.doctor_id,
               a.appointment_date, a.time_slot, a.reason, a.pre_visit_notes,
               a.is_follow_up, a.status, a.notes, a.booked_by, a.created_at,
               p_pat.full_name as patient_name,
               p_pat.phone as patient_phone,
               p_doc.full_name as doctor_name,
               d.specialization as doctor_specialization,
               h.name as hospital_name
        FROM appointment a
        JOIN patient_profile pt ON a.patient_id = pt.patient_id
        JOIN person p_pat ON pt.person_id = p_pat.person_id
        JOIN doctor_profile d ON a.doctor_id = d.doctor_id
        JOIN person p_doc ON d.person_id = p_doc.person_id
        JOIN hospital h ON a.hospital_id = h.hospital_id
        ORDER BY a.appointment_date DESC, a.time_slot DESC
    """)).mappings().all()


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
    return conn.execute(text("""
        SELECT a.appointment_id, a.patient_id, a.hospital_id, a.doctor_id,
               a.appointment_date, a.time_slot, a.reason, a.pre_visit_notes,
               a.is_follow_up, a.status, a.notes, a.booked_by, a.created_at,
               p_pat.full_name as patient_name,
               p_doc.full_name as doctor_name,
               d.specialization as doctor_specialization,
               h.name as hospital_name
        FROM appointment a
        JOIN patient_profile pt ON a.patient_id = pt.patient_id
        JOIN person p_pat ON pt.person_id = p_pat.person_id
        JOIN doctor_profile d ON a.doctor_id = d.doctor_id
        JOIN person p_doc ON d.person_id = p_doc.person_id
        JOIN hospital h ON a.hospital_id = h.hospital_id
        WHERE a.patient_id = :p
        ORDER BY a.appointment_date DESC, a.time_slot DESC
    """), {"p": patient_id}).mappings().all()


def list_by_doctor(conn: Connection, doctor_id: int):
    return conn.execute(text("""
        SELECT a.appointment_id, a.patient_id, a.hospital_id, a.doctor_id,
               a.appointment_date, a.time_slot, a.reason, a.pre_visit_notes,
               a.is_follow_up, a.status, a.notes, a.booked_by, a.created_at,
               p_pat.full_name as patient_name,
               p_pat.phone as patient_phone,
               p_doc.full_name as doctor_name,
               h.name as hospital_name
        FROM appointment a
        JOIN patient_profile pt ON a.patient_id = pt.patient_id
        JOIN person p_pat ON pt.person_id = p_pat.person_id
        JOIN doctor_profile d ON a.doctor_id = d.doctor_id
        JOIN person p_doc ON d.person_id = p_doc.person_id
        JOIN hospital h ON a.hospital_id = h.hospital_id
        WHERE a.doctor_id = :d
        ORDER BY a.appointment_date DESC, a.time_slot DESC
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
