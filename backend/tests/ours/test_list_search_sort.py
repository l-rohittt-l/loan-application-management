"""
Our own tests for the searching and sorting added to the applications list in
Piece 18. Kept out of tests/phase1/ so the trainer's twenty stay exactly as the
spec writes them.

The point of the last test in this file: searching and sorting were added
without changing what the endpoint already did. Calling the list with no
settings at all must return what it returned before — newest first — because
the trainer's TC-01-P1-API-07 takes every default.
"""

AUTH = "Authorization"


def _headers(token):
    return {AUTH: f"Bearer {token}"}


def _make_applicant(client, token, name, email):
    response = client.post("/api/v1/applicants", json={
        "name": name, "email": email, "phone": "9876543210",
        "credit_score": 780, "annual_income": 1200000.0,
        "employment_status": "salaried",
    }, headers=_headers(token))
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _submit(client, token, applicant_id, amount, tenure=24, loan_type="personal"):
    response = client.post("/api/v1/applications", json={
        "applicant_id": applicant_id, "loan_type": loan_type,
        "amount_requested": amount, "tenure_months": tenure,
        "purpose": "Search and sort test",
    }, headers=_headers(token))
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _list(client, token, **params):
    response = client.get("/api/v1/applications", params=params, headers=_headers(token))
    return response


def test_search_finds_part_of_a_name_whatever_the_capitals(client, auth_token):
    """Typing "anit" or "ANITA" both find Anita. Whole-word-only search is useless in a bank."""
    anita = _make_applicant(client, auth_token, "Anita Desai", "anita.desai@example.com")
    _make_applicant(client, auth_token, "Rohan Mehta", "rohan.mehta@example.com")
    _submit(client, auth_token, anita, 300000.0)

    for term in ("anit", "ANITA", "Desai"):
        body = _list(client, auth_token, search=term).json()
        assert body["total_count"] == 1, f"{term} -> {body['total_count']}"
        assert body["items"][0]["applicant_name"] == "Anita Desai"


def test_search_matches_an_email_too(client, auth_token):
    """A manager who only has the customer's email should still find the application."""
    applicant = _make_applicant(client, auth_token, "Vikram Rao", "vikram.rao@example.com")
    _submit(client, auth_token, applicant, 250000.0)

    body = _list(client, auth_token, search="vikram.rao@").json()
    assert body["total_count"] == 1


def test_a_number_searches_the_application_id(client, auth_token):
    """Someone quoting "application 3" should be able to type 3 into the search box."""
    applicant = _make_applicant(client, auth_token, "Meera Iyer", "meera.iyer@example.com")
    wanted = _submit(client, auth_token, applicant, 400000.0)
    _submit(client, auth_token, applicant, 500000.0)

    body = _list(client, auth_token, search=str(wanted)).json()
    ids = [item["id"] for item in body["items"]]
    assert wanted in ids


def test_sorting_by_amount_covers_every_row_not_just_this_page(client, auth_token):
    """
    The reason sorting is done by the database and not in the browser. With a
    page size of 2 and three applications, the largest amount must appear on
    page 1 even though it was submitted first and would be on page 2 by date.
    """
    applicant = _make_applicant(client, auth_token, "Sunil Nair", "sunil.nair@example.com")
    _submit(client, auth_token, applicant, 900000.0)   # biggest, submitted first
    _submit(client, auth_token, applicant, 200000.0)
    _submit(client, auth_token, applicant, 500000.0)

    body = _list(client, auth_token, sort_by="amount_requested", order="desc",
                 page=1, limit=2).json()
    assert body["total_count"] == 3
    assert [item["amount_requested"] for item in body["items"]] == [900000.0, 500000.0]

    ascending = _list(client, auth_token, sort_by="amount_requested", order="asc",
                      page=1, limit=2).json()
    assert [item["amount_requested"] for item in ascending["items"]] == [200000.0, 500000.0]


def test_sorting_by_applicant_name_works(client, auth_token):
    """Sorting by a column that lives on the other table needs a join, so it gets its own test."""
    zara = _make_applicant(client, auth_token, "Zara Khan", "zara.khan@example.com")
    aarav = _make_applicant(client, auth_token, "Aarav Gupta", "aarav.gupta@example.com")
    _submit(client, auth_token, zara, 150000.0)
    _submit(client, auth_token, aarav, 150000.0)

    body = _list(client, auth_token, sort_by="applicant_name", order="asc").json()
    names = [item["applicant_name"] for item in body["items"]]
    assert names == ["Aarav Gupta", "Zara Khan"]


def test_a_column_we_do_not_allow_is_refused(client, auth_token):
    """A caller cannot ask us to sort by any column name they invent."""
    response = _list(client, auth_token, sort_by="hashed_password")
    assert response.status_code == 400
    assert "Cannot sort by" in response.json()["detail"]

    assert _list(client, auth_token, order="sideways").status_code == 400


def test_the_list_with_no_settings_is_unchanged(client, auth_token):
    """
    The cautious-upgrade check (Rule 4). Searching and sorting were added by
    adding, so the plain call the trainer's API-07 makes must still return
    every row, newest first.
    """
    applicant = _make_applicant(client, auth_token, "Neha Joshi", "neha.joshi@example.com")
    first = _submit(client, auth_token, applicant, 100000.0)
    second = _submit(client, auth_token, applicant, 100000.0)
    third = _submit(client, auth_token, applicant, 100000.0)

    body = _list(client, auth_token).json()
    assert body["total_count"] == 3
    assert body["page"] == 1 and body["limit"] == 20
    assert [item["id"] for item in body["items"]] == [third, second, first]

    # And the filtered call API-07 makes still works alongside the new settings.
    filtered = _list(client, auth_token, status="submitted").json()
    assert filtered["total_count"] == 3
