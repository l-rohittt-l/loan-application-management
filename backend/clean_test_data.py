"""
Remove applications created by the Phase 3, 4 and 5 test suites from the demo
database.

Why this exists (T-65): those phases' tests talk to the Phase 1 API over HTTP
through the `running_api` fixture, and that fixture reuses a server that is
already running — which is the real one, on the real `loan_app.db`. So every
test that submits an application writes a row into the demo database. One
full test run left 60 applications named things like "Phase 5 underwriting
fixture" sitting in the manager's pipeline, which would have been the first
thing an Account Delivery Head saw on the dashboard.

Run this before any demo:

    cd backend
    .\\venv\\Scripts\\python.exe clean_test_data.py

It only deletes applications whose purpose matches one of the known test
fixtures below, never anything a person typed. Documents and status history
go with them, because the ORM cascades (T-04).
"""

from app.database import SessionLocal
from app.models.application import LoanApplication

# The exact purposes the test suites use. Anything not on this list is left alone.
TEST_PURPOSES = [
    "Phase 5 underwriting fixture",
    "Phase 4 integration fixture",
    "MCP test application",
    "MCP-04 fixture",
    "Status update test",
    "Chat status change test",
    "Briefing test",
]

TEST_APPLICANT_EMAILS = [
    "mcp.test@example.com",
    "phase5.test@example.com",
]


def main() -> None:
    db = SessionLocal()
    try:
        applications = (
            db.query(LoanApplication)
            .filter(LoanApplication.purpose.in_(TEST_PURPOSES))
            .all()
        )
        if not applications:
            print("Nothing to clean: no test applications found.")
            return

        print(f"Deleting {len(applications)} test application(s):")
        for app in applications:
            print(f"  #{app.id}  {app.loan_type.value:9}  {app.purpose}")
            db.delete(app)          # documents and history cascade with it
        db.commit()
        print("Done. The demo data created by seed.py is untouched.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
