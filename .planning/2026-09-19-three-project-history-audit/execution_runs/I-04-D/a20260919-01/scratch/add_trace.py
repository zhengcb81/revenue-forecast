"""Add an optional hook trace to the I-04-D patcher's generated hook class."""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = """    def __call__(self, point: str, context: dict[str, Any]) -> None:
        code = self.crashes.get(point)
"""

NEW = '''    def __call__(self, point: str, context: dict[str, Any]) -> None:
        trace = os.environ.get("I04D_HOOK_TRACE")
        if trace:
            try:
                with open(trace, "a", encoding="utf-8") as handle:
                    handle.write(
                        f"{point}|{self.tag}|{time.monotonic():.4f}|"
                        f"{context.get('payload')}\\n"
                    )
            except OSError:
                pass
        code = self.crashes.get(point)
'''

text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("hook tracing installed in the patcher")
