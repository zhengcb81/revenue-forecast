"""Minimal reproduction of the F-L8d scheduling problem, with full logging."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "filing-fetch"
PY = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"
CASE = ATTEMPT / "scratch" / "repro-l8d"
import shutil

if CASE.exists():
    shutil.rmtree(CASE)
(CASE / "wiki" / ".source_catalog").mkdir(parents=True)
state = CASE / "worker_state.json"
state.write_text(json.dumps({"desired_state": "enabled", "runtime_state": "running"}), encoding="utf-8")
journal = CASE / "worker.jsonl"
journal.write_text("", encoding="utf-8")

env = dict(**{k: v for k, v in __import__("os").environ.items()})
env["PYTHONUTF8"] = "1"
env["I04D_WORKER_STATE"] = str(state)
env["I04D_WORKER_JOURNAL"] = str(journal)
env["I04D_HOOK_DIR"] = str(CASE)
env["I04D_HOOK_TAG"] = "A"
env["I04D_HOOKS"] = "gate:release-read@A"

argv = [
    str(PY), "-X", "utf8", "-B", str(ISO / "scripts" / "i04d_participant.py"),
    "--case", "REPRO", "--tag", "A",
    "--root", str(CASE / "wiki"),
    "--report", str(CASE / "report.A.json"),
    "--state", str(state),
    "--journal", str(journal),
    "--request-budget", "900", "--graceful", "0.2", "--resume-wait", "0.2",
]
print("argv:", argv)
proc = subprocess.Popen(argv, env=env, cwd=str(ISO),
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
gate = CASE / "gate.release-read.A.reached"
limit = time.monotonic() + 20
while time.monotonic() < limit and not gate.exists():
    time.sleep(0.01)
print("gate reached:", gate.exists())
catalog = CASE / "wiki" / ".source_catalog"
print("catalog listing:", sorted(x.name for x in catalog.iterdir()))
ref = catalog / "filing_fetch_pause.refcount"
print("refcount exists:", ref.exists(), "bytes:", ref.stat().st_size if ref.exists() else None)
if ref.exists():
    print("refcount text:", ref.read_text(encoding="utf-8")[:400])
if gate.exists():
    (CASE / "gate.release-read.A.fence").write_text("go", encoding="utf-8")
out, err = proc.communicate(timeout=60)
print("rc:", proc.returncode)
print("stdout:", out[:400])
print("stderr:", err[:2000])
print("report:", (CASE / "report.A.json").read_text(encoding="utf-8")[:600] if (CASE / "report.A.json").exists() else "<none>")
print("final catalog:", sorted(x.name for x in catalog.iterdir()))
