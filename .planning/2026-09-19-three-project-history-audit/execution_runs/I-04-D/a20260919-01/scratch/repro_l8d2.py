"""Minimal repro with the NEW gate scheme (arrive:release-read + fence gate)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "filing-fetch"
PY = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"
CASE = ATTEMPT / "scratch" / "repro-l8d2"
if CASE.exists():
    shutil.rmtree(CASE)
(CASE / "wiki" / ".source_catalog").mkdir(parents=True)
state = CASE / "worker_state.json"
state.write_text(json.dumps({"desired_state": "enabled", "runtime_state": "running"}), encoding="utf-8")
journal = CASE / "worker.jsonl"
journal.write_text("", encoding="utf-8")

env = dict(os.environ)
env["PYTHONUTF8"] = "1"
env["I04D_WORKER_STATE"] = str(state)
env["I04D_WORKER_JOURNAL"] = str(journal)
env["I04D_HOOK_DIR"] = str(CASE)
env["I04D_HOOK_TAG"] = "A"
env["I04D_HOOKS"] = "arrive:release-read@A,gate:release-read-fence@A"
env["I04D_HOOK_TRACE"] = str(CASE / "hooks.A.txt")

argv = [
    str(PY), "-X", "utf8", "-B", str(ISO / "scripts" / "i04d_participant.py"),
    "--case", "REPRO", "--tag", "A",
    "--root", str(CASE / "wiki"),
    "--report", str(CASE / "report.A.json"),
    "--state", str(state), "--journal", str(journal),
    "--request-budget", "900", "--graceful", "0.2", "--resume-wait", "0.2",
]
proc = subprocess.Popen(argv, env=env, cwd=str(ISO),
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
arrival = CASE / "arrive.release-read.A"
limit = time.monotonic() + 20
while time.monotonic() < limit and not arrival.exists():
    time.sleep(0.005)
print("arrival:", arrival.exists())
time.sleep(0.15)
catalog = CASE / "wiki" / ".source_catalog"
print("catalog listing:", sorted(x.name for x in catalog.iterdir()))
ref = catalog / "filing_fetch_pause.refcount"
print("refcount exists:", ref.exists())
if ref.exists():
    print("refcount text:", ref.read_text(encoding="utf-8")[:300])
print("gate fence needed:", (CASE / "gate.release-read-fence.A.reached").exists())
(CASE / "gate.release-read-fence.A.fence").write_text("go", encoding="utf-8")
out, err = proc.communicate(timeout=60)
print("rc:", proc.returncode)
print("stderr:", err[:1200])
print("hook trace:")
print((CASE / "hooks.A.txt").read_text(encoding="utf-8") if (CASE / "hooks.A.txt").exists() else "<none>")
print("final catalog:", sorted(x.name for x in catalog.iterdir()))
