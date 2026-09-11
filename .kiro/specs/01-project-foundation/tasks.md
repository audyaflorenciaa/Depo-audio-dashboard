# Tasks: Project Foundation

Checklist for building the foundation described in `requirements.md` and
`design.md`. Work top to bottom — later tasks assume earlier ones exist.

- [ ] 1. **Create the backend app package skeleton**
      - [ ] Create `backend/app/__init__.py`
      - [ ] Create `backend/app/core/__init__.py`
      - [ ] Create `backend/app/health/__init__.py`

- [ ] 2. **Set up environment variable scaffolding**
      - [ ] Create `backend/.env.example` listing: `SUPABASE_URL`,
            `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`,
            `CORS_ALLOWED_ORIGINS` (with `http://localhost:5173` as the
            example value)
      - [ ] Create a local `backend/.env` (not committed) with real/dev
            Supabase project values
      - [ ] Confirm `backend/.gitignore` already excludes `.env` (it
            covers `venv/` and `__pycache__/` today — add `.env`
            explicitly if not already implied)

- [ ] 3. **Add any missing dependencies**
      - [ ] Decide: plain `pydantic` `BaseModel` + manual `os.environ`
            reads via `python-dotenv`, **or** adopt `pydantic-settings`
            for a cleaner `Settings` class. If adopting
            `pydantic-settings`, add it to `requirements.txt` with a
            pinned version and install it into the venv.
      - [ ] Confirm `requirements.txt` is UTF-8 (already fixed) before
            running `pip install`.

- [ ] 4. **Implement `app/core/config.py`**
      - [ ] Define the `Settings` model/loader per `design.md`
      - [ ] Load `.env` via `python-dotenv` before settings are read
      - [ ] Instantiate the settings object once at module level
      - [ ] Manually verify: temporarily rename/empty `.env` and confirm
            startup fails with a clear error, then restore `.env`

- [ ] 5. **Implement `app/core/supabase_client.py`**
      - [ ] Add a factory function (e.g. `get_supabase_client()`) that
            constructs the Supabase client from `Settings`
      - [ ] Do not call this factory from anywhere yet — it's foundation
            for the next spec

- [ ] 6. **Implement `app/health/router.py`**
      - [ ] Define a FastAPI `APIRouter`
      - [ ] Add `GET /health` returning `{"status": "ok"}` with no auth
            dependency and no Supabase call

- [ ] 7. **Implement `app/main.py`**
      - [ ] Create the `FastAPI()` app instance
      - [ ] Add `CORSMiddleware` configured from
            `Settings.cors_allowed_origins`, allowing `Authorization` and
            `Content-Type` headers and standard REST methods
      - [ ] Include the health router
      - [ ] Confirm importing `Settings` happens at module load (so a
            bad config fails fast on `uvicorn` startup)

- [ ] 8. **Run and verify locally**
      - [ ] Start the backend: `uvicorn app.main:app --reload` from
            `backend/` (with the venv activated)
      - [ ] Confirm no startup errors and no secrets printed to console
      - [ ] `curl http://localhost:8000/health` (or open in browser)
            returns `200` with `{"status": "ok"}`
      - [ ] Start the frontend (`npm run dev` in `frontend/`) and confirm
            a `fetch('http://localhost:8000/health')` call from the
            browser console succeeds with no CORS error

- [ ] 9. **Document actual run commands**
      - [ ] Add a short "Running the backend locally" section to
            `backend/README.md` (create if it doesn't exist) covering:
            venv activation, `pip install -r requirements.txt`, and the
            `uvicorn` run command — so this isn't tribal knowledge

- [ ] 10. **Confirm scope boundary before moving on**
      - [ ] No product/service/stock/auth code exists yet in `app/`
            beyond the stubs described above
      - [ ] Re-read `requirements.md` acceptance criteria and check each
            one off before starting the next spec
