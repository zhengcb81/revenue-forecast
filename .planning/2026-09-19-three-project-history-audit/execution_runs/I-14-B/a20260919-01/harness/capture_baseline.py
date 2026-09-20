"""I-14-B step-2 binding capture (READ-ONLY on the three product repos).

Writes a single JSON witness: repo HEADs, porcelain, the production catalog
invariants, the audit-reviews mtime invariant, and the freeze instant.

Nothing here writes outside the attempt directory.  git is invoked with
--no-optional-locks so that `status` does not refresh the on-disk index.

Usage:
  <iso-python> -X utf8 -B harness/capture_baseline.py --out evidence/baseline_repos.json --label before
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPOS = {
    "revenue-forecast": r"C:\Users\郑曾波\Projects\revenue-forecast",
    "filing-fetch": r"C:\Users\郑曾波\Projects\filing-fetch",
    "company-wiki": r"C:\Users\郑曾波\Projects\company-wiki",
}

# read-only anchors cited by this card (production tree; must stay byte-identical)
ANCHORS = {
    "RF/tests/test_ca206_soak_window.py": r"C:\Users\郑曾波\Projects\revenue-forecast\tests\test_ca206_soak_window.py",
    "RF/audit_review/2026-08-09_full_completion_assurance_plan/task_plan.md":
        r"C:\Users\郑曾波\Projects\revenue-forecast\audit_review\2026-08-09_full_completion_assurance_plan\task_plan.md",
    "RF/assurance/runs/daily_manifest.json":
        r"C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\daily_manifest.json",
    "RF/assurance/runs/weekly_manifest.json":
        r"C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\weekly_manifest.json",
    "RF/assurance/runs/monthly_manifest.json":
        r"C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\monthly_manifest.json",
    "RF/assurance/runs/legacy_periods.json":
        r"C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\legacy_periods.json",
    "CW/.source_catalog/catalog.sqlite3":
        r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3",
}

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"


def run(argv: list[str], cwd: str | None = None) -> dict:
    proc = subprocess.run(argv, cwd=cwd, capture_output=True)
    return {
        "argv": argv,
        "cwd": cwd,
        "raw_returncode": proc.returncode,
        "stdout": proc.stdout.decode("utf-8", "replace"),
        "stderr": proc.stderr.decode("utf-8", "replace"),
    }


def sha256_file(path: str) -> str | None:
    p = Path(path)
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_of(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"exists": False}
    st = p.stat()
    return {
        "exists": True,
        "size_bytes": st.st_size,
        "mtime_utc": datetime.fromtimestamp(st.st_mtime, UTC).isoformat().replace("+00:00", "Z"),
        "is_dir": p.is_dir(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    args = ap.parse_args()

    observed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    doc: dict = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "label": args.label,
        "observed_at_utc": observed_at,
        "interpreter": sys.executable,
        "interpreter_version": sys.version,
        "writes_performed_outside_attempt": False,
        "repos": {},
        "anchors": {},
        "invariants": {},
        "git_commands": {},
    }

    for name, path in REPOS.items():
        head = run(["git", "--no-optional-locks", "rev-parse", "HEAD"], cwd=path)
        porcelain = run(["git", "--no-optional-locks", "status", "--porcelain"], cwd=path)
        doc["git_commands"][f"{name}:rev-parse"] = head
        doc["git_commands"][f"{name}:status"] = porcelain
        lines = [ln for ln in porcelain["stdout"].splitlines() if ln.strip()]
        doc["repos"][name] = {
            "path": path,
            "head": head["stdout"].strip(),
            "head_rc": head["raw_returncode"],
            "porcelain_rc": porcelain["raw_returncode"],
            "porcelain_lines": lines,
            "porcelain_count": len(lines),
        }

    for label, path in ANCHORS.items():
        doc["anchors"][label] = {"path": path, "stat": stat_of(path), "sha256": sha256_file(path)}

    doc["invariants"]["catalog_sqlite3"] = {
        "path": ANCHORS["CW/.source_catalog/catalog.sqlite3"],
        "size_bytes": stat_of(ANCHORS["CW/.source_catalog/catalog.sqlite3"]).get("size_bytes"),
        "mtime_utc": stat_of(ANCHORS["CW/.source_catalog/catalog.sqlite3"]).get("mtime_utc"),
        "wal": stat_of(ANCHORS["CW/.source_catalog/catalog.sqlite3"] + "-wal"),
        "shm": stat_of(ANCHORS["CW/.source_catalog/catalog.sqlite3"] + "-shm"),
    }
    doc["invariants"]["plan_reviews_dir"] = stat_of(os.path.join(PLAN, "reviews"))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "observed_at_utc": observed_at}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
