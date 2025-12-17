---
description: Start PromptLab development servers (backend + frontend)
---

Start the PromptLab development environment.

## Instructions:
1. Start the backend server (FastAPI on port 8000):
   ```bash
   cd backend && uv run uvicorn app.main:app --reload --port 8000
   ```

2. Start the frontend server (Vite on port 5173):
   ```bash
   cd frontend && npm run dev
   ```

Run both servers in the background so the user can continue working.

Provide the URLs:
- Backend API: http://localhost:8000
- Frontend Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
