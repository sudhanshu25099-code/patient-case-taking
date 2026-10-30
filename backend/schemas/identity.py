from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class PersonCreate(BaseModel):
    full_name: str
    date_of_birth: date
    gender: str
    phone: str
    email:EmailStr
    address: Optional[str] = None

class PersonResponse(PersonCreate):
    person_id: int

class PatientProfileCreate(BaseModel):
    person_id: int
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[str] = None

class DoctorProfileCreate(BaseModel):
    person_id: int
    specialization: str
    qualification: str
    consultation_fee: float