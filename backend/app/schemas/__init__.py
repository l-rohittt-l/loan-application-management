"""
Schemas: what each request may contain, and what each response looks like.

Pydantic checks incoming data against these before any of our code runs.
Bad data gets a 422 error listing the exact problems.
"""

from app.schemas.auth import (
    RegisterRequest, ApplicantSignupRequest, LoginRequest, TokenResponse, UserResponse,
)
from app.schemas.applicant import CreateApplicantSchema, ApplicantResponse
from app.schemas.application import (
    CreateApplicationSchema, StatusUpdateRequest, StatusHistoryResponse,
    ApplicationResponse, ApplicationSummary, ApplicationListResponse,
    EligibilityCheckRequest, EligibilityCheckResponse,
)
from app.schemas.document import CreateDocumentSchema, DocumentResponse
from app.schemas.activity import ActivityLogResponse

__all__ = [
    "RegisterRequest", "ApplicantSignupRequest", "LoginRequest", "TokenResponse", "UserResponse",
    "CreateApplicantSchema", "ApplicantResponse",
    "CreateApplicationSchema", "StatusUpdateRequest", "StatusHistoryResponse",
    "ApplicationResponse", "ApplicationSummary", "ApplicationListResponse",
    "EligibilityCheckRequest", "EligibilityCheckResponse",
    "CreateDocumentSchema", "DocumentResponse",
    "ActivityLogResponse",
]
