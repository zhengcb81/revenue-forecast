"""Run the full main+stress native chain (validate, compute/render, snapshot)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
DELIVERY = WORKDIR / "delivery" / "w09"
PYTHON = Path(r"C:/Miniconda/python.exe")
RUN_NATIVE = DELIVERY / "tools" / "run_native.py"
REGISTRY = DELIVERY / "registry" / "publications.jsonl"

VERSIONS = {"main": "w09-rf-research-20261023-main-v1",
            "stress": "w09-rf-research-20261023-stress-v1"}


def run(args: list[str]) -> int:
    print("+", " ".join(args[-6:]))
    result = subprocess.run(args, cwd=WORKDIR, capture_output=True, text=True,
                            encoding="utf-8")
    print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def main() -> int:
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(REGISTRY)
    os.environ["PYTHONUTF8"] = "1"
    codes = []
    for which in ("main", "stress"):
        source = f"delivery/w09/forecast/{which}-input.json"
        common = ["--input", source]
        codes.append(run([str(PYTHON), str(RUN_NATIVE), "--op", "validate", *common,
                          "--request-id", f"w09-{which}-validate",
                          "--purpose", f"W09 {which} input: native validate (draft mode)"]))
        codes.append(run([str(PYTHON), str(RUN_NATIVE), "--op", "compute", *common,
                          "--request-id", f"w09-{which}-compute",
                          "--purpose", f"W09 {which} input: native compute + render",
                          "--output", f"delivery/w09/forecast/{which}-forecast.json",
                          "--markdown", f"delivery/w09/forecast/{which}-forecast.md"]))
        codes.append(run([str(PYTHON), str(RUN_NATIVE), "--op", "snapshot", *common,
                          "--request-id", f"w09-{which}-snapshot",
                          "--purpose", f"W09 {which} input: immutable snapshot create",
                          "--version", VERSIONS[which],
                          "--output", f"delivery/w09/snapshots/{which}-v1.json"]))
    print(json.dumps({"exit_codes": codes, "all_zero": all(c == 0 for c in codes)}))
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
