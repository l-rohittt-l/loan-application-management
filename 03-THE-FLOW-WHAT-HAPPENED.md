# 03 — THE WHOLE STORY
### What happened from start to finish, in order, explained simply
**Built from:** `01-POC-BLUEPRINT.md` and `02-GROUND-TRUTH-SHIFTS.md`
**Covers:** 19 June 2026 to 20 August 2026, and where things stand now
**Read this if** you want to understand what happened without reading specifications.

---

## THE ONE-PARAGRAPH VERSION

Around 130 engineers sitting on the bench were nominated for a six-week program to learn AI development. They spent a week on self-study, passed a test, and were each given a project to build — one of three: a loan application system, an inventory system, or a personal finance tracker. Over five phases they built a normal web application and then layered AI onto it, ending with a system where you can type instructions in plain English and it carries them out. Along the way the AI coding assistant stopped working for weeks, and the AI model they were required to use turned out to be blocked by the company's own network security for over a month. Deadlines didn't move for either problem. Around the halfway point the goal quietly shifted from "pass the tests" to "give a demo good enough that a senior delivery head wants you on their project." The program ended with everyone rehearsing five-minute presentations and being told to add one unique feature so their version didn't look identical to seven other people's.

Now the detail.

---

## THE PEOPLE

| | |
|---|---|
| **T V S Koushik** | The coordinator. Set deadlines, chased broken licences, ran the demo sessions, decided who presents to the senior stakeholders. |
| **L B Rakesh Kumar** | The technical mentor. Taught the AI architecture concepts, set the RAG requirements, made the test report a hard gate. |
| **Basavaraj Bidanoor** | Mentor for the Monday and Wednesday sessions. Distributed the project files. |
| **~130 engineers** | Nominated by their competency managers. Roughly 85 actively reported progress. |
| **Us** | **Rohit Sawant**, building the loan application system, on an 8-person team with Darshan R, A.C Harish, Yaswanth R, Md Alam, Rujal Rahangdale, Sindhu Kumari and Anuj Mishra. |
| **The ADHs** | Account Delivery Heads — senior people who run client accounts and decide who gets staffed on projects. They're the audience at the end. |

---

## PART 1 — IT STARTED WITH A NOMINATION
### 19 June 2026

Koushik posted in a Teams group: you've been nominated by your competency manager for the *NGA AI Readiness Program*. Orientation is tomorrow at 3 PM, attendance is mandatory. He noted that only 47 people had accepted the calendar invite.

The pitch was short and honest about what it was for:

> You'll do self-learning, attend mentoring sessions, and build a working application.
> *"The program serves as a catalyst to unlock new project opportunities by enabling you to showcase your implemented POCs to **ADHs across various accounts**."*

**What that actually means:** this was never a training course with a certificate at the end. It was a **six-week audition**. The project you build is your audition piece, and the ADHs are the people casting. Everything that happened later — the fixed deadlines, the demo reviews, the "make your version different" instruction — comes from that.

The same day, the six-week plan was shared:

| Week | Dates | Topic |
|---|---|---|
| Orientation | 19 June | Program overview |
| 1 | 22–26 June | **Phase 0** — AI Essentials and Claude overview, self-study, **with a test at the end** |
| 2 | 29 June – 3 July | Phase 1 — Full stack development with an AI coding assistant |
| 3 | 6–10 July | Phase 2 — Prompt engineering |
| 4 | 13–17 July | Phase 3 — Context engineering |
| 5 | 20–24 July | Phase 4 — MCP servers |
| 6 | 27–31 July | Phase 5 — Full agentic solution |

---

## PART 2 — A WEEK OF STUDY, AND A TEST TO GET IN
### 22–26 June — Phase 0

Before anyone was allowed near the actual project, there was a week of self-study: Python basics (14 hours of course material), data science and machine learning principles (4 hours), how REST APIs work (1 hour), and an introduction to Claude AI. Then **an assessment on 26 June. Score under 70% and you didn't move on to Phase 1.**

Koushik spent the week pushing people to actually do it. Day one: *"I hope all of you have completed at least 50–60% of Python Basics by now. Tomorrow the target should be 100%."* Day two, when a poll got only 73 responses out of about 130:

> *"This level of engagement is not acceptable — what about the remaining 65? Everyone is expected to actively participate throughout these 6 weeks. Your involvement is directly linked to your project allocation opportunities, so take this seriously. **Do not wait for someone to walk you through everything step by step. You are professionals now** and are expected to take ownership of your learning."*

**What this set up:** the tone of the whole program. Self-directed, deadline-driven, and not much patience for hand-holding. That tone never softened, and it explains most of what the mentors said later.

---

## PART 3 — THE PROJECTS GET HANDED OUT
### 29 June

At Basavaraj's mentoring session, Koushik shared a spreadsheet called `ICD_Agentic AI_POC_Allocation.xlsx` and three project packages: **POC-01 Loan Application Management**, POC-02 Personal Finance Tracker, and POC-07 Inventory Management. (The README describes ten possible projects; only three were actually run.)

The file sharing broke immediately. *"Same problem." "Same issue." "Same issue."* Several people couldn't open the links. Participants — including Rohit Sawant — started re-sharing the files directly to each other to unblock the room.

Inside those packages was everything described in File 01: the five phase specifications, the database design, 110 test cases, the scoring rules, the logging standard, and a complete 13-section user manual to feed to the chatbot.

**Small moment, but it's the pattern for the whole program:** the group routed around broken infrastructure faster than the infrastructure got fixed. That happened again, twice, and much more seriously.

---

## PART 4 — PROBLEM ONE: THE AI CODING ASSISTANT DOESN'T WORK
### 29 June, and continuing for weeks

The entire method for Phase 1 was "vibe coding with GitHub Copilot" — write a comment describing what you want, let the AI write the code. The specification asks for Copilot on at least 60% of the code plus a written log of where you used it.

Within an hour of the projects being handed out:

- *"I am unable to login to GitHub Copilot WC4C license."* — Arka Maiti
- *"I am also unable to login."* — Sindhu Kumari
- *"While accessing the license it asks me to pay ₹1300/month. What could be the issue?"* — Pathakamuri Charan
- *"I am also unable to use GitHub Copilot."* — Aniruddha Rakshit
- `Reason: token expired or invalid: 403` — Nikhil Sahu, still stuck days later
- Also affected: Hareesh Babu, Naitik Nahta, Shaik Mohammad Fayaz (stuck in a sign-out loop)

**How it got dealt with:** slowly, by brute force. Koushik worked out the escalation path and repeated it: raise a ticket on the service portal with a screenshot of the error, then ping the executive it gets assigned to, add Koushik to the chat, and email `GitHub-Copilot@wipro.com` with Koushik and Rakesh copied. He chased tickets personally, including reopening a network exception request with Zscaler, the company's traffic-inspection software. By 1 July he could say the problems were *"mostly resolved."*

Much later the Copilot **credits ran out entirely**, and the approved workaround became using **M365 Copilot** for code generation instead, with a request process for more credits that was described as unlikely to be approved easily.

**What this means:** the tool the method depended on was unreliable for weeks, and the deadline never moved. That combination is the first appearance of the program's hardest lesson, which Koushik stated directly: *"Deadlines will not move because of blockers."*

---

## PART 5 — MEANWHILE, THE MENTOR TEACHES THE MOST USEFUL THING IN THE PROGRAM
### 30 June – 1 July

While everyone else fought with licences, Rakesh taught architecture. He shared videos on VS Code agent customisation, Copilot token optimisation, repository design patterns and test-driven development. Then he posted a framework that appears **nowhere in the project documents** and is arguably the most valuable technical content in the whole archive:

| Piece | The question it answers |
|---|---|
| Agent.md | Who am I? |
| Copilot Instructions | How should I behave? |
| Skill | How do I perform this task? |
| Prompt | What should I do right now? |
| Tool | What action can I execute? |
| MCP Server | How do I reach external systems? |
| Hook | When should custom code run automatically? |
| Knowledge Base | Where are the facts? |

His summary:

> *"Agent.md = Identity. Skills = Expertise. Prompts = Tasks. Tools = Actions. MCP = Connectivity. Hooks = Governance. Knowledge = Facts. When teams dump everything into one giant system prompt, the agent becomes difficult to maintain. Scalable multi-agent architectures keep these responsibilities separate."*

And a warning:

> *"I hope everyone has gone through the videos I shared above. Otherwise, you will only half-learn Agentic AI and burn your token budgets quickly."*

**What this tells us:** the mentors were teaching a broader syllabus about AI engineering, using the project as the practical exercise. If you only read the project documents, you missed the actual curriculum — and the vocabulary you'd be judged in.

---

## PART 6 — PROBLEM TWO: EVERYONE IS BEHIND, AND THE MENTOR RAISES THE BAR
### 1 July — two days before the Phase 1 deadline

Koushik asked everyone for a progress percentage. About 85 people answered. The spread was rough: **from 5% to 80%**, mostly around 40–50%. Rohit Sawant reported 5%. So did Kushik Mishra, Sushant and Arun Tepan. A few were far ahead — Kiruba Sankar and Krishna Pal Chauhan at 80%, Arka Maiti at 75%.

Rakesh's reply redefined what Phase 1 actually was:

> *"Phase 1 is essentially a **one-hour interview exercise** where candidates are expected to build and explain a full-stack application. After three days, low progress is not acceptable. Complete your implementation with supporting test cases by tomorrow. **Anyone who does not complete Phase 1 will not move to Phase 2.** You have to submit a full **Test Report as sign-off** — the report must include all unit test and integration test results."*

Koushik that evening:

> *"2 days left. GitHub Copilot issues are mostly resolved. **Treat this as a real project scenario. Deliver on time despite blockers.** Deliverables by 03-Jul: End-to-End Working Project, and Test Report with Passed/Failed Test Cases."*

**Two things worth keeping:** the test report wasn't paperwork, it was the formal sign-off and the gate to the next phase. And Rakesh's line is the clearest statement of the standard being applied anywhere in the archive — *Phase 1 is a one-hour interview exercise.* Not "does it run." Can you build it **and explain it** inside an hour.

---

## PART 7 — PROBLEM THREE: THE REQUIRED AI MODEL CAN'T BE REACHED
### 6 July onwards — the biggest problem of the whole program

Phase 2 started. Rakesh gave the instructions for building the chatbot: Google AI Studio is enabled, create your own API key, then build the pipeline — parse documents, keyword search, semantic search, chunk the document, retrieve the relevant chunks, pass them to the AI. And one extra instruction that quietly overrode the specification:

> *"You must have a **React-based chat UI**."*

(The documents had said to use Streamlit. Everyone went React instead. Every demo from that point on used React.)

Balaji S reported he was already there — RAG working, ChromaDB set up. Rakesh: *"Super. Show me a demo tomorrow in my session."* Then, minutes later, Balaji again:

> *"Google Gemini Embedding API is failing with: **SSL: CERTIFICATE_VERIFY_FAILED** due to the corporate certificate chain."*

**What that means in plain words.** The company runs security software that inspects all internet traffic. To read encrypted traffic it has to substitute its own security certificate for the real one. Web browsers on company laptops are configured to trust it, so normal browsing works fine. Python isn't configured that way — it checks the certificate, doesn't recognise the company's, assumes something is attacking the connection, and refuses to connect.

So the AI model and the embedding model that the documents described as mandatory, with an explicit *"can I use a different one? No"*, **could not be reached from the company network.** Koushik reopened a Zscaler exception ticket the next day. It dragged.

**How it got solved: the group stopped following the requirement.**

On 21 July, Shaik Mohammad Fayaz shared the migration plan that became the unofficial standard:

> *Remove Gemini, OpenAI and Google AI. Remove RAG and ChromaDB. **Use Ollama only.** Create `/health` and `/chat` APIs. Build React services and a chat UI. Provide production-ready implementation and validation commands.*
> With the commands: `ollama --version`, `ollama list`, `ollama run smollm:latest`

**Ollama** downloads an AI model onto your own laptop and runs it there. No internet connection, no API key, no certificate problem, no rate limits. The trade-off is smaller models, weaker answers, and it uses your own machine's memory.

By early August the switch was visible in almost every demo:
- **Sana** chunked her manual, converted it to numbers using **`nomic-embed-text`**, stored it in ChromaDB, and generated answers with **Ollama**
- **Darshan**, on our own team, stated plainly that *"Olama powers the AI chatbot"*, and explained to the room that nomic-embed-text turns text into numerical vectors for similarity search rather than generating answers itself
- **Krishna Pal** reframed the whole workaround as a feature: *"locally interfaced LLMs for privacy and low latency"*
- **Varsha** used Ollama and ChromaDB for her inventory assistant

Most people kept ChromaDB and only swapped the AI model and the embeddings. Fayaz's "remove ChromaDB" instruction was one person's approach, not what the group actually did.

**And now the situation has changed again — Gemini works for us.** Which is why the plan is neither one nor the other, but a switch between them. A provider that broke for six weeks can break again, possibly ten minutes before a presentation. The design is in File 02, Part 3.

---

## PART 8 — THE QUIET MIDDLE
### 13–24 July — Phases 3 and 4

The chats go thin here. Access problems dragged on (*"Access issue is not resolved yet"* — Kushik Mishra, 14 July). On 7 July, mid-session, Rakesh said what everyone could see:

> *"Koushik, please end the call. It is recording a 2.5-hour video and I am not sure how useful that will be. **People are barely active in the call.**"*

Meanwhile the more ambitious went beyond what was asked. Fayaz set up **SonarQube on port 9001** — a tool that scans code for bugs and security problems and gives it a grade — aiming for over 80% test coverage, A ratings across the board, and passing quality gates. None of that was ever requested.

**What this means:** attendance and effort sagged badly in the middle weeks. The people who kept moving during that stretch are the same names that show up on the shortlists a month later. The middle of a program is where the field separates, and almost nobody notices it happening at the time.

---

## PART 9 — THE FIRST DEMOS
### 29 July

A demo session. Eight people presented and marked themselves done in the chat: Md Sajjad, Karthickbalaji T, Lokesh Kalathi S, Elamugilan A, Hareesh Babu, Balaji S, Md Shadab Arshad and Yaswanth R. There's almost no technical discussion in the transcript — it's essentially a roll call.

**What's notable is what stopped happening.** Nobody was posting test pass rates any more. The unit of progress had quietly become "did you present."

---

## PART 10 — THE GOAL CHANGES: FROM TESTS TO DEMOS
### 31 July – 4 August

The purpose was now stated outright:

> *"Participants will present their Agentic AI POCs so the team can review them and **identify suitable candidates for presentations in front of ADHs on 12th and 13th**."*

Here's where everyone actually was on 4 August:

| Progress | How many |
|---|---|
| Phase 5 | **1 person** — Bapanapalli Mahammad Ghouse |
| Phase 4 finished or nearly | about 6 |
| Phase 4 in progress | about 18 |
| Phase 3 finished, Phase 4 not started | about 3 |

**Read that table again.** The specification treats Phase 5 as the lightest AI phase, worth 20%. In practice, one person out of roughly eighty had finished it. That makes finishing Phase 5 far more valuable than its weighting suggests — not because of marks, but because almost nobody else has it.

The demos themselves showed that people had built roughly what the blueprint described:

- **Rutuja** showed the registration page with password validation, a dashboard with a live pie chart of loan statuses and an EMI calculator, and separate user and admin views for approving applications. She confirmed she'd integrated MCP with search and get-application tools, and was using JWT for authentication.
- **Puram** showed a loan dashboard with application tracking, manager review, SonarQube code quality analysis, and an AI assistant. Built with React, FastAPI, SQLite and JWT.
- **Rujal** presented a loan system combining a full-stack platform, RAG and an agentic assistant. He described the phased build: authentication and loan workflows first, then document-based Q&A, then a better chat experience, then tool-based assistants.
- **Apurva** demoed an inventory system with role-based access and an AI assistant that summarises stock levels and suggests changes.

Three things happened in this session that shaped everything afterwards.

**One: a real bug surfaced.** Rujal mentioned that his application currently let users see other applicants' information, and said he'd update the code to restrict it. Worth noting that the specification already said this shouldn't happen — the applicant persona explicitly *"cannot view other applicants' data."* The requirement was there; the implementation missed it.

**Two: the key concept got defined.** Koushik asked the room what the difference is between a chat AI assistant and agentic AI. Apurva answered: agentic AI can autonomously take actions based on prompts, while chat assistants only provide answers. Koushik sharpened it — chatbots respond, agentic AI performs tasks like sending emails or storing data, and agents can work together, one creating a file while another sends the notification.

**Three: a question got asked and nobody could answer it.** Koushik asked how you reduce hallucinations in large language models. Silence. Eventually people offered: RAG, better prompt engineering, giving the model domain-specific context, and fallback responses.

**Three free lessons for anyone paying attention:** fix the access bug, make the AI take actions rather than just answer, and have an answer ready for the hallucination question because it's clearly on their list.

---

## PART 11 — TEAMS FORM AND THE REAL ASSIGNMENT ARRIVES
### 18 August, 10:32 PM

Koushik posted the message that defined the endgame:

> *"Those who have the same POC should team up, brainstorm, and identify new requirements or enhancements that add value to your project."*

And the team lists. **Loan Application Management: Darshan R, A.C Harish, Yaswanth R, Md Alam, Rohit Sawant, Rujal Rahangdale, Sindhu Kumari, Anuj Mishra.**

Over the next two days it got more specific: **one unique additional requirement per person, with no two people picking the same thing**, posted in the group chat so everyone can see what's taken. It could be about the UI, security, data handling, performance, or an extra AI feature — but it had to be genuinely distinct and add real value, with justification you could measure.

He enforced that bar straight away. When Aryan and Guru Prasanth suggested adding audit logs, Koushik told them that wouldn't meet the requirement for a distinct, value-adding idea.

Our team started claiming ground:
- **Sindhu** — draft-saving, so applicants can pause an incomplete application and come back to it
- **Yaswanth** — an AI risk simulator estimating approval likelihood from credit score, employment status and other details. Koushik pushed back that it should be aimed at **loan managers** and must add value beyond a basic credit-score indicator.
- **Md Alam** — document upload that extracts details from PDFs and images and flags files that don't match the document type selected, plus testing OTP and email notification APIs

In the same sessions, Koushik went through Rujal's loan system live and produced a punch list that applies to all of us:

- **Do the tenure limits vary by loan type in your system?** Rujal admitted the system only checked loan amount eligibility, and said he'd add tenure limits to the EMI calculator later.
- **The application should stop users applying if they don't meet the criteria**, showing a message prompting them to adjust the amount or duration.
- **Don't highlight basic security as a feature** — *"restricting users from viewing others' details is a standard expectation for any application."*
- **Admins should be able to view and download uploaded documents** like PAN card and address proof inside the application.
- **Merge the separate bots into one assistant** that automatically picks whether to use RAG, tools, or MCP.
- **Fix the architecture diagram's contrast** so it's readable on a slide (that one went to Hareesh).

He also shared a document called *"Questions Asked by ADHs in Previous ADH Showcase.pdf"* and told everyone to prepare answers.

**The assignment had changed shape.** It was no longer "build POC-01." It was **"make your POC-01 different from seven identical ones, and be ready to defend it."**

---

## PART 12 — REHEARSALS
### 17–20 August

Three days of practice presentations with feedback. The format settled into:

- **5 to 7 minutes total.** Suggested: **2 minutes of slides, 3 minutes of live demo.**
- Cover problem statement → solution → technology stack → **architecture diagram** → live demo → business value
- **Focus on the AI implementation, not the UI workflow.** This was said in every single session.
- Be ready to **explain your source code and your design decisions**
- Have logins and queries ready *before* the demo starts
- Use voice modulation and enthusiasm — general feedback Koushik gave to everyone
- Watch the earlier session recordings and apply the feedback given to other people

Koushik then read out the nominations for the **US Bank ADH Showcase on 26 August**: Guru Prasanth Reddy, Arka, Sindhu Kumari, Hasvvath, Aryan, and Karthik Balaji. He explained that anyone not nominated for US Bank would be considered for other accounts, and he'd schedule those calls himself.

Then he explained what was actually at stake:

> *"Strong POC presentations can lead to selection for projects, **sometimes without a formal interview**, based on the ADHs' evaluation."*

The questions to be ready for: how is data stored securely and what prevents a breach · **what would you change architecturally to scale from this to thousands or millions of concurrent users** · which LLM models does it support and why this framework · how do you reduce hallucinations · why multi-agent instead of a single agent.

Other people's plans, shared in the same sessions, give a sense of the level being aimed at: Ghouse presented inventory features including stock-out alerts, supplier reliability scores, demand forecasting, festival-based procurement recommendations and automated supplier notifications. Johith demonstrated four separate AI capabilities in one app and was told to merge them into one assistant. Surendra proposed a financial goal tracker with milestone alerts at 50%, 80% and 100%.

---

## PART 13 — WHERE THINGS STAND NOW

- **The specification is fully catalogued** (File 01), including **seven places where the trainer's own documents contradict each other.** One of those — tenure limits varying by loan type — was already used as a question to one of our teammates in a live review, and he didn't have it implemented.

- **The Gemini problem has reversed.** The cohort worked around it by moving to Ollama; we now have Gemini access back. So we build neither exclusively — we build a switch: Gemini by default, Ollama as fallback, one setting to change it, and separate vector database collections for each so they never get mixed up. That converts a six-week outage into a talking point about running fully on-premise with no data leaving the bank's network, which is exactly what a banking client worries about.

- **We know the review punch list** for loan projects, because it was delivered to our own teammates in front of us: owner-scoped access, per-type tenure limits, blocking ineligible applications with useful guidance, admin document download, and merging the separate bots into one assistant.

- **We know which unique features are already taken** — draft-save, risk simulator, OCR and OTP — so we know which ground is still open.

- **We know that finishing Phase 5 puts us in a group of roughly one.**

---

## PART 14 — THE FOUR LESSONS
### What the story teaches that no specification could

**1. A specification is a plan; infrastructure decides whether the plan survives.**
A document said "you may not use a different AI model." A piece of corporate network security said otherwise, and the network won for six weeks. The practical conclusion isn't cynicism — it's that you design for your dependencies failing, because here they did, twice, and it cost people an entire phase.

**2. Deadlines were fixed. Everything else was negotiable.**
*"Deadlines will not move because of blockers"* was said once and applied permanently. When Copilot broke, the deadline held. When Gemini broke, the deadline held. The people who did well were the ones who changed *what* they delivered in order to protect *when* they delivered it.

**3. What gets measured changed halfway through, and nobody announced it.**
Weeks one to four measured test pass rates. Weeks five to nine measured demo quality. The final weeks measured how different your project was and how well you presented it. There was no memo. The people who noticed the shift are the people who got nominated. The useful habit is to keep asking *what is actually being measured right now*, because the answer is often not what it was last month.

**4. When everyone submits the same thing, only the differences are visible.**
Eight people will show an ADH a loan application form and a chatbot that answers questions about it. Building exactly what the specification describes makes you a competent member of that eight and nothing more. The things that lift you out of it all come from outside the specification: an assistant that **takes an action** and visibly changes the system on screen, a **multi-agent decision engine** that almost nobody finished, an **architecture answer** about privacy and scale that speaks to what a bank actually fears, and **one genuinely distinct feature** that survives the "audit logs isn't enough" test.

---

## WHAT TO DO NEXT

1. Build the Gemini/Ollama switch and re-ingest the manual once per provider into separate collections
2. Fix the seven contradictions from File 01 Part 13, starting with per-loan-type tenure limits
3. Fix the review punch list from File 02 Part 1, Change 10
4. Finish Phase 5 and make it demo-ready
5. Choose one unique feature that doesn't clash with Sindhu, Yaswanth or Md Alam
6. Build the 5-minute presentation, and rehearse the five ADH questions

---

*The three files in this set: `01-POC-BLUEPRINT.md` → `02-GROUND-TRUTH-SHIFTS.md` → `03-THE-FLOW-WHAT-HAPPENED.md`*
