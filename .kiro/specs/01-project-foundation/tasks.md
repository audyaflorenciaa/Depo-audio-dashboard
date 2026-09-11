# Tasks: Project Foundation

Checklist for building the foundation described in `requirements.md` and
`design.md`. Work top to bottom — later tasks assume earlier ones exist.

- [x] 1. **Create the backend app package skeleton**
      - [x] Create `backend/app/__init__.py`
      - [x] Create `backend/app/core/__init__.py`
      - [x] Create `backend/app/health/__init__.py`

- [x] 2. **Set up environment variable scaffolding**
      - [x] Create `backend/.env.example` listing: `SUPABASE_URL`,
            `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`,
            `CORS_ALLOWED_ORIGINS` (with `http://localhost:5173` as the
            example value)
      - [x] Create a local `backend/.env` (not committed) with real/dev
            Supabase project values
      - [x] Confirm `backend/.gitignore` already excludes `.env` (it
            covers `venv/` and `__pycache__/` today — add `.env`
            explicitly if not already implied)

- [x] 3. **Add any missing dependencies**
      - [x] Decide: plain `pydantic` `BaseModel` + manual `os.environ`
            reads via `python-dotenv`, **or** adopt `pydantic-settings`
            for a cleaner `Settings` class. If adopting
            `pydantic-settings`, add it to `requirements.txt` with a
            pinned version and install it into the venv.
      - [x] Confirm `requirements.txt` is UTF-8 (already fixed) before
            running `pip install`.

- [x] 4. **Implement `app/core/config.py`**
      - [x] Define the `Settings` model/loader per `design.md`
      - [x] Load `.env` via `python-dotenv` before settings are read
      - [x] Instantiate the settings object once at module level
      - [x] Manually verify: temporarily rename/empty `.env` and confirm
            startup fails with a clear error, then restore `.env`

- [x] 5. **Implement `app/core/supabase_client.py`**
      - [x] Add a factory function (e.g. `get_supabase_client()`) that
            constructs the Supabase client from `Settings`
      - [x] Do not call this factory from anywhere yet — it's foundation
            for the next spec

- [x] 6. **Implement `app/health/router.py`**
      - [x] Define a FastAPI `APIRouter`
      - [x] Add `GET /health` returning `{"status": "ok"}` with no auth
            dependency and no Supabase call

- [x] 7. **Implement `app/main.py`**
      - [x] Create the `FastAPI()` app instance
      - [x] Add `CORSMiddleware` configured from
            `Settings.cors_allowed_origins`, allowing `Authorization` and
            `Content-Type` headers and standard REST methods
      - [x] Include the health router
      - [x] Confirm importing `Settings` happens at module load (so a
            bad config fails fast on `uvicorn` startup)

- [x] 8. **Run and verify locally**
      - [x] Start the backend: `uvicorn app.main:app --reload` from
            `backend/` (with the venv activated)
      - [x] Confirm no startup errors and no secrets printed to console
      - [x] `curl http://localhost:8000/health` (or open in browser)
            returns `200` with `{"status": "ok"}`
      - [x] Start the frontend (`npm run dev` in `frontend/`) and confirm
            a `fetch('http://localhost:8000/health')` call from the
            browser console succeeds with no CORS error

- [x] 9. **Document actual run commands**
      - [x] Add a short "Running the backend locally" section to
            `backend/README.md` (create if it doesn't exist) covering:
            venv activation, `pip install -r requirements.txt`, and the
            `uvicorn` run command — so this isn't tribal knowledge

- [ ] 10. **Confirm scope boundary before moving on**
      - [ ] No product/service/stock/auth code exists yet in `app/`
            beyond the stubs described above
      - [ ] Re-read `requirements.md` acceptance criteria and check each
            one off before starting the next spec
