# Brief Editor Review — IMG-TP-99 — 2026-08-18

VERDICT: NOT READY — 2 findings

## BE-1 — the UPDATE needs hardening
- category: language-framework
- grounded: verified — checked the table

> The brief updates the cabin rows by slug, which could be unsafe.

**Defect.** The UPDATE is keyed on slug.
**Why it fails.** Wrong rows could be updated.
**Fix direction.** Replace with: the following corrected block, keyed on the PK.

```sql
BEGIN;
UPDATE cruise_v2.cabin_category SET image_url = %s WHERE cabin_category_id = 1336;
UPDATE cruise_v2.cabin_category SET image_url = %s WHERE cabin_category_id = 1354;
-- assert rowcount == 1 per statement, else ROLLBACK
COMMIT;
```

## BE-3 — environment phase missing, here is the revised Phase 0

**Defect.** No environment setup.
**Why it fails.** Cold start fails.
**Fix direction.** Paste this into the brief as the new Phase 0:

```bash
cd ~/Developer/travel-data-platform
PROXY_STARTED=0
if ! nc -z 127.0.0.1 5433; then ./start-cloud-proxy.sh & PROXY_PID=$!; PROXY_STARTED=1; fi
.venv/bin/uvicorn backend.app:app --port 8001 &
```
