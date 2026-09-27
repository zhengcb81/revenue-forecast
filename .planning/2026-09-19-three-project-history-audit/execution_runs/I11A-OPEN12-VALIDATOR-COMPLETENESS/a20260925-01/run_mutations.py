"""I11A-OPEN12-VALIDATOR-COMPLETENESS — mutation runs (oracle §4, M1..M10).

Operator = delete exactly one marker-delimited OPEN12 guard block from the PATCHED
validator (equivalent to weakening the validator back to its pre-patch behaviour for
that rule), then re-run the frozen cases.

Expectation (oracle §4 / J2): the guard's own target case(s) flip back to ACCEPTED,
every other case stays rejected, the positive case still passes and the validator's
own 21-case suite still shows 21/21. rc=0 means that expectation held.
"""

from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys

MUTATIONS = [
    ("M1", "G1", ["CE-01"]),
    ("M2", "G2", ["CE-02", "CE-03", "REPRO-8"]),
    ("M3", "G3", ["CE-04"]),
    ("M4", "G4", ["CE-05"]),
    ("M5", "G5", ["CE-06"]),
    ("M6", "G6", ["CE-07"]),
    ("M7", "G7", ["CE-08"]),
    ("M8", "G8", ["CE-09"]),
    ("M9", "G9", ["CE-10"]),
    ("M10", "G10", ["CE-11"]),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    patched = os.path.join(here, "iso_patched", "tools", "validate_hypotheses.py")
    attempt = os.path.join(here, "iso_patched")
    runner = os.path.join(here, "run_cases.py")
    base_text = io.open(patched, encoding="utf-8", newline="").read()

    summary = []
    for mut_id, guard, targets in MUTATIONS:
        pattern = re.compile(r"[ \t]*# <OPEN12-%s>.*?# </OPEN12-%s>\n" % (guard, guard),
                             re.S)
        text, n = pattern.subn("", base_text)
        if n != 1:
            raise SystemExit("%s: removed %d blocks (expected 1)" % (mut_id, n))
        out_dir = os.path.join(here, "mut", mut_id)
        os.makedirs(out_dir, exist_ok=True)
        vpath = os.path.join(out_dir, "validate_hypotheses.py")
        with io.open(vpath, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        out_json = os.path.join(out_dir, "cases_mutation.json")
        cmd = [sys.executable, "-X", "utf8", "-B", runner, vpath, attempt, out_json,
               "mut"] + targets
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        rep = json.load(io.open(out_json, encoding="utf-8")) if os.path.exists(out_json) else {}
        row = {
            "mutation": mut_id,
            "deleted_guard": "OPEN12-" + guard,
            "deleted_bytes": len(base_text.encode("utf-8")) - len(text.encode("utf-8")),
            "targets": targets,
            "rc": p.returncode,
            "phase_expectation_met": rep.get("phase_expectation_met"),
            "positive": rep.get("positive", {}).get("verdict"),
            "own_suite": rep.get("own_suite"),
            "target_rows": [{"id": r["id"], "rejected": r["rejected"],
                             "codes": r["observed_codes"]}
                            for r in (rep.get("ce", []) + rep.get("repro", []))
                            if r["id"] in targets],
            "other_ce_accepted": [r["id"] for r in rep.get("ce", [])
                                  if not r["rejected"] and r["id"] not in targets],
            "stderr_tail": (p.stderr or "")[-400:],
        }
        summary.append(row)
        print("%-4s %-9s rc=%d met=%s targets_flipped=%s others_leaked=%s"
              % (mut_id, "OPEN12-" + guard, p.returncode, row["phase_expectation_met"],
                 [t["id"] + ":" + str(not t["rejected"]) for t in row["target_rows"]],
                 row["other_ce_accepted"]))

    out = os.path.join(here, "mut", "mutation_results.json")
    with io.open(out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    ok = all(r["rc"] == 0 and r["phase_expectation_met"] for r in summary)
    print("mutations %d/%d met the frozen expectation -> %s"
          % (sum(1 for r in summary if r["rc"] == 0), len(summary), out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
