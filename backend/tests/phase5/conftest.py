"""
Shared setup for the Phase 5 tests. Same shape as Phase 3 and 4's conftest.
"""

import os
import subprocess
import sys
import time

import pytest
import requests

os.environ.setdefault("OTEL_EXPORTER", "none")

HEALTH = "http://localhost:8000/health"


def _api_answers(timeout: float = 1.0) -> bool:
    try:
        requests.get(HEALTH, timeout=timeout)
        return True
    except requests.exceptions.RequestException:
        return False


@pytest.fixture(scope="session")
def running_api():
    """The Phase 1 API, running — started here if it isn't already."""
    if _api_answers():
        yield
        return

    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        env={**os.environ, "OTEL_EXPORTER": "none"},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 20
    while time.time() < deadline:
        if _api_answers():
            break
        time.sleep(0.5)
    else:
        process.terminate()
        pytest.fail("The Phase 1 API did not start within 20 seconds")

    yield

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture
def sample_application_id(running_api):
    """
    A real application id these tests can evaluate — created fresh with a
    complete personal-loan document set, rather than assuming "application 1"
    exists with the shape a given test needs. The trainer's own spec hardcodes
    "1" throughout; this is the same adaptation test_mcp_server.py and
    test_integration.py made in Phase 4, for the same reason (T-06 fixes
    module paths, not row ids in a database whose contents can change).
    """
    from app.services.loan_api_client import api_get, api_post, service_token
    import requests as _requests

    ok, data = api_get("/applicants", params={"limit": 1})
    if ok and data.get("items"):
        applicant_id = data["items"][0]["id"]
    else:
        token = service_token()
        resp = _requests.post(
            "http://localhost:8000/api/v1/applicants",
            json={"name": "Phase 5 Test Applicant", "email": "phase5.test@example.com",
                  "phone": "9991112222", "credit_score": 740,
                  "annual_income": 800000.0, "employment_status": "salaried"},
            headers={"Authorization": f"Bearer {token}"}, timeout=8,
        )
        resp.raise_for_status()
        applicant_id = resp.json()["id"]

    ok, application = api_post("/applications", body={
        "applicant_id": applicant_id, "loan_type": "personal",
        "amount_requested": 200000.0, "tenure_months": 24,
        "purpose": "Phase 5 underwriting fixture",
    })
    assert ok, application
    app_id = application["id"]

    for doc_type in ("id_proof", "income_proof", "bank_statement"):
        api_post(f"/applications/{app_id}/documents", body={
            "doc_type": doc_type, "file_name": f"{doc_type}.pdf",
        })

    return str(app_id)
