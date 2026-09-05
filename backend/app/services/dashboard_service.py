"""
The numbers behind the dashboard.

Three small grouped queries. The database does the counting and hands back
totals, so this stays fast however many applications exist. Never loads the
applications themselves.
"""

import structlog
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain import rules
from app.models.application import ApplicationStatus, LoanApplication
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services import activity_service

logger = structlog.get_logger()


def summary(db: Session, *, user: User, meta: dict | None = None) -> DashboardSummary:
    # Count and total amount by status, in one query.
    by_status_rows = (
        db.query(
            LoanApplication.status,
            func.count(LoanApplication.id),
            func.coalesce(func.sum(LoanApplication.amount_requested), 0.0),
        )
        .group_by(LoanApplication.status)
        .all()
    )
    # Count by loan type, in one query.
    by_type_rows = (
        db.query(LoanApplication.loan_type, func.count(LoanApplication.id))
        .group_by(LoanApplication.loan_type)
        .all()
    )

    # Start every key at zero, then fill in what the database returned.
    by_status = {s: 0 for s in rules.STATUSES}
    amount_by_status = {s: 0.0 for s in rules.STATUSES}
    for status_, count, amount in by_status_rows:
        by_status[status_.value] = count
        amount_by_status[status_.value] = float(amount)

    by_loan_type = {t: 0 for t in rules.LOAN_TYPES}
    for loan_type, count in by_type_rows:
        by_loan_type[loan_type.value] = count

    result = DashboardSummary(
        total_applications=sum(by_status.values()),
        by_status=by_status,
        by_loan_type=by_loan_type,
        total_amount_requested=sum(amount_by_status.values()),
        pending_review=by_status[ApplicationStatus.submitted.value]
        + by_status[ApplicationStatus.under_review.value],
        approved_amount=amount_by_status[ApplicationStatus.approved.value],
    )

    activity_service.record(
        db, action="dashboard_viewed", actor_id=user.email, actor_role=user.role.value,
        **(meta or {}),
    )
    db.commit()
    logger.info("dashboard_viewed", user_email=user.email, total=result.total_applications)
    return result
