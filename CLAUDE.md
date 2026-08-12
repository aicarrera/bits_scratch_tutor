# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**CreaBits Tutor** is a web app that tutors children (ages 8–10) learning to program with Scratch. A child enters an anonymous code, picks a Scratch game, and chats with an AI tutor named **"Bit"** that guides them with progressive hints and Socratic questions (never the full answer). Sessions, conversations, messages, and anonymous feedback are persisted for research.

Two independently-deployed apps: a **FastAPI (async) backend** in [backend/](backend/) and a **React 19 + Vite + TypeScript + Tailwind v4 frontend** in [frontend/](frontend/).

## Conventions that will surprise you

- **The domain layer is in Spanish.** Table names, columns, model attributes, enum values, and API field names are Spanish: `juegos`, `sesiones`, `conversaciones`, `mensajes`, `estudiantes`, `versiones_juego`, `feedback_sesion`, etc. Message roles are `"nino"` and `"tutor"`. Session states are `"activa"`, `"abandonada"`, `"finalizada"`. Keep new code in the same language as the surrounding domain — don't introduce English column/field names.
- **The DB schema is NOT created on startup.** `app.main:app` only serves requests. You must run migrations and seed explicitly (see below) or the API returns empty/404s. This is deliberate — see the note in [README.md](README.md).
- **Default database is local SQLite.** With `DATABASE_URL` unset, the backend uses `backend/creabits_dev.db`. Production sets `DATABASE_URL` to PostgreSQL/Supabase. `Settings.async_database_url` rewrites any `postgresql://`/`sqlite:///` URL to its async driver (`+asyncpg` / `+aiosqlite`) — always store the plain URL in `.env`.

## Common commands

### Backend (run from `backend/`)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python scripts/create_tables.py         # applies Alembic migrations (does NOT run at app startup)
python scripts/seed_initial_data.py     # idempotent: loads game catalog + demo students (e.g. tigre-azul-7)
python -m uvicorn app.main:app --reload # dev server on :8000

pytest                                  # all tests (pytest.ini sets asyncio_mode=auto — no @pytest.mark.asyncio needed)
pytest tests/test_services.py           # one file
pytest tests/test_services.py::test_name -v   # one test
alembic upgrade head                    # what create_tables.py wraps; used by the Docker entrypoint
alembic revision --autogenerate -m "msg"      # new migration (versions in backend/alembic/versions/)
```

### Frontend (run from `frontend/`)
```bash
npm install
npm run dev       # Vite dev server (reads VITE_API_URL, defaults to http://127.0.0.1:8000)
npm run build     # tsc -b && vite build
npm run lint      # eslint
npm run preview
```

### Docker (run from repo root)
```bash
docker compose up -d --build   # backend + frontend; backend entrypoint waits for DB, runs alembic + seed, then uvicorn
docker compose logs -f backend
```
Note: the committed `docker-compose.yml` expects an **external** `DATABASE_URL` (Supabase) and bundles only `backend` + `frontend` (nginx). [DEPLOY.md](DEPLOY.md) documents an alternative setup that also runs a bundled PostgreSQL container with a named volume — treat DEPLOY.md as the ops runbook, but verify against the actual compose file before relying on a `db` service.

## Backend architecture

Strict layering, one module per concern (all under [backend/app/](backend/app/)):

```
api/v1/routes/*  → services/*  → repositories/*  → models/tables.py (SQLAlchemy async ORM)
                        │
                     schemas/*  (Pydantic request/response DTOs)
                     services/serializers.py  (ORM → response schema)
```

- **`api/v1/router.py`** mounts all routers under `/api/v1` (`students`, `sessions`, `games`, `conversations`, `admin/students`). `dependencies.py` holds shared deps like `require_admin_code` (checks the `X-Admin-Code` header against `ADMIN_FINISH_CODE`).
- **Services** own business logic and orchestration; **repositories** own all DB queries. Routes stay thin. Don't put queries in services or logic in routes.
- **`db/database.py`** builds the single async engine + `AsyncSessionLocal`; `get_db()` is the FastAPI session dependency.

### The LLM tutor layer ([app/llm/](backend/app/llm/)) — the core of the product

- **`base.py`** defines the `TutorLLM` interface (`async generate_reply(...) -> TutorReply`) and the `TutorReply` dataclass. A reply is **structured**, not just text: `text`, `fase` (`predecir`/`pista`/`confirmar`/`responder`), `bloques_sugeridos` (Scratch blocks to suggest), `opciones_respuesta` (quick-reply chips), `necesita_aclaracion`, `razonamiento_pedagogico`, plus token counts.
- **`factory.py`** picks the implementation from `settings.llm_mode`: `gemini` → `GeminiTutorLLM`, `openrouter` → `OpenRouterTutorLLM`, else `MockTutorLLM`. If the mode is set but the API key is missing, it silently falls back to mock. Add new providers by implementing `TutorLLM` and extending `build_llm`.
- **`gemini.py` / `openrouter.py`** request **structured JSON** (Gemini uses a Pydantic `response_schema`) built from a system prompt = `HINT_PROGRESSION_BASE` + per-game context + the full Scratch block catalog. Suggested blocks returned by the model are **validated against the catalog** (`catalog.py`: `load_bloques`, `bloques_ids`, `bloque_nombre`, `clean_opciones`, `build_game_context`); unknown block IDs are dropped. Both providers **fall back to a safe plain-text reply on any error** — never let a provider raise into the request path.
- Per-game pedagogy (solution, blocks, video, prompts) lives in **`versiones_juego`** rows, not in code. The active `GameVersion` is loaded per message and its `version` becomes the message's `prompt_version` (format `"{game_id}_{version}"`) for later analysis.

### Conversation lifecycle ([services/conversations.py](backend/app/services/conversations.py))

`open_or_resume` is the key entry point: it **resumes** an existing conversation whenever the session was not teacher-closed (reactivating an `abandonada` session), shows a "already completed" modal if the game was teacher-finished, or otherwise creates a fresh session + conversation seeded with the game's `instruccion_nino`. `send_message` persists the child's message, calls the LLM with the last ~14 messages of history, then persists the tutor reply with all structured fields flattened into `metadata_json`.

## Frontend architecture

- **No router library.** [src/App.tsx](frontend/src/App.tsx) is a single state machine over 5 screens: `welcome → assent → selection → chat → feedback`. Navigation is `setScreen` + lifted state (`student`, `sessionId`, `currentGame`, `conversation`). Screens live in [src/pages/](frontend/src/pages/), shared UI in [src/components/](frontend/src/components/).
- **All backend calls go through [src/api/client.ts](frontend/src/api/client.ts)** (the `api` object). It reads `VITE_API_URL` (default `http://127.0.0.1:8000`); in production nginx proxies `/api/` and `/health` to `backend:8000` (see [frontend/nginx.conf](frontend/nginx.conf)). Add new endpoints here, not with ad-hoc `fetch` calls.
- **Session exit paths** all route through feedback first (`cambiar` / `salir` / `finalizar`). Closing the browser tab fires a `navigator.sendBeacon` to `/sessions/:id/abandon` so the session is marked `abandonada` and can be resumed later.
- **Ending a session requires the teacher's admin code** (`ADMIN_FINISH_CODE`), submitted from the chat screen — children cannot finish their own session.

## Configuration (`backend/.env`, see [backend/.env.example](backend/.env.example))

`DATABASE_URL` (unset → SQLite), `LLM_MODE` (`mock`/`gemini`/`openrouter`), `GEMINI_API_KEY` + `GEMINI_MODEL`, `OPENROUTER_API_KEY` + `OPENROUTER_MODEL`, `CORS_ORIGINS` (comma-separated), `ADMIN_FINISH_CODE`. Never commit `.env` or real credentials.
