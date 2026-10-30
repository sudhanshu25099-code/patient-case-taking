from sqlalchemy import text
from sqlalchemy.engine import Connection


VISIT_COLS = ("visit_id, appointment_id, patient_id, hospital_id, department_id, "
              "doctor_id, visit_date, visit_type, chief_complaint, symptoms, "
              "vitals_summary, notes")


def create_visit(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO visit
            (appointment_id, patient_id, hospital_id, department_id, doctor_id,
             visit_date, visit_type, chief_complaint, symptoms,
             vitals_summary, notes)
        VALUES
            (:appointment_id, :patient_id, :hospital_id, :department_id, :doctor_id,
             :visit_date, :visit_type, :chief_complaint, :symptoms,
             :vitals_summary, :notes)
    """), d).lastrowid


def get_visit(conn: Connection, visit_id: int):
    return conn.execute(
        text(f"SELECT {VISIT_COLS} FROM visit WHERE visit_id = :id"),
        {"id": visit_id},
    ).mappings().first()


def list_visits_by_patient(conn: Connection, patient_id: int):
    return conn.execute(text(f"""
        SELECT {VISIT_COLS} FROM visit
        WHERE patient_id = :p ORDER BY visit_date DESC
    """), {"p": patient_id}).mappings().all()


# ---------- DIAGNOSIS ----------
def add_diagnosis(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO visit_diagnosis
            (visit_id, diagnosis_code, diagnosis_name, diagnosis_type, notes)
        VALUES (:visit_id, :diagnosis_code, :diagnosis_name, :diagnosis_type, :notes)
    """), d).lastrowid


def list_diagnoses(conn: Connection, visit_id: int):
    return conn.execute(text("""
        SELECT diagnosis_id, visit_id, diagnosis_code, diagnosis_name,
               diagnosis_type, notes
        FROM visit_diagnosis WHERE visit_id = :v
    """), {"v": visit_id}).mappings().all()


# ---------- PROCEDURE ----------
def add_procedure(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO visit_procedure
            (visit_id, procedure_name, procedure_type, notes)
        VALUES (:visit_id, :procedure_name, :procedure_type, :notes)
    """), d).lastrowid


def list_procedures(conn: Connection, visit_id: int):
    return conn.execute(text("""
        SELECT procedure_id, visit_id, procedure_name, procedure_type, notes
        FROM visit_procedure WHERE visit_id = :v
    """), {"v": visit_id}).mappings().all()


# ---------- VISIT NOTE ----------
def add_visit_note(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO visit_note
            (visit_id, note_type, title, content, added_by)
        VALUES (:visit_id, :note_type, :title, :content, :added_by)
    """), d).lastrowid


def get_visit_note(conn: Connection, note_id: int):
    return conn.execute(text("""
        SELECT note_id, visit_id, note_type, title, content, added_by, added_at
        FROM visit_note WHERE note_id = :id
    """), {"id": note_id}).mappings().first()


def list_visit_notes(conn: Connection, visit_id: int):
    return conn.execute(text("""
        SELECT note_id, visit_id, note_type, title, content, added_by, added_at
        FROM visit_note WHERE visit_id = :v ORDER BY added_at
    """), {"v": visit_id}).mappings().all()


# ---------- ALLERGY ----------
def create_allergy(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO allergy
            (patient_id, allergen, allergy_type, reaction, severity,
             status, noted_date, recorded_by, notes)
        VALUES
            (:patient_id, :allergen, :allergy_type, :reaction, :severity,
             :status, :noted_date, :recorded_by, :notes)
    """), d).lastrowid


def list_allergies(conn: Connection, patient_id: int):
    return conn.execute(text("""
        SELECT allergy_id, patient_id, allergen, allergy_type, reaction,
               severity, status, noted_date, recorded_by, notes
        FROM allergy WHERE patient_id = :p ORDER BY allergy_id DESC
    """), {"p": patient_id}).mappings().all()


# ---------- PATIENT CONDITION ----------
def create_condition(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO patient_condition
            (patient_id, source_visit_id, condition_name, icd_code,
             condition_type, onset_date, status, notes)
        VALUES
            (:patient_id, :source_visit_id, :condition_name, :icd_code,
             :condition_type, :onset_date, :status, :notes)
    """), d).lastrowid


def list_conditions(conn: Connection, patient_id: int):
    return conn.execute(text("""
        SELECT condition_id, patient_id, source_visit_id, condition_name,
               icd_code, condition_type, onset_date, status, notes
        FROM patient_condition WHERE patient_id = :p ORDER BY condition_id DESC
    """), {"p": patient_id}).mappings().all()


# ---------- PRESCRIPTION ----------
def create_prescription(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO prescription
            (visit_id, patient_id, doctor_id, prescribed_date, notes)
        VALUES (:visit_id, :patient_id, :doctor_id, :prescribed_date, :notes)
    """), d).lastrowid


def add_prescription_item(conn: Connection, d: dict) -> int:
    return conn.execute(text("""
        INSERT INTO prescription_item
            (prescription_id, medicine_name, dosage, frequency, route,
             duration_days, start_date, end_date, is_ongoing, instructions)
        VALUES
            (:prescription_id, :medicine_name, :dosage, :frequency, :route,
             :duration_days, :start_date, :end_date, :is_ongoing, :instructions)
    """), d).lastrowid


def get_prescription(conn: Connection, prescription_id: int):
    return conn.execute(text("""
        SELECT prescription_id, visit_id, patient_id, doctor_id,
               prescribed_date, notes
        FROM prescription WHERE prescription_id = :id
    """), {"id": prescription_id}).mappings().first()


def list_prescription_items(conn: Connection, prescription_id: int):
    return conn.execute(text("""
        SELECT item_id, prescription_id, medicine_name, dosage, frequency,
               route, duration_days, start_date, end_date, is_ongoing, instructions
        FROM prescription_item WHERE prescription_id = :p ORDER BY item_id
    """), {"p": prescription_id}).mappings().all()