from datetime import date, time
from typing import Optional
from pydantic import BaseModel


class PreVisitSnapshot(BaseModel):
    appointment_id: int
    appointment_date: date
    time_slot: time
    doctor_id: int
    patient_id: int
    patient_name: str
    reason: Optional[str] = None
    pre_visit_notes: Optional[str] = None
    todays_symptoms: Optional[str] = None
    active_allergies: Optional[str] = None
    active_conditions: Optional[str] = None
    ongoing_medicines: Optional[str] = None
    latest_summary: Optional[str] = None