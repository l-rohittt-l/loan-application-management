"""
The logic behind documents on an application.
"""

import structlog
from sqlalchemy.orm import Session

from app.domain import rules
from app.models.application import LoanApplication
from app.models.document import Document
from app.models.user import User, UserRole
from app.schemas.document import CreateDocumentSchema
from app.services import activity_service
from app.services.errors import Forbidden, NotFound

logger = structlog.get_logger()


def _application_for(db: Session, application_id: int, viewer: User) -> LoanApplication:
    """Load the application and check the viewer may touch it."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if application is None:
        raise NotFound(f"Application {application_id} not found")
    if viewer.role == UserRole.applicant and application.applicant.user_id != viewer.id:
        raise Forbidden("You can only manage documents on your own applications")
    return application


def add_document(
    db: Session, data: CreateDocumentSchema, *, user: User, meta: dict | None = None
) -> Document:
    """
    Record a document. The same type may be added more than once; both are
    kept (user story 05). New documents start unverified.
    """
    application = _application_for(db, data.application_id, user)

    document = Document(
        application_id=application.id,
        doc_type=data.doc_type,
        file_name=data.file_name,
        verified=False,
    )
    db.add(document)
    db.flush()

    activity_service.record(
        db, action="document_added",
        actor_id=user.email, actor_role=user.role.value,
        entity_type="document", entity_id=document.id,
        details={"application_id": application.id, "doc_type": data.doc_type.value,
                 "file_name": data.file_name},
        **(meta or {}),
    )
    db.commit()
    db.refresh(document)
    logger.info("document_added", application_id=application.id, document_id=document.id,
                doc_type=data.doc_type.value)
    return document


def list_documents(
    db: Session, application_id: int, *, viewer: User
) -> tuple[list[Document], list[str], list[str]]:
    """The documents on an application, what the loan type requires, and what is still missing."""
    application = _application_for(db, application_id, viewer)
    documents = (
        db.query(Document)
        .filter(Document.application_id == application.id)
        .order_by(Document.uploaded_at, Document.id)
        .all()
    )
    required = sorted(rules.required_documents(application.loan_type))
    missing = rules.missing_documents(application.loan_type, [d.doc_type for d in documents])
    return documents, required, missing


def verify_document(
    db: Session, application_id: int, document_id: int, *, user: User, meta: dict | None = None
) -> Document:
    """A loan officer marks a document as checked. Staff only; the router enforces that."""
    application = _application_for(db, application_id, user)
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.application_id == application.id)
        .first()
    )
    if document is None:
        raise NotFound(f"Document {document_id} not found on application {application_id}")

    document.verified = True
    activity_service.record(
        db, action="document_verified",
        actor_id=user.email, actor_role=user.role.value,
        entity_type="document", entity_id=document.id,
        details={"application_id": application.id, "doc_type": document.doc_type.value},
        **(meta or {}),
    )
    db.commit()
    db.refresh(document)
    logger.info("document_verified", application_id=application.id, document_id=document.id,
                verified_by=user.email)
    return document
