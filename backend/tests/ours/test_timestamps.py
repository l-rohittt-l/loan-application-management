"""
Our own tests, kept apart from the trainer's twenty so that suite stays exactly
as the spec writes it.

These cover the timezone bug Rohit spotted on 2026-09-06: every date and time in
the app showed 5 hours 30 minutes early.

What went wrong: SQLite records the time in UTC and hands it back as a plain
date and time with nothing marking it as UTC. The API passed that straight out,
so a browser read "2026-09-05T20:13:55" as the reader's own local time. In India
that is the wrong day, in the evening instead of the small hours.

The fix: end every outgoing time with "Z", which says "this is UTC". The browser
then converts it to the reader's real local time.
"""

from datetime import datetime, timezone


def _submit_one(client, auth_token, test_applicant):
    return client.post("/api/v1/applications", json={
        "applicant_id": test_applicant["id"], "loan_type": "personal",
        "amount_requested": 100000.0, "tenure_months": 24, "purpose": "Timestamp check",
    }, headers={"Authorization": f"Bearer {auth_token}"})


def test_times_sent_to_the_browser_say_they_are_utc(client, auth_token, test_applicant):
    """Every time in an application response ends with Z, so a browser reads it right."""
    application_id = _submit_one(client, auth_token, test_applicant).json()["id"]
    body = client.get(f"/api/v1/applications/{application_id}",
                      headers={"Authorization": f"Bearer {auth_token}"}).json()

    assert body["submitted_at"].endswith("Z"), body["submitted_at"]
    assert body["updated_at"].endswith("Z")
    assert body["applicant"]["created_at"].endswith("Z")
    assert body["status_history"][0]["changed_at"].endswith("Z")


def test_the_time_recorded_is_actually_now(client, auth_token, test_applicant):
    """
    Guards against a stale or made-up clock: an application submitted this second
    must carry a timestamp within a minute of the real current time.
    """
    before = datetime.now(timezone.utc)
    body = _submit_one(client, auth_token, test_applicant).json()
    after = datetime.now(timezone.utc)

    submitted = datetime.fromisoformat(body["submitted_at"].replace("Z", "+00:00"))
    assert before.replace(microsecond=0) <= submitted <= after, (
        f"submitted_at {submitted} is not between {before} and {after}"
    )


def test_other_screens_send_utc_too(client, auth_token, test_applicant):
    """The list, the documents and the activity log all go through the same rule."""
    application_id = _submit_one(client, auth_token, test_applicant).json()["id"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    listed = client.get("/api/v1/applications", headers=headers).json()["items"][0]
    assert listed["submitted_at"].endswith("Z")

    client.post(f"/api/v1/applications/{application_id}/documents",
                json={"doc_type": "id_proof", "file_name": "aadhaar.pdf"}, headers=headers)
    document = client.get(f"/api/v1/applications/{application_id}/documents",
                          headers=headers).json()["items"][0]
    assert document["uploaded_at"].endswith("Z")

    me = client.get("/api/v1/auth/me", headers=headers).json()
    assert me["created_at"].endswith("Z")
