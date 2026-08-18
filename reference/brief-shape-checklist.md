# Brief-shape checklist — machine conformity

The authority is `90-Templates/Brief Template.md`. These are the checks that
gate whether the pipeline can even *route* the draft. `tests/verify.py brief
<draft.md>` runs the mechanical subset; the judgment rows below it are the
editor's.

## Mechanical (verify.py enforces)

| # | Check |
|---|---|
| M1 | Frontmatter present, fenced by `---`, first block in the file. |
| M2 | Keys present: `brief`, `status`, `repo`, `branch`, `model`, `gemini_reviewed`, `touches`. |
| M3 | `repo:` is exactly one of `travel-data-platform` \| `cloudflare-worker` \| `front-end` — the orchestrator routes on this field; a prose value ("the frontend") does not route. |
| M4 | `status:` is one of `awaiting-sa` \| `queued` \| `ready` \| `in-progress` \| `in-review` \| `merged` \| `blocked`. A draft is born `awaiting-sa` with `gemini_reviewed: false`. |
| M5 | `touches:` is a list. Empty (`[]`) is legal only for recon/read-only briefs. |
| M6 | Required sections present: `## Context & Why`, `## Scope`, `### NOT in scope`, `## Pre-execution verification`, `## Phases`, `## Verification`. |
| M7 | The Step-0 claim-gate and `touches`-guard blocks appear (their heading lines) — the machine-contract text is carried, not paraphrased. |

## Judgment (the editor's rows)

| # | Check |
|---|---|
| J1 | `touches` actually covers every path the phases create or modify — an undeclared path defeats the conflict guard silently. |
| J2 | The claim-gate / guard text is verbatim from the template, not reworded — the gate logic is load-bearing. |
| J3 | `model:` matches the work (sonnet default; opus for remediation/fix briefs). Dispatch honors the frontmatter, not the session. |
| J4 | Ordering via `depends_on:` (orchestrator waits for merge), never via `status: blocked`. A dependency that must be *applied* (a migration run against the live store), not merely merged-on-main, is named as such. |
| J5 | New migration ordinals: the brief instructs a next-free-ordinal walk at execution time, not a hardcoded number — parallel lanes collide on ordinals. |
| J6 | Any founder-gated action (prod publish, spend, live-supplier writes, scheduler enablement) carries its gate ABOVE the imperatives it gates, so a top-down reader hits the gate first. |
| J7 | Negative/security specs carry the revert-verification obligation, and any live-DB predicate break names its sandbox (`savepoint_sandbox` / `sql_capture` for TP) — see trap family 2. |
| J8 | Verification phase ends with the target repo's own pre-flight (FE: format:check → lint → test; CW: check → test; TP: ruff check . → scoped pytest), and TP pytest scope is stated (never the full suite against `:5433`). |
| J9 | The brief tells the executor what to READ before writing (exact component paths, real testids, route shapes) — pre-execution verification is codebase-grounded, not brief-trusted. |
