---
description: Run PromptLab tests (backend pytest, frontend if available)
---

Run the test suite for the PromptLab project.

## Backend Tests
Run pytest for the backend with coverage:
```bash
cd backend && uv run python -m pytest -v --tb=short
```

## What to do:
1. Run the backend tests using pytest
2. Report which tests passed/failed
3. If there are failures, analyze the error messages and suggest fixes
4. Summarize the test coverage if available

If the user specifies a specific test file or pattern, run only those tests.
