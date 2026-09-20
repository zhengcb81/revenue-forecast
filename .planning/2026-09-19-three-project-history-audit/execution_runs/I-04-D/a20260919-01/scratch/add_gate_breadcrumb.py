"""Insert a loud stderr breadcrumb wherever a gate file is created.

Temporary diagnostic: shows exactly which code path publishes the fence.
"""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''            reached = self.dir / f"{base}.reached"
            if not reached.exists():
                reached.write_text("reached", encoding="utf-8")
'''
NEW = '''            reached = self.dir / f"{base}.reached"
            if not reached.exists():
                reached.write_text("reached", encoding="utf-8")
                try:
                    import traceback as _tb

                    sys.stderr.write(
                        f"[i04d] gate {base} published by pid {os.getpid()} at {point}\\n"
                        + "".join(_tb.format_stack()[-6:])
                    )
                    sys.stderr.flush()
                except Exception:  # noqa: BLE001
                    pass
'''
text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("gate breadcrumb installed")
