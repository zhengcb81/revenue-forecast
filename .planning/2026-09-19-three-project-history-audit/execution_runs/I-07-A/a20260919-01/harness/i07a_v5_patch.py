"""I-07-A: fold the V5 no-production-mutation witness into state_matrix.json.

Kept as its own tiny step because the matrix is re-derived (and therefore loses the
V5 block) whenever i07a_matrix.py runs.  Read-only with respect to production.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    att = Path(sys.argv[1])
    b = json.loads((att / "before" / "snapshot.json").read_text(encoding="utf-8"))
    a = json.loads((att / "after" / "snapshot.json").read_text(encoding="utf-8"))
    m = json.loads((att / "after" / "state_matrix.json").read_text(encoding="utf-8"))

    catalog_ok = (b["catalog"]["bytes"], b["catalog"]["mtime_iso"]) == \
                 (a["catalog"]["bytes"], a["catalog"]["mtime_iso"])
    anchors = {k: b["anchors_sha256"][k] == a["anchors_sha256"][k]
               for k in b["anchors_sha256"]}
    heads = {k: b["repos"][k]["head"] == a["repos"][k]["head"] for k in b["repos"]}
    porc = b["porcelain_product_only"] == a["porcelain_product_only"]

    detail = {
        "catalog_bytes_before": b["catalog"]["bytes"],
        "catalog_mtime_before": b["catalog"]["mtime_iso"],
        "catalog_bytes_after": a["catalog"]["bytes"],
        "catalog_mtime_after": a["catalog"]["mtime_iso"],
        "catalog_identity_unchanged": catalog_ok,
        "catalog_read_only_observation": True,
        "catalog_read_only_basis": "SQLite mode=ro URI + PRAGMA query_only=ON "
                                   "(the product's own read-only path, CW/store.py:551,556)",
        "catalog_quick_check": "NOT RUN BY DESIGN: a full-file scan on a 49.7 GB catalog is out "
                               "of scope for this card",
        "wal_bytes_before": b["catalog"]["wal_bytes"],
        "wal_bytes_after": a["catalog"]["wal_bytes"],
        "anchors_unchanged": anchors,
        "heads_unchanged": heads,
        "porcelain_product_only_unchanged": porc,
        "porcelain_product_only": a["porcelain_product_only"],
        "porcelain_whole_tree": a["porcelain"],
        "slo_probe_blob_at_head": a["slo_probe_git"]["blob_at_head"],
        "slo_probe_blob_worktree": a["slo_probe_git"]["blob_of_worktree"],
    }
    m["v_checks"]["V5_no_production_mutation"] = {
        "pass": bool(catalog_ok and all(anchors.values()) and all(heads.values()) and porc),
        "detail": detail,
    }
    (att / "after" / "state_matrix.json").write_text(
        json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (att / "after" / "v5_integrity.json").write_text(
        json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"V5_pass": m["v_checks"]["V5_no_production_mutation"]["pass"],
                      "counts": m["counts"],
                      "catalog_identity_unchanged": catalog_ok,
                      "anchors_all_unchanged": all(anchors.values()),
                      "porcelain_product_only_unchanged": porc},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
