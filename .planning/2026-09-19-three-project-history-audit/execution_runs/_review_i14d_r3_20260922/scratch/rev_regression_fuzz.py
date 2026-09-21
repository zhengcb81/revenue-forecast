"""Differential regression fuzz: is there ANY input the base tree redacts and r3 does not?

The strongest form of the r2 BLOCKER criterion was "a persistence regression relative to
the card's starting tree".  This enumerates a cross product of header shapes and asks,
for each tree, whether a credential survives.  Anything leaking on r3 but not on base is
a regression; anything leaking on r3 but not on r2 is a regression against the revision
under review's own predecessor.

Each tree is imported in its OWN subprocess (--one), so no module state is shared.

  python rev_regression_fuzz.py --run     # all trees, then compare
  python rev_regression_fuzz.py --one <tree> <out.json>
"""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
HERE = Path(__file__).resolve().parent
PY = str(ATT / "iso/venv/Scripts/python.exe")
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

PREFIX = ["Authorization: ", "authorization:", "Authorization:Bearer", "Bearer ",
          "bearer\t", "proxy-authorization: ", "authorization = ", "token=", "password: ",
          "Authorization: Bearer "]
SCHEME = ["", "Bearer", "Negotiate", "AWS4-HMAC-SHA256", "SCRAM-SHA-256", "Hawk", "Bot",
          "Zzz", "2foo", "a|b", "A"]
SEP = ["", " ", "\t", "\n", "\r\n", "\n  ", "\n\n", " \n", "\n\t", "\n\r\n"]
VALUE = [S39, M, '"' + S39 + '"', "'" + S39 + "'", S39 + "?x", '"' + S39 + '?x"',
         '"' + S39 + 'x"', "abc " + S39, S39 + "|x", S39 + ";x", "x" + S39,
         '"' + S39 + ' x"', S39 + " x"]
SUFFIX = ["", "\ndoc=17", "\nstage=summarize", " doc=17", "\n  doc=17", "\ndoc=17\nstage=x"]
TREES = ("product_base", "product_narrow", "product_narrow_r3")


def build_inputs():
    return [p + s + sep + v + suf for p in PREFIX for s in SCHEME for sep in SEP
            for v in VALUE for suf in SUFFIX]


def one(tree: str, out: Path) -> int:
    sys.path.insert(0, str((ATT / "iso" / tree / "src").resolve()))
    ob = importlib.import_module("company_wiki.source_catalog.observability")
    fn = ob.redact_text
    leaks = [i for i, t in enumerate(build_inputs())
             if (S39 in fn(t)) or (M in fn(t))]
    out.write_text(json.dumps({"tree": tree, "leaks": leaks}), encoding="utf-8")
    print(tree, "leaking", len(leaks))
    return 0


def run() -> int:
    inputs = build_inputs()
    leak = {}
    for t in TREES:
        p = HERE / ("fuzz_%s.json" % t)
        r = subprocess.run([PY, "-B", str(Path(__file__).resolve()), "--one", t, str(p)],
                           capture_output=True, text=True,
                           env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""})
        if r.returncode != 0:
            print(r.stdout, r.stderr)
            return 1
        leak[t] = set(json.loads(p.read_text(encoding="utf-8"))["leaks"])
    base, r2, r3 = leak["product_base"], leak["product_narrow"], leak["product_narrow_r3"]
    reg_base = sorted(r3 - base)
    reg_r2 = sorted(r3 - r2)
    report = {
        "inputs": len(inputs),
        "leaking_counts": {t: len(v) for t, v in leak.items()},
        "r3_regressions_vs_base_count": len(reg_base),
        "r3_regressions_vs_base_examples": [inputs[i] for i in reg_base[:12]],
        "r3_regressions_vs_r2_count": len(reg_r2),
        "r3_regressions_vs_r2_examples": [inputs[i] for i in reg_r2[:12]],
        "r3_fixed_vs_base_count": len(base - r3),
        "r3_fixed_vs_base_examples": [inputs[i] for i in sorted(base - r3)[:6]],
        "r3_still_leaking_examples": [inputs[i] for i in sorted(r3)[:12]],
    }
    (HERE / "regression_fuzz.json").write_text(json.dumps(report, indent=1, ensure_ascii=False),
                                               encoding="utf-8")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--one")
    ap.add_argument("out", nargs="?")
    a = ap.parse_args()
    if a.one:
        return one(a.one, Path(a.out))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
