---
description: Start development servers
---

Start PromptLab development environment:

1. Backend (FastAPI): `cd backend && uv run uvicorn app.main:app --reload --port 8000`
2. Frontend (Vite): `cd frontend && npm run dev`

Run both in background. URLs:
- API: http://localhost:8000
- Dashboard: http://localhost:5173
- Docs: http://localhost:8000/docs
