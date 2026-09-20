"""Breadcrumbs around the lock acquisition and the worker-status call."""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''        path = _lease_lock_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()'''
NEW = '''        _i04d_call("acquire-lock-begin", path=str(_lease_lock_path(self.root)), budget=budget)
        path = _lease_lock_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        _i04d_call("acquire-lock-mkdir-ok", exists=path.parent.is_dir())
        started = time.monotonic()'''
text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("LOCK PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = '''        handle = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
        try:'''
NEW2 = '''        handle = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
        _i04d_call("acquire-lock-opened", handle=handle)
        try:'''
if OLD2 not in text:
    print("OPEN PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)

OLD3 = '''                if _try_lock_byte(handle):
                    break'''
NEW3 = '''                locked_now = _try_lock_byte(handle)
                _i04d_call("acquire-lock-try", got=locked_now)
                if locked_now:
                    break'''
if OLD3 not in text:
    print("TRY PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD3, NEW3, 1)

OLD4 = '''        try:
            status = self._worker_status(remaining)
        except BaseException as exc:'''
NEW4 = '''        try:
            _i04d_call("worker-status-begin", remaining=remaining)
            status = self._worker_status(remaining)
        except BaseException as exc:'''
if OLD4 not in text:
    print("STATUS PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD4, NEW4, 1)
PATH.write_text(text, encoding="utf-8")
print("lock/status breadcrumbs installed")
