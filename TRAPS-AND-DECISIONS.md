# Traps and decisions

Things I found that you should know about, and things only you can answer.

- **Needs your call** — open questions. Each has my recommendation. "Agree" is a valid answer.
- **Traps and differences** — no decision needed, just be aware.
- **Settled** — answered items, kept so we never argue them twice.

---

# Needs your call

One open, and it can wait.

---

### D-09 · Angular as a third front-end later?

**My recommendation:** revisit once Phase 5 is demo-ready. Listed in `FUTURE-UPGRADES.md`.

**Your answer:**

---

### Parked, not open

**D-12 · Hosting.** Clarified: we build on Rohit's personal laptop, which has no restrictions. The Wipro laptop is restricted and might only ever open the app in a browser. Whether to host the app online is decided before the demo, not now. One design habit from now on so it stays possible: the front-end reads the backend's address from a setting, never hardcoded.

---

# Traps and differences

No decision needed. These break something quietly if forgotten.

### From the Phase 1 test spec

**T-01 · The 401 vs 403 trap.** FastAPI's built-in bearer token helper returns **403** when the Authorization header is missing. Test `TC-01-P1-API-06` asserts **401**. Fix: turn off the automatic error and raise the 401 ourselves.

**T-02 · The trailing slash trap.** All tests call `/api/v1/applications` with no trailing slash. A route declared as `"/"` under a prefix becomes `/api/v1/applications/` and answers with a redirect. Fix: declare route paths as `""`.

**T-03 · Do not turn on SQLite foreign keys.** Tests `DB-02` and `DB-04` create a loan application pointing at applicant ID 1, which doesn't exist. Switch foreign keys on and both tests fail.

**T-04 · Cascade delete has to be at the ORM level.** `DB-04` deletes an application and expects its documents to vanish. Because of T-03 the database enforces nothing, so SQLAlchemy must be told to cascade on the relationship.

**T-05 · Login takes JSON, not a form.** The test fixture posts JSON with email and password and reads back `access_token`. The OAuth2 form from tutorials breaks every authenticated test at once.

**T-06 · Module paths and function names are fixed by the tests.** `app.utils.finance.calculate_emi(principal, annual_rate, tenure_months)`, `app.services.application_service.validate_status_transition(current, new)` returning True or False, `app.services.applicant_service.create_applicant(db, data)`, and the schema names `CreateApplicantSchema`, `CreateApplicationSchema`, `CreateDocumentSchema`.

**T-07 · `User` and `Applicant` are two different tables.** User is who logs in, Applicant is who borrows.

**T-08 · The trainer's test file uses fixtures it never defines.** `db_session` and `test_user`. We write them.

### From the Phase 1 contradiction sweep (2026-09-05)

**T-15 · Three different test folder layouts.** The Phase 1 doc says `tests/test_unit/` and `tests/test_api/`. The test spec's commands say `pytest tests/ -k "P1"`. The associate guide and the **reviewer guide** say `tests/phase1/`. The reviewer runs `pytest tests/phase1/`, so that is the one that counts.

**T-16 · The Phase 1 doc's folder listing has no `user.py`,** but its own auth code imports `app.models.user.User`. We create it.

**T-17 · The CORS port is wrong for us.** The doc allows only `http://localhost:3000`. Vite runs on **5173**. Get this wrong and React cannot reach the API at all. Allow 5173.

**T-18 · Bad filter value: spec says 400, FastAPI gives 422.** Not tested either way. Follow the user story: check it ourselves and return 400.

**T-19 · The applicant endpoints have no user story.** But the test fixture needs `POST /applicants`, and Phase 3 needs `GET /applicants/{id}`. Build both.

**T-20 · Test database: file, not in-memory.** The test spec's own setup uses a file, `test.db`. Follow it.

**T-21 · Request IDs can collide.** The doc builds them from the millisecond clock. Use a UUID.

**T-22 · `associate_id` is missing from the doc's middleware.** The observability guide requires it in every log line. Read it from the settings file.

**T-23 · Applicant signup creates two rows.** A `User` row to log in and an `Applicant` row as the borrower profile, linked. Manual Section 3 Step 1 confirms it.

**T-24 · Session expiry wording.** Manual says 24 hours of *inactivity*. A JWT expires 24 hours after *issue*. Reword the manual in Phase 2.

**T-25 · The manual describes file rules the system doesn't enforce.** PDF/JPG/PNG, 5MB max. Phase 1 stores only a filename. Becomes real when actual upload is added.

**T-26 · The manual promises things the system doesn't have.** Co-applicants and automated notifications. Build later or trim the manual in Phase 2. Both in `FUTURE-UPGRADES.md`.

### From working through the Phase 5 scoring

**T-13 · Rejecting on score alone is almost impossible.** Lowest possible score is 35. Reject is below 40. Only one combination reaches it: bad credit **and** unemployed **and** unaffordable EMI together. To demo a rejection, the applicant needs all three.

**T-14 · There are only two "medium" risks, and both are defined.** Medium credit risk is CIBIL 650 to 749. Medium employment risk is salaried under 2 years or self-employed. Nothing is undefined.

### From designing the dashboard (2026-09-06)

**T-38 · The trainer's five status colours cannot be used in a pie chart.** Ran them through a colour-accessibility validator against a white surface. Side by side as bars, only one pair is weak: green and red measure ΔE 5.0 apart for a viewer with red-green colour blindness, which a written label beside each bar fully mitigates. But in a pie or donut every colour sits against every other, and there the numbers collapse: **purple vs blue measure ΔE 0.4 under red-green colour blindness** (indistinguishable), and **red vs orange measure ΔE 8.7 with normal colour vision** (below the 15 floor — hard for anyone). So the pipeline chart is horizontal bars with written labels, never a pie. Loan type uses a single blue shade instead, because on that chart colour means quantity, not identity. Worth saying out loud in the demo if accessibility comes up.

**T-39 · Every date and time in the app was 5 hours 30 minutes early.** Found by Rohit on 2026-09-06, and it was real. SQLite records `CURRENT_TIMESTAMP` in **UTC** and hands it back as a plain date and time with nothing saying so — `DateTime(timezone=True)` does not change this, because SQLite has no timezone support. The API passed that straight out as `2026-09-05T20:13:55`, and a browser reads a string with no timezone marker as *the reader's own local time*. In India that showed the wrong day, in the evening instead of the small hours.

Fix: a shared `UtcDateTime` type in `schemas/common.py` that stamps naive database times as UTC on the way out, so the API now sends `2026-09-05T20:13:55Z`. The browser converts that to real local time, and the app is also correct for a reader in another country. Guarded by `tests/ours/test_timestamps.py`, including a test that the recorded time is actually within a minute of now.

**Watch for this again in Phase 2 onwards:** any new response field holding a time must use `UtcDateTime`, not `datetime`.

### From the mentor chats

**T-09 · Streamlit was overruled, but not replaced.** The Phase 2–4 tests check Streamlit; the demo runs React. Build both. Chat logic lives in the backend, both front-ends are thin screens.

**T-10 · The embedding trap, for Phase 2.** Gemini's embedding model and Ollama's `nomic-embed-text` both produce 768 numbers per chunk. ChromaDB accepts one against the other with **no error** and returns nonsense. Fix: one collection per provider.

### Environment

**T-27 · This laptop had no git, no Python, and no Node.** Found 2026-09-05, installed 2026-09-06: git 2.55, Python 3.11.9, Node 24.19 LTS. This is Rohit's personal laptop, so there are no restrictions on what can be installed.

**T-28 · The editor's shell still has the old PATH.** VS Code was open before the installs, so any shell it starts doesn't see the new tools until VS Code is restarted. Until then, every command I run starts by refreshing the PATH from the registry. Harmless, just noisy. Goes away on Rohit's next VS Code restart.

**T-29 · The project lives inside OneDrive.** Git and OneDrive can fight: OneDrive syncs the hidden `.git` folder while git is writing to it, and that occasionally corrupts the repository. For a solo project with GitHub as the backup, the risk is small and the fix is to re-clone. If it ever misbehaves, the cure is to either move the project out of OneDrive or tell OneDrive to skip this folder.

### From planning the domain rules (2026-09-06)

**T-32 · Phase 5 reads applicant facts that no table stores.** Employment length and existing loan payments. Raised as D-16.

### PowerShell

**T-34 · No double quotes inside git commit messages.** Windows PowerShell 5.1 mangles a double quote inside an argument to a native program like git, splitting the message into several arguments. The commit fails with a confusing "pathspec did not match" error, and any tag created in the same command lands on the wrong commit. Happened on Piece 7 and needed a tag deleted from GitHub. Rule: commit messages use single quotes or no quotes at all.

### In the trainer's sample code

**T-35 · The trainer's startup log line crashes.** `phase1-fullstack-crud.md` shows `logger.info("startup", event="database_initialized", ...)`. In structlog the first argument already *is* the event, so passing `event=` again raises "got multiple values for argument event" the moment the server starts. Copying that line verbatim means the app never boots. Ours logs `database_initialized` as the event name, which is what the observability checklist actually asks for.

**T-36 · The trainer's DB-02 test reads an id that does not exist yet.** It adds a `LoanApplication` to the session, then immediately builds a `StatusHistory` with `application_id=app.id`. But the row has not been saved, so `app.id` is still `None`, and the history row fails its not-null rule at commit. This would fail on *any* implementation. Our copy adds one `db_session.flush()` after the add, which saves the row and fills in the id. The associate guide allows adapting the skeleton; the reason is in a comment in the test.

**T-37 · pytest does not see `app` from `tests/phase1/`.** With the tests one folder down, pytest puts `tests/` on Python's path, not `backend/`, so `import app` fails. Fixed with `pythonpath = .` in `backend/pytest.ini`.

### Python itself

**T-33 · In Python 3.11, `str()` of a string-enum is not its value.** `str(ApplicationStatus.submitted)` gives `"ApplicationStatus.submitted"`, not `"submitted"`. The trainer's tests hand the rules enum members; the API hands them strings. Any helper that compares them must use `.value` when it's there. Caught while planning Piece 7; the rules file was using `str()` and would have failed UNIT-05. Fixed with a tiny `_v()` helper.

### Packages

**T-30 · passlib 1.7.4 breaks with bcrypt 4.1 or newer.** The trainer pins passlib but not bcrypt. Newer bcrypt removed something passlib reads at startup, so password hashing throws an error. Fix: pin `bcrypt==4.0.1` in `requirements.txt`. Done.

**T-31 · `EmailStr` needs an extra package.** Pydantic's email check, which test UNIT-02 relies on, needs `email-validator` installed separately. The trainer's list leaves it out. Added.

### Security

**T-11 · Never commit the environment file.** `.env` holds the Gemini key and the JWT signing secret. Commit `.env.example` with blank values instead.

**T-12 · The `Chats/` folder never goes to GitHub.** Real colleagues' names. Already in `.gitignore`. Repository stays private.

---

# Settled

### 2026-09-06 · D-17 — Charts on the dashboard
**Answer: horizontal bars, no pie chart.** Rohit asked for pie charts; the colour validator showed the trainer's five mandated status colours cannot carry a pie (purple vs blue ΔE 0.4 under red-green colour blindness, red vs orange ΔE 8.7 with normal vision — see T-38). Bars with the status name written beside each one are accessible and give a real answer if an ADH asks. Loan type uses a single blue shade, since colour there means quantity, not identity.

### 2026-09-06 · D-16 — Two more Applicant fields for Phase 5
**Answer: add both.** `years_with_employer` (decimal, 0.5 = six months) and `existing_monthly_emi` (rupees, default 0). Both optional so no test breaks. When missing, Phase 5 falls back to the trainer's assumptions. Employment length also lets us check the manual's rule of 6 months salaried / 2 years self-employed.

### 2026-09-05 · D-13 — The headline showcase feature
**Answer: the Manager's Morning Briefing.** The AI reads the whole pipeline and writes the manager a short summary: what is stuck, what is risky and why, what needs attention today. Apply-by-chatting and policy what-if go to `FUTURE-UPGRADES.md`. This also closes D-08.

### 2026-09-05 · D-14 — EMI percentage for personal and auto loans
**Answer: 50% for all three loan types.** Matches the manual's home rule and the most common bank practice. The fuller bank data, including the income-tiered version, is in `LEARNING-NOTES.md`. One line gets added to manual Section 5 in Phase 2.

### 2026-09-05 · D-15 — Building teammates' features
**Answer: fine to build.** Rohit has talked it through with the team. Draft saving and OCR stay in `FUTURE-UPGRADES.md` and get built after the headline feature and Phase 5. Draft saving will be planned properly when we reach it; the one fixed rule is that drafts live on the server, not in the browser (Rule 13).

### 2026-09-05 · D-07 — Who registers as what
**Answer: Option A.** The normal `/auth/register` address creates bank staff, defaulting to loan officer. Customers sign up through `/auth/register-applicant`, which creates both a login and a borrower profile (T-23). Managers are seeded, never self-registered.

### 2026-09-05 · D-11 — The activity log
**Answer: build it, in Phase 1, small.** Curated business events only. Every row records who acted: a human by email and role, or an AI by which agent it was and which user it was acting for.

### 2026-09-05 · D-10 — Phase 5 risk threshold
**Answer: approve only above 70.**
```
APPROVE            score > 70  AND compliance passed AND EMI affordable
REJECT             score < 40  OR  compliance failed in a way that can't be fixed
REQUEST_MORE_INFO  everything else
```

### 2026-09-05 · D-01 — EMI affordability
**Answer: advisory, not blocking, for all three loan types.** A `check-eligibility` endpoint the form calls before submitting. Blocking would fail `TC-01-P1-API-03`.

### 2026-09-05 · D-02 — Tenure limits per loan type
**Answer: yes.** Personal 12–60, home 12–360, auto 12–84. Verified against all 20 tests.

### 2026-09-05 · D-03 — Home loan maximum
**Answer: ₹1 crore.** Per-type caps: personal ₹25,00,000, auto ₹50,00,000, home ₹1,00,00,000. The trainer's ₹5 crore in Phase 5 is a real setting, not a test value, and no Phase 5 test goes near it.

### 2026-09-05 · D-04 — Vehicle quotation
**Answer: add it.** Sixth allowed document type, required for auto loans in Phase 5.

### 2026-09-05 · D-05 — Date of birth
**Answer: yes, add it.** Nullable column on Applicant. Missing date treated as eligible.

### 2026-09-05 · D-06 — Role-based access
**Answer: yes.** Only `approved → disbursed` is gated behind manager.

### 2026-09-05 · Folder layout
**Answer: approved as written in `BUILD-PLAN.md`.**

### 2026-09-03 · Backend stack
**Answer: Python + FastAPI.**

### 2026-09-03 · Second front-end
**Answer: Streamlit now, Angular considered after Phase 5.**
