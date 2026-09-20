"""Set I04D_HOOK_TRACE for every spawned participant (diagnostic mode only)."""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

OLD = """        env["I04D_HOOK_DIR"] = str(self.dir)
"""
NEW = """        env["I04D_HOOK_DIR"] = str(self.dir)
        if os.environ.get("I04D_HOOK_TRACE_DIR"):
            env["I04D_HOOK_TRACE"] = str(
                Path(os.environ["I04D_HOOK_TRACE_DIR"]) / f"hooks.{tag}.txt"
            )
            env.pop("I04D_HOOK_TRACE", None) if False else None
            env["I04D_HOOK_TRACE"] = str(
                Path(os.environ["I04D_HOOK_TRACE_DIR"]) / f"hooks.{tag}.txt"
            )
"""

text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("participant hook tracing enabled")
