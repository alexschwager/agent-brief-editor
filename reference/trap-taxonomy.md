# Trap taxonomy — the defect families this editor hunts

Categories 1–5 are the Sovereign Architect's five Agentic Execution Trap
families (Alex's rubric, embedded verbatim in
`.claude/agents/sovereign-architect.md` §0 — the binding downstream
authority). 6–7 are the editor's own upstream heights. Real costs behind
these rules: `known-failures.md`.

## 1. language-framework — instructions that violate the target stack's deep mechanics
- Cloudflare `Response` objects are immutable — construct new, never mutate.
- Env-var fallback: `||` not `??` — a blank string must fall through.
- SQLAlchemy: `.in_()`, not `ANY()`.
- Money across APIs: check BOTH units (decimal-string major units vs integer
  cents) and nullability — `Number(null)` is `0`, a fabricated zero charge.
- Widening a TS union: every hand-written `Record<Union, ...>` literal is a
  compile error regardless of runtime reachability — enumerate sites by grep.
- A delivery/payload shape is not the API shape — the request-body mapping
  must be stated field by field, with its authority named.
- Soft-deleted tables: uniqueness is often a *partial* index
  (`WHERE deleted_at IS NULL`). A resolver without the predicate can return
  exactly one row that is a tombstone — row-count guards never fire, and
  corroboration columns match the tombstone too.
- Success signals: read the artifact, not the transport — a route can return
  HTTP 200 with `{"status": "flagged"}`; counting 200s reports 74/74 while
  nothing was written.

## 2. state-bleed-testing — instructions that produce flaky or lying suites
- Module-level singletons (Pinia, module state) must be re-instantiated per
  test; happy-dom persists `localStorage` across `it`s — clear in `beforeEach`.
- Shared-DB specs: unique-id fixtures + cleanup in `finally`; never hardcoded
  rows (rerun hits unique constraints and orphans rows into live data).
- Never mandate a new import from a module an existing spec replaces with an
  exhaustive `vi.mock` factory — the symbol resolves `undefined`, and the
  reflexive stub can false-green the exact assertion it was added to protect.
  Grep the specs for `vi.mock('<module>')` first.
- Specs land in the tree where that surface's fixtures live — a spec outside
  the package conftest's reach reaches for a live connection: green locally
  (proxy up), red in CI.
- Rate-limited routes: a spec that burns its own quota reproduces the silent
  429 path it was written to eliminate.
- **Live-DB revert-verification is sandboxed, always** — mocked cursor
  (`sql_capture`) for SQL/param assertions, `SAVEPOINT`+`ROLLBACK`
  (`savepoint_sandbox`) for row effects; both in TP's
  `backend/tests/conftest.py` — name them, don't re-derive. Scoping args are
  NOT a mitigation: neutralizing the predicate is what removes the scoping.
  An un-sandboxed live break is a reject, never a style note (DATA-LOSS-TP-1).

## 3. helpful-agent-scope-creep — where "being helpful" breaks things
- "Filter this list" → destructive mutation of the source array.
- "Fix the error swallow" → bare `throw` (unhandled rejection) instead of
  wiring to UI state.
- "Fix the N stale comments" without grounding each → edits outside
  `touches`, regressing comments that were true or about a different hazard.
- Input sets named vaguely ("the files in that directory") → directory glob
  over a different delivery. Inputs are explicit allow-lists, by path.
- A dry-run with no read-only path → the agent either re-implements the
  server's resolution logic client-side (relocating authority into a
  throwaway script) or quietly lets dry-run write.
- Blocked on a missing credential/credit → the forbidden repair is
  fabricating the gated data (e.g. inventing `image_alt` to pass a WCAG
  invariant). The brief must name the STOP and the escalation.

## 4. git-environment — destructive or hanging environment commands
- `git fetch` does not update the working tree; `git pull --rebase` in a
  script needs an abort fallback or it wedges the checkout.
- Every blocking foreground process (proxy, dev server, tunnel, seeder):
  background + PID capture + reuse-if-already-up + teardown of only
  self-started processes. A foreground start hangs the run; a blind kill
  tears down a sibling lane's process.
- A fresh lane worktree has no `.venv`, no `secrets/`, no `node_modules` —
  all gitignored, all failing silently. TP briefs write exactly one line:
  reference `20-Doctrine/tp-lane-bootstrap.md`; never a hand-rolled gate.
- Executor git discipline: the orchestrator makes the worktree/branch;
  `git branch --show-current` before commits (L271); dispatched briefers on a
  shared checkout run no git at all.

## 5. hearsay-blind-wait — pipeline vulnerabilities
- Waiting on a sub-agent "returning" without a timeout or an explicit
  artifact commit → infinite hang.
- Liveness is not data: HTTP 200 on `/health` (a static dict, no DB touch)
  false-greens against a live-but-empty store. Preflight asserts the data
  artifact — a named row count, a non-empty result — and HALTs otherwise.
- "Already handled elsewhere" claims in a draft are grepped, not trusted; a
  CREATE migration is not grounding — a later migration may have dropped it.
  Ground against the full migration history / live schema.

## 6. machine-conformity — what the pipeline parses (see brief-shape-checklist.md)
Frontmatter routing fields, status lifecycle, the Step-0 claim gate and
`touches` guard verbatim, migration-ordinal freshness, gate placement
(founder gates above the imperatives they gate). Most of this is mechanical:
run `tests/verify.py brief <draft>` first.

## 7. executability-economy — lean, cold-start-complete, decision-clean
- Reference settled doctrine; never re-inline it (TR-TP-36's hand-rolled
  bootstrap exited 127 on every run and dead-ended the lane the doctrine
  would have bootstrapped).
- Specify the test *contract* plus one proven pattern to copy — not test
  internals. Over-prescription manufactures SA churn.
- DoD items measurable and binary; phases with exact paths and expected
  outputs; no step that requires a judgment call the executor isn't equipped
  to make. A genuine founder decision is parked as an explicit gate, never
  buried as an imperative.
- Ordering between briefs is `depends_on:`, not `status: blocked` — blocked
  is a surfaced exception, not a scheduling device.
