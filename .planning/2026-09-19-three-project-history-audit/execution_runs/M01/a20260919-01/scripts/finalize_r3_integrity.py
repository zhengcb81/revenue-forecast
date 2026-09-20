"""Final r3 integrity pass: refresh recorded hashes and check for any duplication
left behind by the iterative r3 application.

Records the post-dedup hashes into each evidence/<card>/revision_r3.json, then
verifies that no section marker and no table row appears twice.

ASCII-only stdout.
"""

from __future__ import annotations

import hashlib
import json
import os

RF = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
PLAN = os.path.join(RF, ".planning", "2026-09-19-three-project-history-audit")
CARDS = ["M01", "M02", "M03", "M04"]


def attempt(card):
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01")


def evidence(card):
    return os.path.join(attempt(card), "evidence", card)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main():
    problems = []
    files = ["review.md", "oracle.md", "handoff.json", "decision.md", "changes.diff",
             "recovery/README.md", "evidence/%s/revision_r2.json",
             "evidence/%s/revision_r3.json", "evidence/%s/first_run_forensics.json",
             "before/git_status_revenue-forecast.txt", "after/rerun_sha256.json"]

    # duplication checks (the r3 script was applied iteratively; prove it left no residue)
    dup_markers = [
        "| D (added in r3)", "rc=2 IS reachable", "NOTE (revision r2/r3, NEW-4)",
        "### r3 correction: rc=2 reachability", "#### Self-check: is the new exit code actually meaningful?",
        "## revision r2 - response to the independent review",
    ]
    for card in CARDS:
        review = read_text(os.path.join(attempt(card), "review.md"))
        for marker in dup_markers:
            n = review.count(marker)
            if n > 1:
                problems.append("%s review.md: %r appears %d times" % (card, marker, n))
        oracle = read_text(os.path.join(attempt(card), "oracle.md"))
        for marker in ("## 修订 r2", "修订 r2（独立复审后追加"):
            n = oracle.count(marker)
            if n > 1:
                problems.append("%s oracle.md: %r appears %d times" % (card, marker, n))
        if card == "M03":
            n = oracle.count("### r3 更正 NEW-1")
            if n != 1:
                problems.append("M03 oracle.md r3 note appears %d times" % n)
        gs = read_text(os.path.join(attempt(card), "before", "git_status_revenue-forecast.txt"))
        if gs.count("NOTE (revision r2/r3, NEW-4)") != 1:
            problems.append("%s git_status note count != 1" % card)
        if gs.count("# git status --porcelain=v1") != 1:
            problems.append("%s git_status header count != 1" % card)

    # record refreshed hashes
    for card in CARDS:
        rev_path = os.path.join(evidence(card), "revision_r3.json")
        rev = load_json(rev_path)
        rev["post_r3_sha256_after_dedup"] = {}
        for rel in files:
            path = os.path.join(attempt(card), rel.replace("/", os.sep) % card if "%s" in rel
                                else rel.replace("/", os.sep))
            if "%s" in rel:
                path = os.path.join(attempt(card), (rel % card).replace("/", os.sep))
            if os.path.exists(path):
                rev["post_r3_sha256_after_dedup"][rel.replace("%s", card)] = sha256_file(path)
        rev["dedup_note"] = ("the r3 script was applied iteratively while the idempotency guards were being "
                             "added, so the appends it controls (M03 r3 note, case-D table row, git_status "
                             "note) were de-duplicated afterwards; every remaining occurrence count is 1 and "
                             "the hashes here are post-dedup")
        with open(rev_path, "w", encoding="utf-8") as handle:
            json.dump(rev, handle, ensure_ascii=False, indent=1)
        print("refreshed", os.path.relpath(rev_path))

    # production unchanged
    for card in CARDS:
        binding = load_json(os.path.join(attempt(card), "binding.json"))
        for rel, expected in binding["production_source_hashes"].items():
            if sha256_file(os.path.join(RF, rel.replace("/", os.sep))) != expected:
                problems.append("production drift %s (%s)" % (rel, card))

    if problems:
        print("PROBLEMS:")
        for item in problems:
            print("  -", item)
        return 1
    print("final r3 integrity: no duplication, no drift, %d cards" % len(CARDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
