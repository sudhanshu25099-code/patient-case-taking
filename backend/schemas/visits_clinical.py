from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


# --- visit ---
class VisitCreate(BaseModel):
    appointment_id: Optional[int] = None
    patient_id: int
    hospital_id: int
    department_id: Optional[int] = None
    doctor_id: Optional[int] = None
    visit_date: datetime
    visit_type: Literal["OPD", "IPD", "ER", "Other"] = "OPD"
    chief_complaint: Optional[str] = None
    symptoms: Optional[str] = None
    vitals_summary: Optional[str] = None
    notes: Optional[str] = None


class VisitOut(VisitCreate):
    visit_id: int


# --- diagnosis ---
class VisitDiagnosisCreate(BaseModel):
    visit_id: int
    diagnosis_code: Optional[str] = None
    diagnosis_name: str
    diagnosis_type: Literal["Primary", "Secondary", "Provisional"] = "Primary"
    notes: Optional[str] = None


class VisitDiagnosisOut(VisitDiagnosisCreate):
    diagnosis_id: int


# --- procedure ---
class VisitProcedureCreate(BaseModel):
    visit_id: int
    procedure_name: str
    procedure_type: Optional[str] = None
    notes: Optional[str] = None


class VisitProcedureOut(VisitProcedureCreate):
    procedure_id: int


# --- note ---
class VisitNoteCreate(BaseModel):
    visit_id: int
    note_type: Literal["Consultation", "Follow-up", "Other"] = "Consultation"
    title: Optional[str] = None
    content: str
    added_by: int


class VisitNoteOut(BaseModel):
    note_id: int
    visit_id: int
    note_type: Literal["Consultation", "Follow-up", "Other"]
    title: Optional[str] = None
    content: str
    added_by: int
    added_at: Optional[datetime] = None


# --- allergy ---
class AllergyCreate(BaseModel):
    patient_id: int
    allergen: str
    allergy_type: Literal["Drug", "Food", "Environmental", "Other"]
    reaction: Optional[str] = None
    severity: Optional[Literal["Mild", "Moderate", "Severe"]] = None
    status: Literal["Active", "Resolved"] = "Active"
    noted_date: Optional[date] = None
    recorded_by: Optional[int] = None
    notes: Optional[str] = None


class AllergyOut(AllergyCreate):
    allergy_id: int


# --- patient_condition ---
class PatientConditionCreate(BaseModel):
    patient_id: int
    source_visit_id: Optional[int] = None
    condition_name: str
    icd_code: Optional[str] = None
    condition_type: Literal["Chronic", "Past illness", "Surgery", "Family history"]
    onset_date: Optional[date] = None
    status: Literal["Active", "Controlled", "Resolved"] = "Active"
    notes: Optional[str] = None


class PatientConditionOut(PatientConditionCreate):
    condition_id: int


# --- prescription ---
class PrescriptionItemCreate(BaseModel):
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    duration_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_ongoing: bool = False
    instructions: Optional[str] = None


class PrescriptionItemOut(PrescriptionItemCreate):
    item_id: int
    prescription_id: int


class PrescriptionCreate(BaseModel):
    visit_id: int
    patient_id: int
    doctor_id: int
    prescribed_date: date
    notes: Optional[str] = None
    items: List[PrescriptionItemCreate] = []


class PrescriptionOut(BaseModel):
    prescription_id: int
    visit_id: int
    patient_id: int
    doctor_id: int
    prescribed_date: date
    notes: Optional[str] = None
    items: List[PrescriptionItemOut] = []