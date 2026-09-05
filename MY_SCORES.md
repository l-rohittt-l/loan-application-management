# Test Score Tracker

**Associate Name:** Rohit Sawant
**POC Number:** POC-01 — Loan Application Management System
**Tech Stack:** Python (FastAPI, SQLAlchemy, SQLite) · React 18 + Vite · Streamlit
**Date:** 2026-09-06

## Phase Results

| Phase | Tests Passed | Total Tests | % Score | Cleared (≥70%)? |
|-------|-------------|-------------|---------|-----------------|
| 1     | 20          | 20          | 100%    | Yes             |
| 2     |             | 20          |         |                 |
| 3     |             | 20          |         |                 |
| 4     |             | 25          |         |                 |
| 5     |             | 25          |         |                 |

**Weighted Total:** 15.0 / 100 so far (Phase 1 = 15% × 100%)
**Performance Tier:** in progress

## Failed Test Cases (List each failed TC ID and reason)

| Test Case ID | Reason for Failure |
|--------------|-------------------|
| none         | —                 |

## Notes on the Phase 1 run

- Run with `pytest tests/phase1 -v --junitxml=results/phase1-results.xml` from `backend/`. 27 runs because four of the twenty cases are parametrised (UNIT-04 and UNIT-08 run four values each).
- One skeleton adaptation, documented in the test file: TC-01-P1-DB-02 reads `app.id` before the row is flushed, which fails on any implementation; a `db_session.flush()` was added after `db_session.add(app)`.
- Two fixtures the spec uses but does not define, `db_session` and `test_user`, are provided in `tests/conftest.py`.
