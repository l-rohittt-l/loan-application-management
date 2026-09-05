"""
The logic behind loan applications: submit, view, list, change status.

`validate_status_transition(current, new)` is called by name in the trainer's
UNIT-05 and UNIT-06 tests. It must return True or False, never raise.
"""

from datetime import date, datetime, time
from time import perf_counter

import structlog
from sqlalchemy.orm import Session, joinedload, selectinload

from app.domain import rules
from app.models.applicant import Applicant
from app.models.application import ApplicationStatus, LoanApplication, LoanType
from app.models.status_history import StatusHistory
from app.models.user import User, UserRole
from app.schemas.application import CreateApplicationSchema
from app.services import activity_service
from app.services.errors import Forbidden, NotFound, RuleViolation
from app.utils.finance import format_rupees

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# The function the tests name
# ---------------------------------------------------------------------------

def validate_status_transition(current, new) -> bool:
    """True if an application may move from `current` to `new`. Accepts enums or strings."""
    return rules.is_valid_transition(current, new)


# ---------------------------------------------------------------------------
# Per-loan-type checks (D-02, D-03). The schema already checked the global
# bounds; these are the tighter rules from the manual.
# ---------------------------------------------------------------------------

def check_type_limits(loan_type, amount: float, tenure_months: int) -> None:
    """Raise RuleViolation with a plain-English message if a per-type limit is broken."""
    lo, hi = rules.tenure_range(loan_type)
    if not lo <= tenure_months <= hi:
        raise RuleViolation(
            f"A {rules._v(loan_type)} loan must run between {lo} and {hi} months"
        )
    cap = rules.amount_limit(loan_type)
    if amount > cap:
        raise RuleViolation(
            f"A {rules._v(loan_type)} loan cannot exceed {format_rupees(cap)}"
        )


# ---------------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------------

def create_application(
    db: Session,
    data: CreateApplicationSchema,
    *,
    user: User,
    meta: dict | None = None,
) -> LoanApplication:
    started = perf_counter()
    applicant = db.query(Applicant).filter(Applicant.id == data.applicant_id).first()
    if applicant is None:
        raise NotFound("Applicant not found")

    # An applicant may only apply on their own behalf.
    if user.role == UserRole.applicant and applicant.user_id != user.id:
        raise Forbidden("You can only submit applications for yourself")

    check_type_limits(data.loan_type, data.amount_requested, data.tenure_months)

    application = LoanApplication(**data.model_dump(), status=ApplicationStatus.submitted)
    db.add(application)
    db.flush()   # we need the id for the history row

    # The first history row: no old status, new status "submitted".
    db.add(StatusHistory(
        application_id=application.id,
        old_status=None,
        new_status=ApplicationStatus.submitted,
        changed_by=user.email,
        remarks="Application submitted",
    ))

    activity_service.record(
        db, action="application_submitted",
        actor_id=user.email, actor_role=user.role.value,
        entity_type="application", entity_id=application.id,
        details={"loan_type": data.loan_type.value, "amount": data.amount_requested,
                 "tenure_months": data.tenure_months},
        **(meta or {}),
    )
    db.commit()
    db.refresh(application)
    logger.info("application_created", operation="create_application",
                application_id=application.id, loan_type=data.loan_type.value,
                amount=data.amount_requested,
                duration_ms=int((perf_counter() - started) * 1000), status="success")
    return application


# ---------------------------------------------------------------------------
# View one
# ---------------------------------------------------------------------------

def get_application(db: Session, application_id: int, *, viewer: User) -> LoanApplication:
    """
    One query loads the application, its applicant, every history row and
    every document. Without the load options SQLAlchemy would run a separate
    query each time the router touched a relationship (the N+1 problem).
    """
    application = (
        db.query(LoanApplication)
        .options(
            joinedload(LoanApplication.applicant),
            selectinload(LoanApplication.status_history),
            selectinload(LoanApplication.documents),
        )
        .filter(LoanApplication.id == application_id)
        .first()
    )
    if application is None:
        raise NotFound(f"Application {application_id} not found")
    if viewer.role == UserRole.applicant and application.applicant.user_id != viewer.id:
        raise Forbidden("You can only view your own applications")
    return application


# ---------------------------------------------------------------------------
# List with filters
# ---------------------------------------------------------------------------

def list_applications(
    db: Session,
    *,
    viewer: User,
    status: str | None = None,
    loan_type: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[LoanApplication], int]:
    """
    A page of applications plus the total count. Filters combine with AND.
    Newest first. Applicants see only their own. The applicant is joined in
    the same query so the list screen can show a name without extra queries.
    """
    query = db.query(LoanApplication).options(joinedload(LoanApplication.applicant))

    if viewer.role == UserRole.applicant:
        query = query.join(Applicant).filter(Applicant.user_id == viewer.id)

    if status:
        query = query.filter(LoanApplication.status == ApplicationStatus(status))
    if loan_type:
        query = query.filter(LoanApplication.loan_type == LoanType(loan_type))
    if from_date:
        query = query.filter(LoanApplication.submitted_at >= datetime.combine(from_date, time.min))
    if to_date:
        query = query.filter(LoanApplication.submitted_at <= datetime.combine(to_date, time.max))

    total = query.count()
    items = (
        query.order_by(LoanApplication.submitted_at.desc(), LoanApplication.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


# ---------------------------------------------------------------------------
# Change status
# ---------------------------------------------------------------------------

def update_status(
    db: Session,
    application_id: int,
    new_status: ApplicationStatus,
    remarks: str | None,
    *,
    user: User,
    meta: dict | None = None,
) -> LoanApplication:
    started = perf_counter()
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if application is None:
        raise NotFound(f"Application {application_id} not found")

    old_status = application.status
    if not validate_status_transition(old_status, new_status):
        raise RuleViolation(
            f"Invalid status transition from {old_status.value} to {new_status.value}"
        )
    if rules.requires_manager(old_status, new_status) and user.role != UserRole.branch_manager:
        raise Forbidden("Only a branch manager can disburse a loan")

    application.status = new_status
    db.add(StatusHistory(
        application_id=application.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=user.email,
        remarks=remarks,
    ))
    activity_service.record(
        db, action="status_changed",
        actor_id=user.email, actor_role=user.role.value,
        entity_type="application", entity_id=application.id,
        details={"from": old_status.value, "to": new_status.value, "remarks": remarks},
        **(meta or {}),
    )
    db.commit()
    db.refresh(application)
    logger.info("status_updated", operation="update_status", application_id=application.id,
                old_status=old_status.value, new_status=new_status.value, changed_by=user.email,
                duration_ms=int((perf_counter() - started) * 1000), status="success")
    return application
