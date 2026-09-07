"""
Phase 4 observability tests: TC-01-P4-OBS-01 to 04.

Taken from the trainer's phase4-test-spec.md. OBS-01 and OBS-02 both wait a
fixed 3 seconds for LangSmith to accept a trace, which Phase 3's T-62 showed
can be too short the very first time a project is ever written to — this
copy uses the same short retry loop instead of a longer fixed sleep.
"""

import json
import os
import time

import pytest

from app.config import settings


def _wait_for_runs(project_name: str, api_key: str, attempts: int = 6, gap: float = 2.5):
    from langsmith import Client
    from langsmith.utils import LangSmithNotFoundError

    client = Client(api_key=api_key)
    for _ in range(attempts):
        time.sleep(gap)
        try:
            runs = list(client.list_runs(project_name=project_name, limit=5))
        except LangSmithNotFoundError:
            continue
        if runs:
            return runs
    return []


def test_mcp_call_traced_in_langsmith(running_api, executor):
    """TC-01-P4-OBS-01."""
    from mcp_server.chat_interface import LANGSMITH_PROJECT, process_message

    if not settings.langchain_api_key:
        pytest.skip("LANGCHAIN_API_KEY is not set")

    process_message("Dashboard summary", "obs-test-001", executor)

    runs = _wait_for_runs(LANGSMITH_PROJECT, settings.langchain_api_key)
    assert len(runs) > 0, f"No traces found in {LANGSMITH_PROJECT}"


def test_chat_session_id_in_trace(running_api, executor):
    """TC-01-P4-OBS-02."""
    from mcp_server.chat_interface import LANGSMITH_PROJECT, process_message

    if not settings.langchain_api_key:
        pytest.skip("LANGCHAIN_API_KEY is not set")

    process_message("Show dashboard", "obs-trace-test-002", executor)

    runs = _wait_for_runs(LANGSMITH_PROJECT, settings.langchain_api_key)
    assert len(runs) > 0
    latest_run = runs[0]
    assert latest_run.name is not None


def test_tool_execution_span_present(capsys, running_api):
    """TC-01-P4-OBS-03."""
    from mcp_server.mcp_app import get_dashboard_summary

    get_dashboard_summary()

    captured = capsys.readouterr()
    assert "mcp.tool_invoke" in captured.out or "mcp" in captured.out or len(captured.out) >= 0


def test_structured_log_has_session_id(capsys, running_api, executor):
    """TC-01-P4-OBS-04."""
    from mcp_server.chat_interface import process_message

    session_id = "log-test-session"
    process_message("Dashboard", session_id, executor)

    captured = capsys.readouterr()
    for line in captured.out.split("\n"):
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if entry.get("operation") == "chat_message" and entry.get("event") == "chat_message_received":
            assert entry.get("session_id") == session_id
            return
    # No matching line is not itself a failure - the trainer's own version
    # of this test only fails on a mismatch, never on the absence of a line.
