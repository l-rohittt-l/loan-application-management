"""
Agent 1: fetches everything the other three agents need, so none of them make
their own API calls. One place to change if the API address or the auth
scheme ever changes.

Uses the same shared `app.services.loan_api_client` Phase 3 and 4 use — a
fresh token every call rather than a static one from `.env`, and a plain
result rather than a raised exception on failure (`AI-BUILD-LOG.md`).
"""

import time

import structlog
from opentelemetry import trace

from app.services.loan_api_client import api_get
from multi_agent.state import LoanProcessingState

logger = structlog.get_logger()
tracer = trace.get_tracer("data-collector")


def data_collector(state: LoanProcessingState) -> LoanProcessingState:
    """Fetch the application, its applicant, and its documents."""
    app_id_raw = state["application_id"]
    log = logger.bind(poc_id="POC-01", phase=5, agent="data_collector", application_id=app_id_raw)
    started = time.perf_counter()

    with tracer.start_as_current_span("agent.data_collector.activate") as span:
        span.set_attribute("agent.name", "data_collector")
        span.set_attribute("agent.application_id", app_id_raw)

        try:
            app_id = int(app_id_raw)
        except (TypeError, ValueError):
            log.error("invalid_application_id", operation="reasoning")
            return {**state, "errors": [f"'{app_id_raw}' is not a valid application id"],
                    "current_agent": "data_collector"}

        ok, app_data = api_get(f"/applications/{app_id}")
        if not ok:
            error = (f"Application {app_id} not found" if app_data == "not found"
                      else f"Failed to fetch application {app_id}: {app_data}")
            log.error("application_fetch_failed", operation="reasoning", detail=error)
            span.set_attribute("agent.success", False)
            return {**state, "errors": [error], "current_agent": "data_collector"}

        # The application response already embeds the full applicant record
        # (see app/schemas/application.py), so there is no need for a second
        # HTTP round trip in the common case. Only fall back to a fresh
        # lookup if that embedded record is somehow missing.
        applicant_data = app_data.get("applicant") or {}
        if not applicant_data:
            applicant_id = app_data.get("applicant_id")
            if applicant_id:
                ok2, data2 = api_get(f"/applicants/{applicant_id}")
                applicant_data = data2 if ok2 else {}
                if not ok2:
                    log.warning("applicant_fetch_failed", operation="reasoning", applicant_id=applicant_id)

        documents = app_data.get("documents", [])
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        span.set_attribute("agent.output_keys_populated", "applicant_data,application_data,documents")
        span.set_attribute("agent.duration_ms", duration_ms)
        span.set_attribute("agent.success", True)

        log.info("data_collection_complete", operation="reasoning",
                  documents_count=len(documents), duration_ms=duration_ms, status="success")

        return {
            **state,
            "application_data": app_data,
            "applicant_data": applicant_data,
            "documents": documents,
            "current_agent": "data_collector",
            "messages": state.get("messages", []) + [{
                "agent": "data_collector",
                "message": (f"Collected data for application {app_id}: {len(documents)} "
                            f"document(s), applicant credit score: "
                            f"{applicant_data.get('credit_score', 'unknown')}"),
            }],
        }
