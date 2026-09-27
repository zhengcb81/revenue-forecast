"""RF-RATCHET-REST-B family runner — runs the frozen F0..F9 family inventory against ONE
tree, with identical commands for the BEFORE (pristine) and AFTER (refactored) runs.

Usage:
  python -X utf8 -B run_families.py --root <tree> --label <label> --outdir <dir>

Writes into <outdir>:
  <id>_stdout.txt   raw pytest stdout+stderr (UTF-8, no BOM)
  <id>_rc.txt       process exit code
  summary.json      [{id, rc, tail}] for comparison

Environment per run (identical both phases): PYTHONDONTWRITEBYTECODE=1, PYTHONUTF8=1,
PYTHONIOENCODING=utf-8, PYTHONPATH=<root>\scripts;<root>\tests, pytest always
`-X utf8 -B -m pytest -p no:cacheprovider -q --no-header --basetemp %TEMP%\rf-rest-b\bt_<label>_<id>`
with cwd=<root>. F2 additionally sets RF_IMPORT_ROOT=<root>.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PY = r"C:\Miniconda\python.exe"
TEMP_BASE = Path(os.environ.get("TEMP", r"C:\Temp")) / "rf-rest-b"
I08C = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
            r"\execution_runs\I-08-C\a20260919-01\test_i08c_consumer_rejection.py")

B1_BATTERY = [
    "test_attestation.py",
    "test_publication_pipeline.py",
    "test_publication_registry.py",
    "test_zr701_f1_draft_formal.py",
    "test_zr705_draft_formal_swap.py",
    "test_zr710_publication_txn.py",
    "test_output_report.py",
    "test_recognition_bridge.py",
    "test_zr704_validate_only_gate.py",
    "test_fc905b_trusted_receipt.py",
    "test_zr702_schema_source_of_truth.py",
]
MODEL_BATTERY = [
    "test_model_registry_contract.py",
    "test_model_economic_guardrails.py",
    "test_model_extensions.py",
    "test_model_extensions_anchor.py",
    "test_model_integration_bounds.py",
]

FAMILIES = [
    {"id": "F0_ratchet", "files": ["tools/tests/test_complexity_ratchet.py"]},
    {"id": "F1_b1battery", "files": [f"tests/{f}" for f in B1_BATTERY]},
    {"id": "F2_i08c13", "files": [str(I08C)], "rf_import_root": True},
    {"id": "F3_modelbattery", "files": [f"tests/{f}" for f in MODEL_BATTERY]},
    {"id": "F5_golden", "files": ["tests/test_golden_behavior_lock.py"]},
    {"id": "F6_needles", "files": [
        "tests/test_skill_documentation.py",
        "tests/test_structure_targets.py",
        "tests/test_input_construction_consistency.py",
    ]},
    {"id": "F7_models", "files": ["tests/test_models.py"]},
    {"id": "F8_adversarial", "files": [
        "tests/adversarial/test_anchor_attacks.py",
        "tests/adversarial/test_receipt_attacks.py",
    ]},
    {"id": "F9_backtest", "files": ["tests/test_backtest.py"]},
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--only", default="", help="comma-separated family ids (default all)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    only = {s for s in args.only.split(",") if s}

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(root / "scripts") + os.pathsep + str(root / "tests")
    env.pop("RF_IMPORT_ROOT", None)

    summary = []
    for fam in FAMILIES:
        if only and fam["id"] not in only:
            continue
        bt = TEMP_BASE / f"bt_{args.label}_{fam['id']}"
        bt.mkdir(parents=True, exist_ok=True)
        fam_env = dict(env)
        if fam.get("rf_import_root"):
            fam_env["RF_IMPORT_ROOT"] = str(root)
        argv = [PY, "-X", "utf8", "-B", "-m", "pytest",
                "-p", "no:cacheprovider", "-q", "--no-header",
                f"--basetemp={bt}"] + fam["files"]
        proc = subprocess.run(argv, cwd=str(root), env=fam_env,
                              capture_output=True, timeout=3600)
        out = (proc.stdout + proc.stderr).decode("utf-8", "replace")
        (outdir / f"{fam['id']}_stdout.txt").write_text(out, encoding="utf-8")
        (outdir / f"{fam['id']}_rc.txt").write_text(str(proc.returncode) + "\n", encoding="ascii")
        tail = "\n".join(out.splitlines()[-4:])
        summary.append({"id": fam["id"], "rc": proc.returncode, "files": fam["files"], "tail": tail})
        print(f"{fam['id']:20s} rc={proc.returncode}")
        for line in tail.splitlines():
            print(f"    {line}")
    (outdir / "summary.json").write_text(
        json.dumps({"label": args.label, "root": str(root), "families": summary},
                   indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
