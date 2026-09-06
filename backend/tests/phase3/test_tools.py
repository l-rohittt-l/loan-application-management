"""
Phase 3 tool tests: TC-01-P3-TOOL-01 to 04 and TC-01-P3-EXEC-01 to 06.

Taken from the trainer's phase3-test-spec.md. The tool-definition tests are the
important ones despite looking trivial: the blueprint is explicit that what is
really graded in this phase is whether the model picks the right tool, and it
picks by reading the description text. A tool with a vague description fails
tests its own code was perfectly capable of passing.
"""

import importlib

import pytest

from agent.tools import (
    get_applicant_details,
    get_application_details,
    get_dashboard_summary,
    list_applications,
    search_loan_policy,
)

ALL_FIVE = [
    get_application_details,
    list_applications,
    get_dashboard_summary,
    search_loan_policy,
    get_applicant_details,
]


# --------------------------------------------------------------- definitions

def test_tool_schema_valid():
    """TC-01-P3-TOOL-01: every tool has a usable name and description."""
    for tool in ALL_FIVE:
        assert hasattr(tool, "name"), "Tool missing name"
        assert hasattr(tool, "description"), f"Tool {tool.name} missing description"
        assert len(tool.name) > 0
        assert len(tool.description) > 10


def test_tools_registered_in_agent():
    """TC-01-P3-TOOL-02: all five are actually wired into the agent."""
    from agent.agent import build_agent

    tool_names = {t.name for t in build_agent().tools}
    expected = {"get_application_details", "list_applications", "get_dashboard_summary",
                "search_loan_policy", "get_applicant_details"}
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"


def test_tool_description_present():
    """TC-01-P3-TOOL-03: the description tells the model when to use it."""
    description = get_application_details.description

    assert len(description) >= 50, f"Description too short: {description}"
    usage_indicators = ["use this", "when the user", "use when", "for questions"]
    assert any(indicator in description.lower() for indicator in usage_indicators)


def test_every_description_says_when_not_to_use_it():
    """
    Ours, not the trainer's. Telling the model when a tool *doesn't* apply is
    what stops it reaching for the application lookup on a policy question. The
    blueprint calls this out as the difference between passing and failing the
    end-to-end tests, so it is worth asserting rather than hoping.
    """
    for tool in ALL_FIVE:
        assert "do not use" in tool.description.lower(), (
            f"{tool.name}'s description never says when not to use it"
        )


def test_tool_input_validation():
    """TC-01-P3-TOOL-04: a plain string input is accepted, not rejected."""
    try:
        result = get_application_details.invoke("1")
        assert isinstance(result, str)
    except TypeError as e:
        pytest.fail(f"Tool rejected valid string input: {e}")


# ---------------------------------------------------------------- execution

def test_get_application_tool_returns_data(running_api):
    """TC-01-P3-EXEC-01: a real application comes back readable."""
    result = get_application_details.invoke("1")

    assert isinstance(result, str)
    assert "Application ID" in result or "not found" in result.lower()
    if "Application ID" in result:
        assert "Loan Type" in result
        assert "Status" in result


def test_list_applications_tool_filters_correctly(running_api):
    """TC-01-P3-EXEC-02: the list tool accepts filters and answers."""
    result = list_applications.invoke({"status": "submitted", "loan_type": ""})

    assert isinstance(result, str)
    assert len(result) > 0


def test_dashboard_tool_returns_summary(running_api):
    """TC-01-P3-EXEC-03: the dashboard tool returns the branch totals."""
    result = get_dashboard_summary.invoke({})

    assert isinstance(result, str)
    assert "Dashboard Summary" in result or "Total Applications" in result


def test_search_policy_tool_returns_answer(running_api):
    """TC-01-P3-EXEC-04: the policy tool answers from the Phase 2 manual."""
    result = search_loan_policy.invoke("What documents are required for a personal loan?")

    assert isinstance(result, str)
    assert len(result) > 20
    assert any(term in result.lower()
               for term in ["id_proof", "income_proof", "bank_statement", "document"])


def test_get_application_tool_handles_404(running_api):
    """
    TC-01-P3-EXEC-05: an application that doesn't exist is a sentence, not a crash.

    This matters more than it looks. A tool that raises ends the whole
    conversation; one that returns a sentence lets the agent tell the person
    what happened and carry on.
    """
    result = get_application_details.invoke("99999")

    assert isinstance(result, str)
    assert "not found" in result.lower() or "error" in result.lower()


def test_api_unavailable_handled(monkeypatch):
    """
    TC-01-P3-EXEC-06: with the API pointed somewhere dead, the tool still answers.

    The reload here is the trainer's own technique, and it caught a real bug
    while this was being built: the HTTP client is shared with Phases 4 and 5,
    and reloading the tools module does not re-execute the client module, so an
    address captured at import time would have survived the patch and the tools
    would have kept calling the old server. The client now reads the address per
    call for exactly this reason.
    """
    from agent import tools

    monkeypatch.setenv("API_BASE_URL", "http://localhost:9999/api/v1")
    importlib.reload(tools)

    result = tools.get_application_details.invoke("1")

    assert isinstance(result, str)
    assert any(word in result.lower() for word in ["unavailable", "error", "connection"])

    # Put the module back the way the rest of the suite expects it.
    monkeypatch.undo()
    importlib.reload(tools)
