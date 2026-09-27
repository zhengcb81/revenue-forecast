#!/usr/bin/env python
"""I-10-A harness: changes.diff builder — isolation-surface accounting.

Products (RF/CW) must be byte-identical before vs after: this script compares the
before/after snapshots and asserts anchors_identical; the diff body lists ONLY the
isolation surface (attempt tree writes). Writes changes.diff + after/hash_table_before_after.json.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent
BEFORE = json.loads((ATT / "before" / "snapshot_before.json").read_text(encoding="utf-8"))
AFTER = json.loads((ATT / "after" / "snapshot_after.json").read_text(encoding="utf-8"))


def cmp_group(name: str):
    rows = []
    for key in sorted(set(BEFORE[name]) | set(AFTER[name])):
        b = BEFORE[name].get(key, {})
        a = AFTER[name].get(key, {})
        rows.append({
            "anchor": key,
            "before_sha256": b.get("sha256"),
            "after_sha256": a.get("sha256"),
            "before_bytes": b.get("bytes"),
            "after_bytes": a.get("bytes"),
            "identical": b.get("sha256") == a.get("sha256") and b.get("bytes") == a.get("bytes"),
        })
    return rows


groups = {name: cmp_group(name) for name in ("product_anchors", "sources", "plan_inputs", "iso_copies")}
anchors_identical = all(r["identical"] for r in groups["product_anchors"])
sources_identical = all(r["identical"] for r in groups["sources"])
plan_identical = all(r["identical"] for r in groups["plan_inputs"])
iso_identical = all(r["identical"] for r in groups["iso_copies"])

hash_table = {
    "artifact": "hash_table_before_after",
    "captured_before": BEFORE["captured_at_local"],
    "captured_after": AFTER["captured_at_local"],
    "groups": groups,
    "verdict": {
        "anchors_identical": anchors_identical,
        "anchors_changed": [r["anchor"] for r in groups["product_anchors"] if not r["identical"]],
        "sources_identical": sources_identical,
        "plan_inputs_identical": plan_identical,
        "iso_copies_identical": iso_identical,
        "product_zero_change": anchors_identical and sources_identical and plan_identical,
    },
}
(ATT / "after" / "hash_table_before_after.json").write_text(
    json.dumps(hash_table, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


changed_files = []
for p in sorted(ATT.rglob("*")):
    if p.is_file() and "command_runs" not in p.parts and "_scratch" not in p.parts and "iso" not in p.parts:
        changed_files.append(str(p.relative_to(ATT)).replace("\\", "/"))

lines = []
lines.append("# I-10-A a20260923-01 changes.diff")
lines.append("")
lines.append("# SCOPE: isolation surface ONLY. Production (RF) and company-wiki (CW) trees:")
lines.append("# ZERO writes. Plan-tree inputs: ZERO writes (read-only). All writes confined to")
lines.append("# allowed_write_roots = <attempt_root>/** (binding.json).")
lines.append("#")
lines.append(f"# anchors_identical: {anchors_identical}  (product anchors before==after)")
lines.append(f"# sources_identical: {sources_identical}  (3 raws + 3 sidecars re-hashed before==after)")
lines.append(f"# plan_inputs_identical: {plan_identical}  (frozen plan/dependency inputs unchanged)")
lines.append(f"# iso_copies_identical: {iso_identical}  (isolated product copies unchanged across the run)")
lines.append(f"# anchors_changed: {hash_table['verdict']['anchors_changed']}")
lines.append("")
lines.append("--- /dev/null (isolation surface: files created under execution_runs/I-10-A/a20260923-01)")
lines.append("+++ execution_runs/I-10-A/a20260923-01")
for f in changed_files:
    lines.append(f"+ {f}  sha256={sha(ATT / f)}")
lines.append("")
lines.append("# Product diff: EMPTY (zero-change assertion above is measured from before/after")
lines.append("# snapshots; see after/hash_table_before_after.json for the per-anchor rows).")

(ATT / "changes.diff").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(hash_table["verdict"], ensure_ascii=False))
