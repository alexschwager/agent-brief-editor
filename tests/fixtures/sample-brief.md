---
brief: IMG-TP-99
status: awaiting-sa
depends_on: []
repo: travel-data-platform
branch: feature/img-tp-99-cabin-image-backfill
model: sonnet
pr: null
gemini_reviewed: false
touches:
  - scripts/load_cabin_images.py
  - backend/tests/test_cabin_image_backfill.py
worktree: null
---

# Brief IMG-TP-99 — Cabin image backfill from staged catalog delivery

> Fixture brief for `verify.py selftest`. Deliberately seeded with judgment
> flaws (see `review-pass.md`) while staying shape-conformant.

## Context & Why

The catalog cell delivered cabin image payloads for the MSC World Atlantic.
Two cabin categories still carry dead `WA_*` image URLs. This brief loads the
delivered images through the rehost endpoint and repoints the two rows.

## Current State

Payload files sit in `95-Brain/doc/suppliers/_catalog-deliveries/2026-08-13/`.
The rehost endpoint exists at `/api/v1/images/rehost`.

## Scope

### In scope
- A loader script that reads the staged payload files and POSTs each row to
  `/api/v1/images/rehost`. The loader accepts any payload files found in the
  staged delivery directory.
- After the rows land, update the cabin rows to the new master URL:
  `UPDATE cruise_v2.cabin_category SET image_url = %s WHERE slug IN (%s, %s)`.

### NOT in scope
- Port images, hero demotion, any FE change.

### Off-limits paths
- `backend/routes/images.py` — read-only for this brief.

## Machine Contract Notes

### Step 0 — claim gate (EVERY executor starts here)

Before doing ANYTHING else, read this brief's frontmatter `status`: `queued`
means claim it; anything else means HALT and surface the existing claim.

### `touches` conflict guard

`touches` lists every repo-relative path this brief creates or modifies; the
orchestrator holds any brief whose set overlaps an in-flight brief's.

## Pre-execution verification (NON-NEGOTIABLE)

- Read `backend/routes/images.py` to confirm the request model's required
  fields before writing the loader.
- Confirm the two target slugs still resolve to the expected cabin rows.

## Phases

### Phase 1 — loader
Write `scripts/load_cabin_images.py`: read the payload rows, POST each row to
`/api/v1/images/rehost`, print a per-row result line.

### Phase 2 — repoint the cabin rows
Run the UPDATE from Scope and confirm the two rows carry the new URL.

### Phase 3 — tests
Add `backend/tests/test_cabin_image_backfill.py` covering the loader's row
mapping and the flagged-row path.

## Verification

- [ ] Loader runs clean against the staged delivery.
- [ ] Both cabin rows carry the rehosted URL.
- [ ] `ruff check .` passes; scoped pytest for the new test module passes.
