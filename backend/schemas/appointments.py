from datetime import date, datetime, time, timedelta
from typing import List, Literal, Optional, Any
from pydantic import BaseModel, field_validator


class AppointmentCreate(BaseModel):
    patient_id: int
    hospital_id: int
    doctor_id: int
    appointment_date: date
    time_slot: Any
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
    time_slot: Any
    reason: Optional[str] = None
    pre_visit_notes: Optional[str] = None
    is_follow_up: bool
    status: Literal["Scheduled", "Completed", "Cancelled", "No Show"]
    notes: Optional[str] = None
    booked_by: Optional[int] = None
    created_at: Optional[datetime] = None

    @field_validator("time_slot", mode="before")
    @classmethod
    def parse_time_slot(cls, v):
        if isinstance(v, timedelta):
            total_seconds = int(v.total_seconds())
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return str(v)


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
    added_by: Optional[int] = None


class AppointmentNoteOut(AppointmentNoteCreate):
    note_id: int
    created_at: Optional[datetime] = None


class AppointmentStatusUpdate(BaseModel):
    status: Literal["Scheduled", "Completed", "Cancelled", "No Show"]


class AppointmentDetail(AppointmentOut):
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    symptoms: List[AppointmentSymptomOut] = []
    notes_list: List[AppointmentNoteOut] = []
