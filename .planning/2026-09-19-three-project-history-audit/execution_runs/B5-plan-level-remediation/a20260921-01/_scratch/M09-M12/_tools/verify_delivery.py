"""REM-21 / batch M09-M12 -- final self-verification of the delivered claims.

Re-reads the delivered evidence.json and asserts every claim against the artifact it came from.
Prints a PASS/FAIL checklist.  Exit code 0 only if every check passes.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M09-M12")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M09-M12")
CARDS = ["M09", "M10", "M11", "M12"]

fails = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print("%-6s %s%s" % ("PASS" if ok else "FAIL", name, ("  <- " + detail) if detail else ""))
    if not ok:
        fails.append(name)


def sha(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    ev = json.load(open(os.path.join(BATCH, "evidence.json"), encoding="utf-8"))
    raw = json.load(open(os.path.join(SCRATCH, "_tools", "raw_rc.json"), encoding="utf-8"))
    rc = {(r["arm"], r["card"]): r["rc"] for r in raw["runs"]}

    # ---- deliverables exist
    for name in ("run_card.py", "run_card_before.py", "runner.diff", "evidence.json"):
        check("deliverable exists: %s" % name, os.path.exists(os.path.join(BATCH, name)))

    # ---- runner hashes
    check("runner_after.sha256 == file",
          ev["runner_after"]["sha256"] == sha(os.path.join(BATCH, "run_card.py")))
    check("runner_after.bytes == file size",
          ev["runner_after"]["bytes"] == os.path.getsize(os.path.join(BATCH, "run_card.py")))
    hist = os.path.join(PLAN, "execution_runs", "M09", "a20260919-01", "scripts", "run_card.py")
    check("runner_before.sha256 == read-only historical runner",
          ev["runner_before"]["sha256"] == sha(hist)
          == "997c553b0b9e6452e9edfeb8bfec3a40ff55d10f2646e562456913feb9332fce")
    check("runner_before.bytes == 28912", ev["runner_before"]["bytes"] == 28912)
    check("runner_before_copy.sha256 == runner_before.sha256",
          ev["runner_before_copy"]["sha256"] == ev["runner_before"]["sha256"])
    for card in CARDS:
        p = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "scripts", "run_card.py")
        check("historical runner %s byte-identical + untouched" % card,
              sha(p) == ev["runner_before"]["sha256"])

    # ---- rc constants unchanged in the patched runner
    src = open(os.path.join(BATCH, "run_card.py"), encoding="utf-8").read()
    consts = dict(re.findall(r"^(EXIT_\w+) = (\d+)$", src, re.M))
    check("rc constants unchanged", consts == {"EXIT_PASS": "0", "EXIT_HARNESS": "1",
                                              "EXIT_NO_VERDICT": "2", "EXIT_NEGATIVE": "3"},
          json.dumps(consts))

    # ---- frozen inputs
    for card in CARDS:
        p = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card,
                         "cases.json")
        e = os.path.join(SCRATCH, "E", "evidence", card, "cases.json")
        check("frozen cases.json %s hash (evidence + E arm verbatim)" % card,
              ev["cards_cases_sha256"][card] == sha(p) == sha(e))

    # ---- arm rc values, straight from the recorded child processes
    want = {"E": 0, "F": 3, "G": 2}
    for arm, rcval in want.items():
        check("arm %s rc=%d on every card" % (arm, rcval),
              all(rc[(arm, c)] == rcval for c in CARDS),
              json.dumps({c: rc[(arm, c)] for c in CARDS}))
        check("evidence.json arm %s rc == raw measured rc" % arm, ev["arms"][arm]["rc"] == rcval)
    check("arm B rc == raw measured rc (measurement, not a prediction)",
          ev["arms"]["B"]["rc"] == rc[("B", "M09")] == 3)
    check("historical_runner_already_gated == True", ev["historical_runner_already_gated"] is True)
    check("supplementary F2 rc == raw measured rc",
          all(ev["supplementary_arms"]["F2"]["rc"][c] == rc[("F2", c)] == 3 for c in CARDS))
    check("supplementary Gpre rc == raw measured rc",
          all(ev["supplementary_arms"]["Gpre"]["rc"][c] == rc[("Gpre", c)] == 1 for c in CARDS))

    # ---- arm observations, re-derived from the run outputs
    def out(arm, card, name="run_result.json"):
        p = os.path.join(SCRATCH, arm, card, name)
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

    for card in CARDS:
        e = out("E", card)
        check("E/%s: verdict pass, 11 PASS_rejected, mismatch 0" % card,
              e["verdict"] == "pass" and e["negative_summary"]["passed"] == 11
              and e["negative_counts"]["declared_expectation_mismatch"] == 0)
        f = out("F", card)
        nm = [x for x in f["negatives"] if x["id"] == "NEG-CARD"][0]
        check("F/%s: NEG-CARD FAIL_declared_expectation_mismatch + mismatch counter 1" % card,
              nm["verdict"] == "FAIL_declared_expectation_mismatch"
              and nm["declared_expectation_mismatch"] is True and nm["judged"] is True
              and nm["declared"] == "ValueError" and nm["raised"] == "ModelRegistryError"
              and f["negative_counts"]["declared_expectation_mismatch"] == 1
              and any("declared_expectation_mismatch:NEG-CARD" == r
                      for r in f["verdict_reasons"]))
        b = out("B", card)
        bn = [x for x in b["negatives"] if x["id"] == "NEG-CARD"][0]
        check("B/%s: OLD runner fires with its own label, no declared-expectation accounting" % card,
              bn["verdict"] == "FAIL_wrong_exception_type"
              and "declared_expectation_mismatch" not in bn
              and b["negative_summary"]["passed"] == 10)
        g = out("G", card)
        gn = [x for x in g["negatives"] if x["id"] == "NEG-CARD"][0]
        check("G/%s: rc=2 no_verdict, NEG-CARD NOT_JUDGED (not a mismatch)" % card,
              g["verdict"] == "no_verdict" and g["exit_code"] == 2
              and gn["verdict"] == "NOT_JUDGED_declaration_unusable"
              and gn["judged"] is False and gn["declared_expectation_mismatch"] is False
              and gn["declared_expectation_ok"] is None
              and g["negative_counts"]["declared_expectation_mismatch"] == 0
              and g["negative_counts"]["declared_expectation_missing_in_cases_json"] == 1
              and "cases_json_declared_expectation_missing:NEG-CARD" in g["verdict_reasons"])
        check("Gpre/%s: nothing written by the crashed OLD runner" % card,
              out("Gpre", card) is None)

    # ---- isolated code root identity
    for name, want_hash in (("model_registry.py",
                             "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"),
                            ("model_extensions.py",
                             "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911")):
        check("code_root/%s == iso sha256" % name,
              sha(os.path.join(SCRATCH, "code_root", name)) == want_hash
              == ev["isolated_code_root_sha256"][name])

    # ---- no NEW __pycache__ anywhere: -B must have prevented every bytecode write.  (The
    # pre-existing iso venv ships pip's own __pycache__ dirs from 2026-09-20; those predate this
    # session, so freshness - not mere existence - is the assertion.)
    marker = os.path.getmtime(os.path.join(SCRATCH, "_tools", "prepare_arms.py"))
    new_pyc, src_pyc = [], []
    for root in (ATTEMPT, *(os.path.join(PLAN, "execution_runs", c) for c in CARDS)):
        for dp, dn, fn in os.walk(root):
            base = os.path.basename(dp)
            if base == "__pycache__" and os.path.getmtime(dp) > marker:
                new_pyc.append(dp)
            if base in ("scripts", "checkout_scripts") and "__pycache__" in dn:
                src_pyc.append(dp)
    check("no __pycache__ created by this session (anywhere, incl. historical dirs)",
          not new_pyc, "; ".join(new_pyc[:3]))
    check("no __pycache__ at all under any scripts/ or iso/checkout_scripts/", not src_pyc,
          "; ".join(src_pyc[:3]))

    # ---- boundary: nothing historical modified during this session
    newer = []
    for c in CARDS:
        for dp, dn, fn in os.walk(os.path.join(PLAN, "execution_runs", c)):
            for f in fn:
                p = os.path.join(dp, f)
                if os.path.getmtime(p) > marker:
                    newer.append(os.path.relpath(p, PLAN))
    check("0 files newer than the session marker under execution_runs/M09..M12",
          not newer, "; ".join(newer[:3]))
    check("historical_writes == [] and boundaries_respected",
          ev["historical_writes"] == [] and ev["boundaries_respected"] is True)

    # ---- contract s2 required fields present in the new negative entries
    required = ["declared", "raised", "declared_expectation_ok", "declared_expectation_mismatch",
                "declared_expectation_not_met", "declared_expectation_comparison", "judged",
                "expected", "verdict", "raised_matches_expected_name"]
    f0 = out("F", "M09")
    missing = [k for k in required if k not in f0["negatives"][0]]
    check("s2 per-case fields present in every negative entry",
          not missing and all(all(k in e for k in required) for e in f0["negatives"]),
          ",".join(missing))
    nsum = f0["negative_summary"]
    check("s2 negative_summary fields present (F: both declared values reported)",
          nsum["declared_expectations_enforced"] is True
          and nsum["declared_expectations_in_cases_json"] == ["ModelRegistryError", "ValueError"]
          and "exact exception type name" in nsum["declared_expectation_comparison"])
    check("s2 negative_summary on the green control (E: one declared value only)",
          out("E", "M09")["negative_summary"]["declared_expectations_in_cases_json"]
          == ["ModelRegistryError"])
    check("s2 negative_summary on G (missing declaration surfaces as None)",
          out("G", "M09")["negative_summary"]["declared_expectations_in_cases_json"]
          == ["ModelRegistryError", "None"])
    sem = f0["exit_code_semantics"]
    check("s2 exit_code_semantics additions present",
          sem["cases_json_declared_expectations_usable"] is True
          and sem["declared_expectation_mismatch_case_ids"] == ["NEG-CARD"]
          and "SUBSET of declared_expectation_mismatch" in sem["reason_namespace"])

    print()
    print("checks failed:", len(fails), fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
