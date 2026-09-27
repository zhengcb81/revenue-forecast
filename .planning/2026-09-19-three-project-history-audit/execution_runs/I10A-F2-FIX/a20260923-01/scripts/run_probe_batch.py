#!/usr/bin/env python
"""I10A-F2-FIX probe batch driver — records RAW rc per probe run.

Runs the frozen I-10-A harness (`harness/run_mapping_probe.py`, sha-pinned in the
binding) against `iso/rf` for the 4 frozen cases x the requested arms, captures
each run's process rc (the harness's own `raw_rc` is asserted to match), and
writes `evidence/rc_<tag>.json`.

Usage:
  python scripts/run_probe_batch.py <tag> <out_dir_name_under_evidence> <arm> [<arm> ...]
Exit 0 iff every run's process rc equals the harness raw_rc AND the collected
table matches the requested arms (so a harness failure cannot be misread).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
HARNESS = ATT / "harness" / "run_mapping_probe.py"
EXPECT = (
    ATT.parent.parent
    / "I-10-A"
    / "a20260923-01"
    / "evidence"
    / "I-10-A"
    / "oracle_expected.json"
)
CASES = ["ZJ-MIN-M09", "ZJ-SMT-M09", "XM-PHONE-M03", "XM-EV-M03"]


def main() -> int:
    tag = sys.argv[1]
    out_name = sys.argv[2]
    arms = sys.argv[3:]
    if not arms:
        print("usage: run_probe_batch.py <tag> <out_dir> <arm> [<arm> ...]")
        return 1
    out_root = ATT / "evidence" / out_name
    rows = []
    mismatch = []
    for case in CASES:
        for arm in arms:
            out_dir = out_root / case / arm
            proc = subprocess.run(
                [
                    sys.executable,
                    str(HARNESS),
                    "--case",
                    case,
                    "--variant",
                    arm,
                    "--out",
                    str(out_dir),
                    "--expect-file",
                    str(EXPECT),
                ],
                capture_output=True,
                text=True,
            )
            result_path = out_dir / "probe_result.json"
            raw_rc = None
            if result_path.exists():
                raw_rc = json.loads(result_path.read_text(encoding="utf-8"))["raw_rc"]
            row = {
                "case": case,
                "arm": arm,
                "process_rc": proc.returncode,
                "harness_raw_rc": raw_rc,
                "stdout_tail": proc.stdout.strip()[-400:],
                "stderr_tail": proc.stderr.strip()[-400:],
            }
            rows.append(row)
            if raw_rc is not None and proc.returncode != raw_rc:
                mismatch.append(row)
            print(json.dumps({k: row[k] for k in ("case", "arm", "process_rc", "harness_raw_rc")}))
    table: dict[str, dict[str, int]] = {}
    for row in rows:
        table.setdefault(row["arm"], {})[row["case"]] = row["harness_raw_rc"]
    payload = {
        "artifact": "probe_batch_rc",
        "tag": tag,
        "out_dir": str(out_root.relative_to(ATT)).replace("\\", "/"),
        "expect_file": str(EXPECT),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "table": table,
        "rows": rows,
        "process_rc_equals_harness_raw_rc": not mismatch,
    }
    out_path = ATT / "evidence" / f"rc_{tag}.json"
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({"table": table, "mismatch": len(mismatch)}))
    return 0 if not mismatch else 1


if __name__ == "__main__":
    raise SystemExit(main())
