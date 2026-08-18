#!/usr/bin/env python3
"""Offline verifier for the dev brief editor. No API key, no network, stdlib only.

Modes:
  verify.py brief  <draft.md>              mechanical brief-shape checks (M1-M7)
  verify.py review <review.md> <draft.md>  editor-output contract + no-rewrite scans
  verify.py selftest                       run all fixture expectations (the demo)

Exit 0 = all checks pass. Exit 1 = at least one FAIL (selftest: unexpected outcome).
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

REPOS = {"travel-data-platform", "cloudflare-worker", "front-end"}
STATUSES = {"awaiting-sa", "queued", "ready", "in-progress", "in-review", "merged", "blocked"}
CATEGORIES = {
    "machine-conformity", "language-framework", "state-bleed-testing",
    "helpful-agent-scope-creep", "git-environment", "hearsay-blind-wait",
    "executability-economy",
}
REQUIRED_BRIEF_HEADINGS = [
    "## Context & Why", "## Scope", "### NOT in scope",
    "## Pre-execution verification", "## Phases", "## Verification",
]
FINDING_PARTS = ["**Defect.**", "**Why it fails.**", "**Fix direction.**"]
REWRITE_PHRASES = [
    "here is the corrected", "here is the revised", "here's the corrected",
    "rewritten brief", "revised brief", "replace with:", "replace it with",
    "replace this with", "paste this", "copy-paste", "should read:",
    "change it to:", "updated frontmatter:",
]

results = []


def check(name, ok, detail=""):
    results.append(ok)
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f" — {detail}" if detail and not ok else ""))
    return ok


def collapse(text):
    return re.sub(r"\s+", " ", text).strip()


def frontmatter(text):
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    return m.group(1) if m else None


def fm_value(fm, key):
    m = re.search(rf"^{key}:[ \t]*([^\n#]*)", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


# ---------------------------------------------------------------- brief mode
def check_brief(path):
    text = Path(path).read_text(encoding="utf-8")
    fm = frontmatter(text)
    if not check("M1 frontmatter is the first fenced block", fm is not None):
        return
    missing = [k for k in ("brief", "status", "repo", "branch", "model",
                           "gemini_reviewed", "touches") if fm_value(fm, k) is None]
    check("M2 required frontmatter keys", not missing, f"missing: {missing}")
    repo = fm_value(fm, "repo") or ""
    check("M3 repo is machine-valued", repo in REPOS, f"repo: {repo!r} not in {sorted(REPOS)}")
    status = fm_value(fm, "status") or ""
    check("M4 status in lifecycle set", status in STATUSES, f"status: {status!r}")
    touches = fm_value(fm, "touches")
    touches_ok = touches is not None and (
        touches.startswith("[") or touches == "" and re.search(
            r"^touches:\s*(#[^\n]*)?\n(\s+-\s+\S+\n?)+", fm, re.MULTILINE))
    check("M5 touches is a list", bool(touches_ok), f"touches: {touches!r}")
    for h in REQUIRED_BRIEF_HEADINGS:
        check(f"M6 section present: {h}", h in text)
    check("M7 claim-gate heading carried",
          bool(re.search(r"^#+.*claim gate", text, re.MULTILINE | re.IGNORECASE)))
    check("M7 touches-guard heading carried",
          bool(re.search(r"^#+.*conflict guard", text, re.MULTILINE | re.IGNORECASE)))


# --------------------------------------------------------------- review mode
def fenced_blocks(text):
    return [m.group(1) for m in re.finditer(r"^```[^\n]*\n(.*?)^```", text,
                                            re.DOTALL | re.MULTILINE)]


def blockquotes(text):
    quotes, current = [], []
    for line in text.splitlines():
        if line.startswith(">"):
            current.append(line.lstrip("> ").rstrip())
        elif current:
            quotes.append(" ".join(current))
            current = []
    if current:
        quotes.append(" ".join(current))
    return [collapse(q) for q in quotes if collapse(q)]


def check_review(review_path, brief_path):
    review = Path(review_path).read_text(encoding="utf-8")
    brief = Path(brief_path).read_text(encoding="utf-8")
    brief_flat = collapse(brief)

    verdicts = re.findall(
        r"^VERDICT: (?:READY FOR SA|NOT READY)\s*[—-]+\s*(\d+) findings?\s*$",
        review, re.MULTILINE)
    check("V1 exactly one well-formed VERDICT line", len(verdicts) == 1,
          f"found {len(verdicts)}")
    declared = int(verdicts[0]) if len(verdicts) == 1 else -1
    ready = bool(re.search(r"^VERDICT: READY FOR SA", review, re.MULTILINE))

    ids = [int(m.group(1)) for m in re.finditer(r"^## BE-(\d+)", review, re.MULTILINE)]
    check("V2 finding IDs sequential from BE-1 and unique",
          ids == list(range(1, len(ids) + 1)), f"ids: {ids}")
    check("V3 verdict count matches findings", declared == len(ids),
          f"declared {declared}, found {len(ids)}")
    check("V4 READY only with zero findings", (not ready) or len(ids) == 0)

    sections = re.split(r"^## BE-\d+[^\n]*\n", review, flags=re.MULTILINE)[1:]
    for i, body in enumerate(sections, 1):
        cat = re.search(r"^- category:\s*(\S+)", body, re.MULTILINE)
        check(f"F{i} category tag valid", bool(cat) and cat.group(1) in CATEGORIES,
              f"category: {cat.group(1) if cat else None!r}")
        check(f"F{i} grounded tag present (verified/unverified)",
              bool(re.search(r"^- grounded:\s*(verified|unverified)\b", body, re.MULTILINE)))
        for part in FINDING_PARTS:
            check(f"F{i} has {part}", part in body)
        quotes = blockquotes(body)
        check(f"F{i} anchors a draft quote", bool(quotes))
        for q in quotes:
            check(f"F{i} quote is verbatim from the draft", q in brief_flat,
                  f"not found: {q[:80]!r}")

    # No-rewrite scans
    low = review.lower()
    hits = [p for p in REWRITE_PHRASES if p in low]
    check("R1 no rewrite phrases", not hits, f"hits: {hits}")
    long_alien = []
    for block in fenced_blocks(review):
        lines = [l for l in block.splitlines() if l.strip()]
        if len(lines) > 3 and collapse(block) not in brief_flat:
            long_alien.append(lines[0][:60])
    check("R2 no long fenced block absent from the draft (replacement text)",
          not long_alien, f"suspect blocks starting: {long_alien}")
    check("R3 no reconstructed frontmatter",
          not re.search(r"^---\s*\n(?:[^\n]*\n){0,4}?(?:brief|status|repo):",
                        review, re.MULTILINE))


# ------------------------------------------------------------------ selftest
def run_mode(argv):
    global results
    results = []
    if argv[0] == "brief":
        check_brief(argv[1])
    elif argv[0] == "review":
        check_review(argv[1], argv[2])
    else:
        raise SystemExit(f"unknown mode: {argv[0]}")
    ok = all(results)
    print(("ALL CHECKS PASS" if ok else "CHECKS FAILED") + f" ({sum(results)}/{len(results)})")
    return ok


def selftest():
    fx = HERE / "fixtures"
    expectations = [
        (["brief", str(fx / "sample-brief.md")], True,
         "sample brief passes mechanical shape checks"),
        (["review", str(fx / "review-pass.md"), str(fx / "sample-brief.md")], True,
         "compliant review passes the contract"),
        (["review", str(fx / "review-fail.md"), str(fx / "sample-brief.md")], False,
         "rewriting review is caught and failed"),
    ]
    failures = 0
    for argv, expected, label in expectations:
        print(f"\n=== selftest: {label} — expect {'PASS' if expected else 'FAIL'} ===")
        got = run_mode(argv)
        outcome = "OK" if got == expected else "SELFTEST MISMATCH"
        if got != expected:
            failures += 1
        print(f"=== {outcome}: got {'PASS' if got else 'FAIL'} ===")
    print(f"\nselftest: {len(expectations) - failures}/{len(expectations)} expectations met")
    return failures == 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        raise SystemExit(2)
    if args[0] == "selftest":
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0 if run_mode(args) else 1)
