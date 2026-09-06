"""
One HTTP client for talking to this project's own Phase 1 API.

Phase 3's tools, Phase 4's MCP tools, and Phase 5's data collector all need to
call the loan API over HTTP as a signed-in user. Writing that three times is
exactly how the trainer's own reference code ended up with three different and
inconsistently buggy versions of the same idea — a static token in one, an HTTP
call that raises in another. So it lives here once.

Two rules this module exists to enforce:

**It never raises.** Every call returns `(True, data)` or `(False, "a plain
sentence")`. A tool that raises kills the whole conversation it was part of; a
tool that returns a sentence lets the assistant say "the loan system is
unavailable right now" and carry on. The trainer's Phase 4 skeleton calls
`raise_for_status()`, which would end an agent's turn with a stack trace on any
error that isn't a 404.

**The token is minted fresh every call.** Both the Phase 4 and Phase 5 skeletons
read a fixed `API_JWT_TOKEN` out of `.env`. Tokens here expire 24 hours after
they are issued (T-24), so a token pasted into `.env` on a Friday stops working
on a Saturday — most likely mid-demo, as a confusing 401 with no obvious cause.
Minting one per call costs nothing (it is a local signing operation, no network)
and cannot go stale.
"""

from __future__ import annotations

import os

import requests
import structlog

from app.config import settings
from app.utils.auth import create_access_token
from app.utils.otel_config import get_tracer

logger = structlog.get_logger()

REQUEST_TIMEOUT_SECONDS = 8


def _normalise(raw: str) -> str:
    """Accept either "http://host:8000" or "http://host:8000/api/v1"; return the former."""
    return raw[: -len("/api/v1")] if raw.endswith("/api/v1") else raw


def base_url() -> str:
    """
    The API's address, re-read from the environment on every call.

    Deliberately *not* captured once at import time. The trainer's
    TC-01-P3-EXEC-06 proves the tools notice a changed address by patching
    `API_BASE_URL` and calling `importlib.reload()` on the tools module — but
    reloading that module does not re-execute *this* one, since Python keeps it
    in `sys.modules`. A value frozen here would silently survive the reload and
    the tools would keep calling the old address. Reading it per call is one
    dictionary lookup and cannot go stale.
    """
    return _normalise(os.getenv("API_BASE_URL", settings.api_base_url))


# Kept for anything that wants to read the address without making a call.
API_BASE_URL = base_url()


def service_token(role: str = "branch_manager") -> str:
    """
    A signed-in identity for the AI layers to call the API as.

    Every Phase 1 endpoint is owner-scoped and role-checked, so the agent has to
    be somebody — it cannot call anonymously. It acts as a branch manager
    because that role can read everything and perform every status change, which
    is the widest the API itself allows; the API's own permission checks still
    apply on every single call.
    """
    return create_access_token(email=settings.agent_service_email, role=role)


def _extract_detail(response: requests.Response) -> str:
    """Pull FastAPI's error message out of a failed response, whatever shape it took."""
    try:
        detail = response.json().get("detail")
    except Exception:                                          # noqa: BLE001
        return response.text[:200] or f"status {response.status_code}"
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        # Pydantic validation errors: [{"loc": [...], "msg": "..."}, ...]
        return "; ".join(
            f"{(item.get('loc') or ['field'])[-1]}: {item.get('msg', '')}"
            for item in detail
        )
    return str(detail) if detail else f"status {response.status_code}"


def _request(method: str, path: str, *, params: dict | None = None,
             body: dict | None = None) -> tuple[bool, dict | str]:
    """
    Make one call. Returns (True, parsed json) or (False, a readable sentence).

    The sentence matters: it is what an AI assistant ends up saying to a person,
    so "The loan system is unavailable right now" is the right answer and
    `ConnectionError` is not.
    """
    tracer = get_tracer()
    url = f"{base_url()}/api/v1{path}"

    with tracer.start_as_current_span("api.call") as span:
        span.set_attribute("api.endpoint", path)
        span.set_attribute("api.method", method)
        try:
            response = requests.request(
                method, url, params=params, json=body,
                headers={"Authorization": f"Bearer {service_token()}"},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.exceptions.ConnectionError:
            span.set_attribute("api.status_code", 0)
            logger.warning("api_unavailable", operation="api_call", endpoint=path)
            return False, ("The loan system's API is unavailable right now, so I "
                           "cannot fetch live data. Please try again shortly.")
        except requests.exceptions.Timeout:
            span.set_attribute("api.status_code", 0)
            logger.warning("api_timeout", operation="api_call", endpoint=path)
            return False, "The loan system took too long to respond. Please try again."

        span.set_attribute("api.status_code", response.status_code)

        if response.status_code == 404:
            # Deliberately a bare marker rather than a sentence: callers phrase
            # "not found" differently ("Application not found", "Applicant not
            # found"), and they need to be able to tell this apart from a real error.
            return False, "not found"
        if response.status_code >= 400:
            detail = _extract_detail(response)
            logger.warning("api_error", operation="api_call", endpoint=path,
                           status_code=response.status_code, detail=detail[:200])
            return False, f"The loan system returned an error: {detail}"

        return True, (response.json() if response.content else {})


def api_get(path: str, params: dict | None = None) -> tuple[bool, dict | str]:
    return _request("GET", path, params=params)


def api_post(path: str, body: dict | None = None) -> tuple[bool, dict | str]:
    return _request("POST", path, body=body)


def api_patch(path: str, body: dict | None = None) -> tuple[bool, dict | str]:
    return _request("PATCH", path, body=body)
