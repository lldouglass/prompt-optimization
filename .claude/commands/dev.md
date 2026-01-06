---
description: Start development servers
---

Start the development environment:

1. Kill any existing processes on ports 8000 and 5173
2. Start Backend: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
3. Start Frontend: `cd frontend && npm run dev`
4. Wait for both to be ready
5. Verify backend health: `curl http://localhost:8000/health`
6. Verify frontend: `curl http://localhost:5173`
7. Test dev-login works: `curl -X POST http://localhost:8000/api/v1/auth/dev-login`

Run servers in background. When ready, report:
- Backend: http://localhost:8000 (API docs: http://localhost:8000/docs)
- Frontend: http://localhost:5173

Auto-login is enabled on localhost - just open http://localhost:5173/agents to start testing.
