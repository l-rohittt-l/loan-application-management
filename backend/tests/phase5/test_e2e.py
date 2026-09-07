"""
Phase 5 end-to-end workflow tests: TC-01-P5-E2E-01 to 07.

Taken from the trainer's phase5-test-spec.md, with the same hardcoded-id
adaptation as the rest of this phase's tests, and the same retry-instead-of-
fixed-sleep fix for the LangSmith trace test that Phase 3's T-62 and Phase
4's OBS tests already needed — a brand-new LangSmith project can take longer
than a few seconds to become queryable the very first time it is written to.
"""

import time

import pytest

from app.config import settings


def _wait_for_runs(project_name: str, api_key: str, attempts: int = 12, gap: float = 4.0):
    from langsmith import Client
    from langsmith.utils import LangSmithNotFoundError

    client = Client(api_key=api_key)
    for _ in range(attempts):
        time.sleep(gap)
        try:
            runs = list(client.list_runs(project_name=project_name, limit=10))
        except LangSmithNotFoundError:
            continue
        if runs:
            return runs
    return []


def test_full_graph_executes_for_valid_application(running_api, sample_application_id):
    """TC-01-P5-E2E-01."""
    from multi_agent.graph import evaluate_loan_application

    result = evaluate_loan_application(sample_application_id)

    assert result is not None
    assert isinstance(result, dict)
    assert result.get("final_decision") != "" or len(result.get("errors", [])) > 0


def test_final_decision_in_state(running_api, sample_application_id):
    """TC-01-P5-E2E-02."""
    from multi_agent.graph import evaluate_loan_application

    result = evaluate_loan_application(sample_application_id)

    if not result.get("errors"):
        assert result.get("final_decision") in ["APPROVE", "REJECT", "REQUEST_MORE_INFO"]


def test_reasoning_field_populated(running_api, sample_application_id):
    """TC-01-P5-E2E-03."""
    from multi_agent.graph import evaluate_loan_application

    result = evaluate_loan_application(sample_application_id)

    if not result.get("errors") and result.get("final_decision"):
        assert len(result.get("reasoning", "")) > 20


def test_all_agents_traced_in_langsmith(running_api, sample_application_id):
    """TC-01-P5-E2E-04."""
    from multi_agent.graph import LANGSMITH_PROJECT, evaluate_loan_application

    if not settings.langchain_api_key:
        pytest.skip("LANGCHAIN_API_KEY is not set")

    evaluate_loan_application(sample_application_id)

    runs = _wait_for_runs(LANGSMITH_PROJECT, settings.langchain_api_key)
    assert len(runs) > 0, f"No traces in {LANGSMITH_PROJECT}"


def test_full_graph_with_low_credit_score():
    """TC-01-P5-E2E-05: mocked data, the high-risk path."""
    from multi_agent.agents.compliance_checker import compliance_checker
    from multi_agent.agents.decision_maker import decision_maker
    from multi_agent.agents.risk_assessor import risk_assessor

    state = {
        "application_id": "mock-1",
        "applicant_data": {"credit_score": 550, "annual_income": 180000, "employment_status": "unemployed"},
        "application_data": {"loan_type": "personal", "amount_requested": 300000, "tenure_months": 12},
        "documents": [{"doc_type": "id_proof"}],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    state = risk_assessor(state)
    state = compliance_checker(state)
    state = decision_maker(state)

    assert state["final_decision"] in ["REJECT", "REQUEST_MORE_INFO"]


def test_graph_with_all_documents():
    """TC-01-P5-E2E-06: mocked data, a compliant home loan application."""
    from multi_agent.agents.compliance_checker import compliance_checker
    from multi_agent.agents.decision_maker import decision_maker

    state = {
        "application_id": "mock-2",
        "applicant_data": {"credit_score": 760, "annual_income": 900000},
        "application_data": {"loan_type": "home", "amount_requested": 3000000, "tenure_months": 240},
        "documents": [
            {"doc_type": "id_proof", "verified": True},
            {"doc_type": "income_proof"}, {"doc_type": "bank_statement"},
            {"doc_type": "property_docs"}, {"doc_type": "employment_letter"},
        ],
        "risk_assessment": {
            "overall_risk_score": 75.0, "emi_affordability": "yes",
            "credit_risk_level": "low", "employment_risk": "low",
            "risk_summary": "Good candidate",
        },
        "compliance_check": {}, "final_decision": "", "reasoning": "",
        "messages": [], "current_agent": "", "errors": [],
    }

    state = compliance_checker(state)
    state = decision_maker(state)

    assert state["compliance_check"]["documents_complete"] is True
    assert state["compliance_check"]["compliance_passed"] is True
    assert state["final_decision"] in ["APPROVE", "REQUEST_MORE_INFO"]


def test_graph_output_contains_agent_messages(running_api, sample_application_id):
    """TC-01-P5-E2E-07."""
    from multi_agent.graph import evaluate_loan_application

    result = evaluate_loan_application(sample_application_id)

    messages = result.get("messages", [])
    if not result.get("errors"):
        assert len(messages) >= 1
        for msg in messages:
            assert "agent" in msg
            assert "message" in msg
