"""
Piece 19: every application must carry the server's own eligibility
assessment, taken at the moment of submission, not the browser's copy.
"""


def _make_applicant(client, auth_token, **overrides):
    body = {
        "name": "Priya Sharma", "email": "priya@example.com",
        "phone": "9876543210", "credit_score": 720,
        "annual_income": 600000.0, "employment_status": "salaried",
    }
    body.update(overrides)
    response = client.post("/api/v1/applicants", json=body,
                            headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201, response.text
    return response.json()


def test_eligible_application_stores_a_passing_summary(client, auth_token):
    applicant = _make_applicant(client, auth_token)
    response = client.post("/api/v1/applications", json={
        "applicant_id": applicant["id"], "loan_type": "personal",
        "amount_requested": 200000.0, "tenure_months": 24, "purpose": "Wedding",
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["eligibility_passed"] is True
    assert body["eligibility_checked_at"] is not None
    assert "ELIGIBLE" in body["eligibility_summary"]
    assert "PASS" in body["eligibility_summary"]
    assert "Submitted anyway" not in body["eligibility_summary"]


def test_ineligible_application_still_returns_201_and_records_why(client, auth_token):
    """
    A big home loan on a modest income fails affordability. The plan (Piece
    19) says this must never block the 201 the trainer's tests rely on
    (API-01, API-03) — it only has to be recorded honestly.
    """
    applicant = _make_applicant(client, auth_token, email="low.income@example.com",
                                 annual_income=400000.0)
    response = client.post("/api/v1/applications", json={
        "applicant_id": applicant["id"], "loan_type": "home",
        "amount_requested": 4000000.0, "tenure_months": 120, "purpose": "House purchase",
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["eligibility_passed"] is False
    assert "NOT ELIGIBLE" in body["eligibility_summary"]
    assert "FAIL" in body["eligibility_summary"]
    assert "Submitted anyway by" in body["eligibility_summary"]


def test_check_eligibility_endpoint_reports_every_rule_not_just_failures(client, auth_token):
    applicant = _make_applicant(client, auth_token, email="check@example.com")
    response = client.post("/api/v1/applications/check-eligibility", json={
        "applicant_id": applicant["id"], "loan_type": "personal",
        "amount_requested": 200000.0, "tenure_months": 24,
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["eligible"] is True
    assert len(body["rule_checks"]) >= 6
    assert all(row["passed"] for row in body["rule_checks"])
