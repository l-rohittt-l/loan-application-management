"""
The Manager's Morning Briefing address. Mounted at /api/v1/briefing by main.py.

Manager-only, the same gate the activity log uses: this reads across every
customer's application at once, which is a branch-level view rather than a
per-file one.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_manager
from app.models.user import User
from app.schemas.briefing import BriefingResponse
from app.services import briefing_service
from app.services.activity_service import request_meta

router = APIRouter()


@router.get("", response_model=BriefingResponse)
def morning_briefing(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    """
    Today's pipeline, read and summarised. The numbers are computed from the
    database; the narrative is written from those numbers by the AI, and
    `written_by_ai` says whether that succeeded.
    """
    return briefing_service.build_briefing(db, user=user, meta=request_meta(request))
