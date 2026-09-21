#!/usr/bin/env python3
"""I-10-B seq 11 — anchor + artifact hash recheck (card point 6: recompute EVERY attempt resume).

Recomputes:
  * production anchors  scripts/model_registry.py / scripts/model_extensions.py
  * every artifact/script hash recorded in binding.json
  * the isolated copies under iso/rf/scripts/ and _scratch_import/before/

Read-only. Writes nothing.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

PLAN = pathlib.Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit")
ATT = PLAN / "execution_runs" / "I-10-B" / "a20260919-01"
PROD = pathlib.Path(r"C:\Users\郑曾波\Projects\revenue-forecast\scripts")

PROD_ANCHOR = {
    "model_registry.py": (26446, "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"),
    "model_extensions.py": (14475, "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"),
}


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    out: dict = {"recheck": "seq11-anchor-and-artifact-hashes"}

    prod = {}
    drift = False
    for name, (wb, wh) in PROD_ANCHOR.items():
        p = PROD / name
        b, h = p.stat().st_size, sha(p)
        ok = b == wb and h == wh
        drift = drift or not ok
        prod[name] = {"bytes": b, "sha256": h, "match": ok}
    out["production_anchors"] = prod
    out["production_anchor_drift"] = drift

    binding = json.loads((ATT / "binding.json").read_text(encoding="utf-8"))
    recs: dict = {}
    recs.update(binding.get("artifacts", {}))
    recs.update(binding.get("scripts", {}))
    arts = {}
    for rel, meta in recs.items():
        p = ATT / rel
        if not p.exists():
            arts[rel] = {"missing": True}
            drift = True
            continue
        b, h = p.stat().st_size, sha(p)
        ok = b == meta["bytes"] and h == meta["sha256"]
        drift = drift or not ok
        arts[rel] = {"bytes": b, "sha256": h, "match": ok}
    out["binding_recorded_artifacts"] = arts

    iso = binding["isolation"]
    iso_checks = {}
    for rel, meta in (
        ("iso/rf/scripts/model_registry.py", iso["iso_model_registry.py"]),
        ("iso/rf/scripts/model_extensions.py", iso["iso_model_extensions.py"]),
    ):
        p = ATT / rel
        b, h = p.stat().st_size, sha(p)
        ok = b == meta["bytes"] and h == meta["sha256"]
        drift = drift or not ok
        iso_checks[rel] = {"bytes": b, "sha256": h, "match": ok}
    p = ATT / "_scratch_import/before/model_registry.py"
    b, h = p.stat().st_size, sha(p)
    ok = h == PROD_ANCHOR["model_registry.py"][1]
    drift = drift or not ok
    iso_checks["_scratch_import/before/model_registry.py"] = {"bytes": b, "sha256": h, "match": ok}
    out["isolated_copies"] = iso_checks
    out["all_match"] = not drift

    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
