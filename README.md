# Loan Application Management System

POC-01 for the Agentic AI Readiness Program. A loan application system for a bank, built in five phases: the website first, then AI layers on top.

**Status: all five phases complete. Every trainer test passes, none skipped.**

| Phase | What it is | Tests |
|---|---|---|
| 1 | REST API, React and Streamlit front-ends | 20 / 20 |
| 2 | RAG chatbot that answers from the user manual | 20 / 20 |
| 3 | Agent with five tools reading live data | 20 / 20 |
| 4 | MCP server and a staff chat interface | 25 / 25 |
| 5 | Four-agent underwriting review (LangGraph) | 25 / 25 |

Plus the headline feature that is not a trainer requirement: **the Manager's Morning Briefing**, which reads the whole pipeline and tells the branch manager what needs attention today.

## What is where

| Folder | What it is |
|---|---|
| `backend/app/` | Phase 1 — the API (Python, FastAPI, SQLite) |
| `backend/rag/` | Phase 2 — the manual, ingestion, and the chatbot chain |
| `backend/agent/` | Phase 3 — the agent and its five tools |
| `backend/mcp_server/` | Phase 4 — the MCP server and the staff chat screen |
| `backend/multi_agent/` | Phase 5 — the four underwriting agents and the graph |
| `frontend/` | The React app. This is what gets demoed. |
| `frontend-streamlit/` | The second front-end, in Streamlit. |
| `POC-01-Loan-Application-Management/` | The trainer's original documents, unchanged. |

The five Python packages sit side by side under `backend/` because the trainer's tests import them by those exact names. Everything is run from `backend/`.

The working documents at the root (`BUILD-PLAN.md`, `PROGRESS-LOG.md`, `TRAPS-AND-DECISIONS.md`, `RUN-REPORT.md`, `FUTURE-UPGRADES.md`, `LEARNING-NOTES.md`, `AI-BUILD-LOG.md`) are the project's memory. `01`, `02` and `03` are the reference documents.

## Before you start

You need **Python 3.11**, **Node 18+**, and git. You also need a **Google Gemini API key** for Phases 2 to 5 — the free tier is enough, with one caveat in "Things worth knowing" below.

Everything is run from PowerShell.

### First-time setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

Then open `backend\.env` and set:

- `SECRET_KEY` — any random string
- `GOOGLE_API_KEY` — your Gemini key (needed from Phase 2 onward)
- `LANGCHAIN_API_KEY` — optional, free from smith.langchain.com; without it two Phase 2 observability tests skip

Finally, load the demo data:

```powershell
.\venv\Scripts\python.exe seed.py
```

## Running it

### 1. The backend — always start this first (port 8000)

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Swagger is at http://localhost:8000/docs, health check at http://localhost:8000/health.

Everything else in this project talks to this server, so nothing below works without it.

### 2. React front-end — the demo (port 5173)

```powershell
cd frontend
npm install                              # first time only
copy .env.example .env                   # first time only
npm run dev
```

Open http://localhost:5173. Sign in as the manager to see the Morning Briefing at the top of the dashboard.

### 3. Streamlit front-end (port 8501)

```powershell
backend\venv\Scripts\streamlit run frontend-streamlit/app.py
```

The customer-and-staff screens, plus the Phase 2 assistant tab.

### 4. Phase 2 — the chatbot's knowledge

The manual is ingested into ChromaDB once. It is fingerprinted, so re-running costs nothing unless the manual changed.

```powershell
cd backend
.\venv\Scripts\python.exe -m rag.ingest            # add --force to re-embed anyway
```

The chatbot itself is the Assistant page in React and the Assistant tab in Streamlit.

### 5. Phase 4 — the staff chat interface (port 8502)

A separate Streamlit app where staff manage applications by typing sentences.

```powershell
cd backend
.\venv\Scripts\streamlit run mcp_server/chat_interface.py --server.port 8502
```

Try "Show me all pending applications" or "Show details of application 1".

### 6. Phase 5 — the four-agent underwriting review

```powershell
cd backend
.\venv\Scripts\python.exe -m multi_agent.main
# then type an application number, e.g. 1
```

Prints what each of the four agents concluded, then the final decision and its reasoning.

## Tests

Run from `backend/`, with the backend server already running (Phases 3, 4 and 5 call it over HTTP).

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/phase1 -v          # 27 runs (4 cases are parametrised)
.\venv\Scripts\python.exe -m pytest tests/phase2 -v          # 22
.\venv\Scripts\python.exe -m pytest tests/phase3 -v          # 23
.\venv\Scripts\python.exe -m pytest tests/phase4 -v          # 25
.\venv\Scripts\python.exe -m pytest tests/phase5 -v          # 25
.\venv\Scripts\python.exe -m pytest tests/ours  -v           # 20, ours rather than the trainer's
```

The submission reports:

```powershell
.\venv\Scripts\python.exe -m pytest tests/phase1 --junitxml=../results/phase1-results.xml
```

**Two things to know before running the full suite.** Phases 2 to 5 make real AI calls, so a full run takes several minutes and spends a few dozen requests of the daily quota. And the Phase 3, 4 and 5 tests write real rows into the demo database — run this afterwards to clear them out:

```powershell
.\venv\Scripts\python.exe clean_test_data.py
```

## Demo logins (after `seed.py`)

| Role | Email | Password |
|---|---|---|
| Branch manager | anita@bank.com | Manager@123 |
| Loan officer | rajan@bank.com | Officer@123 |
| Customer | priya@example.com (also rahul, meera, arjun, kavya, sanjay @example.com) | Customer@123 |

A manager sees everything, including the activity log and the Morning Briefing. An officer reviews and moves applications but cannot pay out. A customer sees only their own applications.

## Before a demo

1. `python clean_test_data.py` — clears any rows the test suites left behind
2. **Do not run the full test suite on demo day.** It spends the AI quota; the demo itself costs only a handful of calls.
3. Start the backend, then the React app. Sign in as the manager.

## Things worth knowing

- **The AI quota is 500 requests a day** on Gemini's free tier. A full test run spends a few dozen; two or three full runs in a day exhausts it. Every AI feature degrades to plain deterministic text and says so on screen rather than failing, so nothing breaks — but the AI writing disappears until the quota resets.
- **No number in this system is calculated by an AI.** Eligibility, risk scores, underwriting decisions and the briefing's figures are all plain Python reading `backend/app/domain/rules.py`. The AI writes the prose a human reads. That makes decisions repeatable and auditable, and means a quota outage can never change a lending decision.
- The models the trainer specified were withdrawn by Google mid-programme. The project runs `gemini-3.5-flash-lite` and `gemini-embedding-001`, both set in `.env` so swapping them is one line.
- Bank staff register at `/register`; customers sign up at `/signup`. Managers are created by the bank, never self-registered.
- Every rule of the loan system is in one file: `backend/app/domain/rules.py`.
- The eligibility check on the application form is advice, not a block. It explains what would fail and suggests a fix — and the server records its own copy of that assessment permanently on every application.
- The backend address for the front-ends comes from a `.env` setting, never from code, so the app can be hosted later.
- The activity log records who did what, including whether it was a person or an AI acting for one.
