"""Attribution arithmetic for the FC-1204 coverage ratchet's 3 red rows.

Read-only: reads the two judged CI-equivalent coverage JSON archives (BEFORE-B /
AFTER-B) and the pristine-CW / split-iso copies of the three modules; prints
  (a) per-module raw summaries for both arms (same numbers the gate test prints),
  (b) static statement/arc counts (coverage's own parser) for pristine vs split,
  (c) an UPPER BOUND on what the pristine module could have measured, which is
      metric_pristine <= C_split / T_pristine  because pure code motion cannot
      remove an executed unit from the split file (split adds wrapper units).
If that upper bound is below floor-0.5, the split cannot be the cause.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from coverage.parser import PythonParser

SCRATCH = Path(r"C:\Users\郑曾波\AppData\Local\Temp\cwgu2\scratch")
ISO = Path(r"C:\Users\郑曾波\AppData\Local\Temp\cwgu2\repo")
CWGU3 = Path(r"C:\Users\郑曾波\AppData\Local\Temp\cwgu3\repo")
PREFIX = "src/company_wiki/source_catalog/"
MODS = [
    "observability.py",
    "prompt_injection.py",
    "prune_retired_evidence.py",
    "archive_retired_evidence.py",
]
FLOORS = {"observability.py": 91, "prompt_injection.py": 73,
          "prune_retired_evidence.py": 87, "archive_retired_evidence.py": 95}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def entry(data: dict, rel: str) -> dict | None:
    target = PREFIX + rel
    for key, val in data.get("files", {}).items():
        if key.replace("\\", "/") == target:
            return val
    return None


def summary(entry: dict) -> dict:
    s = entry["summary"]
    num = s.get("num_statements", 0)
    cov = s.get("covered_lines", 0)
    tot = s.get("num_branches", 0)
    covb = s.get("covered_branches", 0)
    return {
        "num_statements": num, "covered_lines": cov,
        "num_branches": tot, "covered_branches": covb,
        "combined": cov + covb, "total": num + tot,
        "pct": round(100.0 * (cov + covb) / (num + tot), 1) if (num + tot) else 0.0,
        "missing_lines": entry.get("missing_lines", []),
        "missing_branches": entry.get("missing_branches", []),
    }


def static(path: Path) -> tuple[int, int]:
    """(num_statements, num_branches) computed statically, coverage's own rules.

    statements = PythonParser.statements; num_branches = number of arcs leaving
    lines that have more than one exit  (= sum of exit_counts > 1), which is the
    quantity coverage writes into coverage.json's summary.num_branches.
    """
    parser = PythonParser(text=path.read_text(encoding="utf-8"), filename=str(path))
    parser.parse_source()
    stmts = len(parser.statements)
    branches = sum(c for c in parser.exit_counts().values() if c > 1)
    return stmts, branches


def main() -> None:
    before_p = SCRATCH / "cov_beforeB.json"
    after_p = SCRATCH / "cov_afterB.json"
    print("=== data files ===")
    print(f"cov_beforeB.json sha256 {sha(before_p)}  bytes {before_p.stat().st_size}")
    print(f"cov_afterB.json  sha256 {sha(after_p)}  bytes {after_p.stat().st_size}")
    before, after = load(before_p), load(after_p)

    print("\n=== (a) per-module raw summaries, both CI-equivalent arms ===")
    print("module | arm | stmts | cov_lines | branches | cov_branches | combined/total | pct | missing_lines | missing_branches")
    for mod in MODS:
        for arm, data in (("BEFORE-B", before), ("AFTER-B", after)):
            e = entry(data, mod)
            if e is None:
                print(f"{mod} | {arm} | NOT MEASURED")
                continue
            s = summary(e)
            print(f"{mod} | {arm} | {s['num_statements']} | {s['covered_lines']} | "
                  f"{s['num_branches']} | {s['covered_branches']} | "
                  f"{s['combined']}/{s['total']} | {s['pct']} | "
                  f"{len(s['missing_lines'])} | {len(s['missing_branches'])}")

    print("\n=== (b) static counts (coverage 7.12 PythonParser) pristine(CW) vs split(iso) ===")
    print("module | pristine stmts/branches | split stmts/branches | json(afterB) stmts/branches | parser==json?")
    for mod in MODS:
        pristine = CWGU3 / PREFIX.replace("/", "\\") / mod
        split = ISO / PREFIX.replace("/", "\\") / mod
        ps, pa = static(pristine)
        ss, sa = static(split)
        je = entry(after, mod)
        js = summary(je)["num_statements"] if je else -1
        jb = summary(je)["num_branches"] if je else -1
        print(f"{mod} | {ps}/{pa} | {ss}/{sa} | {js}/{jb} | stmts {ss == js} arcs {sa == jb}")
        print(f"    pristine sha {sha(pristine)}")
        print(f"    split    sha {sha(split)}")

    print("\n=== (c) upper bound: could the SPLIT alone explain the shortfall? ===")
    print("bound: metric_pristine <= C_split / T_pristine  (code motion cannot drop executed units)")
    print("module | floor | measured(AFTER-B) | T_split | C_split | T_pristine | upper bound % | bound < floor-0.5 ?")
    for mod in MODS:
        je = entry(after, mod)
        if je is None:
            continue
        s = summary(je)
        pristine = CWGU3 / PREFIX.replace("/", "\\") / mod
        ps, pa = static(pristine)
        T_pristine = ps + pa
        C_split = s["combined"]
        upper = 100.0 * C_split / T_pristine if T_pristine else 0.0
        floor = FLOORS[mod]
        verdict = "YES -> split cannot be the cause" if upper < floor - 0.5 else "NO -> inconclusive"
        print(f"{mod} | {floor} | {s['pct']} | {s['total']} | {C_split} | {T_pristine} | "
              f"{upper:.1f} | {verdict}")


if __name__ == "__main__":
    main()
