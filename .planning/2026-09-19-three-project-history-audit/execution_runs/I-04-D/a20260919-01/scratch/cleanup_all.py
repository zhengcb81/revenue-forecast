"""Remove every temporary diagnostic from the patcher and the scheduler.

Keeps only the reviewed surface: the protocol, the hook mechanism (gate/arrive/crash)
and the cases.  Also drops the at-lock-attempt hook, which is not needed by any case.
"""

from __future__ import annotations

import pathlib
import re
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)
SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)
PART = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_participant.py"
)

text = PATCHER.read_text(encoding="utf-8")
removals = 0

# 1. call tracer helper
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


'''
if TRACER in text:
    text = text.replace(TRACER, "", 1)
    removals += 1

# 2. hook-level probe + breadcrumb
text, n = re.subn(
    r"        try:\n            root = Path\(context\.get\(\"root\"\) or \"\.\"\)\n(?:.*?\n)*?"
    r"        code = self\.crashes\.get\(point\)\n",
    "        code = self.crashes.get(point)\n",
    text,
    count=1,
)
removals += n

# 3. _i04d_call insertions
text, n = re.subn(r"^ *_i04d_call\([^\n]*\)\n", "", text, flags=re.MULTILINE)
removals += n

# 4. the at-lock-attempt hook (no case needs it)
text, n = re.subn(
    r'^ *_i04d_hook\("at-lock-attempt", root=self\.root, payload=\{"lease_id": self\.lease_id\}\)\n',
    "",
    text,
    flags=re.MULTILINE,
)
removals += n

# 5. worker-status try/except wrapper added for diagnosis
OLD_WRAP = '''        try:
            _i04d_call("worker-status-begin", remaining=remaining)
            status = self._worker_status(remaining)
        except BaseException as exc:
            _i04d_call("_worker_status_raised", kind=type(exc).__name__, detail=str(exc)[:200])
            raise
        _i04d_call("_worker_status_ok", desired=status.get("desired_state"))
        state = _read_pause_state(self.root)'''
NEW_WRAP = '''        status = self._worker_status(remaining)
        state = _read_pause_state(self.root)'''
if OLD_WRAP in text:
    text = text.replace(OLD_WRAP, NEW_WRAP, 1)
    removals += 1

text, n = re.subn(
    r"^ *_i04d_call\([^\n]*\)\n(?: *try:\n)?", "", text, flags=re.MULTILINE
)
removals += n

PATCHER.write_text(text, encoding="utf-8")
print(f"patcher cleaned ({removals} removals); remaining _i04d_call refs: {text.count('_i04d_call')}")

# --- scheduler: drop the call-trace plumbing ---
sched = SCHED.read_text(encoding="utf-8")
sched, n = re.subn(
    r"        if os\.environ\.get\(\"I04D_CALL_TRACE_DIR\"\):\n"
    r"            env\[\"I04D_CALL_TRACE\"\] = str\(\n"
    r"                Path\(os\.environ\[\"I04D_CALL_TRACE_DIR\"\]\) / f\"calls\.\{tag\}\.txt\"\n"
    r"            \)\n",
    "",
    sched,
)
print(f"scheduler call-trace removals: {n}")
SCHED.write_text(sched, encoding="utf-8")

# --- participant: drop the startup breadcrumbs ---
part = PART.read_text(encoding="utf-8")
part, n = re.subn(r"^ *_(?:note|startup)[^\n]*\n", "", part, flags=re.MULTILINE)
part, n2 = re.subn(
    r"    _startup = report_path\.parent / f\"startup\.\{args\.tag\}\.log\"\n\n"
    r"    def _note\(self[^)]*\) -> None:\n"
    r"(?:.*?\n)*?            pass\n\n",
    "",
    part,
)
print(f"participant breadcrumb removals: {n} + {n2}")
PART.write_text(part, encoding="utf-8")
