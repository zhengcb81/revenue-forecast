"""I-14-C: drive the PRODUCT'S OWN CLI entry point for case E5.

r1 review finding F-I14C-03: the r1 "CLI exit" was a harness-local re-implementation,
so the real exit was never executed.  In particular ``cli.py:866
config_path = args.config.resolve(strict=True)`` sits OUTSIDE ``main``'s try/except, so an
unreadable ``--config`` escaped as a bare interpreter traceback.

This driver invokes the real module entry point as a subprocess:

    python -m company_wiki.source_catalog.cli --config <missing path> status

with ``--config`` pointing at a path that does NOT exist, so the CLI raises at
config-resolution time and **never creates or opens a catalog**.  The driver asserts that
no ``catalog.sqlite3`` appeared under the scratch project root.

Shapes:
    E5a  the missing file name is credential-shaped  (token=SYNTHETIC_AUDIT_TOKEN.yaml)
    E5b  the missing file name is a bare marker      (SYNTHETIC_AUDIT_TOKEN.yaml)
    E5c  argparse failure                            (marker argv value + unknown flag)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from run_guard import REFUSAL_EXIT, guard_run_dir

MARKER = "SYNTHETIC_AUDIT_TOKEN"

SHAPES = {
    "E5a": ("credential-shaped-config-name", "config", "token=" + MARKER + ".yaml"),
    "E5b": ("bare-marker-config-name", "config", MARKER + ".yaml"),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shape", required=True, choices=sorted(SHAPES) + ["E5c"])
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--src", required=True)
    parser.add_argument("--python", required=True)
    args = parser.parse_args(argv)

    run_dir = guard_run_dir(args.run_dir)
    if run_dir is None:
        return REFUSAL_EXIT
    project = run_dir / "scratch-project"
    (project / "config").mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = str(Path(args.src).resolve())

    if args.shape == "E5c":
        # argparse's own error path: echoes argv, is NOT the except-Exception handler.
        cli_argv = [
            args.python, "-X", "utf8", "-B", "-m", "company_wiki.source_catalog.cli",
            "--config", str(project / "config" / "source_catalog.yaml"),
            "status", "--definitely-not-a-flag", "token=" + MARKER,
        ]
    else:
        _label, subdir, filename = SHAPES[args.shape]
        missing = project / subdir / filename        # deliberately never created
        cli_argv = [
            args.python, "-X", "utf8", "-B", "-m", "company_wiki.source_catalog.cli",
            "--config", str(missing), "status",
        ]

    proc = subprocess.run(cli_argv, cwd=str(project), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    stdout = proc.stdout.decode("utf-8", "replace")
    stderr = proc.stderr.decode("utf-8", "replace")
    (run_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(stderr, encoding="utf-8")

    catalogs = [str(p) for p in project.rglob("catalog.sqlite3")]
    result = {
        "shape": args.shape,
        "argv": cli_argv,
        "cwd": str(project),
        "returncode": proc.returncode,
        "marker_hits": {
            "stdout": stdout.count(MARKER),
            "stderr": stderr.count(MARKER),
        },
        "bare_traceback_on_stderr": "Traceback (most recent call last)" in stderr,
        "structured_envelope_on_stderr": '"status": "failed"' in stderr,
        "catalogs_created": catalogs,
        "stderr_head": stderr[:600],
    }
    (run_dir / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
