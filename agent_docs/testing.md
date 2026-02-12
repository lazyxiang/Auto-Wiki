# Audit & Testing Strategy ("The Architect" Role)

Since we are using AI to generate complex logic, we must audit:

## 1. ELI5 Audit (Explain Like I'm 5)
* Ask: "Explain how `parser.py` handles syntax errors. Does it crash or skip?"
* Ask: "How does the chunker handle circular dependencies?"

## 2. Security Audit
* **CSRF/CORS:** Ensure FastAPI is configured to allow only localhost:3000 (or configured domains).
* **File Access:** Ensure the parser cannot access files outside the target repo (Path Traversal check).

## 3. Logic Verification
* **AST Check:** Verify that the parser is actually identifying function boundaries and not just guessing based on indentation.
* **Config Priority:** Create a test case where `.autowiki.json` conflicts with the file structure, and ensure the JSON wins.