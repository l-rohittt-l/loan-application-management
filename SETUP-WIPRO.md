# Setting this up on the Wipro laptop

Everything here was worked out from a survey of that machine on 2026-09-09 and
prepared on the personal laptop, so most of the thinking is already done. Follow
it top to bottom. If a step behaves differently from what is written, that is
worth stopping on rather than working around.

**What is already true on that machine**, so you do not need to check again:

- No proxy, no TLS interception. PyPI, the npm registry, GitHub over HTTPS,
  Gemini and LangSmith are all directly reachable.
- Ports 8000, 5173 and 8501 are free, and binding to them as a non-admin works.
- Ollama is installed and running, with `qwen3.5:0.8b` and `nomic-embed-text:v1.5`.
- Node 18.20.3, npm 10.7.0 and Git 2.51 are installed.
- SSH to github.com is blocked. **Clone over HTTPS**, which works, and Git
  Credential Manager is already configured.
- You are not a local administrator, and you do not need to be.

---

## 1. Use Python 3.12, not the default

The default `python` on that machine is 3.14.5, and this project will **not**
install on it. Streamlit 1.36.0 requires Pillow below version 11, and Pillow only
began publishing Windows builds for 3.14 at version 11.3. Nothing satisfies both
at once, so pip stops with `No matching distribution found for pillow`. Python
3.12.6 was installed for this reason.

Proved rather than assumed: the whole requirements file was resolved against
3.12, 3.13 and 3.14 before this guide was written. On 3.12 all 180 packages come
down as ready-built wheels. On 3.14 it fails on Pillow as above. **3.13 also
resolves cleanly**, so the 3.13 already on that machine is a working fallback if
3.12 gives trouble for any reason.

Check it is there:

```powershell
py -0p
```

You should see a `-V:3.12` line. Every command below uses `py -3.12` explicitly
so the 3.14 default never gets a chance to be picked up.

## 2. Create the environment and install

From the project root:

```powershell
cd backend
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

This installs about forty packages and takes a few minutes. **Every one of them
has a ready-built Windows wheel for 3.12**, checked package by package against
PyPI, so nothing should need compiling. If you see the words "building wheel" or
"Microsoft Visual C++ 14.0 or greater is required", stop — it means the wrong
Python is being used. Check `.\venv\Scripts\python.exe --version` says 3.12.

If PowerShell refuses to run the activate script, do not fight it. Every command
in this guide calls `.\venv\Scripts\python.exe` directly and never needs the
environment activated.

## 3. Settings files

Two ready-made files are in the repo. They are not secrets, which is why they
travelled with it.

```powershell
copy backend\.env.wipro backend\.env
copy frontend\.env.wipro frontend\.env
```

Then open `backend\.env`. **Two lines want your attention, and both are marked
FILL ME IN.**

First, `SECRET_KEY`:

```powershell
py -3.12 -c "import secrets; print(secrets.token_hex(32))"
```

Paste the result in. The app starts without it, but it would sign every login
token with a key written down in a public file.

Second, `GOOGLE_API_KEY`. Gemini is the default provider, so paste a free key
from https://aistudio.google.com/app/apikey. If you would rather not use a key
at all, change `LLM_PROVIDER` to `ollama` instead and see step 10 — but if you do
that, step 6 has to be run with that setting in place.

**Everything else is already filled in for that machine**, including the two
Ollama model names with their exact tags. Those tags matter: the project's
normal defaults are `llama3.1` and `nomic-embed-text`, and neither is what that
laptop has pulled. A wrong tag makes Ollama answer with a 404 that reads like a
network problem.

## 4. Load the demo data

```powershell
cd backend
.\venv\Scripts\python.exe seed.py
```

## 5. Front-end packages

```powershell
cd frontend
npm install
```

Watch this one. It writes many thousands of small files, and Cortex XDR is
running on that machine as endpoint protection. Nobody has tested the two
against each other. If it is unusually slow or stalls, that is the likely cause
and it is worth mentioning rather than retrying blindly.

## 6. Teach the chatbot the manual

This is a step people forget, and its absence looks like a broken chatbot rather
than a missing step.

```powershell
cd backend
.\venv\Scripts\python.exe -m rag.ingest
```

The manual gets converted into numbers and stored in ChromaDB. **Each provider
keeps its own separate collection and neither can read the other's**, so this
must be run once under whichever provider you are actually using.

The settings file ships with `LLM_PROVIDER=gemini`, so this run fills the Gemini
collection, `poc_01_loan_manual`. Ollama would fill `poc_01_loan_manual_ollama`.
They are separate on purpose: Gemini's embedding model produces 3072 numbers per
chunk and Ollama's produces 768, so the two are not interchangeable in any sense.
Mixing them would not raise an error — ChromaDB just compares numbers — it would
produce confident, plausible, completely wrong answers.

**This is the one thing to get right, so read the next paragraph twice.** Chat
falls back from Gemini to Ollama automatically (see below), but **embeddings
never do**. So if you end up running on Ollama because Gemini has no key or is
blocked, you must run the ingest step again with `LLM_PROVIDER=ollama` set. If
you skip it, the chatbot will search an empty collection and answer from nothing
at all — with no error and no sources, which looks like a stupid AI rather than
a missing step.

To check which collections actually hold anything:

```powershell
cd backend
.\venv\Scripts\python.exe -c "import chromadb; c=chromadb.PersistentClient(path='./chroma_db'); print([(x.name, c.get_collection(x.name).count()) for x in c.list_collections()])"
```

You want to see a non-zero count against the collection for the provider you
are running.

## 7. Start it up

Three terminals. **The backend must be first** — everything else talks to it.

```powershell
# Terminal 1 — the API
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

The first time this binds, Windows Firewall may show a prompt. The survey could
not test this, because it only ever bound on loopback. Approve it if you can. If
it needs an administrator you do not have, the fallback is to add
`--host 127.0.0.1`, which keeps the server on the loopback address where the
firewall generally does not interfere. Nothing in this project needs the server
visible to other machines.

```powershell
# Terminal 2 — the React front-end
cd frontend
npm run dev
```

```powershell
# Terminal 3 — Streamlit
backend\venv\Scripts\streamlit run frontend-streamlit/app.py
```

Then open http://localhost:5173 and sign in:

| Who | Email | Password |
|---|---|---|
| Manager | anita@bank.com | Manager@123 |
| Loan officer | rajan@bank.com | Officer@123 |
| Customer | priya@example.com | Customer@123 |

The manager sees the Morning Briefing at the top of the dashboard, which is the
headline feature of the demo.

## 8. Check it works

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v
```

142 tests, about ten minutes, **with the backend server running** — Phases 3, 4
and 5 call it over HTTP and will fail without it.

Expect some difference from the 142 that pass on the personal laptop, and do not
read it as breakage:

- The two LangSmith tracing tests need a key. The settings file ships with
  tracing off, so they will skip or fail. Add a free key from
  smith.langchain.com if you want them.
- Anything asserting on the *quality* of an AI answer may behave differently.
  `qwen3.5:0.8b` is a much smaller model than Gemini, and small models ramble.
  The plumbing is what matters here.

**Phase 1's 27 tests use no AI at all.** If those pass, the foundation is sound
regardless of what the AI tests do.

## 9. One more port than the survey checked

Phase 4's staff chat runs on **8502**, which the survey never tested because I
had not spotted it at the time. Everything else is confirmed free.

```powershell
cd backend
.\venv\Scripts\streamlit run mcp_server/chat_interface.py --server.port 8502
```

If 8502 turns out to be taken, any free port works — it is a command-line flag,
nothing in the code refers to it.

## 10. The two providers, and what switches by itself

**Gemini is the default**, here and everywhere else in this project. It is the
better model and the survey confirmed it is reachable from that machine. Paste a
free key into `GOOGLE_API_KEY` in `backend\.env` and it is used for everything.

**Ollama is the fallback**, and for chat it now happens on its own. If Gemini
refuses — a dead daily quota, a network block, a withdrawn model — the very next
question is retried against Ollama on that machine and the answer still arrives.
No file to edit, no server to restart, nothing for anyone to notice mid-demo.
The switch is logged as `llm_fallback_armed` when the safety net is attached.

Two deliberate limits on that:

- **It only goes one way.** If you set `LLM_PROVIDER=ollama` yourself, Gemini is
  never called behind your back.
- **Embeddings never switch automatically**, for the reason in step 6. Changing
  which provider does the *retrieval* means editing `.env` and re-running the
  ingest.

To see whether the safety net is currently there, the backend's health endpoint
reports it: a `chat_fallback` naming the Ollama model means armed, `null` means
Ollama is not answering on that machine.

**If you want to run entirely on Ollama** — no Google key at all, nothing leaving
the laptop — set `LLM_PROVIDER=ollama` in `backend\.env` and **re-run step 6**.
That is a perfectly good demo configuration and costs nothing.

---

## Things that will look like bugs and are not

**A stale server.** If a change does not seem to take effect, check whether an
old backend is still running on 8000 from an earlier session. Open
http://localhost:8000/openapi.json and see whether what you expect is listed.
This has cost real time before.

**Timestamps five and a half hours out.** Fixed long ago, but if it reappears it
is a timezone marker missing from an API response, not a clock problem.

**The Phase 4 chat crashing on import.** It adds `backend/` to its own path, so
it should be fine wherever it is run from. If `ModuleNotFoundError: No module
named 'app'` appears, that fix has been lost.

## What to report back

If something here does not work, the useful things to carry back are the exact
error text, which Python `.\venv\Scripts\python.exe --version` reports, and
which step number it happened on.
