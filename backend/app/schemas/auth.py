"""
Schemas for registering, signing up, and logging in.

Two ways in (decision D-07):
  - RegisterRequest: bank staff. The trainer's test uses this address.
  - ApplicantSignupRequest: customers. Creates a login AND a borrower profile.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.applicant import EmploymentStatus
from app.models.user import UserRole
from app.schemas.common import (
    UtcDateTime, check_date_of_birth, check_name, check_password, check_phone,
)


class RegisterRequest(BaseModel):
    """Staff registration. Matches the trainer's test payload: name, email, password."""
    name: str = Field(..., max_length=100)
    email: EmailStr
    password: str
    # Optional so the trainer's fixture (which sends no role) still works.
    # The service defaults it to loan_officer.
    role: UserRole | None = None

    _check_name = field_validator("name")(check_name)
    _check_password = field_validator("password")(check_password)


class ApplicantSignupRequest(BaseModel):
    """Customer signup. Everything needed for both the login and the borrower profile."""
    name: str = Field(..., max_length=100)
    email: EmailStr
    password: str
    phone: str
    annual_income: float = Field(..., gt=0, le=1_000_000_000)
    employment_status: EmploymentStatus
    credit_score: int | None = Field(default=None, ge=300, le=900)
    date_of_birth: date | None = None
    years_with_employer: float | None = Field(default=None, ge=0, le=60)
    existing_monthly_emi: float = Field(default=0, ge=0)

    _check_name = field_validator("name")(check_name)
    _check_password = field_validator("password")(check_password)
    _check_phone = field_validator("phone")(check_phone)
    _check_dob = field_validator("date_of_birth")(check_date_of_birth)


class LoginRequest(BaseModel):
    """JSON body, not a form. The trainer's fixture posts {email, password} (T-05)."""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_hours: int
    email: str
    role: UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: UtcDateTime | None = None
