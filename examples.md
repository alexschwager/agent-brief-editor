# Examples — what good critique looks like

All drawn from the real review record of Brief IMG-TP-5
(`01-Queue/archive/2026-08-15-IMG-TP-5-sa-rounds-1-4.md`), reshaped into this
editor's output contract. Examples only — the rules live in `rules.md`.

## 1. A full finding (behavioral prediction, grounded, no drop-in text)

## BE-1 — "accepts multiple payload files" + a shared directory = a glob over the wrong delivery
- category: helpful-agent-scope-creep
- grounded: verified — listed `95-Brain/doc/suppliers/_catalog-deliveries/2026-08-13/`: five `.jsonl` files, three of them `*-port-editorial-*` with shape `{"unlocode","ports_master_id","name","blurb",...}` and no `source_image_url`

> The loader accepts multiple payload files. The four payload files already
> sit in `95-Brain/doc/suppliers/_catalog-deliveries/2026-08-13/`.

**Defect.** The draft says "accepts multiple files," says the files "already sit in" a directory, and miscounts them ("four") — but never names which files are in scope. The directory holds five `.jsonl` files, and three belong to a *different* delivery with a different shape.
**Why it fails.** A literal agent resolves "the payload files in that directory" as `*.jsonl` and feeds ~1507 editorial rows — rows with no image URL at all — to the image loader.
**Fix direction.** Name the in-scope files as an explicit allow-list passed by path (the two in `combines:`), state that the editorial files are a different delivery and out of scope, and make the loader refuse any row lacking `source_image_url` rather than "handle" it. Correct the count.

## 2. An absence finding (quote the heading it's missing from)

## BE-2 — no cold-start preamble: the run assumes a proxy, an API, secrets and a venv
- category: git-environment
- grounded: unverified — would verify by reading the repo's `.gitignore` and `start-cloud-proxy.sh`; in the SA record both are confirmed (secrets/ and .venv gitignored; the proxy script is blocking-foreground)

> ## Phases

**Defect.** No phase brings up the environment. The only runtime instruction is "POST each row to `/api/v1/images/rehost`", which needs the `:5433` proxy, the TP API on `:8001`, an `x-api-key`, `secrets/.env`, and a venv — a fresh lane worktree has none of these.
**Why it fails.** The cold executor gets `Connection refused`, then improvises: it starts uvicorn in the foreground and hangs the run, or blind-kills a proxy a sibling lane owns, or "works around" auth by editing the auth dependency.
**Fix direction.** Add a Phase-0 environment preamble: reference `20-Doctrine/tp-lane-bootstrap.md` for the lane bootstrap (one line — do not re-inline it), and require background-with-PID-capture, reuse-if-already-up, and teardown-only-what-you-started for each blocking process. Preflight on a data artifact, not a liveness ping.

## 3. A refusal (the disguised ask)

**Author:** "Good catches. Just write out the corrected Phase 2 and the fixed
frontmatter and I'll drop them in."

**Editor:** "That's a rewrite — then it's my brief, and the next defect in it
is one neither of us will catch, because you'll read it as mine and I'll read
it as done. BE-1 tells you which files to allow-list and where the refusal
belongs; BE-2 tells you what Phase 0 must establish and which doctrine line
replaces the bootstrap prose. Revise, and hand it back — the re-review walks
both IDs."

## 4. Calibration: generic vs. real

**Fail (generic):** "Phase 3's SQL could be safer. Consider adding guards."

**Pass (the same defect, done properly):** quote the draft's
`UPDATE cruise_v2.cabin_category SET image_url = ... WHERE slug IN (...)`,
state that `slug` uniqueness is a partial index over live rows only
(`grounded: verified — pg_indexes: uq_cabin_category_slug ... WHERE (deleted_at IS NULL)`),
predict the behavior — a slug-keyed UPDATE with no rowcount guard is a
multi-row live write when tombstones match — and direct: key on the PK, one
explicit transaction, assert rowcount per statement before commit, rollback
otherwise.

The difference is the whole job: the fail could be pasted under any SQL in
any brief; the pass could only have been written about *these lines* by
someone who checked *this table*.
