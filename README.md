# PromptLab

A self-hosted platform for logging, monitoring, and analyzing LLM API calls. Track your OpenAI usage, measure latency, monitor token consumption, and debug prompts through a clean web dashboard.

## Features

- **Automatic Request Logging** - Wrap your OpenAI client to automatically capture all API calls
- **Web Dashboard** - View and analyze requests in a modern React interface
- **Request Details** - Inspect messages, responses, latency, and token usage
- **Organization Support** - Isolate data with API key-based authentication
- **Lightweight SDK** - Non-blocking background logging with minimal overhead

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Your App   │────▶│  PromptLab  │────▶│   OpenAI    │
│             │     │     SDK     │     │     API     │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    (background)
                           │
                           ▼
                   ┌──────────────┐     ┌─────────────┐
                   │   PromptLab  │────▶│  PostgreSQL │
                   │   Backend    │     │             │
                   └──────────────┘     └─────────────┘
                           ▲
                           │
                   ┌──────────────┐
                   │     Web      │
                   │  Dashboard   │
                   └──────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/prompt-optimization.git
cd prompt-optimization
```

### 2. Configure Database

Create a PostgreSQL database and set the connection URL:

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/promptlab
```

### 3. Start Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### 5. Create an API Key

```bash
# Create an organization
curl -X POST http://localhost:8000/api/v1/admin/organizations \
  -H "Content-Type: application/json" \
  -d '{"name": "My Organization"}'

# Response: {"id": "org-uuid-here", "name": "My Organization", ...}

# Create an API key (use the org ID from above)
curl -X POST http://localhost:8000/api/v1/admin/organizations/ORG_ID/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name": "Development"}'

# Response: {"key": "pl_live_xxxxx", ...}
```

Save the `key` value - you'll need it for the SDK and dashboard login.

### 6. Login to Dashboard

Open `http://localhost:5173` and enter your API key to sign in.

---

## SDK Usage

### Installation

```bash
pip install ./sdk
# or
uv add ./sdk
```

### Basic Usage - Automatic Tracking

The simplest way to use PromptLab is to wrap your OpenAI client:

```python
from promptlab import track
from openai import OpenAI

# Wrap the OpenAI client with your PromptLab API key
client = track(OpenAI(), api_key="pl_live_xxxxx")

# Use the client normally - all requests are logged automatically
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
# Output: The capital of France is Paris.
```

That's it! The request is logged in the background without blocking your code.

### Environment Variable

Instead of passing the API key directly, you can set an environment variable:

```bash
export PROMPTLAB_API_KEY=pl_live_xxxxx
```

```python
from promptlab import track
from openai import OpenAI

# API key is read from PROMPTLAB_API_KEY
client = track(OpenAI())
```

### Adding Metadata

You can add custom metadata to track requests:

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
    # PromptLab-specific parameters:
    prompt_slug="greeting-v1",      # Link to a prompt template
    trace_id="user-session-123",    # Group related requests
    tags={"env": "production"},     # Custom tags
)
```

### Manual Logging

For more control, you can log requests manually:

```python
from promptlab import PromptLab

lab = PromptLab(api_key="pl_live_xxxxx")

# Make your API call however you want
# ...

# Then log it
lab.api.log_request({
    "model": "gpt-4",
    "provider": "openai",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ],
    "response_content": "Hi there! How can I help you?",
    "latency_ms": 250,
    "input_tokens": 10,
    "output_tokens": 15,
})
```

### Self-Hosted Backend

If your backend is running on a different URL:

```python
client = track(
    OpenAI(),
    api_key="pl_live_xxxxx",
    base_url="https://promptlab.yourcompany.com"
)
```

---

## API Reference

### Authentication

All authenticated endpoints require a Bearer token:

```
Authorization: Bearer pl_live_xxxxx
```

### Endpoints

#### Health Check

```
GET /health
```

Returns API status.

---

#### Create Organization

```
POST /api/v1/admin/organizations
```

**Body:**
```json
{
  "name": "My Organization"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "My Organization",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### List Organizations

```
GET /api/v1/admin/organizations
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "My Organization",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### Create API Key

```
POST /api/v1/admin/organizations/{org_id}/api-keys
```

**Body:**
```json
{
  "name": "Production Key"
}
```

**Response:**
```json
{
  "id": "uuid",
  "key": "pl_live_xxxxx",
  "key_prefix": "pl_live_xxxx",
  "name": "Production Key",
  "created_at": "2024-01-01T00:00:00Z"
}
```

> **Note:** The full `key` is only returned once at creation time. Store it securely.

---

#### List API Keys

```
GET /api/v1/admin/organizations/{org_id}/api-keys
```

**Response:**
```json
[
  {
    "id": "uuid",
    "key_prefix": "pl_live_xxxx",
    "name": "Production Key",
    "created_at": "2024-01-01T00:00:00Z",
    "last_used_at": "2024-01-02T00:00:00Z"
  }
]
```

---

#### Delete API Key

```
DELETE /api/v1/admin/api-keys/{key_id}
```

**Response:**
```json
{
  "success": true
}
```

---

#### Log Request (Authenticated)

```
POST /api/v1/logs
Authorization: Bearer pl_live_xxxxx
```

**Body:**
```json
{
  "model": "gpt-4",
  "provider": "openai",
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"}
  ],
  "response_content": "Hi there!",
  "latency_ms": 250,
  "input_tokens": 15,
  "output_tokens": 10,
  "parameters": {"temperature": 0.7},
  "prompt_slug": "greeting-v1",
  "trace_id": "session-123",
  "tags": {"env": "prod"}
}
```

**Required fields:** `model`, `provider`, `messages`

**Response:**
```json
{
  "id": "uuid",
  "org_id": "uuid",
  "model": "gpt-4",
  "provider": "openai",
  "messages": [...],
  "response_content": "Hi there!",
  "latency_ms": 250,
  "input_tokens": 15,
  "output_tokens": 10,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

#### List Requests (Authenticated)

```
GET /api/v1/requests
Authorization: Bearer pl_live_xxxxx
```

**Query Parameters:**
- `limit` (int): Max results (default: 50)
- `offset` (int): Pagination offset

**Response:**
```json
[
  {
    "id": "uuid",
    "model": "gpt-4",
    "provider": "openai",
    "messages": [...],
    "response_content": "...",
    "latency_ms": 250,
    "input_tokens": 15,
    "output_tokens": 10,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### Get Request (Authenticated)

```
GET /api/v1/requests/{request_id}
Authorization: Bearer pl_live_xxxxx
```

**Response:** Single request object

---

## Dashboard

### Login

Enter your API key on the login page. The key is stored locally in your browser.

### Requests View

The main dashboard shows:

- **Total Requests** - Count of logged requests
- **Total Tokens** - Sum of input + output tokens
- **Avg Latency** - Average response time

Click any request to view details including:
- Full message history
- Response content
- Model and provider
- Token counts
- Trace ID (if set)

### Settings

Manage API keys for your organization:
- Create new keys
- View existing keys (prefix only)
- Delete keys

---

## Project Structure

```
prompt-optimization/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── config.py       # Settings management
│   │   ├── database.py     # Database connection
│   │   ├── auth.py         # API key authentication
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # API endpoints
│   │   └── schemas/        # Pydantic schemas
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/                # React dashboard
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # UI components
│   │   └── lib/            # Utilities and API client
│   ├── package.json
│   └── vite.config.ts
└── sdk/                     # Python SDK
    ├── promptlab/
    │   ├── client.py       # Main client and tracking
    │   └── api.py          # API wrapper
    └── pyproject.toml
```

---

## Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `API_KEY_PREFIX` | Prefix for generated API keys | `pl_live_` |

### SDK Environment Variables

| Variable | Description |
|----------|-------------|
| `PROMPTLAB_API_KEY` | Default API key for SDK |
| `PROMPTLAB_BASE_URL` | Backend URL (default: `http://localhost:8000`) |

---

## Development

### Running Tests

```bash
# Backend
cd backend
uv run pytest

# SDK
cd sdk
uv run pytest
```

### Building Frontend

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/`

---

## License

MIT
