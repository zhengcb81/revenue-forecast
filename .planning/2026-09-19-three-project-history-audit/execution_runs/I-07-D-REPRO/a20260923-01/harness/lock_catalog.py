"""I-07-D registration-failure injection (scenario F03 pattern, scratch-only).

Holds a BEGIN EXCLUSIVE write transaction on ONE isolated case catalog for N
seconds, logging the hold, then releases cleanly. Touches only
%TEMP%\\i07d\\cases\\<case> — never production.

Usage: lock_catalog.py <case_id> <hold_seconds>
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
CASES = Path(os.environ.get("TEMP", r"C:\Temp")) / "i07d" / "cases"


def main() -> int:
    case_id, hold = sys.argv[1], float(sys.argv[2])
    cat = CASES / case_id / "cwroot" / ".source_catalog" / "catalog.sqlite3"
    ev = ATT / "evidence" / "cases" / case_id / "lock"
    ev.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(cat, timeout=5.0, isolation_level=None)
    rec = {"case": case_id, "catalog": str(cat), "hold_s": hold,
           "started": datetime.now(timezone.utc).isoformat()}
    try:
        con.execute("BEGIN EXCLUSIVE")
        rec["lock"] = "BEGIN EXCLUSIVE acquired (isolation-only target)"
        rec["locked_at"] = datetime.now(timezone.utc).isoformat()
        time.sleep(hold)
        con.execute("ROLLBACK")
        rec["released"] = datetime.now(timezone.utc).isoformat()
        rec["ok"] = True
    except Exception as exc:  # noqa: BLE001
        rec["ok"] = False
        rec["error"] = f"{type(exc).__name__}: {exc}"
        try:
            con.execute("ROLLBACK")
        except sqlite3.Error:
            pass
    finally:
        con.close()
    (ev / "hold.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
    print(json.dumps(rec, ensure_ascii=False))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
