---
description: Database operations (query, status, reset)
---

Perform database operations for PromptLab using the PostgreSQL MCP server.

## Common Queries

- Recent requests: `SELECT * FROM requests ORDER BY created_at DESC LIMIT 10`
- Count by model: `SELECT model, COUNT(*) FROM requests GROUP BY model`
- Organizations: `SELECT * FROM organizations`
- API keys: `SELECT id, org_id, name, created_at FROM api_keys`

## Tables
- `organizations` - Multi-tenant isolation
- `api_keys` - API key management
- `requests` - Logged LLM requests with metrics
- `prompts`, `prompt_versions` - Prompt templates
- `test_suites`, `test_cases`, `test_runs`, `test_results` - Testing

Use the MCP postgres server to execute queries.
