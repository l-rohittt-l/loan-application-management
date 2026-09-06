"""
Shared setup for the Phase 3 tests.

`running_api` is referenced by the trainer's spec but never defined in it. Their
intended version simply skips the test when port 8000 doesn't answer, which
quietly turns a dozen tests into "didn't run" the moment somebody forgets to
start the server — and a skipped test reads exactly like a passing one in a
summary line. So this version starts the server itself when it isn't already up,
and only stops what it started, never a server the developer had running.

The agent executor is built once for the whole session. Building it is not free,
and every end-to-end test would otherwise construct its own — which also matters
because the free Gemini tier allows only a handful of requests a minute (T-55).
"""

import os
import subprocess
import sys
import time

import pytest
import requests

# Spans off by default so the test output stays readable.
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
    """One agent, shared by every end-to-end test."""
    from agent.agent import build_agent

    return build_agent()
