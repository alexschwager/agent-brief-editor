# Known failures — what each rule cost when it was learned

Case files behind the taxonomy. Cite these by name in findings; they are why
a rule exists, in rows a skeptic can check.

## DATA-LOSS-TP-1 — the verification method was the weapon
A brief's revert-verification step said to "temporarily break the control" —
and the control was a live-DB predicate. Neutralizing the WHERE clause is
precisely what removes the scoping, so the scoping args
(`market_code='ZAR', occupancy='2A'`) saved nothing: **640,186 rows of
`staging.msc_live_fare` destroyed, unrecoverable, no backup.** The code was
correct; the verification method executed against a live connection was the
weapon. Doctrine: `20-Doctrine/live-write-revert-sandbox.md`. Sanctioned
sandboxes landed as TP fixtures: `savepoint_sandbox`, `sql_capture`
(`backend/tests/conftest.py`). Editor rule: an un-sandboxed live-DB break in
a draft is the most severe finding class there is.

## TR-TP-36 — the hand-rolled bootstrap that dead-ended every lane
Instead of the one-line reference to `20-Doctrine/tp-lane-bootstrap.md`, the
brief re-inlined its own cold-start gate. It (a) invoked bare `python`, which
does not exist on this machine, so the gate exited 127 on every run
regardless of real state, and (b) told the executor to "escalate and stop"
on a missing venv — the exact case the doctrine says to bootstrap. The
executor had to override its own brief to make progress. Editor rule:
re-inlined settled doctrine is a defect, not diligence.

## EXPLORA-TP-1 — SA churn as a measurable cost
13 SA traps on one brief; **6 were lane-bootstrap issues** the doctrine
reference would have deleted, and two full review rounds went on fixing
bootstrap patches that had themselves introduced new traps. This is the
number that justifies an authoring-time editor at all: review rounds are the
scarce resource, and boilerplate defects spend them.

## IMG-TP-5 — five SA rounds, and one the reviewer got wrong
The richest single record (`01-Queue/archive/2026-08-15-IMG-TP-5-sa-rounds-1-4.md`).
Two lessons:
1. **Round 1's Trap 2 was materially wrong.** It asserted "there is no unique
   index on `slug`" after checking `pg_constraint` only. Round 2 re-grounded
   against `pg_indexes` and found `uq_cabin_category_slug UNIQUE (slug) WHERE
   (deleted_at IS NULL)` — a *partial* index. The real hazard was soft-delete
   tombstones (72 slugs existing ONLY as tombstones), which round 1's
   ">1 rows → flag" patch did not close. The correction is preserved in the
   record, superseding — not deleting — the wrong finding. That is the
   editor's model for owning a miss (rules.md Rule 7), and the concrete
   lesson: a constraint-only check misreads partial-index uniqueness;
   grounding has failure modes too, so name *how* you verified.
2. **A round that isn't applied is a round wasted.** Round 2 opens by noting
   the round-1 block "was never applied — the brief body is byte-unchanged."
   The editor proposes; the author applies; the re-review checks for the
   apply, not for the proposal's existence.

## The false-green family — three shapes, one lesson
- `GET /health` returns a static dict with no DB touch: 200 proves the
  process, not the proxy or the data. A live-but-DB-less API "cleanly
  flagged" all 74 rows — indistinguishable from a real mapping gap.
- A route that returns HTTP 200 with `{"status": "flagged"}`: a loader
  counting 200s reports 74/74 success while writing nothing.
- A reachability preflight against a live-but-empty seeded store.
One lesson: **assert the artifact** — the named row count, the response-body
status, the non-empty result — never the transport signal.

## The verify-outcome discipline (vault-wide)
"0 failures" in a run log is not the goal met; green tests are not the
rendered UI; a reviewer's "already handled" is grepped before it is believed;
a delivered fix is confirmed against the live store. The editor applies the
same standard to itself: a READY verdict names what was walked, and
`tests/verify.py` can fail the editor's own output.
