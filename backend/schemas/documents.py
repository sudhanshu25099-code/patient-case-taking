from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


class DocumentTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DocumentTypeOut(DocumentTypeCreate):
    document_type_id: int


class DocumentTagCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DocumentTagOut(DocumentTagCreate):
    tag_id: int


class MedicalDocumentCreate(BaseModel):
    patient_id: int
    visit_id: Optional[int] = None
    document_type_id: int
    test_result_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    document_date: Optional[date] = None
    ocr_text: Optional[str] = None
    ocr_status: Literal["Pending", "Done", "Failed", "Not Needed"] = "Pending"
    verification_status: Literal["Pending", "Verified", "Rejected"] = "Pending"
    uploaded_by: int


class MedicalDocumentOut(BaseModel):
    document_id: int
    patient_id: int
    visit_id: Optional[int] = None
    document_type_id: int
    test_result_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    document_date: Optional[date] = None
    ocr_status: Literal["Pending", "Done", "Failed", "Not Needed"]
    verification_status: Literal["Pending", "Verified", "Rejected"]
    uploaded_by: int
    uploaded_at: Optional[datetime] = None
    tag_ids: List[int] = []