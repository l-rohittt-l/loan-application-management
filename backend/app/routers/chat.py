"""
The one chat address for the whole assistant.

**This endpoint is deliberately the only chat door in the product, and it does
not change as the phases are added.** The mentor's instruction was one chat box
rather than three — a policy question, a data question and an instruction should
all go to the same place, and the assistant should work out for itself what kind
of question it just received.

So the front-end talks to `POST /api/v1/chat` and always will. What sits behind
it grows:

    Phase 2 (now)  the RAG chain, answering policy questions from the manual
    Phase 3        a tool-using agent that can also read live application data
    Phase 4        the same agent, with its tools served over MCP
    Phase 5        the multi-agent reviewer for "assess application 7"

Each phase replaces the brain behind this door. No screen has to be rewritten,
and the demo shows one assistant getting steadily more capable instead of three
disconnected chatbots.

The `mode` field in the reply says which brain answered. It is what lets the
screen show "answered from the user manual" versus "read from live data", and
it is genuinely useful in a demo: it makes the routing visible instead of
magic.
"""

from __future__ import annotations

import time

import structlog
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services import activity_service

logger = structlog.get_logger()

router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Ask the assistant something.

    Anyone signed in may ask. What comes back is limited by who is asking:
    from Phase 3 onwards the tools that read live data check the caller's role,
    so a customer asking "show me application 5" only ever sees their own.
    """
    started = time.perf_counter()
    question = body.message.strip()

    if not question:
        return ChatResponse(
            answer="Ask me something about loans, and I will answer from the bank's manual.",
            mode="empty",
            sources=[],
            duration_ms=0.0,
        )

    # Phase 2's brain. Phase 3 swaps this for the agent, which will still call
    # the same RAG chain underneath for policy questions.
    from rag.rag_chain import answer_question, get_chain

    chain, retriever = get_chain()
    result = answer_question(question, chain, retriever)

    duration_ms = round((time.perf_counter() - started) * 1000, 2)

    activity_service.record(
        db, action="chat_message",
        actor_id=user.email, actor_role=user.role.value,
        entity_type="chat",
        details={"question": question[:200], "mode": "rag",
                 "sources": len(result["sources"])},
        **activity_service.request_meta(request),
    )
    db.commit()

    logger.info("chat_answered", operation="chat_answered",
                question=question[:200], mode="rag",
                sources=len(result["sources"]), duration_ms=duration_ms)

    return ChatResponse(
        answer=result["answer"],
        mode="rag",
        sources=[
            ChatSource(
                chunk_id=s["chunk_id"],
                source=s["source"],
                excerpt=s["excerpt"][:600],
            )
            for s in result["sources"]
        ],
        duration_ms=duration_ms,
    )
