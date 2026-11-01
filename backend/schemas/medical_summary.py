from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class MedicalSummaryCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    summary_type: str = "Pre-visit"
    summary_text: str
    generated_by: str = "System"
    version_no: int = 1
    is_current: bool = True
    document_ids: List[int] = []
    document_notes: Optional[List[Optional[str]]] = None


class MedicalSummaryOut(BaseModel):
    summary_id: int
    patient_id: int
    appointment_id: Optional[int] = None
    summary_type: str
    summary_text: str
    generated_by: str
    generated_at: Optional[datetime] = None
    version_no: int
    is_current: bool
    document_ids: List[int] = []