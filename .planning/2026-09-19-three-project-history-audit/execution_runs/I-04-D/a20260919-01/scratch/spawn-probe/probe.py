
import json, os, sys, time, traceback
from pathlib import Path
sys.path.insert(0, r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts")
import fetch_filing as ff

HERE = Path(__file__).resolve().parent
log = open(HERE / "probe.log", "w", encoding="utf-8")
def note(*parts):
    log.write(" ".join(str(p) for p in parts) + "\n")
    log.flush()

note("module", ff.__file__)
note("hooks", os.environ.get("I04D_HOOKS"), "dir", os.environ.get("I04D_HOOK_DIR"))
try:
    scope = ff.PausedWorkerScope(
        root=HERE / "wiki",
        command_prefix=[sys.executable, "-X", "utf8", "-B", r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_fake_worker.py"],
        enabled=True,
        graceful_timeout_seconds=0.2,
        resume_wait_seconds=0.2,
        deadline=time.monotonic() + 900,
        stats=ff._normalize_stats({}),
    )
    note("scope made")
    with scope:
        note("inside scope, action=", scope.action)
    note("after scope, action=", scope.action)
except BaseException as exc:
    note("RAISED", type(exc).__name__, str(exc)[:400])
    note(traceback.format_exc())
log.close()
