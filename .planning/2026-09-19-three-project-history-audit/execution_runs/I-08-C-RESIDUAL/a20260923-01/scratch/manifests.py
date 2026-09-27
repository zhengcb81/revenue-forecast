"""I08CR-c0 / I08CR-c12 — per-file hash manifests of the READ-ONLY referenced attempts.

Modes:  before -> evidence/manifests_before.json
        after  -> evidence/manifests_after.json + evidence/manifests_comparison.json
                  (asserts 0 added / 0 removed / 0 changed against the before manifest)

Writes ONLY inside this attempt's evidence/ directory.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
PLAN = ATT.parents[2]  # .../execution_runs/I-08-C-RESIDUAL/a20260923-01 -> plan root

TREES = {
    "I-08-C/a20260919-01": PLAN / "execution_runs" / "I-08-C" / "a20260919-01",
    "B1-I08C-product-fixes/a20260921-01": PLAN / "execution_runs" / "B1-I08C-product-fixes" / "a20260921-01",
    "B1-PREREQ/a20260922-01": PLAN / "execution_runs" / "B1-PREREQ" / "a20260922-01",
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root: Path):
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            st = p.stat()
            out[rel] = {
                "sha256": sha256_file(p),
                "bytes": st.st_size,
                "mtime_ns": st.st_mtime_ns,
            }
    return out


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "before"
    EVID.mkdir(parents=True, exist_ok=True)
    payload = {
        "mode": mode,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "trees": {name: {"root": str(root), "files": walk(root)} for name, root in TREES.items()},
    }
    for name, t in payload["trees"].items():
        print(f"{name}: {len(t['files'])} files")

    if mode == "before":
        (EVID / "manifests_before.json").write_text(
            json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8"
        )
        ho = payload["trees"]["I-08-C/a20260919-01"]["files"].get("handoff.json")
        print("I-08-C handoff.json BEFORE:", json.dumps(ho))
        return 0

    (EVID / "manifests_after.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8"
    )
    before = json.loads((EVID / "manifests_before.json").read_text(encoding="utf-8"))
    comparison = {"trees": {}, "all_untouched": True}
    for name in TREES:
        b = before["trees"][name]["files"]
        a = payload["trees"][name]["files"]
        added = sorted(set(a) - set(b))
        removed = sorted(set(b) - set(a))
        changed = sorted(k for k in set(a) & set(b) if a[k]["sha256"] != b[k]["sha256"])
        mtime_changed = sorted(
            k for k in set(a) & set(b) if a[k]["mtime_ns"] != b[k]["mtime_ns"]
        )
        ok = not (added or removed or changed)
        comparison["trees"][name] = {
            "files_before": len(b),
            "files_after": len(a),
            "added": added,
            "removed": removed,
            "content_changed": changed,
            "mtime_changed": mtime_changed,
            "content_untouched": ok,
        }
        comparison["all_untouched"] = comparison["all_untouched"] and ok
        print(f"{name}: added={len(added)} removed={len(removed)} content_changed={len(changed)} mtime_changed={len(mtime_changed)}")
    ho_b = before["trees"]["I-08-C/a20260919-01"]["files"].get("handoff.json")
    ho_a = payload["trees"]["I-08-C/a20260919-01"]["files"].get("handoff.json")
    comparison["i08c_handoff_unchanged_assertion"] = {
        "before": ho_b,
        "after": ho_a,
        "sha256_equal": (ho_b or {}).get("sha256") == (ho_a or {}).get("sha256"),
    }
    (EVID / "manifests_comparison.json").write_text(
        json.dumps(comparison, indent=1, sort_keys=True), encoding="utf-8"
    )
    print("all_untouched:", comparison["all_untouched"])
    print("i08c handoff unchanged:", comparison["i08c_handoff_unchanged_assertion"]["sha256_equal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
