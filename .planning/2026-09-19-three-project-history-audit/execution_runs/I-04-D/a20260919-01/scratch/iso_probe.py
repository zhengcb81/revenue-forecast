"""Isolate the failing hook path: run the patched module in a subprocess and report."""

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
SCRIPTS = ISO / "scripts"
PY = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"
CASE = ATTEMPT / "scratch" / "iso-probe"
if CASE.exists():
    shutil.rmtree(CASE)
(CASE / "wiki" / ".source_catalog").mkdir(parents=True)
state = CASE / "worker_state.json"
state.write_text(json.dumps({"desired_state": "enabled", "runtime_state": "running"}), encoding="utf-8")
journal = CASE / "worker.jsonl"
journal.write_text("", encoding="utf-8")

PROBE = CASE / "probe.py"
PROBE.write_text(
    '''
import json, os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, r"%s")
import fetch_filing as ff

log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe.log"), "w", encoding="utf-8")
def note(*parts):
    log.write(" ".join(str(p) for p in parts) + "\\n")
    log.flush()

note("module", ff.__file__)
note("hook env", os.environ.get("I04D_HOOKS"))
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki")
try:
    scope = ff.PausedWorkerScope(
        root=__import__("pathlib").Path(root),
        command_prefix=[sys.executable, "-X", "utf8", "-B", r"%s"],
        enabled=True,
        graceful_timeout_seconds=0.2,
        resume_wait_seconds=0.2,
        deadline=__import__("time").monotonic() + 900,
        stats=ff._normalize_stats({}),
    )
    note("scope made")
    with scope:
        note("inside scope, action=", scope.action)
    note("after scope, action=", scope.action)
except BaseException as exc:
    note("RAISED", type(exc).__name__, str(exc)[:300])
    note(traceback.format_exc())
log.close()
'''
    % (str(SCRIPTS), str(SCRIPTS / "i04d_fake_worker.py")),
    encoding="utf-8",
)

env = dict(os.environ)
env["PYTHONUTF8"] = "1"
env["I04D_WORKER_STATE"] = str(state)
env["I04D_WORKER_JOURNAL"] = str(journal)
env["I04D_HOOK_DIR"] = str(CASE)
env["I04D_HOOK_TAG"] = "A"
env["I04D_HOOKS"] = "gate:enter-complete@A"
env["I04D_CALL_TRACE"] = str(CASE / "calls.txt")

proc = subprocess.Popen(
    [str(PY), "-X", "utf8", "-B", str(PROBE)],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
gate = CASE / "gate.enter-complete.A.reached"
limit = time.monotonic() + 20
while time.monotonic() < limit and not gate.exists():
    time.sleep(0.01)
print("gate reached within 20s:", gate.exists(), "proc alive:", proc.poll() is None)
if gate.exists():
    (CASE / "gate.enter-complete.A.fence").write_text("go", encoding="utf-8")
try:
    out, err = proc.communicate(timeout=60)
except subprocess.TimeoutExpired:
    proc.kill()
    out, err = proc.communicate()
    print("KILLED after timeout")
print("rc:", proc.returncode)
print("stdout:", out[:500])
print("stderr:", err[:1500])
for name in ("probe.log", "calls.txt"):
    path = CASE / name
    print(f"--- {name} ---")
    print(path.read_text(encoding="utf-8")[:2500] if path.exists() else "<absent>")
print("catalog:", sorted(p.name for p in (CASE / "wiki" / ".source_catalog").iterdir()))
