#!/usr/bin/env python3
"""I-10-B compatibility impact — BEFORE/AFTER differential.

BEFORE = the production anchor snapshot, which is the pre-fix state.
         (I-10-B is not yet ratified, so the product file still holds the
          un-fixed registry. Both files are copied into attempt-local
          scratch and imported under distinct module names. No product file
          is executed in place and nothing is written outside this run dir.)
AFTER  = the attempt-local isolated copy carrying both card fixes.

The differential enumerates every (model, driver) bound cell under BOTH
registries and reports only the cells whose (lo, hi) pair actually changed.
This is deliberately NOT a test of "which cells end at -inf": a large number
of cells already sat at -inf before the fix (other_revenue, bank_revenue
.asset_yield, ...), and conflating those with the change set would both
overstate the blast radius and hide the real one.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
ISO = RUN / "iso" / "rf" / "scripts"
SCRATCH = RUN / "_scratch_import"
PROD_SCRIPTS = pathlib.Path("C:/Users/郑曾波/Projects/revenue-forecast/scripts")

PROD_ANCHOR = {
    "model_registry.py": (
        26446,
        "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    ),
    "model_extensions.py": (
        14475,
        "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
    ),
}


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def cells(reg):
    out = {}
    for model_id, spec in reg.MODEL_REGISTRY.items():
        for driver in list(spec.required) + list(spec.optional):
            lo, hi = reg.driver_value_bounds(model_id, driver)
            out[(model_id, driver)] = {
                "lo": lo,
                "hi": hi,
                "declared": "required" if driver in spec.required else "optional",
                "has_default": driver in spec.defaults,
            }
    return out


def show(v):
    lo, hi = v["lo"], v["hi"]
    return (
        "-inf" if lo == float("-inf") else repr(lo),
        "inf" if hi == float("inf") else repr(hi),
    )


def main() -> int:
    report: dict = {}

    # ---- verify production anchor BEFORE copying anything ----
    prod_check = {}
    for name, (nbytes, want) in PROD_ANCHOR.items():
        p = PROD_SCRIPTS / name
        got_bytes, got_sha = p.stat().st_size, sha(p)
        prod_check[name] = {
            "bytes": got_bytes,
            "sha256": got_sha,
            "expected_bytes": nbytes,
            "expected_sha256": want,
            "match": got_bytes == nbytes and got_sha == want,
        }
    report["production_anchor_check"] = prod_check
    if not all(v["match"] for v in prod_check.values()):
        print(json.dumps(report, indent=1, ensure_ascii=False))
        raise SystemExit("PRODUCTION ANCHOR DRIFT — aborting")

    # ---- stage both variants under distinct package-free module names ----
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    for variant, src in (
        ("before", PROD_SCRIPTS),
        ("after", ISO),
    ):
        d = SCRATCH / variant
        d.mkdir(parents=True)
        for name in ("model_registry.py", "model_extensions.py"):
            shutil.copy2(src / name, d / name)

    report["variants"] = {
        v: {
            name: {
                "bytes": (SCRATCH / v / name).stat().st_size,
                "sha256": sha(SCRATCH / v / name),
            }
            for name in ("model_registry.py", "model_extensions.py")
        }
        for v in ("before", "after")
    }

    sys.path.insert(0, str(SCRATCH / "before"))
    sys.path.insert(0, str(SCRATCH / "after"))
    mb = load("reg_before", SCRATCH / "before" / "model_registry.py")
    ma = load("reg_after", SCRATCH / "after" / "model_registry.py")

    cb, ca = cells(mb), cells(ma)
    report["model_count_before"] = len(mb.MODEL_REGISTRY)
    report["model_count_after"] = len(ma.MODEL_REGISTRY)
    report["cell_count_before"] = len(cb)
    report["cell_count_after"] = len(ca)
    report["cell_keys_identical"] = set(cb) == set(ca)

    diffs = []
    for key in sorted(set(cb) & set(ca), key=lambda k: (k[0], k[1])):
        blo, bhi = show(cb[key])
        alo, ahi = show(ca[key])
        if (blo, bhi) != (alo, ahi):
            diffs.append({
                "model": key[0],
                "driver": key[1],
                "declared": cb[key]["declared"],
                "has_default": cb[key]["has_default"],
                "before_lo": blo,
                "before_hi": bhi,
                "after_lo": alo,
                "after_hi": ahi,
                "lower_bound_widened": blo != alo,
                "upper_bound_widened": bhi != ahi,
                "direction": "[-inf,+inf)" if (alo == "-inf" and ahi == "inf") else "other",
            })

    report["changed_cell_count"] = len(diffs)
    report["changed_cells"] = diffs

    # unchanged-cell population, for the "25 drivers each individually" clause
    unchanged = sorted(
        {k[1] for k in set(cb) & set(ca)} - {d["driver"] for d in diffs}
    )
    report["drivers_unchanged"] = unchanged
    report["driver_count_unchanged"] = len(unchanged)

    (RUN / "compatibility_cells.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
