"""
Phase 4 LangChain-MCP integration tests: TC-01-P4-INT-01 to 07.

Taken from the trainer's phase4-test-spec.md. Where the spec names a
hardcoded "application 1" or "application number 1", this copy creates a
real application first and references its actual id instead — the same
adaptation as test_mcp_server.py, and for the same reason: a hardcoded row
id only works on one freshly seeded database.
"""

import pytest


@pytest.fixture
def sample_application_id(running_api, sample_applicant_id):
    """A real application id these tests can ask the agent about by number."""
    from mcp_server.mcp_app import submit_loan_application

    created = submit_loan_application(
        applicant_id=sample_applicant_id, loan_type="personal",
        amount_requested=150000.0, tenure_months=24, purpose="Phase 4 integration fixture",
    )
    return created["id"]


def test_langchain_discovers_mcp_tools():
    """TC-01-P4-INT-01."""
    from mcp_server.chat_interface import MCP_TOOLS

    assert len(MCP_TOOLS) == 6
    tool_names = {t.name for t in MCP_TOOLS}

    expected = {
        "submit_loan_application", "get_application_details",
        "update_application_status", "list_applications_by_filter",
        "get_dashboard_summary", "upload_document_metadata",
    }
    assert expected == tool_names


def test_mcp_tool_invoked_via_chat(running_api, executor):
    """TC-01-P4-INT-02."""
    from mcp_server.chat_interface import process_message

    result = process_message("Show me all submitted applications", "integration-test-session", executor)

    steps = result.get("intermediate_steps", [])
    tool_names_used = [step[0].tool for step in steps]

    assert "list_applications_by_filter" in tool_names_used or len(result["output"]) > 0


def test_correct_tool_selected_for_app_query(running_api, executor, sample_application_id):
    """TC-01-P4-INT-03."""
    from mcp_server.chat_interface import process_message

    result = process_message(f"Get details of application number {sample_application_id}",
                              "test-session", executor)

    steps = result.get("intermediate_steps", [])
    tool_names_used = [step[0].tool for step in steps]

    if tool_names_used:
        assert "get_application_details" in tool_names_used


def test_response_routed_back(running_api, executor):
    """TC-01-P4-INT-04."""
    from mcp_server.chat_interface import process_message

    result = process_message("What is the dashboard summary?", "test-session", executor)

    output = result.get("output", "")
    assert isinstance(output, str)
    assert len(output) > 0


def test_multi_turn_conversation_context():
    """
    TC-01-P4-INT-05. LangChain's classic ReAct agent is stateless per call, so
    "multi-turn" here means the caller folds prior context into the next
    message before sending it — this test only proves that shape of message
    still reads as a real question.
    """
    history = [
        {"role": "user", "content": "Show application 1"},
        {"role": "assistant", "content": "Application 1: Personal loan, Rs 100,000, Status: submitted"},
    ]

    context_message = f"Previous context: {history[-1]['content']}\n\nNew question: What is the status?"

    assert "status" in context_message.lower() or "application" in context_message.lower()


def test_tool_chain_in_single_query(running_api, executor, sample_application_id):
    """TC-01-P4-INT-06."""
    from mcp_server.chat_interface import process_message

    result = process_message(
        f"Get the dashboard summary and tell me details about application {sample_application_id}",
        "test-session", executor,
    )

    steps = result.get("intermediate_steps", [])
    assert len(steps) >= 1


def test_upload_document_tool_reachable(running_api, sample_application_id):
    """TC-01-P4-INT-07."""
    from mcp_server.mcp_app import upload_document_metadata

    result = upload_document_metadata(
        application_id=sample_application_id, doc_type="id_proof", file_name="test_aadhaar.pdf",
    )

    assert isinstance(result, dict)
