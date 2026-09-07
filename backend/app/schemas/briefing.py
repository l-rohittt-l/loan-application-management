"""
Schemas for the Manager's Morning Briefing (D-13).

`written_by_ai` is deliberately part of the response rather than hidden: if
the LLM was unavailable and the manager is reading the plain fallback, the
screen says so. A briefing that quietly degrades without telling anyone is
worse than one that admits it.
"""

from pydantic import BaseModel

from app.schemas.common import UtcDateTime


class BriefingNumbers(BaseModel):
    open_applications: int
    awaiting_decision: int
    value_awaiting_decision: float
    approved_not_disbursed: int
    value_approved_not_disbursed: float
    waiting_too_long: int
    missing_documents: int
    failed_eligibility: int


class StuckApplication(BaseModel):
    id: int
    applicant_name: str
    status: str
    days_waiting: float
    amount: float
    loan_type: str


class MissingDocumentsRow(BaseModel):
    id: int
    applicant_name: str
    missing: list[str]


class FailedEligibilityRow(BaseModel):
    id: int
    applicant_name: str
    status: str
    amount: float
    loan_type: str


class BriefingResponse(BaseModel):
    # T-39: any response field holding a time uses UtcDateTime, never a bare datetime.
    generated_at: UtcDateTime
    written_by_ai: bool
    narrative: str
    headline_numbers: BriefingNumbers
    needs_attention: list[StuckApplication] = []
    missing_documents: list[MissingDocumentsRow] = []
    failed_eligibility: list[FailedEligibilityRow] = []
