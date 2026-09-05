"""
The `activity_log` table: who did what, and when.

Rohit's addition (D-11). Records business events, never raw debug output.
Because every phase goes through the same API, the chatbot in Phase 3, the
assistant in Phase 4 and the agents in Phase 5 all get recorded here without
extra work, and each row says whether a person or an AI did it.
"""

import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class ActorType(str, enum.Enum):
    human = "human"
    ai = "ai"


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)

    # Who did it.
    actor_type = Column(Enum(ActorType), nullable=False, default=ActorType.human)
    # A person's email, or an AI agent's name like "phase3_agent".
    actor_id = Column(String(150), nullable=False, index=True)
    actor_role = Column(String(30), nullable=True)
    # When an AI acts for a logged-in user, that user's email goes here.
    on_behalf_of = Column(String(150), nullable=True)

    # What happened.
    action = Column(String(60), nullable=False, index=True)     # e.g. "status_changed"
    entity_type = Column(String(40), nullable=True)             # e.g. "application"
    entity_id = Column(Integer, nullable=True, index=True)
    details = Column(Text, nullable=True)                       # small JSON string

    # Where it came from.
    request_id = Column(String(64), nullable=True)
    ip_address = Column(String(45), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
