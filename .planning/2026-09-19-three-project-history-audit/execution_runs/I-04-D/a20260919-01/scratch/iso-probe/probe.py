
import json, os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts")
import fetch_filing as ff

log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe.log"), "w", encoding="utf-8")
def note(*parts):
    log.write(" ".join(str(p) for p in parts) + "\n")
    log.flush()

note("module", ff.__file__)
note("hook env", os.environ.get("I04D_HOOKS"))
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki")
try:
    scope = ff.PausedWorkerScope(
        root=__import__("pathlib").Path(root),
        command_prefix=[sys.executable, "-X", "utf8", "-B", r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_fake_worker.py"],
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
