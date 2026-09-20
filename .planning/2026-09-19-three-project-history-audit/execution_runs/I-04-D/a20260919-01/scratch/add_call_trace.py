"""Insert (and later remove) a call-trace into the generated protocol.

Writes one line per instrumented method into $I04D_CALL_TRACE so a stuck/absent code
path can be located exactly instead of inferred.
"""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

MARKER = '''_HOOKS: "_Hooks | None" = None
'''

TRACER = '''def _i04d_call(name: str, **fields: Any) -> None:
    """Diagnostic call trace; inert unless I04D_CALL_TRACE names a file."""
    path = os.environ.get("I04D_CALL_TRACE")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{name}|{os.getpid()}|{time.monotonic():.4f}|{fields}\\n")
    except OSError:
        pass


_HOOKS: "_Hooks | None" = None
'''

text = PATH.read_text(encoding="utf-8")
if "_i04d_call" in text:
    print("tracer already present")
    sys.exit(0)
if MARKER not in text:
    print("MARKER NOT FOUND")
    sys.exit(1)
text = text.replace(MARKER, TRACER, 1)

INSERTS = [
    (
        '''    def __enter__(self) -> "PausedWorkerScope":
        if not self.enabled:''',
        '''    def __enter__(self) -> "PausedWorkerScope":
        _i04d_call("__enter__", lease_id=self.lease_id, enabled=self.enabled)
        if not self.enabled:''',
    ),
    (
        '''    def _enter_locked(self) -> None:
        remaining = self._request_remaining()''',
        '''    def _enter_locked(self) -> None:
        _i04d_call("_enter_locked")
        remaining = self._request_remaining()''',
    ),
    (
        '''        status = self._worker_status(remaining)
        state = _read_pause_state(self.root)''',
        '''        try:
            status = self._worker_status(remaining)
        except BaseException as exc:
            _i04d_call("_worker_status_raised", kind=type(exc).__name__, detail=str(exc)[:200])
            raise
        _i04d_call("_worker_status_ok", desired=status.get("desired_state"))
        state = _read_pause_state(self.root)''',
    ),
    (
        '''    def _dispatch_locked(
        self,
        state: _LeaseState,
        live: list[dict[str, Any]],
        *,
        status: dict[str, Any],
        probe_timeout: float,
    ) -> None:
        desired = status.get("desired_state")''',
        '''    def _dispatch_locked(
        self,
        state: _LeaseState,
        live: list[dict[str, Any]],
        *,
        status: dict[str, Any],
        probe_timeout: float,
    ) -> None:
        desired = status.get("desired_state")
        _i04d_call("_dispatch_locked", desired=desired, live=len(live), entries=len(state.entries))''',
    ),
    (
        '''    def _fresh_cycle_locked(
        self, state: _LeaseState, live: list[dict[str, Any]], *, resume_required: bool
    ) -> None:''',
        '''    def _fresh_cycle_locked(
        self, state: _LeaseState, live: list[dict[str, Any]], *, resume_required: bool
    ) -> None:
        _i04d_call("_fresh_cycle_locked", live=len(live))''',
    ),
    (
        '''    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        # I-04-A D5: the pause outcome is reported even when no cleanup is owed.''',
        '''    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        _i04d_call("__exit__", action=self.action, lease_held=self.lease_held)
        # I-04-A D5: the pause outcome is reported even when no cleanup is owed.''',
    ),
]
for old, new in INSERTS:
    if old not in text:
        print(f"INSERT PATTERN NOT FOUND:\n{old[:120]}")
        sys.exit(1)
    text = text.replace(old, new, 1)

PATH.write_text(text, encoding="utf-8")
print("call tracer installed in the patcher")

SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)
sched = SCHED.read_text(encoding="utf-8")
OLD = '''        env["I04D_HOOK_DIR"] = str(self.dir)
'''
NEW = '''        env["I04D_HOOK_DIR"] = str(self.dir)
        if os.environ.get("I04D_CALL_TRACE_DIR"):
            env["I04D_CALL_TRACE"] = str(
                Path(os.environ["I04D_CALL_TRACE_DIR"]) / f"calls.{tag}.txt"
            )
'''
if OLD not in sched:
    print("SCHED PATTERN NOT FOUND")
    sys.exit(1)
SCHED.write_text(sched.replace(OLD, NEW, 1), encoding="utf-8")
print("participant call tracing enabled")
