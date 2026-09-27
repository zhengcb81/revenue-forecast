"""WC-6 stage runner: executes the PRODUCT's own CLI on the probe cell and
captures argv / stdout / stderr / raw product rc / read-only catalog dump.

  python run_stage.py <label> <scan|resolve|cfg01>

Inner argv (I-00-B form):
  <iso-python> -X utf8 -B -m company_wiki.source_catalog.cli --config <cfg> <stage...>
cwd = <cell>/cwroot; PYTHONPATH = <attempt>/iso/cw/src (the code under test).
The harness never scans, never resolves and never writes a catalog row.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from wc6_common import (ATT, CASES, EVID, ISO_SRC, dump_catalog, load_fixture,
                        normalized, read_json, write_json)

STAGES = ("scan", "rescan", "resolve", "cfg01")


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in STAGES:
        print(f"usage: run_stage.py <label> <{'|'.join(STAGES)}>", file=sys.stderr)
        return 2
    label, stage = sys.argv[1], sys.argv[2]
    case_dir = CASES / "probes"
    cwroot = case_dir / "cwroot"
    good_cfg = cwroot / "config" / "source_catalog.yaml"
    bad_cfg = cwroot / "config" / "source_catalog_bad_adapter.yaml"
    cfg = bad_cfg if stage == "cfg01" else good_cfg
    if not cfg.is_file():
        print(f"missing isolated config: {cfg}", file=sys.stderr)
        return 2

    argv = [sys.executable, "-X", "utf8", "-B", "-m",
            "company_wiki.source_catalog.cli", "--config", str(cfg)]
    request = None
    if stage in ("scan", "rescan"):
        # rescan = the SAME product scan argv run a second time on the same cell
        # (idempotency arm: a persisted remediation reason must not be counted as
        # a scan error on re-entry, and must not flap).
        argv.append("scan")
    elif stage == "cfg01":
        argv.append("scan")
    else:
        fx = load_fixture()
        request = {"entity": fx["company_name"],
                   "document_kind": fx["document_kind"],
                   "as_of_date": fx["as_of_date"]}
        argv += ["resolve", "--entity", request["entity"],
                 "--document-kind", request["document_kind"],
                 "--as-of-date", request["as_of_date"]]

    out_dir = EVID / label / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ISO_SRC)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    started = time.time()
    proc = subprocess.run(argv, cwd=str(cwroot), env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=560)
    elapsed = round(time.time() - started, 3)
    (out_dir / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (out_dir / "stderr.txt").write_text(proc.stderr, encoding="utf-8")
    write_json(out_dir / "argv.json", {
        "label": label, "stage": stage, "argv": argv, "cwd": str(cwroot),
        "pythonpath": str(ISO_SRC), "request": request,
        "elapsed_seconds": elapsed,
    })
    write_json(out_dir / "product_rc.json",
               {"stage": stage, "product_returncode": proc.returncode,
                "elapsed_seconds": elapsed})
    dump = dump_catalog(cwroot)
    write_json(out_dir / "catalog_dump.json", dump)
    write_json(out_dir / "normalized.json", normalized(dump))
    print(json.dumps({"label": label, "stage": stage,
                      "product_returncode": proc.returncode,
                      "elapsed_seconds": elapsed}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
