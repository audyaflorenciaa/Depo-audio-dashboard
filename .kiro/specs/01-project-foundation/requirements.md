# Requirements: Project Foundation

## Purpose

Before any Products/Services API work begins, the FastAPI backend needs a
working, runnable skeleton: a real app instance, environment-based
configuration for Supabase, CORS permitting the React dashboard to call
it, and a health check to prove it's alive. This spec covers exactly that
foundation — no product/service/stock/auth business logic yet.

## In Scope

1. **Initialize the FastAPI application**
   - A runnable FastAPI app under `backend/app/` (not a flat `main.py`
     with everything inlined), following the resource-oriented structure
     described in `tech.md`.
   - App starts locally via `uvicorn` and is reachable on a local port.

2. **Environment variable configuration for Supabase**
   - A `.env.example` (committed) documenting required variables, and a
     real `.env` (gitignored, already covered by `backend/.gitignore`)
     for local values.
   - Required variables at minimum: `SUPABASE_URL`,
     `SUPABASE_SERVICE_ROLE_KEY`. Include a placeholder for the JWT
     verification value (`SUPABASE_JWT_SECRET`) even though auth
     middleware itself is not built in this spec — the config loader
     should support it so the next spec doesn't need to touch this layer
     again.
   - Config is loaded once via `python-dotenv` and validated at startup
     (fail fast with a clear error if a required variable is missing,
     rather than failing later on first request).
   - No secret values are hardcoded anywhere in source.

3. **Basic `/health` endpoint**
   - `GET /health` returns `200 OK` with a small JSON body (e.g.
     `{"status": "ok"}`) confirming the app is running.
   - Must not require authentication (this spec does not implement auth
     yet — see Out of Scope).
   - Should not depend on a live Supabase connection to return `200` for
     basic liveness; a deeper "readiness" check (e.g. verifying Supabase
     connectivity) is optional and can be a stretch goal, not a
     requirement.

4. **CORS configuration**
   - The backend must accept requests from the local React dev server
     (Vite default, `http://localhost:5173`) so the dashboard can call
     `/health` and future endpoints without CORS errors.
   - Allowed origin(s) should be configurable via environment variable
     rather than hardcoded, so staging/production origins can be added
     later without code changes.

## Out of Scope (explicitly deferred)

- Any Products, Services, or Stock Movements endpoints or schemas.
- Supabase Auth / JWT verification middleware (the `get_current_staff`
  dependency described in `tech.md`) — only the config placeholder for
  it is included here, not the implementation.
- Actual Supabase client calls / database queries. `/health` does not
  need to touch the database.
- Frontend work (API client wrapper, login UI, etc.) — this spec is
  backend-only.
- Deployment/hosting configuration.

## Acceptance Criteria

- [ ] Running the backend locally starts without errors and without any
      hardcoded secrets in source.
- [ ] `GET /health` returns `200 OK` with a JSON status body.
- [ ] Missing required environment variables cause a clear startup
      failure (not a silent `None` or a runtime `KeyError` on first
      request).
- [ ] A request to `/health` from the Vite dev server origin
      (`http://localhost:5173`) succeeds without a CORS error in the
      browser console.
- [ ] `.env.example` exists and lists every variable the app reads;
      `.env` is confirmed gitignored (already true per
      `backend/.gitignore`).
- [ ] No product/service/stock/auth logic is introduced in this spec.
