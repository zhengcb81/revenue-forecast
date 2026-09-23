"""I-07-B anchor-drift diff (difflib; no git). Emits unified diffs between the
I-00-B-era pristine copies (I-06-A iso/rf/scripts) and the current RF scripts."""
from __future__ import annotations

import difflib
import hashlib
import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
OLD = ATT.parents[1] / "I-06-A" / "a20260919-01" / "iso" / "rf" / "scripts"
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast") / "scripts"
PAIRS = ["source_preparation.py", "revenue_forecast.py", "filing_fetch_client.py",
         "company_wiki_source.py"]
I00B = {
    "source_preparation.py": "5ec16eaf0fe480126b680f6e069717ebfc218ae39531372a380cfcc9b91bce46",
    "revenue_forecast.py": "6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    out_dir = ATT / "evidence" / "anchor_drift"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for name in PAIRS:
        old_p, new_p = OLD / name, RF / name
        rec = {"old_path": str(old_p), "new_path": str(new_p),
               "old_sha256": sha(old_p) if old_p.is_file() else None,
               "new_sha256": sha(new_p)}
        if name in I00B:
            rec["i00b_expected_sha256"] = I00B[name]
            rec["drifted"] = rec["old_sha256"] == I00B[name] and rec["new_sha256"] != I00B[name]
        if rec["old_sha256"] != rec["new_sha256"]:
            old_lines = old_p.read_text(encoding="utf-8").splitlines(keepends=True)
            new_lines = new_p.read_text(encoding="utf-8").splitlines(keepends=True)
            diff = "".join(difflib.unified_diff(
                old_lines, new_lines,
                fromfile=f"I-00-B-era:{name}", tofile=f"current:{name}"))
            (out_dir / f"{name}.diff").write_text(diff, encoding="utf-8")
            rec["diff_file"] = str(out_dir / f"{name}.diff")
            rec["diff_lines"] = diff.count("\n")
        report[name] = rec
    (out_dir / "anchor_drift.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: {"drifted": v.get("drifted"),
                          "old": (v["old_sha256"] or "")[:12],
                          "new": (v["new_sha256"] or "")[:12],
                          "diff_lines": v.get("diff_lines", 0)}
                      for k, v in report.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
