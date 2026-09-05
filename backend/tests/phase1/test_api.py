"""
Phase 1 API integration tests. TC-01-P1-API-01 to API-08, from the trainer's
phase1-test-spec.md. Function names and payloads are the trainer's.
"""


def test_post_application_success(client, auth_token, test_applicant):
    """TC-01-P1-API-01: POST /applications returns 201."""
    response = client.post("/api/v1/applications", json={
        "applicant_id": test_applicant["id"],
        "loan_type": "personal",
        "amount_requested": 100000.0,
        "tenure_months": 24,
        "purpose": "Home renovation"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["status"] == "submitted"
    assert data["loan_type"] == "personal"
    assert data["amount_requested"] == 100000.0


def test_post_application_missing_fields(client, auth_token, test_applicant):
    """TC-01-P1-API-02: POST /applications with missing fields returns 422."""
    response = client.post("/api/v1/applications", json={
        "applicant_id": test_applicant["id"],
        # Missing: loan_type, amount_requested, tenure_months, purpose
    }, headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 422
    errors = response.json()["detail"]
    field_names = [e["loc"][-1] for e in errors]
    assert "loan_type" in field_names


def test_get_application_by_id(client, auth_token, test_applicant):
    """TC-01-P1-API-03: GET /applications/{id} returns full details with nested history."""
    create_resp = client.post("/api/v1/applications", json={
        "applicant_id": test_applicant["id"],
        "loan_type": "home", "amount_requested": 2000000.0,
        "tenure_months": 120, "purpose": "Buy home"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    app_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/applications/{app_id}",
                          headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == app_id
    assert "status_history" in data
    assert len(data["status_history"]) >= 1
    assert data["status_history"][0]["new_status"] == "submitted"


def test_get_application_not_found(client, auth_token):
    """TC-01-P1-API-04: GET /applications/{id} for a missing id returns 404."""
    response = client.get("/api/v1/applications/99999",
                          headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 404
    assert "detail" in response.json()


def test_patch_status_valid_transition(client, auth_token, test_applicant):
    """TC-01-P1-API-05: PATCH /status with a valid transition returns 200."""
    create = client.post("/api/v1/applications", json={
        "applicant_id": test_applicant["id"], "loan_type": "auto",
        "amount_requested": 500000.0, "tenure_months": 48, "purpose": "Car"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    app_id = create.json()["id"]

    response = client.patch(f"/api/v1/applications/{app_id}/status", json={
        "new_status": "under_review", "remarks": "Documents look good, starting review"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 200

    # Verify status changed
    get_resp = client.get(f"/api/v1/applications/{app_id}",
                          headers={"Authorization": f"Bearer {auth_token}"})
    assert get_resp.json()["status"] == "under_review"


def test_patch_status_unauthorized(client):
    """TC-01-P1-API-06: PATCH /status without a token returns 401."""
    # No auth header
    response = client.patch("/api/v1/applications/1/status", json={
        "new_status": "under_review", "remarks": "test"
    })
    assert response.status_code == 401


def test_list_applications_with_filters(client, auth_token, test_applicant):
    """TC-01-P1-API-07: GET /applications with filters returns only matching rows."""
    # Create 2 submitted applications
    for i in range(2):
        client.post("/api/v1/applications", json={
            "applicant_id": test_applicant["id"], "loan_type": "personal",
            "amount_requested": 50000.0, "tenure_months": 12,
            "purpose": f"Purpose {i}"
        }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/api/v1/applications?status=submitted",
                          headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 200
    data = response.json()
    items = data.get("items", data if isinstance(data, list) else [])
    assert all(item["status"] == "submitted" for item in items)
    assert len(items) >= 2


def test_get_dashboard_summary(client, auth_token, test_applicant):
    """TC-01-P1-API-08: GET /dashboard/summary returns the counts."""
    client.post("/api/v1/applications", json={
        "applicant_id": test_applicant["id"], "loan_type": "personal",
        "amount_requested": 100000.0, "tenure_months": 12, "purpose": "Test"
    }, headers={"Authorization": f"Bearer {auth_token}"})

    response = client.get("/api/v1/dashboard/summary",
                          headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 200
    data = response.json()
    assert "total_applications" in data
    assert data["total_applications"] >= 1
    assert "by_status" in data
    assert "by_loan_type" in data
    assert isinstance(data["by_status"], dict)
