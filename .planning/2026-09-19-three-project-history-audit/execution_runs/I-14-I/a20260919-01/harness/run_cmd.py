"""Command runner for the I-14-I attempt.

Runs each bound command as a real subprocess with an explicit argv, captures
raw stdout / stderr / returncode into ``evidence/<label>/``, and records the
argv it actually used.  This exists because the attempt must record RAW exit
codes separately from EXPECTED ones and must not lose a subprocess's stderr
(the shell's native-command redirection was observed to swallow it).

Usage:
  <python> -X utf8 -B harness/run_cmd.py --spec <spec.json>

spec.json:
  {"label": "...", "cwd": "...", "argv": [...],
   "expected_returncode": 0, "out_dir": "...", "env": {...}}

Writes: <out_dir>/<label>/{stdout.txt,stderr.txt,argv.json}
Exit code of this runner is ALWAYS 0 when the capture succeeded; the observed
return code lives in argv.json so that a non-zero business rc is data, not an
infrastructure failure.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()

    # utf-8-sig: the spec files are authored by hand and may carry a BOM.
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8-sig"))
    label = spec["label"]
    out_dir = Path(spec["out_dir"]).resolve() / label
    out_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env.update(spec.get("env") or {})

    started = datetime.now(timezone.utc)
    proc = subprocess.run(spec["argv"], cwd=spec.get("cwd"),
                          env=env, capture_output=True)
    finished = datetime.now(timezone.utc)

    (out_dir / "stdout.txt").write_bytes(proc.stdout)
    (out_dir / "stderr.txt").write_bytes(proc.stderr)
    (out_dir / "argv.json").write_text(json.dumps({
        "label": label,
        "cwd": spec.get("cwd"),
        "argv": spec["argv"],
        "env_overrides": spec.get("env") or {},
        "raw_returncode": proc.returncode,
        "expected_returncode": spec.get("expected_returncode"),
        "matches_expectation": proc.returncode == spec.get("expected_returncode"),
        "started_at_utc": started.isoformat().replace("+00:00", "Z"),
        "finished_at_utc": finished.isoformat().replace("+00:00", "Z"),
        "stdout_bytes": len(proc.stdout),
        "stderr_bytes": len(proc.stderr),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"label": label, "raw_returncode": proc.returncode,
                      "expected_returncode": spec.get("expected_returncode"),
                      "stdout_bytes": len(proc.stdout),
                      "stderr_bytes": len(proc.stderr)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
