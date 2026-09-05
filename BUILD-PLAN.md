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
| 0 | Tools on the laptop | Install git, Python, Node. Create the GitHub repository. | **Done 2026-09-06** |
| 1 | Project skeleton | Folders, virtual environment, package list, settings file | **Done 2026-09-06** |
| 2 | Domain rules | Every loan rule in one file | **Done 2026-09-06** |
| 3 | Database + 6 models | Six tables, with indexes on the filtered columns | **Done 2026-09-06** |
| 4 | Schemas | Input checking on every field, not just the ones the trainer names | **Done 2026-09-06** |
| 5 | Auth | Staff register, applicant signup, login, token, roles (Option A) | **Done 2026-09-06** |
| 6 | Applicant endpoints | Create and view a borrower | **Done 2026-09-06** |
| **7** | **Application endpoints** | Create, view, list, change status. History and documents loaded in one query. | **Next** |
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

## Piece 2 — Domain rules

**One file:** `backend/app/domain/rules.py`.

**What it is:** every business rule of the loan system, written once, as plain Python constants and a few tiny helper functions. Nothing else in the project types a loan limit or a status transition by hand. They import it from here.

**Why it matters more than its size:** the same rules appear in five places across the five phases: Phase 1 validation, the Phase 2 manual, the Phase 3 tool that reports status, the Phase 4 tool that changes status, and the Phase 5 compliance and decision agents. If each phase has its own copy, they drift, and the chatbot ends up contradicting the app. One file, imported everywhere, and they cannot drift.

**One design choice:** this file imports nothing from the rest of the app. No database, no models, no FastAPI. Just numbers, sets, and small functions. That way Phase 3 and Phase 5 can import it without dragging in the whole web server. The status and document *enums* live in the models (the tests import them from there), but they use the same string values as this file, so they compare equal.

**What goes in it:**

| Group | Contents | Source |
|---|---|---|
| Allowed values | loan types, statuses, document types (six, with vehicle quotation), employment statuses, user roles | Blueprint Part 5, D-04, D-07 |
| Status machine | which status can move to which, and which move needs a manager | Blueprint Part 5, D-06 |
| Amounts | global 10,000 to 1 crore; per type: personal 25 lakh, auto 50 lakh, home 1 crore | Blueprint Part 6, D-03 |
| Tenure | global 6 to 360; per type: personal 12–60, home 12–360, auto 12–84 | Blueprint Part 6, D-02 |
| Eligibility | minimum CIBIL, minimum income, age range per type; home loan must end before 70 | Manual Section 5, D-05 |
| Documents | required documents per loan type | Manual Section 4, D-04 |
| Affordability | EMI may not exceed 50% of monthly income; default interest 12% for estimates | D-14, Phase 5 doc |
| Employment | salaried need 6 months with current employer, self-employed need 2 years | Manual Section 11 FAQ |
| Phase 5 scoring | approve above 70, reject below 40, the deduction table | D-10, T-13, T-14 |
| Helpers | `is_valid_transition`, `requires_manager`, `tenure_range`, `amount_limit`, `required_documents`, `missing_documents` | — |

**What does not go in it:** the EMI formula. The tests require that at `app.utils.finance.calculate_emi`, so it lives there. Eligibility *checking* (which needs EMI maths and an applicant's data) goes in a service in Piece 10. This file only holds the numbers and the yes/no rules.

**Tests it satisfies:** UNIT-05 and UNIT-06 (status transitions) end up as one-line wrappers around this file.

**Open before building:** D-16 in the traps file. Two Phase 5 rules reference applicant data the table does not have.

---

## Piece 3 — Database and the six tables

**Files:** `app/database.py` (the connection), `app/models/__init__.py`, and one file per table in `app/models/`.

**What a "model" is:** a Python class that describes one database table. Each attribute is a column. SQLAlchemy reads these classes and creates the tables for us. So this piece is "describe the six tables in Python".

### The connection — `database.py`

- Opens the SQLite file named in `.env`.
- Sets `check_same_thread=False`, which SQLite needs when a web server handles several requests at once (trainer's common-mistake #1).
- **Does not turn on foreign-key enforcement.** Two of the trainer's tests create records pointing at an applicant that doesn't exist, and would fail if SQLite checked (T-03).
- Provides `Base` and `get_db`, which the tests import by those exact names (T-06).

### The six tables

| Table | File | Columns | Notes |
|---|---|---|---|
| **users** | `user.py` | id, name, email, hashed_password, role, is_active, created_at | Who logs in. `role` is one of the three in the rules file. Email unique. |
| **applicants** | `applicant.py` | id, user_id, name, email, phone, **date_of_birth**, credit_score, annual_income, employment_status, **years_with_employer**, **existing_monthly_emi**, created_at | Who borrows. The three bold columns are our additions (D-05, D-16), all optional. `user_id` links to a login when the applicant signed up themselves; empty when an officer created the record. |
| **loan_applications** | `application.py` | id, applicant_id, loan_type, amount_requested, tenure_months, purpose, status, submitted_at, updated_at | The loan request. Also defines the `LoanType` and `ApplicationStatus` enums the tests import. |
| **documents** | `document.py` | id, application_id, doc_type, file_name, uploaded_at, verified | Six document types. Deleted automatically when the application is deleted (T-04). |
| **status_history** | `status_history.py` | id, application_id, old_status, new_status, changed_by, changed_at, remarks | The audit trail. Also deleted with the application. |
| **activity_log** | `activity_log.py` | id, actor_type, actor_id, actor_role, on_behalf_of, action, entity_type, entity_id, details, request_id, ip_address, created_at | Your idea (D-11). `actor_type` is "human" or "ai". `actor_id` is the email, or the agent's name. `on_behalf_of` is the user an AI was acting for. |

### Speed, built in now

Indexes on every column we will filter or sort by: `status`, `loan_type`, `applicant_id`, `submitted_at` on applications; `application_id` on documents and history; `created_at`, `actor_id` and `entity_id` on the activity log; `email` on users and applicants. An index is a lookup table the database keeps so it can find rows without reading the whole table.

### Tests this piece satisfies

DB-01, DB-03, DB-04 pass with the models alone. DB-02 needs the models plus the fixtures from Piece 13.

### Nothing open. All decisions this needs are settled.

---

## Piece 4 — Schemas, the input-checking layer

**What a schema is:** a description of what a request is allowed to contain. When someone sends data to the API, it is checked against the schema before any of our code runs. If a field is missing, too long, the wrong type, or out of range, the API answers with a 422 error listing exactly what was wrong, and our code never sees the bad data. Pydantic is the library that does this.

**Files, one per topic in `app/schemas/`:** `auth.py` (register, applicant signup, login, token), `applicant.py`, `application.py` (create, status change, list, the eligibility check, and the detailed response with the applicant and history nested inside), `document.py`, `activity.py`.

**The names the tests fix:** `CreateApplicantSchema`, `CreateApplicationSchema`, `CreateDocumentSchema` (T-06).

**Rule 6 applied — every field gets checked, not just the ones the trainer lists:**

| Field | Check |
|---|---|
| name | 2 to 100 characters, letters, spaces, dots and hyphens only |
| email | a real email shape (this is what test UNIT-02 checks) |
| phone | exactly 10 digits, Indian mobile |
| password | 8 to 72 characters, at least one capital letter and one digit (72 is bcrypt's hard limit) |
| credit_score | optional; if given, 300 to 900 (UNIT-08) |
| annual_income | more than zero, sane upper bound |
| date_of_birth | optional; not in the future; not before 1900 |
| years_with_employer | optional; zero or more, at most 60 |
| existing_monthly_emi | zero or more |
| amount_requested | 10,000 to 1 crore (UNIT-04). The per-type cap is checked in the service, so this test keeps passing exactly as written. |
| tenure_months | 6 to 360. Per-type range checked in the service, same reason. |
| purpose | 3 to 500 characters |
| doc_type | one of the six (UNIT-07) |
| file_name | 1 to 255 characters, must end in .pdf, .jpg, .jpeg or .png (manual Section 12) |
| remarks | up to 1,000 characters |
| status filter | one of the five, else 400 (T-18) |
| page / limit | page 1 or more; limit 1 to 100 |

**Why per-type limits live in the service, not here:** the trainer's UNIT-04 test builds a `CreateApplicationSchema` with `loan_type="personal"` and only checks the global amount bounds. If the schema also enforced the 25-lakh personal cap, the test would still pass, but the eligibility check in Piece 10 needs to explain *why* something is over the limit, which is a service job. Keeping schemas to shape-and-range and services to business rules is the cleaner split.

**Tests this piece satisfies on its own:** UNIT-02, UNIT-04, UNIT-07, UNIT-08.

**Nothing open.**

---

## Piece 5 — Auth: who you are, and what you're allowed to do

**What it is:** the login system. Register, sign up, log in, get a token, and a small piece that every protected endpoint uses to say "who is calling, and are they allowed?"

**How a token works, in plain words:** when you log in with the right password, the server hands you a long string of text called a JWT. It contains your email and role, signed with the server's secret so it cannot be forged. You send it back with every later request in a header, and the server reads it to know who you are without asking for the password again. It expires after 24 hours.

**Files:**

| File | Holds |
|---|---|
| `utils/auth.py` | hash a password, check a password, create a token, read a token |
| `dependencies.py` | `get_current_user` (reads the token, loads the user, or answers 401) and `require_role(...)` for endpoints only some roles may call |
| `services/auth_service.py` | the logic: register staff, sign up an applicant (creates both rows, T-23), check a login |
| `services/activity_service.py` | one small function, `record(...)`, that writes an activity-log row. Created here because logins are the first thing worth recording; every later piece reuses it. |
| `routers/auth.py` | the four addresses below |

**Addresses:**

| Method | Address | What it does | Answers |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Staff account. Defaults to loan officer (D-07). The trainer's test uses this. | 201, 409 if email exists, 422 if weak password |
| POST | `/api/v1/auth/register-applicant` | Customer signup. One request creates the login and the borrower profile. | 201, 409 |
| POST | `/api/v1/auth/login` | JSON body in, token out (T-05) | 200, 401 without saying which field was wrong |
| GET | `/api/v1/auth/me` | Who am I, from the token | 200, 401 |

**Two traps handled here:**
- T-01: the built-in bearer helper answers 403 when the header is missing. We turn its automatic error off and raise 401 ourselves, which is what test API-06 expects.
- Login failures say "invalid email or password", never which one, so nobody can use the login page to discover which emails exist.

**What gets recorded in the activity log:** staff registered, applicant signed up, login succeeded, login failed (with the email tried, so a manager can spot someone guessing passwords).

**Tests this piece satisfies:** the `auth_token` fixture every API test depends on, and API-06.

**Nothing open.**

---

## Piece 6 — Applicant endpoints

**What it is:** creating and viewing a borrower profile. Small piece, but it carries the first owner-scoping rule (the peer bug from Change 10) and the function the trainer's UNIT-01 test calls by name.

**Files:** `services/applicant_service.py`, `routers/applicants.py`.

**Addresses:**

| Method | Address | Who may call | Answers |
|---|---|---|---|
| POST | `/api/v1/applicants` | Staff | 201, 409 duplicate email, 422 bad data. The trainer's `test_applicant` fixture uses this with an officer's token. |
| GET | `/api/v1/applicants` | Staff | 200, paged list |
| GET | `/api/v1/applicants/{id}` | Staff see anyone. **An applicant sees only their own profile**; asking for someone else's gets 403. | 200, 403, 404 |

**The function the test names:** `applicant_service.create_applicant(db, data)` must accept exactly a session and a `CreateApplicantSchema`, and return an object with `id`, `email`, `credit_score` and `created_at` filled in (UNIT-01).

**Recorded in the activity log:** `applicant_created`, with who created it.

**Nothing open.**

---

## Piece 7 — Application endpoints, the heart of Phase 1

**What it is:** submitting a loan application, viewing one, listing them with filters, and moving one through its statuses. Half of the trainer's API tests hit these four addresses.

**Files:** `services/application_service.py`, `routers/applications.py`.

**Addresses:**

| Method | Address | Who | Answers |
|---|---|---|---|
| POST | `/api/v1/applications` | Anyone logged in. An applicant may only apply for themselves. | 201; 404 unknown applicant; 422 missing fields or a per-type rule broken; 403 applying for someone else |
| GET | `/api/v1/applications` | Staff see all. Applicants see only their own. | 200 with `items`, `total_count`, `page`, `limit`; **400** for a bad status or loan type (T-18) |
| GET | `/api/v1/applications/{id}` | Staff, or the owning applicant | 200 with the applicant, every status change and every document nested; 403; 404 |
| PATCH | `/api/v1/applications/{id}/status` | Staff only. `approved → disbursed` needs a manager (D-06). | 200; **400 "Invalid status transition"**; 403; 404 |

**The function the tests name:** `application_service.validate_status_transition(current, new)` returning True or False (UNIT-05, UNIT-06). It is a one-line wrapper around the rules file.

**What happens on submit:** the applicant must exist; the amount and tenure must be inside the per-loan-type range (D-02, D-03), with a plain-English message if not; the application is created with status `submitted`; a first history row is written with no old status; an activity row is written; all committed together.

**What happens on a status change:** the move must be allowed by the rules file; if it is the manager-only move, the caller must be a manager; the status changes, `updated_at` refreshes, a history row records who and why, an activity row is written; all committed together.

**Speed:** the detail view loads the applicant, the history and the documents in **one** query, not one per row. The list view joins the applicant's name in the same query. This is the trainer's "no N+1" requirement.

**Filters on the list:** status, loan type, submitted from date, submitted to date. All combined with AND. Sorted newest first. Page and limit as in the spec.

**Tests this piece satisfies:** UNIT-05, UNIT-06, API-01, API-02, API-03, API-04, API-05, API-06, API-07.

**One bug fixed on the way:** T-33.

**Nothing open.**

---

## Done

| # | Piece | Finished | Commit |
|---|---|---|---|
| 0 | Tools on the laptop | 2026-09-06 | `02fcf34` first commit; repo at `github.com/l-rohittt-l/loan-application-management` (private) |
| 1 | Project skeleton | 2026-09-06 | `backend/` with `app/` package, venv on Python 3.11.9, `requirements.txt` at trainer's versions plus two fixes (T-30, T-31), `.env` with a generated secret, `.env.example` |
| 2 | Domain rules | 2026-09-06 | `app/domain/rules.py`: every rule as plain constants and six helpers. No imports from the app. Sanity checks pass. |
| 3 | Database + 6 models | 2026-09-06 | `config.py`, `database.py`, and `models/` with the six tables. Smoke test mirrors DB-01 to DB-04 and passes. Tag `v0.0.3`. |
| 4 | Schemas | 2026-09-06 | `schemas/` with six files. Every input field checked. Smoke test mirrors UNIT-02, 04, 07, 08 plus eight stricter checks; all pass. Tag `v0.0.4`. |
| 5 | Auth | 2026-09-06 | `utils/auth.py`, `dependencies.py`, `services/auth_service.py`, `services/activity_service.py`, `services/errors.py`, `routers/auth.py`. Smoke test covers the trainer's fixture, 401-not-403, role gate, applicant signup creating two rows, and five activity-log rows. Tag `v0.0.5`. |
| 6 | Applicant endpoints | 2026-09-06 | `services/applicant_service.py`, `routers/applicants.py`. Smoke test covers UNIT-01, the `test_applicant` fixture, and owner scoping (an applicant is blocked from other profiles, the list, and creating). Tag `v0.0.6`. |
