# AI Softwear Company

An operational workspace for an AI-powered software house. It gives a studio one place to intake a project, coordinate specialist AI roles, monitor delivery, and prepare marketing for each launch.

## What is included

- React/Vite workspace for executive overview, project intake, AI office, delivery board, and marketing studio.
- FastAPI API for health, projects, and work items.
- A dependency-free SQLite store for projects and tasks, so office work persists without external infrastructure.
- Existing specialist-agent and workflow modules, ready to be connected behind the core API as integrations are completed.

## Run locally

```powershell
cd frontend
npm install --include=dev
npm run dev
```

In a second terminal with Python 3.11+ available:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

The frontend runs without the API using demo workspace data. When the API is running, it shows a connected status and project intake persists to `backend/data/office.db`. Set `OFFICE_DATABASE` to use a different SQLite file.

## Core API

- `GET /api/status` — platform health
- `GET|POST /api/projects` — list or create projects
- `GET|PATCH /api/projects/{id}` — retrieve or update a project
- `GET|POST /api/tasks` — list or create tasks; filter with `?project_id=`
- `PATCH /api/tasks/{id}` — assign, rename, or move a task
- `POST /api/auth/register` — create an owner account and organization
- `POST /api/auth/login` — create a seven-day bearer-token session
- `GET /api/auth/me` and `POST /api/auth/logout` — inspect or end the active session

Authentication requests return a token. Send it on protected endpoints as `Authorization: Bearer <token>`. Passwords are salted and derived with PBKDF2-SHA256; only the derived value is stored.

## Product direction

See [ROADMAP.md](ROADMAP.md) for the path from this foundation to a fully persistent, agent-orchestrated software company.
