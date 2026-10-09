"""Run native RF validation, publication, report and snapshot for a new input."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--version", help="new frozen forecast version (defaults to input version)")
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    version = args.version or data.get("forecast_version", f"{data['as_of_date']}-v1")
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ)
    environment.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
                       REVENUE_PUBLICATION_REGISTRY=str(output / "publications.jsonl"))
    python = [sys.executable, "-X", "utf8", "-B"]
    commands = [
        [*python, str(ROOT / "scripts/revenue_forecast.py"), str(args.input.resolve()), "--validate-only", "--verbose"],
        [*python, str(ROOT / "scripts/revenue_forecast.py"), str(args.input.resolve()), "--output", str(output / "forecast.json"), "--markdown", str(output / "forecast.md")],
        [*python, str(ROOT / "scripts/revenue_backtest.py"), "create", str(args.input.resolve()), "--version", version, "--output", str(output / "snapshot.json")],
    ]
    events = []
    for command in commands:
        started = time.monotonic()
        completed = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True,
                                   encoding="utf-8", timeout=120, check=False)
        events.append({"command": command, "exit_code": completed.returncode,
                       "seconds": time.monotonic() - started, "stdout": completed.stdout[-4096:],
                       "stderr": completed.stderr[-4096:]})
        receipt = {"schema_version": "native-target-measurement-run/1", "created_at": datetime.now(timezone.utc).isoformat(),
                   "events": events, "supplier_calls": 0, "model_calls": 0}
        (output / "commands.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if completed.returncode:
            return completed.returncode
    print(json.dumps({"status": "completed", "commands": len(events)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
