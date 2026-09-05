"""
The `loan_applications` table: one loan request.

Also defines the two enums the tests import from this exact module:
`LoanType` and `ApplicationStatus`.
"""

import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class LoanType(str, enum.Enum):
    personal = "personal"
    home = "home"
    auto = "auto"


class ApplicationStatus(str, enum.Enum):
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    disbursed = "disbursed"


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False, index=True)

    # Indexed because the list screen filters and sorts by these.
    loan_type = Column(Enum(LoanType), nullable=False, index=True)
    amount_requested = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    purpose = Column(String(500), nullable=False)
    status = Column(
        Enum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.submitted,
        index=True,
    )

    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    # onupdate: the database refreshes this whenever the row changes.
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    applicant = relationship("Applicant", back_populates="applications")

    # cascade="all, delete-orphan": when an application is deleted, its
    # documents and history rows are deleted with it. This is done by
    # SQLAlchemy, not by the database, so it works even though SQLite's
    # foreign-key checking is off (TRAPS T-03, T-04). Test DB-04 relies on it.
    documents = relationship(
        "Document", back_populates="application", cascade="all, delete-orphan"
    )
    status_history = relationship(
        "StatusHistory",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="StatusHistory.changed_at",   # oldest first, as the spec says
    )
