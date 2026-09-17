# AI Career Intelligence Platform

A full-stack app that matches a resume against a job posting and tells
you exactly what's missing. Upload a resume, pick a job, and get a
match score, a matched/missing skills breakdown, and AI-generated
advice on how to close the gap — backed by a RAG pipeline over a
vector store for the career-assistant Q&A.

## Features

- **Auth** — JWT-based register/login (`passlib` + `python-jose`).
- **Resume upload & parsing** — PDF upload, text extraction (`pymupdf`),
  skill extraction via a normalized skill taxonomy.
- **Job matching** — skill-overlap match score between a resume and a
  job posting.
- **Career analysis** — match score + matched/missing skills +
  prioritized recommendations.
- **AI career advice** — LLM-generated advice (Groq) on closing the
  skill gap for a specific job/resume pair.
- **Career assistant** — free-form Q&A about a job/resume pairing,
  grounded with retrieval over a Chroma vector store (RAG).

## Tech stack

| Layer    | Tech |
|----------|------|
| Frontend | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS |
| Backend  | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Auth     | JWT (`python-jose`), `passlib`/`bcrypt` password hashing |
| AI/RAG   | Groq (LLM inference), ChromaDB (vector store, default embeddings) |
| Database | SQLite by default (swap `DATABASE_URL` for Postgres) |

## Project structure

```
backend/
  app/
    api/v1/        # FastAPI routers (auth, users, jobs, resumes)
    services/      # business logic (matching, RAG, AI advice, parsing)
    repositories/   # data access
    models/         # SQLAlchemy models
    schemas/        # Pydantic request/response schemas
    tests/          # pytest suite
frontend/
  app/              # Next.js App Router pages
  components/       # shared UI components
  lib/              # API client + auth context
Project Documentation/   # BRD/SRS, architecture, ER diagrams, API spec, etc.
```

## Running locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in GROQ_API_KEY to enable AI features
uvicorn app.main:app --reload --port 8000
```

The API is served at `http://localhost:8000`; interactive docs at
`http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Environment variables

**`backend/.env`** (see `backend/.env.example`)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQLAlchemy connection string (defaults to local SQLite) |
| `JWT_SECRET` | Secret used to sign access tokens — set a real value outside dev |
| `GROQ_API_KEY` | Enables `/ai-advice` and `/assistant` endpoints |

**`frontend/.env.local`** (see `frontend/.env.local.example`)

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | Base URL of the backend API |

## Running with Docker

Requires Docker Desktop (or Docker Engine + Compose plugin).

```bash
cp .env.example .env     # fill in JWT_SECRET, POSTGRES_PASSWORD, GROQ_API_KEY
docker compose up --build
```

This starts three containers:

| Service | URL | Notes |
|---------|-----|-------|
| `frontend` | http://localhost:3000 | Next.js, standalone build |
| `backend` | http://localhost:8000 | FastAPI, docs at `/docs` |
| `db` | — | Postgres 16, data persisted in a named volume |

The vector store (`chroma_data`) and uploaded resumes (`resumes_data`)
are also persisted in named Docker volumes, so they survive
`docker compose down` (use `docker compose down -v` to wipe everything).

`NEXT_PUBLIC_API_URL` is baked into the frontend at **build** time
(Next.js inlines `NEXT_PUBLIC_*` vars at build, not runtime) — if you
change it in `.env`, re-run with `--build` for it to take effect.

To stop: `docker compose down`.

## Tests

```bash
cd backend
pytest
```

## Documentation

The `Project Documentation/` folder contains the full design process
this project was built from: business requirements, architecture
(HLD/LLD/ADRs), ER diagrams, API spec, AI/RAG design, infra plan,
threat model, and test plan.

## Known limitations / next steps

- No live deployment yet — see `Project Documentation/06_DevOps` for the
  planned Docker/CI setup.
- Job postings are creatable by any authenticated-looking request (no
  employer/admin role separation yet).
- Database migrations aren't wired up (`alembic/` scaffolding exists
  but isn't in the dependency chain — schema is created via
  `create_all` on startup).
