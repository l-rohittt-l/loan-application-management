"""
Schemas for documents.

`CreateDocumentSchema` is a name the trainer's tests import (T-06).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.document import DocumentType

# Manual Section 12: documents must be PDF, JPG or PNG.
_ALLOWED_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png")


class CreateDocumentSchema(BaseModel):
    application_id: int = Field(..., gt=0)
    # One of the six types. Test UNIT-07 sends "passport_copy" and expects a rejection.
    doc_type: DocumentType
    file_name: str = Field(..., min_length=1, max_length=255)

    @field_validator("file_name")
    @classmethod
    def check_file_name(cls, value: str) -> str:
        value = value.strip()
        if not value.lower().endswith(_ALLOWED_EXTENSIONS):
            raise ValueError("file_name must end in .pdf, .jpg, .jpeg or .png")
        # Guard against path tricks like "../../etc/passwd".
        if "/" in value or "\\" in value:
            raise ValueError("file_name must not contain folder separators")
        return value


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    doc_type: DocumentType
    file_name: str
    uploaded_at: datetime | None = None
    verified: bool
