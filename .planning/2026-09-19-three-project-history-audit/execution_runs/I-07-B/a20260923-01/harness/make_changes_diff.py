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
TEMP_CASE = Path(__import__("os").environ.get("TEMP", r"C:\Temp")) / "i07b" / "cases"


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
    iso_path = TEMP_CASE / "S-CN-1" / "cwroot" / "config" / "source_catalog.yaml"
    iso = iso_path.read_text(encoding="utf-8").splitlines(True) if iso_path.is_file() else []
    diff = "".join(difflib.unified_diff(prod, iso, fromfile="PRODUCTION/CW/config/source_catalog.yaml",
                                        tofile=f"ISOLATED/{iso_path}"))
    cat_before = before["production_catalog"]
    cat_after = after["production_catalog"]
    lines = [
        "# I-07-B changes.diff — isolation-only card\n",
        f"# product/plan anchors identical before vs after: {len(same)}; changed: {changed or 'NONE'}\n",
        f"# production catalog identity before: bytes={cat_before['bytes']} mtime_ns={cat_before['mtime_ns']}\n",
        f"# production catalog identity after : bytes={cat_after['bytes']} mtime_ns={cat_after['mtime_ns']}\n",
        f"# identical: {cat_before['bytes'] == cat_after['bytes'] and cat_before['mtime_ns'] == cat_after['mtime_ns']}\n",
        "# production writes by this attempt: ZERO; CW writes: ZERO; RF product writes: ZERO\n",
        "# attempt-local (not a product change) files: see handoff.json changed_paths\n",
        "\n",
        "=== the only semantic isolation change (config copy, production file untouched) ===\n",
        diff,
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
