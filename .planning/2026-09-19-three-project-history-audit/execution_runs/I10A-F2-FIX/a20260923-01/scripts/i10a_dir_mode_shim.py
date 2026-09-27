"""I10A-F2-FIX environment shim — directory-creation mode only (NOT a product edit).

Observed in this session (measurement, `scripts/_modeprobe.py`):
  os.mkdir(p, 0o700)  -> created directory is UNWRITABLE (Errno 13 / WinError 5,
                          icacls "Access is denied"); pathlib.Path.mkdir(mode=0o700)
                          and tempfile.mkdtemp() (which uses mode 0o700) behave the
                          same.
  os.mkdir(p, 0o777) / os.mkdir(p) -> created directory is writable (normal ACL).

pytest's own machinery creates every temporary directory with mode 0o700
(`TempPathFactory` -> ``pytest-of-*``, ``shutil``-style numbered dirs) and
``cacheprovider`` uses ``tempfile.mkdtemp``, so in this session the session-scoped
autouse fixture ``tests/conftest.py::_isolate_publication_registry`` dies with
PermissionError and every testcase would ERROR — for a reason that has nothing to
do with the F-I10A-2 fix or with any assertion.

This plugin (loaded with ``-p i10a_dir_mode_shim``) wraps ``os.mkdir`` so the
*mode* argument is always the default 0o777. It changes directory ACLs only; it
does not touch product code, fixtures, assertions, or test selection, and it is
applied identically to every family run in this attempt. Disclosed in handoff.
"""
from __future__ import annotations

import os

_original_mkdir = os.mkdir


def _mkdir(path, mode=0o777, *, dir_fd=None):  # noqa: ANN001, ARG001
    if dir_fd is None:
        return _original_mkdir(path)
    return _original_mkdir(path, dir_fd=dir_fd)


os.mkdir = _mkdir  # type: ignore[assignment]
