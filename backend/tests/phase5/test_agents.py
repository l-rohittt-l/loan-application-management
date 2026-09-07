"""
Phase 5 individual-agent tests: TC-01-P5-AGENT-01 to 08.

Taken from the trainer's phase5-test-spec.md. AGENT-01 and AGENT-02 use
`sample_application_id` / a fresh non-existent id instead of a hardcoded
"1" / "99999" for AGENT-01 — same adaptation as the rest of this run's
Phase 4 and 5 tests (T-06 fixes module paths, not row ids in a database
whose contents can change). AGENT-03 through AGENT-08 use mock state, exactly
as the trainer's own notes for this phase say they should, and need no
adaptation at all.
"""


def test_data_collector_fetches_applicant(running_api, sample_application_id):
    """TC-01-P5-AGENT-01."""
    from multi_agent.agents.data_collector import data_collector

    initial_state = {
        "application_id": sample_application_id,
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "",
        "messages": [], "current_agent": "", "errors": [],
    }

    result = data_collector(initial_state)

    if not result.get("errors"):
        assert result["applicant_data"] != {}
        assert result["application_data"] != {}
        assert result["current_agent"] == "data_collector"


def test_data_collector_handles_missing_app(running_api):
    """TC-01-P5-AGENT-02."""
    from multi_agent.agents.data_collector import data_collector

    state = {
        "application_id": "99999",
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    result = data_collector(state)

    assert len(result.get("errors", [])) > 0
    assert "99999" in result["errors"][0] or "not found" in result["errors"][0].lower()


def test_risk_assessor_calculates_dti():
    """TC-01-P5-AGENT-03."""
    from multi_agent.agents.risk_assessor import risk_assessor

    state = {
        "application_id": "1",
        "applicant_data": {
            "name": "Test", "annual_income": 600000,
            "credit_score": 720, "employment_status": "salaried",
        },
        "application_data": {
            "loan_type": "personal", "amount_requested": 100000, "tenure_months": 24,
        },
        "documents": [], "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    result = risk_assessor(state)

    assert result["risk_assessment"] != {}
    assert "overall_risk_score" in result["risk_assessment"]
    assert 0 <= result["risk_assessment"]["overall_risk_score"] <= 100
    assert result["risk_assessment"]["credit_risk_level"] in ["low", "medium", "high"]


def test_risk_assessor_flags_high_risk():
    """TC-01-P5-AGENT-04."""
    from multi_agent.agents.risk_assessor import risk_assessor

    state = {
        "application_id": "1",
        "applicant_data": {
            "name": "High Risk", "annual_income": 200000,
            "credit_score": 580, "employment_status": "self_employed",
        },
        "application_data": {
            "loan_type": "personal", "amount_requested": 500000, "tenure_months": 12,
        },
        "documents": [], "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    result = risk_assessor(state)

    assert result["risk_assessment"]["credit_risk_level"] in ["medium", "high"]
    assert result["risk_assessment"]["overall_risk_score"] <= 70


def test_compliance_checker_validates_docs():
    """TC-01-P5-AGENT-05."""
    from multi_agent.agents.compliance_checker import compliance_checker

    state = {
        "application_id": "1",
        "applicant_data": {"credit_score": 720},
        "application_data": {"loan_type": "personal", "amount_requested": 100000},
        "documents": [
            {"doc_type": "id_proof", "verified": True},
            {"doc_type": "income_proof", "verified": False},
            {"doc_type": "bank_statement", "verified": False},
        ],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    result = compliance_checker(state)

    assert result["compliance_check"]["documents_complete"] is True
    assert result["compliance_check"]["amount_within_limit"] is True
    assert result["compliance_check"]["compliance_passed"] is True
    assert result["compliance_check"]["missing_documents"] == []


def test_compliance_checker_flags_missing_docs():
    """TC-01-P5-AGENT-06."""
    from multi_agent.agents.compliance_checker import compliance_checker

    state = {
        "application_id": "1",
        "applicant_data": {"credit_score": 720},
        "application_data": {"loan_type": "home", "amount_requested": 2000000},
        "documents": [{"doc_type": "id_proof"}],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    result = compliance_checker(state)

    assert result["compliance_check"]["documents_complete"] is False
    assert len(result["compliance_check"]["missing_documents"]) >= 3
    assert "property_docs" in result["compliance_check"]["missing_documents"]
    assert result["compliance_check"]["compliance_passed"] is False


def test_decision_maker_approves():
    """TC-01-P5-AGENT-07."""
    from multi_agent.agents.decision_maker import decision_maker

    state = {
        "application_id": "1",
        "applicant_data": {"name": "Good Applicant", "credit_score": 780},
        "application_data": {"loan_type": "personal", "amount_requested": 100000, "tenure_months": 24},
        "documents": [],
        "risk_assessment": {
            "overall_risk_score": 80.0, "emi_affordability": "yes",
            "credit_risk_level": "low", "employment_risk": "low",
            "risk_summary": "Low risk applicant",
        },
        "compliance_check": {
            "compliance_passed": True, "documents_complete": True,
            "missing_documents": [], "kyc_verified": True,
            "amount_within_limit": True, "age_eligible": True,
            "compliance_notes": "All checks passed",
        },
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    result = decision_maker(state)

    assert result["final_decision"] in ["APPROVE", "REQUEST_MORE_INFO"]
    assert len(result["reasoning"]) > 10
    assert result["current_agent"] == "decision_maker"


def test_decision_maker_rejects():
    """TC-01-P5-AGENT-08."""
    from multi_agent.agents.decision_maker import decision_maker

    state = {
        "application_id": "1",
        "applicant_data": {"credit_score": 580},
        "application_data": {"loan_type": "personal", "amount_requested": 500000},
        "documents": [],
        "risk_assessment": {
            "overall_risk_score": 30.0, "emi_affordability": "no",
            "credit_risk_level": "high", "employment_risk": "high",
            "risk_summary": "Very high risk",
        },
        "compliance_check": {
            "compliance_passed": False, "documents_complete": False,
            "missing_documents": ["income_proof", "bank_statement"],
            "kyc_verified": False, "amount_within_limit": True,
            "age_eligible": True, "compliance_notes": "Missing 2 documents",
        },
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    }

    result = decision_maker(state)

    assert result["final_decision"] in ["REJECT", "REQUEST_MORE_INFO"]
    assert result["final_decision"] != "APPROVE"
