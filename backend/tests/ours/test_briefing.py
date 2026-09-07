"""
The Manager's Morning Briefing (D-13). Ours, not the trainer's.

The point of these tests is the part that must never be wrong: the numbers.
The narrative is written by an LLM and will read differently every time, so
what is asserted here is that the figures are computed correctly from the
database, that the role gate holds, and that the briefing still works when
the LLM does not.
"""

from datetime import datetime, timedelta, timezone


def _manager_token(client):
    """A branch manager login. Register creates a loan officer, so the role is set directly."""
    from app.models.user import User, UserRole
    from tests.conftest import TestingSessionLocal

    client.post("/api/v1/auth/register", json={
        "name": "Briefing Manager", "email": "briefing.manager@test.com", "password": "Test@1234",
    })
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "briefing.manager@test.com").first()
    user.role = UserRole.branch_manager
    db.commit()
    db.close()

    response = client.post("/api/v1/auth/login", json={
        "email": "briefing.manager@test.com", "password": "Test@1234",
    })
    return response.json()["access_token"]


def _make_application(client, token, *, amount=200000.0, loan_type="personal", email=None):
    applicant = client.post("/api/v1/applicants", json={
        "name": "Briefing Applicant", "email": email or "briefing.applicant@test.com",
        "phone": "9876543210", "credit_score": 720,
        "annual_income": 900000.0, "employment_status": "salaried",
    }, headers={"Authorization": f"Bearer {token}"}).json()

    return client.post("/api/v1/applications", json={
        "applicant_id": applicant["id"], "loan_type": loan_type,
        "amount_requested": amount, "tenure_months": 24, "purpose": "Briefing test",
    }, headers={"Authorization": f"Bearer {token}"}).json()


def test_briefing_is_manager_only(client, auth_token):
    """A loan officer gets 403 — this is a branch-wide view, same gate as the activity log."""
    response = client.get("/api/v1/briefing", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 403


def test_briefing_needs_a_login(client):
    """No token is 401, not 403 (T-01)."""
    response = client.get("/api/v1/briefing")
    assert response.status_code == 401


def test_briefing_counts_what_is_waiting(client):
    token = _manager_token(client)
    _make_application(client, token, amount=200000.0)

    response = client.get("/api/v1/briefing", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    body = response.json()

    numbers = body["headline_numbers"]
    assert numbers["open_applications"] == 1
    assert numbers["awaiting_decision"] == 1
    assert numbers["value_awaiting_decision"] == 200000.0
    assert numbers["approved_not_disbursed"] == 0
    assert len(body["narrative"]) > 20
    assert body["generated_at"].endswith("Z")   # T-39


def test_briefing_flags_an_application_that_has_waited_too_long(client):
    """An old submitted application shows up in needs_attention with its days counted."""
    from app.models.application import LoanApplication
    from tests.conftest import TestingSessionLocal

    token = _manager_token(client)
    created = _make_application(client, token)

    # Age it deliberately: SQLite stores naive UTC (T-39), so write naive UTC.
    db = TestingSessionLocal()
    row = db.query(LoanApplication).filter(LoanApplication.id == created["id"]).first()
    row.submitted_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=9)
    db.commit()
    db.close()

    body = client.get("/api/v1/briefing",
                      headers={"Authorization": f"Bearer {token}"}).json()

    assert body["headline_numbers"]["waiting_too_long"] == 1
    stuck = body["needs_attention"][0]
    assert stuck["id"] == created["id"]
    assert stuck["status"] == "submitted"
    assert stuck["days_waiting"] >= 8


def test_briefing_lists_missing_documents(client):
    """A home loan with no documents at all is held up by five of them."""
    token = _manager_token(client)
    created = _make_application(client, token, loan_type="home", amount=2000000.0)

    body = client.get("/api/v1/briefing",
                      headers={"Authorization": f"Bearer {token}"}).json()

    assert body["headline_numbers"]["missing_documents"] == 1
    row = body["missing_documents"][0]
    assert row["id"] == created["id"]
    assert "property_docs" in row["missing"]


def test_briefing_still_works_when_the_llm_is_unavailable(client, monkeypatch):
    """
    The narrative degrades to the plain facts rather than failing — and says
    so with written_by_ai=False, so nobody mistakes the fallback for the AI's
    own writing.
    """
    from app.services import briefing_service

    monkeypatch.setattr(briefing_service, "_narrative",
                        lambda facts: (briefing_service._fallback_narrative(facts), False))

    token = _manager_token(client)
    _make_application(client, token)

    body = client.get("/api/v1/briefing",
                      headers={"Authorization": f"Bearer {token}"}).json()

    assert body["written_by_ai"] is False
    assert len(body["narrative"]) > 20
    assert body["headline_numbers"]["awaiting_decision"] == 1


def test_briefing_on_an_empty_pipeline_says_so(client):
    """No applications at all must not produce an error or an invented concern."""
    token = _manager_token(client)

    body = client.get("/api/v1/briefing",
                      headers={"Authorization": f"Bearer {token}"}).json()

    assert body["headline_numbers"]["open_applications"] == 0
    assert body["needs_attention"] == []
    assert len(body["narrative"]) > 10
