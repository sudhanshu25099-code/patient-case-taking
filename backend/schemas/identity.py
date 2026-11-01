from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr


# --- person ---
class PersonBase(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonOut(PersonBase):
    person_id: int
    created_at: Optional[datetime] = None


# --- user_account ---
class UserAccountCreate(BaseModel):
    person_id: int
    username: str
    email: EmailStr
    password: str
    is_active: bool = True


class UserAccountOut(BaseModel):
    user_id: int
    person_id: int
    username: str
    email: EmailStr
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None


# --- role ---
class RoleCreate(BaseModel):
    role_name: str


class RoleOut(BaseModel):
    role_id: int
    role_name: str


class UserRoleOut(BaseModel):
    user_id: int
    role_id: int
    assigned_at: Optional[datetime] = None


# --- patient_profile ---
class PatientProfileCreate(BaseModel):
    person_id: int
    blood_group: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    abha_linked: bool = False


class PatientProfileOut(PatientProfileCreate):
    patient_id: int
    created_at: Optional[datetime] = None


# --- doctor_profile ---
class DoctorProfileCreate(BaseModel):
    person_id: int
    license_no: str
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[Decimal] = None


class DoctorProfileOut(DoctorProfileCreate):
    doctor_id: int


# --- nurse_profile ---
class NurseProfileCreate(BaseModel):
    person_id: int
    department_id: Optional[int] = None
    employee_no: str
    shift: Optional[Literal["Morning", "Evening", "Night"]] = None

class NurseProfileOut(NurseProfileCreate):
    nurse_id: int


class PasswordUpdate(BaseModel):
    new_password: str

class RoleAssignment(BaseModel):
    role_id: int