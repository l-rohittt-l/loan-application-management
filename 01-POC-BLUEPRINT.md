# 01 — THE BLUEPRINT
### Everything the trainer gave us, explained in plain words
**Source:** the `POC-01-Loan-Application-Management/` folder (17 documents)
**What we were assigned:** POC-01, a Loan Application Management System
**Read this first.** File 02 covers what changed in real life. File 03 tells the story from start to finish.

---

## PART 1 — WHAT WE ARE ACTUALLY BUILDING

Forget the jargon for a minute. Here is the project in ordinary language.

**We are building a website for a bank that handles loan applications.**

A customer logs in, fills a form saying "I want a ₹20 lakh home loan for 15 years," and submits it. A bank employee (a loan officer) sees that application in a list, reviews it, and moves it along: submitted → under review → approved or rejected → money paid out. The customer can upload documents like ID proof and salary slips. A manager can see a dashboard showing how many applications are at each stage.

That is a normal web application. Any developer could build it. **That is only Phase 1 of five.**

The other four phases add artificial intelligence on top of that website, one layer at a time:

| Phase | What gets added | In plain words |
|---|---|---|
| **1** | The website itself | A normal loan application system: forms, lists, login, database. |
| **2** | A question-answering chatbot | You write a bank policy manual. The chatbot reads it and answers customer questions like "what documents do I need for a home loan?" — using only what the manual says, so it can't make things up. |
| **3** | The chatbot gets access to live data | Now it can also look up real applications in the database. Ask "what's the status of application 5 and what does policy say about home loans?" and it answers both halves in one reply. |
| **4** | The chatbot can *do* things, not just answer | Say "approve application 3, all documents verified" and it actually changes the status in the database. This is where it stops being a chatbot and becomes an assistant that takes actions. |
| **5** | Four AI specialists that judge a loan together | Instead of one AI doing everything, four AI workers each do one job: one gathers the data, one calculates risk, one checks paperwork and rules, one makes the final call. They pass their findings to each other and produce a recommendation with reasoning you can audit. |

So the arc is: **a website → a website that can explain itself → a website that can look things up → a website you can operate by typing in English → a website that can reason about a decision the way a team of bank employees would.**

Each phase depends on the one before it. The website built in Phase 1 is what all four AI layers talk to. If Phase 1 is badly built, all four later phases inherit the problem.

---

## PART 2 — THE WORDS YOU NEED TO KNOW

The documents use a lot of technical terms without explaining them. Here they are in plain language. Come back to this section whenever a term stops making sense.

**API (or REST API)** — The backend program. The website you see in the browser doesn't touch the database directly; it sends requests to the API ("give me application 5", "create a new application") and the API does the work. `GET`, `POST`, `PATCH` are the types of request: get something, create something, change something.

**CRUD** — Create, Read, Update, Delete. The four basic things any app does to data.

**SQLite** — A database that lives in a single file on your computer. No server to install. Good for demos, not for real banks.

**JWT (JSON Web Token)** — Your login pass. You log in once with email and password, the server hands you a long string of text, and you attach that string to every later request to prove who you are. It expires (here, after 24 hours).

**bcrypt** — The correct way to store passwords. It scrambles them so that even someone with the database can't read them back.

**LLM (Large Language Model)** — The AI that generates text. Here it's **Gemini 2.0 Flash**, Google's model, used through a free API key.

**Prompt** — The text instruction you send to the LLM. Most of "AI engineering" is writing good prompts.

**Hallucination** — When the AI confidently makes something up. The main thing all this engineering is trying to prevent.

**RAG (Retrieval Augmented Generation)** — The technique that stops hallucination. Instead of asking the AI "what documents are needed for a home loan?" and hoping it knows, you: (1) search your own manual for the relevant paragraphs, (2) paste those paragraphs into the prompt, (3) tell the AI "answer using only this text." The answer is then grounded in your document, not the AI's imagination.

**Chunking** — Splitting a long document into small pieces (here, 512 characters each) so you can search and retrieve individual paragraphs instead of the whole file.

**Embeddings** — Turning a piece of text into a long list of numbers that represents its *meaning*. Two texts about the same idea produce similar number-lists, even if they use different words. This is how the computer finds "relevant" text rather than just matching keywords.

**Vector database / ChromaDB** — A database built to store those number-lists and instantly find the closest matches to a question. ChromaDB is the one we use; it saves to a folder on disk.

**Similarity search / top-k** — Asking the vector database "give me the 4 chunks closest in meaning to this question." Here k = 4.

**LangChain** — A Python library that wires all of this together: prompts, LLM calls, retrieval, tools, chains. It's plumbing, not intelligence.

**Tool** — A normal Python function that the AI is allowed to call. You describe what it does in plain English, and the AI decides when to use it. Example: `get_application_details(5)`.

**Agent** — An LLM that has been given a set of tools and decides for itself which ones to call, in what order, to answer your question.

**ReAct** — A specific way of running an agent where it writes out its thinking in a loop: *Thought* (what should I do?) → *Action* (call this tool) → *Observation* (here's what came back) → repeat → *Final Answer*. You can read its reasoning, which makes it debuggable.

**MCP (Model Context Protocol)** — An open standard, created by Anthropic, for exposing tools to AI systems. Without it, every AI app needs custom code to talk to your system. With it, you expose your tools once in a standard format and any MCP-compatible AI can use them. Think of it as USB for AI tools: one plug shape that everything understands.

**fastmcp** — The Python library for building an MCP server.

**LangGraph** — A library for building AI workflows shaped like a flowchart. Each box is a step (here, an AI agent). A shared packet of data travels from box to box, and each box adds its findings to it.

**StateGraph / state** — The flowchart, and the shared data packet travelling through it.

**TypedDict** — A Python dictionary where you declare in advance exactly which keys it has. Used here to define that shared packet.

**Supervisor pattern** — A design where something decides which agent runs next, instead of a fixed sequence. In our case the routing is mostly linear with one decision point.

**Node / edge** — A box in the flowchart, and an arrow between boxes. A *conditional edge* is an arrow that goes one of two ways depending on a check.

**Observability** — Being able to see what your software did after the fact. Three parts: logs (records of events), traces (the path a request took), metrics (numbers over time).

**structlog** — A logging library that writes logs as JSON instead of plain sentences, so machines can read and filter them.

**OpenTelemetry (OTel) / span** — An industry standard for timing and labelling steps in your code. A "span" is one measured step, like `rag.retrieve`, with a start time, end time, and labels attached.

**LangSmith** — A website by the LangChain team that records every AI call your app makes: the exact prompt sent, the exact response, how long it took, which documents were retrieved. Essential for debugging AI, because AI doesn't give the same answer twice.

**Streamlit** — A Python library that turns a script into a simple web page. Popular for quick AI demos because you can build a chat interface in twenty lines.

**pytest / xUnit / JUnit** — Automated testing tools for Python / .NET / Java.

**GitHub Copilot** — The AI coding assistant in the editor. "Vibe coding" means writing a comment describing what you want and letting Copilot write the code.

**EMI** — Equated Monthly Installment. The fixed amount you pay the bank every month.

**CIBIL score** — India's credit score, from 300 to 900. Higher is better; 750+ is considered good.

**ADH (Account Delivery Head)** — A senior person who runs a client account at the company. They decide who gets staffed onto projects. They are the audience for the final presentation.

---

## PART 3 — THE FILES WE WERE GIVEN

| File | What it contains | Why you'd open it |
|---|---|---|
| `README.md` | Program overview | Phase weights, tiers, list of all 10 POCs, program rules |
| `overview.md` | POC-01 description | Business background, the three user types, banking glossary, **the database design**, status rules |
| `TECH_STACK_REFERENCE.md` | Setup instructions | Exact package versions, `.env` templates, how to get Gemini/LangSmith/Chroma/Copilot working |
| `SCORING_RUBRIC.md` | How marks are given | Test counts per category, pass calculation, AI-quality scoring, cheating rules |
| `OBSERVABILITY_GUIDE.md` | Logging and tracing rules | Which fields every log line needs, which span names each phase requires |
| `ASSOCIATE_TEST_GUIDE.md` | How *we* run and submit tests | Commands, report formats, the `MY_SCORES.md` template, submission package layout |
| `REVIEWER_VERIFICATION_GUIDE.md` | How *they* check our work | Worth reading — it lists exactly what they look for to catch faked results |
| `Phasewise-UserStories/phase1..5*.md` | The five build specs | Requirements, architecture diagrams, working code examples, checklists |
| `tests/phase1..5-test-spec.md` | The 110 test cases | Test IDs, code skeletons, expected results |

Every `.md` file also exists as a `.pdf` with the same content. The PDFs can be ignored.

**One small oddity:** the README describes a folder structure rooted at `d:/ICD_NGA_AI Readiness_Program_POCs/` with a `banking/` parent folder. We got the POC folder on its own. This tells us these documents were cut out of a bigger master repository — which is probably why some details don't line up between phases (see Part 13).

---

## PART 4 — HOW THE PROGRAM IS SCORED

### The five phases

| Phase | Name | Days | Weight | Tests | What you build |
|---|---|---|---|---|---|
| **1** | Full Stack CRUD with Copilot | 5 | **15%** | 20 | REST API + React UI + SQLite database |
| **2** | RAG Application | 5 | **20%** | 20 | Chatbot answering from a user manual |
| **3** | Context Engineering & Tool Integration | 5 | **20%** | 20 | Agent with 5 tools that read live data |
| **4** | MCP Server & Chat Interface | 5 | **25%** | 25 | MCP server + chat that takes actions |
| **5** | Multi-Agent with LangGraph | 5 | **20%** | 25 | Four AI agents doing loan underwriting |

25 working days total. 110 test cases. 100 points.

### The maths

```
Phase score  = (tests passed ÷ total tests) × 100
Final score  = P1×0.15 + P2×0.20 + P3×0.20 + P4×0.25 + P5×0.20
```

A phase is **"cleared"** if you pass 70% of its tests:
- Phases 1, 2, 3 → **14 of 20**
- Phases 4, 5 → **18 of 25**

### The three ranks

| Rank | How you get it | What it leads to |
|---|---|---|
| 🏆 Elite Performer | Cleared all 5 phases | First pick for advanced AI projects |
| ⭐ Emerging Contributor | Cleared exactly 4 | AI-adjacent work with mentoring |
| 🌱 Foundational Builder | Cleared 3 or fewer | Extended learning plan, basic AI tasks |

### The important detail most people miss

The rubric says directly: *"Total program score is tracked for recognition but does NOT override tier classification. Tier is determined solely by number of phases cleared."*

**In plain words: your rank depends only on how many phases you got above 70%. Nothing else.**

Scoring 100% in Phase 4 does not make up for scoring 69% in Phase 3. You would still lose the top rank. So the smart approach is not "make one phase excellent" — it's **"get every single phase over the 70% line, and don't leave any behind."**

Also worth noting: **Phase 4 is the heaviest (25%) and needs the most tests passed (18 of 25).** It deserves more preparation time than the others.

---

## PART 5 — THE BUSINESS SIDE

### Why a bank would want this

Loan processing is how retail banks make money, and traditionally it's slow: paperwork, manual credit checks, days or weeks of back-and-forth between the customer and the loan officer. Going digital cuts processing time, lets customers see their own status without phoning anyone, and gives managers a live view of the pipeline.

### The three types of user

The documents define three people who use the system. **These effectively define the permission rules.**

**Priya Sharma — the applicant.** 32, software engineer, applying for a home loan. She wants to apply online, check her status without calling the bank, know which documents she needs, and know how long approval takes. Her frustrations today: the process is unclear, she can't see status, and the bank keeps asking for documents again.
> The documents state she **"cannot view other applicants' data."** That single line is a security requirement — and it turned out to be a real bug in one teammate's build. See File 02.

**Rajan Mehta — the loan officer.** 8 years in retail banking, reviews 15–20 applications a day. He wants to filter applications quickly, request more documents, update statuses, and add review notes. His frustrations: manual data entry, missing documents, no audit trail.

**Anita Krishnan — the branch manager.** Manages 8 loan officers, responsible for monthly targets. She wants to monitor the pipeline, spot bottlenecks, and stay compliant with regulations. Her frustration: no live visibility, reports must be made by hand.

### Banking terms used throughout

| Term | Meaning |
|---|---|
| **KYC** | Know Your Customer — the mandatory identity check |
| **LTV** | Loan-to-Value — the loan as a percentage of the property's value |
| **EMI** | Equated Monthly Installment — the fixed monthly repayment |
| **CIBIL Score** | Credit score, 300–900; 750+ is good |
| **Underwriting** | The process of assessing loan risk before approving |
| **Disbursement** | Actually transferring the approved money |
| **Collateral** | An asset pledged as security against the loan |
| **Tenure** | How long the loan runs, in months |
| **Processing Fee** | One-time bank fee, usually 0.5–2% of the loan |
| **Sanction Letter** | The official approval document |
| **DTI Ratio** | Debt-to-Income — monthly debt payments ÷ monthly income |
| **FOIR** | Fixed Obligation to Income Ratio — the Indian banking version of DTI |
| **Co-applicant** | A second person who signs the loan with you |
| **Moratorium** | A period where you're allowed to pause repayments |
| **NPA** | Non-Performing Asset — a loan overdue by 90+ days |
| **Disbursement Advice** | The document confirming money was released |

### The database — four tables

```
APPLICANT  (the person borrowing)
  id | name | email | phone | credit_score | annual_income
  employment_status | created_at
        │  one applicant can have many applications
        ▼
LOAN_APPLICATION  (one loan request)
  id | applicant_id | loan_type | amount_requested
  tenure_months | purpose | status | submitted_at | updated_at
        │                          │
        │  many documents          │  many status changes
        ▼                          ▼
DOCUMENT                      STATUS_HISTORY
  id                            id | application_id
  application_id                old_status | new_status
  doc_type                      changed_by | changed_at | remarks
  file_name
  uploaded_at
  verified
```

`STATUS_HISTORY` is the audit trail: every time an application's status changes, a row is written recording what it was, what it became, who changed it, when, and why.

### The fixed lists of allowed values

These four lists appear again and again across all five phases. Learn them.

| List | Allowed values |
|---|---|
| `EmploymentStatus` | `salaried`, `self_employed`, `unemployed` |
| `LoanType` | `personal`, `home`, `auto` |
| `ApplicationStatus` | `submitted`, `under_review`, `approved`, `rejected`, `disbursed` |
| `DocumentType` | `id_proof`, `income_proof`, `bank_statement`, `property_docs`, `employment_letter` |

### How an application moves through its life

```
submitted ──▶ under_review ──▶ approved ──▶ disbursed
                     │
                     └──▶ rejected      (dead end)
```

The rules:
- Only loan officers can move it past `under_review`
- **It only moves forward.** No going backwards, except a manager override
- **Every** change must write a row into `STATUS_HISTORY`
- `rejected` and `disbursed` are final — nothing follows them

**Why this matters:** this one diagram controls Phase 1's validation code, Section 6 of the Phase 2 manual, the Phase 3 tool that reports status, the Phase 4 tool that changes status, and the Phase 5 agent that decides the outcome. It appears in five places. Write it **once** in code as a single `VALID_TRANSITIONS` dictionary and import it everywhere — never retype it, or the five copies will drift apart.

---

## PART 6 — PHASE 1: THE WEBSITE
**15% of marks · 20 tests · need 14 to pass**

**In plain words:** build a working loan application website. Backend, database, login, and two front-ends. No AI yet. This is the foundation everything else sits on.

### The 5-day plan the documents suggest

| Day | Work |
|---|---|
| 1 | Environment setup, design the database, write the models, initialise the database |
| 2 | Write all the API endpoints, add login/JWT, set up logging |
| 3 | Write unit tests and API tests, add OpenTelemetry, fix bugs |
| 4 | Build the React front-end (using Copilot heavily), connect it to the API |
| 5 | Build the second front-end, run all tests, fix failures |

### The 12 requirements

| ID | What it is | Priority | Effort |
|---|---|---|---|
| US-01-P1-01 | Submit a loan application | Must | 5 |
| US-01-P1-02 | View one application's full details plus its history | Must | 3 |
| US-01-P1-03 | List applications with filters and paging | Must | 3 |
| US-01-P1-04 | Change an application's status, with an audit record | Must | 5 |
| US-01-P1-05 | Record an uploaded document | Must | 3 |
| US-01-P1-06 | Register a new user | Must | 2 |
| US-01-P1-07 | Log in and get a token | Must | 2 |
| US-01-P1-08 | Dashboard summary | Must | 2 |
| US-01-P1-09 | React list screen | Must | 3 |
| US-01-P1-10 | React submission form | Must | 3 |
| US-01-P1-11 | React detail screen with history timeline | Should | 2 |
| US-01-P1-12 | A second front-end in another framework | Should | 3 |

### The API — 11 endpoints

| Method | Address | Success | What can go wrong |
|---|---|---|---|
| POST | `/api/v1/auth/register` | 201 created | 409 if email already exists · 422 if password too weak |
| POST | `/api/v1/auth/login` | 200 + token | 401 — and **don't say which field was wrong** |
| POST | `/api/v1/applications` | 201 created | 422 missing fields · 401 no token |
| GET | `/api/v1/applications/{id}` | 200 with nested data | 404 not found · **must respond in under 200ms** |
| GET | `/api/v1/applications?status=&loan_type=&page=&limit=` | 200 paged list | 400 if the status value is invalid |
| PATCH | `/api/v1/applications/{id}/status` | 200 | 400 "Invalid status transition" · 401 |
| POST | `/api/v1/applications/{id}/documents` | 201 | 422 if doc_type isn't in the allowed list |
| GET | `/api/v1/applications/{id}/documents` | 200 list | — |
| GET | `/api/v1/applicants/{id}` | 200 | 404 |
| POST | `/api/v1/applicants` | 201 | 422 |
| GET | `/api/v1/dashboard/summary` | 200 | **must respond in under 500ms**, and return zeros (not an error) when the database is empty |

The status codes, in plain terms: **200** = fine, **201** = created something, **400** = your request was wrong, **401** = you're not logged in, **404** = doesn't exist, **409** = conflicts with something that already exists, **422** = your data failed validation.

### The validation rules — these are tested

| Field | Rule |
|---|---|
| `loan_type` | must be `personal`, `home`, or `auto` |
| `amount_requested` | between **10,000 and 10,000,000** |
| `tenure_months` | between **6 and 360** |
| `doc_type` | one of the five allowed document types |
| `file_name` | 255 characters maximum |
| password | at least 8 characters, 1 uppercase letter, 1 digit, **stored hashed with bcrypt** |
| JWT token | signed with HS256, contains the user's email and role, **expires in 24 hours** |
| paging | defaults to page 1, 20 per page; **maximum 100 per page** |
| list order | newest first (`submitted_at` descending) |
| history order | oldest first (`changed_at` ascending) |
| `changed_by` | must be the email from the token, not something the client sends |
| multiple filters | combined with AND, not OR |

### The React front-end (compulsory)

- A table showing: application ID, applicant name, loan type, amount, status, submission date
- Dropdown filters for status and loan type that refresh the table
- **Status colours, exactly as specified:** `submitted` = blue · `under_review` = orange · `approved` = green · `rejected` = red · `disbursed` = purple
- A submission form that checks the input *before* sending it, shows server errors if they come back, and sends the user to the new application's page on success
- A detail page showing all fields plus a **vertical timeline** of the status history, a loading spinner while data loads, and an "Update Status" button for officers
- A dashboard page
- Login and register screens that store the token in the browser's localStorage
- An Axios setup that automatically attaches the token to every request

### The second front-end

Pick any of Angular, Blazor, Thymeleaf, or Streamlit. It must at minimum do: the list with filters, the submission form, and the dashboard. It talks to the same backend and must also send the token.

### Logging — every one of these events is required

| Event | Level | Fields it must contain |
|---|---|---|
| App starts | INFO | `poc_id`, `phase`, `event="database_initialized"` |
| Request begins | INFO | `request_id`, `method`, `path` |
| Request ends | INFO | `request_id`, `status_code`, `duration_ms`, `status` |
| Application created | INFO | `application_id`, `loan_type`, `amount`, `duration_ms` |
| Status changed | INFO | `application_id`, `old_status`, `new_status`, `changed_by`, `duration_ms` |
| Token checked | INFO | `user_email`, `token_valid=true` |
| Login failed | WARN | `reason`, the method and path |
| Any crash | ERROR | `error_type`, `error_message`, `stack_trace`, `request_id` |

**Required OTel spans:** `http.request` (automatic, via `FastAPIInstrumentor.instrument_app(app)`), `db.query`, `auth.validate`.

### The 20 tests

| # | ID | Type | What it checks |
|---|---|---|---|
| 1 | TC-01-P1-UNIT-01 | Unit | Creating an applicant with valid data works |
| 2 | TC-01-P1-UNIT-02 | Unit | An invalid email is rejected |
| 3 | TC-01-P1-UNIT-03 | Unit | EMI is calculated correctly |
| 4 | TC-01-P1-UNIT-04 | Unit | Loan amount limits are enforced |
| 5 | TC-01-P1-UNIT-05 | Unit | A legal status change is accepted |
| 6 | TC-01-P1-UNIT-06 | Unit | An illegal status change is rejected |
| 7 | TC-01-P1-UNIT-07 | Unit | Document type must be from the allowed list |
| 8 | TC-01-P1-UNIT-08 | Unit | An out-of-range credit score is rejected |
| 9–16 | TC-01-P1-API-01 to 08 | API | Create returns 201 · missing fields return 422 · detail returns full data · missing ID returns 404 · status change returns 200 · no token returns 401 · filters work · dashboard counts are right |
| 17–20 | TC-01-P1-DB-01 to 04 | Database | The record is really saved · a history row appears on status change · documents link to the application · **deleting an application deletes its documents** |

*Unit test* = test one function on its own, no database, no network. *API test* = send a real HTTP request and check the response. *Database test* = check the data really landed in SQLite.

### Mistakes the documents specifically warn about

Missing `check_same_thread: False` on the SQLite connection · storing passwords as plain text · calling `add()` without `commit()` · using a weak JWT secret · forgetting CORS so React on port 3000 can't reach the API on 8000 · N+1 queries in the list endpoint (use `joinedload()`) · not calling `load_dotenv()` first · skipping status-transition validation · React `useEffect` running in an infinite loop because of a missing dependency array · forgetting to attach the token in Axios · tests running against the real database instead of a test one · only testing the cases that succeed.

### Why Phase 1 matters more than its 15%

Every later phase talks to this API. Phase 2's manual documents it. Phase 3's tools call it. Phase 4's MCP server wraps it. Phase 5's data collector queries it. **If the API is sloppy, that sloppiness is copied into four more phases.** It's worth the fewest marks and deserves the most care.

---

## PART 7 — PHASE 2: THE CHATBOT THAT READS THE MANUAL
**20% of marks · 20 tests · need 14 to pass**

**In plain words:** you write a user manual for the loan system. Then you build a chatbot that answers questions using only that manual. If someone asks something the manual doesn't cover, it must say so rather than invent an answer.

### How the pipeline works

**Step 1 — Load the manual once (the "ingestion" run):**
```
user_manual.md
  → read the file                     [span: rag.document_load]
  → split into 512-character chunks   [span: rag.chunk]   with 50 characters of overlap
  → convert each chunk to numbers     [span: rag.embed]   using models/text-embedding-004
  → store in ChromaDB, collection "poc_01_loan_manual", saved to ./chroma_db
```

**Step 2 — Every time someone asks a question:**
```
question
  → find the 4 most similar chunks    [span: rag.retrieve]
  → paste them into a prompt with the question
  → send to Gemini 2.0 Flash, temperature 0.1   [span: rag.generate]
  → show the answer plus the source excerpts in a chat interface (port 8501)
```

*Overlap* means consecutive chunks share 50 characters, so a sentence split across a boundary still appears whole in one of them. *Temperature 0.1* means "be predictable and factual" rather than creative.

### The exact settings

```env
CHROMA_PERSIST_DIR=./chroma_db
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_RESULTS=4
LANGCHAIN_PROJECT=AI-Readiness-POC-01-P2
```

- Collection name: **`poc_01_loan_manual`**, using cosine similarity
- Each chunk gets an ID like `chunk_0`, `chunk_1`... **This is how re-running ingestion avoids duplicates** — same ID overwrites instead of adding a copy
- Split on these boundaries, in order of preference: paragraph breaks, line breaks, sentence ends, spaces
- When it doesn't know, it must say exactly: *"I don't have information about that in the user manual. Please contact our helpdesk."*
- Answers must come back **within 10 seconds**

### The five requirements
`US-01-P2-01` load the manual into the database · `US-01-P2-02` answer questions from it, and refuse when out of scope · `US-01-P2-03` a chat interface showing conversation history · `US-01-P2-04` every question creates a LangSmith trace within 30 seconds · `US-01-P2-05` the OTel spans appear with timing

### The user manual — the most important content in the whole POC

The Phase 2 document contains a complete 13-section manual to copy into `rag/user_manual.md`. **This isn't documentation — it's the source of every business rule the AI will state.** Here is what's in it:

**Section 1 — System overview.** Called LAMS. Handles personal, home and auto loans. Available 24/7. Features: online submission, live status tracking, document upload and verification, an officer review dashboard, a manager analytics dashboard, automated notifications.

**Section 2 — Who can do what.**
- *Applicant:* submit applications, upload documents, track their own status. **Cannot see other applicants' data.**
- *Loan Officer:* view all applications, change statuses, add remarks, verify documents. **Cannot approve disbursement.**
- *Branch Manager:* everything, plus approving disbursements, the analytics dashboard, and **overriding status transitions in exceptional cases.**

**Section 3 — The six-step workflow.** Registration → application submission → document upload → loan officer review → decision → disbursement.

**Section 4 — Which documents are required**

| Loan type | Documents |
|---|---|
| Personal | ID proof, income proof (3 months of salary slips), bank statement (6 months) |
| Home | The above, plus property documents (sale deed, NOC, building plan approval) and an employment letter for salaried applicants |
| Auto | The above three, plus a **vehicle quotation or proforma invoice** |

**Section 5 — Eligibility rules.** These exact numbers get asked about.

| | Personal | Home | Auto |
|---|---|---|---|
| Age | 21–60 | 21–70 (must be repaid before 70) | 21–65 |
| Minimum annual income | ₹2,40,000 | ₹4,80,000 | ₹1,80,000 |
| Minimum CIBIL score | **650** | **700** | **600** |
| Maximum amount | ₹25,00,000 | up to 80% of property value | up to 90% of vehicle value |
| Tenure | **12–60 months** | **12–360 months** | **12–84 months** |
| Extra condition | — | EMI must not exceed 50% of monthly income | — |

**Section 6 — Status rules.** Same as the flow diagram in Part 5. Once rejected, an application can't be reopened — you must submit a new one.

**Section 7 — How EMI is calculated**
```
EMI = P × r × (1+r)^n / ((1+r)^n − 1)

P = the loan amount
r = monthly interest rate (annual rate ÷ 12 ÷ 100)
n = number of months

Example: ₹5,00,000 at 12% per year for 36 months
  r = 12/12/100 = 0.01
  EMI = ₹16,607 per month
```

**Section 8 — The dashboard.** Shows total applications, counts by status, counts by loan type, total amount requested. Refreshes every 5 minutes. Manager login required.

**Section 9 — How long processing takes**

| Loan type | Target | Maximum |
|---|---|---|
| Personal | 2–3 business days | 7 business days |
| Home | 7–10 business days | 21 business days |
| Auto | 1–2 business days | 5 business days |

**Section 10 — Security.** Everyone logs in with email and password. Sessions expire after 24 hours of inactivity. Financial data is encrypted at rest. Every status change is recorded in the audit log with who, when, and why.

**Section 11 — 21 frequently asked questions.** The key facts inside them:
- Interest rates: **personal 10.99–18%, home 8.5–12%, auto 9–14%** per year
- Processing fee: **0.5–2% of the loan, minimum ₹500**, deducted from the disbursed amount
- Early repayment allowed after a lock-in of **6 months (personal) or 12 months (home)**, with a **2% charge** on outstanding principal
- If rejected, you can reapply after **90 days**; common reasons are low income, low CIBIL, incomplete documents, property valuation issues
- Applications **cannot be modified after submission** — you withdraw and resubmit
- Salaried applicants need **6 months** with their current employer; self-employed need **2 years** of business history
- Income is verified by salary slips and Form 16, or 2 years of ITR for self-employed
- Only **unverified** documents can be replaced
- A **co-applicant must be added at submission time**, not afterwards
- Applicants with no CIBIL score can only be considered for **secured loans** (home or auto with collateral)
- Sanction amount vs disbursement amount: the sanction is what's approved, the disbursement is what actually reaches your account after fees are deducted

**Section 12 — Troubleshooting.** Documents must be PDF, JPG or PNG, **maximum 5MB each**. Loan officers work **Monday to Saturday, 9 AM to 6 PM**, so a 24-hour delay in "submitted" status is normal.

**Section 13 — Glossary.** CIBIL, EMI, LTV, KYC, sanction letter, disbursement, collateral, NPA, FOIR, Pre-EMI.

### The 20 tests
- `TC-01-P2-ING-01` to `04` — **Ingestion:** does the file load, are chunks the right size, are embeddings created, does ChromaDB keep the data between runs
- `TC-01-P2-RET-01` to `06` — **Retrieval:** does a relevant question return relevant chunks, does it return exactly 4, does an unrelated question score low, how fast is it
- `TC-01-P2-GEN-01` to `06` — **Generation:** is the answer based on the retrieved text, does it get the document requirements right, does it answer FAQs, **does it refuse to invent things**, is the format right
- `TC-01-P2-OBS-01` to `04` — **Observability:** does a LangSmith trace appear, do the OTel spans appear, are the log fields complete, is the trace metadata right

**How answer quality is judged:** the answer must share at least 60% of its keywords with the retrieved chunks (so it's actually using them), must be a non-empty string, must address the question, and for out-of-scope questions must clearly say the information isn't available.

### The thing to watch for

**Your manual and your code must agree.** If your API accepts a 6-month personal loan but your manual says the minimum is 12 months, your own chatbot will contradict your own product — live, in front of whoever is watching. Treat every number in Sections 4, 5, 7 and 9 as something your code has to match.

---

## PART 8 — PHASE 3: THE CHATBOT GETS TOOLS
**20% of marks · 20 tests · need 14 to pass**

**In plain words:** the Phase 2 chatbot could only read the manual. Now you give it five functions it can call, four of which fetch live data from the Phase 1 database. The AI decides for itself which ones to use. So it can answer "what's the status of application 5?" (live data) *and* "what documents does a home loan need?" (manual) — and it can answer a question that needs both at once.

### The five tools

| Tool | What it calls | When the AI should use it |
|---|---|---|
| `get_application_details(application_id)` | `GET /applications/{id}` | Someone asks about one specific application by ID |
| `list_applications(status, loan_type)` | `GET /applications` | Someone asks about several applications or the pipeline |
| `get_dashboard_summary()` | `GET /dashboard/summary` | Someone asks a general "how many / what's the overall picture" question |
| `search_loan_policy(query)` | The Phase 2 RAG chain | Policy, eligibility, documents, fees, process questions |
| `get_applicant_details(applicant_id)` | `GET /applicants/{id}` | Someone asks about a person's profile, income, or credit score |

### How the agent is set up

- **ReAct** pattern, built with `create_react_agent`, running Gemini 2.0 Flash at `temperature=0` (fully predictable)
- `AgentExecutor(max_iterations=8, handle_parsing_errors=True, return_intermediate_steps=True)` — it gets at most 8 thinking steps, it recovers from malformed output instead of crashing, and it reports which tools it used
- **Anything a tool returns that's longer than 2000 characters gets summarised** by a separate AI call before being handed back, so the conversation doesn't overflow
- The system prompt must: say it's a loan assistant (not a generic AI), explain when to use each tool, forbid inventing application IDs or amounts, and politely refuse off-topic questions

### Error handling — this is directly tested

- Bad application ID → return the text **"Application not found"**, don't throw an exception
- Phase 1 API is switched off → return a clear message, **and don't crash the agent**
- Nothing matches the filters → *"No applications found matching the criteria"*

### Settings
```env
API_BASE_URL=http://localhost:8000
API_JWT_TOKEN=<a token from logging into Phase 1>
LANGCHAIN_PROJECT=AI-Readiness-POC-01-P3
```

### Required spans
`agent.tool_call` (with tool name, input, output length) · `agent.reasoning` (step number, the thought text cut to 200 characters) · `api.call` (endpoint, method, status code) · `agent.summarize` (input length, output length, compression ratio)

### The 20 tests
- `TOOL-01` to `04` — are the tools properly defined, registered, described, and validating input
- `EXEC-01` to `06` — does each tool return correct data, handle bad input, and cope when the API is down
- `CTX-01` to `04` — does the prompt build correctly, do long responses get summarised, does everything stay within the model's limits
- `E2E-01` to `06` — a status query, a **two-tool** query, a policy+data query, a summarised list, an ambiguous question, and a trace check

### The thing to watch for

**What's really being graded here is whether the AI picks the right tool** — not whether your tool code works. The benchmark question is *"What is the status of application 5 and what does the policy say about home loans?"* It must call **two** tools and combine the answers.

The AI chooses tools by reading the description text you write above each function. If your descriptions are vague, the AI picks wrong and you fail tests your code was perfectly capable of passing. **Write those descriptions like instructions: "Use this when… Do not use this for…"**

---

## PART 9 — PHASE 4: THE ASSISTANT THAT DOES THINGS
**25% of marks — the heaviest · 25 tests · need 18 to pass**

**In plain words:** rebuild your tools as an MCP server — a standard format any AI client can plug into — and build a chat interface where a bank employee can just type "approve application 3, documents verified" and the system actually does it. Phase 3's tools only *read* data. Phase 4 introduces tools that *change* data. That's the difference between a chatbot and an assistant.

### Why bother with MCP

MCP is an open standard from Anthropic that defines how AI applications talk to outside tools and data. If you expose your loan system through MCP, **any** MCP-compatible AI can operate it — not just the LangChain agent you happened to write. It's becoming the common plug shape for AI tooling.

### The six MCP tools

| Tool | What you pass it | Which API call it makes |
|---|---|---|
| `submit_loan_application` | `applicant_id, loan_type, amount_requested, tenure_months, purpose` | `POST /applications` |
| `get_application_details` | `application_id` | `GET /applications/{id}` |
| `update_application_status` | `application_id, new_status, remarks` | `PATCH /applications/{id}/status` |
| `list_applications_by_filter` | `status, loan_type, page, limit` | `GET /applications` |
| `get_dashboard_summary` | nothing | `GET /dashboard/summary` |
| `upload_document_metadata` | `application_id, doc_type, file_name` | `POST /applications/{id}/documents` |

Built with **`fastmcp==0.4.1`**. Runs either over `stdio` (for local testing) or as HTTP on **port 8080**. Note the port layout: REST API on 8000, MCP server on 8080, chat interface on 8501.

### What the chat interface must do

- Generate a session ID at startup: `str(uuid.uuid4())[:8]`, keep it in `st.session_state`, and display it in the sidebar
- Show the full conversation history in order
- Show an expandable **"Tools Used"** section under each response listing which tools ran and with what input — **and hide that section entirely when no tools were used**
- Handle follow-ups: ask "tell me about application 5", then say "approve it", and it must know you mean application 5
- Start a fresh session when the page is refreshed (this is intended behaviour, not a bug)

### Observability
Spans: `mcp.tool_invoke` (tool name, session ID, input) · `chat.message` (session ID, message number, length) · `mcp.response` (response length, tool name).
LangSmith traces must carry the **session ID**, `poc_id`, and `phase=4` in their metadata, and you must be able to filter LangSmith by session to see one whole conversation.

### The 25 tests
- `MCP-01` to `08` — server starts, tools can be discovered, each tool runs, errors return proper MCP error responses
- `CHAT-01` to `06` — page loads, messages flow, history shows, session ID is assigned, tool display works
- `INT-01` to `07` — LangChain finds the MCP tools, calls them from natural language, keeps context across turns
- `OBS-01` to `04` — traces, spans, log fields

### The thing to watch for

Two of these six tools (`submit_loan_application` and `update_application_status`) **change the database**. That's the whole point of the phase, and it's exactly what makes a demo impressive: typing a sentence and watching the application status change on screen. It's also the heaviest phase at 25% with the highest bar (18 of 25). Plan the most time for it.

---

## PART 10 — PHASE 5: FOUR AI SPECIALISTS
**20% of marks · 25 tests · need 18 to pass**

**In plain words:** instead of one AI trying to do everything, you build four small AI workers, each with one job, and connect them in a chain. Give the system a loan application ID and it produces a full underwriting recommendation — approve, reject, or ask for more information — with the reasoning written out.

### Why split it into four

If a single AI has to collect the data, calculate the risk, check compliance, *and* decide, three things go wrong: too much information for one prompt, no single prompt can be expert at all four jobs, and when the answer is wrong you can't tell which part of the thinking failed.

With four specialists: each gets a focused prompt, each one's output is visible separately, a failure in one is isolated from the others, and you can add a fifth (say, fraud detection) later without rewriting anything. **Be ready to explain this — the documents list it as a learning outcome, and it's an obvious interview question.**

### The shared data packet

Every agent receives this, adds its findings, and passes it on:

```python
class LoanProcessingState(TypedDict):
    application_id: str
    applicant_data: dict        # the person's profile
    application_data: dict      # the loan request
    documents: List[dict]       # what they uploaded
    risk_assessment: RiskAssessment
    compliance_check: ComplianceCheck
    final_decision: str         # APPROVE, REJECT, or REQUEST_MORE_INFO
    reasoning: str
    messages: List[dict]        # a running log of what each agent said
    current_agent: str
    errors: List[str]

RiskAssessment contains:  debt_to_income_ratio, emi_amount, emi_affordability,
                          credit_risk_level, employment_risk, overall_risk_score, risk_summary

ComplianceCheck contains: documents_complete, missing_documents, kyc_verified,
                          amount_within_limit, age_eligible, compliance_passed, compliance_notes
```

### The flowchart

```
START → data collector ──(any errors?)──▶ END
             │ no errors
             ▼
      risk assessor → compliance checker → decision maker → END
```

There is exactly **one** decision point: if the data collector fails, the whole thing stops cleanly instead of letting the other three work on nothing. No loops — a loan evaluation runs straight through.

### The four agents

**1. Data Collector** — no AI, just API calls. Fetches the application, the applicant, and the documents from Phase 1. If the application doesn't exist, it adds a message to `errors` and the workflow stops gracefully. Sets `current_agent = "data_collector"`.

**2. Risk Assessor** — uses the LLM at temperature 0, and must return JSON:
- `credit_risk_level`: **low** if CIBIL is 750+, **medium** if 650–749, **high** if under 650 or missing
- `employment_risk`: **low** if salaried 2+ years, **medium** if salaried under 2 years or self-employed, **high** if unemployed
- `emi_affordability`: **"no"** if the EMI is more than 50% of monthly income
- `overall_risk_score`: 0–100 where 100 is a perfect candidate. Start at 100 and subtract 30 for high credit risk, 20 if the EMI is unaffordable, 15 for high employment risk, 10 for each medium risk
- Assumes existing monthly obligations are 10% of income and interest is 12%, unless told otherwise
- **Must pull the JSON out of the AI's reply with a regular expression and fall back to safe defaults if that fails** — the documents say this explicitly, because AI models don't reliably return clean JSON

**3. Compliance Checker** — no AI, pure rules:
```python
REQUIRED_DOCS = {
  "personal": [id_proof, income_proof, bank_statement],
  "home":     [id_proof, income_proof, bank_statement, property_docs, employment_letter],
  "auto":     [id_proof, income_proof, bank_statement]
}
LOAN_LIMITS = {"personal": 2,500,000, "home": 50,000,000, "auto": 5,000,000}
```
KYC counts as verified only if an `id_proof` document exists **and** its `verified` flag is true.

**4. Decision Maker** — uses the LLM at temperature 0.1, and outputs three labelled sections: `DECISION:`, `REASONING:`, `RECOMMENDATIONS:`
```
APPROVE            if compliance passed AND risk score ≥ 60 AND the EMI is affordable
REJECT             if compliance failed in a way that can't be fixed (over the limit,
                   ineligible age) OR the risk score is below 40
REQUEST_MORE_INFO  if documents are missing but obtainable, OR the risk score is 40–59
```
**It must never approve when compliance failed.**

### Required spans
`agent.{name}.activate` for each agent · `supervisor.route` (which agent to which, and why) · `graph.execute` wrapping the whole run.

### The 25 tests
`STATE-01` to `04` (the data packet) · `AGENT-01` to `08` (each agent tested on its own with fake input) · `ROUTE-01` to `06` (routing decisions and the error path) · `E2E-01` to `07` (full runs and LangSmith traces)

### The three scenarios you must be able to demonstrate
- Credit score below 600 → REJECT or REQUEST_MORE_INFO
- A home loan with no `property_docs` → REQUEST_MORE_INFO, and `missing_documents` lists "property_docs"
- Good credit and all documents present → APPROVE

### Two traps in this phase

**Trap 1 — losing the data.** Every agent must return `{**state, "new_field": value}`. That `**state` part copies forward everything the previous agents wrote. Forget it and you silently wipe their work, so the decision maker sees an empty risk assessment and makes a nonsense decision.

**Trap 2 — the AI's text output is the fragile part.** Two of the four agents call the LLM and then parse its reply as text — one digs JSON out of prose, the other looks for the literal string `"DECISION: APPROVE"`. Both break if the model phrases things slightly differently. The documents hand you a regex and fallback values precisely because of this. **Harden these two parsers first**; they're where the end-to-end tests will fail.

---

## PART 11 — RULES THAT APPLY TO EVERY PHASE

### The technology stack

| Layer | What to use |
|---|---|
| Backend (choose one) | Python 3.11 + FastAPI + SQLAlchemy + Alembic **/** .NET 8 + ASP.NET Core + EF Core **/** Java 21 + Spring Boot 3 + Spring Data JPA |
| Front-end | **React 18 + Vite + Axios is compulsory**, plus one more (Angular 17 / Blazor / Thymeleaf / Streamlit) |
| Database | SQLite |
| AI model | **Google Gemini 2.0 Flash** (`gemini-2.0-flash`) on the free tier |
| Embeddings | `models/text-embedding-004` |
| Vector database | ChromaDB 0.5.3 |
| AI plumbing, Phases 2–4 | LangChain 0.2.6 + langchain-google-genai |
| AI plumbing, Phase 5 | LangGraph 0.1.17 |
| MCP | fastmcp 0.4.1 |
| Observability | LangSmith + structlog / Serilog / SLF4J + OpenTelemetry |
| Testing | pytest + httpx / xUnit / JUnit 5 |
| Coding assistant | GitHub Copilot |

**Gemini free tier limits:** 15 requests per minute · 1,500 per day · 1 million input tokens per minute · 32,000 output tokens per minute · 1 million token context window. If you hit the rate limit in a batch job, put `time.sleep(4)` between calls.

The documents say plainly: *"Can I use a different LLM instead of Gemini? **No.**"* — remember that line; File 02 explains what happened to it.

### Every log line must contain these fields

```json
{ "timestamp": "2026-06-17T14:30:00.123Z", "level": "INFO",
  "poc_id": "POC-01", "phase": 1, "associate_id": "your.name",
  "operation": "create_application", "duration_ms": 45,
  "status": "success", "error": null, "request_id": "req_abc123", "extra": {} }
```

Two rules that catch people out: read `poc_id` from `os.getenv("POC_ID")` rather than hardcoding it (hardcoding works locally and breaks during evaluation), and call `load_dotenv()` **before any LangChain import**, or the tracing environment variables won't be picked up.

### Required span names, by phase

| Phase | Spans |
|---|---|
| 1 | `http.request`, `db.query`, `auth.validate` |
| 2 | `rag.document_load`, `rag.chunk`, `rag.embed`, `rag.retrieve`, `rag.generate` |
| 3 | `agent.tool_call`, `agent.reasoning`, `api.call`, `agent.summarize` |
| 4 | `mcp.tool_invoke`, `chat.message`, `mcp.response` |
| 5 | `agent.{name}.activate`, `supervisor.route`, `graph.execute` |

### Change the LangSmith project name every phase
```
AI-Readiness-POC-01-P2  →  -P3  →  -P4  →  -P5
```
Forget this and all your traces pile into one project and you can't tell them apart.

### Common problems the setup guide covers

- *"API quota exceeded" from Gemini* → free tier is 15 requests/minute; add `time.sleep(4)` between calls, or use a fake LLM for testing
- *ChromaDB "dimension mismatch"* → you built the collection with one embedding model and are now querying with another; delete the `./chroma_db` folder and re-ingest
- *LangSmith traces not appearing* → check `LANGCHAIN_TRACING_V2=true` (exactly lowercase) and that `load_dotenv()` runs before LangChain imports
- *SQLite database is locked* → close the SQLite Viewer in VS Code; SQLite allows only one writer at a time

---

## PART 12 — HOW WE ARE GRADED, AND HOW PEOPLE GET CAUGHT

### Test categories per phase

| Phase | Breakdown |
|---|---|
| 1 | 8 unit · 8 API integration · 4 database |
| 2 | 4 ingestion · 6 retrieval · 6 generation · 4 observability |
| 3 | 4 tool definition · 6 tool execution · 4 context management · 6 end-to-end |
| 4 | 8 MCP server · 6 chat interface · 7 LangChain-MCP integration · 4 observability |
| 5 | 4 state schema · 8 individual agents · 6 supervisor routing · 7 end-to-end |

### How AI answer quality is scored (Phases 2–5)

Because you can't test an AI answer with `assert answer == "..."`, some tests use another AI as a judge, scoring four things:

| Measure | What it asks | Minimum |
|---|---|---|
| Faithfulness | Did the answer only use the retrieved text? | 0.7 |
| Answer relevance | Did it actually answer the question? | 0.7 |
| Context precision | Were the retrieved chunks actually relevant? | 0.6 |
| Context recall | Did the retrieved chunks contain what was needed? | 0.6 |

Advanced option: the RAGAS library automates this.

### What you submit at the end of every phase

```
submission/
├── phase[N]-results.xml     ← from: pytest --junitxml=results/phaseN-results.xml
├── MY_SCORES.md             ← tests passed, total, %, cleared yes/no, failed test IDs with reasons
├── screenshot-phase[N].png  ← the full terminal output, not cropped
└── source-code/             ← the whole project
```
Due end of day 5 of each phase window. The reviewer then re-runs your tests against your code within 48 hours and tells you your score within 72.

### What the reviewer looks for to catch faked work

Straight from their own guide:
- `assert True` or empty test bodies → **counted as failures**
- Test names that don't match the spec's IDs (`TC-01-P1-UNIT-01`) → **partial credit only**
- XML timestamps that don't match your screenshot → treated as possibly someone else's results
- Everything mocked, including the thing being tested → marks reduced on API and database categories
- Identical code across several people → flagged as plagiarism
- All 20 or 25 tests passing perfectly → triggers a **code walkthrough** where you must explain everything

**One rule in your favour:** if the reviewer's re-run shows *more* passes than you reported, they take the higher number.

### The integrity rules

Allowed: using Copilot for code, using ChatGPT/Claude/Gemini to learn concepts and debug, reading documentation and Stack Overflow, discussing approaches with teammates.
Not allowed: copying someone's implementation, submitting AI-generated code you can't explain, sharing test solutions before evaluation.
Mentors do code walkthroughs at Phase 4 and Phase 5, and **you must be able to explain every part of your implementation.**

If you disagree with a score, you have 24 hours to raise it, they re-run within 48 hours, and the coordinator decides if there's still disagreement.

---

## PART 13 — CONTRADICTIONS IN THE DOCUMENTS

The trainer's own documents disagree with each other in seven places. These aren't complaints — they're things that will break your build or get you asked awkward questions if you don't handle them. One of them was already used as a question to a teammate in a live review.

| # | The contradiction | Where | Why it causes trouble |
|---|---|---|---|
| **1** | **Tenure.** The Phase 1 API allows **6–360 months** for every loan type. The manual says personal is **12–60**, auto is **12–84**, home is **12–360**. | Phase 1 rules vs manual Section 5 | Your API would accept a 6-month home loan that your own chatbot calls invalid. **Koushik asked a teammate about exactly this in a review, and the answer was no, it wasn't implemented.** Fix: validate tenure per loan type. |
| **2** | **Loan limits.** Phase 1 caps every loan at **10,000,000**. Phase 5's compliance checker sets the home limit at **50,000,000**. | Phase 1 vs Phase 5 | Home loans between 1 crore and 5 crore can never be created, so that compliance check can never trigger. Pick one number. |
| **3** | **Vehicle quotation.** The manual says auto loans require a vehicle quotation, but it's not in the `DocumentType` list, and not in Phase 5's required documents for auto. | Manual Section 4 vs the enum vs Phase 5 | Your chatbot will tell a customer to upload a document your system cannot accept. Either add it to the list or change the manual. |
| **4** | **Risk threshold.** The Phase 5 requirement says approve when the risk score is **above 70**. The actual prompt in the same document says **60 or above**. | Phase 5 requirement vs Phase 5 code | Scores between 60 and 70 are undefined. Pick one, write it in both places, and test the boundary. |
| **5** | **Age checks.** Phase 5's compliance agent checks whether the applicant is age-eligible, but **there is no date of birth field anywhere in the database.** | Phase 5 vs the data model | The sample code admits it: `age_eligible = ... or True  # Simplified`. Either add a date of birth, or say out loud in your demo that it's a known simplification. |
| **6** | **Roles.** The manual carefully defines that officers can't approve disbursement and managers can override transitions — but **no endpoint in Phase 1 is specified to check the user's role.** | Manual Section 2 vs Phase 1 | The token carries a role and nothing uses it. This is a free improvement: implement real role-based access. |
| **7** | **Streamlit.** All the AI phases specify Streamlit for the chat interfaces. | Phases 2, 3, 4 | The mentor overruled this in a live session. See File 02. |

**How to use these:** find them, fix them, and say that you did. Saying *"I noticed the manual's tenure rules conflicted with the API's validation, so I implemented per-loan-type limits and made the chatbot cite the same rules"* shows more engineering judgement than quietly passing all 110 tests.

---

## PART 14 — WHAT THE PROGRAM SAYS YOU'LL BE ABLE TO DO

These twelve outcomes are also a good list of talking points for interviews.

1. Build production-quality REST APIs with authentication, validation and structured logging
2. Design relational database schemas for real business processes
3. Build a complete RAG pipeline from document loading to answer generation
4. Write effective prompts with injected context and retrieved information
5. Build LangChain agents with custom tools that call external APIs
6. Design and build an MCP server from an existing REST API
7. Build a conversational interface with session management
8. Build a LangGraph multi-agent system using the supervisor pattern
9. Apply observability practices: structured logging, LangSmith tracing, OpenTelemetry spans
10. Write automated test suites, including tests for AI output quality
11. Use GitHub Copilot productively for full-stack development
12. **Explain why you'd use a multi-agent architecture instead of a single agent**

Number 12 isn't a coding skill — it's an explaining skill. It turned out to be one of the most important things in the whole program, and File 02 explains why.

---

*End of blueprint. Next: `02-GROUND-TRUTH-SHIFTS.md`.*
