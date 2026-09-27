"""WU-104: v1 behavior characterization — golden trace pack (CHR-01..04).

Captures canonical traces (exit code + stdout/stderr sha256, duration
excluded) for the declared offline-only CLI targets across the three repos.
A second run is diffed against the golden pack; any output/exit change or a
removed candidate fails the gate.  known_bad behaviors must have a RED owner
before Phase 2 may start.

All targets are offline invocations (--help / doctor with CI=true); the
harness never touches real roots, network, parser or LLM (CHR-04).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parents[1]
DEFAULT_GOLDEN = PLAN_DIR / "baselines" / "WU-104-trace-golden.json"

REPOS = {
    "revenue": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
    "wiki": Path(r"C:\Users\郑曾波\Projects\company-wiki"),
}

# Declared offline-only trace targets (CHR-04 allowlist).
TRACE_TARGETS = [
    {"name": "wiki-config-doctor", "repo": "wiki", "offline": True,
     "argv": ["python", "scripts/config_doctor.py"],
     "env": {"CI": "true", "PYTHONPATH": "src"}},
    {"name": "wiki-snapshot-help", "repo": "wiki", "offline": True,
     "argv": ["python", "scripts/snapshot_manifest.py", "--help"]},
    {"name": "filing-fetch-help", "repo": "filing", "offline": True,
     "argv": ["python", "scripts/fetch_filing.py", "--help"]},
    {"name": "revenue-client-help", "repo": "revenue", "offline": True,
     "argv": ["python", "scripts/filing_fetch_client.py", "--help"]},
    {"name": "revenue-forecast-help", "repo": "revenue", "offline": True,
     "argv": ["python", "scripts/revenue_forecast.py", "--help"]},
]


@dataclass
class TraceResult:
    exit_code: int
    stdout_sha256: str
    stderr_sha256: str
    duration_ms: int


def canonical_trace(trace: TraceResult) -> str:
    """Duration excluded so repeated runs compare equal (CHR-01)."""
    return json.dumps(
        {"exit": trace.exit_code, "stdout": trace.stdout_sha256,
         "stderr": trace.stderr_sha256},
        sort_keys=True,
    )


def run_target(target: dict) -> TraceResult:
    repo = REPOS[target["repo"]]
    command = [sys.executable if arg == "python" else arg for arg in target["argv"]]
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    for key, value in (target.get("env") or {}).items():
        env[key] = value
    proc = subprocess.run(
        command, cwd=repo, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=300, check=False,
    )
    return TraceResult(
        exit_code=proc.returncode,
        stdout_sha256=hashlib.sha256(proc.stdout.encode("utf-8")).hexdigest(),
        stderr_sha256=hashlib.sha256(proc.stderr.encode("utf-8")).hexdigest(),
        duration_ms=0,  # not part of the canonical trace
    )


def capture_golden() -> dict:
    pack: dict = {}
    for target in TRACE_TARGETS:
        trace = run_target(target)
        pack[target["name"]] = json.loads(canonical_trace(trace))
    return dict(sorted(pack.items()))


def trace_diff(golden: dict, current: dict) -> list[str]:
    problems: list[str] = []
    # CHR-02 both directions: a removed candidate AND an unexpected new one
    for name in sorted(set(golden) | set(current)):
        if name not in golden:
            problems.append(f"unexpected trace candidate: {name}")
            continue
        if name not in current:
            problems.append(f"trace candidate missing: {name}")
            continue
        expected = golden[name]
        actual = current[name]
        for key in ("exit", "stdout", "stderr"):
            if expected.get(key) != actual.get(key):
                problems.append(
                    f"{name}: {key} {str(actual.get(key))[:12]} != "
                    f"golden {str(expected.get(key))[:12]}"
                )
    return problems


def check_known_bad_owners(known_bad: dict, mapping: dict) -> list[str]:
    problems: list[str] = []
    for kb_id in sorted(known_bad):
        if kb_id not in mapping:
            problems.append(
                f"known_bad {kb_id} ({known_bad[kb_id][:40]}...) has no RED owner "
                "(CHR-03: Phase 2 blocked)"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="WU-104 v1 trace pack")
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true", help="write golden pack")
    group.add_argument("--check", action="store_true", help="diff vs golden")
    group.add_argument("--known-bad", action="store_true",
                       help="validate known_bad owners (CHR-03)")
    args = parser.parse_args()

    if args.capture:
        pack = capture_golden()
        args.golden.parent.mkdir(parents=True, exist_ok=True)
        args.golden.write_text(
            json.dumps(pack, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(f"golden written: {args.golden}")
        for name, entry in pack.items():
            print(f"  {name}: exit={entry['exit']}")
        return 0

    if args.check:
        if not args.golden.is_file():
            print(f"missing golden: {args.golden} (run --capture first)")
            return 1
        golden = json.loads(args.golden.read_text(encoding="utf-8"))
        current = capture_golden()
        problems = trace_diff(golden, current)
        for problem in problems:
            print(f"TRACE-GATE: {problem}")
        if not problems:
            print("OK: all traces identical to golden")
        return 1 if problems else 0

    if args.known_bad:
        known_bad_path = PLAN_DIR / "known_bad.json"
        if not known_bad_path.is_file():
            print(f"missing known_bad registry: {known_bad_path}")
            return 1
        registry = json.loads(known_bad_path.read_text(encoding="utf-8"))
        mapping = registry.get("mapping", {})
        problems = check_known_bad_owners(registry.get("known_bad", {}), mapping)
        for problem in problems:
            print(f"TRACE-GATE: {problem}")
        if not problems:
            print("OK: every known_bad has a RED owner")
        return 1 if problems else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
