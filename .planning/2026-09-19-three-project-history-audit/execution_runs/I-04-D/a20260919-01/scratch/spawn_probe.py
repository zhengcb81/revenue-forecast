"""Run the probe body EXACTLY the way the scheduler spawns a participant.

Redirects stdout/stderr to FILES (not pipes), uses the attempt's venv python, sets
I04D_HOOK_DIR to the case dir, and records everything the process writes.
"""

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
CASE = ATTEMPT / "scratch" / "spawn-probe"
if CASE.exists():
    shutil.rmtree(CASE)
(CASE / "wiki" / ".source_catalog").mkdir(parents=True)
state = CASE / "worker_state.json"
state.write_text(json.dumps({"desired_state": "enabled", "runtime_state": "running"}), encoding="utf-8")
journal = CASE / "worker.jsonl"
journal.write_text("", encoding="utf-8")

PROBE = CASE / "probe.py"
PROBE.write_text(
    f'''
import json, os, sys, time, traceback
from pathlib import Path
sys.path.insert(0, r"{SCRIPTS}")
import fetch_filing as ff

HERE = Path(__file__).resolve().parent
log = open(HERE / "probe.log", "w", encoding="utf-8")
def note(*parts):
    log.write(" ".join(str(p) for p in parts) + "\\n")
    log.flush()

note("module", ff.__file__)
note("hooks", os.environ.get("I04D_HOOKS"), "dir", os.environ.get("I04D_HOOK_DIR"))
try:
    scope = ff.PausedWorkerScope(
        root=HERE / "wiki",
        command_prefix=[sys.executable, "-X", "utf8", "-B", r"{SCRIPTS / 'i04d_fake_worker.py'}"],
        enabled=True,
        graceful_timeout_seconds=0.2,
        resume_wait_seconds=0.2,
        deadline=time.monotonic() + 900,
        stats=ff._normalize_stats({{}}),
    )
    note("scope made")
    with scope:
        note("inside scope, action=", scope.action)
    note("after scope, action=", scope.action)
except BaseException as exc:
    note("RAISED", type(exc).__name__, str(exc)[:400])
    note(traceback.format_exc())
log.close()
''',
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

stdout_handle = (CASE / "stdout.A.txt").open("wb")
stderr_handle = (CASE / "stderr.A.txt").open("wb")
proc = subprocess.Popen(
    [str(PY), "-X", "utf8", "-B", str(PROBE)],
    env=env,
    cwd=str(ISO),
    stdin=subprocess.DEVNULL,
    stdout=stdout_handle,
    stderr=stderr_handle,
)
gate = CASE / "gate.enter-complete.A.reached"
limit = time.monotonic() + 20
while time.monotonic() < limit and not gate.exists():
    time.sleep(0.01)
print("gate reached:", gate.exists(), "alive:", proc.poll() is None)
if gate.exists():
    (CASE / "gate.enter-complete.A.fence").write_text("go", encoding="utf-8")
try:
    rc = proc.wait(timeout=60)
except subprocess.TimeoutExpired:
    proc.kill()
    rc = proc.wait()
    print("KILLED")
stdout_handle.close()
stderr_handle.close()
print("rc:", rc)
for name in ("probe.log", "calls.txt", "stderr.A.txt"):
    path = CASE / name
    print(f"--- {name} ---")
    print(path.read_text(encoding="utf-8", errors="replace")[:2500] if path.exists() else "<absent>")
print("catalog:", sorted(p.name for p in (CASE / "wiki" / ".source_catalog").iterdir()))
