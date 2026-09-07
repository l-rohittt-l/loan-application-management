"""
The shared state every agent in the pipeline reads from and writes to.

A `TypedDict` rather than a class with methods: LangGraph passes this dict
from node to node, and each node hands back a dict to merge into it. There
is no behaviour here on purpose — the four agent files hold all of it.

Every field has a sensible empty default (`{}`, `[]`, `""`) so that reading a
field an earlier agent has not run yet never raises `KeyError` — the trainer's
own US-01-P5-01 asks for exactly this.
"""

from typing import List, TypedDict


class RiskAssessment(TypedDict):
    debt_to_income_ratio: float
    emi_amount: float
    emi_affordability: str      # "yes" or "no"
    credit_risk_level: str      # "low", "medium", "high"
    employment_risk: str        # "low", "medium", "high"
    overall_risk_score: float   # 0-100 (higher = better candidate)
    risk_summary: str


class ComplianceCheck(TypedDict):
    documents_complete: bool
    missing_documents: List[str]
    kyc_verified: bool
    amount_within_limit: bool
    age_eligible: bool
    compliance_passed: bool
    compliance_notes: str


class LoanProcessingState(TypedDict):
    application_id: str
    applicant_data: dict           # From API: applicant profile
    application_data: dict         # From API: loan application details
    documents: List[dict]          # From API: uploaded documents
    risk_assessment: RiskAssessment
    compliance_check: ComplianceCheck
    final_decision: str            # "APPROVE", "REJECT", "REQUEST_MORE_INFO"
    reasoning: str                 # Full decision reasoning
    messages: List[dict]           # Agent messages for tracing
    current_agent: str             # Which agent is currently active
    errors: List[str]              # Any errors encountered


def initial_state(application_id: str) -> LoanProcessingState:
    """Every field defaulted, so no agent ever meets a missing key (US-01-P5-01)."""
    return {
        "application_id": application_id,
        "applicant_data": {},
        "application_data": {},
        "documents": [],
        "risk_assessment": {},
        "compliance_check": {},
        "final_decision": "",
        "reasoning": "",
        "messages": [],
        "current_agent": "",
        "errors": [],
    }
