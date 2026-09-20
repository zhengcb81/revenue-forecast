"""Record the attempt-local isolated interpreter (read-only diagnostic, no product import).

Writes, into <out>/:
  venv_probe.json   absolute interpreter path, sha256, version/platform, isolation statement

Usage:
  python -X utf8 -B venv_probe.py --out <dir> --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import sys


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt_root)
    interp = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    os.makedirs(args.out, exist_ok=True)
    doc = {
        "attempt_root": attempt,
        "venv_interpreter_path": interp,
        "venv_interpreter_exists": os.path.isfile(interp),
        "venv_interpreter_sha256": sha256(interp) if os.path.isfile(interp) else None,
        "running_interpreter": sys.executable,
        "running_interpreter_is_the_venv": os.path.normcase(os.path.abspath(sys.executable))
                                            == os.path.normcase(interp),
        "python_version": sys.version,
        "platform": platform.platform(),
        "isolation": ("attempt-local venv created with `python -m venv` from the I-00-A template venv; "
                      "the global Miniconda interpreter is never used for a card command"),
        "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    out = os.path.join(args.out, "venv_probe.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("venv interpreter", interp)
    print("exists", doc["venv_interpreter_exists"], "sha256", doc["venv_interpreter_sha256"])
    print("running interpreter is the venv", doc["running_interpreter_is_the_venv"])
    print("python", doc["python_version"].splitlines()[0])
    print("written", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
