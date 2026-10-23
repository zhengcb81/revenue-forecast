"""Build one execution_request for a native RF operation and run it under capture.

Usage:
  python run_native.py --op validate --input forecast/main-input.json \
      --request-id w09-main-validate --purpose "..."

The script only orchestrates the two read-only tools:
  * execution_request.py build  -> frozen request bytes + argv + input position
  * audit_run.py capture        -> freeze the exact consumed input and run it

It never edits the recorder tools and never rewrites a request after capture.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
DELIVERY = WORKDIR / "delivery" / "w09"
RECORDER = DELIVERY / "recorder"
RUN = RECORDER / "w09-rf-research-20261023"
REQUESTS = RECORDER / "requests"
SCOPE_DIR = DELIVERY / "request-scope"
TOOLS = Path(r"C:\Users\郑曾波\.agents\skills\revenue-forecast-audit\scripts")
EXECUTION_REQUEST = TOOLS / "execution_request.py"
AUDIT_RUN = TOOLS / "audit_run.py"
PYTHON = Path(r"C:/Miniconda/python.exe")
FORECAST = WORKDIR / "scripts" / "revenue_forecast.py"
BACKTEST = WORKDIR / "scripts" / "revenue_backtest.py"


def native_argv(op: str, request_path: Path, extra: list[str]) -> list[str]:
    argv = [str(PYTHON), "-X", "utf8", "-B"]
    if op in {"validate", "compute"}:
        argv += [str(FORECAST), str(request_path)]
        argv += extra
    elif op == "snapshot":
        argv += [str(BACKTEST), "create", str(request_path)] + extra
    else:
        raise SystemExit(f"unknown op {op}")
    return argv


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--op", required=True, choices=["validate", "compute", "snapshot"])
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--request-id", required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--markdown", type=Path)
    ap.add_argument("--version")
    ap.add_argument("--max-log-bytes", type=int, default=131072)
    ap.add_argument("--timeout-seconds", type=int, default=210)
    args = ap.parse_args()

    input_path = (WORKDIR / args.input).resolve() if not args.input.is_absolute() else args.input
    request = json.loads(input_path.read_text(encoding="utf-8"))
    extra: list[str] = []
    if args.op == "validate":
        extra = ["--validate-only", "--verbose"]
    elif args.op == "compute":
        if args.output is None or args.markdown is None:
            raise SystemExit("compute needs --output and --markdown")
        extra = ["--output", str(args.output.resolve()), "--markdown", str(args.markdown.resolve())]
    else:
        if args.version is None or args.output is None:
            raise SystemExit("snapshot needs --version and --output")
        extra = ["--version", args.version, "--output", str(args.output.resolve())]

    # The request template's argv must contain {request} exactly once.
    argv_template = native_argv(args.op, Path("{request}"), extra)
    template = {
        "request_id": args.request_id,
        "purpose": args.purpose,
        "profile": "P1",
        "native_adapter": "revenue-forecast/business/1",
        "request": request,
        "command": argv_template,
    }
    REQUESTS.mkdir(parents=True, exist_ok=True)
    template_path = REQUESTS / f"{args.request_id}.template.json"
    template_path.write_text(json.dumps(template, ensure_ascii=False, indent=1) + "\n",
                             encoding="utf-8")

    build = subprocess.run(
        [str(PYTHON), str(EXECUTION_REQUEST), "build",
         "--scope", str(SCOPE_DIR / "local-scope.json"),
         "--deploy", str(SCOPE_DIR / "local-deploy.json"),
         "--template", str(template_path),
         "--out-root", str(REQUESTS)],
        capture_output=True, text=True, encoding="utf-8")
    if build.returncode != 0:
        print(build.stdout)
        print(build.stderr, file=sys.stderr)
        return build.returncode
    record = json.loads(build.stdout)
    positions = record["input_argv_positions"]
    if len(positions) != 1:
        raise SystemExit(f"unexpected input positions {positions}")
    index = positions[0]
    expected = f"{index}:{record['request_sha256']}:{record['request_bytes']}"

    capture = subprocess.run(
        [str(PYTHON), str(AUDIT_RUN), "capture", "--run", str(RUN), "--role", "executor",
         "--timeout-seconds", str(args.timeout_seconds),
         "--max-log-bytes", str(args.max_log_bytes),
         "--max-input-bytes", "4194304",
         "--freeze-input", record["request_file"],
         "--expected-input-sha256", expected,
         "--", *record["argv"]],
        capture_output=True, text=True, encoding="utf-8")
    summary = None
    try:
        summary = json.loads(capture.stdout)
    except json.JSONDecodeError:
        pass
    out = {
        "op": args.op,
        "request_id": args.request_id,
        "input": str(input_path),
        "template_path": str(template_path),
        "request_file": record["request_file"],
        "request_sha256": record["request_sha256"],
        "request_bytes": record["request_bytes"],
        "input_argv_positions": positions,
        "argv": record["argv"],
        "capture_exit": capture.returncode,
        "capture": summary,
        "capture_stderr": capture.stderr.strip(),
    }
    ledger = RECORDER / "native-calls.jsonl"
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(out, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({
        "request_id": args.request_id,
        "request_sha256": record["request_sha256"],
        "request_bytes": record["request_bytes"],
        "capture_exit": capture.returncode,
        "child_started": (summary or {}).get("child_started"),
        "exit_code": (summary or {}).get("exit_code"),
        "input_complete": (summary or {}).get("input_complete"),
        "output_complete": (summary or {}).get("output_complete"),
        "capture_id": (summary or {}).get("capture_id"),
        "stdout_artifact": (summary or {}).get("stdout_artifact"),
        "stderr_artifact": (summary or {}).get("stderr_artifact"),
        "warnings": (summary or {}).get("warnings"),
    }, ensure_ascii=False))
    return 0 if capture.returncode == 0 else capture.returncode


if __name__ == "__main__":
    raise SystemExit(main())
