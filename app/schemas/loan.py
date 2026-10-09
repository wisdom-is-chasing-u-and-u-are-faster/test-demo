from pydantic import BaseModel, Field
from typing import List


class AddressSchema(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str


class ApplicantSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    ssn: str = Field(..., description="Full 9-digit SSN or formatted SSN")
    date_of_birth: str
    address: AddressSchema


class EmploymentSchema(BaseModel):
    employer_name: str
    job_title: str
    annual_income: float = Field(..., gt=0)
    employment_status: str
    years_employed: int = Field(default=0, ge=0)


class LoanDetailsSchema(BaseModel):
    amount: float = Field(..., gt=0, le=1000000)
    term_months: int = Field(..., gt=0, le=360)
    purpose: str


class LoanApplicationRequest(BaseModel):
    applicant: ApplicantSchema
    employment: EmploymentSchema
    loan: LoanDetailsSchema


class DecisionSummary(BaseModel):
    decision: str  # APPROVED, REJECTED, MANUAL_REVIEW
    credit_score: int
    interest_rate: float
    max_approved_amount: float
    reason_codes: List[str] = []


class LoanApplicationResponse(BaseModel):
    application_id: str
    status: str
    decision: DecisionSummary
    created_at: str


class StageTimelineItem(BaseModel):
    stage: str
    status: str
    timestamp: str


class ApplicationStatusResponse(BaseModel):
    application_id: str
    applicant_name: str
    masked_ssn: str
    amount: float
    status: str
    decision: str
    timeline: List[StageTimelineItem]
