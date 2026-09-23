"""I-07-C read-only production census (X03 blocked-proof, best effort).

Opens the PRODUCTION catalog with mode=ro + PRAGMA query_only (never writes).
Every query runs under a wall-clock guard; if the 49.7GB catalog cannot answer
in time, the step is recorded as NOT-COMPLETED-with-reason - X03 stays BLOCKED
either way, this query is corroboration only.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import threading
from datetime import datetime, timezone

from i07c_common import EVID, PROD_CATALOG, write_json

DEADLINE_SECONDS = 240.0

STEPS = [
    ("locations_per_root",
     "SELECT root_id, COUNT(*) AS n FROM locations GROUP BY root_id ORDER BY root_id"),
    ("document_total",
     "SELECT COUNT(*) AS n FROM documents"),
    ("external_only_candidates",
     "SELECT COUNT(*) AS n FROM documents d"
     " WHERE EXISTS (SELECT 1 FROM locations l WHERE l.document_id=d.document_id)"
     " AND NOT EXISTS (SELECT 1 FROM locations l WHERE l.document_id=d.document_id"
     " AND l.root_id NOT IN ('dropbox_stock','future_lake'))"),
]

EXTERNAL_ROOT_IDS = ("dropbox_stock", "future_lake")


def run_guarded(conn, name: str, sql: str, deadline: float) -> dict:
    result: dict = {"step": name, "sql": sql}
    box: dict = {}

    def worker() -> None:
        try:
            box["rows"] = [tuple(r) for r in conn.execute(sql).fetchall()]
        except Exception as exc:  # noqa: BLE001 - record, do not raise
            box["error"] = f"{type(exc).__name__}: {exc}"

    thread = threading.Thread(target=worker, daemon=True)
    started = datetime.now(timezone.utc).isoformat()
    thread.start()
    thread.join(timeout=max(0.1, deadline))
    if thread.is_alive():
        result.update({"status": "NOT_COMPLETED", "reason":
                       f"query exceeded remaining budget ({deadline:.0f}s); "
                       "production catalog too large to answer within the bound timeout",
                       "started_at_utc": started})
    elif "error" in box:
        result.update({"status": "ERROR", "error": box["error"], "started_at_utc": started})
    else:
        result.update({"status": "OK", "rows": box.get("rows", []),
                       "started_at_utc": started})
    return result


def main() -> int:
    payload: dict = {
        "purpose": "X03 external-only blocked proof (corroboration): verify all "
                   "registered locations before anyone could ever conclude 'only'",
        "opened": str(PROD_CATALOG),
        "mode": "ro + PRAGMA query_only (zero writes)",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "external_root_ids": list(EXTERNAL_ROOT_IDS),
        "steps": [],
    }
    if not PROD_CATALOG.is_file():
        payload["status"] = "NOT_COMPLETED"
        payload["reason"] = "production catalog missing"
        write_json(EVID / "prod_census.json", payload)
        print("production catalog missing")
        return 0
    payload["catalog_bytes"] = PROD_CATALOG.stat().st_size

    import time
    budget_start = time.time()
    try:
        # check_same_thread=False: queries run in a guard thread; the
        # connection itself stays mode=ro + query_only (zero writes).
        conn = sqlite3.connect(f"file:{PROD_CATALOG}?mode=ro", uri=True,
                               check_same_thread=False)
        conn.execute("PRAGMA query_only=ON")
        for name, sql in STEPS:
            remaining = DEADLINE_SECONDS - (time.time() - budget_start)
            if remaining <= 0:
                payload["steps"].append(
                    {"step": name, "status": "SKIPPED",
                     "reason": "global budget exhausted"})
                continue
            payload["steps"].append(run_guarded(conn, name, sql, remaining))
        conn.close()
    except Exception as exc:  # noqa: BLE001
        payload["status"] = "ERROR"
        payload["error"] = f"{type(exc).__name__}: {exc}"
    payload["elapsed_seconds"] = round(time.time() - budget_start, 2)
    payload.setdefault("status",
                       "OK" if all(s.get("status") == "OK"
                                   for s in payload["steps"]) else "PARTIAL")
    payload["verdict_note"] = (
        "This census never signs X03: sample_manifest EXTERNAL-ONLY is unbound "
        "(reviewer must freeze identity/authority first) and manufacturing "
        "exclusivity by deleting other copies is forbidden. BLOCKED stands "
        "regardless of what these steps return.")
    write_json(EVID / "prod_census.json", payload)
    print(json.dumps({"status": payload["status"],
                      "steps": [(s["step"], s["status"]) for s in payload["steps"]]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
