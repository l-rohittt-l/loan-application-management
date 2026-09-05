# 02 — WHAT CHANGED IN REAL LIFE
### The difference between what the documents said and what actually happened
**Source:** the `Chats/` folder — 9 transcripts covering 19 June to 20 August 2026
**Read `01-POC-BLUEPRINT.md` first.** After this, read `03-THE-FLOW-WHAT-HAPPENED.md`.

---

## THE SHORT VERSION

File 01 describes a clean plan: five phases, five days each, a fixed technology stack, 110 tests, a score, a rank.

That plan met reality and bent in eleven places. The coding assistant didn't work for weeks. The AI model the documents called mandatory was unreachable from the company network for over a month. The chat interface the documents specified got overruled by a mentor. Deadlines were fixed while everything else moved. And most importantly, **what was being measured changed halfway through** — from "how many tests pass" to "how good is your demo" — without anyone sending an announcement.

This file catalogues those changes, then lists exactly what we do differently because of them.

---

## PART 0 — WHO'S WHO

| Person | Role | What they control |
|---|---|---|
| **T V S Koushik** | Program coordinator | Deadlines, chasing licence tickets, deciding who presents to ADHs. He is the route to opportunity. |
| **L B Rakesh Kumar** | Technical mentor | The architecture teaching, the RAG requirements, the test-report rule, deciding who moves to the next phase |
| **Basavaraj Bidanoor** | Mentor | Monday and Wednesday sessions, distributed the POC files |
| **Kasturika** | Program staff | Communications with the US Bank account |
| **"Facilitator (AI)"** | Teams' automatic note-taker | The source of the "Facilitator Data" files — auto-generated meeting summaries |

### Our team

On 18 August, Koushik split everyone into teams by which POC they built. Ours:

> **Loan Application Management:** Rohit Sawant · Darshan R · A.C Harish · Yaswanth R · Md Alam · Rujal Rahangdale · Sindhu Kumari · Anuj Mishra

The other two teams were **Inventory Management** (11 people including Bapanapalli Ghouse, Aryan Kollurishetty, Hareesh Babu, Guru Prasanth Reddy, Apurva Waghmare, Ankit Kumar Warathe) and **Personal Finance Tracker** (6 people including Karthickbalaji T, Karan Negi, Hasvvath R, Arka Maiti, Md Arshad, Surendra Patidar).

**Why this matters:** eight people are presenting the same loan application system to the same audience. Building exactly what the blueprint describes makes you identical to seven other people. Everything that makes you stand out has to come from outside the blueprint.

---

## PART 1 — THE ELEVEN CHANGES

---

### CHANGE 1 — The program's real name and real purpose
**From Chat 1, 19 June**

The documents call it the *"AI Readiness Training Program."* The live program is the **"Agentic AI Readiness Program."** That word *agentic* points at the destination — AI that takes actions, not AI that answers questions.

The purpose was stated openly in the very first message:

> *"The program serves as a catalyst to unlock new project opportunities by enabling you to showcase your implemented POCs to ADHs across various accounts."*

**In plain words:** this is not a course with a certificate at the end. It's a six-week audition. The POC is the audition piece and the ADHs are the people deciding who gets staffed onto projects. Every deadline, every demo review, and every "make your version different" instruction later on follows from this one fact.

---

### CHANGE 2 — The real calendar is six weeks with an entry test, not five phases of five days
**From Chat 1, 19 June**

| Week | Dates | Phase | Topic |
|---|---|---|---|
| Orientation | 19 Jun | — | Program orientation |
| **1** | 22–26 Jun | **Phase 0** | AI Essentials + Claude Overview — self-study, **assessment on 26 June** |
| 2 | 29 Jun – 3 Jul | Phase 1 | Full Stack Java/.NET/Python vibe coding |
| 3 | 6–10 Jul | Phase 2 | **Prompt Engineering** |
| 4 | 13–17 Jul | Phase 3 | **Context Engineering + Claude Cowork** — plus an assessment |
| 5 | 20–24 Jul | Phase 4 | MCP Servers |
| 6 | 27–31 Jul | Phase 5 | Full Stack Agentic Solution |

Two things the POC documents never mention:

**There was a Phase 0 with a gate.** A full week of self-study before touching the POC: Python basics (14 hours of course material), Data Science and Machine Learning principles (4 hours), RESTful APIs (1 hour), and an introduction to Claude AI. Then **a calibration assessment on 26 June, where you needed 70% to be allowed into Phase 1.**

**The phase names drift.** Week 3 is labelled "Prompt Engineering" where the blueprint says "RAG Application." Week 4 adds "Claude Cowork." Week 6 is "Full Stack Agentic Solution" rather than "Multi-Agent with LangGraph."

**What this tells us:** the mentors were teaching a wider syllabus than the POC documents cover, using the POC as the practical exercise. When a question comes up that isn't in the POC folder, it's coming from this wider syllabus.

---

### CHANGE 3 — The mentor taught an architecture framework that isn't in the documents at all
**From Chat 2, 1 July — L B Rakesh Kumar**

This is the most useful technical content in the entire chat archive, and it appears nowhere in the POC folder. It's a way of organising an AI system by separating responsibilities:

| Piece | The question it answers |
|---|---|
| **Agent.md** | Who am I? |
| **Copilot Instructions** | How should I behave? |
| **Skill** | How do I perform this task? |
| **Prompt** | What should I do right now? |
| **Tool** | What action can I execute? |
| **MCP Server** | How do I reach external systems? |
| **Hook** | When should custom code run automatically? |
| **Knowledge Base** | Where are the facts? |

He summarised it as:

> *"Agent.md = Identity. Skills = Expertise. Prompts = Tasks. Tools = Actions. MCP = Connectivity. Hooks = Governance. Knowledge = Facts.*
> *When teams dump everything into one giant system prompt, the agent becomes difficult to maintain. Scalable multi-agent architectures keep these responsibilities separate."*

And a warning:

> *"I hope everyone has gone through the videos I shared above. Otherwise, you will only half-learn Agentic AI and burn your token budgets quickly."*

The supporting material he shared: VS Code agent customisation documentation, a video on Copilot agent mode with skills and hooks, "The 5 Rules of Token Optimization Every Developer Must Know," plus **Repository and Unit of Work design patterns** and **Test Driven Development**.

**Why it's worth memorising:** this is the vocabulary the mentors use, and it's a genuinely good way to explain your architecture in thirty seconds when someone asks how your system is organised.

---

### CHANGE 4 — GitHub Copilot didn't work, for weeks, for a lot of people
**From Chats 2 and 3, continuously from 29 June to 21 July**

The entire Phase 1 method depends on GitHub Copilot — the documents ask for Copilot on at least 60% of the code plus a written usage log. Within an hour of the POCs being handed out, the complaints started:

- *"I am unable to login to GitHub Copilot WC4C license."* — Arka Maiti
- *"I am also unable to login to the GitHub Copilot WC4C license."* — Sindhu Kumari
- *"While accessing the license it asks me to pay ₹1300/month. What could be the issue?"* — Pathakamuri Charan
- *"I am also unable to use GitHub Copilot."* — Aniruddha Rakshit
- `Reason: token expired or invalid: 403` — Nikhil Sahu, still stuck days later
- A sign-out loop — Shaik Mohammad Fayaz
- Also affected: R Hareesh Babu, Naitik Nahta

**How it got sorted out:** slowly, by pushing tickets. Koushik established the working path — raise a ticket on the Wipro service portal with a screenshot of the error, ping the executive it gets assigned to, add Koushik to the chat, and email `GitHub-Copilot@wipro.com` with Koushik and Rakesh copied in. He personally chased tickets, including reopening a **Zscaler** network exception. By 1 July he could say the issues were *"mostly resolved."*

Much later (Chat 7), Copilot **credits ran out entirely**, and the approved workaround became **M365 Copilot** for code generation, with a process for requesting more credits that was described as *"uncertain due to stricter requirements."*

**What this means for us:** the tool the method depends on was unreliable for weeks, and the deadline never moved. Keep the Copilot usage log because the documents ask for it, but never let tooling stop delivery. Koushik's position was blunt: *"Deadlines will not move because of blockers."*

---

### CHANGE 5 — The biggest one: the required AI model couldn't be reached
**From Chat 3 (6–7 July) and Chat 2 (21 July)**

**What happened.** On 6 July, Rakesh gave the Phase 2 instructions: `aistudio.google.com` is enabled, create a personal API key, and build the RAG pipeline — parse documents, keyword search, semantic search, chunking, retrieve relevant chunks, pass the context to the LLM.

Minutes later, Balaji S reported:

> *"Google Gemini Embedding API is failing with: **SSL: CERTIFICATE_VERIFY_FAILED** due to the corporate certificate chain."*

**What that error actually means, in plain words.** Companies run software (here, Zscaler) that inspects all internet traffic for security. To read encrypted traffic, it replaces the website's security certificate with its own. Your browser is configured to trust the company certificate, so browsing works fine. But Python is not — it checks the certificate against its own list, doesn't recognise the company one, assumes it's being attacked, and refuses to connect.

So: **the AI model and embedding model the documents said were mandatory and could not be substituted were unreachable from the company network.** Koushik reopened a Zscaler exception ticket on 7 July.

**How it got solved: the cohort abandoned the requirement.**

On 21 July, Shaik Mohammad Fayaz shared the migration plan that effectively became the standard:

> *Remove Gemini / OpenAI / Google AI · Remove RAG and ChromaDB · **Use Ollama only** · Create `/health` and `/chat` APIs · Build React services and chat UI · Provide production-ready implementation and validation commands.*
> With commands: `ollama --version`, `ollama list`, `ollama run smollm:latest`

**Ollama**, in plain words, is software that downloads an AI model onto your own laptop and runs it there. No internet, no API key, no certificate problem, no rate limits. The trade-off is that the models are smaller and the answers are weaker than Gemini's, and it uses your own machine's memory and CPU.

By early August, this migration was visible in nearly every demo:
- **Sana** — chunked the manual, embedded it with **`nomic-embed-text`**, stored it in ChromaDB, generated answers with **Ollama**
- **Darshan** (on our team) — *"Olama powers the AI chatbot"*; he also explained to the room that nomic-embed-text turns text into numerical vectors for similarity search rather than generating answers
- **Krishna Pal** — described using *"locally interfaced LLMs for privacy and low latency"*, turning the workaround into a selling point
- **Varsha** — Ollama plus ChromaDB for an inventory assistant

Note that most people **kept ChromaDB** and only swapped the model and embeddings. Fayaz's "remove ChromaDB" instruction was one person's approach, not what the cohort actually did.

**And the situation has now changed again: Gemini access works for us.**

**What this means:** the lesson isn't "use Gemini" or "use Ollama." It's that **the AI provider is a piece of infrastructure you don't control.** It broke once for six weeks. It can break again — including right before a presentation. So we build a switch. The design is in Part 3 of this file.

---

### CHANGE 6 — React chat interface, not Streamlit
**From Chat 3, 6 July — Rakesh, immediately after giving the RAG requirements**

> *"You must have a **React-based chat UI**."*

The blueprint specifies Streamlit for the Phase 2 chatbot, the Phase 3 agent interface, and the Phase 4 chat interface. The mentor overruled that in the live session, and the cohort followed. Every loan POC demo described in the chats runs React: Rujal used *"React plus Vite"*, Darshan used *"React.js and Vite"*, Puram built with *"React, FastAPI, SQLite, and JWT authentication"*.

**What we do:** the React chat interface is the real deliverable and what gets demoed. Keep a Streamlit version too, since the Phase 4 test spec explicitly tests Streamlit behaviour like `st.session_state` — but it's a test harness, not the presentation.

---

### CHANGE 7 — Deadlines were fixed, and the test report became a hard gate
**From Chats 2 and 3, 1 July**

On 1 July — two days before the Phase 1 deadline — Koushik collected progress from about 85 people. The results ranged from **5% to 80%**, mostly clustering at 40–50%. Rohit Sawant reported 5%, as did Kushik Mishra, Sushant, and Arun Tepan.

Rakesh's response reframed what Phase 1 actually was:

> *"Phase 1 is essentially a **one-hour interview exercise** where candidates are expected to build and explain a full-stack application. After three days, low progress is not acceptable. Complete your implementation with supporting test cases by tomorrow. **Anyone who does not complete Phase 1 will not move to Phase 2.** You have to submit a full **Test Report as sign-off** — the report must include all unit test and integration test results."*

Koushik that same evening:

> *"2 days left to complete Phase 1 deliverables. GitHub Copilot issues are mostly resolved. **Treat this as a real project scenario. Deliver on time despite blockers.** Deliverables by 03-Jul-2026: End-to-End Working Project, and Test Report with Passed/Failed Test Cases."*

**Two things to take from this.** First, the test report isn't paperwork — it's the formal sign-off, and it gated entry to the next phase. Second, Rakesh's framing is the most useful line in the archive: **Phase 1 is a one-hour interview exercise.** That's the standard being applied. Not "does it work" — can you build it *and explain it* inside an hour.

---

### CHANGE 8 — What was being measured changed, quietly
**From Chats 4, 5 and 6, late July to early August**

From the end of July, the chats stop mentioning test pass rates entirely and start running **demo reviews**. On 4 August the reason was stated outright:

> *"Participants will present their Agentic AI POCs so the team can review them and **identify suitable candidates for presentations in front of ADHs on 12th and 13th**."*

Here is where the cohort actually stood on 4 August:

| Progress | Roughly how many |
|---|---|
| Phase 5 | **1 person** (Bapanapalli Mahammad Ghouse) |
| Phase 4 done or nearly done | ~6 |
| Phase 4 in progress | ~18 |
| Phase 3 done, Phase 4 not started | ~3 |

The shortlisting criteria (Chat 6): agentic AI implementation · system architecture · AI integrations · **demonstration quality** · UI and workflow quality · **presentation skills**. What they asked people to produce: **flow diagrams, architecture diagrams, showcase-ready demos.**

**What this means:** look at that table again. Almost nobody finished Phase 5. The blueprint gives Phase 5 the lightest AI weighting (20%), but in practice it became the rarest thing anyone had. If we finish it and can demo it, we're in a group of about one. Rarity, not the weighting in the rubric, is what makes something stand out.

---

### CHANGE 9 — The rule that got repeated most: an agent *does things*, a chatbot only *answers*
**From Chat 5 Facilitator Data and Chat 7 Part 2**

This came up in multiple sessions and is clearly something they grade on.

- **Apurva** explained it: agentic AI can autonomously take actions based on prompts, while chat assistants only provide answers to questions.
- **Koushik** sharpened it: chatbots provide responses; agentic AI can autonomously perform tasks such as sending emails or storing data. And **agents can collaborate** — one agent creates a file, another sends the notification email.
- **Koushik again (17–20 August):** *"An Agent must **perform tasks** rather than only provide chatbot responses, using **multiple agents and tools through an MCP server** to select and execute appropriate actions."*
- **Aryan** scored a direct point by saying his POC can perform actions while a competing POC only responds to requests.

Two related things were explained in the same sessions:

**MCP versus plain API calls.** Ankit: *"MCP acts as a standardised layer over REST API, enabling seamless integration of multiple tools with AI agents."* Koushik: MCP provides a standard protocol for tool integration, making it easier to connect various tools to AI agents compared to wiring up each API by hand.

**Reducing hallucinations.** Koushik asked the room how you reduce hallucinations in large language models — and **nobody answered.** Eventually people offered: retrieval-augmented generation, better prompt engineering, providing domain-specific context, and fallback responses. Assume this question gets asked again.

**What we do:** the strongest moment in our demo isn't the chatbot answering a policy question. It's typing a sentence in plain English and watching an application's status actually change on screen. That's the Phase 4 `update_application_status` tool. Lead with it.

---

### CHANGE 10 — Actual review comments given to loan POCs
**These are real findings from the sessions. Every one is free marks for us.**

| # | What was said | Who and when | What we do |
|---|---|---|---|
| 1 | **Users could see other applicants' information.** Rujal said his app currently allowed this and he'd update the code to restrict it | Rujal's demo, 4 Aug | Make every read owner-scoped. This is in the blueprint already — the applicant persona says she cannot view others' data. |
| 2 | **Tenure limits vary by loan type — is that implemented?** Rujal confirmed the system only checked loan *amount* eligibility, and said he'd add tenure limits later | Koushik to Rujal, 18 Aug | Implement per-type tenure: personal 12–60, home 12–360, auto 12–84. This is contradiction #1 from File 01. |
| 3 | **Stop users applying if they don't meet the criteria**, and show a message telling them to adjust the amount or duration | Koushik, 18 Aug | Check eligibility before submission and give useful guidance, rather than rejecting silently later |
| 4 | **Don't present basic security as a feature.** *"Restricting users from viewing others' details is a standard expectation for any application"* | Koushik, 18 Aug | Fix it, but don't spend demo time on it. Use those seconds on AI instead. |
| 5 | **Admins should be able to view and download uploaded documents** — PAN card, address proof — inside the application | Koushik, 4 Aug | Add document viewing and download for officers and managers |
| 6 | **Loan eligibility criteria and validations are missing** — logged as an open question for the whole group | Chat 7 decisions list | Build a proper eligibility rule engine from manual Section 5 |
| 7 | **Risk assessment should be aimed at loan managers**, and must give value beyond a basic credit-score indicator | Koushik to Yaswanth, about his risk simulator | If we touch risk, it must use multiple factors and be manager-facing |
| 8 | **Merge RAG, MCP and tool queries into one assistant** that picks the right approach automatically | Koushik to Johith, Chat 7 Part 3 | One chat box, with routing behind it. Don't ship three separate bots. |
| 9 | **Make the architecture diagram readable** — change the background or font colour | Koushik to Hareesh | Basic slide hygiene, but it was worth a comment |
| 10 | Adding audit logs was **explicitly rejected** as not meeting the bar for a distinct, value-adding idea | Koushik to Aryan and Guru Prasanth | Our unique feature has to be more substantial than a small addition |

---

### CHANGE 11 — The final assignment: one unique feature each, and a five-minute presentation
**From Chat 7 and its Facilitator Data, 17–20 August**

**The instruction** (Koushik, 18 August, 22:32):

> *"Those who have the same POC should team up, brainstorm, and identify new requirements or enhancements that add value to your project."*

Refined over the following days into: **one unique additional requirement per team member, with no overlap between people**, posted in the group chat so everyone can see what's taken. It can be about the UI, security, data handling, performance, or an additional AI feature — but it has to be genuinely distinct and value-adding, with justification you can measure.

He enforced that bar immediately. When Aryan and Guru Prasanth proposed adding audit logs, Koushik said that wouldn't meet the requirement.

**Ideas already claimed — avoid these:**

| Idea | Taken by | Which POC |
|---|---|---|
| Draft-saving, so applicants can pause and resume an incomplete application | **Sindhu Kumari** | Loan — our team |
| AI risk simulator estimating approval likelihood from credit score, employment status and other details | **Yaswanth R** | Loan — our team |
| Document upload that extracts details from PDFs and images and **flags files that don't match the selected document type** (OCR), plus OTP verification and notifications | **Md Alam** | Loan — our team |
| AI-driven auto-ordering when stock hits a threshold | Bapanapalli Ghouse | Inventory |
| Spending-freeze plans, financial health timeline, humorous notifications | Arka Maiti | Finance |
| Voice assistant input | Karthickbalaji T | Finance |
| Uploading bank statements and parsing SMS messages to capture transactions automatically | Surendra Patidar, Hasvvath R | Finance |
| Financial goal tracker with milestone alerts at 50%, 80%, 100% | Surendra Patidar | Finance |
| Audit logs | — | ❌ rejected as too small |

Also mentioned for loans but not clearly claimed: OTP-based identity verification, submission notifications, and security hardening across authentication, data storage, data flow between layers, APIs and endpoint encryption.

**The presentation format:**
- **5 to 7 minutes total.** Suggested split: **2 minutes of slides, 3 minutes of live demo**
- Cover: problem statement → solution → technology stack → **architecture diagram** → live demo → business value
- **Focus on the AI implementation, not the UI workflow.** This was repeated in every single session.
- Be ready to **explain your source code and your design decisions**
- Have logins and queries ready *before* you start the demo
- Use voice modulation and enthusiasm — Koushik gave this as general feedback to everyone
- Watch previous session recordings and apply the feedback given to others

**Questions the ADHs ask.** Koushik shared a document called *"Questions Asked by ADHs in Previous ADH Showcase.pdf"* and told everyone to prepare answers. The themes recorded in the notes:
- How is data stored securely, and what prevents a breach?
- **What architectural changes would you need to scale from current usage to thousands or millions of concurrent users?**
- Which LLM models does it support? Why did you choose this framework?
- How do you reduce hallucinations?
- Why multi-agent rather than a single agent?

**The date and the nominations.** The US Bank ADH Showcase was set for **26 August 2026**. Nominated for that specific session: Guru Prasanth Reddy, Arka, Sindhu Kumari, Hasvvath, Aryan, and Karthik Balaji. Koushik said everyone not nominated for US Bank would be considered for other accounts and that he'd schedule calls with those ADHs.

And the reason all of this matters:

> *"Strong POC presentations can lead to selection for projects, **sometimes without a formal interview**, based on the ADHs' evaluation."* — Koushik

---

## PART 2 — THE DIFFERENCES, IN ONE TABLE
### What the blueprint says · what actually happened · what we do

| # | Blueprint | Reality | **What we do** |
|---|---|---|---|
| 1 | Gemini 2.0 Flash is mandatory. *"Can I use a different LLM? No."* | Company network blocked it via SSL for weeks; the cohort moved to Ollama; **Gemini now works for us again** | **Build a switch.** Gemini by default, Ollama as fallback, changed with one setting. See Part 3. |
| 2 | ChromaDB with `text-embedding-004` | Peers used `nomic-embed-text` through Ollama, but kept ChromaDB | Keep ChromaDB. **Use a separate collection per provider** — never mix the two. |
| 3 | Streamlit chat interfaces in Phases 2, 3 and 4 | Rakesh: *"You must have a React-based chat UI."* Every peer demo used React | **React + Vite is the deliverable.** Keep Streamlit only to satisfy the Phase 4 tests. |
| 4 | Copilot for 60% of Phase 1, with a usage log | Licences broken for weeks, then credits ran out; M365 Copilot became the approved fallback | Keep the log. Use whatever works. Never be blocked by tooling. |
| 5 | 5 days per phase, submit at end of day 5 | Real deadlines were fixed calendar dates regardless of blockers | Deliver to the calendar, not the idealised window |
| 6 | Test pass percentage determines your rank | Shortlisting was based on demo quality, architecture, AI depth and presentation skill | **Tests are the entry ticket. The demo is the prize.** Do both, but optimise the demo. |
| 7 | Tenure is 6–360 for everything | Koushik challenged a teammate on per-type tenure limits | Per-type validation, plus an eligibility check that blocks submission with a helpful message |
| 8 | Nothing said about cross-user access | A teammate's app leaked other applicants' data; Koushik said don't showcase basic security | Enforce owner-scoped access. Fix it quietly, don't pitch it. |
| 9 | A RAG chatbot that answers questions | *"An agent must perform tasks, not only provide chatbot responses"* | Lead the demo with a tool that **changes** data — `update_application_status` |
| 10 | Three separate interfaces across Phases 2, 3, 4 | Koushik: merge them into one assistant that picks the approach automatically | **One chat box.** Policy question → RAG. Data question → tools. Instruction → MCP. |
| 11 | Documents are metadata only — just a filename | Koushik asked for admins to view and download the actual files | Real file storage plus download for officers and managers |
| 12 | Everyone builds the same POC | Eight people demo the same loan system to the same ADHs | **One unique, substantial feature** — and not draft-save, risk simulator, or OCR/OTP |
| 13 | Nothing about code quality tools | A peer ran SonarQube on port 9001, aiming for >80% coverage, A ratings, passing quality gates | Optional, but it's a credible answer to "how do you ensure quality?" |
| 14 | Nothing about scale | ADHs ask how you'd scale to millions of users | Prepare the answer even though we won't build it |
| 15 | Phase 5 is the lightest AI phase at 20% | Almost nobody in the cohort finished it | **Finish Phase 5 and demo it.** It's the rarest thing in the room. |

---

## PART 3 — THE GEMINI / OLLAMA SWITCH

Gemini works again, so the plan is: **Gemini by default, Ollama as a fallback, switched with a single setting.**

This isn't just convenience. The required provider already failed this cohort once, for six weeks, because of a network policy nobody in the program controlled. It can fail again — including during a presentation. The switch is insurance.

### The settings

```env
# ---- Which provider to use ----------------------------------------------
LLM_PROVIDER=gemini              # gemini | ollama
LLM_AUTO_FALLBACK=true           # if the provider fails at startup, switch and log it loudly

# ---- Gemini (the default) -----------------------------------------------
GOOGLE_API_KEY=AIza...
GEMINI_CHAT_MODEL=gemini-2.0-flash
GEMINI_EMBED_MODEL=models/text-embedding-004

# ---- Ollama (the fallback) ----------------------------------------------
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.1        # or smollm:latest on a low-spec laptop
OLLAMA_EMBED_MODEL=nomic-embed-text

# ---- Vector store -------------------------------------------------------
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_PREFIX=poc_01_loan_manual
```

### The one rule that makes this work

**Only one file is allowed to decide which provider is being used. No other file may import a provider class directly.**

```python
# ai/llm_provider.py
# This is the ONLY file that imports ChatGoogleGenerativeAI or ChatOllama.

def get_llm(temperature: float = 0.1):
    if PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL,
                                      google_api_key=GOOGLE_API_KEY,
                                      temperature=temperature)
    return ChatOllama(model=OLLAMA_CHAT_MODEL,
                      base_url=OLLAMA_BASE_URL,
                      temperature=temperature)

def get_embeddings():
    if PROVIDER == "gemini":
        return GoogleGenerativeAIEmbeddings(model=GEMINI_EMBED_MODEL,
                                            google_api_key=GOOGLE_API_KEY)
    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)

def get_collection_name() -> str:
    return f"{CHROMA_COLLECTION_PREFIX}_{PROVIDER}"   # important — see the warning below
```

Everything else — `rag/ingest.py`, `rag/rag_chain.py`, `agent/tools.py`, `agent/summarizer.py`, the MCP server files, and the Phase 5 risk assessor and decision maker — calls `get_llm()`, `get_embeddings()` and `get_collection_name()`. Switching providers then means changing **one line in `.env`** instead of editing fourteen files.

### ⚠️ The dangerous part

The setup guide warns you'll get a *"dimension mismatch"* error if you change embedding models. **That warning will not protect you here.**

- `models/text-embedding-004` produces **768 numbers** per chunk
- `nomic-embed-text` also produces **768 numbers** per chunk

Same size, completely different meaning. ChromaDB will happily accept a Gemini-generated question against an Ollama-generated collection **without raising any error at all** — and hand back confident, plausible, completely random chunks. Your chatbot doesn't crash. It just quietly starts giving wrong answers that look right.

That's the worst possible failure during a demo: invisible, silent, and it just looks like your AI is stupid.

**The fix is `get_collection_name()` above.** Two physically separate collections:

```
poc_01_loan_manual_gemini    ← built with text-embedding-004
poc_01_loan_manual_ollama    ← built with nomic-embed-text
```

Run the ingestion once for each provider. They are never interchangeable. Log which provider and which collection is active at startup so it shows up in every trace.

### A startup health check

```
1. Make one cheap call to the configured provider
   (a one-token prompt for Gemini, or GET /api/tags for Ollama)
2. If it works  → log "provider_selected" with provider, chat model, embed model, collection
3. If it fails and LLM_AUTO_FALLBACK=true → switch, and log "provider_fallback" as a WARNING
4. If it fails and there's no fallback → stop at startup, not halfway through a demo
```

**Never fall back silently.** If it switches quietly and then someone asks "which model is this running on," you'll give the wrong answer without knowing it.

### How to run it on demo day

Run **Gemini as the default** — better answers, better reasoning, more impressive output. Keep **Ollama running on localhost** in the background during every demo. If the network, the proxy, or the free-tier limit (15 requests per minute, 1,500 per day) causes a problem mid-presentation, change one setting and carry on.

And when someone asks "which LLMs does this support?", the answer is ready:

> *"The provider is behind a single abstraction. We run Gemini 2.0 Flash by default, with Ollama running locally as a fallback — which also means the whole system can run on-premise with no data leaving the bank's network. Switching between them is one environment variable."*

That answer does three useful things at once: it shows good architecture, it shows you planned for failure, and it addresses **data privacy for a bank** — which is the thing a banking client actually worries about. One peer stumbled into this point by accident (*"locally interfaced LLMs for privacy and low latency"* — Krishna Pal). We can make it deliberately.

---

## PART 4 — WHAT WE DO NOW
### Ordered by how much each item is worth, not by phase number

**Group 1 — Non-negotiable, this is the entry ticket**
1. All five phases running end to end, each passing its 70% test threshold
2. Real test reports produced the way `ASSOCIATE_TEST_GUIDE.md` describes — genuine tests, IDs matching the spec, no `assert True`
3. The provider switch built, both collections ingested, startup health check logging which one is live

**Group 2 — The fixes, all taken from real review comments**
4. Owner-scoped access, so applicants only see their own applications
5. Per-loan-type tenure limits and a full eligibility check built from manual Section 5, blocking submission with a helpful message
6. Document view and download for officers and managers
7. One assistant that routes internally: policy questions to RAG, data questions to tools, instructions to MCP
8. Resolve the seven contradictions listed in File 01 Part 13

**Group 3 — What actually makes us stand out**
9. **Pick one unique, substantial feature** that doesn't clash with Sindhu (draft-save), Yaswanth (risk simulator) or Md Alam (OCR and OTP), and that survives Koushik's "audit logs isn't enough" test
10. Finish and demo **Phase 5**, which almost nobody in the cohort completed

**Group 4 — The presentation**
11. An architecture diagram that's readable at slide size, with good contrast
12. A 5–7 minute script: 2 minutes of slides (problem → solution → stack → architecture), 3 minutes of demo, AI-first
13. Rehearsed answers on data security, scaling to millions of users, which LLMs are supported, how hallucinations are reduced, and why multi-agent
14. Logins pre-loaded, demo queries chosen in advance, Ollama already running, and a clean, believable set of demo data in the database

---

*End of this file. Next: `03-THE-FLOW-WHAT-HAPPENED.md`.*
