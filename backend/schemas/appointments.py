from datetime import date, datetime, time
from typing import List, Literal, Optional
from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    patient_id: int
    hospital_id: int
    doctor_id: int
    appointment_date: date
    time_slot: time
    reason: Optional[str] = None
    pre_visit_notes: Optional[str] = None
    is_follow_up: bool = False
    status: Literal["Scheduled", "Completed", "Cancelled", "No Show"] = "Scheduled"
    notes: Optional[str] = None
    booked_by: Optional[int] = None


class AppointmentOut(BaseModel):
    appointment_id: int
    patient_id: int
    hospital_id: int
    doctor_id: int
    appointment_date: date
    time_slot: time
    reason: Optional[str] = None
    pre_visit_notes: Optional[str] = None
    is_follow_up: bool
    status: Literal["Scheduled", "Completed", "Cancelled", "No Show"]
    notes: Optional[str] = None
    booked_by: Optional[int] = None
    created_at: Optional[datetime] = None


class AppointmentSymptomCreate(BaseModel):
    appointment_id: int
    symptom_name: str
    severity: Optional[Literal["Mild", "Moderate", "Severe"]] = None
    since_date: Optional[date] = None
    notes: Optional[str] = None


class AppointmentSymptomOut(AppointmentSymptomCreate):
    symptom_id: int


class AppointmentNoteCreate(BaseModel):
    appointment_id: int
    note_text: str
    added_by: int


class AppointmentNoteOut(BaseModel):
    appt_note_id: int
    appointment_id: int
    note_text: str
    added_by: int
    added_at: Optional[datetime] = None


class AppointmentDetail(AppointmentOut):
    symptoms: List[AppointmentSymptomOut] = []
    notes: List[AppointmentNoteOut] = []


class AppointmentStatusUpdate(BaseModel):
    status: Literal["Scheduled", "Completed", "Cancelled", "No Show"]