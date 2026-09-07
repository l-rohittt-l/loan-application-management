# Test Score Tracker

**Associate Name:** Rohit Sawant
**POC Number:** POC-01 — Loan Application Management System
**Tech Stack:** Python (FastAPI, SQLAlchemy, SQLite) · React 18 + Vite · Streamlit
**Date:** 2026-09-06

## Phase Results

| Phase | Tests Passed | Total Tests | % Score | Cleared (≥70%)? |
|-------|-------------|-------------|---------|-----------------|
| 1     | 20          | 20          | 100%    | Yes             |
| 2     | 20          | 20          | 100%    | Yes             |
| 3     | 23          | 23          | 100%    | Yes             |
| 4     | 25          | 25          | 100%    | Yes             |
| 5     |             | 25          |         |                 |

Phase 2 and Phase 3 each have a few extra tests of ours beyond the trainer's count (Phase 2: 20 trainer + 2 ours for LangSmith; Phase 3: 20 trainer + 3 ours, one of them catching a real gap in a tool's description). The row above is the trainer's own 20 in each case, at 100%.

**Phase weights, from the blueprint:** Phase 1 = 15%, Phase 2 = 20%, Phase 3 = 20%, Phase 4 = 25%, Phase 5 = 20%.

**Weighted Total so far:** 15.0 (Phase 1) + 20.0 (Phase 2) + 20.0 (Phase 3) + 25.0 (Phase 4) = **80.0 / 100**
**Performance Tier:** in progress

## Failed Test Cases (List each failed TC ID and reason)

| Test Case ID | Reason for Failure |
|--------------|-------------------|
| none         | —                 |

## Notes on the Phase 1 run

- Run with `pytest tests/phase1 -v --junitxml=results/phase1-results.xml` from `backend/`. 27 runs because four of the twenty cases are parametrised (UNIT-04 and UNIT-08 run four values each).
- One skeleton adaptation, documented in the test file: TC-01-P1-DB-02 reads `app.id` before the row is flushed, which fails on any implementation; a `db_session.flush()` was added after `db_session.add(app)`.
- Two fixtures the spec uses but does not define, `db_session` and `test_user`, are provided in `tests/conftest.py`.
