---
inclusion: always
---

# Tech Stack & Conventions

## Stack Overview

- **Monorepo** with two top-level app folders: `frontend/` and `backend/`,
  plus `database/` (SQL migrations/schema) and `docs/` (architecture
  references). No shared package layer yet — keep it this way until
  there's an actual need to share code between frontend and backend.
- **Frontend**: React 19 + Vite. Plain JS/JSX (no TypeScript configured
  currently — follow existing `.jsx` convention unless the user asks to
  migrate to TS).
- **Backend**: Python, FastAPI.
- **Database**: Supabase (managed PostgreSQL), accessed from the backend
  via the `supabase` Python client (already in `backend/requirements.txt`).
- **Auth**: Supabase Auth (JWT) for staff login. Staff accounts are
  Supabase Auth users; there is no separate custom auth system.
- **Linting**: ESLint (flat config, `eslint.config.js`) on the frontend.

## Backend (FastAPI) Conventions

- Structure by resource/domain, not by technical layer alone:
  `app/products/`, `app/services/`, `app/stock/`, etc., each with its own
  router, Pydantic schemas, and data-access functions. Avoid a single
  giant `main.py` with all routes inline.
- Use Pydantic models for all request/response bodies — no passing raw
  dicts across the API boundary.
- The Supabase **service role key** is a backend-only secret. It must
  never be sent to or used by the frontend. Load it from environment
  variables via `python-dotenv` (already a dependency), never hardcoded.
- All product/service/stock mutations happen through backend endpoints,
  not direct frontend-to-Supabase calls, so business rules (like "stock
  changes must create a movement record") are enforced in one place.
- Prefer explicit REST resource routes: `GET/POST /api/products`,
  `PATCH /api/products/{id}`, `POST /api/products/{id}/stock` (for
  add/reduce stock as an explicit action, not a raw PATCH on quantity),
  `GET /api/products/{id}/movements`.
- Use FastAPI's dependency injection for the Supabase client and for
  auth/staff-session checks, instead of instantiating clients inline in
  route handlers.

## Access Control (Staff Dashboard)

- **Supabase Auth** is the system of record for staff identity — login,
  password management (including reset/forgot-password flows), and
  session/refresh tokens are all handled by Supabase Auth. Do not build a
  custom login/password system.
- **Frontend**: staff log in via the Supabase Auth client SDK (using the
  **anon/public** key only) directly from the React app. On success, the
  frontend holds a Supabase-issued JWT (access token) and attaches it to
  every request to the FastAPI backend as `Authorization: Bearer <jwt>`.
- **Backend**: every protected route depends on a shared FastAPI
  dependency (e.g. `get_current_staff`) that:
  1. Extracts the bearer token from the `Authorization` header.
  2. Verifies it against Supabase (via the Supabase JWT secret/JWKS, or
     by calling Supabase Auth's user-lookup endpoint with the service
     role client).
  3. Rejects the request with `401 Unauthorized` if missing/invalid, and
     otherwise makes the authenticated staff user available to the route.
  - Apply this dependency to all `/api/*` routes that mutate or expose
    business data (products, services, stock, and later inquiries).
    `/health` remains public.
- **Backend never issues or manages passwords** — it only verifies
  tokens that Supabase Auth already issued. Password rules, resets, and
  MFA (if ever added) are Supabase Auth's responsibility, not FastAPI's.
- Keep this JWT-verification dependency staff-only for Phase 1. It is not
  the same mechanism Phase 2's chatbot will use to call the backend —
  the bot is a trusted backend-to-backend client, not a logged-in staff
  session, so it should not be routed through this dependency
  unmodified. Design the bot's own auth (e.g. a service token) when that
  work actually starts.

## Frontend (React) Conventions

- Structure by feature: `src/features/products/`, `src/features/services/`,
  each containing its own components, hooks, and API calls, rather than
  global `components/` and `pages/` dumping grounds.
- Data fetching: use a dedicated fetch/query layer (e.g. a small
  `api/client.js` wrapper around `fetch`, or React Query if the project
  adopts it later) — don't scatter raw `fetch()` calls through components.
- Keep image upload UI resilient to slow uploads (loading state, disable
  submit while in-flight) since product photos will be uploaded to
  Supabase Storage via the backend.
- Component styling follows the existing plain CSS convention
  (`App.css`, `index.css`) unless the user requests a UI library.

## Environment & Secrets

- Backend expects a `.env` file (gitignored) with at least:
  `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and a value usable for JWT
  verification (Supabase's JWT secret, or JWKS URL depending on the
  verification approach chosen during implementation). Never commit this
  file or print its values in logs/output.
- Frontend uses the Supabase **anon/public** key via Vite's
  `import.meta.env` for the Supabase Auth client SDK (login, session
  handling). It never receives or uses the service role key.

## What Not to Do

- Don't introduce a second database, ORM, or backend framework without
  explicit user request — the stack is fixed for now (FastAPI +
  Supabase Postgres).
- Don't build a custom username/password or session system — staff auth
  is Supabase Auth (JWT) end to end.
- Don't add authentication/authorization scaffolding speculatively for
  Phase 2 bot users; Phase 1 only needs staff-side access considerations.
- Don't merge Products and Services into a shared table/type (see
  `product.md` for why).
