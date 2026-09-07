"""
One place to turn an LLM response's `.content` into plain text.

`ChatGoogleGenerativeAI.content` is not always a string — this model version
sometimes returns a list of content blocks, each a dict with a `"text"` key,
instead. Found by actually running the risk assessor and decision maker
agents rather than by reading the library's type hints: every call silently
fell back to a deterministic summary because `.strip()` on a list raised,
until this normalised both shapes to plain text. Shared here so both agents
that call an LLM for prose (never for a number that matters) use the same fix.
"""


def text_of(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return " ".join(
            (part.get("text", "") if isinstance(part, dict) else str(part)) for part in content
        ).strip()
    return str(content).strip()
