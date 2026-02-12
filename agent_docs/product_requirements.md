# Product Requirements (MVP)

## Core Value
Solving "Documentation Debt" by turning code into "Living Docs".

## Critical Functional Requirements
* **FR-002 (Hybrid Parsing):** Must use AST + LLM. Tree-sitter for skeleton, LLM for explanation.
* **FR-003 (Smart Chunking):** Cluster based on file dependency graphs, not just lines.
* **FR-006 (Mermaid):** Auto-generate System Architecture (C4), Sequence, and ER diagrams.
* **FR-009 (Steerability):** Prioritize `.autowiki.json` for structure definition.
* **FR-012/013 (Agentic RAG):** Sidebar chat with context-awareness and multi-step reasoning.

## UX/UI Requirements
* **Theme:** Dark Mode First (Reference: Zed Editor / GitHub Dark Dimmed).
* **Layout:** Three-Column "Holy Grail" (Nav - Content - Context/Chat).
* **Dashboard:** "Glassy" Project Cards.

## Performance
* Indexing 100k LOC < 5 mins.