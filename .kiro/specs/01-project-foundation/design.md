# Design: Project Foundation

## Folder Structure

Following `tech.md`'s "structure by resource/domain, not by technical
layer" rule, applied at foundation scale — there are no resources yet,
so this lays out the shared scaffolding those resources will plug into.

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # creates the FastAPI() instance, mounts
│   │                           # routers, registers CORS + startup checks
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings loader (env vars), validated at import time
│   │   └── supabase_client.py   # factory for the Supabase client (constructed lazily;
│   │                             # not called by /health in this spec)
│   └── health/
│       ├── __init__.py
│       └── router.py            # GET /health
├── .env.example                 # committed template of required env vars
├── .env                         # gitignored, real local values
├── .gitignore                   # already exists (venv/, __pycache__/)
└── requirements.txt              # already exists
```

Rationale:
- `app/core/` holds cross-cutting concerns (config, the Supabase client
  factory) that every future resource module (`app/products/`,
  `app/services/`, etc.) will import — it is not itself a "resource."
- `app/health/` is treated as its own small resource module rather than
  inlining the route in `main.py`, so `main.py` stays a thin composition
  point (`app = FastAPI()`, `app.include_router(...)`, middleware setup)
  as more routers are added in later specs.
- `supabase_client.py` is included now as a **factory function** (e.g.
  `get_supabase_client()`) so later specs can start importing/using it
  immediately, but this spec does not call it from any route —
  `/health` stays dependency-free on purpose.

## Configuration (`app/core/config.py`)

- Use `pydantic`'s settings pattern (Pydantic is already a dependency)
  to define a `Settings` model:
  - `supabase_url: str`
  - `supabase_service_role_key: str`
  - `supabase_jwt_secret: str` (placeholder for the next spec's auth
    work; required now so the shape doesn't change later — the value can
    just be present in `.env`, unused until auth middleware exists)
  - `cors_allowed_origins: list[str]` (parsed from a comma-separated env
    var, defaulting to `http://localhost:5173` for local dev)
- Settings are instantiated **once** at import time (module-level
  singleton), so a missing required variable raises immediately on
  startup — not on first incoming request.
- `python-dotenv` loads `.env` before `Settings` is constructed (either
  via `load_dotenv()` explicitly in `config.py`, or via Pydantic's
  built-in dotenv support if using `pydantic-settings` — note:
  `pydantic-settings` is **not** currently in `requirements.txt`; if used,
  add it explicitly as a new pinned dependency rather than assuming it's
  present).

## `/health` Endpoint (`app/health/router.py`)

- `GET /health` → `200 OK`, body: `{"status": "ok"}`.
- No dependencies on `Settings` beyond the app having started
  successfully, and no Supabase client call — keeps liveness checking
  independent of database availability.
- Registered with no auth dependency, since Phase 1's auth middleware
  doesn't exist yet and `/health` is explicitly meant to stay public per
  `architecture.md`.

## CORS Setup (`app/main.py`)

- Use FastAPI's `CORSMiddleware`.
- Allowed origins come from `Settings.cors_allowed_origins`, not a
  hardcoded list, so adding a staging/production frontend origin later
  is a config change, not a code change.
- Allow methods: at minimum `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`
  (future resource routes will need all of these; no reason to restrict
  now and revisit per-endpoint).
- Allow headers: include `Authorization` and `Content-Type` explicitly —
  `Authorization` isn't used yet in this spec, but the next spec's JWT
  bearer tokens will need it, and adding it now avoids a second CORS
  config touch.
- `allow_credentials`: not required for a bearer-token approach (no
  cookies involved), so leave `False` unless a reason to change this
  surfaces later.

## Startup Validation

- `main.py` imports `Settings` at module load time (not inside a request
  handler), so `uvicorn app.main:app` fails immediately with a readable
  Pydantic validation error if a required env var is missing, rather
  than starting successfully and failing later on first real request.

## What This Design Deliberately Excludes

- No Supabase client is actually invoked anywhere in this spec —
  `supabase_client.py` exists as a factory stub for later specs to
  import.
- No JWT verification dependency is implemented — `supabase_jwt_secret`
  is loaded into config only so `.env` and `Settings` don't need
  reshaping when the auth spec arrives.
- No `/api` prefix or resource routers exist yet — `/health` is
  intentionally the only route, mounted at the root path (not under
  `/api`), matching common convention for liveness endpoints.
