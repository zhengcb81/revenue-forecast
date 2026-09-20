"""Final consistency check for cards M25-M28 (stdlib only; reads the attempt artefacts).

Verifies the cross-document invariants the reviewer will attack first:
  1. card id / model_id / title consistent across oracle.md, binding.json, handoff.json, review.md
  2. every commands.json argv path exists (or is a python/venv interpreter path)
  3. every commands.json unit scopes this card only
  4. qualification.json: formula=review_pending, disclosure_adaptation=unmapped, accuracy=unproven
  5. every evidence file named in the delivery contract exists
  6. evidence_hashes.json matches the files on disk
  7. no file under the four attempts claims 'accepted'
  8. no write happened under PLAN/reviews

Run:
  python -X utf8 -B scripts/verify_attempt.py --card M25 --attempt-root <attempt> --plan-root <plan>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

REQUIRED_EVIDENCE = [
    "input.json", "oracle.json", "cases.json", "source_manifest.json", "command_manifest.json",
    "stdout.txt", "stderr.txt", "formula_result.json", "negative_results.json",
    "qualification.json", "oq_rulings.json", "integrity.json", "oracle_selfcheck.json",
    "revision_r2.json", "evidence_hashes.json", "run_result.json",
]
REQUIRED_ROOT = ["binding.json", "oracle.md", "commands.json", "decision.md", "handoff.json",
                 "changes.diff", "review.md"]


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--plan-root", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)
    problems = []
    notes = []

    binding = load(os.path.join(attempt, "binding.json"))
    handoff = load(os.path.join(attempt, "handoff.json"))
    qual = load(os.path.join(ev, "qualification.json"))
    commands = load(os.path.join(attempt, "commands.json"))
    model_id = binding["model_id"]

    # 1. titles
    oracle_md = read(os.path.join(attempt, "oracle.md"))
    review_md = read(os.path.join(attempt, "review.md"))
    decision_md = read(os.path.join(attempt, "decision.md"))
    if not oracle_md.startswith("# %s " % card):
        problems.append("oracle.md does not start with '# %s '" % card)
    if model_id not in oracle_md.splitlines()[0]:
        problems.append("oracle.md title does not carry the model_id " + model_id)
    if not review_md.startswith("# %s " % card):
        problems.append("review.md does not start with '# %s '" % card)
    if model_id not in review_md.splitlines()[2]:
        problems.append("review.md line 3 does not carry the model_id")
    if not decision_md.startswith("# %s " % card):
        problems.append("decision.md does not start with '# %s '" % card)
    for doc, label in ((binding, "binding.json"), (handoff, "handoff.json")):
        if doc.get("card_id") != card:
            problems.append("%s card_id mismatch" % label)
        if doc.get("model_id") != model_id:
            problems.append("%s model_id mismatch" % label)
        if doc.get("attempt_id") != "a20260919-01":
            problems.append("%s attempt_id mismatch" % label)

    # 2/3. commands.json argv paths + scope
    missing_paths = []
    for unit in commands["units"]:
        for token in unit["argv"]:
            if not isinstance(token, str):
                continue
            if token.startswith("-") or token in ("python", "powershell", "Copy-Item"):
                continue
            if "/" in token or "\\" in token:
                if not os.path.exists(token):
                    missing_paths.append((unit["unit_id"], token))
        joined = " ".join(str(t) for t in unit["argv"])
        for other in ("M25", "M26", "M27", "M28"):
            if other != card and ("execution_runs\\%s\\" % other) in joined:
                problems.append("unit %s references another card's attempt: %s"
                                % (unit["unit_id"], joined))
    if missing_paths:
        problems.append("commands.json argv paths that do not exist: %s" % missing_paths)

    # 4. qualification
    if qual["formula"]["state"] != "review_pending":
        problems.append("qualification.formula is not review_pending")
    if qual["disclosure_adaptation"]["state"] != "unmapped":
        problems.append("qualification.disclosure_adaptation is not unmapped")
    if qual["accuracy"]["state"] != "unproven":
        problems.append("qualification.accuracy is not unproven")
    if qual["formula"]["a_to_c_conditions"]["negatives_rejected"].split("/")[0] != \
            qual["formula"]["a_to_c_conditions"]["negatives_rejected"].split("/")[1]:
        problems.append("qualification reports unrejected negatives")

    # 5. required evidence
    for name in REQUIRED_EVIDENCE:
        if not os.path.exists(os.path.join(ev, name)):
            problems.append("missing evidence file: " + name)
    for name in REQUIRED_ROOT:
        if not os.path.exists(os.path.join(attempt, name)):
            problems.append("missing attempt file: " + name)
    for name in ("before", "after", "scripts", "iso", "recovery"):
        if not os.path.isdir(os.path.join(attempt, name)):
            problems.append("missing attempt directory: " + name)
    if not os.path.exists(os.path.join(attempt, "recovery", "README.md")):
        problems.append("missing recovery/README.md")

    # 6. evidence_hashes
    recorded = load(os.path.join(ev, "evidence_hashes.json"))["hashes"]
    bad = []
    for rel, expected in recorded.items():
        path = rel if os.path.isabs(rel) else os.path.join(attempt, rel)
        if not os.path.exists(path):
            bad.append((rel, "missing"))
        elif sha256_file(path) != expected:
            bad.append((rel, "hash mismatch"))
    if bad:
        problems.append("evidence_hashes.json stale for: %s" % bad[:6])
    else:
        notes.append("evidence_hashes.json verifies %d files" % len(recorded))

    # 7. nobody signed accepted
    for name in REQUIRED_ROOT + ["recovery/README.md"]:
        path = os.path.join(attempt, name.replace("/", os.sep))
        text = read(path)
        for pattern in ('"formula": "accepted_scoped"', '"state": "accepted_scoped"',
                        "formula: accepted_scoped", "accepted_scoped (implementer",
                        "I accept", "本实现者接受"):
            if pattern in text:
                problems.append("%s contains a signing pattern: %r" % (name, pattern))
    if load(os.path.join(ev, "qualification.json"))["formula"]["state"] != "review_pending":
        problems.append("qualification.formula is not review_pending")
    if handoff["status"] != "review_pending":
        problems.append("handoff.status is not review_pending")
    if handoff.get("implementer_is_not_the_reviewer") is not True:
        problems.append("handoff does not assert implementer_is_not_the_reviewer")
    notes.append("no signing pattern; qualification.formula is review_pending "
                 "(the r1 verdict accepted_scoped is REPORTED, not signed)")

    # 8. PLAN/reviews untouched
    reviews = os.path.join(args.plan_root, "reviews")
    if os.path.isdir(reviews):
        newest = max((os.path.getmtime(os.path.join(dp, f))
                      for dp, _, fs in os.walk(reviews) for f in fs), default=0)
        cutoff = 1789808733  # 2026-09-19 10:05:33 local; newest reviews mtime is 10:05:32
        if newest > cutoff:
            problems.append("PLAN/reviews has a file newer than the frozen capture: %.0f" % newest)
        else:
            notes.append("PLAN/reviews newest mtime %.0f (<= frozen 1789808732)" % newest)

    print("verify %s (%s)" % (card, model_id))
    for note in notes:
        print("  ok:", note)
    if problems:
        print("  PROBLEMS:")
        for problem in problems:
            print("   -", problem)
        return 1
    print("  all consistency checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
