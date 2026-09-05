# POC-01: Loan Application Management System

**Domain:** Banking | **Difficulty:** Intermediate | **POC ID:** POC-01

---

## Business Context

Loan application processing is the core revenue-generating activity of any retail bank. Traditionally, this involves mountains of paperwork, manual credit checks, and days or weeks of back-and-forth between applicants and loan officers. A digital loan application management system reduces processing time, improves transparency for applicants, and gives bank managers real-time visibility into portfolio risk.

In this POC, you will build a digital loan application management system from the ground up — starting with a full-stack CRUD application, and progressively adding AI capabilities that mirror real-world banking AI features: policy Q&A chatbots, intelligent data retrieval agents, conversational banking interfaces, and multi-agent loan underwriting systems.

---

## What You Will Build Across All 5 Phases

**Phase 1 — Full Stack Application:**
Build a complete loan application management system with a FastAPI (or .Net/Java) REST API backend, SQLite database, and React frontend. Applicants can submit loan applications with supporting documents. Loan officers can update application statuses. Bank managers get a dashboard showing application volumes by status and loan type. All of this is built using GitHub Copilot vibe coding.

**Phase 2 — RAG Application:**
Build a Q&A chatbot that answers questions about the loan application process using the app's user manual as the knowledge source. Using LangChain, ChromaDB, and Gemini 2.0 Flash, the chatbot can answer questions like "What documents are required for a home loan?" or "How long does approval take?" — all grounded in the actual user manual content.

**Phase 3 — Context Engineering & Tool Integration:**
Expand the Phase 2 chatbot into a context-aware agent that can both answer policy questions (via RAG) AND look up live application data (via REST API tools). The agent can answer questions like "What is the status of application APP-001 and what does the policy say about home loans?" using a combination of retrieved policy context and live database queries.

**Phase 4 — MCP Server & Chat Interface:**
Convert the Phase 1 REST API into a Model Context Protocol (MCP) server and build a conversational Streamlit chat interface. Bank staff can now interact with the entire loan management system through natural language: "Show me all pending applications submitted this week" or "Approve application APP-005 with the note that all documents are verified."

**Phase 5 — Multi-Agent System:**
Build a LangGraph multi-agent system that automates loan application evaluation. Four specialized agents — Data Collector, Risk Assessor, Compliance Checker, and Decision Maker — work in a coordinated pipeline to evaluate any loan application and produce a comprehensive underwriting recommendation with full reasoning transparency.

---

## Key Learning Outcomes

By completing all 5 phases of this POC, associates will be able to:

1. Build production-quality REST APIs with authentication, validation, and structured logging
2. Design relational data models for domain-specific business processes
3. Implement a complete RAG pipeline from document ingestion to answer generation
4. Engineer effective prompts with context injection and retrieval augmentation
5. Build LangChain agents with custom tool definitions that call external APIs
6. Design and implement an MCP server converting a REST API to the MCP protocol
7. Build a conversational chat interface with session management using Streamlit
8. Implement a LangGraph multi-agent system with the Supervisor routing pattern
9. Apply observability best practices: structured logging, LangSmith tracing, OpenTelemetry spans
10. Write automated test suites (unit, integration, AI quality) for all 5 phases
11. Use GitHub Copilot productively for full-stack application development
12. Explain the rationale for multi-agent architecture vs. single-agent approaches

---

## User Personas

### Persona 1: Priya Sharma — Loan Applicant
- **Background:** 32-year-old software engineer applying for a home loan
- **Goals:** Submit application online, track status without calling the bank, understand what documents are needed, know how long approval takes
- **Pain Points:** Unclear process, no status visibility, repeated document requests
- **How she uses the system:** Submits application via React UI, uploads documents, checks status, uses the Phase 2 chatbot to understand the process

### Persona 2: Rajan Mehta — Loan Officer
- **Background:** 8 years experience in retail banking, reviews 15-20 applications per day
- **Goals:** Quickly review pending applications, request additional documents, update statuses, add review notes
- **Pain Points:** Manual data entry, missing documents, no audit trail
- **How he uses the system:** Filters applications by status/type via React UI, uses Phase 4 chat interface to quickly query application details

### Persona 3: Anita Krishnan — Branch Manager
- **Background:** Manages a team of 8 loan officers, responsible for monthly targets
- **Goals:** Monitor application pipeline, identify bottlenecks, ensure regulatory compliance
- **Pain Points:** No real-time visibility, manual report generation
- **How she uses the system:** Dashboard view, Phase 5 multi-agent reports for risk portfolio analysis

---

## Domain Terminology Glossary

| Term | Definition |
|------|-----------|
| **KYC** | Know Your Customer — mandatory identity and background verification |
| **LTV** | Loan-to-Value ratio — loan amount as % of property value (for home loans) |
| **EMI** | Equated Monthly Installment — fixed monthly repayment amount |
| **CIBIL Score** | Credit score (300–900) indicating creditworthiness; 750+ is considered good |
| **Underwriting** | The process of evaluating loan risk before approval |
| **Disbursement** | Transfer of approved loan funds to the borrower's account |
| **Collateral** | Asset pledged as security against the loan |
| **Tenure** | Duration of the loan in months |
| **Processing Fee** | One-time fee charged by the bank for loan processing (typically 0.5–2%) |
| **Sanction Letter** | Official document from the bank approving the loan |
| **DTI Ratio** | Debt-to-Income ratio — total monthly debt payments ÷ gross monthly income |
| **FOIR** | Fixed Obligation to Income Ratio — similar to DTI, used in Indian banking |
| **Co-applicant** | Additional person who co-signs the loan application |
| **Moratorium** | A period during which loan repayments are deferred |
| **NPA** | Non-Performing Asset — a loan where payments are overdue by 90+ days |
| **Disbursement Advice** | Document confirming the disbursement of loan funds |

---

## Data Model

```
┌─────────────────────────────────────────────────────────────────┐
│                         APPLICANT                               │
│  id (PK) | name | email | phone | credit_score | annual_income  │
│  employment_status | created_at                                  │
└─────────────────────────────────────┬───────────────────────────┘
                                      │ 1:N
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LOAN_APPLICATION                            │
│  id (PK) | applicant_id (FK) | loan_type | amount_requested     │
│  tenure_months | purpose | status | submitted_at | updated_at   │
└──────────────────────────┬──────────────────┬────────────────────┘
                           │ 1:N              │ 1:N
                           ▼                  ▼
┌──────────────────────┐  ┌─────────────────────────────────────────┐
│       DOCUMENT        │  │              STATUS_HISTORY              │
│  id (PK)             │  │  id (PK) | application_id (FK)          │
│  application_id (FK) │  │  old_status | new_status | changed_by   │
│  doc_type            │  │  changed_at | remarks                    │
│  file_name           │  └─────────────────────────────────────────┘
│  uploaded_at         │
│  verified            │
└──────────────────────┘
```

### Status Transition Rules
```
submitted → under_review → approved → disbursed
                        ↘ rejected
```
- Only loan officers can change status from `under_review` onwards
- Status can only move forward (no backward transitions except manager override)
- Every status change must be recorded in `STATUS_HISTORY`

---

## Phase Progression Roadmap

| Phase | What You Build | Key Technologies Added | Output Artifact |
|-------|---------------|----------------------|----------------|
| 1 | Full stack CRUD app | FastAPI/Spring/ASP.NET + React + SQLite + JWT | Running web application |
| 2 | RAG Q&A chatbot | LangChain + ChromaDB + Gemini 2.0 Flash + Streamlit | Working chatbot with user manual corpus |
| 3 | Tool-integrated agent | LangChain agents + `@tool` decorators + ReAct | Agent that queries live application data |
| 4 | MCP server + chat UI | fastmcp + LangChain MCP client + Streamlit chat | Conversational banking assistant |
| 5 | Multi-agent system | LangGraph + StateGraph + Supervisor pattern | Automated loan underwriting pipeline |

---

## Prerequisites Before Starting

- [ ] Python 3.11+ (or .NET 8 / JDK 21) installed
- [ ] Node.js 18+ and npm installed (for React frontend)
- [ ] VS Code with GitHub Copilot extension active
- [ ] Google AI Studio API key obtained (see TECH_STACK_REFERENCE.md Section 4)
- [ ] LangSmith account created (see TECH_STACK_REFERENCE.md Section 5)
- [ ] Read TECH_STACK_REFERENCE.md completely
- [ ] Read SCORING_RUBRIC.md to understand evaluation criteria
- [ ] Read OBSERVABILITY_GUIDE.md to understand logging requirements
