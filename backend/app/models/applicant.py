"""
The `applicants` table: the person borrowing money.

The trainer's version has name, email, phone, credit score, income and
employment status. We add three optional columns so later phases can check
age, job length and existing loan payments (decisions D-05 and D-16).
"""

import enum

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EmploymentStatus(str, enum.Enum):
    salaried = "salaried"
    self_employed = "self_employed"
    unemployed = "unemployed"


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)

    # Link to the login account, if the applicant signed up themselves.
    # Empty when a loan officer created the record on the customer's behalf.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(15), nullable=False)

    # CIBIL score, 300 to 900. Optional: first-time borrowers may not have one.
    credit_score = Column(Integer, nullable=True)
    annual_income = Column(Float, nullable=False)
    employment_status = Column(Enum(EmploymentStatus), nullable=False)

    # ---- Our additions, all optional ----
    # Needed for the age rules in manual Section 5 (D-05).
    date_of_birth = Column(Date, nullable=True)
    # Years in the current job or business. 0.5 means six months (D-16).
    years_with_employer = Column(Float, nullable=True)
    # Rupees per month already going to other loans (D-16).
    existing_monthly_emi = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship("LoanApplication", back_populates="applicant")
