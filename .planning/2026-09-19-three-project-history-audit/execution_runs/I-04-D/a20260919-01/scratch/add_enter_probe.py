"""Compare the working repro against the scheduler run: instrument __enter__ end-to-end."""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''            _i04d_hook("at-lock-attempt", root=self.root, payload={"lease_id": self.lease_id})
            with self._lock as locked:
                _i04d_hook("enter-acquired", root=self.root, payload={"lease_id": self.lease_id})
                locked._scope._enter_locked()
'''
NEW = '''            _i04d_hook("at-lock-attempt", root=self.root, payload={"lease_id": self.lease_id})
            _i04d_call("before-lock")
            with self._lock as locked:
                _i04d_call("lock-held")
                _i04d_hook("enter-acquired", root=self.root, payload={"lease_id": self.lease_id})
                locked._scope._enter_locked()
            _i04d_call("enter-returned", action=self.action)
'''
text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("enter instrumentation installed")
