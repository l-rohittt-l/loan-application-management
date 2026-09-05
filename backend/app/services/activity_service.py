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
