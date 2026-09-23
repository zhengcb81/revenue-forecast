"""I-07-C stage runner: executes the PRODUCT's own CLI for one cell/stage and
captures argv, stdout, stderr, raw product rc and a read-only isolated-catalog
dump. The harness itself never scans, never resolves and never writes a row.

  python run_stage.py scan    <cell>
  python run_stage.py resolve <cell>

Inner argv (I-00-B form, frozen in commands.json):
  <iso-python> -X utf8 -B -m company_wiki.source_catalog.cli --config <cfg> scan
  ... resolve --entity <v> --document-kind <k> --as-of-date <d>
cwd = <cell>/cwroot (same as fetch_filing builds it).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from i07c_common import AS_OF, ATT, CW, EVID, dump_catalog, read_json, write_json

STAGES = ("scan", "resolve")


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in STAGES:
        print(f"usage: run_stage.py <{'|'.join(STAGES)}> <cell>", file=sys.stderr)
        return 1
    stage, cell = sys.argv[1], sys.argv[2]
    case_dir = Path(os.environ["TEMP"]) / "i07c" / "cells" / cell
    cwroot = case_dir / "cwroot"
    cfg = cwroot / "config" / "source_catalog.yaml"
    if not cfg.is_file():
        print(f"missing isolated config: {cfg}", file=sys.stderr)
        return 1

    argv = [sys.executable, "-X", "utf8", "-B", "-m",
            "company_wiki.source_catalog.cli", "--config", str(cfg)]
    if stage == "scan":
        argv.append("scan")
        # next free scanN dir: superseded run evidence is never overwritten
        idx = len(list((EVID / cell).glob("scan[0-9]*"))) + 1
        out_dir = EVID / cell / f"scan{idx}"
        run_one("scan", argv, cwroot, out_dir, None)
        return 0

    req = read_json(case_dir / "resolve_request.json")
    requests = req["requests"] if isinstance(req, dict) else req
    base = len(list((EVID / cell).glob("resolve[0-9]*")))
    for i, r in enumerate(requests, start=base + 1):
        argv = [sys.executable, "-X", "utf8", "-B", "-m",
                "company_wiki.source_catalog.cli", "--config", str(cfg),
                "resolve", "--entity", r["entity"],
                "--document-kind", r["document_kind"],
                "--as-of-date", r.get("as_of_date", AS_OF)]
        out_dir = EVID / cell / f"resolve{i}"
        run_one("resolve", argv, cwroot, out_dir, r)
    return 0


def run_one(stage: str, argv: list[str], cwroot: Path, out_dir: Path,
            request) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(CW / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    started = time.time()
    proc = subprocess.run(argv, cwd=str(cwroot), env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=560)
    elapsed = time.time() - started
    (out_dir / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (out_dir / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
    write_json(out_dir / "argv.json", {
        "stage": stage, "argv": argv, "cwd": str(cwroot),
        "pythonpath": str(CW / "src"),
        "request": request,
        "elapsed_seconds": round(elapsed, 3),
    })
    write_json(out_dir / "product_rc.json",
               {"stage": stage, "product_returncode": proc.returncode,
                "elapsed_seconds": round(elapsed, 3)})
    write_json(out_dir / "catalog_dump.json", dump_catalog(cwroot))
    print(json.dumps({"cell": out_dir.parent.name, "stage": stage,
                      "product_returncode": proc.returncode,
                      "elapsed_seconds": round(elapsed, 3)}))


if __name__ == "__main__":
    sys.exit(main())
