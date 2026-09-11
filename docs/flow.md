# Phase 2 Conversation & Human Handoff Flow (Design Reference)

This document maps out the customer-facing chatbot flow for Phase 2. It
is **not implemented in Phase 1** — it exists so Phase 1's API/database
design doesn't conflict with it later. Do not build against this
document unless the user is actively working on Phase 2.

## Actors

- **Customer**: chats via Telegram (testing) or WhatsApp Business API
  (production).
- **Bot service**: stateless-ish conversation handler; calls the FastAPI
  backend for all data (never talks to Supabase directly).
- **FastAPI backend**: single source of truth for compatibility, stock,
  and pricing — shared with the dashboard.
- **Staff**: picks up handed-off inquiries from the React dashboard.

## Conversation Flow

```
1. Customer opens chat
   → Bot greets, asks for vehicle details (make, model, year)

2. Customer provides vehicle details
   → Bot calls backend: "what products/services are relevant/compatible?"
     GET /api/catalog/compatible?make=...&model=...&year=...
     (Phase 3+: real compatibility filtering; Phase 2 may start with a
      simple "ask what part they want" flow if compatibility data isn't
      populated yet.)

3. Customer selects desired product(s) and/or service(s)
   → Bot calls backend: "is this in stock, what's the price?"
     GET /api/products/{id}   (stock_quantity, price)
     GET /api/services/{id}   (price, estimated_duration_minutes)

4. Bot presents quote
   → estimated_total_price = sum(product.price) + sum(service.price)
   → Bot shows itemized quote to customer, asks "would you like to book?"

5a. Customer declines / drops off
    → Conversation ends, no record created (or optionally logged as an
      abandoned inquiry for analytics — not required in initial build).

5b. Customer confirms booking intent
    → Bot calls backend: POST /api/inquiries
      { source: "telegram", customer_contact, vehicle_*, line_items[] }
    → Backend creates `inquiries` row (status = 'pending_handoff') and
      `inquiry_line_items` rows.
    → Bot replies with a hand-off message (e.g. "A staff member will
      confirm your booking shortly") and STOPS actively responding to
      further catalog/pricing questions in that conversation.

6. Human handoff
    → New inquiry appears on the React dashboard (a Phase 2 UI addition:
      an "Inquiries" or "Bookings" panel, not part of Phase 1 scope).
    → Staff reviews, finalizes (confirms stock, schedules), and updates
      `inquiries.status` → 'in_progress' → 'completed' (or 'cancelled').
```

## Human Handoff Rules

- Handoff is **one-directional and immediate**: once an inquiry is
  created, the bot must not attempt to keep negotiating price, stock, or
  scheduling — that becomes a human responsibility entirely.
- The bot should send exactly one clear "a staff member will follow up"
  message at handoff, not repeat it on every subsequent customer message.
- If the customer sends more messages after handoff, the bot may
  acknowledge receipt (e.g. "Your request is already with our team") but
  must not re-enter the quoting flow for that same inquiry.
- Staff-side finalization (confirming/rejecting/rescheduling) happens
  entirely in the dashboard, not through the bot.

## API Surface Implied by This Flow (for later phases)

These endpoints are **not** part of Phase 1 deliverables — listed only so
Phase 1's routing structure doesn't need to be reshaped to accommodate
them:

- `GET /api/products/{id}` / `GET /api/services/{id}` — already needed
  for Phase 1 dashboard, reused as-is by the bot.
- `GET /api/catalog/compatible` — Phase 3+, vehicle compatibility.
- `POST /api/inquiries` — Phase 2, creates a booking/inquiry + line items.
- `GET /api/inquiries` / `PATCH /api/inquiries/{id}` — Phase 2, dashboard
  side for staff to view and finalize.

## Channel Notes

- **Telegram first**: used for testing the conversation logic cheaply
  before dealing with WhatsApp Business API's approval/verification
  process.
- **WhatsApp Business API later**: same backend contract; only the bot's
  transport/webhook layer changes. Conversation logic and handoff rules
  above should not need to change between channels.
