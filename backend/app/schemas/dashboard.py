"""
Schema for the dashboard summary.
"""

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_applications: int
    # Every status and loan type is present, even with a count of zero,
    # so the front-end never has to guess which keys exist.
    by_status: dict[str, int]
    by_loan_type: dict[str, int]
    total_amount_requested: float
    # Extras beyond the spec (cautious upgrade):
    pending_review: int        # submitted + under_review, the officer's to-do pile
    approved_amount: float     # rupees approved and waiting to be paid out
