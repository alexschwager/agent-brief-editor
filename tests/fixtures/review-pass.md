# Brief Editor Review — IMG-TP-99 — 2026-08-18

VERDICT: NOT READY — 3 findings

## BE-1 — live UPDATE keyed on slug with no rowcount guard
- category: language-framework
- grounded: unverified — settle with `pg_indexes` on `cruise_v2.cabin_category`: if slug uniqueness is a partial index over live rows, a tombstone can satisfy a slug match

> After the rows land, update the cabin rows to the new master URL:
> `UPDATE cruise_v2.cabin_category SET image_url = %s WHERE slug IN (%s, %s)`.

**Defect.** A slug-keyed live UPDATE with no transaction and no rowcount assertion, on a table where slug uniqueness may hold only among live rows.
**Why it fails.** If a tombstone or duplicate matches, the statement silently updates the wrong number of rows and the run still reports success — a confidently wrong write, not a visible failure.
**Fix direction.** Key the UPDATE on the primary key resolved at execution time, run both statements in one explicit transaction, assert the rowcount per statement before commit, and roll back on any other count. The known-failures file's IMG-TP-5 entry documents this exact table's partial-index hazard.

## BE-2 — "accepts any payload files" is a directory glob waiting to happen
- category: helpful-agent-scope-creep
- grounded: verified — the draft's own Current State names a shared staged directory, and the 2026-08-13 delivery drop is on record as holding multiple unrelated payload shapes

> The loader accepts any payload files found in the
> staged delivery directory.

**Defect.** The input set is defined by location, not by name.
**Why it fails.** A literal agent globs the staged directory and feeds every `.jsonl` it finds — including deliveries of a different shape — to the image loader.
**Fix direction.** Name the in-scope files as an explicit allow-list passed by path, and make the loader refuse any row that lacks the image-payload shape rather than skip it silently.

## BE-3 — no cold-start phase: the loader's runtime is assumed, not established
- category: git-environment
- grounded: unverified — confirm against the repo's `.gitignore` and proxy script; the lane-bootstrap doctrine records both as gitignored and blocking-foreground respectively

> ## Phases

**Defect.** No phase establishes the environment the loader needs: the DB proxy, the TP API, the auth key, `secrets/.env`, a venv. A fresh lane worktree has none of them.
**Why it fails.** The cold executor hits connection refused and improvises — foregrounds a blocking server and hangs, or kills a process a sibling lane owns.
**Fix direction.** Add a Phase 0 that references `20-Doctrine/tp-lane-bootstrap.md` in one line (never re-inlined — see TR-TP-36 in known-failures), backgrounds each blocking process with PID capture and reuse-if-up, tears down only what it started, and preflights on a data artifact rather than a liveness ping.
