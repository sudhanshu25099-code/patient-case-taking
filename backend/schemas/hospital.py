from datetime import date
from typing import Optional
from pydantic import BaseModel


class HospitalCreate(BaseModel):
    name: str
    registration_no: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    contact_no: Optional[str] = None
    email: Optional[str] = None


class HospitalOut(HospitalCreate):
    hospital_id: int


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentOut(DepartmentCreate):
    department_id: int
    hospital_id: int


class DoctorHospitalCreate(BaseModel):
    department_id: Optional[int] = None
    joined_date: Optional[date] = None
    is_active: bool = True


class DoctorHospitalOut(DoctorHospitalCreate):
    doctor_id: int
    hospital_id: int


class DoctorAtHospital(BaseModel):
    doctor_id: int
    full_name: str
    specialization: Optional[str] = None
    department_id: Optional[int] = None
    is_active: bool