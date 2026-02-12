# Tech Stack & Architecture

## Core Components
- **Frontend:** Next.js 15.3.1, React 19, TypeScript.
- **Styling:** Tailwind CSS 4, `next-themes` (Dark Mode default).
- **Backend:** Python 3.10+, FastAPI.
- **Orchestration:** AgentScope (for managing Agent state machines).
- **Parsing:** `tree-sitter` (Python bindings) for AST extraction.
- **Database:** SQLite (Metadata), Chroma or FAISS (Vector Embeddings - Local).
- **Infrastructure:** Docker Compose.

## Key Libraries
- **LLM Interface:** Google Generative AI SDK (Gemini), OpenAI SDK (Generic).
- **Visualization:** Mermaid.js (Frontend rendering).

## Architecture Diagram (Mental Model)
Frontend <-> FastAPI <-> AgentScope <-> Tree-sitter <-> Local FS / Vector DB