from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection
from sqlalchemy import text

from dependencies import get_db_connection
from queries import summary_queries as q
from schemas.medical_summary import MedicalSummaryCreate, MedicalSummaryOut

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("", response_model=MedicalSummaryOut, status_code=201)
def create(p: MedicalSummaryCreate, conn: Connection = Depends(get_db_connection)):
    data = p.model_dump(exclude={"document_ids", "document_notes"})
    sid = q.create_summary(conn, data)
    for i, did in enumerate(p.document_ids):
        note = p.document_notes[i] if p.document_notes and i < len(p.document_notes) else None
        q.link_document(conn, sid, did, note)
    return {**q.get_summary(conn, sid),
            "document_ids": q.summary_documents(conn, sid)}


@router.get("/{summary_id}", response_model=MedicalSummaryOut)
def get_one(summary_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_summary(conn, summary_id)
    if not row:
        raise HTTPException(404, "Summary not found")
    return {**row, "document_ids": q.summary_documents(conn, summary_id)}


@router.get("/patient/{patient_id}", response_model=list[MedicalSummaryOut])
def by_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    rows = q.list_by_patient(conn, patient_id)
    return [{**r, "document_ids": q.summary_documents(conn, r["summary_id"])}
            for r in rows]

@router.post("/generate/{appointment_id}", response_model=MedicalSummaryOut)
def generate_summary(appointment_id: int, conn: Connection = Depends(get_db_connection)):
    snapshot = conn.execute(text("""
        SELECT patient_id, latest_summary FROM v_previsit_snapshot WHERE appointment_id = :a
    """), {"a": appointment_id}).mappings().first()
    if not snapshot:
        raise HTTPException(404, "Appointment not found")
    
    data = {
        "patient_id": snapshot["patient_id"],
        "appointment_id": appointment_id,
        "summary_type": "Pre-visit",
        "summary_text": snapshot["latest_summary"] or "No previous summary available.",
        "generated_by": "System",
        "version_no": 1,
        "is_current": True
    }
    sid = q.create_summary(conn, data)
    return {**q.get_summary(conn, sid), "document_ids": []}