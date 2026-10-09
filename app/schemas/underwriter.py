from pydantic import BaseModel, Field
from typing import Optional, List


class WorklistItem(BaseModel):
    case_id: str
    application_id: str
    applicant_name: str
    loan_amount: float
    credit_score: int
    dti_ratio: float
    risk_grade: str
    trigger_reason: str
    status: str
    submitted_at: str


class WorklistResponse(BaseModel):
    total_cases: int
    pending_review: int
    cases: List[WorklistItem]


class CaseAdjudicationRequest(BaseModel):
    action: str = Field(..., description="APPROVE, REJECT, or REQUEST_INFO")
    notes: Optional[str] = ""
    approved_amount: Optional[float] = None
    approved_rate: Optional[float] = None
    reason_codes: Optional[List[str]] = []


class CaseAdjudicationResponse(BaseModel):
    case_id: str
    action: str
    status: str
    adjudicated_by: str
    adjudicated_at: str
    notice_generated: bool
