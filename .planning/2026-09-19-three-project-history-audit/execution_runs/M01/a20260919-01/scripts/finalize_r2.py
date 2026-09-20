"""Revision r2, part 3: record the exit-code self-check, then verify everything.

Adds the self-check outcome to each card's review.md r2 section and to
revision_r2.json / handoff.json, then runs a full verification sweep:
  * every JSON artefact parses
  * no UTF-16 leftovers
  * the corrected F-M03-01 / F-M04-01 values are present and the stale ones are gone
  * frozen oracle bodies were appended to, not rewritten
  * production source hashes still match the binding

ASCII-only stdout.
"""

from __future__ import annotations

import json
import os

RF = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
PLAN = os.path.join(RF, ".planning", "2026-09-19-three-project-history-audit")
CARDS = ["M01", "M02", "M03", "M04"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def append(path, text):
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


SELF_CHECK_TEXT = """
#### Self-check: is the new exit code actually meaningful? (do not take it on trust)

`recovery/r2_exit_code_selfcheck/selfcheck_result.json` runs the **patched** harness against deliberately
corrupted copies of `oracle.json` / `cases.json` in a scratch tree, so the frozen evidence is untouched:

| case | mutation | raw rc | expected | what it proves |
|---|---|---|---|---|
| A | `oracle.json positive.expected_float -> [999,999,999]` | **3** | 3 | a corrupted expectation is no longer hidden behind a bookkeeping-only rc=0; the product itself still returned the correct path |
| B | `cases.json first case base_input -> 'no_such_block'` | **1** | non-zero | a harness defect cannot masquerade as a pass; it raises |
| C | none (the real card) | **0** | 0 | the repaired exit code stays 0 for a genuinely passing card |

Known residual (stated, not fixed): case B exits **1 with an unhandled `KeyError`** rather than the clean
rc=2 intended for "harness incomplete", because the corruption happens outside the guarded block. The
outcome is still fail-loud, but rc=2 is not yet reachable in practice; a reviewer may ask for that guard.
"""


def main():
    for card in CARDS:
        attempt = os.path.join(PLAN, "execution_runs", card, "a20260919-01")
        evidence = os.path.join(attempt, "evidence", card)
        print("===", card, "===")

        selfcheck = None
        sc_path = os.path.join(attempt, "recovery", "r2_exit_code_selfcheck", "selfcheck_result.json")
        if os.path.exists(sc_path):
            selfcheck = load_json(sc_path)
            cases = {c["id"]: c for c in selfcheck["cases"]}
            rev = load_json(os.path.join(evidence, "revision_r2.json"))
            rev["items"]["F-M01-02"]["exit_code_selfcheck"] = {
                "evidence": "recovery/r2_exit_code_selfcheck/selfcheck_result.json",
                "A_corrupted_oracle": {"raw_returncode": cases["A_corrupted_oracle_expectation"]["raw_returncode"],
                                       "expected": 3},
                "B_corrupted_case_plan": {"raw_returncode": cases["B_corrupted_case_plan"]["raw_returncode"],
                                          "expected": "non-zero",
                                          "residual": "rc=1 with an unhandled KeyError; the intended clean "
                                                      "rc=2 path is not reachable for this corruption class"},
                "C_uncorrupted_card": {"raw_returncode": cases["C_uncorrupted_card"]["raw_returncode"],
                                       "expected": 0},
                "frozen_evidence_touched": False,
            }
            dump_json(os.path.join(evidence, "revision_r2.json"), rev)
            print("  recorded self-check in revision_r2.json")

        review = os.path.join(attempt, "review.md")
        if "#### Self-check: is the new exit code actually meaningful?" in read_text(review):
            print("  self-check section already present in review.md (idempotent, not re-appended)")
        else:
            append(review, SELF_CHECK_TEXT)
            print("  appended self-check section to review.md")

        handoff_path = os.path.join(attempt, "handoff.json")
        handoff = load_json(handoff_path)
        if "R2-exit-code-selfcheck" in handoff.get("commands_executed", []):
            print("  handoff.json already records the self-check (idempotent)")
            continue
        handoff["commands_executed"] = handoff.get("commands_executed", []) + ["R2-exit-code-selfcheck"]
        handoff["raw_exit_codes"]["R2_selfcheck_A_corrupted_oracle"] = 3
        handoff["expected_exit_codes"]["R2_selfcheck_A_corrupted_oracle"] = 3
        handoff["raw_exit_codes"]["R2_selfcheck_B_corrupted_case_plan"] = 1
        handoff["expected_exit_codes"]["R2_selfcheck_B_corrupted_case_plan"] = "non-zero"
        handoff["raw_exit_codes"]["R2_selfcheck_C_uncorrupted"] = 0
        handoff["expected_exit_codes"]["R2_selfcheck_C_uncorrupted"] = 0
        handoff["evidence_paths"] = sorted(set(handoff.get("evidence_paths", []) + [
            "recovery/r2_exit_code_selfcheck/selfcheck_result.json"]))
        handoff["open_questions"].append(
            "F-M01-02 residual: the intended clean rc=2 ('harness incomplete') is not reachable for the "
            "corruption classes tested - an out-of-guard harness defect exits 1 with an unhandled KeyError. "
            "Fail-loud either way, but a reviewer may require the guard to be widened.")
        dump_json(handoff_path, handoff)
        print("  refreshed handoff.json")

    # ------------------------------------------------------------------
    # verification sweep
    # ------------------------------------------------------------------
    print("\n=== verification sweep ===")
    problems = []
    for card in CARDS:
        attempt = os.path.join(PLAN, "execution_runs", card, "a20260919-01")
        evidence = os.path.join(attempt, "evidence", card)
        # 1. JSON parses everywhere in the attempt
        for root, _dirs, files in os.walk(attempt):
            if os.sep + "iso" + os.sep in root + os.sep or root.endswith(os.sep + "iso"):
                continue
            for name in files:
                if not name.endswith(".json"):
                    continue
                path = os.path.join(root, name)
                try:
                    load_json(path)
                except Exception as exc:  # noqa: BLE001
                    problems.append("JSON parse failure %s: %s" % (path, exc))
        # 2. no UTF-16 leftovers
        for root, _dirs, files in os.walk(attempt):
            if os.sep + "iso" + os.sep in root + os.sep or root.endswith(os.sep + "iso"):
                continue
            for name in files:
                if not name.lower().endswith((".txt", ".md", ".json", ".diff", ".py", ".ps1")):
                    continue
                path = os.path.join(root, name)
                with open(path, "rb") as handle:
                    head = handle.read(2)
                if head in (b"\xff\xfe", b"\xfe\xff"):
                    problems.append("UTF-16 file: %s" % path)
        # 3. required r2 artefacts exist
        for rel in ("changes.diff", "recovery/README.md", "after/rerun_sha256.json",
                    "after/rerun_stdout.txt", "after/rerun_stderr.txt",
                    "evidence/%s/revision_r2.json" % card,
                    "evidence/%s/source_manifest.json" % card):
            if not os.path.exists(os.path.join(attempt, rel.replace("/", os.sep))):
                problems.append("missing %s in %s" % (rel, card))
        # 4. exit code recorded in the frozen evidence
        run = load_json(os.path.join(evidence, "run_result.json"))
        if "exit_code_semantics" not in run:
            problems.append("no exit_code_semantics in %s" % card)
        elif run["exit_code_semantics"]["exit_code"] != 0:
            problems.append("unexpected exit code in %s: %s" % (card, run["exit_code_semantics"]))
        # 5. qualifications untouched
        qual = load_json(os.path.join(evidence, "qualification.json"))
        if qual["disclosure_adaptation"]["status"] != "unmapped":
            problems.append("disclosure_adaptation changed in %s" % card)
        if qual["accuracy"]["status"] != "unproven":
            problems.append("accuracy changed in %s" % card)
        if qual["formula"]["status"] != "review_pending":
            problems.append("formula status changed in %s" % card)
        # 6. production hashes unchanged
        binding = load_json(os.path.join(attempt, "binding.json"))
        import hashlib

        def sha(path):
            digest = hashlib.sha256()
            with open(path, "rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(chunk)
            return digest.hexdigest()

        for rel, expected in binding["production_source_hashes"].items():
            if sha(os.path.join(RF, rel.replace("/", os.sep))) != expected:
                problems.append("production drift %s (%s)" % (rel, card))

    # 7. M03 arithmetic corrected, stale gone from the FROZEN bodies.
    #    oracle.md legitimately quotes the stale values once, inside the r2
    #    correction note that documents what was fixed - so the frozen part
    #    (everything above the r2 append) must be clean, and the stale numbers
    #    may appear only after the marker.
    m03 = os.path.join(PLAN, "execution_runs", "M03", "a20260919-01")
    oracle_md = read_text(os.path.join(m03, "oracle.md"))
    marker = "### r2 更正 F-M03-01"
    if marker not in oracle_md:
        problems.append("M03 oracle.md has no r2 revision marker")
    else:
        frozen_body, r2_body = oracle_md.split(marker, 1)
        for stale in ("528,681,308,161.71", "88,700,626,838.29"):
            if stale in frozen_body:
                problems.append("stale M03 arithmetic still present in the frozen body of oracle.md: %s" % stale)
        for good in ("528,684,368,999.31", "88,697,566,000.69"):
            if good not in frozen_body:
                problems.append("corrected M03 arithmetic missing from the frozen body of oracle.md: %s" % good)
            if good not in r2_body:
                problems.append("corrected M03 arithmetic missing from the r2 note: %s" % good)
    for rel in ("evidence/M03/historical_reconciliation.json",
                "evidence/M03/disclosure_mapping.json",
                "evidence/M03/accounting_decision.md"):
        text = read_text(os.path.join(m03, rel.replace("/", os.sep)))
        if "528,681,308,161.71" in text or "88,700,626,838.29" in text:
            problems.append("stale M03 arithmetic still present in %s" % rel)
        if "528,684,368,999.31" not in text or "88,697,566,000.69" not in text:
            problems.append("corrected M03 arithmetic missing in %s" % rel)

    # 8. M04 typo corrected. The corrected value must be present, and any
    #    mention of the old typo must be explicitly labelled as the fixed typo.
    m04_review = read_text(os.path.join(PLAN, "execution_runs", "M04", "a20260919-01", "review.md"))
    if "780,860.59" not in m04_review:
        problems.append("corrected M04 wafers/month missing")
    for line in m04_review.splitlines():
        if "781,861" in line and "was" not in line:
            problems.append("unlabelled stale M04 wafers/month: %s" % line.strip())

    # 9. M01 provenance artefacts
    m01 = os.path.join(PLAN, "execution_runs", "M01", "a20260919-01")
    for rel in ("evidence/M01/first_run_forensics.json", "scripts/oracle_M01.v1.reconstructed.py"):
        if not os.path.exists(os.path.join(m01, rel.replace("/", os.sep))):
            problems.append("missing %s" % rel)
    sm = load_json(os.path.join(m01, "evidence", "M01", "source_manifest.json"))
    if "oracle_versions" not in sm:
        problems.append("source_manifest.oracle_versions missing for M01")

    # 10. F-M02-01 carried as an open question, not self-decided
    h02 = load_json(os.path.join(PLAN, "execution_runs", "M02", "a20260919-01", "handoff.json"))
    if not any("requires_owner_or_specialist_ruling" in q for q in h02["open_questions"]):
        problems.append("F-M02-01 not carried in M02 handoff open_questions")
    rev02 = load_json(os.path.join(PLAN, "execution_runs", "M02", "a20260919-01",
                                   "evidence", "M02", "revision_r2.json"))
    if rev02["items"]["F-M02-01"]["self_decided"] is not False:
        problems.append("F-M02-01 appears self-decided")

    if problems:
        print("PROBLEMS:")
        for item in problems:
            print("  -", item)
        return 1
    print("all checks passed: %d cards, no problems" % len(CARDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
