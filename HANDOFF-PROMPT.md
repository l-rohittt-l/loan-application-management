# Prompt to paste into a new session

Copy everything below the horizontal line into a fresh Claude Code chat.

Suggested settings: **Opus, high effort.** This is real design and code work across backend and front-end, not mechanical checking.

---

I'm Rohit Sawant, building POC-01, a Loan Application Management System, for Wipro's Agentic AI Readiness Program. The project is at `C:\Users\Sawan\OneDrive\Desktop 1\FINAL_CHANCE`.

**Read these first, in this order:**

1. `CLAUDE.md` — how I work. Rules 7, 9, 11, 14 and 17 matter most.
2. `BUILD-PLAN.md` — go to the section **"PIECE 22 — One assistant in React that gets smarter, with role-gated tools"**. That is the job. The full plan is already written; you are continuing it, not designing it.
3. `TRAPS-AND-DECISIONS.md` — the whole thing. Every trap in there cost real time to find once already. T-75 is the one this piece is built on.
4. `PROGRESS-LOG.md` — the top few entries, for where things stand.

## Where the project is

All five phases are built and passing. `pytest tests/` from `backend/` gives **142 passed, 0 failed, 0 skipped** (takes about 10 minutes; it makes real AI calls). Tagged `v1.0.0`. The working tree is clean and the last commit is `2260e94`.

## What Piece 22 is, and why

I noticed a problem and pushed back on it. Phases 3, 4 and 5 were built as separate things — Phase 3 reachable only from a Python prompt, Phase 4 as its own Streamlit page. But the React **Assistant** page, which is the screen customers actually use and the one in the demo, still only had Phase 2's brain (answering from the user manual).

So the smartest parts of the product were invisible in the product.

**My instruction:** every phase should build *on top of* the Phase 2 chatbot, in the same chat window. One assistant that got smarter three times, not three separate chat screens that each know different things.

**The priority is getting the trainer's Phase 3, 4 and 5 functions working in the React app.** Other things were parked to make room — they are listed in `FUTURE-UPGRADES.md` under "Parked while Piece 22 puts Phases 3-5 into the React chat". Do not pick those up.

## The safety rule, which matters more than the feature

**Customers must only ever see the manual and their own applications.** Never anyone else's data, and never the ability to change anything. Bank staff can read everything. Officers get everything except paying money out. Managers get everything.

Step 1 of this piece is **already done and committed** — that is commit `2260e94`. It closed a real hole: the AI used to call the loan API as a branch manager no matter who was asking, so wiring it into the customer chat unchanged would have shown one customer another customer's loan.

The fix is `acting_as(email, role)` in `backend/app/services/loan_api_client.py`. Every API call inside that block happens **as the person who asked**, so Phase 1's existing owner-scoping does the work — no new permission system. Six tests in `backend/tests/ours/test_agent_acts_as_caller.py` guard it, including one proving end to end that a customer gets a 403 on someone else's application.

**Use `acting_as()` around every agent call you wire up. Do not bypass it.**

## What is left — steps 2 to 5

These are written out in `BUILD-PLAN.md`; this is the summary.

**Step 2 — route the chat to the Phase 3 agent.** `backend/app/routers/chat.py` currently calls the Phase 2 RAG chain directly (line 74, `from rag.rag_chain import answer_question, get_chain`) and always returns `mode="rag"`. Change it to call the agent instead — `build_agent()` and `run_agent()` in `backend/agent/agent.py` — wrapped in `acting_as()`. Policy questions still reach the manual, because `search_loan_policy` is one of the agent's five tools. `mode` becomes `"agent"`, and the response should carry which tools ran.

`ChatResponse` in `backend/app/schemas/chat.py` has `answer`, `mode`, `sources`, `duration_ms`. It already anticipates this: its comment says *"Phase 3 adds 'agent', Phase 5 adds 'review'"*.

**Step 3 — the screen.** `frontend/src/pages/Assistant.jsx` should show which tools were used for each answer, the way Phase 4's Streamlit chat already does. Sources still show for manual-based answers.

**Step 4 — Phase 4's action tools, staff only.** Tools that change data appear only for staff. A destructive instruction must restate what it will do and ask before acting — match the confirmation dialogs already used on the application detail page and in Piece 19's form.

**Step 5 — Phase 5 in the chat.** "Assess application 7" runs the four-agent underwriting review and shows the verdict with its reasoning.

## How I need you to work

- **One step at a time.** Build step 2, show me, commit it, stop. Do not chain into step 3 on your own.
- **Keep every existing test green.** After each step, at minimum run `pytest tests/phase1 tests/ours -q` from `backend/`. Before saying a step is finished, run the phase suites it touches. 142 passing is the baseline and it must not drop.
- **Commit after each step** with a plain-words message, per Rule 11.
- **Explain in plain words, not jargon.** I have three years of Java and I am new to Python. If you use a technical term, gloss it. I have told a previous session it was bad at explaining — short sentences, say the concrete thing, do not make me read four paragraphs to find the point.
- **Tell me what to click to check your work.** After each step, tell me exactly where to navigate and what I should see.
- Update `PROGRESS-LOG.md` and `TRAPS-AND-DECISIONS.md` as you go, per Rules 1 and 2. Do not narrate that beyond one line.

## Two practical things

**The AI has a daily quota.** Google's free tier is 500 requests a day, and a full test run spends a few dozen. If AI answers suddenly stop, that is the quota, not your code — every AI feature degrades to plain text and says so on screen. It resets on Google's clock.

**Run `python clean_test_data.py` from `backend/` after running the test suites.** The Phase 3, 4 and 5 tests write real rows into the demo database. One full run once left 60 junk applications in the manager's pipeline, which is what a reviewer would have seen first.

## To start the app

Backend, from `backend/`:
```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

React, from `frontend/`:
```powershell
npm run dev
```

Then http://localhost:5173. Logins: manager `anita@bank.com` / `Manager@123`, officer `rajan@bank.com` / `Officer@123`, customer `priya@example.com` / `Customer@123`.

Always use `.\venv\Scripts\python.exe`, never plain `python` — that is a different Python without the packages.

Please start by reading the four files above, then tell me in a few lines what you understand step 2 to be and how you plan to do it. Then build it.
