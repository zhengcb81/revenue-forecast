"""I08CR-c10 — AX-5 (AUDIT-DESIGN D1b): fs-scan for the never-produced evidence file
`before/production_anchors.txt` (plan tree + RF repo, .git excluded). Read-only."""
from __future__ import annotations

import json
import os
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
PLAN = ATT.parents[2]
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")


def scan(root: Path, name: str):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        for fn in filenames:
            if fn == name:
                hits.append(str(Path(dirpath) / fn))
    return hits


def main() -> int:
    out = {
        "production_anchors_txt_in_plan_tree": scan(PLAN, "production_anchors.txt"),
        "production_anchors_txt_in_rf_repo": scan(RF, "production_anchors.txt"),
        "production_anchors_json_in_plan_tree": scan(PLAN, "production_anchors.json"),
    }
    cmd = (PLAN / "execution_runs" / "B1-I08C-product-fixes" / "a20260921-01" / "commands.json")
    txt = cmd.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()
    out["b1_commands_json_evidence_entry_lines"] = [
        {"line": i, "text": line.strip()}
        for i, line in enumerate(lines, 1)
        if "production_anchors" in line
    ]
    ok = (
        not out["production_anchors_txt_in_plan_tree"]
        and not out["production_anchors_txt_in_rf_repo"]
        and len(out["production_anchors_json_in_plan_tree"]) >= 1
    )
    out["interpretation"] = (
        "AUDIT-DESIGN D1b confirmed by fresh fs-scan: the evidence entry "
        "`before/production_anchors.txt` was registered but the file was never produced "
        "(only the .json sibling exists). Disposition (append-only erratum in THIS attempt, "
        "AUDIT-DESIGN addendum A4): record the entry as 'never produced (only .json)'; "
        "the file is NOT fabricated after the fact."
    )
    out["all_ok"] = ok
    (EVID / "AX5_d1b_fsscan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("AX5_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
