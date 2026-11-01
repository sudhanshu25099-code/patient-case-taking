from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, model_validator


class ConsentCreate(BaseModel):
    patient_id: int
    hospital_id: Optional[int] = None
    consent_type: Literal["View Only"] = "View Only"
    valid_from: datetime
    valid_to: Optional[datetime] = None
    status: Literal["Active", "Revoked", "Expired"] = "Active"
    purpose: Optional[str] = None
    remarks: Optional[str] = None


class ConsentOut(ConsentCreate):
    consent_id: int


class ConsentAccessCreate(BaseModel):
    consent_id: int
    doctor_id: Optional[int] = None
    department_id: Optional[int] = None
    access_from: datetime
    access_to: Optional[datetime] = None
    status: Literal["Active", "Revoked", "Expired"] = "Active"

    @model_validator(mode="after")
    def _at_least_one_target(self):
        if self.doctor_id is None and self.department_id is None:
            raise ValueError("At least one of doctor_id or department_id must be set")
        return self


class ConsentAccessOut(ConsentAccessCreate):
    access_id: int