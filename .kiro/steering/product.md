---
inclusion: always
---

# Product: Depo Audio OS

## Business Context

Depo Audio OS is the internal operating system for an automotive lighting
(and audio) installation workshop. Today, quoting customers, tracking the
install queue, and managing physical parts inventory are all manual and
slow. This system replaces that manual process with a dashboard first,
then a customer-facing chatbot that quotes and hands off bookings to staff.

Build order is sequential by phase. **Do not build ahead of the current
phase** unless a change is explicitly framed as "future-proofing" — the
priority right now is Phase 1.

## Core Domain Rule: Products vs. Services

This is the single most important modeling decision in the system. The two
concepts are **never merged into one generic "item" or "catalog entry"
table/type**, because they have fundamentally different lifecycles:

| Aspect | Product | Service |
|---|---|---|
| Definition | A physical part (e.g. HID kit, LED strip, amplifier) | Labor performed by staff (e.g. headlight retrofit, wiring) |
| Has stock quantity? | Yes — physical, countable | No — labor has no inventory |
| Has stock movement history? | Yes — every in/out/adjustment is logged | No |
| Has estimated duration? | No | Yes — used for scheduling/quoting |
| Has an image? | Yes — staff upload product photos | Optional, lower priority |
| Price | Unit price | Flat or duration-based labor price |
| Active/inactive toggle | Yes | Yes |

Consequences for implementation:
- Products and Services are **separate database tables**, separate API
  resources, and separate frontend sections. Do not build a shared
  `items` table with a `type` discriminator column — the fields diverge
  too much (stock vs. duration) and it invites bugs where stock logic
  leaks into services or vice versa.
- A quote/booking line item can reference **either** a product **or** a
  service, never both — model this as two nullable foreign keys (or a
  polymorphic line-item pattern), not a shared ID space.
- Stock changes are **never** direct field edits. Every change to a
  product's stock quantity must go through a stock movement record
  (reason + delta + resulting quantity), so the dashboard can show a full
  inventory movement history per product. Treat the stock quantity on the
  product as a derived/cached value, and the movement log as the source
  of truth.

## Phase 1 — Catalog & Inventory Dashboard (current priority)

Staff-facing React dashboard only. No customer-facing surface yet.

**Products**
- List, view, add, edit, activate/deactivate (soft toggle, never hard
  delete — products may be referenced by historical quotes later).
- Upload and manage a product image.
- Add stock / reduce stock as explicit operations, each producing a
  movement record (quantity delta, reason, timestamp, staff member).
- View inventory movement history per product.

**Services**
- List, view, add, edit, activate/deactivate.
- Price + estimated labor duration. No stock concept at all — do not add
  stock fields to services "just in case."

## Phase 2 — Customer Inquiry & Chatbot Flow (design context, not built yet)

Phase 1's database and API must be shaped so Phase 2 can be added without
reworking the catalog/inventory core. Concretely, this means Phase 1 should
account for:
- **Vehicle-aware compatibility checks**: products may need to be checked
  against a customer's car (make/model/year). Keep product records
  extensible enough to attach compatibility rules later without
  restructuring the core `products` table.
- **Live stock lookups**: the bot will ask "is this in stock for my car"
  before quoting, so stock quantity must be reliably queryable via API,
  not just visible in the dashboard.
- **Quoting math**: an estimated price is Product Price + Service Price.
  Keep pricing fields simple numeric values (not bundled/composite) so a
  future quoting engine can sum them directly.
- **Human handoff**: when a customer wants to book, the bot stops
  responding and a booking/inquiry record is created for staff to
  finalize on the dashboard. Phase 1's data model should leave room for an
  "inquiry" or "booking" concept even though the dashboard UI for it isn't
  built until Phase 2.

See `docs/database.md` for the concrete schema proposal and
`docs/flow.md` for the conversation/handoff flow design.

## Future Phases (context only, do not implement)

Phase 3–10 roughly cover: AI conversation engines, vehicle compatibility
automation, manual-to-auto scheduling, full WhatsApp Business API
production rollout, and upselling logic. These are not requirements for
current work — they exist here only so early modeling decisions don't
paint the project into a corner.
