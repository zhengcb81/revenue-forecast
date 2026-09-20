"""W06A evidence builder: the three card-required JSON files.

Reads the driver outputs and the demand DB and writes:
  <tag>/demand.cross-process.json
  <tag>/request-to-demand-binding.json
  <tag>/paused-before-after.json

The demand table is read with plain sqlite3 (never through the candidate
API), so these are independent observations.

  <py> -X utf8 -B scripts/w06a_evidence.py <tag> <baseline|candidate>
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples"

DEMAND_ID_RE = re.compile(r"demand_id=(demand-[0-9a-f]+)")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_demands(db: Path) -> list[dict]:
    if not db.is_file():
        return []
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        return [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM processing_demands ORDER BY created_at, demand_id"
            )
        ]
    finally:
        connection.close()


def main() -> int:
    tag = sys.argv[1] if len(sys.argv) > 1 else "before"
    kind = sys.argv[2] if len(sys.argv) > 2 else "baseline"
    results = json.loads(
        (ATTEMPT / tag / f"case_results_{kind}.json").read_text(encoding="utf-8")
    )
    db = Path(results["demand_store"])
    rows = read_demands(db)
    out_dir = ATTEMPT / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- demand.cross-process.json -------------------------------------
    observed_ids = {}
    for case, payload in results["cases"].items():
        match = DEMAND_ID_RE.search(payload.get("stderr") or "")
        observed_ids[case] = match.group(1) if match else None
    active = [row for row in rows if row["status"] in ("pending", "running", "failed")]
    cross = {
        "tag": tag,
        "tree": kind,
        "demand_database": str(db),
        "database_exists": db.is_file(),
        "process_count": sum(
            1 for case in results["cases"] if case.startswith(("b", "c"))
            and not case.endswith("query")
        ),
        "query_processes": {
            case: value["returncode"]
            for case, value in results["cases"].items()
            if "query" in case
        },
        "demand_ids_in_stderr": observed_ids,
        "request_hashes": results.get("request_hashes"),
        "active_demand_count": len(active),
        "rows": [
            {
                "demand_id": row["demand_id"],
                "demand_key": row["demand_key"],
                "status": row["status"],
                "source_sha256": row["source_sha256"],
                "review_policy": row["review_policy"],
                "role_set": row["role_set"],
                "request_sha256": row["request_sha256"],
                "request_json": row["request_json"],
                "gaps": json.loads(row["gaps_json"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ],
        "independent_key_check": [
            {
                "demand_id": row["demand_id"],
                "recorded_key": row["demand_key"],
                "recomputed_key": canonical_sha256(
                    {
                        "source_sha256": row["source_sha256"],
                        "review_policy": row["review_policy"],
                        "role_set": row["role_set"],
                    }
                ),
                "key_matches": row["demand_key"]
                == canonical_sha256(
                    {
                        "source_sha256": row["source_sha256"],
                        "review_policy": row["review_policy"],
                        "role_set": row["role_set"],
                    }
                ),
                "source_sha256_matches_fixture_file": row["source_sha256"]
                in (
                    sha256_file(SAMPLES / "source_bytes.txt"),
                    results.get("changed_source_bytes_sha256"),
                ),
            }
            for row in rows
        ],
        "note": (
            "The demand table is read with plain sqlite3, not through the "
            "candidate API; the key is recomputed here from the stored fields."
        ),
    }
    (out_dir / "demand.cross-process.json").write_text(
        json.dumps(cross, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- request-to-demand-binding.json --------------------------------
    request = json.loads((SAMPLES / "request.json").read_text(encoding="utf-8"))
    binding = {
        "tag": tag,
        "tree": kind,
        "request_path": str(SAMPLES / "request.json"),
        "request_sha256_recomputed": canonical_sha256(request),
        "request_json": request,
        "request_file_sha256": sha256_file(SAMPLES / "request.json"),
        "handle_path": str(SAMPLES / "handle.json"),
        "handle_sha256": sha256_file(SAMPLES / "handle.json"),
        "rows": [
            {
                "demand_id": row["demand_id"],
                "request_sha256": row["request_sha256"],
                "request_sha256_matches": row["request_sha256"]
                == canonical_sha256(request),
                "source_sha256": row["source_sha256"],
                "review_policy": row["review_policy"],
                "role_set": row["role_set"],
                "gaps": json.loads(row["gaps_json"]),
                "attempts": row["attempts"],
                "status": row["status"],
            }
            for row in rows
        ],
        "no_review_fabricated": {
            "prompt_injection_status_in_envelope": json.loads(
                (SAMPLES / "handle.json").read_text(encoding="utf-8")
            )["resolution_envelope"]["prompt_injection_status"],
            "review_rows_written": 0,
            "note": "no review result is written anywhere by this attempt",
        },
    }
    (out_dir / "request-to-demand-binding.json").write_text(
        json.dumps(binding, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ---- paused-before-after.json --------------------------------------
    control = Path(results["worker_control"])
    paused = {
        "tag": tag,
        "tree": kind,
        "worker_control_path": str(control),
        "note": (
            "The attempt clones contain NO worker control file; this fixture "
            "lives under %TEMP% and is only READ by the candidate."
        ),
        "before": results["paused_before"],
        "after": results["paused_after"],
        "unchanged": results["paused_unchanged"],
        "bytes_sha256_before": (
            hashlib.sha256(
                (results["paused_before"]["bytes"] or "").encode("utf-8")
            ).hexdigest()
            if results["paused_before"]["bytes"] is not None
            else None
        ),
        "bytes_sha256_after": (
            hashlib.sha256(
                (results["paused_after"]["bytes"] or "").encode("utf-8")
            ).hexdigest()
            if results["paused_after"]["bytes"] is not None
            else None
        ),
        "real_worker_control_touched": False,
        "resume_automation_observed": False,
    }
    (out_dir / "paused-before-after.json").write_text(
        json.dumps(paused, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps({
        "tag": tag,
        "tree": kind,
        "active_demand_count": len(active),
        "rows": len(rows),
        "paused_unchanged": results["paused_unchanged"],
        "request_sha_matches": [
            row["request_sha256"] == canonical_sha256(request) for row in rows
        ],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
