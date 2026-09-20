"""Revision r3 part 2: product re-run (raw rc) + full verification sweep.

Re-runs the SAME product call (calculate_registered_model via run_card.py) on all
four cards with the verdict-carrying exit code, records the raw return codes, then
re-verifies:
  * r3 items landed (NEW-1..NEW-4) with no leftovers and no duplicates
  * the M03 unit price is now internally consistent with the printed result
  * exit_code_semantics present and 0
  * qualifications unchanged (accepted_scoped formula / unmapped / unproven)
  * every JSON parses; no UTF-16
  * no production file changed

ASCII-only stdout.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess

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


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main():
    results = {}
    print("=== r3 product re-run (verdict-carrying exit code) ===")
    for card in CARDS:
        py = os.path.join(attempt(card), "iso", "venv", "Scripts", "python.exe")
        argv = [py, "-X", "utf8", "-B", os.path.join(attempt(card), "scripts", "run_card.py"),
                "--card", card, "--attempt", attempt(card),
                "--code-root", os.path.join(attempt(card), "iso", "checkout_scripts"),
                "--out", os.path.join(evidence(card), "run_result.json")]
        proc = subprocess.run(argv, cwd=attempt(card), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.decode("utf-8", "replace")
        err = proc.stderr.decode("utf-8", "replace")
        with open(os.path.join(evidence(card), "stdout.txt"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(out)
        with open(os.path.join(evidence(card), "stderr.txt"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(err)
        run = load_json(os.path.join(evidence(card), "run_result.json"))
        results[card] = {"raw_returncode": proc.returncode,
                         "exit_code_semantics": run["exit_code_semantics"],
                         "negative_summary": run["negative_summary"],
                         "positive_actual": run["positive"].get("actual")}
        print("  %s raw_rc=%d verdict=%s negatives=%d/%d"
              % (card, proc.returncode, run["exit_code_semantics"]["verdict"],
                 run["negative_summary"]["passed"], run["negative_summary"]["total"]))

        # fresh after/ hashes
        after = os.path.join(attempt(card), "after")
        doc = load_json(os.path.join(after, "rerun_sha256.json"))
        doc["revision"] = "r2 + r3"
        doc["r3_rerun_raw_returncode"] = proc.returncode
        doc["r3_sha256"] = {
            "evidence/%s/run_result.json" % card: sha256_file(os.path.join(evidence(card), "run_result.json")),
            "evidence/%s/stdout.txt" % card: sha256_file(os.path.join(evidence(card), "stdout.txt")),
            "evidence/%s/stderr.txt" % card: sha256_file(os.path.join(evidence(card), "stderr.txt")),
        }
        dump_json(os.path.join(after, "rerun_sha256.json"), doc)
        with open(os.path.join(after, "rerun_stdout.txt"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(out)
        with open(os.path.join(after, "rerun_stderr.txt"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(err)

    # ---------------- verification sweep ----------------
    print("\n=== r3 verification sweep ===")
    problems = []

    # M03: the printed unit price must be consistent with the printed result.
    # The stale value may survive ONLY inside the r3 note that documents the fix.
    m03_oracle = read_text(os.path.join(attempt("M03"), "oracle.md"))
    marker = "### r3 更正 NEW-1"
    if marker not in m03_oracle:
        problems.append("M03 oracle.md missing the r3 NEW-1 note")
    else:
        frozen_body, r3_note = m03_oracle.split(marker, 1)
        if "123,751.5203" in frozen_body:
            problems.append("M03 frozen body still prints the inconsistent unit price 123,751.5203")
        if "123,751.503987" not in frozen_body:
            problems.append("M03 frozen body missing the corrected unit price 123,751.503987")
        if "123,751.5203" not in r3_note:
            problems.append("M03 r3 note no longer documents the value it replaced")
        # the frozen body must not still pair the stale price with the result
        if "123,751.5203… = 528,684,368,999.31" in frozen_body:
            problems.append("M03 frozen body still pairs the stale unit price with the corrected result")
    if m03_oracle.count(marker) != 1:
        problems.append("M03 oracle.md r3 note count = %d (expected 1)" % m03_oracle.count(marker))
    forensics_text = read_text(os.path.join(evidence("M01"), "first_run_forensics.json"))
    if "byte-exact prefix hash" not in forensics_text:
        problems.append("M01 forensics missing the byte-exact prefix hash annotation")

    for card in CARDS:
        # rc=2 claims corrected on every card
        review = read_text(os.path.join(attempt(card), "review.md"))
        if "rc=2 is not yet reachable in practice" in review:
            problems.append("%s still carries the wrong rc=2 claim" % card)
        if "rc=2 IS reachable" not in review:
            problems.append("%s missing the corrected rc=2 statement" % card)
        if "D (added in r3)" not in review:
            problems.append("%s self-check table missing the case-D row" % card)
        # NEW-4 header present exactly once
        gs = read_text(os.path.join(attempt(card), "before", "git_status_revenue-forecast.txt"))
        if gs.count("NOTE (revision r2/r3, NEW-4)") != 1:
            problems.append("%s git_status header count wrong" % card)
        # r3 record
        rev = load_json(os.path.join(evidence(card), "revision_r3.json"))
        if rev["items"]["NEW-2"]["case_D_raw_returncode"] != 2:
            problems.append("%s r3 record does not carry case D rc=2" % card)
        # qualifications
        qual = load_json(os.path.join(evidence(card), "qualification.json"))
        if qual["disclosure_adaptation"]["status"] != "unmapped":
            problems.append("%s disclosure_adaptation changed" % card)
        if qual["accuracy"]["status"] != "unproven":
            problems.append("%s accuracy changed" % card)
        handoff = load_json(os.path.join(attempt(card), "handoff.json"))
        if "accepted_scoped" not in handoff["qualifications"]["formula"]:
            problems.append("%s handoff formula qualification not accepted_scoped" % card)
        if handoff["qualifications"]["disclosure_adaptation"] != "unmapped":
            problems.append("%s handoff disclosure qualification wrong" % card)
        if handoff["qualifications"]["accuracy"] != "unproven":
            problems.append("%s handoff accuracy qualification wrong" % card)
        if not any("requires_owner_or_specialist_ruling" in q for q in handoff["open_questions"]):
            problems.append("%s F-M02-01 open question lost" % card)
        # product re-run code
        if results[card]["raw_returncode"] != 0:
            problems.append("%s r3 product re-run rc=%d" % (card, results[card]["raw_returncode"]))
        # JSON + encoding
        for root, _dirs, files in os.walk(attempt(card)):
            if os.sep + "iso" + os.sep in root + os.sep or root.endswith(os.sep + "iso"):
                continue
            for name in files:
                path = os.path.join(root, name)
                if name.endswith(".json"):
                    try:
                        load_json(path)
                    except Exception as exc:  # noqa: BLE001
                        problems.append("JSON parse failure %s: %s" % (path, exc))
                if name.lower().endswith((".txt", ".md", ".json", ".diff", ".py", ".ps1")):
                    with open(path, "rb") as handle:
                        if handle.read(2) in (b"\xff\xfe", b"\xfe\xff"):
                            problems.append("UTF-16 file: %s" % path)
        # production unchanged
        binding = load_json(os.path.join(attempt(card), "binding.json"))
        for rel, expected in binding["production_source_hashes"].items():
            if sha256_file(os.path.join(RF, rel.replace("/", os.sep))) != expected:
                problems.append("production drift %s (%s)" % (rel, card))

    # M02 must still not have self-decided F-M02-01
    rev02 = load_json(os.path.join(evidence("M02"), "revision_r3.json"))
    if "F-M02-01" not in rev02["reserved_for_owner_ruling"]:
        problems.append("M02 r3 record lost the F-M02-01 reservation")

    if problems:
        print("PROBLEMS:")
        for item in problems:
            print("  -", item)
        return 1
    print("all r3 checks passed: %d cards, no problems" % len(CARDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
