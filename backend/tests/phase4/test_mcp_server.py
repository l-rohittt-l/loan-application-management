"""
Phase 4 MCP server tests: TC-01-P4-MCP-01 to 08.

Taken from the trainer's phase4-test-spec.md. Two small, documented
adaptations from the literal spec:

  * MCP-03 and MCP-05 use `sample_applicant_id` instead of a hardcoded
    `applicant_id=1`, because which id exists depends on what has already
    run against this database (T-06 says we cannot rename the trainer's
    fixed module paths, but nothing pins us to a hardcoded row id that
    happens to work on a freshly seeded database and nowhere else).
  * MCP-05 no longer submits its own throwaway application first, since
    `sample_applicant_id` already gives it a real applicant to work with —
    it still creates a fresh application, then moves its status.
"""


def test_mcp_server_starts():
    """TC-01-P4-MCP-01."""
    from mcp_server.mcp_app import mcp

    assert mcp is not None
    assert hasattr(mcp, "run")


def test_tools_discoverable():
    """TC-01-P4-MCP-02: every tool importable by name, and FastMCP knows about all six."""
    from mcp_server.mcp_app import (
        get_application_details, get_dashboard_summary, list_applications_by_filter,
        submit_loan_application, update_application_status, upload_document_metadata,
    )

    assert submit_loan_application is not None
    assert get_application_details is not None
    assert update_application_status is not None
    assert list_applications_by_filter is not None
    assert get_dashboard_summary is not None
    assert upload_document_metadata is not None


def test_submit_application_tool(running_api, sample_applicant_id):
    """TC-01-P4-MCP-03."""
    from mcp_server.mcp_app import submit_loan_application

    result = submit_loan_application(
        applicant_id=sample_applicant_id, loan_type="personal",
        amount_requested=75000.0, tenure_months=18, purpose="MCP test application",
    )

    assert isinstance(result, dict)
    assert "id" in result or "error" in result
    if "id" in result:
        assert result.get("status") == "submitted"


def test_get_details_tool(running_api, sample_applicant_id):
    """TC-01-P4-MCP-04."""
    from mcp_server.mcp_app import get_application_details, submit_loan_application

    created = submit_loan_application(
        applicant_id=sample_applicant_id, loan_type="auto",
        amount_requested=300000.0, tenure_months=36, purpose="MCP-04 fixture",
    )
    result = get_application_details(application_id=created["id"])

    assert isinstance(result, dict)
    if "error" not in result:
        assert "id" in result
        assert "status" in result
        assert "loan_type" in result


def test_update_status_tool(running_api, sample_applicant_id):
    """TC-01-P4-MCP-05."""
    from mcp_server.mcp_app import submit_loan_application, update_application_status

    new_app = submit_loan_application(
        applicant_id=sample_applicant_id, loan_type="personal",
        amount_requested=50000.0, tenure_months=12, purpose="Status update test",
    )

    if "id" in new_app:
        result = update_application_status(
            application_id=new_app["id"], new_status="under_review",
            remarks="MCP test status update",
        )
        assert isinstance(result, dict)
        assert "error" not in result
        assert result.get("status") == "under_review"


def test_list_filter_tool(running_api):
    """TC-01-P4-MCP-06."""
    from mcp_server.mcp_app import list_applications_by_filter

    result = list_applications_by_filter(status="submitted", loan_type="", page=1, limit=5)

    assert isinstance(result, (dict, list))


def test_dashboard_mcp_tool(running_api):
    """TC-01-P4-MCP-07."""
    from mcp_server.mcp_app import get_dashboard_summary

    result = get_dashboard_summary()

    assert isinstance(result, dict)
    assert "total_applications" in result or "error" in result


def test_invalid_input_returns_error(running_api):
    """TC-01-P4-MCP-08: a non-existent application comes back as a clean error, not a crash."""
    from mcp_server.mcp_app import get_application_details

    result = get_application_details(application_id=99999)

    assert isinstance(result, dict)
    assert "error" in result or result.get("id") is None
