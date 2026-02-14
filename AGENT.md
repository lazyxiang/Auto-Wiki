# AGENTS.md — Master Plan for AutoWiki

## Project Overview
**App:** AutoWiki
**Goal:** Enterprise-grade intelligent code knowledge base generator that turns code into structured, visual, and interactive Wikis.
**Stack:** Next.js 15 (Frontend), FastAPI (Backend), AgentScope (Orchestration), Tree-sitter (Parsing), SQLite + FAISS/Chroma (Data).
**Current Phase:** Phase 1 — Foundation & Ingestion

## How I Should Think
1. **Architect First, Coder Second**: Always verify the "Glass Box" logic. Don't just generate code; explain *how* it parses the AST or handles the Context Window.
2. **Steerability is Key**: Respect the `.autowiki.json` logic above all else.
3. **Plan Before Coding**: Propose a plan, ask for approval, then implement.
4. **Security Mindset**: Since this is local/self-hosted, ensure we aren't exposing local file system vulnerabilities via the API.
5. **Test-Driven Reliability**: Every new feature or refactor MUST include corresponding unit tests. A task is only complete when all unit tests pass.

## Plan → Execute → Verify
1. **Plan:** Outline the approach (e.g., "I will create the Tree-sitter parser in `parser.py`").
2. **Execute:** Implement the feature.
3. **Verify:**
    * **Unit Testing:** Write and run new tests for the changes, and ensure existing tests still pass.
    * **ELI5 Audit:** Explain how errors are handled.
    * **Logic Check:** Verify AST parsing isn't just simple regex splitting.

## Roadmap
### Phase 1: Foundation (Current)
- [ ] **Docker Setup:** Create `docker-compose.yml` for Next.js + FastAPI + Chroma/FAISS.
- [ ] **Backend Skeleton:** Initialize FastAPI with AgentScope integration.
- [ ] **Data Ingestion (The Hard Part):** Implement `parser.py` using Tree-sitter for AST extraction.
- [ ] **Chunking Logic:** Implement `chunker.py` to split by function/class (Smart Chunking).

### Phase 2: Core Features
- [ ] **Steerable Config:** Implement `.autowiki.json` parser.
- [ ] **Vector Storage:** Implement `storage.py` to save chunks to Vector DB.
- [ ] **Frontend Dashboard:** Dark mode, Project Cards, Real-time status.

### Phase 3: Visualization & RAG
- [ ] **Mermaid Generation:** Integrate LLM to generate C4/Sequence diagrams.
- [ ] **Agentic RAG:** Implement the "Chat with Codebase" endpoint.

## Context Files
- `agent_docs/tech_stack.md`: Specific library versions (Next.js 15, Tailwind 4, etc.).
- `agent_docs/product_requirements.md`: The FR-001 to FR-019 list.
- `agent_docs/testing.md`: How to audit the generated code.

## Project Structure

```text
autowiki/
├── docker-compose.yml      # Orchestration
├── .env.example            # Env template
├── frontend/               # Next.js Application
│   ├── app/                # App Router Pages
│   ├── components/         # UI Components
│   ├── lib/                # Utilities (API Client)
│   └── Dockerfile
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── core/           # Core Config & Logging
│   │   ├── api/            # Route Definitions
│   │   ├── services/       # Business Logic (Parser, LLM, Vector)
│   │   └── models/         # Pydantic Models & DB Schema
│   ├── data/               # Mounted Persistence (SQLite, VectorDB)
│   ├── requirements.txt
│   └── Dockerfile
└── agents.md               # This file
```

## What NOT To Do
- Do NOT use simple text splitting for code; usage of **Tree-sitter** is mandatory.
- Do NOT hardcode LLM keys; use environment variables or user settings.
- Do NOT complicate the MVP with distributed storage (NFS/S3) yet; stick to Local FS.