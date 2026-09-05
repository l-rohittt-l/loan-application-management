# Build plan

This is where we plan each piece **before** building it.

1. I write the plan for one small piece here.
2. You read it and suggest changes.
3. We build it.
4. It gets marked done, committed to git, and I plan the next piece.

Only one piece is being planned at a time, so you can see the details instead of approving a finished pile of code.

---

## The folder layout for the whole project

### The one rule that decides this layout

The trainer's test files import code by name. Those names are fixed:

| Phase | The tests write | So the folder must be called |
|---|---|---|
| 1 | `from app.models.application import ...` | `app` |
| 2 | `from rag.ingest import ingest_manual` | `rag` |
| 3 | `from agent.tools import ...` | `agent` |
| 4 | `from mcp_server.mcp_app import mcp` | `mcp_server` |
| 5 | `from multi_agent.agents.compliance_checker import ...` | `multi_agent` |

None of those names has a parent folder in front of it. In Python that means **all five must sit side by side, in the same folder**, and that folder is where we run everything from. Nesting them under something like `ai/` would break every later-phase test on its first line.

### Does this layout slow the app down?

No. Folder layout has no effect on speed. Python reads the files once when the server starts, and after that the layout is irrelevant. Speed comes from other places, and those are planned in:

- **Piece 3** — indexes on the columns we filter and sort by: `status`, `loan_type`, `applicant_id`, `submitted_at`
- **Piece 7** — loading an application's history and documents in one query, not one query per row (the N+1 problem the trainer warns about)
- **Piece 9** — the dashboard counts done as a single grouped query, not by loading every application
- **Piece 12** — the timing on every request, so we can see the 200ms and 500ms targets being met

The names are the trainer's because the tests force them. The organisation around them is ours.

### The proposed layout

```
FINAL_CHANCE/                     ← the git repository starts here
│
├── CLAUDE.md                     ← instructions for me
├── PROGRESS-LOG.md               ← what we did, session by session
├── TRAPS-AND-DECISIONS.md        ← what we found, what you decided
├── BUILD-PLAN.md                 ← this file
├── FUTURE-UPGRADES.md            ← ideas for after the base is done
├── 01-POC-BLUEPRINT.md           ← the three reference documents
├── 02-GROUND-TRUTH-SHIFTS.md
├── 03-THE-FLOW-WHAT-HAPPENED.md
├── .gitignore
│
├── POC-01-Loan-Application-Management/   ← trainer's originals, never edited
├── Chats/                                ← never goes to GitHub
│
├── backend/                      ← all Python lives here, run everything from here
│   │
│   ├── app/                      ← PHASE 1 — the API
│   │   ├── main.py               starts the server, wires everything together
│   │   ├── config.py             reads the settings file
│   │   ├── database.py           the database connection
│   │   ├── domain/
│   │   │   └── rules.py          every loan rule, in one place
│   │   ├── models/               the database tables
│   │   │   ├── user.py           who can log in, with a role
│   │   │   ├── applicant.py      who borrows, with date of birth
│   │   │   ├── application.py    the loan request
│   │   │   ├── document.py       uploaded paperwork, six types
│   │   │   ├── status_history.py the audit trail of status changes
│   │   │   └── activity_log.py   who did what, human or AI
│   │   ├── schemas/              input checking on every field
│   │   ├── routers/              the web addresses
│   │   │   ├── auth.py           staff register, applicant signup, login
│   │   │   ├── applicants.py
│   │   │   ├── applications.py   includes the eligibility check
│   │   │   ├── documents.py
│   │   │   ├── dashboard.py
│   │   │   └── activity.py       manager-only activity view
│   │   ├── services/             the actual logic
│   │   ├── middleware/           runs on every request: logging, request ID
│   │   └── utils/                tokens, EMI maths, logging setup, tracing setup
│   │
│   ├── llm_provider.py           ← the Gemini / Ollama switch, used by phases 2 to 5
│   │
│   ├── rag/                      ← PHASE 2
│   │   ├── user_manual.md
│   │   ├── ingest.py
│   │   ├── rag_chain.py
│   │   └── chatbot.py            Streamlit chat, for the tests
│   │
│   ├── agent/                    ← PHASE 3
│   │   ├── tools.py
│   │   ├── prompts.py
│   │   ├── summarizer.py
│   │   └── agent.py
│   │
│   ├── mcp_server/               ← PHASE 4
│   │   ├── mcp_app.py
│   │   └── chat_interface.py     Streamlit chat, for the tests
│   │
│   ├── multi_agent/              ← PHASE 5
│   │   ├── state.py
│   │   ├── graph.py
│   │   └── agents/
│   │       ├── data_collector.py
│   │       ├── risk_assessor.py
│   │       ├── compliance_checker.py
│   │       └── decision_maker.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   └── phase1/  phase2/  phase3/  phase4/  phase5/    ← what the reviewer runs
│   │
│   ├── seed.py                   fills the database with demo data
│   ├── requirements.txt
│   ├── .env                      secrets, never committed
│   └── .env.example              same file, secrets blanked out
│
├── frontend/                     ← FIRST front-end: React + Vite. This is the demo.
│   ├── src/
│   │   ├── api/                  talks to the backend; address comes from a setting
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
│
├── frontend-streamlit/           ← SECOND front-end: Streamlit
│   └── app.py
│
└── results/                      ← test reports for submission, never committed
```

---

## The pieces of Phase 1

| # | Piece | What it is | Status |
|---|---|---|---|
| **0** | **Tools on the laptop** | Install git, Python, Node. Create the GitHub repository. | **Installs done. Waiting on GitHub.** |
| 1 | Project skeleton | Folders, virtual environment, package list, settings file, first commit | Planned below |
| 2 | Domain rules | Every loan rule in one file | Waiting on D-14 |
| 3 | Database + 6 models | Six tables, with indexes on the filtered columns | Ready |
| 4 | Schemas | Input checking on every field, not just the ones the trainer names | Ready |
| 5 | Auth | Staff register, applicant signup, login, token, roles (Option A) | Ready |
| 6 | Applicant endpoints | Create and view a borrower | Ready |
| 7 | Application endpoints | Create, view, list, change status. History and documents loaded in one query. | Ready |
| 8 | Document endpoints | Record an uploaded document | Ready |
| 9 | Dashboard endpoint | The counts, as one grouped query | Ready |
| 10 | Eligibility check | Warns the form before submitting, all three loan types | Waiting on D-14 |
| 11 | Activity log | One table, one write helper, one manager-only page. Records human or AI actor. | Ready |
| 12 | Logging and tracing | JSON logs with request ID and associate ID; timings on every request | Ready |
| 13 | Tests | All 20, in `tests/phase1/`, named as the trainer's file says | Ready |
| 14 | React front-end | The demo. Backend address from a setting, never hardcoded. | After the backend |
| 15 | Streamlit front-end | List, form, dashboard | After React |
| 16 | Seed data and test report | Demo data, then the submission files | Last |

---

## Piece 0 — Tools on the laptop

Checked on 2026-09-05: git, Python and Node are not installed. winget is. This is Rohit's personal laptop, so anything can be installed.

Claude is running the installs. If you'd rather do it yourself, the commands are:

```powershell
winget install --id Git.Git -e --source winget
winget install --id Python.Python.3.11 -e --source winget
winget install --id OpenJS.NodeJS.LTS -e --source winget
```

Then close PowerShell, open it again, and check all three answer:

```powershell
git --version
python --version
node --version
```

Then tell git who you are, once, using the same name and email you'll use on GitHub:

```powershell
git config --global user.name "Rohit Sawant"
git config --global user.email "your-github-email@example.com"
```

**On GitHub:**
1. Sign in, click **New repository**.
2. Name: `poc-01-loan-application-management`.
3. Set it to **Private**.
4. Leave every "initialize with" box **unticked**. We already have files.
5. Click Create, then copy the HTTPS address it shows, and paste it to me.

I'll connect the folder to it and push. The first push will open a browser window asking you to sign in to GitHub; that's normal.

---

## Piece 1 — Project skeleton

Runs as soon as Piece 0 is done.

**Creates:** the `backend/` folder with an empty `app/` package inside, the `frontend-streamlit/` folder, a Python virtual environment inside `backend/`, the package list, the settings file and its blank example, and the first commit.

**The virtual environment** is a private copy of Python for this project. Packages installed into it don't touch anything else on the laptop, and the exact versions the trainer specifies stay pinned.

**The package list** uses the trainer's versions from `TECH_STACK_REFERENCE.md` for Phase 1 only: FastAPI, uvicorn, SQLAlchemy, pydantic, python-jose, passlib with bcrypt, structlog, the OpenTelemetry packages, python-dotenv, pytest, httpx. Phase 2+ packages get added when those phases start.

**The settings file** holds: the database address, the JWT secret, the token lifetime, `POC_ID`, `PHASE`, `ASSOCIATE_ID`, and the allowed front-end origin (5173).

**Nothing here depends on any open question.**

---

## Done

Nothing yet.
