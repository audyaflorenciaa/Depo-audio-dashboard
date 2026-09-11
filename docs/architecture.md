# Architecture

## Monorepo Layout

```
Depo-audio-dashboard/
├── frontend/        React dashboard (Vite). Staff-facing UI.
├── backend/         FastAPI service. Owns all business logic.
├── database/        SQL schema/migrations for Supabase Postgres.
├── docs/            Architecture & design references (this folder).
└── .kiro/steering/  Standing context for AI-assisted development.
```

There is no shared code package between `frontend/` and `backend/` yet.
Introduce one (e.g. a shared OpenAPI-generated types package) only if
duplication becomes a real maintenance problem — not preemptively.

## Communication Flow (Phase 1)

```
┌─────────────────┐        HTTPS / JSON         ┌──────────────────┐        ┌────────────────────┐
│  React Dashboard │  ───────────────────────►   │  FastAPI Backend  │ ──►    │  Supabase Postgres  │
│  (frontend/)      │  ◄───────────────────────   │  (backend/)        │ ◄──    │  + Storage           │
└─────────────────┘                              └──────────────────┘        └────────────────────┘
```

- **Frontend → Backend**: the React app talks only to the FastAPI backend
  over REST (`/api/...`), using `fetch`/JSON. It never calls Supabase
  directly and never holds the Supabase service role key.
- **Backend → Supabase**: FastAPI is the only component with database
  credentials. It uses the `supabase` Python client (service role key)
  for all reads/writes, including:
  - Postgres tables (`products`, `services`, `stock_movements`, etc.)
  - Supabase Storage (product images)
- **Why not let the frontend hit Supabase directly?** Two reasons:
  1. Business rules — e.g. "a stock change must always create a movement
     record" — need to be enforced in one place. If the frontend wrote to
     Postgres directly, that rule could be bypassed.
  2. Phase 2 requires the *same* backend logic (stock checks, pricing) to
     be reusable by the chatbot, which has no frontend at all. Centralizing
     logic in FastAPI means the dashboard and the bot are just two
     different clients of the same API.

## Access Control (Staff Login)

```
┌─────────────────┐   1. login (email/pw)   ┌───────────────────┐
│  React Dashboard │ ───────────────────────►│  Supabase Auth      │
│  (frontend/)      │ ◄─────────────────────  │  (JWT issuer)        │
└─────────────────┘   2. JWT access token    └───────────────────┘
        │
        │ 3. Authorization: Bearer <jwt>
        ▼
┌──────────────────┐   4. verify JWT   ┌───────────────────┐
│  FastAPI Backend   │ ─────────────────►│  Supabase Auth      │
│  (protected routes) │ ◄─────────────────│  (JWT secret/JWKS)  │
└──────────────────┘                    └───────────────────┘
```

- **Login happens client-side**: the React dashboard authenticates staff
  directly against **Supabase Auth** using the anon/public key (no
  custom login endpoint on the FastAPI backend). Supabase Auth owns
  credentials, password resets, and token issuance/refresh.
- **Every request to the backend carries the JWT**: the frontend attaches
  the Supabase-issued access token as `Authorization: Bearer <jwt>` on
  all calls to `/api/*`.
- **Backend verifies, never issues**: FastAPI has a shared dependency
  that validates the incoming JWT (signature + expiry) against Supabase's
  JWT secret/JWKS before allowing the request to reach a route handler.
  The backend does not generate tokens or manage passwords — it only
  trusts tokens Supabase Auth already signed.
- **`/health` is the only public route** in Phase 1; every other
  `/api/*` route requires a valid staff JWT.
- This mechanism is staff-only. Phase 2's bot is a separate,
  backend-to-backend caller and will need its own auth approach — it is
  not a Supabase Auth user and should not be forced through the staff
  login dependency.

## Communication Flow (Phase 2 — chatbot, for context)

```
┌────────────┐   Telegram/WhatsApp   ┌──────────────────┐        ┌──────────────────┐
│  Customer   │ ───────────────────► │  Bot Service       │ ──►   │  FastAPI Backend   │
│  (chat app) │ ◄─────────────────── │  (webhook handler) │ ◄──   │  (same API)         │
└────────────┘                       └──────────────────┘        └──────────────────┘
                                                                          │
                                                                          ▼
                                                                 ┌──────────────────┐
                                                                 │  Supabase Postgres │
                                                                 │  (inquiries table) │
                                                                 └──────────────────┘
                                                                          │
                                                                          ▼
                                                                 ┌──────────────────┐
                                                                 │  React Dashboard   │
                                                                 │  (staff picks up)  │
                                                                 └──────────────────┘
```

- The bot (Telegram first, then WhatsApp Business API) is a **separate
  service/process** from the FastAPI backend, but calls the **same**
  backend REST API for compatibility checks, stock lookups, and pricing —
  it does not duplicate business logic or talk to Supabase directly.
- When a customer wants to book, the bot calls a backend endpoint to
  create an `inquiry`/`booking` record and then stops replying (human
  handoff). That record shows up in the dashboard for staff to finalize.
- Swapping Telegram for WhatsApp later should only require swapping the
  bot's webhook/transport layer — the backend API contract stays the same.

## Environments & Secrets Boundary

- Only the **backend** ever holds the Supabase service role key (via
  `.env`, gitignored).
- The **frontend** holds no database secrets. If frontend-side Supabase
  access is ever needed (e.g. direct auth), it would use the anon/public
  key only, via Vite env vars — not implemented in Phase 1.
- The **bot service** (Phase 2) holds Telegram/WhatsApp API tokens, not
  database credentials — it authenticates to the backend like any other
  API client.
- Supabase Auth's JWT secret (or JWKS endpoint, depending on verification
  approach) is a backend-only value used to verify staff tokens. It is
  never exposed to the frontend and is distinct from the anon/public key
  the frontend uses to talk to Supabase Auth for login.

## Deployment Shape (not yet implemented, noted for future reference)

Not a current task — no CI/CD or hosting decisions have been made. When
this becomes relevant, revisit this section to document chosen hosting
for the FastAPI backend, the static frontend build, and the bot service.
