"""
Writes one row to the activity log (Rohit's addition, D-11).

Every service that does something worth remembering calls `record(...)`.
Because every phase goes through the same services, the Phase 3 chatbot,
the Phase 4 assistant and the Phase 5 agents get recorded for free.

`record` adds the row to the session but does NOT commit. The caller commits
together with whatever else it changed, so the log and the change land
together or not at all.
"""

import json

from fastapi import Request
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog, ActorType


def record(
    db: Session,
    *,
    action: str,
    actor_id: str,
    actor_type: ActorType = ActorType.human,
    actor_role: str | None = None,
    on_behalf_of: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    details: dict | None = None,
    request_id: str | None = None,
    ip_address: str | None = None,
) -> ActivityLog:
    row = ActivityLog(
        action=action,
        actor_id=actor_id,
        actor_type=actor_type,
        actor_role=actor_role,
        on_behalf_of=on_behalf_of,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details) if details else None,
        request_id=request_id,
        ip_address=ip_address,
    )
    db.add(row)
    db.flush()   # get the id now; commit happens with the caller's transaction
    return row


def list_activity(
    db: Session,
    *,
    page: int = 1,
    limit: int = 50,
    actor_id: str | None = None,
    actor_type: ActorType | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    from_date=None,
    to_date=None,
) -> tuple[list[ActivityLog], int]:
    """A page of events, newest first, with optional filters combined with AND."""
    from datetime import datetime, time

    query = db.query(ActivityLog)
    if actor_id:
        # Searching for a person should not mean typing their whole email.
        # "anita" finds anita@bank.com, and capital letters do not matter.
        # It also looks at who an AI was acting for, so searching a person's
        # name finds work an assistant did on their behalf.
        term = f"%{actor_id.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(ActivityLog.actor_id).like(term),
                func.lower(ActivityLog.on_behalf_of).like(term),
            )
        )
    if actor_type:
        query = query.filter(ActivityLog.actor_type == actor_type)
    if action:
        query = query.filter(ActivityLog.action == action)
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(ActivityLog.entity_id == entity_id)
    if from_date:
        query = query.filter(ActivityLog.created_at >= datetime.combine(from_date, time.min))
    if to_date:
        query = query.filter(ActivityLog.created_at <= datetime.combine(to_date, time.max))

    total = query.count()
    items = (
        query.order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


def history_for(db: Session, entity_type: str, entity_id: int) -> list[ActivityLog]:
    """Everything that ever happened to one record, oldest first."""
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.entity_type == entity_type, ActivityLog.entity_id == entity_id)
        .order_by(ActivityLog.created_at, ActivityLog.id)
        .all()
    )


def request_meta(request: Request | None) -> dict:
    """
    Pull the request id and caller's IP off a request, for `record(...)`.
    The request id is set by the logging middleware (Piece 12). Until then
    it is simply missing, which is fine.
    """
    if request is None:
        return {}
    return {
        "request_id": getattr(request.state, "request_id", None),
        "ip_address": request.client.host if request.client else None,
    }
