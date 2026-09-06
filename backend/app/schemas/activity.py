"""
Schema for the manager's activity view (D-11).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.activity_log import ActorType
from app.schemas.common import UtcDateTime


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_type: ActorType
    actor_id: str
    actor_role: str | None = None
    on_behalf_of: str | None = None
    action: str
    entity_type: str | None = None
    entity_id: int | None = None
    details: str | None = None
    request_id: str | None = None
    ip_address: str | None = None
    created_at: UtcDateTime | None = None
