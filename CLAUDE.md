# Project instructions

## What this project is

POC-01 Loan Application Management System, built for Wipro's Agentic AI Readiness Program. It is a loan application website for a bank, with AI layers added on top across five phases. The end goal is not passing tests — it is a five-minute demo to Account Delivery Heads that leads to a project allocation.

Rohit Sawant is building it. He has three years of Java and is new to Python. He is in QET practice, moving toward AI work.

## Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.11 + FastAPI + SQLAlchemy |
| Database | SQLite |
| Front-end | React 18 + Vite + Axios (required) |
| Second front-end | Streamlit |
| AI model | Gemini 2.0 Flash by default, Ollama as fallback (from Phase 2) |
| Vector DB | ChromaDB |
| Testing | pytest |

## Where things are

| File | What it holds |
|---|---|
| `01-POC-BLUEPRINT.md` | Everything the trainer specified. All five phases, the database design, all 110 tests, the seven contradictions. |
| `02-GROUND-TRUTH-SHIFTS.md` | What changed in real life. Eleven shifts from the mentor chats, the review punch list, the Gemini/Ollama switch design. |
| `03-THE-FLOW-WHAT-HAPPENED.md` | The story of the program in order, for context. |
| `PROGRESS-LOG.md` | What we have done, session by session. **You maintain this.** |
| `TRAPS-AND-DECISIONS.md` | Findings, traps, and open questions. **You maintain this.** |
| `POC-01-Loan-Application-Management/` | The trainer's original documents. |
| `Chats/` | Exported Teams conversations from the program. |

---

## How we work

A loop, one component at a time. A component is models, or schemas, or auth, or one router — not a whole phase.

1. Name a specific short section for Rohit to read.
2. He reads it.
3. **Explain how you plan to implement that specific thing before writing any code.** Files, function names, decisions, trade-offs.
4. He approves or corrects.
5. Build it.
6. Log it.

Never skip step 3. He is learning Python while building this, and he has to be able to explain every line.

**The same discipline applies to you.** Rohit reads one section at a time instead of trying to hold everything in his head. Do the same. Do not work from memory of a document when the document is sitting right there. Memory drifts and invents details; the file does not. This matters most for the trainer's original test specs, which hardcode module paths and function names that are not ours to choose.

### At the start of every session, before anything else

1. Read `PROGRESS-LOG.md`. It tells you where we are, what Rohit has actually read, and what "next" was last time.
2. Read `TRAPS-AND-DECISIONS.md`. It tells you which questions are still open and which traps apply.
3. **If a component depends on an unanswered item in "Needs your call", do not build it.** Say which item is blocking and ask.
4. Say in one or two lines where we are and what you propose doing, then wait.

### Before building any component

Read these four, in this order, every time. Do not skip one because you think you remember it.

| # | Read | Looking for |
|---|---|---|
| 1 | The matching section of `01-POC-BLUEPRINT.md` | The requirement itself, the validation rules, the exact expected behaviour |
| 2 | `02-GROUND-TRUTH-SHIFTS.md` | Whether a mentor overruled it, or a reviewer already flagged it on a teammate's build |
| 3 | `TRAPS-AND-DECISIONS.md` | Traps that apply here, and settled answers that constrain the design |
| 4 | The trainer's own file in `POC-01-Loan-Application-Management/` | Hardcoded names, exact test assertions, code skeletons. **The test spec for the phase is the real contract.** |

Then explain the plan. Then build.

### After building

1. Add the log entry (Rule 1).
2. Add anything new you found to the traps file (Rule 2).
3. Say what the next component is and which section Rohit should read for it.

---

## Rule 1 — Keep the progress log

After every meaningful work session, add an entry to the top of `PROGRESS-LOG.md`.

**Write it in plain language.** Like explaining to a colleague over chat, not like documentation. If you use a technical term, gloss it in plain words.

Fixed shape, about five short lines:

```
## YYYY-MM-DD — Session N: <short title>

**Asked for:** what Rohit wanted
**Built:** what actually got made
**Found:** anything surprising or worth knowing
**Realised:** what Rohit worked out or decided
**Next:** the immediate next step
```

Rules:
- Newest at the top.
- Never a wall of text. If an entry runs long, it belongs in `TRAPS-AND-DECISIONS.md` instead.
- Skip trivia. Typo fixes and renames do not get logged.
- Also tick off the reading checklist at the top of the file when he reads something.

---

## Rule 2 — Never let a finding die in chat

Chat scrolls away. The file does not.

The moment you find any of these, write it into `TRAPS-AND-DECISIONS.md`:

- A contradiction between two documents
- Something that would silently fail a test
- A difference between what the spec says and what the mentors actually asked for
- Anything needing Rohit's decision rather than yours

**If it needs a decision:** put it in "Needs your call" with an ID, what's wrong, why it matters, and your recommendation. Leave it there until he answers.

**If it just needs awareness:** put it in "Traps and differences" as one or two lines.

**Once he answers:** move it to "Settled" with his answer and the date, so we never re-argue it.

**Update this file at the end of every conversation, without being asked.** Rohit should never have to prompt for it. If a conversation produced a finding, a decision, or an answer, the file gets updated before the reply ends.

---

## Rule 3 — He must be able to explain every line

Mentors run code walkthroughs at Phases 4 and 5. The program's integrity rules say submitting AI-generated code you cannot explain is not permitted.

So:
- Prefer clear code over clever code.
- Short comments on anything non-obvious.
- No unexplained libraries or patterns. If something new is needed, say what it is and why in plain words first.
- Offer to quiz him at the end of each component.

---

## Rule 4 — Cautious upgrade

Get the base requirement working properly first. Then improve on it **by adding, never by changing.**

An upgrade is allowed if it is purely additive: a new column, a new endpoint, a new page, a new rule that only tightens something previously unchecked. An upgrade is not allowed if it alters behaviour the trainer's tests or documents already depend on.

Before adding anything, check it against the 20 Phase 1 tests and say out loud whether it breaks any of them. If it does, it is not a cautious upgrade — find another way or leave it.

## Rule 5 — One thing at a time, planned before built

Backend, React front-end, Streamlit front-end, activity logging, and each later phase are **separate iterations**. Plan the first, build the first properly, then plan the second. Do not start two at once, and do not plan all of them up front.

## Rule 6 — Validate every input, not just the ones the spec lists

The trainer's documents name validation rules for a handful of fields. Apply the same care to **every field that accepts user input**, on both the server and the form. Length limits, allowed characters, formats, ranges, required-ness. Server-side validation is the real one; client-side is for a good error message.

## Rule 7 — Write simply

Rohit is learning Python while building this. Long sentences and clever phrasing slow him down.

- Natural sentences that flow, not chopped fragments. Rohit found very short sentences *harder* to follow, because the connecting words were missing. Write the way you would say it out loud.
- Everyday words. If a technical word is needed, explain it the first time.
- No abstract phrasing. Say the concrete thing instead.
- Write like you are chatting with a colleague, not writing a document.
- When explaining something new, start from the basics and build up. Do not assume he already knows the middle steps.
- Do not dump everything at once. Answer what was asked.

## Rule 8 — End every reply by telling him what to read

We are running several files at once and it gets confusing. So the **last thing in every reply** is a short list:

- What to read, in order
- Exact file and line numbers where possible
- **What he did not answer.** Go back through his message and check every question you asked him. If he skipped one, say so plainly. He should never discover weeks later that something was left hanging.

Never leave him to work out where to look next.

## Rule 9 — Plan each piece in `BUILD-PLAN.md` before building it

Rohit wants to see the small details and suggest changes, not just approve finished work. So:

- Break the work into small pieces. Even inside the Phase 1 backend, each piece gets planned on its own.
- Write the plan for the current piece into `BUILD-PLAN.md` before writing any code.
- Ask him for input on anything with a real choice in it.
- Build only after he has seen the plan.

## Rule 10 — Catch ideas for later in `FUTURE-UPGRADES.md`

Conversations throw up good ideas that go beyond what the trainer asked for. Do not lose them, and do not build them early.

Whenever a chat produces an idea like that — a bigger version of a feature, a nice-to-have, something a peer did, something the manual promises but the system doesn't do — write it into `FUTURE-UPGRADES.md` with where it came from and a rough size. Do this at the end of the conversation without being asked.

Nothing in that file gets built until the base requirement it sits on is done and passing its tests.

## Rule 11 — Git after every piece

- Commit after every completed piece from `BUILD-PLAN.md`. Not after every file, not once a week. Every piece.
- Commit messages say what changed and why, in plain words.
- **Every piece gets a version tag when it is pushed.** The middle number is the last completed phase, the last number is the piece: `v0.0.3` is Phase 1 in progress, piece 3. When Phase 1's tests pass it becomes `v0.1.0`. Phase 2 pieces are `v0.1.1`, `v0.1.2`… and Phase 2 done is `v0.2.0`. `v1.0.0` is demo-ready. Push tags with `git push --tags`.
- Never commit `.env`, database files, `chroma_db/`, `results/`, or `Chats/`. The `.gitignore` handles it; check `git status` before every commit anyway.
- Work on `main`. One person, one branch, no ceremony.

## Rule 12 — The manual and the code must agree

The user manual is what the Phase 2 chatbot reads and quotes to customers. If the code enforces a rule the manual doesn't state, or the manual states a rule the code doesn't enforce, the chatbot will contradict the app in front of whoever is watching.

So: whenever a rule is added or changed in the code, the same change goes into the manual. And whenever the manual is written or edited, check it against the domain rules file.

## Rule 13 — Customer data never lives in the browser

Drafts, profiles, documents, application details — all stored on the server, tied to the logged-in user, fetched with their token. The browser holds the login token and nothing else that matters. Browser storage can be read by anyone with access to the machine, and Rohit's customers' data must not be there.

## Rule 14 — One thing per reply

Rohit cannot keep up with ten things in one message, and he will forget what he was asked to do. So:

- Each reply deals with **one** problem or one step. Say what it is, say what you need from him, stop.
- Do not batch questions. If three things need his answer, ask the first, wait, then the second.
- Do not give reading lists longer than one item. Walk him through things; do not hand him a list.
- Bookkeeping in the files (log, traps, future upgrades, learning notes) happens quietly in the same reply. Do not narrate it beyond one line.
- Before moving to the next step, confirm the current one is done and ask if he has questions.
- **Never skip asking him something because it would make the reply longer.** Ask it in the next reply instead.
- **Parked questions get raised when the piece in front of us needs them, not before.** Draft saving gets designed when we reach it. Hosting gets decided before the demo. Do not bring them up early just because they are open.

## Rule 15 — Keep a learning-notes file for him

Rohit wants to re-read interesting domain facts he learns along the way, like what percentage of income banks allow for EMIs. These go in `LEARNING-NOTES.md`, written simply, with sources where there are any.

Add to it when he says "store this", and also when a chat produces a fact of that kind without him asking. Keep entries short. It is a reader for him, not documentation.

## The two laptops

- **This laptop** is Rohit's personal machine. No restrictions. Install anything, use any service.
- **The Wipro laptop** is a company asset with software restrictions. The app might be used from it later through a browser. Nothing gets built on it.

## Things that are settled — do not re-litigate

- **Python, not Java.** The 20 Phase 1 test skeletons hardcode Python import paths, and Phases 2-5 are Python-only libraries.
- **Streamlit as the second front-end**, because Phase 2-4 test specs check it specifically. Angular is a possibility after Phase 5 is demo-ready, not before.
- **No GitHub Copilot licence.** A ticket is being raised separately.
- **Rank depends only on how many phases clear 70%**, not on total score. Getting all five over the line beats making any one excellent.
- **Logins follow Option A.** The normal register address creates bank staff (default loan officer, which the trainer's test expects). Customers use a separate applicant signup that creates both a login and a borrower profile. Managers are seeded, never self-registered.
- **The five Python package names are fixed by the tests:** `app`, `rag`, `agent`, `mcp_server`, `multi_agent`. They sit side by side under `backend/`. Do not nest them.
- **Folder layout does not affect speed.** Performance comes from database indexes, avoiding N+1 queries, and the response-time targets. Not from where files sit.
- **The folder layout in `BUILD-PLAN.md` is approved.** Build to it.
- **The headline showcase feature is the Manager's Morning Briefing.** Apply-by-chatting and policy what-if are in `FUTURE-UPGRADES.md`.
- **EMI affordability is 50% of monthly income for all three loan types.**
- **Teammates' features (draft saving, OCR) may be built after the headline and Phase 5.** Rohit has talked it through with the team; there is no friction.
