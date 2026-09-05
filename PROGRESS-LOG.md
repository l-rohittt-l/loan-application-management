# Progress log

Newest entries at the top. Short on purpose.

---

## What I've read so far

- [x] `01-POC-BLUEPRINT.md` — Parts 1 to 6, the whole Phase 1 contract
- [x] `01` — Part 13, the contradictions
- [x] `02` — Part 1, Change 10, the review punch list
- [ ] `TRAPS-AND-DECISIONS.md` — 4 items need answers: D-12, D-13, D-14, D-15 ← **next**
- [ ] `BUILD-PLAN.md` — Piece 0, the install commands ← **next**
- [ ] `02-GROUND-TRUTH-SHIFTS.md` — the rest. Part 3 needed before Phase 2 starts.
- [ ] `03-THE-FLOW-WHAT-HAPPENED.md`

---

## Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-09-03 | Backend is **Python + FastAPI**, not Java | The 20 test skeletons hardcode Python import paths, and Phases 2-5 are Python-only. Java would mean building everything twice. |
| 2026-09-03 | Second front-end is **Streamlit** | Phase 2-4 test specs check Streamlit behaviour, so it gets built anyway. Costs about an hour instead of days. |
| 2026-09-03 | **Angular deferred** until after Phase 5 is demo-ready | Better career skill, wrong timing. Phases 4 and 5 are worth 45% combined and almost nobody in the cohort finished Phase 5. |
| 2026-09-03 | AI instructions live in **`CLAUDE.md` only** | No Copilot licence yet. |
| 2026-09-03 | Work in a **read → explain → build loop**, one component at a time | Reading 900 lines up front doesn't stick. |
| 2026-09-05 | **Cautious upgrade** — improve only by adding, never by changing what already works | Base requirements are what get graded. Additions must not break them. |
| 2026-09-05 | **One iteration at a time** — plan it, build it properly, then plan the next | Backend, React, Streamlit, activity log are separate pieces of work. |
| 2026-09-05 | **Validate every user input**, not just the fields the spec names | The spec names a handful. Real applications validate everything. |
| 2026-09-05 | Use **git and GitHub**, private repo, commit after every piece, tag each phase | Version control, and a real commit history is evidence of real work. |
| 2026-09-05 | Logins follow **Option A**: normal register creates staff, separate applicant signup | The trainer's test registers "Test Officer" and immediately changes a status. |
| 2026-09-05 | Ideas beyond the trainer's requirements go to **`FUTURE-UPGRADES.md`**, built after the base | Scope control. Phase 5 needs protecting. |
| 2026-09-05 | **Customer data is stored on the server**, never in the browser | Rohit's security point on draft saving. Now Rule 13. |
| 2026-09-05 | **The manual and the code must agree** — change one, change the other | The chatbot quotes the manual. Now Rule 12. |

---

## The log

## 2026-09-06 — Session 12: Piece 4, the input-checking layer

**Asked for:** keep going.
**Built:** the schemas, six files under `app/schemas/`. Every field that accepts user input is now checked: name shape, Indian mobile format, password strength, email, credit score range, income, date of birth not in the future, file names limited to PDF/JPG/PNG with no folder tricks, and the trainer's amount and tenure bounds. A smoke test mirroring the trainer's UNIT-02, 04, 07 and 08 passes, plus eight of our own stricter checks.
**Found:** nothing new.
**Realised:** the per-loan-type limits belong in the service layer, not the schema, so the trainer's UNIT-04 keeps passing exactly as written and the eligibility check can explain *why* something is over the limit.
**Next:** Piece 5, auth. Plan written.

---

## 2026-09-06 — Session 11: Piece 3, the six tables

**Asked for:** keep going without waiting for approval on each piece, since Rohit needs time to learn the tech before he can suggest changes. Also: can every push carry a version number?
**Built:** `config.py` (reads the settings file), `database.py` (the connection, with foreign-key checking deliberately off), and the six table models. A smoke test that copies the trainer's four database tests passes, including the cascade delete and the row that points at a missing applicant.
**Found:** nothing new in the code. In the writing, Rohit found very short sentences *harder* to read, not easier, so Rule 7 now says natural sentences.
**Realised:** version tags per piece are cheap and give Rohit a number to point at. Scheme: `v0.0.N` for Phase 1 piece N, `v0.1.0` when Phase 1 passes, then `v0.1.N` for Phase 2 pieces, and so on. Rule 11 updated.
**Next:** Piece 4, the schemas. Plan written.

---

## 2026-09-06 — Session 10: Piece 2, the rules file

**Asked for:** add the two missing applicant fields (job length, existing EMIs) and build Piece 2.
**Built:** `app/domain/rules.py`. Every loan rule as plain Python: allowed values, the status machine, amount and tenure limits per loan type, eligibility numbers, required documents, the 50% EMI rule, employment minimums, and the Phase 5 scoring bands. Six small helper functions. Imports nothing from the app, so any phase can use it.
**Found:** nothing new. Every rule already had a settled source.
**Realised:** Rohit is happy with the one-thing-at-a-time pace.
**Next:** Piece 3, the database connection and the six tables. Plan is written; waiting for a go.

---

## 2026-09-06 — Session 9: Piece 1, the skeleton

**Asked for:** go ahead with Piece 1, and only raise parked questions when a piece actually needs them.
**Built:** the `backend/` folder with the `app/` package, a virtual environment on Python 3.11.9, `requirements.txt` at the trainer's versions, `.env` with a real generated secret, and `.env.example` for GitHub. All packages installed and importing.
**Found:** two gaps in the trainer's package list. `passlib` breaks with newer `bcrypt`, so bcrypt is pinned to 4.0.1. And Pydantic's email check needs `email-validator`, which the trainer never lists but test UNIT-02 depends on. Both in the traps file.
**Realised:** nothing new. This piece was groundwork.
**Next:** Piece 2, the domain rules file. Every loan rule in one place.

---

## 2026-09-05 — Session 8: Slowing down to one thing at a time

**Asked for:** stop doing ten things per reply. One problem, one answer, then move on. Also a notes file for domain facts worth re-reading.
**Built:** `LEARNING-NOTES.md` with the bank EMI rules. Two new rules in `CLAUDE.md`: one thing per reply, and keep the learning notes. Settled the headline feature (Manager's Morning Briefing), the EMI percentage (50% everywhere), and the folder layout. Installed git, Python 3.11 and Node 24. Started the git repository, made the first commit, and pushed it to a private GitHub repository. **Piece 0 done.**
**Found:** the restriction confusion was mine. This is Rohit's personal laptop with no limits. The Wipro laptop is the restricted one and nothing gets built there. Also: the editor's shell won't see the new tools until VS Code restarts, so I refresh the PATH at the start of each command for now.
**Realised:** Rohit isn't reading the reading lists. From now on I walk him through one item at a time and ask before moving on.
**Next:** Piece 1, the project skeleton.

---

## 2026-09-05 — Session 7: The Phase 1 sweep, and the laptop has no tools

**Asked for:** real bank numbers for the EMI rule on personal and auto loans, a file for ideas to build later, git set up now, the Phase 1 contradiction sweep, and answers on five features.
**Built:** `FUTURE-UPGRADES.md`, a `.gitignore`, four new rules in `CLAUDE.md` (catch ideas for later, git after every piece, manual and code must agree, customer data never in the browser). Settled D-07 as Option A. The sweep found twelve more things, T-15 to T-26, including the wrong CORS port and three different test folder layouts across the trainer's own documents.
**Found:** this laptop has no git, no Python, and no Node. Nothing can be built until they're installed. winget is available so it's three commands.
**Realised:** Rohit said yes to five features on top of the base. That's too many with Phase 5 to protect, so it went back as a question: pick one headline.
**Next:** Rohit runs the three install commands and creates the GitHub repository. Then Piece 1.

---

## 2026-09-05 — Session 6: The folder layout, and three more decisions settled

**Asked for:** whether the trainer defined the smaller risk deductions, how the activity log records later phases "automatically", and to see the project folder structure before any code.
**Built:** the full folder layout for all five phases, written into `BUILD-PLAN.md`. Settled D-01 (EMI warning on all three loan types) and D-10 (approve above 70).
**Found:** the folder names are decided for us. The trainer's tests import `app`, `rag`, `agent`, `mcp_server` and `multi_agent` as top-level names, so all five must sit side by side or the imports break. Also found that rejecting a loan on score alone is nearly impossible with the trainer's numbers — only one combination out of eighteen can do it.
**Realised:** the activity log deserves to be a proper piece with its own table, so Phase 1 has six tables, not five.
**Next:** confirm the folder layout, decide D-07 (how staff and applicants log in), then build Piece 1.

---

## 2026-09-05 — Session 5: Simpler explanations, and a shared build plan

**Asked for:** simpler English, an answer on whether the trainer's ₹5 crore was a test value, and a way to see the small details instead of approving finished work.
**Built:** `BUILD-PLAN.md`, where each piece gets planned before it is built. Three new rules in `CLAUDE.md`: write simply, always end by saying what to read next, plan each piece before building it. Settled the vehicle quotation and the activity log.
**Found:** the ₹5 crore is a real setting in the Phase 5 code, not a test value. No Phase 5 test goes near it, so lowering home loans to ₹1 crore breaks nothing.
**Realised:** Rohit wants to co-build, not review. So Phase 1's backend gets split into 13 small pieces, planned one at a time.
**Next:** answer the 5 remaining open questions, then plan Piece 1, the project skeleton.

---

## 2026-09-05 — Session 4: Reading the Phase 1 contract, and settling four contradictions

**Asked for:** exact line numbers to read, then answers on the seven contradictions, plus advice on an activity-log idea and how to set up git.
**Built:** no code. Four contradictions settled (D-02 tenure per type, D-03 loan cap at ₹1 crore, D-05 add date of birth, D-06 role checks). Added three new working rules to `CLAUDE.md`.
**Found:** the risk threshold question has a right answer, not a preference — only "greater than 70" makes the trainer's own required demo scenario work. Also that the activity-log idea doesn't conflict with the POC, but Koushik already rejected audit logs as a showcase feature, so it can't be the differentiator.
**Realised:** improvements should be additive only — named it "cautious upgrade". Also that each piece (backend, React, Streamlit, activity log) should be planned and built in its own iteration.
**Next:** a full contradiction sweep of Phase 1 specifically, before the domain rules file gets written. Then git setup, then the project skeleton.

---

## 2026-09-03 — Session 3: Planning Phase 1

**Asked for:** a plan before writing any code, plus a way to remember things across chat sessions.
**Built:** `CLAUDE.md`, this log, and `TRAPS-AND-DECISIONS.md`. No code yet, on purpose.
**Found:** the Phase 1 test file hardcodes Python module paths and function names, so the stack choice was effectively already made. Also found 4 traps that fail tests silently, and one test that breaks if we enforce the EMI affordability rule.
**Realised:** reading the whole blueprint in one go doesn't stick, so we switched to reading one short section then building that piece.
**Next:** read the three short sections listed above, answer the 9 open items, then start the project skeleton.

---

## 2026-09-03 — Session 2: Making sense of everything

**Asked for:** read the trainer's POC folder and the exported Teams chats, then write down what we were meant to build, what changed, and what happened.
**Built:** three reference documents — `01-POC-BLUEPRINT.md` (the spec), `02-GROUND-TRUTH-SHIFTS.md` (what changed in real life), `03-THE-FLOW-WHAT-HAPPENED.md` (the story in order).
**Found:** the trainer's own documents contradict each other in seven places. Also that Gemini was blocked by the company network for weeks so the cohort moved to Ollama, and that the goal quietly shifted from passing tests to giving a good demo.
**Realised:** the first version was written in a heavy "master and disciple" style that got in the way, so it was rewritten in plain words with a glossary.
**Next:** plan Phase 1 before building anything.

---

## 2026-09-03 (earlier) — Session 1: Getting the raw material together

**Asked for:** nothing from Claude yet. This was manual work.
**Built:** exported the program's Teams conversations into text files in `Chats/` — 9 files covering 19 June to 20 August, including the AI-generated meeting notes.
**Found:** the POC pack from the trainer, `POC-01-Loan-Application-Management/`, with 17 documents covering all five phases.
**Realised:** there was too much scattered material to hold in my head, and it needed to be compiled into something readable.
**Next:** hand both folders to Claude and have it work out what's going on.
