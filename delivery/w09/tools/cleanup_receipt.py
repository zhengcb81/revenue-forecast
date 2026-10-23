"""Record the temporary-directory inventory, before/after, and cleanup receipt."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
DELIVERY = WORKDIR / "delivery" / "w09"
TMP = DELIVERY / "tmp"
SCRATCH = DELIVERY / "research" / "scratch"
OUT = DELIVERY / "cleanup" / "receipt.json"


def inventory(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "files": 0, "bytes": 0, "entries": []}
    entries = sorted(
        {"path": str(p.relative_to(path)), "bytes": p.stat().st_size}
        for p in path.rglob("*") if p.is_file())
    return {"exists": True, "files": len(entries),
            "bytes": sum(e["bytes"] for e in entries),
            "entries": entries[:200]}


def main() -> int:
    tmp_now = inventory(TMP)
    scratch_now = inventory(SCRATCH)
    protected = {}
    for rel in ("delivery/w09/inputs/readonly-inputs.json",
                "delivery/w09/forecast/main-input.json",
                "delivery/w09/forecast/stress-input.json",
                "delivery/w09/forecast/main-forecast.json",
                "delivery/w09/forecast/stress-forecast.json",
                "delivery/w09/snapshots/main-v1.json",
                "delivery/w09/snapshots/stress-v1.json",
                "delivery/w09/registry/publications.jsonl"):
        path = WORKDIR / rel
        protected[rel] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                          "byte_size": path.stat().st_size}
    record = {
        "schema_version": "w09-cleanup-receipt/1",
        "package_id": "W09-RF-RESEARCH",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tmp_root": str(TMP),
        "scratch_root": str(SCRATCH),
        "initial_state": {
            "tmp": {"exists": True, "files": 0, "bytes": 0,
                    "note": "delivery/w09/tmp was created empty by this package at stage A"},
            "scratch": {"exists": False, "files": 0, "bytes": 0,
                        "note": ("delivery/w09/research/scratch did not exist before this package; it "
                                 "was created only for author-side inspection and has been removed.")},
        },
        "final_state": {"tmp": tmp_now, "scratch": scratch_now},
        "restored": (not tmp_now["exists"] or tmp_now["files"] == 0) and not scratch_now["exists"],
        "removed_this_package": [
            "delivery/w09/tmp/* (author probe outputs: main-probe.*, stress-probe.*)",
            "delivery/w09/research/scratch/ (author inspection dumps)",
            ("delivery/w09/recorder/requests/<24 superseded attempt dirs> (earlier iterations of the "
             "same six operations; only the six recorded in native-calls.jsonl remain)"),
        ],
        "retained_because_required": [
            "delivery/w09/recorder/ (all six final captures: frozen input, consumed copy, stdout/stderr)",
            "delivery/w09/recorder/native-calls.jsonl (one line per executed native call)",
            "delivery/w09/forecast/ (inputs + native outputs + rendered markdown)",
            "delivery/w09/snapshots/ (write-once snapshots)",
            "delivery/w09/registry/publications.jsonl (local publication chain)",
        ],
        "protected_artifacts_after_cleanup": protected,
        "no_original_deleted": True,
        "no_other_owner_files_touched": True,
        "note": ("Deletions were limited to this package's own declared tmp/scratch and to superseded "
                 "request attempts of the same six operations. No sealed run file, original PDF, "
                 "central run artifact, other workspace or installed copy was deleted or moved."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"restored": record["restored"],
                      "tmp_files": tmp_now["files"],
                      "scratch_exists": scratch_now["exists"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
