"""
Phase 1 unit tests. TC-01-P1-UNIT-01 to UNIT-08, from the trainer's
phase1-test-spec.md. Function names are the trainer's.
"""

import pytest
from pydantic import ValidationError

from app.schemas import CreateApplicantSchema, CreateApplicationSchema, CreateDocumentSchema
from app.services import applicant_service


def test_create_applicant_valid(db_session):
    """TC-01-P1-UNIT-01: Create applicant with valid data."""
    # Arrange
    data = CreateApplicantSchema(
        name="Priya Sharma", email="priya@example.com",
        phone="9876543210", credit_score=720,
        annual_income=600000.0, employment_status="salaried"
    )
    # Act
    applicant = applicant_service.create_applicant(db_session, data)
    # Assert
    assert applicant.id is not None
    assert applicant.email == "priya@example.com"
    assert applicant.credit_score == 720
    assert applicant.created_at is not None


def test_create_applicant_invalid_email():
    """TC-01-P1-UNIT-02: Reject invalid email format."""
    with pytest.raises(ValidationError) as exc_info:
        CreateApplicantSchema(
            name="Test", email="not-an-email",
            phone="9876543210", annual_income=500000,
            employment_status="salaried"
        )
    assert "email" in str(exc_info.value).lower()


def test_calculate_emi_correctly():
    """TC-01-P1-UNIT-03: Calculate EMI correctly (₹5,00,000 at 12% over 36 months ≈ ₹16,607)."""
    from app.utils.finance import calculate_emi
    result = calculate_emi(principal=500000, annual_rate=12, tenure_months=36)
    assert 16597 <= result <= 16617, f"Expected ~16607, got {result}"


@pytest.mark.parametrize("amount", [5000, 15000000, -100, 0])
def test_validate_loan_amount_bounds(amount):
    """TC-01-P1-UNIT-04: Validate loan amount bounds (10,000 to 1,00,00,000)."""
    with pytest.raises(ValidationError):
        CreateApplicationSchema(
            applicant_id=1, loan_type="personal",
            amount_requested=amount, tenure_months=24,
            purpose="Test"
        )


def test_status_transition_valid():
    """TC-01-P1-UNIT-05: Accept valid status transition."""
    from app.services.application_service import validate_status_transition
    from app.models.application import ApplicationStatus
    # Should not raise
    assert validate_status_transition(
        ApplicationStatus.submitted,
        ApplicationStatus.under_review
    ) == True


def test_status_transition_invalid():
    """TC-01-P1-UNIT-06: Reject invalid (backward) status transition."""
    from app.services.application_service import validate_status_transition
    from app.models.application import ApplicationStatus
    result = validate_status_transition(
        ApplicationStatus.approved,
        ApplicationStatus.submitted
    )
    assert result == False


def test_document_type_validation_invalid():
    """TC-01-P1-UNIT-07: Validate document type enum (invalid value rejected)."""
    with pytest.raises(ValidationError):
        CreateDocumentSchema(
            application_id=1,
            doc_type="passport_copy",
            file_name="passport.pdf"
        )


def test_document_type_validation_valid():
    """TC-01-P1-UNIT-07: Validate document type enum (valid value accepted)."""
    # Should not raise
    doc = CreateDocumentSchema(
        application_id=1, doc_type="id_proof", file_name="aadhaar.pdf"
    )
    assert doc.doc_type == "id_proof"


@pytest.mark.parametrize("score", [1200, 100, -1, 0])
def test_credit_score_validation_invalid(score):
    """TC-01-P1-UNIT-08: Reject credit score outside 300 to 900."""
    with pytest.raises(ValidationError):
        CreateApplicantSchema(
            name="Test", email="test@test.com", phone="9876543210",
            credit_score=score, annual_income=500000, employment_status="salaried"
        )
