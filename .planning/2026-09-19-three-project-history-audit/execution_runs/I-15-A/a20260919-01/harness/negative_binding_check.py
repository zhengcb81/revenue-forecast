"""I-15-A negative binding case: a prune aimed at the PRODUCTION catalog must be refused.

Asserts that `guard_scratch` refuses before any connection is opened, and that the
production catalog file is not even opened for reading by this harness.

    python negative_binding_check.py
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from archive_verifier import guard_scratch  # noqa: E402

PROD_CATALOG = Path(r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog")
PROD_DB = PROD_CATALOG / "catalog.sqlite3"


def main() -> int:
    report: dict = {"cases": []}

    # 1. the production catalog dir itself
    try:
        guard_scratch(PROD_CATALOG)
        report["cases"].append({"path": str(PROD_CATALOG), "refused": False})
    except SystemExit as exc:
        report["cases"].append({"path": str(PROD_CATALOG), "refused": True, "message": str(exc)})

    # 2. the production catalog database file
    try:
        guard_scratch(PROD_DB)
        report["cases"].append({"path": str(PROD_DB), "refused": False})
    except SystemExit as exc:
        report["cases"].append({"path": str(PROD_DB), "refused": True, "message": str(exc)})

    # 3. a path outside execution_runs entirely
    try:
        guard_scratch(Path.home() / "i15a-outside")
        report["cases"].append({"path": str(Path.home() / "i15a-outside"), "refused": False})
    except SystemExit as exc:
        report["cases"].append({"path": str(Path.home() / "i15a-outside"), "refused": True,
                                "message": str(exc)})

    # 4. the production DB must not have been opened at all by this process
    report["prod_db_size_bytes"] = PROD_DB.stat().st_size
    report["prod_db_sha256_note"] = "not hashed: hashing would read 49.7 GB; size+mtime only"
    report["prod_db_mtime_ns"] = PROD_DB.stat().st_mtime_ns
    report["opened_connections"] = []

    # 5. a connection to the production DB must fail if attempted with the guard
    try:
        guarded = guard_scratch(PROD_DB)          # raises
        sqlite3.connect(f"file:{guarded}?mode=ro", uri=True)
        report["opened_connections"].append({"path": str(PROD_DB), "opened": True})
    except SystemExit as exc:
        report["cases"].append({"path": "connect-after-guard", "refused": True, "message": str(exc)})

    report["all_refused"] = all(c["refused"] for c in report["cases"]) and not report["opened_connections"]
    out = HERE.parent / "after_pass" / "evidence" / "negative-binding-check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["all_refused"] else 1


if __name__ == "__main__":
    sys.exit(main())
