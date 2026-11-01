from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import previsit_queries as q
from schemas.previsit import PreVisitSnapshot

router = APIRouter(prefix="/previsit", tags=["previsit"])


@router.get("/appointment/{appointment_id}", response_model=PreVisitSnapshot)
def snapshot_for_appointment(appointment_id: int,
                              conn: Connection = Depends(get_db_connection)):
    row = q.snapshot(conn, appointment_id)
    if not row:
        raise HTTPException(404, "Appointment not found")
    return row


@router.get("/doctor/{doctor_id}", response_model=list[PreVisitSnapshot])
def by_doctor(doctor_id: int, on: date,
              conn: Connection = Depends(get_db_connection)):
    return q.by_doctor_on_date(conn, doctor_id, on)