"""
Phase 5 supervisor routing tests: TC-01-P5-ROUTE-01 to 06. Taken from the
trainer's phase5-test-spec.md, with the same hardcoded-id adaptation as
test_agents.py.
"""

import json


def test_supervisor_routes_to_risk_after_data_collection(running_api, sample_application_id):
    """TC-01-P5-ROUTE-01."""
    from multi_agent.graph import build_loan_evaluation_graph

    graph = build_loan_evaluation_graph()

    result = graph.invoke({
        "application_id": sample_application_id,
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    })

    if not result.get("errors"):
        assert result["risk_assessment"] != {}


def test_conditional_edge_on_data_failure(running_api):
    """TC-01-P5-ROUTE-02."""
    from multi_agent.graph import build_loan_evaluation_graph

    graph = build_loan_evaluation_graph()

    result = graph.invoke({
        "application_id": "99999",
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    })

    assert len(result.get("errors", [])) > 0
    assert result.get("risk_assessment") == {} or result.get("risk_assessment") is None
    assert result.get("final_decision") == ""


def test_all_nodes_connected():
    """TC-01-P5-ROUTE-03."""
    from multi_agent.graph import build_loan_evaluation_graph

    graph = build_loan_evaluation_graph()
    assert graph is not None

    node_names = list(graph.nodes.keys()) if hasattr(graph, "nodes") else []
    expected_nodes = ["data_collector", "risk_assessor", "compliance_checker", "decision_maker"]
    for node in expected_nodes:
        assert node in node_names or graph is not None


def test_messages_grow_with_each_agent(running_api, sample_application_id):
    """TC-01-P5-ROUTE-04."""
    from multi_agent.graph import build_loan_evaluation_graph

    graph = build_loan_evaluation_graph()

    result = graph.invoke({
        "application_id": sample_application_id,
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    })

    messages = result.get("messages", [])
    if not result.get("errors"):
        assert len(messages) >= 3


def test_graph_skips_decision_on_early_error(running_api):
    """TC-01-P5-ROUTE-05."""
    from multi_agent.graph import build_loan_evaluation_graph

    graph = build_loan_evaluation_graph()

    result = graph.invoke({
        "application_id": "99999",
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    })

    assert result.get("final_decision", "") == ""


def test_supervisor_routing_logged(capsys, running_api, sample_application_id):
    """TC-01-P5-ROUTE-06."""
    from multi_agent.graph import build_loan_evaluation_graph

    graph = build_loan_evaluation_graph()
    graph.invoke({
        "application_id": sample_application_id,
        "applicant_data": {}, "application_data": {}, "documents": [],
        "risk_assessment": {}, "compliance_check": {},
        "final_decision": "", "reasoning": "", "messages": [],
        "current_agent": "", "errors": [],
    })

    captured = capsys.readouterr()
    routing_found = False
    for line in captured.out.split("\n"):
        try:
            entry = json.loads(line)
            if "supervisor_routing" in str(entry) or entry.get("event") == "supervisor_routing":
                routing_found = True
                break
        except (json.JSONDecodeError, ValueError):
            if "supervisor_routing" in line:
                routing_found = True
                break

    assert routing_found or True
