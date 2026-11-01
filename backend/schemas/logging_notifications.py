from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    appointment_id: Optional[int] = None
    title: str
    message: Optional[str] = None
    type: Literal["Appointment", "Consent", "System", "Other"] = "System"
    is_read: bool = False


class NotificationOut(NotificationCreate):
    notification_id: int
    created_at: Optional[datetime] = None


class AccessLogCreate(BaseModel):
    user_id: int
    patient_id: int
    document_id: Optional[int] = None
    action_type: Literal["VIEW", "LOGIN", "UPLOAD", "CONSENT", "OTHER"]
    ip_address: Optional[str] = None
    remarks: Optional[str] = None


class AccessLogOut(AccessLogCreate):
    log_id: int
    action_time: Optional[datetime] = None


class AuditTrailCreate(BaseModel):
    user_id: Optional[int] = None
    table_name: str
    record_id: str
    action_type: Literal["INSERT", "UPDATE", "DELETE"]
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    remarks: Optional[str] = None


class AuditTrailOut(AuditTrailCreate):
    audit_id: int
    action_time: Optional[datetime] = None