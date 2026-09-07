"""
The MCP server: the same six loan-management operations the trainer's Phase 4
plan names, exposed as MCP tools rather than as five read-only LangChain tools
(Phase 3) or a REST API (Phase 1).

MCP (Model Context Protocol) is Anthropic's open standard for how an AI
application discovers and calls tools. Wrapping the same operations in
`@mcp.tool()` rather than `@tool` from `langchain_core` means any
MCP-compatible client — not just this project's own chat interface — can
plug into the same six tools.

Every tool below calls the Phase 1 REST API through the same shared
`app.services.loan_api_client` Phase 3's tools and Phase 5's data collector
also use, for the two reasons written up there and in `AI-BUILD-LOG.md`:

  * the trainer's own skeleton reads a static `API_JWT_TOKEN` from `.env`,
    which expires 24 hours after issue and would go stale mid-session —
    this mints a fresh token on every call instead;
  * the trainer's own skeleton calls `resp.raise_for_status()`, which raises
    on any 4xx/5xx that isn't a 404 and would end an MCP tool call with a
    stack trace instead of a message the assistant can read out.

Every tool returns a plain `dict`, never raises, and puts `"error"` in the
dict on any failure — that is what `TC-01-P4-MCP-08` checks for, and it is
also simply a better shape for an MCP client to receive than an exception.
"""

from __future__ import annotations

import time

import structlog
from fastmcp import FastMCP

from app.services.loan_api_client import api_get, api_patch, api_post
from app.utils.otel_config import get_tracer

mcp = FastMCP("Loan Application Management MCP Server")
logger = structlog.get_logger()


def _wrap(ok: bool, data) -> dict:
    """
    Turn the shared client's `(ok, data)` into the dict shape every tool here
    returns. A 404 becomes `{"error": "not_found", ...}`; any other failure
    becomes `{"error": "api_error", ...}` with the server's own message.
    """
    if ok:
        return data if isinstance(data, dict) else {"result": data}
    if data == "not found":
        return {"error": "not_found", "detail": "The requested record was not found."}
    return {"error": "api_error", "detail": data}


def _tool_span(tool_name: str, attributes: dict, fn):
    """The `mcp.tool_invoke` span and structured log every tool call needs (Phase 4's observability table)."""
    tracer = get_tracer()
    started = time.perf_counter()
    with tracer.start_as_current_span("mcp.tool_invoke") as span:
        span.set_attribute("mcp.tool_name", tool_name)
        for key, value in attributes.items():
            span.set_attribute(f"mcp.input.{key}", value)
        result = fn()
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        success = "error" not in result
        span.set_attribute("mcp.success", success)
        logger.info("mcp_tool_called", operation="mcp_tool_call", tool=tool_name,
                    duration_ms=duration_ms, success=success,
                    poc_id="POC-01", phase=4)
        if not success:
            logger.warning("mcp_tool_error", operation="mcp_tool_call", tool=tool_name,
                           error=result.get("detail"), poc_id="POC-01", phase=4)
        return result


@mcp.tool()
def submit_loan_application(
    applicant_id: int,
    loan_type: str,
    amount_requested: float,
    tenure_months: int,
    purpose: str,
) -> dict:
    """Submit a new loan application for an existing applicant.
    loan_type must be one of: personal, home, auto.
    amount_requested must be between 10000 and 10000000.
    tenure_months must be between 6 and 360.
    Returns the created application with its assigned ID, or an error dict."""
    def run():
        ok, data = api_post("/applications", body={
            "applicant_id": applicant_id, "loan_type": loan_type,
            "amount_requested": amount_requested, "tenure_months": tenure_months,
            "purpose": purpose,
        })
        return _wrap(ok, data)

    return _tool_span("submit_loan_application", {"applicant_id": applicant_id, "loan_type": loan_type}, run)


@mcp.tool()
def get_application_details(application_id: int) -> dict:
    """Retrieve full details of a specific loan application including status history.
    Returns application fields, applicant info, documents, and complete status history,
    or an error dict if the application does not exist."""
    def run():
        ok, data = api_get(f"/applications/{application_id}")
        return _wrap(ok, data)

    return _tool_span("get_application_details", {"application_id": application_id}, run)


@mcp.tool()
def update_application_status(
    application_id: int,
    new_status: str,
    remarks: str,
) -> dict:
    """Update the status of a loan application.
    new_status must be one of: under_review, approved, rejected, disbursed.
    remarks is required and will be recorded in the audit trail.
    Returns the updated application, or an error dict if the move is not allowed."""
    def run():
        ok, data = api_patch(f"/applications/{application_id}/status", body={
            "new_status": new_status, "remarks": remarks,
        })
        return _wrap(ok, data)

    return _tool_span("update_application_status",
                       {"application_id": application_id, "new_status": new_status}, run)


@mcp.tool()
def list_applications_by_filter(
    status: str = "",
    loan_type: str = "",
    page: int = 1,
    limit: int = 10,
) -> dict:
    """List loan applications with optional filters.
    status options: submitted, under_review, approved, rejected, disbursed.
    loan_type options: personal, home, auto.
    Returns a paginated list with total count."""
    def run():
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if loan_type:
            params["loan_type"] = loan_type
        ok, data = api_get("/applications", params=params)
        return _wrap(ok, data)

    return _tool_span("list_applications_by_filter", {"status": status, "loan_type": loan_type}, run)


@mcp.tool()
def get_dashboard_summary() -> dict:
    """Get the dashboard summary showing total applications by status and loan type.
    Returns total count, total amount requested, breakdown by status, and breakdown by loan type."""
    def run():
        ok, data = api_get("/dashboard/summary")
        return _wrap(ok, data)

    return _tool_span("get_dashboard_summary", {}, run)


@mcp.tool()
def upload_document_metadata(
    application_id: int,
    doc_type: str,
    file_name: str,
) -> dict:
    """Record that a document has been uploaded for a loan application.
    doc_type must be one of: id_proof, income_proof, bank_statement, property_docs, employment_letter.
    file_name is the name of the uploaded file.
    Returns the created document record, or an error dict."""
    def run():
        ok, data = api_post(f"/applications/{application_id}/documents", body={
            "doc_type": doc_type, "file_name": file_name,
        })
        return _wrap(ok, data)

    return _tool_span("upload_document_metadata",
                       {"application_id": application_id, "doc_type": doc_type}, run)


ALL_MCP_TOOLS = [
    submit_loan_application, get_application_details, update_application_status,
    list_applications_by_filter, get_dashboard_summary, upload_document_metadata,
]


if __name__ == "__main__":
    logger.info("mcp_server_starting", operation="mcp_server_starting",
                port=8080, tool_count=len(ALL_MCP_TOOLS), poc_id="POC-01", phase=4)
    # stdio is what a local MCP client (this project's own chat interface,
    # or any other MCP-compatible tool) talks to by default.
    mcp.run(transport="stdio")
