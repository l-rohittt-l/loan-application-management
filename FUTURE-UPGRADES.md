# Future upgrades

Ideas that came up while we worked, that go **beyond** what the trainer asked for.

Nothing here gets built until the base requirement it sits on is done and passing its tests. This file exists so good ideas don't get lost, and so they don't sneak into the build early and eat time.

Each entry says where the idea came from, why it waits, and a rough size.

---

## Activity log — the "big version"

The Phase 1 activity log is deliberately small: one table, one write function, one manager-only page. These are the pieces we left out on purpose.

| Idea | Why it waits | Size |
|---|---|---|
| Store the full text of every request and response | Storage grows fast, and most of it is never read | Medium |
| Search page with filters and date ranges | Useful only once there is a lot of activity | Medium |
| Export to Excel or CSV | Managers ask for this in real banks; not needed for a demo | Small |
| Retention rules (delete or archive after N days) | Only matters at scale | Small |
| Alerts when something looks suspicious, like many failed logins | Genuinely useful, but it's a separate feature | Medium |
| A developer-only screen for raw errors | Never shown to bank users; belongs in a log tool, not the app | Small |

---

## Features your teammates claimed

These were posted in the group chat as other people's showcase features. Rohit has talked it through with the team, so building them is fine. They wait until our own headline feature and Phase 5 are done.

| Idea | Claimed by | What it is | Size |
|---|---|---|---|
| Draft saving | Sindhu | Save a half-finished application and come back to it. **Must be stored server-side, tied to the logged-in user, never in the browser.** Drafts are separate from submitted applications, because the manual says submitted applications cannot be edited. | Small |
| OCR document reading | Md Alam | Upload a photo of a PAN card, the system reads the fields off it and checks it really is a PAN card. Gemini can read images directly, so no extra library. | Medium |
| AI risk simulator | Yaswanth | A what-if tool estimating approval chance. Phase 5 already gives us a manager-facing risk assessment, so this may not be needed at all. | Medium |

---

## Showcase features not chosen as the headline

Three ideas came up for our own unique feature. **The Manager's Morning Briefing is the headline** (settled 2026-09-05). These two wait.

| Idea | What it is | Size |
|---|---|---|
| Apply by chatting | Talk to the assistant instead of filling a form. It asks one question at a time, checks each answer against the rules, and submits at the end. Reuses the Phase 4 tools. | Medium |
| Policy what-if | The manager asks "what if we raise the minimum credit score to 700?" and the system recalculates the pipeline and shows what changes. | Medium |

---

## Things the manual promises that the system doesn't do yet

The user manual is written for Phase 2. It describes some things the trainer's Phase 1 never builds. Either build them later or trim the manual.

| Idea | Where the manual says it | Size |
|---|---|---|
| Real file upload with PDF/JPG/PNG and a 5MB cap, plus view and download for staff | Section 12. Koushik also asked for staff download in a review. | Medium |
| Co-applicants | Section 11 FAQ | Medium |
| Automated status notifications by email | Section 1 features list | Small once email works |
| Session expiry based on inactivity, not a fixed 24 hours | Section 10. Needs refresh tokens. | Medium |

---

## Everything else

| Idea | Where it came from | Why it waits | Size |
|---|---|---|---|
| Angular as a third front-end | Your career interest (D-09) | Days of work; Phases 4 and 5 need them more | Large |
| SMS OTP | Your idea | Needs a paid gateway and DLT registration we can't get. Email OTP is the realistic version. | Blocked |
| Hosting the app online | Your idea, so it can be used from the Wipro laptop through a browser | Decide before the demo, not now. See D-12. | Medium |
| SonarQube code quality gates | A peer ran it targeting 80% coverage and A ratings | Good answer to "how do you ensure quality?", but not graded | Medium |
| Automated tests for the React app | Came up while finishing Phase 1; the program grades only backend tests | Vitest plus React Testing Library for the form validation and the status badge colours | Small |
| A `python -m app` entry so `uvicorn` is not typed by hand | Convenience noticed writing the README | One file | Tiny |
| RAGAS automated answer scoring | Scoring rubric mentions it as optional | Only useful once Phase 2 answers exist | Small |
