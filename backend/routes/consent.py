from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection
from sqlalchemy import text

from dependencies import get_db_connection
from queries import consent_queries as q
from schemas.consent import (
    ConsentCreate, ConsentOut, ConsentAccessCreate, ConsentAccessOut,
)

router = APIRouter(prefix="/consent", tags=["consent"])


@router.post("", response_model=ConsentOut, status_code=201)
def create_consent(p: ConsentCreate, conn: Connection = Depends(get_db_connection)):
    cid = q.create_consent(conn, p.model_dump())
    return q.get_consent(conn, cid)


@router.get("/{consent_id}", response_model=ConsentOut)
def get_consent(consent_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_consent(conn, consent_id)
    if not row:
        raise HTTPException(404, "Consent not found")
    return row


@router.get("/patient/{patient_id}", response_model=list[ConsentOut])
def by_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_by_patient(conn, patient_id)


@router.patch("/{consent_id}/revoke", response_model=ConsentOut)
def revoke(consent_id: int, conn: Connection = Depends(get_db_connection)):
    q.revoke(conn, consent_id)
    return q.get_consent(conn, consent_id)


@router.post("/access", response_model=ConsentAccessOut, status_code=201)
def create_access(p: ConsentAccessCreate,
                  conn: Connection = Depends(get_db_connection)):
    aid = q.create_access(conn, p.model_dump())
    return q.get_access(conn, aid)


@router.get("/{consent_id}/access", response_model=list[ConsentAccessOut])
def list_access(consent_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_access(conn, consent_id)


@router.get("/check")
def has_access(patient_id: int, doctor_id: int, conn: Connection = Depends(get_db_connection)):
    row = conn.execute(text("""
        SELECT ca.access_id FROM consent_access ca
        JOIN patient_consent pc ON pc.consent_id = ca.consent_id
        WHERE pc.patient_id = :p AND ca.doctor_id = :d 
          AND pc.status = 'Active' AND ca.status = 'Active'
          AND (pc.valid_to IS NULL OR pc.valid_to > NOW())
    """), {"p": patient_id, "d": doctor_id}).first()
    
    if not row:
        raise HTTPException(status_code=403, detail="No active consent granted to this doctor")
    return {"has_access": True, "access_id": row[0]}