# The survey prompt

Paste everything below the line into a **fresh Claude Code session on the Wipro laptop**,
opened in that laptop's copy of the project. Bring the whole reply back here.

---

You are surveying a restricted corporate laptop so that a project built on a different,
unrestricted machine can be made to run here without surprises. **You are gathering facts
only. Do not change any file, do not install anything, do not fix anything you find.** If
something is broken, write it down and move on.

## What the project is

POC-01 Loan Application Management System — a loan application website for a bank, with AI
layers on top. Five phases, all built. The stack is Python 3.11 with FastAPI and SQLAlchemy,
SQLite for the database, React 18 with Vite for the front-end, Streamlit as a second
front-end, ChromaDB as the vector store, and pytest for tests. The AI is Google Gemini by
default with Ollama as a local fallback. The folders that matter are `backend/`, `frontend/`
and `frontend-streamlit/`.

## How to work through this

Go **one section at a time**, in order. For each section: say in one line what you are about
to check and why it matters, tell Rohit exactly what to type and where, then wait for him to
paste the output back before moving to the next section. **Never give him more than one
command at a time, and never a list of six.** He has the terminal open and would rather run
things himself than watch you run them — asking him for output instead of gathering it
yourself is the point, not a limitation.

If a command fails, that failure **is** a finding. Record the exact error text and carry on.
Do not try to make it work.

---

## Section 1 — What is actually installed

For each of these, get the version and the full path to the executable. If it is missing,
say missing.

- Python (and whether `python`, `py`, or `python3` is the working command here)
- pip
- Node.js and npm
- Git
- Ollama
- Docker (only whether it exists at all)

Also: the Windows version, and whether Rohit's account is a local administrator.

## Section 2 — Which ports are free

This is the big one. The project currently assumes four ports, all of which may be taken by
company software:

| Port | What wants it |
|---|---|
| 8000 | FastAPI backend (uvicorn) |
| 5173 | React front-end (Vite dev server) |
| 8501 | Both Streamlit apps |
| 11434 | Ollama |

Find out, for each of those four, whether something is already listening, and if so **what
program it is** — the process name matters, because a company agent that restarts itself is
a different problem from a stray dev server.

Then find a block of ports that are free and stay free, and check whether anything blocks
listening on them at all. Some corporate builds restrict which ports a non-admin process may
bind. Test an actual bind, not just "nothing is listening" — those are different questions.
Report a suggested free block of four ports, and say how confident you are that they will
still be free tomorrow.

## Section 3 — Can Python install packages

The backend needs about forty packages. Find out:

- Whether `pip install` reaches the public PyPI at all, or whether it is redirected to an
  internal mirror such as Artifactory or Nexus. Check for a `pip.ini` or `pip.conf` and
  report its contents, and report `pip config list`.
- Whether there is a proxy in play. Report the `HTTP_PROXY`, `HTTPS_PROXY` and `NO_PROXY`
  environment variables, with any password blanked out.
- Whether TLS inspection is happening — a corporate certificate replacing the real one. The
  symptom is an SSL certificate verify failure on any install. Check whether `REQUESTS_CA_BUNDLE`
  or `SSL_CERT_FILE` are set, and to what.
- Whether creating a virtual environment works (`python -m venv`), and whether activating one
  is blocked by PowerShell's execution policy. Report `Get-ExecutionPolicy -List`.

Do **not** run a full install. A single small package as a test is enough, and only if that
is safe to do.

## Section 4 — Can npm install packages

Same three questions for Node: does npm reach the public registry or an internal one
(`npm config get registry`), what does `npm config list` say, and does it hit a certificate
problem. Do not run a full `npm install`.

## Section 5 — The AI models

This decides how much of the project works here at all.

- Is Ollama installed and is its service running.
- List the models already pulled (`ollama list`). **Report the exact names and tags**, not
  approximations — `llama3.1:8b` and `llama3.1:latest` are different strings and the project
  needs the exact one.
- Say which of those is a **chat** model and which is an **embedding** model. The project
  needs one of each. If there is no embedding model pulled, that is a serious finding, because
  the whole Phase 2 retrieval layer depends on one.
- Can new models be pulled here, or is that blocked or impractically slow. Do not actually
  pull one.
- Is `https://generativelanguage.googleapis.com` reachable from this machine, and is
  `https://smith.langchain.com` reachable. Both are external AI services and both may be
  blocked. A blocked Google endpoint means Gemini cannot be used here at all, which is
  expected but must be confirmed.

## Section 6 — What the machine will not let you do

Report anything that would stop a development server running:

- Whether Windows Firewall prompts on first bind, and whether Rohit can approve that prompt
  himself or whether it needs IT.
- Whether antivirus or endpoint protection interferes with a local server or with a folder
  full of new files. Name the product if you can see it.
- Whether writing to disk is restricted anywhere relevant. The project writes a SQLite file,
  a `logs/` folder, and a `chroma_db/` folder, all inside the project directory.
- Whether the project sits on OneDrive or another synced folder here. A synced folder holding
  a live SQLite database and a vector store causes file-locking problems.
- Whether `localhost` resolves normally, and whether the proxy settings would try to send
  localhost traffic through the proxy. If `NO_PROXY` does not cover localhost and 127.0.0.1,
  the front-end cannot reach the backend even though both are on this machine.

## Section 7 — Git and the company GitHub

Rohit intends to push from his personal laptop and pull here, using a company GitHub account.

- Report `git --version` and the current `user.name`, `user.email` and `remote -v` if the
  project is already a repo here.
- Which GitHub host is reachable: public `github.com`, or an internal GitHub Enterprise, or
  neither. Report the hostname of any internal one.
- Whether HTTPS git works, whether SSH git works, and whether a credential helper is
  configured.
- Whether the git protocol goes through the proxy and whether it hits the certificate problem
  from Section 3.

## Section 8 — What already exists here

- Is there already a copy of this project on this machine, and if so where and at what commit.
- Does `backend/.env` exist here, and if so report every line **with secret values blanked**.
- Does `frontend/.env` exist here, and what is in it.

---

## What to bring back

Finish with a single block Rohit can copy in one go. It must contain, in this order:

1. **A version table** — every tool from Section 1 with its version, or "missing".
2. **A port table** — the four ports, whether each is taken, by what, and the four
   replacement ports you recommend.
3. **The exact Ollama model strings available**, labelled chat or embedding.
4. **A list of what is blocked**, one line each, worst first. Say plainly whether Gemini,
   PyPI, npm and GitHub are reachable.
5. **A list of anything that failed with its exact error text.**
6. **Your own one-paragraph verdict** on the single biggest obstacle to getting this project
   running here.

Be precise with strings. Model names, port numbers, hostnames and error text will be used to
change code on the other machine, so an approximation is worse than a gap. If you did not
check something, say you did not check it rather than guessing.
