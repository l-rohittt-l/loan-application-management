"""
The logic behind borrower profiles.

`create_applicant(db, data)` is called by name in the trainer's UNIT-01 test,
so its first two arguments stay exactly as they are.
"""

import structlog
from sqlalchemy.orm import Session

from app.models.applicant import Applicant
from app.models.user import User, UserRole
from app.schemas.applicant import CreateApplicantSchema
from app.services import activity_service
from app.services.errors import EmailAlreadyRegistered, Forbidden, NotFound

logger = structlog.get_logger()


def create_applicant(
    db: Session,
    data: CreateApplicantSchema,
    *,
    created_by: str | None = None,
    created_by_role: str | None = None,
    meta: dict | None = None,
) -> Applicant:
    """Create a borrower profile. Used by staff on a customer's behalf."""
    email = data.email.lower()
    if db.query(Applicant).filter(Applicant.email == email).first() is not None:
        raise EmailAlreadyRegistered("An applicant with this email already exists")

    applicant = Applicant(**{**data.model_dump(), "email": email})
    db.add(applicant)
    db.flush()

    activity_service.record(
        db, action="applicant_created",
        actor_id=created_by or "system", actor_role=created_by_role,
        entity_type="applicant", entity_id=applicant.id,
        details={"email": email},
        **(meta or {}),
    )
    db.commit()
    db.refresh(applicant)   # pulls back the database-generated id and created_at
    logger.info("applicant_created", applicant_id=applicant.id, created_by=created_by)
    return applicant


def get_applicant(db: Session, applicant_id: int) -> Applicant:
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if applicant is None:
        raise NotFound(f"Applicant {applicant_id} not found")
    return applicant


def get_applicant_for_viewer(db: Session, applicant_id: int, viewer: User) -> Applicant:
    """
    Fetch a profile, enforcing who may see it. Staff see anyone. An applicant
    sees only their own profile. This is the rule a teammate's app was missing
    in the 4 August review (Change 10, item 1).
    """
    applicant = get_applicant(db, applicant_id)
    if viewer.role == UserRole.applicant and applicant.user_id != viewer.id:
        raise Forbidden("You can only view your own profile")
    return applicant


def get_own_profile(db: Session, user: User) -> Applicant | None:
    """The borrower profile linked to a logged-in applicant, if any."""
    return db.query(Applicant).filter(Applicant.user_id == user.id).first()


def list_applicants(db: Session, *, page: int, limit: int) -> tuple[list[Applicant], int]:
    """A page of profiles plus the total count, newest first."""
    query = db.query(Applicant).order_by(Applicant.created_at.desc(), Applicant.id.desc())
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total
