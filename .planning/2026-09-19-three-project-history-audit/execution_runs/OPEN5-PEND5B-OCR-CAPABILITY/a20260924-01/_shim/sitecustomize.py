"""Process-local sandbox shim for OPEN5-PEND5B-OCR-CAPABILITY (a20260924-01).

Why: the DSH file sandbox turns os.mkdir(mode=0o700) / tempfile.mkdtemp()
directories into directories the owner cannot write (PermissionError [Errno 13]),
reproduced across multiple cards. pip itself dies with
  "PermissionError [Errno 13] ... pip-unpack-XXXX\\*.whl.metadata"
because tempfile.mkdtemp() calls os.mkdir(dir, 0o700).

Fix: force every os.mkdir mode to 0o777 for this process only.

Activation: PYTHONPATH=<this dir> for the specific python invocation.
NOT a system-level change: no PATH edits, no Windows packages, no writes to
global site-packages. Disabled unless PYTHONPATH points here.
"""
import os as _os

_orig_mkdir = _os.mkdir


def _mkdir(path, mode=0o777, *, dir_fd=None):
    if mode != 0o777:
        mode = 0o777
    return _orig_mkdir(path, mode, dir_fd=dir_fd)


_os.mkdir = _mkdir  # os.makedirs() and tempfile.mkdtemp() resolve this global.
