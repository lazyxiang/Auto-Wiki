# **Product Requirements Document: Intelligent Code Knowledge Base Generator "AutoWiki"**

## **1. Product Overview & Strategic Vision**

### **1.1 Background: The "Documentation Debt" Crisis in Software Engineering**

In today's Software Development Life Cycle (SDLC), documentation maintenance has become a core bottleneck hindering team agility. With the prevalence of CI/CD pipelines, code iteration speeds have reached hourly or even minute-level frequency, while traditional documentation updates remain stuck in the manual Markdown or Confluence page writing stage. This disconnect in rates leads to severe **"Documentation Debt"**—documentation becomes inconsistent with code logic, misleading developers, increasing onboarding costs for new hires, and heightening system maintenance risks.

Simultaneously, the expansion of Large Language Model (LLM) context windows (e.g., GLM-4's 128k or GPT-4's 128k+) provides the technical foundation to solve this problem. Market pioneers like **DeepWiki (Devin AI)** and **Zread (Zhipu AI)** have validated the feasibility of "Code as Documentation." DeepWiki achieves deep semantic understanding of code and visual architecture generation through Agents, while Zread reshapes the readability of open-source projects through structured reading experiences and project health analysis.

### **1.2 Product Definition: AutoWiki**

**AutoWiki** is defined as an enterprise-grade intelligent code knowledge base generation platform. It is not just a documentation generator, but an **Agentic Hub** based on the **Model Context Protocol (MCP)**. It automatically connects to GitHub/GitLab repositories, utilizing a combination of AST (Abstract Syntax Tree) parsing and LLM semantic analysis to transform obscure codebases into structured, visual, and interactive Wikis.

AutoWiki's core design philosophy is **"Structured Autonomy"**: combining **"Steerability"**—allowing architects to intervene in the documentation generation logic via configuration files—with an "Immersive Reading Experience"—providing an e-book-like dual-column reading interface and interactive Q&A.

### **1.3 Core Value Proposition**

AutoWiki aims to solve industry pain points through the following core values:

| Value Dimension | Traditional Pain Point | AutoWiki Solution | Reference Competitor Feature |
| :---- | :---- | :---- | :---- |
| **Timeliness** | Documentation lags behind code commits, leading to obsolete information. | **Living Docs**: Integrated Webhooks; code commits trigger incremental documentation updates immediately. | DeepWiki Auto-Indexing |
| **Readability** | Code logic is complex, lacking a high-level architectural perspective. | **Visual Intelligence**: Automatically generates Mermaid architecture diagrams, sequence diagrams, and ER diagrams. | DeepWiki Architecture Maps |
| **Accuracy** | AI-generated content is prone to hallucinations and lacks focus. | **Steerability**: Supports `.autowiki.json` config files, allowing humans to define documentation structural priorities. | Devin `.wiki.json` |
| **Interactivity** | Static documentation cannot answer specific logical questions. | **Agentic RAG**: Built-in AI assistant for "Chat with Codebase," supporting multi-step reasoning and precise citations. | Zread Q&A, DeepWiki Ask |

## **2. Target User Personas**

To ensure targeted feature design, we need to deeply analyze three core user types and their behavioral patterns.

### **2.1 Persona A: "The Explorer" (New Contributor)**

* **Role Description:** Junior/Mid-level developers just joining a team, or external contributors trying to submit their first PR to an open-source project.
* **Core Pain Points:** Facing a massive Monorepo or complex microservices architecture, they cannot find the entry point. Lacking context, they often waste days on environment setup and understanding module dependencies.
* **Product Requirements:**
    * **Wiki Caching:** Quickly access **"Getting Started"** guides, eliminating the redundant processing cost of frequent repo visits for Wiki generation.
    * **Architecture Visualization:** High-quality Wikis must include architecture diagrams, integrating Mermaid.js chart generation.
    * **Interactive Exploration:** Based on semantic analysis, keyword search, and combined with RAG, providing code Q&A capabilities that maintain conversation context.

### **2.2 Persona B: "The Architect" (Senior Maintainer)**

* **Role Description:** Tech Leads of projects or core maintainers of open-source libraries.
* **Core Pain Points:**
    * Tired of repeating answers to the same basic architectural questions during PR reviews.
    * Worried that fully automated AI documentation will contain misinformation or focus on irrelevant utility scripts while ignoring core business logic.
* **Product Requirements:**
    * **Strong Desire for Control:** Must be able to intervene in the AI generation process. They need a DeepWiki-style config file (`.devin/wiki.json`) to specify "Required Reading Chapters" and "Ignored Directories."
    * **Accuracy Verification:** AI-generated content needs code citation links for quick verification.

### **2.3 Persona C: "The Auditor" (Tech Auditor)**

* **Role Description:** CTOs, Engineering Managers, or third-party developers conducting technology selection.
* **Core Pain Points:** Need to quickly assess a project's architecture, tech stack, security risks, and popularity without reading the code.
* **Product Requirements:**
    * **Cross-Repo Analysis:** Modern microservices often span multiple Git Repos; needs the ability to trace cross-service API calls and generate system-level Wikis.
    * **Security & Compliance:** Supports multiple deployment modes (Self-hosted/SaaS) and custom model selection. For internal enterprise projects, it must ensure internal code data is not leaked.

## **3. Functional Requirements**

This section details the core functional modules of AutoWiki.

### **3.1 Intelligent Indexing & Generation**

#### **3.1.1 Multi-Source Repository Ingestion**
The system must support seamless integration with mainstream code hosting platforms.

* **FR-001 (Multi-Source Support):** Supports GitHub, GitLab (SaaS & Self-hosted), and Bitbucket access via HTTP/SSH protocols.
* **FR-002 (Hybrid Parsing Strategy):** Adopts a **AST (Abstract Syntax Tree) + LLM** hybrid parsing mode. This method is more precise and token-efficient than pure LLM scanning.
    1.  Use Tree-sitter to extract code skeletons (classes, function signatures, inheritance relationships), generating corresponding embeddings and precise dependency graphs stored in vector and graph databases respectively.
    2.  Feed core logic blocks to the LLM to generate semantic explanations.
* **FR-003 (Large Repo Chunking):** For massive repositories exceeding 1GB or million lines of code, implement **Smart Chunking**. The system should cluster based on file dependency graphs rather than simple directory splitting, ensuring cross-file logical context is not lost.

#### **3.1.2 Multi-Model Provider Integration**
* **FR-004 (Multi-LLM Provider Support):** Support Google's gemini-3-pro-preview / gemini-3-flash-preview, OpenRouter's gpt-5-nano, Dashscope's qwen-plus, BigModel's glm-4.7, DeepSeek's deepseek-v3.2, Ollama local models, etc.
* **FR-005 (Multi-Embedding Provider Support):** Support Google's text-embedding-004, and Ollama local embedding models, etc.

#### **3.1.3 Automated Visualization**
To replicate DeepWiki's visual advantages, AutoWiki must possess automated charting capabilities. 
* **FR-006 (Mermaid Chart Integration):** The system must automatically insert Mermaid.js code blocks into the documentation and render them in real-time on the frontend.
* **FR-007 (Chart Type Coverage):**
    * **System Architecture (C4 Model):** Shows high-level module interactions.
    * **Sequence Diagrams:** Automatically traces key API call chains (e.g., Controller -> Service -> Repository).
    * **ER Diagrams (Entity-Relationship):** Automatically generates database structure diagrams based on ORM model files (e.g., Prisma schema, TypeORM entity).
* **FR-008 (Interactive Zoom):** Frontend rendered SVG charts must support click-to-zoom and drag-to-pan for viewing complex architectural details.

#### **3.1.4 "Steerable" Document Generation**
This is the key differentiator between a "toy" and a "productivity tool," directly referencing DeepWiki's `.devin/wiki.json` design.

* **FR-009 (Config File Parsing):** During the indexing phase, the system must prioritize looking for an `.autowiki.json` file in the root directory.
* **FR-010 (Schema Definition):**
    The configuration file should support the following structure:
    ```JSON
    {
      "repo_notes": "...",
      "pages": [
          {
            "title": "Payment System Architecture",
            "target_files": ["src/payments/**", "src/checkout/**"],
            "parent": "System Architecture"
          }
      ],
      "ignore": ["legacy/**", "scripts/**"]
    }
    ```
* **FR-011 (Hybrid Planning Mode):** If no configuration file is provided, the system falls back to the default "Cluster-based Planning" mode, automatically generating a directory structure based on code similarity; if a configuration is provided, it strictly follows human instructions and only automatically supplements undefined areas.

### **3.2 Agentic RAG Q&A System**

Reference DeepWiki's "Ask" feature to build a deep Q&A experience.

* **FR-012 (Context-Aware Sidebar):** When a user reads a specific chapter of the document (e.g., "Payment Module"), the right-side AI assistant's initial Prompt should automatically load the context of that module.
* **FR-013 (Multi-Step Reasoning Agent):** The Q&A system should not just be simple RAG, but possess Agent capabilities.
    * *Scenario:* User asks "If I modify the User model, which APIs will be affected?"
    * *Execution:* Agent first retrieves the User model definition, then uses the dependency graph to reverse-lookup Controllers referencing that model, and finally summarizes the list of affected endpoints.
* **FR-014 (Precise Citations):** Every AI response must include clickable footnotes, such as ``, jumping directly to the code line to eliminate hallucinations.

### **3.3 Wiki Caching**

* **FR-015 (Cache Reuse):** Display a dashboard of recently completed Wiki generation projects on the homepage. Support refreshing, allowing users to explore on their own and directly view cached Wikis when navigating to a project page.
* **FR-016 (Periodic Updates):** Record the generation time of each project's Wiki. A re-generation can only be triggered if the document is older than one week.

### **3.4 Scalability**
This MVP implementation aims to remain simple, reducing reliance on external services, but needs to define stable interfaces for future integration and expansion.

* **FR-017 (Storage Extensibility):** MVP uses the local file system to store generated Project Wikis. Future expansion to NFS distributed file systems or Object Storage Services.
* **FR-018 (RDBMS Extensibility):** MVP uses SQLite to store Project Wiki metadata. Future expansion to MySQL, PostgreSQL, etc.
* **FR-019 (Vector DB Extensibility):** MVP uses FAISS with the local file system for high-performance vector similarity operations. Future expansion to Pinecone, Weaviate, Milvus, etc.

## **4. UX & UI Design**

### **4.1 General Design Principles**
Establishing the visual tone before specific pages:
* **Dark Mode First:** Default to a dark theme (reference Zed Editor or GitHub Dark Dimmed) to suit developers' long-usage habits and highlight syntax coloring. Optional light theme with one-click toggle.
* **Typography:** Use high-readability serif fonts (body) combined with sans-serif (UI elements).
* **Interaction:** Reduce page jumps; use side drawers and modals to maintain context.

### **4.2 Core Page Layouts**

#### **4.2.1 Page 1: Home Dashboard**
The gateway to knowledge, emphasizing "Exploration" and "Discovery."

* **Layout:** Center-focused. Top feature bar, central core search, bottom project card stream.
* **Modules:**
    * **Top Nav:** Logo, User Avatar, Theme Toggle.
    * **Core Search:** Oversized input box (similar to Perplexity/Google). Supports GitHub URL input or keyword search.
    * **Project Showcase:** Grid layout of "Recent / Popular Projects".
* **Project Card Design:**
    * Header: Project Icon + Name (Bold).
    * Body: Project Description (Max 3 lines).
    * Bottom: Tags (#React, #LLM), Star Count, Last Updated.
    * Hover: Card floats slightly, showing "Read Now" button.

#### **4.2.2 Page 2: Wiki Workspace** The core page, adopting a classic **Three-Column Layout (Holy Grail Layout)**, mimicking an IDE but biased towards reading.

* **Header:** Fixed top, narrow height. Contains Breadcrumbs, Project Name, Outline Edit (Modal), Share, Export.
* **Left: Wiki Navigation:** Tree View structure with multi-level folding and current section highlighting.
* **Middle: Main Content:** Large line height, comfortable font size (16px-18px). Markdown rendering with LaTeX, Mermaid, and Code Highlighting support.
* **References & Context:**
    * List of source code files or web links referenced in the current paragraph.
    * Clicking a reference expands the raw code snippet or summary without jumping pages.
* **Floating Copilot (Bottom):**
    * **UI:** Floating Capsule or Bottom Panel.
    * **Mode Toggle:**
        1.  **⚡ Fast Mode:** RAG-only. For questions about current Wiki content. (Yellow/Blue Lightning Icon).
        2.  **🧠 Deep Research:** Agentic Search + Code Analysis + CoT. For deep reasoning questions. (Purple Brain Icon). Shows "Thinking..." steps.

### **4.3 User Flow**
1.  **Start:** User enters Home.
2.  **Input:** Enters GitHub URL or Keywords.
3.  **Wait:** System displays generation animation (Outline generation -> Content filling).
4.  **Read:** Enters Project Doc page, browses left nav.
5.  **Explore:** Reads middle content, checks right-side references.
6.  **Query:** Uses bottom Fast Mode for questions.
7.  **Deep Dive:** Finds missing content, switches to Deep Research mode to ask AI to supplement.
8.  **Edit:** Clicks top Wiki Outline Edit to solidify supplemented info into the document.

## **5. Key Data Flows**

### **5.1 Flow 1: Ingestion Pipeline**
1.  **Trigger:** User input or Webhook Push.
2.  **Clone & Clean:** Docker clone -> `.gitignore` + binary/lock file filtering.
3.  **AST Analysis:** Tree-sitter extracts Symbol table & Import/Export relations. Batch embeddings. Generate **Dependency Graph**. Cluster into hierarchical module tree.
4.  **Planning:**
    * Check for `.autowiki.json`.
    * **Case A (Config):** Map dependency graph nodes to defined pages.
    * **Case B (No Config):** Call LLM Planning Agent for directory structure suggestions.
5.  **Generation:** Bottom-up generation. Sub-modules generate Markdown + Mermaid; Parent modules aggregate summaries.
6.  **Persistence:** Markdown to file; Embeddings to local FS; Relations to SQLite.

### **5.2 Flow 2: Agentic RAG Query**
1.  **Intent Recognition:** Router Agent determines if the query is "How-to" (needs code retrieval) or conceptual.
2.  **Hybrid Retrieval:** Semantic Search (Vector) + Structural Search (SQL/Graph DB).
3.  **Re-ranking:** Use Rerank model (e.g., bge-reranker).
4.  **Synthesis:** LLM synthesizes answer + generates new Mermaid diagrams.
5.  **Citation:** Post-processing script inserts hyperlinks to code locations.

## **6. Non-Functional Requirements (NFRs)**

### **6.1 Performance**
* **NFR-001 (Indexing Efficiency):** 100k LOC medium project: Initial full index < **5 mins**. Incremental update < **30 seconds**.
* **NFR-002 (Response Speed):** Doc Page TTFB < 200ms. AI Chat TTFT < 1.5s.
* **NFR-003 (Concurrency):** Support 5 concurrent Deep Research sessions per tenant.

### **6.2 Security & Compliance**
* **NFR-004 (Zero-Retention):** Force privacy mode on LLM APIs (e.g., Azure OpenAI Privacy Policy) to ensure code is not used for training.
* **NFR-005 (Data Isolation):** Strict multi-tenant isolation. Vector Indices must be physically or logically separated.
* **NFR-006 (PII Filtering):** PII Scanner must mask hardcoded keys, emails, and IPs before sending code to LLM.

### **6.3 Reliability**
* **NFR-007 (Hallucination Suppression):** If retrieval confidence is low (e.g., < 0.6), AI must explicitly state "Information not found," forbidding fabrication of code or filenames.
* **NFR-008 (Fallback Strategy):** If LLM provider is down, degrade to pure AST mode (show directory structure and code graph only).

## **7. Technical Architecture Blueprint**

| Layer | Tech Stack Suggestion | Responsibility |
| :---- | :---- | :---- |
| **Frontend** | React 19, Next.js 15.3.1, TypeScript | UI Rendering & Client Logic |
| **Styling** | Tailwind CSS 4, next-themes | Responsive Design & Theming |
| **Backend** | Python (FastAPI) | API Server & Business Logic |
| **Agent Framework** | AgentScope | Manage Agent State Machine, Plan Retrieval Paths, Call LLM API |
| **Parsing Layer** | Tree-sitter | Static Code Analysis, AST Extraction, Dependency Calculation |
| **RDBMS Layer** | SQLite / MySQL / PostgreSQL | User Data, Repo Config (.json), Structural Tree, Metadata |
| **Vector Layer** | FAISS / Pinecone / Weaviate / Milvus | Store Document & Code Embeddings |
| **Task Layer** | Job Queue (SQLite / ZeroMQ / Redis) | Async processing of time-consuming indexing & generation tasks |

## **8. Summary & Future Outlook**

AutoWiki does not aim to replace developers writing documentation, but to eliminate repetitive labor in documentation maintenance, allowing developers to focus on decisions rather than description. Through **Steerable Architecture**, we ensure depth and accuracy; through **User Experience Design**, we ensure readability and usability.

In the future (2025-2026), AutoWiki will evolve from "One-way Generation" to "Two-way Synchronization." When a user modifies business logic descriptions in the Wiki interface, the Agent will be capable of reverse-submitting a Pull Request to the codebase, truly realizing the "Documentation as Code" loop. Furthermore, with the proliferation of MCP protocols, AutoWiki will become an indispensable "External Brain" within IDEs, Chatbots, and even CI/CD pipelines.

#### **References**

1.  DeepWiki - Devin Docs, Accessed Jan 5, 2026, [https://docs.devin.ai/work-with-devin/deepwiki](https://docs.devin.ai/work-with-devin/deepwiki)
2.  Zhipu AI Launches Zread: Convert GitHub Projects into Clear User Manuals with One Click - A Must-Have Tool for Developers - AIBase, Accessed Jan 5, 2026, [https://www.aibase.com/news/19847](https://www.aibase.com/news/19847)
3.  Zread GitHub Documentation Tool Transforms Repos into Structured Manuals - Gaoxiao Manong, Accessed Jan 5, 2026, [https://www.xugj520.cn/en/archives/zread-github-tool.html](https://www.xugj520.cn/en/archives/zread-github-tool.html)
4.  Merge the Agent panel back into Zed's text-based discussions #30187 - GitHub, Accessed Jan 5, 2026, [https://github.com/zed-industries/zed/discussions/30187](https://github.com/zed-industries/zed/discussions/30187)
5.  Devin AI Introduces DeepWiki: A New AI-Powered Interface to Understand GitHub Repositories - MarkTechPost, Accessed Jan 5, 2026, [https://www.marktechpost.com/2025/04/27/devin-ai-introduces-deepwiki-a-new-ai-powered-interface-to-understand-github-repositories/](https://www.marktechpost.com/2025/04/27/devin-ai-introduces-deepwiki-a-new-ai-powered-interface-to-understand-github-repositories/)
6.  We wrote a blog post detailing how we implemented our agentic RAG system. Also AMA!, Accessed Jan 5, 2026, [https://www.reddit.com/r/Rag/comments/1jlbwhg/we_wrote_a_blog_post_detailing_how_we_implemented/](https://www.reddit.com/r/Rag/comments/1jlbwhg/we_wrote_a_blog_post_detailing_how_we_implemented/)
7.  LLM Security in 2025: Risks, Mitigations & What's Next - Mend.io, Accessed Jan 5, 2026, [https://www.mend.io/blog/llm-security-risks-mitigations-whats-next/](https://www.mend.io/blog/llm-security-risks-mitigations-whats-next/)
8.  I Rebuilt DevinAI's $300K DeepWiki in 60 Minutes with Gemini : r/GoogleGeminiAI - Reddit, Accessed Jan 5, 2026, [https://www.reddit.com/r/GoogleGeminiAI/comments/1kbl94l/i_rebuilt_devinais_300k_deepwiki_in_60_minutes/](https://www.reddit.com/r/GoogleGeminiAI/comments/1kbl94l/i_rebuilt_devinais_300k_deepwiki_in_60_minutes/)
9.  CodeWiki: Research-Grade Repository Documentation at Scale - Reddit, Accessed Jan 5, 2026, [https://www.reddit.com/r/LocalLLaMA/comments/1osmnlp/codewiki_researchgrade_repository_documentation/](https://www.reddit.com/r/LocalLLaMA/comments/1osmnlp/codewiki_researchgrade_repository_documentation/)
10. MermaidSeqBench: An Evaluation Benchmark for LLM-to-Mermaid Sequence Diagram Generation - arXiv, Accessed Jan 5, 2026, [https://arxiv.org/html/2511.14967v1](https://arxiv.org/html/2511.14967v1)
11. Wiki Generation Guide - DeepWiki-Open, Accessed Jan 5, 2026, [https://asyncfunc.mintlify.app/guides/wiki-generation](https://asyncfunc.mintlify.app/guides/wiki-generation)
12. Release Notes - Devin Docs, Accessed Jan 5, 2026, [https://docs.devin.ai/release-notes/overview](https://docs.devin.ai/release-notes/overview)
13. DeepWiki Uncovered: How I Tamed a Monstrous Codebase in an Afternoon - Skywork.ai, Accessed Jan 5, 2026, [https://skywork.ai/skypage/en/DeepWiki-Uncovered-How-I-Tamed-a-Monstrous-Codebase-in-an-Afternoon/1974507427870732288](https://skywork.ai/skypage/en/DeepWiki-Uncovered-How-I-Tamed-a-Monstrous-Codebase-in-an-Afternoon/1974507427870732288)
14. What is RAG? - Retrieval-Augmented Generation AI Explained - AWS, Accessed Jan 5, 2026, [https://aws.amazon.com/what-is/retrieval-augmented-generation/](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
15. Using DeepWiki as your coding companion : r/vibecoding - Reddit, Accessed Jan 5, 2026, [https://www.reddit.com/r/vibecoding/comments/1msv3hy/using_deepwiki_as_your_coding_companion/](https://www.reddit.com/r/vibecoding/comments/1msv3hy/using_deepwiki_as_your_coding_companion/)
16. Zread MCP Server - Overview - Z.AI DEVELOPER DOCUMENT, Accessed Jan 5, 2026, [https://docs.z.ai/devpack/mcp/zread-mcp-server](https://docs.z.ai/devpack/mcp/zread-mcp-server)
17. Model Context Protocol (MCP). MCP is an open protocol that… | by Aserdargun | Nov, 2025, Accessed Jan 5, 2026, [https://medium.com/@aserdargun/model-context-protocol-mcp-e453b47cf254](https://medium.com/@aserdargun/model-context-protocol-mcp-e453b47cf254)
18. Hot take: Dark mode screenshots convert better than light mode. : r/Frontend - Reddit, Accessed Jan 5, 2026, [https://www.reddit.com/r/Frontend/comments/1pscj3i/hot_take_dark_mode_screenshots_convert_better/](https://www.reddit.com/r/Frontend/comments/1pscj3i/hot_take_dark_mode_screenshots_convert_better/)
19. Wave 12 Released! Fresh UI, DeepWiki, Vibe and Replace, Faster Tab and more! : r/windsurf - Reddit, Accessed Jan 5, 2026, [https://www.reddit.com/r/windsurf/comments/1mqal3x/wave_12_released_fresh_ui_deepwiki_vibe_and/](https://www.reddit.com/r/windsurf/comments/1mqal3x/wave_12_released_fresh_ui_deepwiki_vibe_and/)
20. LLM Trends 2025: A Deep Dive into the Future of Large Language Models | by PrajnaAI, Accessed Jan 5, 2026, [https://prajnaaiwisdom.medium.com/llm-trends-2025-a-deep-dive-into-the-future-of-large-language-models-bff23aa7cdbc](https://prajnaaiwisdom.medium.com/llm-trends-2025-a-deep-dive-into-the-future-of-large-language-models-bff23aa7cdbc)
21. Enhancing software development with retrieval-augmented generation - GitHub, Accessed Jan 5, 2026, [https://github.com/resources/articles/software-development-with-retrieval-augmentation-generation-rag](https://github.com/resources/articles/software-development-with-retrieval-augmentation-generation-rag)
22. My LLM coding workflow going into 2026 | by Addy Osmani | Dec, 2025 - Medium, Accessed Jan 5, 2026, [https://medium.com/@addyosmani/my-llm-coding-workflow-going-into-2026-52fe1681325e](https://medium.com/@addyosmani/my-llm-coding-workflow-going-into-2026-52fe1681325e)
23. The Spec-to-Code Workflow: Building Software Using Only LLMs : r/LLMDevs - Reddit, Accessed Jan 5, 2026, [https://www.reddit.com/r/LLMDevs/comments/1p6t3cp/the_spectocode_workflow_building_software_using/](https://www.reddit.com/r/LLMDevs/comments/1p6t3cp/the_spectocode_workflow_building_software_using/)