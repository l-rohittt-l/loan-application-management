"""
Summarising a tool's output when it is too long to hand back as-is.

Every tool call becomes part of the conversation the model has to re-read on
its next thinking step. A long list of applications repeated across several
turns eats into the model's context window fast, and Gemini's free tier also
counts every character. So anything a tool returns past 2000 characters is
condensed to the facts that matter before it goes back to the agent.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger()

SUMMARIZE_ABOVE_CHARS = 2000


def summarize_text(text: str) -> str:
    """
    Condense a long piece of tool output to its important facts.

    Uses a plain, non-agentic call to the chat model — no tools, no reasoning
    loop, just "shorten this" — so it costs one call and cannot itself call a
    tool or loop.
    """
    from llm_provider import get_llm

    if not text:
        return text

    llm = get_llm(temperature=0)
    prompt = (
        "Summarise the following in a few short sentences. Keep every number, "
        "status, and application ID exactly as written. Do not add anything "
        "that is not in the text.\n\n" + text
    )
    try:
        response = llm.invoke(prompt)
        summary = (response.content if hasattr(response, "content") else str(response)).strip()
    except Exception as e:                                     # noqa: BLE001
        logger.warning("summarize_failed", error=str(e)[:200])
        # A failed summary is not worth crashing the agent over. Fall back to a
        # plain truncation so the agent still has something to reason about.
        summary = text[:SUMMARIZE_ABOVE_CHARS] + " …(truncated)"

    logger.info("agent_summarize", operation="summarize",
                input_length=len(text), output_length=len(summary),
                compression_ratio=round(len(summary) / len(text), 3) if text else 0)
    return summary
