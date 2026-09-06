"""
Schemas for the borrower profile.

`CreateApplicantSchema` is a name the trainer's tests import (T-06).
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.applicant import EmploymentStatus
from app.schemas.common import UtcDateTime, check_date_of_birth, check_name, check_phone


class CreateApplicantSchema(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str
    # Optional: first-time borrowers may have no score. If given, 300 to 900.
    # Test UNIT-08 sends 1200, 100, -1 and 0 and expects all four rejected.
    credit_score: int | None = Field(default=None, ge=300, le=900)
    annual_income: float = Field(..., gt=0, le=1_000_000_000)
    employment_status: EmploymentStatus

    # Our additions (D-05, D-16). All optional.
    date_of_birth: date | None = None
    years_with_employer: float | None = Field(default=None, ge=0, le=60)
    existing_monthly_emi: float = Field(default=0, ge=0)

    _check_name = field_validator("name")(check_name)
    _check_phone = field_validator("phone")(check_phone)
    _check_dob = field_validator("date_of_birth")(check_date_of_birth)


class ApplicantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str
    credit_score: int | None
    annual_income: float
    employment_status: EmploymentStatus
    date_of_birth: date | None
    years_with_employer: float | None
    existing_monthly_emi: float
    created_at: UtcDateTime | None = None
