"""
Phase 1 database tests. TC-01-P1-DB-01 to DB-04, from the trainer's
phase1-test-spec.md. Function names are the trainer's.

These talk to SQLAlchemy directly, no HTTP. Two of them point an application
at applicant id 1 when no such applicant exists; that only works because
SQLite's foreign-key checking is off (T-03).
"""


def test_application_created_in_db(db_session, test_user):
    """TC-01-P1-DB-01: Application record persisted with correct fields and defaults."""
    from app.models.applicant import Applicant
    from app.models.application import LoanApplication, ApplicationStatus

    # Create applicant directly
    applicant = Applicant(name="DB Test", email="db@test.com", phone="1234567890",
                          annual_income=500000, employment_status="salaried")
    db_session.add(applicant)
    db_session.commit()

    # Create application
    app = LoanApplication(applicant_id=applicant.id, loan_type="personal",
                          amount_requested=100000, tenure_months=12, purpose="Test")
    db_session.add(app)
    db_session.commit()

    # Query and verify
    db_app = db_session.query(LoanApplication).filter(LoanApplication.id == app.id).first()
    assert db_app is not None
    assert db_app.status == ApplicationStatus.submitted
    assert db_app.amount_requested == 100000
    assert db_app.submitted_at is not None


def test_status_history_recorded(db_session):
    """TC-01-P1-DB-02: Status history recorded on status change."""
    from app.models.application import LoanApplication, ApplicationStatus
    from app.models.status_history import StatusHistory

    # Create application
    app = LoanApplication(applicant_id=1, loan_type="personal",
                          amount_requested=50000, tenure_months=12, purpose="Test")
    db_session.add(app)
    # The trainer's skeleton reads app.id on the next line, but the row has
    # not been saved yet so the id is still None (T-36). flush() saves it and
    # fills in the id without ending the transaction.
    db_session.flush()
    # Add initial history
    history = StatusHistory(application_id=app.id, old_status=None,
                            new_status=ApplicationStatus.submitted,
                            changed_by="system", remarks="Submitted")
    db_session.add(history)
    db_session.commit()

    # Update status
    app.status = ApplicationStatus.under_review
    history2 = StatusHistory(application_id=app.id,
                             old_status=ApplicationStatus.submitted,
                             new_status=ApplicationStatus.under_review,
                             changed_by="officer@test.com",
                             remarks="Starting review")
    db_session.add(history2)
    db_session.commit()

    records = db_session.query(StatusHistory).filter(
        StatusHistory.application_id == app.id
    ).all()
    assert len(records) == 2
    assert records[1].old_status == ApplicationStatus.submitted
    assert records[1].new_status == ApplicationStatus.under_review
    assert records[1].changed_by == "officer@test.com"


def test_document_upload_persisted(db_session):
    """TC-01-P1-DB-03: Document persisted and linked to the application, unverified by default."""
    from app.models.application import LoanApplication
    from app.models.document import Document, DocumentType

    app = LoanApplication(applicant_id=1, loan_type="home",
                          amount_requested=2000000, tenure_months=120, purpose="House")
    db_session.add(app)
    db_session.commit()

    doc = Document(application_id=app.id, doc_type=DocumentType.id_proof,
                   file_name="aadhaar_card.pdf")
    db_session.add(doc)
    db_session.commit()

    saved_doc = db_session.query(Document).filter(
        Document.application_id == app.id
    ).first()
    assert saved_doc is not None
    assert saved_doc.doc_type == DocumentType.id_proof
    assert saved_doc.verified == False
    assert saved_doc.file_name == "aadhaar_card.pdf"


def test_cascade_delete_documents(db_session):
    """TC-01-P1-DB-04: Deleting an application deletes its documents."""
    from app.models.application import LoanApplication
    from app.models.document import Document, DocumentType

    app = LoanApplication(applicant_id=1, loan_type="personal",
                          amount_requested=50000, tenure_months=12, purpose="Test")
    db_session.add(app)
    db_session.commit()
    app_id = app.id

    for doc_type in [DocumentType.id_proof, DocumentType.income_proof]:
        doc = Document(application_id=app_id, doc_type=doc_type, file_name="test.pdf")
        db_session.add(doc)
    db_session.commit()

    # Verify 2 docs exist
    assert db_session.query(Document).filter(Document.application_id == app_id).count() == 2

    # Delete application
    db_session.delete(app)
    db_session.commit()

    # Verify documents also deleted
    assert db_session.query(Document).filter(Document.application_id == app_id).count() == 0
