"""
Shared test setup. The trainer's phase1-test-spec.md gives `client`,
`auth_token` and `test_applicant` almost exactly as below. It also uses
`db_session` and `test_user` without ever defining them (T-08); those two
are ours.

Every test gets a fresh database file, test.db, created before and dropped
after (T-20). The real app database is never touched.
"""

import os

# Keep the test output readable: no span dumps. Must be set before app.main
# is imported, because settings are read at import time.
os.environ.setdefault("OTEL_EXPORTER", "none")
# Tests should not leave log files behind.
os.environ.setdefault("LOG_TO_FILE", "false")

import pytest                                        # noqa: E402
from fastapi.testclient import TestClient            # noqa: E402
from sqlalchemy import create_engine                 # noqa: E402
from sqlalchemy.orm import sessionmaker              # noqa: E402

from app.main import app                             # noqa: E402
from app.database import Base, get_db                # noqa: E402
from app.models.user import User, UserRole           # noqa: E402
from app.utils.auth import hash_password             # noqa: E402

TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def client():
    """The trainer's fixture: a fresh database and a test client whose get_db points at it."""
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def auth_token(client):
    """The trainer's fixture: register an officer and log in."""
    client.post("/api/v1/auth/register", json={
        "name": "Test Officer", "email": "officer@test.com", "password": "Test@1234"
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "officer@test.com", "password": "Test@1234"
    })
    return response.json()["access_token"]


@pytest.fixture
def test_applicant(client, auth_token):
    """The trainer's fixture: one borrower profile, created by the officer."""
    response = client.post("/api/v1/applicants", json={
        "name": "Test Applicant", "email": "applicant@test.com",
        "phone": "9876543210", "credit_score": 720,
        "annual_income": 600000.0, "employment_status": "salaried"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    return response.json()


# ---- The two fixtures the trainer's tests use but never define (T-08) ----

@pytest.fixture(scope="function")
def db_session():
    """A plain database session on a fresh test database, for the unit and DB tests."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user(db_session):
    """A loan officer row, for tests that need someone to have made a change."""
    user = User(
        name="Test Officer", email="officer@test.com",
        hashed_password=hash_password("Test@1234"), role=UserRole.loan_officer,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
