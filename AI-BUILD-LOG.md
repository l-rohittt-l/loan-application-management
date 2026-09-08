# AI build log — Phases 3, 4, 5

Rohit was tired and asked me to keep building through Phase 5 on my own
judgement, logging what I hit here instead of stopping to ask each time. This
file is that log. `TRAPS-AND-DECISIONS.md` stays the file for things that need
his call; this one is for things I decided myself and why.

Format: what I hit, what I chose, why.

---

## 2026-09-06 — Phase 2 finished properly

**What I hit.** Phase 2 looked done at 18 of 20 tests, but two things were quietly
missing. The two LangSmith tests were *skipping*, not passing — and a skip reads
like a pass in a summary line while proving nothing. And the Streamlit chat page
the project had already committed to (`T-09`) had never been built at all; only
the React one existed.

**What I chose.** Neither counts as done until it's real. With Rohit's LangSmith
key wired in, Phase 2 now reads **22 passed, 0 skipped** — all 20 of the
trainer's plus 2 of ours. And the Streamlit Assistant tab is built to the same
standard as the React page rather than a thin version of it: same one
`/api/v1/chat` endpoint, same source-citation expander showing which manual
extracts produced the answer, same mode caption. Verified by actually driving it
in a headless browser and reading the rendered answer, not by assuming it worked.

**Why it matters.** A chatbot that cites its sources can be checked; one that
doesn't has to be trusted. Building the second front-end without citations would
have been the "technically there, actually thin" gap Rohit specifically asked me
to stop producing.

---

## 2026-09-06 — Three bugs in the trainer's own Phase 4 and Phase 5 reference code

Found while planning, before writing any code. Recording them here because each
one would have passed quietly into our build if the skeletons had been copied.

**1. A JWT that expires mid-demo.** Both the Phase 4 and Phase 5 skeletons read a
static `API_JWT_TOKEN` from `.env`. Tokens in this project expire 24 hours after
issue (`T-24`), so a token pasted into `.env` on a Friday silently stops working
on a Saturday — most likely mid-presentation, with a confusing 401 and no obvious
cause. **Chosen instead:** mint a fresh token on every call, as Phase 3 already
does. There is no scenario where a static token is better, only ones where it is
equally fine.

**2. An HTTP call that raises instead of returning.** The Phase 4 skeleton's `_api`
helper calls `resp.raise_for_status()`, which throws on any 4xx/5xx that isn't a
404. Inside a chat agent that means one unusual server response ends the whole
conversation with a stack trace. **Chosen instead:** one shared client that never
raises and always returns `(ok, value)`, so a failure becomes a sentence the
assistant can actually say out loud.

**3. An age check that never checks age.** The Phase 5 compliance skeleton
literally contains `age_eligible = applicant.get("credit_score") is not None or
True  # Simplified`. The trailing `or True` makes the whole expression always
true regardless of anything before it — and what it pretends to inspect is a
credit score, not an age. This project already added `date_of_birth` to the
applicant model precisely so this wouldn't need excusing (`D-05`). **Chosen
instead:** a real age check using the `age_on()` helper already written and tested
for Phase 1, against `rules.AGE_LIMITS`, plus the home-loan-must-end-before-70
rule. When date of birth is genuinely missing, age passes by default — a bank
cannot fail someone on data it never collected.

### All three were carried through — confirmed 2026-09-08

The section above was written while *planning* Phases 4 and 5, before either
existed. Both are now built, so here is where each fix actually lives:

| Bug | Where the fix is |
|---|---|
| 1. Static JWT | `app/services/loan_api_client.py` — `service_token()` mints a fresh token per call. Phase 4's `mcp_app.py` and Phase 5's `data_collector.py` both go through it; neither reads `API_JWT_TOKEN`. |
| 2. `raise_for_status()` | The same shared client. Every call returns `(ok, value)` and never raises. Phase 4's tools turn a failure into `{"error": ..., "detail": ...}`; `TC-01-P4-MCP-08` checks exactly that. |
| 3. Fake age check | `multi_agent/agents/compliance_checker.py` — `_check_age()` parses the applicant's real date of birth and checks it against `rules.AGE_LIMITS`, including the home-loan-ends-before-70 rule. |

Worth saying out loud in a code walkthrough: these were found by reading the
trainer's reference code rather than by a test failing, because **no test in the
programme would have caught any of them.** A static token passes every test on
the day it is created. `raise_for_status()` only bites on an error path nothing
exercises. And an age check that always returns true passes a test suite that
never supplies an ineligible age.

---
