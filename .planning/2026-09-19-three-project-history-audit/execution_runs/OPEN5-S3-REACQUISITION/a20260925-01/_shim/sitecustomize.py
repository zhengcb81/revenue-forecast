"""OPEN5-S3-REACQUISITION · process-local mkdir shim (copy of the PEND-5b shim
mechanism, written INSIDE this attempt; their _shim directory is only read).

Why: the DSH file sandbox turns os.mkdir(mode=0o700)/tempfile.mkdtemp()
directories into directories the owner cannot write (PermissionError [Errno 13]),
reproduced across cards.

Activation: PYTHONPATH=<this dir> for the specific python invocation only.
Not a system-level change.
"""
import os as _os

_orig_mkdir = _os.mkdir


def _mkdir(path, mode=0o777, *, dir_fd=None):
    if mode != 0o777:
        mode = 0o777
    return _orig_mkdir(path, mode, dir_fd=dir_fd)


_os.mkdir = _mkdir
