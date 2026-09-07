"""
Shared setup for the Phase 4 tests. Same shape as Phase 3's conftest — see
the reasoning there. Copied rather than imported because pytest fixtures are
discovered per test-folder and the trainer's own layout keeps each phase's
tests self-contained.
"""

import os
import subprocess
import sys
import time

import pytest
import requests

os.environ.setdefault("OTEL_EXPORTER", "none")

HEALTH = "http://localhost:8000/health"


def _api_answers(timeout: float = 1.0) -> bool:
    try:
        requests.get(HEALTH, timeout=timeout)
        return True
    except requests.exceptions.RequestException:
        return False


@pytest.fixture(scope="session")
def running_api():
    """The Phase 1 API, running — started here if it isn't already."""
    if _api_answers():
        yield
        return

    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        env={**os.environ, "OTEL_EXPORTER": "none"},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 20
    while time.time() < deadline:
        if _api_answers():
            break
        time.sleep(0.5)
    else:
        process.terminate()
        pytest.fail("The Phase 1 API did not start within 20 seconds")

    yield

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="session")
def executor():
    """One chat agent, shared by every test that needs the LLM (T-55: the free tier's rate limit)."""
    from mcp_server.chat_interface import build_executor

    return build_executor()


@pytest.fixture
def sample_applicant_id(running_api):
    """
    A real applicant id to submit test applications against, created fresh
    rather than assumed to be "1" — the seed data can change, and Phase 4's
    own MCP-03 test needs a genuine applicant to attach a submission to.
    """
    from app.services.loan_api_client import api_get, service_token
    import requests as _requests

    ok, data = api_get("/applicants", params={"limit": 1})
    if ok and data.get("items"):
        return data["items"][0]["id"]

    # No applicants yet (a completely fresh database) - create one.
    token = service_token()
    resp = _requests.post(
        "http://localhost:8000/api/v1/applicants",
        json={"name": "MCP Test Applicant", "email": "mcp.test@example.com",
              "phone": "9998887777", "credit_score": 720,
              "annual_income": 700000.0, "employment_status": "salaried"},
        headers={"Authorization": f"Bearer {token}"}, timeout=8,
    )
    resp.raise_for_status()
    return resp.json()["id"]
