"""
The `documents` table: a piece of paperwork attached to an application.

Phase 1 stores only the file name, not the file itself. Real upload comes
later (FUTURE-UPGRADES).
"""

import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class DocumentType(str, enum.Enum):
    id_proof = "id_proof"
    income_proof = "income_proof"
    bank_statement = "bank_statement"
    property_docs = "property_docs"
    employment_letter = "employment_letter"
    # Added: the manual requires it for auto loans (D-04).
    vehicle_quotation = "vehicle_quotation"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer, ForeignKey("loan_applications.id"), nullable=False, index=True
    )
    doc_type = Column(Enum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    # False until a loan officer checks it.
    verified = Column(Boolean, nullable=False, default=False)

    application = relationship("LoanApplication", back_populates="documents")
