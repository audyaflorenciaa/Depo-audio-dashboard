# Database Schema Proposal

Target: Supabase (PostgreSQL). This document proposes the **Phase 1**
schema (Catalog & Inventory) shaped so **Phase 2** (chatbot + human
handoff) can be added without restructuring these core tables. Treat this
as a living design doc — update it when the schema actually changes.

Conventions used below:
- `id uuid primary key default gen_random_uuid()` on every table.
- `created_at timestamptz default now()`, `updated_at timestamptz default now()`
  on every table (maintain `updated_at` via trigger or application code).
- Money stored as `numeric(10,2)`, never `float`.
- Soft delete via `is_active boolean default true` — no hard deletes on
  catalog data, since historical quotes/bookings may reference it later.

---

## Phase 1 Tables

### `products`

Physical parts with stock.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, PK | |
| `name` | text, not null | |
| `description` | text | |
| `sku` | text, unique | optional but recommended for inventory |
| `price` | numeric(10,2), not null | unit price |
| `stock_quantity` | integer, not null, default 0 | **cached/derived** — always updated via a `stock_movements` insert, never edited directly |
| `image_url` | text | Supabase Storage URL |
| `category` | text | free-form or FK to a future `categories` table; keep simple for Phase 1 |
| `is_active` | boolean, not null, default true | activate/deactivate toggle |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

Phase 2 forward-compatibility note: no vehicle-compatibility columns on
`products` itself. Compatibility is modeled as a separate join table
(`product_vehicle_compatibility`, not built in Phase 1) so the core table
never needs restructuring when that feature lands — just add the new
table and start populating it.

### `stock_movements`

Append-only log; source of truth for stock. `products.stock_quantity` is
a cache updated whenever a row is inserted here.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, PK | |
| `product_id` | uuid, FK → `products.id`, not null | |
| `change_quantity` | integer, not null | positive = stock added, negative = stock reduced |
| `resulting_quantity` | integer, not null | snapshot of `stock_quantity` after this movement, for audit clarity |
| `reason` | text, not null | e.g. `"restock"`, `"used_in_install"`, `"correction"`, `"damaged"` — consider a check constraint or enum once reasons stabilize |
| `note` | text | optional free-text detail |
| `staff_id` | uuid | who performed the change; nullable until staff/auth accounts exist |
| `created_at` | timestamptz, not null, default now() | |

No `updated_at` — movements are immutable, never edited after creation.

### `services`

Labor services. No stock, no image priority — deliberately fewer fields
than `products`.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, PK | |
| `name` | text, not null | |
| `description` | text | |
| `price` | numeric(10,2), not null | flat labor price |
| `estimated_duration_minutes` | integer, not null | used for scheduling/quoting |
| `is_active` | boolean, not null, default true | |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

## Phase 2 Tables (proposed now, not built in Phase 1)

Listed here so Phase 1 design doesn't conflict with them later. Do not
create these tables as part of Phase 1 work unless explicitly asked —
they're documented for forward-compatibility review only.

### `inquiries` (a.k.a. bookings)

Created by the bot when a customer wants to book; picked up by staff on
the dashboard (human handoff).

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, PK | |
| `source` | text, not null | `"telegram"`, `"whatsapp"`, `"manual"` |
| `customer_name` | text | |
| `customer_contact` | text | phone/handle, channel-dependent |
| `vehicle_make` | text | |
| `vehicle_model` | text | |
| `vehicle_year` | integer | |
| `status` | text, not null, default `'pending_handoff'` | `pending_handoff` → `in_progress` → `completed` / `cancelled` |
| `estimated_total_price` | numeric(10,2) | product price + service price at time of quote |
| `assigned_staff_id` | uuid | nullable until a staff member picks it up |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

### `inquiry_line_items`

The product/service pairing the bot quoted, per inquiry. Mirrors the
"product XOR service" rule from `product.md`.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, PK | |
| `inquiry_id` | uuid, FK → `inquiries.id`, not null | |
| `product_id` | uuid, FK → `products.id`, nullable | set if this line is a product |
| `service_id` | uuid, FK → `services.id`, nullable | set if this line is a service |
| `quantity` | integer, not null, default 1 | mainly relevant for products |
| `price_at_time` | numeric(10,2), not null | snapshot, so later price changes don't rewrite history |

Constraint: exactly one of `product_id` / `service_id` must be set
(enforce via a `CHECK` constraint:
`(product_id IS NOT NULL) <> (service_id IS NOT NULL)`).

### `product_vehicle_compatibility` (Phase 3+ groundwork, not Phase 1)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid, PK | |
| `product_id` | uuid, FK → `products.id` | |
| `vehicle_make` | text | |
| `vehicle_model` | text | |
| `vehicle_year_start` | integer | |
| `vehicle_year_end` | integer | |

Not needed until vehicle compatibility automation (later phase) is
actually built. Mentioned here only so `products` isn't redesigned when
it arrives.

---

## Why This Shape Supports Phase 2 Without Rework

- `products.stock_quantity` is already a queryable API field — the bot's
  "check live stock" step just calls the same `GET /api/products/{id}`
  the dashboard uses.
- `price` on both `products` and `services` are plain numerics — the
  bot's quoting math (`product.price + service.price`) doesn't need a
  new pricing engine.
- `inquiries` / `inquiry_line_items` are additive tables — they don't
  require any column changes to `products`, `services`, or
  `stock_movements`.
- Nothing in Phase 1 hard-codes "no vehicle data" — vehicle compatibility
  is deferred to a join table specifically so it can be bolted on later.
