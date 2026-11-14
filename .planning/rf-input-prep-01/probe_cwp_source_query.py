"""Probe the CWP source query CLI directly with one JSON request on stdin."""
from __future__ import annotations

import json
import os
import subprocess
import sys

WIKI = r"C:\Users\郑曾波\Projects\company-wiki"


def run(request: dict) -> dict:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = WIKI + r"\src"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, "-m", "company_wiki.source_catalog.source_query_cli",
         "--config", WIKI + r"\config\source_catalog.yaml"],
        input=json.dumps(request, ensure_ascii=False).encode("utf-8"),
        capture_output=True, cwd=WIKI, env=env,
    )
    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        payload = {"_raw_stdout": out[:4000]}
    return {"exit": proc.returncode, "payload": payload, "stderr": err[:2000]}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as handle:
            request = json.load(handle)
    else:
        request = json.load(sys.stdin)
    print(json.dumps(run(request), ensure_ascii=False, indent=2))
