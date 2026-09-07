# Prompt to paste into a new session

Copy everything below the line into a fresh Claude Code chat. Suggested settings for that session: **Sonnet, medium effort** — it is careful checking, not heavy reasoning.

When that session is finished it will tell you exactly what to copy back here.

---

I'm Rohit Sawant. I'm working on POC-01, a Loan Application Management System, for Wipro's Agentic AI Readiness Program. The project lives at `C:\Users\Sawan\OneDrive\Desktop 1\FINAL_CHANCE`. Please read `CLAUDE.md` in that folder first — it explains how I like to work.

Another session just finished a long unattended build and handed me four checks to run. It ran out of its own working memory, so these were handed to you to save it. You do not need to know anything about how the project was built — everything you need is below.

## How I need you to work with me

This matters more than the tasks themselves:

- **One small step per reply.** Tell me what we're doing and why, tell me exactly where to navigate and exactly what to type, then stop and wait for me to come back with the result. Never give me a list of six commands.
- **Ask me to run things and paste the output back to you — don't run them yourself.** I have the terminal open. This saves your memory and I learn more watching it happen.
- **Tell me where to click or navigate before telling me what to type.** Assume I need the path, not just the command.
- **I'm new to Python** (three years of Java). If something is worth understanding, explain it in plain words as we go.
- If a check passes, say so plainly and move to the next. If something fails, help me understand what it means before we try to fix it.

## What you need to know about the project

- Everything runs from the `backend` folder: `C:\Users\Sawan\OneDrive\Desktop 1\FINAL_CHANCE\backend`
- There's a Python virtual environment there. The Python to use is always `.\venv\Scripts\python.exe` — never plain `python`, because that's a different Python that doesn't have the packages.
- The app is a FastAPI backend (port 8000), a React front-end (port 5173), and a Streamlit front-end (port 8501).
- It uses Google's Gemini for its AI features. **The free tier allows 500 requests per day and yesterday's run used them all up.** They reset on Google's clock. This matters for task 1.
- I'm on Windows, using PowerShell.

## The four things to check, in this order

### Task 1 — Is Phase 2 actually passing? (most important)

**The problem:** The previous session reported Phase 2 as passing 22 of 22 tests. It passed twice that day. But the very last run of the day came back with **9 failures**, three of them in `tests/phase2/test_observability.py`, and the error text was cut off so nobody could read it. That last run happened *after* the daily Gemini quota ran out.

**The expectation:** those failures are the exhausted quota, not broken code. But nobody proved it, so right now Phase 2's result is unverified.

**What I need from this task:** run the Phase 2 tests and read the *actual* error message. Then tell me which of these it is:

- Error mentions `RESOURCE_EXHAUSTED`, `429`, or a rate limit → it's the quota. Phase 2 is fine.
- Error is anything else → Phase 2 has a real problem and we need to understand it.

Please walk me through starting the backend server first if the tests need it, then running the tests, then reading the output together. The tests take several minutes because they make real AI calls, so warn me about that before I start.

### Task 2 — Look at two screens nobody has ever seen

Two parts of the app were built and tested but **never actually looked at in a browser**, because the browser tooling broke during the build. The tests pass and the code builds cleanly, but this project has already been burnt once by a bug that was invisible to everything except a screenshot.

The two screens:

1. **The Manager's Morning Briefing** — a card at the top of the manager's dashboard in the React app. Log in as `anita@bank.com` / `Manager@123`. I need to check it renders properly, the text is readable, nothing overlaps, and the "How this was worked out" button opens a panel with real numbers in it.
2. **The Phase 4 staff chat interface** — a separate Streamlit app at `backend/mcp_server/chat_interface.py`. I need to check the page loads, the sidebar shows a session ID and four quick-action buttons, and clicking a quick-action button actually produces an answer from the AI (not just my own message appearing with nothing after it).

Walk me through starting each one and tell me what to look for. If something looks wrong, help me describe it precisely enough that the other session can fix it.

### Task 3 — Regenerate two missing test result files

The project submits test reports as XML files in a `results` folder. Phase 3, 4 and 5 have theirs. **Phase 1 and Phase 2 are missing** and need regenerating.

The command shape is `pytest tests/phase1 --junitxml=../results/phase1-results.xml` run from the `backend` folder using the virtual environment's Python — but please give me the exact full command and tell me where to run it.

Do Phase 1 first (it's fast, no AI calls). Only do Phase 2 if task 1 showed Phase 2 is healthy.

### Task 4 — Check whether Ollama is worth installing

The project can fall back to a local AI called Ollama when Gemini's quota runs out, but **Ollama isn't installed on this laptop**, so that fallback doesn't currently exist.

I don't want to install it yet — I want to understand the trade-off first. Please tell me, in plain words:

- Roughly how big the download is and how long it typically takes
- Whether it will be noticeably slower than Gemini for this app's use
- Whether it runs on Windows without fuss
- Whether it's worth it for a five-minute demo, given the alternative is just "don't run the tests on demo day"

Then let me decide. Don't install anything without asking me first.

## When you're done

End the session by giving me a short block I can copy straight back into the other chat, containing:

1. **Task 1 result** — was it the quota, or a real problem? Paste the actual error text you saw.
2. **Task 2 result** — did both screens look right? If not, exactly what looked wrong.
3. **Task 3 result** — which results files now exist.
4. **Task 4 result** — what I decided about Ollama.

Keep that block short and factual. It's going into a session that's low on memory.

Please start with task 1, one small step at a time.
