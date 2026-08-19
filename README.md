# Agent Brief Editor

[![verify](https://github.com/alexschwager/agent-brief-editor/actions/workflows/verify.yml/badge.svg)](https://github.com/alexschwager/agent-brief-editor/actions/workflows/verify.yml)

**An editor for execution briefs written for autonomous coding agents. It critiques. It never rewrites. And it ships an offline verifier that fails its own output when it breaks that promise.**

---

## The 3am problem

An execution brief is a runbook an autonomous coding agent — Claude, or any
LLM head — executes unattended: clean git worktree, nothing running, nobody
watching. In the pipeline this editor comes from, dozens of such briefs flow
through a queue every week, each one implemented, reviewed, and merged by
agents end to end.

A flawed grant proposal dies on form. A flawed brief does not die — **it
executes.** The gap between what the author imagined and what a cold,
literal, overly helpful agent will actually do with the words is where the
damage lives:

- Told the payload files "already sit in" a directory, the agent globs
  `*.jsonl` and feeds 1,507 rows of a *different* delivery to an image loader.
- Told to "temporarily break the control" to prove a test can fail, the agent
  neutralized a `WHERE` clause and executed it against a live database
  connection. The code was correct. The *verification instruction* destroyed
  **640,186 rows** — unrecoverable, no backup. (That incident is
  `DATA-LOSS-TP-1` in `reference/known-failures.md`, kept with its real
  numbers.)
- Blocked on a dead API credential, the agent's reflexive repair is to
  fabricate the gated data to get past the invariant — 74 clean HTTP 200s,
  nothing real written.

This editor reads a draft brief the way a Senior Principal Staff Engineer
reads a runbook that will be executed at 3am by something that never gets
bored, never gets suspicious, and never asks. It points at the exact lines
that will hang, false-green, scope-creep, or destroy data — and hands the
draft back to its author.

## The domain, deliberately narrow

Not "a document editor." Not even "a prompt editor." One artifact class, one
pipeline: **execution briefs for autonomous coding agents**, in a specific
production system — a travel-platform monorepo family (Python/FastAPI +
Postgres, Cloudflare Workers/TypeScript + D1, Nuxt/Vue frontend) where
briefs are queued, machine-routed on frontmatter fields, pre-flighted by a
reviewer agent called the **sovereign-architect (SA)**, executed in isolated
worktrees, and merged through an agent review chain.

The editor sits **upstream** of the SA gate:

```
author drafts brief → THIS EDITOR → author revises → SA gate → queue → executor
```

The SA is the binding pre-flight: it grounds every finding against live code
and a live database, and it emits copy-paste patches. This editor exists so
drafts arrive at that gate clean enough to clear in **one round**. The number
that justifies it: one real brief (`EXPLORA-TP-1`) took 13 SA traps and two
full review rounds — six of the traps were boilerplate a five-minute editing
pass would have deleted.

## An editor is not a rewriter

That distinction is the entire design. When this editor reviews a draft, it
returns numbered findings, each one anchored to a **verbatim quote** of the
draft lines that don't work, with three parts: the defect, what the cold
executor will actually *do* (a behavioral prediction, never "this is
unclear"), and the *direction* of the fix. Never replacement text. Never a
fixed frontmatter block. Never "here's the corrected phase."

The rewrite request arrives wearing disguises, and `rules.md` names and
refuses each one explicitly:

| Disguise | What it actually is |
|---|---|
| "Just fix it / apply your feedback" | A rewrite. |
| "Ask me questions and assemble the brief" | A rewrite with extra steps. |
| "Give me two versions and I'll pick" | A rewrite, twice. |
| "What should this section say instead?" | A rewrite, dictated. |
| "Write the patch like the SA does" | The SA's lane, downstream. |
| "Draft the fix so I can edit it" | A rewrite with the authorship laundered. |

Why hold this line in a system where a *downstream* agent legitimately emits
patches? Because the author who fixes their own defect learns the trap
family; the author who pastes a fix ships the next instance of it. And
because a brief the editor rewrote is a brief nobody owns — the author reads
it as the editor's, the editor reads it as done, and the next defect in it
belongs to no one.

## Ninety seconds to see the gate work

No API key, no network, no dependencies beyond Python 3 stdlib:

```
git clone https://github.com/alexschwager/agent-brief-editor
cd agent-brief-editor
python3 tests/verify.py selftest
```

Four expectations run:

1. `tests/fixtures/sample-brief.md` — a shape-conformant draft with three
   seeded judgment flaws (a slug-keyed live UPDATE with no rowcount guard, a
   directory-glob input definition, a missing cold-start phase) — **passes**
   the mechanical shape checks. Shape-clean and still dangerous: that split
   is the point.
2. `tests/fixtures/review-pass.md` — a compliant review of those three flaws —
   **passes** the full output contract (28/28 checks).
3. `tests/fixtures/review-fail.md` — a review that "helpfully" rewrites
   (drop-in SQL block, drop-in bash Phase 0, "replace with:", a paraphrased
   quote, a skipped finding ID) — **is caught and failed on seven distinct
   checks.**

4. The `contract` mode — the prose contract in `rules.md` still states every
   literal the verifier enforces (the seam guard) — **passes.**

Exit code 0 means all four expectations met. Then run it on your own use:

```
python3 tests/verify.py brief  <your-draft.md>                # mechanical shape checks
python3 tests/verify.py review <editor-output.md> <draft.md>  # the output contract
```

## The folder

Each file does one job:

| File | The one job |
|---|---|
| `identity.md` | Who the editor is, what it reviews, where it sits in the pipeline, the three heights it reads at. |
| `rules.md` | How it critiques: the never-rewrite rule and its disguise table, verbatim quote-anchoring, ground-or-label honesty, the machine-checkable output contract, re-review-by-ID discipline. |
| `examples.md` | What good critique looks like — drawn from a real five-round review record, plus a refusal exchange and a generic-vs-real calibration pair. Examples only; no rules hide here. |
| `reference/trap-taxonomy.md` | The seven defect families: the SA's five Agentic Execution Trap families (language/framework, state-bleed/testing, helpful-agent/scope-creep, git/environment, hearsay/blind-wait) plus the editor's two upstream heights (machine conformity, executability economy). |
| `reference/brief-shape-checklist.md` | The conformity checks: seven mechanical rows the verifier enforces, nine judgment rows the editor reads. |
| `reference/known-failures.md` | The case files behind every rule — what each one cost when it was learned, real numbers kept. Including one the reviewer itself got wrong. |
| `tests/verify.py` | The offline enforcement layer. |
| `tests/fixtures/` | The seeded-flaw brief and the pass/fail reviews the selftest runs. |

To use it as an editor: drop the folder into a Claude project (or point a
session at it), have it read `identity.md` → `rules.md` → `reference/` →
`examples.md`, then
hand it a draft. It returns findings in the `rules.md` §Rule 6 format — which
is exactly the format `verify.py review` checks.

## What the verifier actually enforces

`verify.py review` is a tripwire line under the editor's promises:

- **Verdict discipline** — exactly one `VERDICT:` line; `READY FOR SA` only
  with zero findings; the declared count matches the findings present.
- **ID discipline** — findings numbered `BE-1..n`, sequential, unique; the
  re-review convention (walk old IDs, never reuse them) has something to
  anchor to.
- **Anchoring** — every finding carries a blockquote, and every blockquote is
  verbatim-present in the draft under review (whitespace-collapsed match). A
  paraphrased anchor fails mechanically, no matter how convincing it reads.
- **Honesty tags** — every finding declares `grounded: verified — <evidence>`
  or `grounded: unverified — <the check that would settle it>`.
- **No-rewrite scans** — three of them: rewrite phrasing ("replace with:",
  "here is the revised", "paste this", …); any fenced block longer than three
  lines that does *not* come from the draft (replacement text has nowhere to
  hide — quoting the draft's own code is always legal, supplying new code
  never is); and reconstructed frontmatter.

**An editor output that fails `verify.py` is discarded, not argued with.**

## Provenance

Distilled 2026-08-18 from a private operations vault where this pipeline
runs: the sovereign-architect's rubric (the binding downstream authority this
editor conforms to and never supersedes), the brief template and its machine
contract, the doctrine pages behind the trap families, and an archive of
**829 briefs carrying SA review blocks**. The richest single record — a brief
that took five SA rounds — supplied `examples.md` nearly wholesale.

That record also supplies the editor's most important calibration, kept
deliberately: **round 1's Trap 2 was wrong.** The reviewer asserted "there is
no unique index on `slug`" after checking `pg_constraint` only; round 2
re-grounded against `pg_indexes` and found a *partial* unique index
(`WHERE deleted_at IS NULL`) — the real hazard was soft-delete tombstones,
which round 1's proposed guard did not close. The correction supersedes the
wrong finding without deleting it. A `grounded: verified` tag with a named
method was still wrong, because the method had a blind spot. That is why the
tag must name *how* it verified, and why the re-review walk — not the tag —
is the correction mechanism. The full case is in
`reference/known-failures.md`.

What ships here and what doesn't: the distilled system and a runnable
fixture gate ship; the 829-brief corpus, the live database, and the vault
pages the reference files cite by path (`20-Doctrine/...`,
`01-Queue/archive/...`) stay private. Those paths are kept in the text as
honest provenance pointers — they will not resolve in this repo, and no
claim in this README depends on your ability to read them.

## Don't take the claims — where each one would break

- **"It never rewrites."** Enforced only as far as the scanner reaches. A
  rewrite dictated in flowing prose — no fenced block, no trigger phrase —
  passes `verify.py` and is caught only by a human holding `rules.md` Rule 0.
  The scanner is a tripwire, not a proof.
- **"The contract is machine-checked."** The output contract lives twice —
  prose in `rules.md`, regex constants in `tests/verify.py` — and until
  2026-08-19 nothing kept them agreeing (a seam found by running a rival
  entrant's cartographer, Cassini, over this repo — credit where due). The
  `contract` selftest now pins every enforced literal to the prose, so a
  one-sided edit goes red in CI; a change that rewords BOTH sides
  consistently-but-differently still slips it.
- **"Quotes are verbatim."** Checked whitespace-collapsed. An anchor edited
  in ways collapse normalizes away still passes; a semantically-faithful
  paraphrase fails. The check is byte-honesty, not meaning-honesty.
- **"Findings are grounded."** The verifier checks the tag's *presence*, not
  its *truth*. The five-round record above shows a verified-tagged claim
  being wrong. Grounding has failure modes; the folder documents its own.
- **"Edited drafts clear the SA in one round."** **Unproven.** The measure
  that matters — SA rounds-to-clear on edited vs. unedited drafts — has not
  been run. `EXPLORA-TP-1`'s 13 traps motivate the editor; they do not
  validate it. Nothing here is dressed as a result that doesn't exist yet.
- **"The fixtures prove the gate."** They prove the gate catches *these*
  seeded violations. Nine-fixture-style adversarial coverage (a distinct
  negative fixture per named check) is the obvious next hardening; today
  `review-fail.md` trips seven checks in one file.
- **Portability.** The trap taxonomy is split roughly half universal (glob
  hazards, false-green liveness pings, foreground-process hangs, mock-factory
  false-greens) and half system-specific (this pipeline's frontmatter
  contract, this stack's fixtures). Swapping `reference/` for your own
  system's equivalents is the intended reuse path; it has not been
  demonstrated on a second system.

## What this is not

- **Not the sovereign-architect.** The SA grounds against live code and a
  live DB and emits Implementation Patches; it remains the binding gate.
  This editor is the pass before it, and refuses the SA's lane when asked.
- **Not a code reviewer.** It reviews the *instructions*, not the diff the
  instructions eventually produce.
- **Not a general writing editor.** Outside its one artifact class, its
  taxonomy is noise.

## If you read one file

`reference/known-failures.md` — the case files. Every rule in this folder is
a receipt from something that actually went wrong, with the numbers left in,
including the one where the reviewer was the thing that was wrong.

And if you find a break — a rewrite that slips the scanner, a check that
false-passes, a trap family the taxonomy misses — open an issue. The
known-failures file shows exactly what happens to found breaks here: they
become rules, with their numbers kept.
