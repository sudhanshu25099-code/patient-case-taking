from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import appointment_queries as q
from schemas.appointments import (
    AppointmentCreate, AppointmentDetail,
    AppointmentSymptomCreate, AppointmentSymptomOut,
    AppointmentNoteCreate, AppointmentNoteOut, AppointmentStatusUpdate,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _format_appt(row):
    if not row:
        return None
    d = dict(row)
    ts = d.get("time_slot")
    if hasattr(ts, "total_seconds"):
        tot = int(ts.total_seconds())
        d["time_slot"] = f"{tot // 3600:02d}:{(tot % 3600) // 60:02d}:{tot % 60:02d}"
    elif ts is not None:
        d["time_slot"] = str(ts)
    return d


@router.get("")
def list_appointments(conn: Connection = Depends(get_db_connection)):
    return [_format_appt(a) for a in q.list_all(conn)]


@router.post("", status_code=201)
def create(p: AppointmentCreate, conn: Connection = Depends(get_db_connection)):
    aid = q.create_appointment(conn, p.model_dump())
    row = q.get_appointment(conn, aid)
    return _format_appt(row)


@router.get("/{appointment_id}")
def get_one(appointment_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_appointment(conn, appointment_id)
    if not row:
        raise HTTPException(404, "Appointment not found")
    d = _format_appt(row)
    d["symptoms"] = [dict(s) for s in q.list_symptoms(conn, appointment_id)]
    d["notes"] = [dict(n) for n in q.list_notes(conn, appointment_id)]
    return d


@router.put("/{appointment_id}")
def reschedule(appointment_id: int, p: AppointmentCreate, conn: Connection = Depends(get_db_connection)):
    if q.update_appointment(conn, appointment_id, p.model_dump()) == 0:
        raise HTTPException(404, "Appointment not found")
    row = q.get_appointment(conn, appointment_id)
    return _format_appt(row)


@router.post("/{appointment_id}/check-in")
def check_in(appointment_id: int, conn: Connection = Depends(get_db_connection)):
    if q.check_in_appointment(conn, appointment_id) == 0:
        raise HTTPException(404, "Appointment not found")
    return {"ok": True}


@router.get("/patient/{patient_id}")
def by_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    return [_format_appt(r) for r in q.list_by_patient(conn, patient_id)]


@router.get("/doctor/{doctor_id}")
def by_doctor(doctor_id: int, conn: Connection = Depends(get_db_connection)):
    return [_format_appt(r) for r in q.list_by_doctor(conn, doctor_id)]


@router.patch("/{appointment_id}/status")
def set_status(appointment_id: int, p: AppointmentStatusUpdate, conn: Connection = Depends(get_db_connection)):
    if q.update_status(conn, appointment_id, p.status) == 0:
        raise HTTPException(404, "Appointment not found")
    row = q.get_appointment(conn, appointment_id)
    return _format_appt(row)


@router.post("/symptoms", response_model=AppointmentSymptomOut, status_code=201)
def add_symptom(p: AppointmentSymptomCreate, conn: Connection = Depends(get_db_connection)):
    sid = q.add_symptom(conn, p.model_dump())
    return {**p.model_dump(), "symptom_id": sid}


@router.post("/notes", response_model=AppointmentNoteOut, status_code=201)
def add_note(p: AppointmentNoteCreate, conn: Connection = Depends(get_db_connection)):
    nid = q.add_note(conn, p.model_dump())
    return {**p.model_dump(), "note_id": nid}
