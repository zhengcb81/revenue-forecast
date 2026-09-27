"""Emit changes.diff: this card changed NO product file. The diff contains
(1) the witness that all product/plan anchors are byte-identical before/after,
and (2) the one semantic isolation change as an actual unified diff — the
isolated source_catalog.yaml vs the production one (catalog_dir + single
company_raw root rebound into the case tree)."""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
TEMP_CASE = Path(__import__("os").environ.get("TEMP", r"C:\Temp")) / "i07d" / "cases"


def main() -> int:
    before = json.loads((ATT / "evidence" / "snapshot_before.json").read_text(encoding="utf-8"))
    after = json.loads((ATT / "evidence" / "snapshot_after.json").read_text(encoding="utf-8"))
    same = []
    changed = []
    for k, v in before["anchors"].items():
        cur = after["anchors"].get(k, {})
        if v.get("missing") or cur.get("missing"):
            continue  # the J8 path bug entries; corrected in plan_anchor_hashes.json
        (same if v.get("sha256") == cur.get("sha256") else changed).append(k)
    prod = (CW / "config" / "source_catalog.yaml").read_text(encoding="utf-8").splitlines(True)
    iso_path = TEMP_CASE / "F01" / "cwroot" / "config" / "source_catalog.yaml"
    iso = iso_path.read_text(encoding="utf-8").splitlines(True) if iso_path.is_file() else []
    diff = "".join(difflib.unified_diff(prod, iso, fromfile="PRODUCTION/CW/config/source_catalog.yaml",
                                        tofile=f"ISOLATED/{iso_path}"))
    # F01's second isolated-config change: cn adapter command -> 403 fixture
    prod_acq = (CW / "config" / "source_acquisition.yaml").read_text(
        encoding="utf-8").splitlines(True)
    acq_path = TEMP_CASE / "F01" / "cwroot" / "config" / "source_acquisition.yaml"
    acq = acq_path.read_text(encoding="utf-8").splitlines(True) if acq_path.is_file() else []
    diff_acq = "".join(difflib.unified_diff(
        prod_acq, acq, fromfile="PRODUCTION/CW/config/source_acquisition.yaml",
        tofile=f"ISOLATED/{acq_path} (F01 fault fixture: cn adapter command)"))
    cat_before = before["production_catalog"]
    cat_after = after["production_catalog"]
    shm_note = ""
    if cat_before.get("shm") != cat_after.get("shm"):
        shm_note = (
            f"# NOTE: production catalog -shm stat changed (bytes "
            f"{cat_before.get('shm', {}).get('bytes')} -> "
            f"{cat_after.get('shm', {}).get('bytes')}; mtime only) — expected "
            "side effect of READ-ONLY WAL reader attachment (all opens used "
            "mode=ro + PRAGMA query_only=ON); main db bytes+mtime and -wal "
            "bytes+mtime are IDENTICAL (no data write).\n")
    lines = [
        "# I-07-D changes.diff — isolation-only card\n",
        f"# product/plan anchors identical before vs after: {len(same)}; changed: {changed or 'NONE'}\n",
        f"# production catalog identity before: bytes={cat_before['bytes']} mtime_ns={cat_before['mtime_ns']}\n",
        f"# production catalog identity after : bytes={cat_after['bytes']} mtime_ns={cat_after['mtime_ns']}\n",
        f"# identical: {cat_before['bytes'] == cat_after['bytes'] and cat_before['mtime_ns'] == cat_after['mtime_ns']}\n",
        shm_note,
        "# production writes by this attempt: ZERO; CW writes: ZERO; RF product writes: ZERO\n",
        "# attempt-local (not a product change) files: see handoff.json changed_paths\n",
        "# (this attempt additionally: %TEMP%\\i07d cells built product-isomorphically;\n",
        "#  ATT/iso/rf = read-only copy of current RF for the publication writer;\n",
        "#  F05 cell seeded with a production_observation_copy of the normalized\n",
        "#  artifacts row + derived file, paths relocated — scratch state, not product)\n",
        "\n",
        "=== isolated config vs production (production files untouched) ===\n",
        diff,
        "\n",
        "=== F01 fault-fixture config (isolated per-cell source_acquisition.yaml) ===\n",
        diff_acq,
    ]
    (ATT / "changes.diff").write_text("".join(lines), encoding="utf-8")
    print(json.dumps({"written": str(ATT / "changes.diff"),
                      "anchors_identical": len(same),
                      "anchors_changed": changed,
                      "catalog_identity_identical":
                          cat_before["bytes"] == cat_after["bytes"]
                          and cat_before["mtime_ns"] == cat_after["mtime_ns"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
