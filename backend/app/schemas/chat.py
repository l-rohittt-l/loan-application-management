"""
What goes in and out of the one chat address.

Kept deliberately open at the edges so the later phases can add to it without
changing what the screens already send. `mode` tells the screen which brain
answered, and `sources` lets it show the manual extracts the answer came from —
which is what turns "trust the AI" into "check the AI".
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=0, max_length=2000,
                         description="What the person typed")
    session_id: str | None = Field(
        None, max_length=64,
        description="Groups messages into one conversation. Phase 4 uses it for "
                    "session memory; Phase 2 accepts and ignores it.",
    )


class ChatSource(BaseModel):
    """One extract from the manual that the answer was based on."""
    chunk_id: str | None = None
    source: str | None = None
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    # Which brain answered: "rag" from the manual, "empty" for a blank message.
    # Phase 3 adds "agent", Phase 5 adds "review".
    mode: str
    sources: list[ChatSource] = []
    duration_ms: float
