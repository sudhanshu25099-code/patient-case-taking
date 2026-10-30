import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.engine import Connection
from sqlalchemy import text

from dependencies import get_db_connection
from queries import document_queries as q
from schemas.documents import (
    DocumentTypeCreate, DocumentTypeOut, DocumentTagCreate, DocumentTagOut,
    MedicalDocumentCreate, MedicalDocumentOut,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/types", response_model=DocumentTypeOut, status_code=201)
def create_type(p: DocumentTypeCreate, conn: Connection = Depends(get_db_connection)):
    tid = q.create_doc_type(conn, p.model_dump())
    return {**p.model_dump(), "document_type_id": tid}


@router.get("/types", response_model=list[DocumentTypeOut])
def list_types(conn: Connection = Depends(get_db_connection)):
    return q.list_doc_types(conn)


@router.post("/tags", response_model=DocumentTagOut, status_code=201)
def create_tag(p: DocumentTagCreate, conn: Connection = Depends(get_db_connection)):
    tid = q.create_tag(conn, p.model_dump())
    return {**p.model_dump(), "tag_id": tid}


@router.get("/tags", response_model=list[DocumentTagOut])
def list_tags(conn: Connection = Depends(get_db_connection)):
    return q.list_tags(conn)


@router.post("", response_model=MedicalDocumentOut, status_code=201)
def create_doc(p: MedicalDocumentCreate, conn: Connection = Depends(get_db_connection)):
    did = q.create_document(conn, p.model_dump())
    return {**q.get_document(conn, did), "tag_ids": []}


@router.post("/{document_id}/tags/{tag_id}", status_code=201)
def tag_doc(document_id: int, tag_id: int,
            conn: Connection = Depends(get_db_connection)):
    q.link_tag(conn, document_id, tag_id)
    return {"ok": True}


@router.get("/{document_id}", response_model=MedicalDocumentOut)
def get_doc(document_id: int, conn: Connection = Depends(get_db_connection)):
    row = q.get_document(conn, document_id)
    if not row:
        raise HTTPException(404, "Document not found")
    return {**row, "tag_ids": q.doc_tags(conn, document_id)}


@router.get("/patient/{patient_id}", response_model=list[MedicalDocumentOut])
def by_patient(patient_id: int, conn: Connection = Depends(get_db_connection)):
    rows = q.list_documents_by_patient(conn, patient_id)
    return [{**r, "tag_ids": q.doc_tags(conn, r["document_id"])} for r in rows]


@router.post("/upload", status_code=201)
def upload_file(
    patient_id: int = Form(...), document_type_id: int = Form(...),
    title: str = Form(...), uploaded_by: int = Form(...),
    file: UploadFile = File(...), conn: Connection = Depends(get_db_connection)
):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    data = {
        "patient_id": patient_id, "document_type_id": document_type_id,
        "title": title, "file_path": file_path, "uploaded_by": uploaded_by,
        "visit_id": None, "test_result_id": None, "description": None,
        "file_size": os.path.getsize(file_path), "mime_type": file.content_type,
        "document_date": None, "ocr_text": None, "ocr_status": "Pending", 
        "verification_status": "Pending"
    }
    did = q.create_document(conn, data)
    return q.get_document(conn, did)

@router.patch("/{document_id}/verify")
def verify_doc(document_id: int, conn: Connection = Depends(get_db_connection)):
    conn.execute(text("""
    UPDATE medical_document SET verification_status = 'Verified' 
    WHERE document_id = :id
    """), {"id": document_id})
    return {"ok": True}

@router.delete("/{document_id}", status_code=204)
def delete_doc(document_id: int, conn: Connection = Depends(get_db_connection)):
    conn.execute(text("DELETE FROM medical_document WHERE document_id = :id"), {"id": document_id})
