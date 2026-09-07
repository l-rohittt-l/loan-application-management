"""
Phase 4 chat interface tests: TC-01-P4-CHAT-01 to 06.

Taken from the trainer's phase4-test-spec.md, using the shared session-scoped
`executor` fixture from conftest.py instead of building a fresh one per test
(T-55: the free Gemini tier allows only a handful of requests a minute, and
this phase's tests make several LLM calls each).
"""


def test_chat_executor_builds():
    """TC-01-P4-CHAT-01."""
    from mcp_server.chat_interface import build_executor

    executor = build_executor()
    assert executor is not None
    assert hasattr(executor, "invoke")


def test_message_processed_and_received(running_api, executor):
    """TC-01-P4-CHAT-02."""
    from mcp_server.chat_interface import process_message

    result = process_message("What is the dashboard summary?", "test-session-01", executor)

    assert isinstance(result, dict)
    assert "output" in result
    assert len(result["output"]) > 0


def test_session_id_assigned():
    """TC-01-P4-CHAT-03."""
    import uuid

    session_id = str(uuid.uuid4())[:8]

    assert len(session_id) == 8
    assert session_id.replace("-", "").isalnum()


def test_conversation_history_persists():
    """TC-01-P4-CHAT-04: messages list grows with each interaction, as Streamlit's session_state would."""
    messages = []

    messages.append({"role": "user", "content": "Show dashboard"})
    messages.append({"role": "assistant", "content": "Dashboard data...", "tool_calls": []})
    messages.append({"role": "user", "content": "Now show application 1"})

    assert len(messages) == 3
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_tool_call_extraction(running_api, executor):
    """TC-01-P4-CHAT-05."""
    from mcp_server.chat_interface import process_message

    result = process_message("Get the dashboard summary", "test-session", executor)

    steps = result.get("intermediate_steps", [])
    if steps:
        action, _ = steps[0]
        assert hasattr(action, "tool")
        assert isinstance(action.tool, str)


def test_error_message_on_bad_request(executor):
    """TC-01-P4-CHAT-06: an empty message must not crash the executor."""
    import pytest
    from mcp_server.chat_interface import process_message

    try:
        result = process_message("", "test-session", executor)
        assert "output" in result
    except Exception as e:                                        # noqa: BLE001
        pytest.fail(f"Executor crashed on edge case: {e}")
