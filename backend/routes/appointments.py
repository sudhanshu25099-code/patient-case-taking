from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import appointment_queries as q
from schemas.appointments import (
    AppointmentCreate, AppointmentOut, AppointmentDetail,
    AppointmentSymptomCreate, AppointmentSymptomOut,
    AppointmentNoteCreate, AppointmentNoteOut, AppointmentStatusUpdate,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut, status_code=201)
def create(p: AppointmentCreate, conn: Connection = Depends(get_db_connection)):
    aid = q.create_appointment(conn, p.model_dump())
    return q.get_appointment(conn, aid)


@router.get("/{appointment_id}", response_model=AppointmentDetail)
def get_one(appointment_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_appointment(conn, appointment_id)
    if not row:
        raise HTTPException(404, "Appointment not found")
    return {
        **dict(row),
        "symptoms": q.list_symptoms(conn, appointment_id),
        "notes": q.list_notes(conn, appointment_id),
    }


@router.get("/patient/{patient_id}", response_model=list[AppointmentOut])
def by_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_by_patient(conn, patient_id)


@router.get("/doctor/{doctor_id}", response_model=list[AppointmentOut])
def by_doctor(doctor_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_by_doctor(conn, doctor_id)


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def set_status(appointment_id: int, p: AppointmentStatusUpdate,
               conn: Connection = Depends(get_db_connection)):
    q.update_status(conn, appointment_id, p.status)
    return q.get_appointment(conn, appointment_id)


@router.post("/symptoms", response_model=AppointmentSymptomOut, status_code=201)
def add_symptom(p: AppointmentSymptomCreate,
                conn: Connection = Depends(get_db_connection)):
    sid = q.add_symptom(conn, p.model_dump())
    return {**p.model_dump(), "symptom_id": sid}


@router.post("/notes", response_model=AppointmentNoteOut, status_code=201)
def add_note(p: AppointmentNoteCreate,
             conn: Connection = Depends(get_db_connection)):
    nid = q.add_note(conn, p.model_dump())
    return q.get_note(conn, nid)