"""
The `status_history` table: the audit trail.

One row every time an application's status changes: what it was, what it
became, who did it, when, and why.
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.application import ApplicationStatus


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer, ForeignKey("loan_applications.id"), nullable=False, index=True
    )
    # Empty for the very first row, when the application is created.
    old_status = Column(Enum(ApplicationStatus), nullable=True)
    new_status = Column(Enum(ApplicationStatus), nullable=False)
    # The email of the user who made the change, taken from their token.
    changed_by = Column(String(150), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    remarks = Column(String(1000), nullable=True)

    application = relationship("LoanApplication", back_populates="status_history")
