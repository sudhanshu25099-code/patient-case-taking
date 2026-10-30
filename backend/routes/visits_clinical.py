from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.engine import Connection

from dependencies import get_db_connection
from queries import visit_queries as q
from schemas.visits_clinical import (
    VisitCreate, VisitOut, VisitDiagnosisCreate, VisitDiagnosisOut,
    VisitProcedureCreate, VisitProcedureOut, VisitNoteCreate, VisitNoteOut,
    AllergyCreate, AllergyOut, PatientConditionCreate, PatientConditionOut,
    PrescriptionCreate, PrescriptionOut,
)

router = APIRouter(prefix="/visits", tags=["visits"])


# ---- visits ----
@router.post("", response_model=VisitOut, status_code=201)
def create_visit(p: VisitCreate, conn: Connection = Depends(get_db_connection)):
    vid = q.create_visit(conn, p.model_dump())
    return q.get_visit(conn, vid)


@router.get("/{visit_id}", response_model=VisitOut)
def get_visit(visit_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_visit(conn, visit_id)
    if not row:
        raise HTTPException(404, "Visit not found")
    return row


@router.get("/patient/{patient_id}", response_model=list[VisitOut])
def by_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_visits_by_patient(conn, patient_id)


# ---- diagnoses ----
@router.post("/diagnoses", response_model=VisitDiagnosisOut, status_code=201)
def add_diag(p: VisitDiagnosisCreate, conn: Connection = Depends(get_db_connection)):
    did = q.add_diagnosis(conn, p.model_dump())
    return {**p.model_dump(), "diagnosis_id": did}


@router.get("/{visit_id}/diagnoses", response_model=list[VisitDiagnosisOut])
def list_diag(visit_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_diagnoses(conn, visit_id)


# ---- procedures ----
@router.post("/procedures", response_model=VisitProcedureOut, status_code=201)
def add_proc(p: VisitProcedureCreate, conn: Connection = Depends(get_db_connection)):
    pid = q.add_procedure(conn, p.model_dump())
    return {**p.model_dump(), "procedure_id": pid}


@router.get("/{visit_id}/procedures", response_model=list[VisitProcedureOut])
def list_proc(visit_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_procedures(conn, visit_id)


# ---- visit notes ----
@router.post("/notes", response_model=VisitNoteOut, status_code=201)
def add_note(p: VisitNoteCreate, conn: Connection = Depends(get_db_connection)):
    nid = q.add_visit_note(conn, p.model_dump())
    return q.get_visit_note(conn, nid)


@router.get("/{visit_id}/notes", response_model=list[VisitNoteOut])
def list_notes(visit_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_visit_notes(conn, visit_id)


# ---- allergies ----
@router.post("/allergies", response_model=AllergyOut, status_code=201)
def add_allergy(p: AllergyCreate, conn: Connection = Depends(get_db_connection)):
    aid = q.create_allergy(conn, p.model_dump())
    return {**p.model_dump(), "allergy_id": aid}


@router.get("/patient/{patient_id}/allergies", response_model=list[AllergyOut])
def patient_allergies(patient_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_allergies(conn, patient_id)


# ---- conditions ----
@router.post("/conditions", response_model=PatientConditionOut, status_code=201)
def add_condition(p: PatientConditionCreate,
                  conn: Connection = Depends(get_db_connection)):
    cid = q.create_condition(conn, p.model_dump())
    return {**p.model_dump(), "condition_id": cid}


@router.get("/patient/{patient_id}/conditions", response_model=list[PatientConditionOut])
def patient_conditions(patient_id: int, conn: Connection = Depends(get_db_connection)):
    return q.list_conditions(conn, patient_id)


# ---- prescriptions ----
@router.post("/prescriptions", response_model=PrescriptionOut, status_code=201)
def create_presc(p: PrescriptionCreate, conn: Connection = Depends(get_db_connection)):
    data = p.model_dump(exclude={"items"})
    pid = q.create_prescription(conn, data)
    for item in p.items:
        q.add_prescription_item(conn, {**item.model_dump(), "prescription_id": pid})
    return {
        "prescription_id": pid,
        **data,
        "items": q.list_prescription_items(conn, pid),
    }