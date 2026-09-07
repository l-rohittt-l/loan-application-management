"""
Phase 5 state schema tests: TC-01-P5-STATE-01 to 04. Taken verbatim from the
trainer's phase5-test-spec.md — none of these need adapting.
"""


def test_state_schema_valid_typeddict():
    """TC-01-P5-STATE-01."""
    from multi_agent.state import LoanProcessingState

    assert hasattr(LoanProcessingState, "__annotations__")

    required_keys = [
        "application_id", "applicant_data", "application_data",
        "documents", "risk_assessment", "compliance_check",
        "final_decision", "reasoning", "messages", "current_agent", "errors",
    ]
    for key in required_keys:
        assert key in LoanProcessingState.__annotations__, f"Missing key: {key}"


def test_state_initializes_correctly():
    """TC-01-P5-STATE-02."""
    initial_state = {
        "application_id": "1",
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "",
        "messages": [], "current_agent": "", "errors": [],
    }

    assert initial_state["application_id"] == "1"
    assert initial_state["documents"] == []
    assert initial_state["errors"] == []
    assert initial_state["final_decision"] == ""


def test_state_updated_by_agent():
    """TC-01-P5-STATE-03."""
    initial_state = {
        "application_id": "test-1",
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "",
        "messages": [], "current_agent": "", "errors": [],
    }

    updated = {
        **initial_state,
        "current_agent": "data_collector",
        "applicant_data": {"name": "Test", "credit_score": 720},
        "messages": [{"agent": "data_collector", "message": "Collected"}],
    }

    assert updated["current_agent"] == "data_collector"
    assert updated["applicant_data"]["credit_score"] == 720
    assert len(updated["messages"]) == 1
    assert initial_state["current_agent"] == ""


def test_state_persists_across_nodes():
    """TC-01-P5-STATE-04: state accumulated by an earlier agent is visible to a later one."""
    state = {
        "application_id": "1",
        "applicant_data": {"name": "Priya", "credit_score": 720},
        "application_data": {"loan_type": "personal", "amount_requested": 100000},
        "documents": [{"doc_type": "id_proof"}],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "",
        "messages": [], "current_agent": "data_collector", "errors": [],
    }

    from multi_agent.agents.compliance_checker import compliance_checker

    result = compliance_checker(state)

    assert result["compliance_check"] != {}
    assert result["applicant_data"]["credit_score"] == 720
