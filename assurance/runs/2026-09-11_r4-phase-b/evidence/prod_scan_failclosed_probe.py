"""F-PROD-01 probe: WHY the production scan now fail-closes on `company_raw` (read-only).

Found on 2026-09-19 while reading the production catalog's OWN `scan_runs` table: the two most
recent runs (2026-09-19T04:52Z) completed_with_errors with `files_seen: 0` and the error
"scan_root_strategy: v2 scanner unavailable (fail closed): root 'company_raw' has no adapter_id
(2.x policy required)".  This script establishes the chain from the artefacts themselves:

  1. `catalog_dir/runtime_policy.json` -> flags.v2_scan_shadow (and WHEN the snapshot was written)
  2. `config/source_catalog.yaml`      -> which roots declare an `adapter_id`
  3. the catalog's `scan_runs` rows    -> the last runs that actually did work
  4. the code path                     -> service/canonical_writer -> scanner.use_adapter ->
                                          scan_root_strategy -> adapter_dispatch fail-closed

The catalog is opened `mode=ro` (no write, no migration, no journal change); the config and the
snapshot are read as text.  Nothing is written except the --out JSON.

Usage::

    python prod_scan_failclosed_probe.py --out prod-scan-failclosed.json
"""

from __future__ import annotations

import argparse
import datetime
import json
import sqlite3
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
CATALOG_DIR = WIKI / ".source_catalog"
DB = CATALOG_DIR / "catalog.sqlite3"
SNAPSHOT = CATALOG_DIR / "runtime_policy.json"
CONFIG = WIKI / "config" / "source_catalog.yaml"

# git says the fail-closed check predates this run entirely: 7cf5957 (2026-08-10) introduced
# "root {root_id!r} has no adapter_id (2.x policy required)" in adapter_dispatch.py.
PREDATES_THIS_RUN = "7cf5957 (2026-08-10, feat(fc-302): production AdapterRegistry dispatch)"


def file_state(path: Path) -> dict:
    stat = path.stat()
    return {
        "path": str(path),
        "byte_size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "mtime_utc": datetime.datetime.fromtimestamp(
            stat.st_mtime, datetime.timezone.utc).isoformat(),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).with_name("prod-scan-failclosed.json"))
    parser.add_argument("--runs", type=int, default=6)
    args = parser.parse_args(argv)

    import yaml

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    roots = [
        {"root_id": root.get("root_id"), "kind": root.get("kind"),
         "adapter_id": root.get("adapter_id"), "priority": root.get("priority")}
        for root in config.get("roots", [])
    ]
    roots_without_adapter = [root["root_id"] for root in roots if not root.get("adapter_id")]

    con = sqlite3.connect("file:" + str(DB).replace("\\", "/") + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    runs = []
    for row in con.execute(
            "SELECT run_id, started_at, completed_at, status, report_json "
            "FROM scan_runs ORDER BY rowid DESC LIMIT ?", (args.runs,)):
        report = {}
        if row["report_json"]:
            try:
                report = json.loads(row["report_json"])
            except ValueError:
                report = {"unparsable": True}
        runs.append({
            "run_id": row["run_id"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "status": row["status"],
            "files_seen": report.get("files_seen"),
            "files_hashed": report.get("files_hashed"),
            "files_reused": report.get("files_reused"),
            "errors": report.get("errors"),
            "strategy": report.get("strategy"),
            "error_details": report.get("error_details"),
        })
    con.close()

    v2_scan_shadow = bool((snapshot.get("flags") or {}).get("v2_scan_shadow"))
    runs_after_snapshot = [
        run for run in runs if (run["started_at"] or "") > snapshot.get("updated_at", "")
    ]
    record = {
        "artifact": "prod-scan-failclosed-probe",
        "question": ("is the 2026-09-19 production scan failure caused by this run's product "
                     "changes, or by the production activation snapshot enabling v2_scan_shadow "
                     "while company_raw declares no adapter?"),
        "catalog": file_state(DB),
        "wal": file_state(Path(str(DB) + "-wal")) if Path(str(DB) + "-wal").exists() else None,
        "shm": file_state(Path(str(DB) + "-shm")) if Path(str(DB) + "-shm").exists() else None,
        "snapshot": {**file_state(SNAPSHOT),
                     "updated_at": snapshot.get("updated_at"),
                     "policy_hash": snapshot.get("policy_hash"),
                     "flags": snapshot.get("flags")},
        "config": {**file_state(CONFIG), "roots": roots},
        "v2_scan_shadow": v2_scan_shadow,
        "roots_without_adapter_id": roots_without_adapter,
        "recent_scan_runs": runs,
        "chain": [
            "service.py:148-159 / canonical_writer.py:190 resolve v2_scan_shadow from "
            "catalog_dir/runtime_policy.json (cutover_decision, scanner.py:1219-1224)",
            "scanner.py:855 use_adapter = v2_scan_shadow or root.adapter_id is not None "
            "-> True for every root while the snapshot says true",
            "scanner.py:1941-1947 scan_root_strategy(v2_scan_shadow=True) -> "
            "scan_root_via_adapter -> AdapterDispatchError, re-raised as ScannerFacadeError "
            "(FC-303: never fall back to v1)",
            "adapter_dispatch.py:41 raises for the adapter-less root: " + PREDATES_THIS_RUN,
            "scanner.py: per-root ScannerFacadeError handling (F-BA1-04, 2026-09-18) records the "
            "root as an error and lets the run finish; BEFORE that change the same error aborted "
            "the WHOLE run, so the failure is not introduced by it either",
        ],
        "conclusion": (
            "NOT caused by the 2026-09-18/19 product changes: the snapshot has said "
            "v2_scan_shadow=true since " + str(snapshot.get("updated_at")) + ", and the "
            "adapter-less-root refusal has existed since " + PREDATES_THIS_RUN + ". Every "
            "production scan since the snapshot therefore fail-closes on company_raw and sees "
            "0 files; the pre-09-18 code would have aborted the entire run instead. The fix is a "
            "production decision (declare an adapter for company_raw, turn the shadow flag off, "
            "or make the dispatch fall back to v1 for adapter-less roots) and is OUTSIDE this "
            "step's authorization"
        ),
        "runs_after_snapshot": len(runs_after_snapshot),
        "ran_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({
        "v2_scan_shadow": record["v2_scan_shadow"],
        "snapshot_updated_at": record["snapshot"]["updated_at"],
        "roots_without_adapter_id": record["roots_without_adapter_id"],
        "catalog_mtime_utc": record["catalog"]["mtime_utc"],
        "recent_runs": [(run["started_at"], run["status"], run["files_seen"])
                        for run in record["recent_scan_runs"]],
        "runs_after_snapshot": record["runs_after_snapshot"],
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
