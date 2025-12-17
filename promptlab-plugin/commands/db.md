---
description: Database operations (query, migrate, seed)
allowed_args:
  - query
  - status
  - reset
---

Perform database operations for PromptLab.

## Available operations:

### `query` (default)
Use the PostgreSQL MCP server to query the database. Common queries:
- List recent requests: `SELECT * FROM requests ORDER BY created_at DESC LIMIT 10`
- Count by model: `SELECT model, COUNT(*) FROM requests GROUP BY model`
- Check organizations: `SELECT * FROM organizations`

### `status`
Check database connection and show table statistics.

### `reset`
Drop and recreate all tables (WARNING: destructive). Only do this if explicitly requested.

## Database Schema Reference:
- `organizations` - Multi-tenant org isolation
- `api_keys` - API key management (key_hash, org_id)
- `requests` - Logged LLM requests with metrics
- `prompts`, `prompt_versions` - Prompt templates
- `test_suites`, `test_cases`, `test_runs`, `test_results` - Testing framework

Use the MCP postgres server to execute queries when available.
