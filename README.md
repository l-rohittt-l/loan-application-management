# Loan Application Management System

POC-01 for the Agentic AI Readiness Program. A loan application system for a bank, built in five phases: the website first, then AI layers on top.

**Phase 1 status:** complete. All 20 trainer tests pass.

## What is where

| Folder | What it is |
|---|---|
| `backend/` | The API (Python, FastAPI, SQLite). Every later phase lives under here too. |
| `frontend/` | The React app. This is what gets demoed. |
| `frontend-streamlit/` | The second front-end, in Streamlit. |
| `POC-01-Loan-Application-Management/` | The trainer's original documents, unchanged. |

The working documents at the root (`BUILD-PLAN.md`, `PROGRESS-LOG.md`, `TRAPS-AND-DECISIONS.md`, `FUTURE-UPGRADES.md`, `LEARNING-NOTES.md`) are the project's memory. `01`, `02` and `03` are the reference documents.

## Running it

You need Python 3.11, Node 18+, and git. Everything below is run from the project root in PowerShell.

### 1. Backend (port 8000)

```powershell
cd backend
python -m venv venv                      # first time only
.\venv\Scripts\python.exe -m pip install -r requirements.txt   # first time only
copy .env.example .env                   # first time only; then set SECRET_KEY to a random string
.\venv\Scripts\python.exe seed.py        # optional: demo data and logins
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Swagger is at http://localhost:8000/docs. Health check at http://localhost:8000/health.

### 2. React front-end (port 5173)

```powershell
cd frontend
npm install                              # first time only
copy .env.example .env                   # first time only
npm run dev
```

Open http://localhost:5173.

### 3. Streamlit front-end (port 8501)

```powershell
backend\venv\Scripts\streamlit run frontend-streamlit/app.py
```

### 4. Tests

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/phase1 -v
.\venv\Scripts\python.exe -m pytest tests/phase1 --junitxml=results/phase1-results.xml   # the submission report
```

## Demo logins (after `seed.py`)

| Role | Email | Password |
|---|---|---|
| Branch manager | anita@bank.com | Manager@123 |
| Loan officer | rajan@bank.com | Officer@123 |
| Customer | priya@example.com (also rahul, meera, arjun, kavya, sanjay @example.com) | Customer@123 |

A manager sees everything including the activity log. An officer reviews and moves applications, but cannot pay out. A customer sees only their own applications.

## Things worth knowing

- Bank staff register at `/register`; customers sign up at `/signup`. Managers are created by the bank, never self-registered.
- Every rule of the loan system is in one file: `backend/app/domain/rules.py`.
- The eligibility check on the application form is advice, not a block. It explains what would fail and suggests a fix.
- The backend address for the front-ends comes from a `.env` setting, never from code, so the app can be hosted later.
- The activity log records who did what, including whether it was a person or an AI acting for one. Every later phase gets recorded automatically because it uses the same backend.
