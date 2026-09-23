"""I-07-C changes.diff producer (no git): proves the delta of this card is
isolated config/root/catalog only and that every product anchor is byte-still.

Writes <attempt>/changes.diff.
"""
from __future__ import annotations

import difflib
import sys
from pathlib import Path

from i07c_common import (ATT, CASES, CELLS, CW, EVID, PROD_CONFIG, read_json,
                         sha256_file)

OUT = ATT / "changes.diff"


def main() -> int:
    before = read_json(EVID / "snapshot_before.json")
    after = read_json(EVID / "snapshot_after.json")
    anchors_changed = sorted(
        k for k in set(before["anchors"]) | set(after["anchors"])
        if before["anchors"].get(k) != after["anchors"].get(k))
    samples_changed = sorted(
        k for k in set(before["samples"]) | set(after["samples"])
        if before["samples"].get(k) != after["samples"].get(k))

    lines = ["# I-07-C changes.diff (difflib-based; no git)",
             "# product anchors (RF/CW/FF source + production config):",
             f"#   before={len(before['anchors'])} after={len(after['anchors'])} "
             f"changed={anchors_changed}",
             f"# manifest samples (raw+sidecar): changed={samples_changed}",
             f"# production catalog identity changed="
             f"{before['production_catalog'] != after['production_catalog']}",
             "# isolation-only writes follow (config deltas vs production config)",
             ""]
    prod_cfg = PROD_CONFIG.read_text(encoding="utf-8").splitlines(keepends=True)
    any_cell = False
    for cell in CELLS:
        cfg = CASES / cell / "cwroot" / "config" / "source_catalog.yaml"
        if not cfg.is_file():
            lines.append(f"# {cell}: NO CONFIG (not built - expected only for blocked cells)")
            continue
        any_cell = True
        cell_lines = cfg.read_text(encoding="utf-8").splitlines(keepends=True)
        diff = difflib.unified_diff(
            prod_cfg, cell_lines,
            fromfile="production/config/source_catalog.yaml (read-only reference)",
            tofile=f"%TEMP%/i07c/cells/{cell}/cwroot/config/source_catalog.yaml (ISOLATED)",
        )
        lines.append(f"--- cell {cell} (isolated root/config/catalog only) ---")
        lines.extend(diff)
        lines.append("")
    if not any_cell:
        lines.append("# WARNING: no isolated configs found")
    lines.append("# trees written: %TEMP%\\i07c\\cells\\<cell>\\** + this attempt dir")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written {OUT} anchors_changed={anchors_changed} "
          f"samples_changed={samples_changed} sha256={sha256_file(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
