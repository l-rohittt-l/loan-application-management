# Run report — the unattended build, 2026-09-06 to 2026-09-07

You were away. The job was to finish everything that was left: Piece 19, then Phase 3, Phase 4, Phase 5, the headline feature, and this report. This is what happened, what I decided on your behalf, and what I would not want you to find out later from someone else.

**Short version: all five phases pass every test, none skipped, and the headline feature is built.** Three things found along the way would have embarrassed us in front of an Account Delivery Head, and none of them were visible in the code or in a green test summary. They are in "What worries me" below, and they are the part of this report worth reading twice.

---

## Where the scores landed

| Phase | What it is | Passed | Skipped | Total | Cleared 70%? |
|---|---|---|---|---|---|
| 1 | REST API, React and Streamlit front-ends | 20 | 0 | 20 | Yes — 100% |
| 2 | RAG chatbot reading the user manual | 20 | 0 | 20 | Yes — 100%, **re-confirmed 2026-09-08** |
| 3 | Agent with five tools reading live data | 20 | 0 | 20 | Yes — 100% |
| 4 | MCP server and the staff chat interface | 25 | 0 | 25 | Yes — 100% |
| 5 | Four-agent underwriting review | 25 | 0 | 25 | Yes — 100% |

> ### Phase 2 was doubted, then cleared — 2026-09-08
>
> The last verification run of 2026-09-07, after the Gemini daily quota had run out, came back **9 failed, 60 passed**, three of them in `tests/phase2/test_observability.py` with the error text truncated. That was enough to stop trusting the row above, and this report said so rather than claiming a clean sweep.
>
> **A separate session re-ran it the next day, after the quota reset: 22 of 22, three times over, with no code changed in between.** So the failures were the exhausted quota and nothing else.
>
> Worth noting how that was proved, because it is the better method: there was no `RESOURCE_EXHAUSTED` error to read, because once the quota reset **there were no failures left at all**. Three clean runs against unchanged code is stronger evidence than one error string would have been.
>
> A bonus from the same run: the two LangSmith observability tests now **pass** rather than skip, which confirms the API key is properly wired (T-68).

Those are the trainer's own test counts. The suites actually run more than that, because we wrote extra tests of our own and because four Phase 1 cases are parametrised:

| Suite | Tests it runs |
|---|---|
| `tests/phase1` | 27 |
| `tests/phase2` | 22 |
| `tests/phase3` | 23 |
| `tests/phase4` | 25 |
| `tests/phase5` | 25 |
| `tests/ours` | 20 |
| **Total** | **142** |

**Verified as one command on 2026-09-08:** `pytest tests/` from `backend/` gives **142 passed, 0 failed, 0 skipped** in 9 minutes 34 seconds, with the backend running. That is the whole project checked the way a reviewer would check it — and it was the first time it had ever been possible, because until that day the command aborted during collection (T-72, below).

**Weighted total: 100 out of 100.** Phase weights from the blueprint are 15, 20, 20, 25 and 20. Rank depends on how many phases clear 70%, and all five do.

**On skipped tests.** Every number above is passed-plus-skipped against the total, because a skipped test reads exactly like a passing one in a summary line — that is how two of Phase 2's tests hid for days in an earlier session. There are no skips anywhere now.

---

## What got built, phase by phase

### Piece 19 — automatic eligibility, and a permanent record (tag `v0.2.3`)

The last outstanding piece of the Phase 1 polish, and the one you asked for personally.

The eligibility check no longer waits for a button. Once the applicant, loan type, amount and tenure are all valid, it fires on its own 600ms after you stop typing. The panel beside the form became a proper assessment card showing **every rule as a passed or failed row**, not only the failures — seven green rows and one red one is far more convincing than one line of red text. Submitting an application that fails now opens a real decision dialog: what failed, what it means, and two clear choices.

The backend half is the part that matters. **The server now runs its own eligibility assessment the moment an application is created and stores it permanently** — three new columns on `loan_applications`. Not the browser's copy: the server's own, so it cannot be skipped or faked by anything calling the API directly. Every application now carries a permanent record of what the bank knew and what its rules said at that moment, which Phase 5 and the morning briefing both read.

I drove it in a real browser as the loan officer, reproduced Priya Sharma's example from the plan, watched the check fire on its own, watched the "not eligible" dialog appear, submitted anyway, and read the stored note back on the application page. It matched the plan almost word for word.

### Phase 3 — the tests that had never been run (tag `v0.3.0`)

`agent/` and `tests/phase3/` both existed from an earlier session, but nobody had ever run `pytest tests/phase3`. Nobody knew whether Phase 3 worked.

It did. Three failures on the first run were all bugs in the tests, not the agent:

- Our own test checking every tool description says "do not use" tripped over the description wrapping onto two lines.
- **The trainer's own status-query test checks for the literal enum spelling `under_review`, with the underscore** — but a correctly working agent answers in English, "is currently under review", with a space. Same class of bug as T-36 in Phase 1: their test would fail against any implementation doing what the phase asks. Our copy accepts either spelling with the reason written next to it (T-61).
- The LangSmith trace test failed because the very first trace that project ever received had to create the project server-side first, which takes longer than the fixed three-second sleep (T-62).

I ran the agent by hand before touching any test, so the fix is based on what it actually said rather than a guess.

### Phase 4 — MCP server and staff chat (tag `v0.4.0`)

Built from nothing. `mcp_server/mcp_app.py` exposes six tools over the Model Context Protocol; `mcp_server/chat_interface.py` wraps them for a LangChain agent and provides the Streamlit chat screen where staff manage applications by typing sentences.

Both avoid the two bugs already documented in `AI-BUILD-LOG.md` from reading the trainer's reference code: a static token from `.env` that expires 24 hours after issue, most likely mid-demo, and an HTTP helper that raises on any error that isn't a 404, ending a conversation with a stack trace. Everything goes through the shared `loan_api_client` that mints a fresh token per call and never raises.

### Phase 5 — the four-agent underwriting review (tag `v0.5.0`)

Built from nothing. A LangGraph pipeline: data collector, risk assessor, compliance checker, decision maker, with one conditional edge that stops the graph if the application could not be fetched.

**The design decision here is the one I most want you to review — it is D-19 below.** The trainer's reference has the LLM calculate the debt-to-income ratio, the EMI and the risk score itself and return JSON; their own tips table then admits the consequence ("JSON parsing fails in Risk Assessor... have fallback values"). Every number in our version is computed in plain Python from the same `domain/rules.py` thresholds Phase 1 already uses. The LLM writes only the prose a human reads.

It also fixes the third bug from `AI-BUILD-LOG.md`: the trainer's compliance skeleton contains `age_eligible = applicant.get("credit_score") is not None or True`, which always evaluates true and inspects a credit score rather than an age. Ours does a real age check against `AGE_LIMITS`, including the rule that a home loan must be repaid before 70.

### The Manager's Morning Briefing (tag `v1.0.0`)

The headline feature, settled as D-13 back on 2026-09-05. Not a trainer requirement — the thing that makes the demo memorable rather than merely complete.

The manager opens the app and the AI has already read the whole pipeline: what is stuck and for how long, what is held up by missing documents, what failed the bank's own eligibility check at submission and is somehow still open, and what is approved but not yet paid out. A card at the top of the manager's dashboard, with a **"how this was worked out" panel** that opens the actual numbers behind every sentence, so nothing is a black box.

Same discipline as Phase 5: every figure is counted from the database before the AI is asked anything. When the AI is unavailable it shows the plain figures and **says so on screen** rather than degrading silently.

It uses every phase at once — Phase 1's data, Piece 19's stored eligibility, Phase 5's view of risk — and it answers the question an ADH actually asks, which is not "does it have a chatbot" but "what does this change on Monday morning".

---

## Decisions I made on your behalf

All four are written up in `TRAPS-AND-DECISIONS.md` under "Needs your call", with the reasoning. You can overturn any of them.

| ID | The decision | Why it might matter to you |
|---|---|---|
| **D-19** | **Phase 5's LLM writes the prose; plain Python computes every number.** | The one I would most want you to look at, because it is a deliberate departure from the trainer's design. It makes decisions repeatable, auditable and explainable in a walkthrough, and means a rate limit can never change a lending decision. |
| **D-18** | Three new columns added to the existing SQLite database with a small `ALTER TABLE` step in `init_db()`, rather than adding Alembic. | Right for a POC's SQLite file. I would not recommend it for a production system where several people deploy against one database. |
| D-09 | Still open, unchanged — Angular as a third front-end. | Was already open before this run. Revisit after the demo. |
| D-12 | Still parked, unchanged — hosting. | Decide before the demo, not now. |

---

## What worries me

Three things, in the order I would fix them.

### 1. The AI runs on a quota that this run exhausted

The Gemini free tier is **500 requests a day**, not just the 5-a-minute limit we already knew about (T-55). This run used them up, and near the end the morning briefing could only show its plain-figures fallback. Nothing broke — every AI feature degrades and says so — but the AI narrative could not be demonstrated live.

Phases 2 through 5 together make well over a hundred LLM calls per full test run. **Two or three full test runs in one day exhausts the day's quota.**

What to do, in order of preference:

1. **Do not run the full test suite on demo day.** Run it the day before. The demo itself costs a handful of calls.
2. **Get a paid Gemini key** if this demo matters. It is inexpensive and it is the real fix.
3. **Install Ollama** as the local fallback the project already supports. I checked — it is **not installed on this laptop**, so that fallback is currently theoretical rather than available.

You raised automatic provider switching after seeing this. It is written up in `FUTURE-UPGRADES.md` with the open questions, parked for discussion.

### 2. The test suites were writing into your demo database

This is the one that would have cost you the demo, and it was completely invisible.

Phases 3, 4 and 5 talk to the Phase 1 API over HTTP. That fixture reuses whatever server is already running — which is the real one, on the real `loan_app.db`. So every test that submits an application left a real row behind. One full test run had left **60 applications** named things like "Phase 5 underwriting fixture" and "MCP test application" sitting in the manager's pipeline. The dashboard showed 68 open applications, nearly all junk. That would have been the first screen an Account Delivery Head saw.

Cleaned up, and there is now `backend/clean_test_data.py`, which deletes only rows matching known test-fixture names and never anything a person typed. **Run it before any demo.**

The deeper fix — pointing those phases at their own database — I deliberately did not attempt this late in the run, because the fixture reuses an already-running server, so it only helps someone who remembers to stop theirs first. Written up as T-65 and listed below as the next thing worth doing.

### 3. A defensive fallback hid a real bug for a whole phase

Both Phase 5 agents that call an LLM wrap the call in a try/except with a deterministic fallback. Good design — except that Gemini returns `response.content` as a **list of content blocks**, not a string, so `.strip()` raised on every single call. Nothing crashed, every test passed, and the pipeline quietly used the plain fallback sentence every time instead of the LLM's writing. It was working, but not doing what it looked like it was doing.

Found only by reading the warning lines in the log. Fixed (T-64). The lesson worth keeping: **log the reason on every fallback path**, because a silent fallback hides a bug indefinitely.

---

## Things I am less sure about

Honest uncertainty, not known faults.

- **The briefing card has now been seen — and looking at it found a bug, as predicted.** Rohit opened it on 2026-09-08. The layout holds, the three paragraphs read well, the four stats sit correctly, and the "Written by AI" pill confirmed the AI narrative working live for the first time. The writing was genuinely good: it named application #1 as most critical with three specific reasons and recommended a concrete first action.

  **But "How this was worked out" was rendering as plain text rather than a button** — ghost styling with no border or background, standing alone under a divider with no neighbouring buttons to make it look pressable. The panel it opens is the entire trust story of the feature, and nothing told a manager it could be clicked. Fixed as a proper disclosure control with a rotating chevron (T-73).

  That is now **twice** this project has shipped a control invisible to code review, to a clean build and to a green test suite, and caught only by a person looking at a rendered page (T-42 was the first). It is the strongest argument in this report for looking at screens.

- **The Phase 4 chat screen still has not been seen.** One screen left. Its behaviour is proven — driven end to end, the quick-action button returns a real AI answer — but layout and readability are unverified.

  What *has* been checked, on 2026-09-08: the briefing endpoint returns a real narrative, eight headline numbers and three populated tables, and `MorningBriefing.jsx` consumes exactly those fields with no mismatch. The Streamlit chat was driven end to end with Streamlit's own `AppTest` — the title renders, the session ID shows, there are exactly four quick-action buttons, and clicking one returns a genuine AI answer naming real applications, with no exceptions raised. That last check matters most, because the dead quick-action button was a real bug that no unit test caught.

  What is **still unverified: layout, overlap, and readability on both screens.** Data and behaviour are proven; appearance is not. Phase 1 already taught this project that its worst bug was invisible to code review, to a clean build and to a green test suite, and was only ever found by looking at a screenshot (T-42). Ten minutes with a browser closes this.
- **The briefing's AI narrative has been seen working, but not in the finished card.** The endpoint produces real prose and the fallback is verified, but the AI-written version has not been viewed inside the rendered dashboard card. Same ten minutes as above.
- **The Streamlit chat interface has had less use than the React app.** It passes its tests and I drove it end to end, but the React front-end is the one that gets demoed and the one that has been inspected hardest.
- **The `sample_application_id` fixtures create real data every run.** That is what caused problem 2 above. The cleanup script handles it, but it will keep happening every time the suite runs.

---

## What I would do next

In this order:

1. **Look at the Phase 4 chat screen** — the one screen still unseen. The briefing card was checked on 2026-09-08 and that immediately found a real bug (T-73), which is the argument for doing the same here. Start it with `streamlit run mcp_server/chat_interface.py --server.port 8502` from `backend/`.
2. **Review D-19**, the Phase 5 numbers decision. It is defensible and I would argue for it in a walkthrough, but it is a departure from the trainer's design and you should agree with it before a mentor asks.
3. **Practise the five-minute demo** against clean seed data, and pick which of the five phases you actually show. All five work; five minutes is not enough for all five.
4. **Fix T-65 properly** — give the Phase 3/4/5 tests their own database instead of relying on a cleanup script and a good memory.
5. **Have the provider-switching discussion** when you want it. Parked in `FUTURE-UPGRADES.md` with the open questions.

**Found and fixed on 2026-09-08, after a sweep for anything still broken:**

- **`pytest tests/` — the command a reviewer types first — did not work at all.** Every phase passed individually, but running them together aborted during collection, before a single test ran, because Phase 3 and Phase 5 both have a `test_e2e.py` and three test folders were missing an `__init__.py`. Fixed; all 142 tests now collect and run in one command (T-72). This is the most valuable thing found today, because it would have been the grader's first impression.
- **The README documented only Phase 1.** It still said "Phase 1 status: complete" and gave no way to run the Phase 4 chat interface or the Phase 5 review. Rewritten to cover all five phases, with every command verified by running it.
- **A third model value nobody had noticed.** `.env` said `gemini-3.5-flash-lite` but `config.py`'s fallback default said `gemini-3.8-flash` — so a fresh clone, before anyone fills in `.env`, would have silently run a model that was never chosen and never rate-limit tested. All three sources now agree (T-69).
- **Lint and dead-import sweep**, the first since the build. Found a ternary used as a statement in Piece 19's code, which works but reads badly and would be awkward in a walkthrough, and seven dead imports. Cleaned up.

**Done since this report was first written, on 2026-09-08:**

- ~~Confirm Phase 2~~ — done, 22 of 22, three runs, quota was the only culprit.
- ~~Regenerate the Phase 1 and 2 results files~~ — done, all five are now in `results/`.
- ~~Decide the AI quota question~~ — **decided: don't install Ollama before the demo.** Roughly 3GB and 10-20 minutes, installs on Windows without fuss, but noticeably slower without a strong GPU and might fail Phase 2's own latency test. The quota is 500 a day and a full test run spends a few dozen, so the real protection is simply not running the whole suite on demo morning. Installing an untested fallback days before a demo adds a failure mode rather than removing one.

---

## Where things stand in git

Every piece is committed and tagged, and every commit is a state the app runs in.

| Tag | What it is |
|---|---|
| `v0.2.3` | Piece 19 — automatic eligibility and the stored summary |
| `v0.3.0` | Phase 3 verified — 23 of 23 |
| `v0.4.0` | Phase 4 — MCP server and staff chat, 25 of 25 |
| `v0.5.0` | Phase 5 — the four-agent review, 25 of 25 |
| `v1.0.0` | The Manager's Morning Briefing — demo-ready |

There is also one commit that is not a feature and matters more than it looks: **`requirements.txt` had been Phase 1 only since Phase 2 started.** Every AI package had been installed by hand into one venv and never written down, so a clean checkout would have built a Phase-1-only environment and every later phase would have failed on its first import line — on a reviewer's machine, not yours. Rewritten from the real environment and validated by installing into a brand new venv (T-63).

---

## The files that carry the detail

- `PROGRESS-LOG.md` — sessions 33 to 37, one entry per piece, newest first
- `TRAPS-AND-DECISIONS.md` — the four open decisions, and traps T-61 through T-66 from this run
- `BUILD-PLAN.md` — the plan for each piece, written before it was built
- `AI-BUILD-LOG.md` — the three bugs in the trainer's own reference code, and what was done instead
- `MY_SCORES.md` — the score tracker
- `FUTURE-UPGRADES.md` — including the provider-switching idea you raised, with the open questions
