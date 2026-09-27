"""I-07-D isolation scaffolding: create the adapter project_root/config_root
directories the acquisition config declares (acquisition_config._path +
adapter __init__ resolve(strict=True) — code evidence in decision.md J7).
Directories only; no files are fabricated, the provider itself is still the
frozen simulation or a real adapter. Records evidence/adapter_scaffolding.json.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CASES = Path(os.environ.get("TEMP", r"C:\Temp")) / "i07d" / "cases"

NEEDED = {
    "cn": ["StockInfoDLSimple/v2-clean-rewrite",
           "dayu-agent/dayu-agent", "dayu-agent/workspace/config"],
    "hk": ["dayu-agent/dayu-agent", "dayu-agent/workspace/config",
           "StockInfoDLSimple/v2-clean-rewrite"],
    "us": ["dayu-agent/dayu-agent", "dayu-agent/workspace/config",
           "StockInfoDLSimple/v2-clean-rewrite"],
}


F_MARKET = {"F01": "cn", "F02": "hk", "F03": "hk", "F04": "hk", "F05": "cn"}


def _market_of(name: str) -> str | None:
    if name in F_MARKET:
        return F_MARKET[name]
    parts = name.split("-")
    if len(parts) > 1:
        return {"CN": "cn", "HK": "hk", "US": "us"}.get(parts[1])
    return None


def main() -> int:
    made = {}
    for case in sorted(p for p in CASES.iterdir() if p.is_dir()):
        market = _market_of(case.name)
        if market is None:
            continue
        rec = []
        for rel in NEEDED[market]:
            d = case / Path(rel)
            d.mkdir(parents=True, exist_ok=True)
            rec.append({"path": str(d), "created": d.is_dir(), "files": len(list(d.iterdir()))})
        # preserve any pre-scaffold run evidence before a re-run overwrites it
        preserved = []
        for sub in ("run2", "run3"):
            src = ATT / "evidence" / "cases" / case.name / sub
            if src.is_dir():
                n = 1
                dst = ATT / "evidence" / "cases" / case.name / f"{sub}.pre_scaffold"
                while dst.exists():
                    n += 1
                    dst = ATT / "evidence" / "cases" / case.name / f"{sub}.pre_scaffold{n}"
                shutil.move(str(src), str(dst))
                preserved.append(dst.name)
        made[case.name] = {"dirs": rec, "preserved_run_dirs": preserved}
    out = ATT / "evidence" / "adapter_scaffolding.json"
    out.write_text(json.dumps({"created": made,
                               "note": "empty declared adapter project roots only; "
                                       "no fabricated executables; provider still "
                                       "frozen-sim or real"},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"written": str(out), "cases": len(made)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
