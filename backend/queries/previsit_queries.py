from sqlalchemy import text
from sqlalchemy.engine import Connection


def snapshot(conn: Connection, appointment_id: int):
    return conn.execute(text("""
        SELECT appointment_id, appointment_date, time_slot, doctor_id,
               patient_id, patient_name, reason, pre_visit_notes,
               todays_symptoms, active_allergies, active_conditions,
               ongoing_medicines, latest_summary
        FROM v_previsit_snapshot WHERE appointment_id = :a
    """), {"a": appointment_id}).mappings().first()


def by_doctor_on_date(conn: Connection, doctor_id: int, on_date):
    return conn.execute(text("""
        SELECT * FROM v_previsit_snapshot
        WHERE doctor_id = :d AND appointment_date = :dt
        ORDER BY time_slot
    """), {"d": doctor_id, "dt": on_date}).mappings().all()