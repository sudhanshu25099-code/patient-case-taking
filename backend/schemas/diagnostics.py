from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel


class DiagnosticTestCreate(BaseModel):
    test_name: str
    category: Literal["Blood", "Urine", "Imaging", "Other"]
    description: Optional[str] = None


class DiagnosticTestOut(DiagnosticTestCreate):
    test_id: int


class TestParameterCreate(BaseModel):
    test_id: int
    parameter_name: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None


class TestParameterOut(TestParameterCreate):
    parameter_id: int


class TestOrderCreate(BaseModel):
    visit_id: int
    ordered_by: int
    status: Literal["Ordered", "Completed", "Cancelled"] = "Ordered"
    clinical_note: Optional[str] = None
    test_ids: List[int]


class TestOrderOut(BaseModel):
    order_id: int
    visit_id: int
    ordered_by: int
    order_date: Optional[datetime] = None
    status: Literal["Ordered", "Completed", "Cancelled"]
    clinical_note: Optional[str] = None
    test_ids: List[int] = []


class TestOrderItemOut(BaseModel):
    order_item_id: int
    order_id: int
    test_id: int
    status: Literal["Pending", "Completed"]


class TestResultItemCreate(BaseModel):
    parameter_id: int
    result_value: str
    flag: Optional[Literal["Normal", "High", "Low"]] = None
    notes: Optional[str] = None


class TestResultItemOut(TestResultItemCreate):
    result_item_id: int
    result_id: int


class TestResultCreate(BaseModel):
    order_item_id: int
    report_date: datetime
    overall_finding: Optional[str] = None
    verified_by: Optional[int] = None
    verification_status: Literal["Pending", "Verified", "Rejected"] = "Pending"
    items: List[TestResultItemCreate] = []


class TestResultOut(BaseModel):
    result_id: int
    order_item_id: int
    report_date: datetime
    overall_finding: Optional[str] = None
    verified_by: Optional[int] = None
    verification_status: Literal["Pending", "Verified", "Rejected"]
    items: List[TestResultItemOut] = []