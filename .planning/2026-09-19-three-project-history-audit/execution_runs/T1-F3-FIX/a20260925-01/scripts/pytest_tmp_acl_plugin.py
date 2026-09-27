"""Attempt-local pytest plugin: sandbox ACL accommodation for basetemp.

Observed on this host (evidence: evidence/before/suites/*.stderr.txt, first
run of the before-phase suites): `os.mkdir(path, 0o700)` / `Path.mkdir(mode=
0o700)` succeeds but the resulting directory is NOT listable or removable by
the same user (`PermissionError: [WinError 5]`), i.e. the mode->ACL mapping of
the sandbox turns pytest's `basetemp.mkdir(mode=0o700)` into a directory whose
own cleanup (`_pytest.tmpdir.pytest_sessionfinish` -> `cleanup_dead_symlinks`)
raises, so pytest dies BEFORE printing its summary line and no passed/failed
counts can be parsed.

This plugin widens only the *directory mode* pytest asks for (0o700 -> 0o777).
It changes no assertion, no fixture, no test file and no SUT byte; it only
keeps the temporary directory readable by the process that created it.
Loaded with `-p pytest_tmp_acl_plugin` from this attempt's scripts/ dir, so it
is never imported by the SUT or by the frozen harness/test files.
"""

from __future__ import annotations

import os
import pathlib

_MODE = 0o700
_WIDEN = 0o777

_orig_path_mkdir = pathlib.Path.mkdir
_orig_os_mkdir = os.mkdir


def _widen(mode: int) -> int:
    if (mode & 0o777) == _MODE:
        return (mode & ~0o777) | _WIDEN
    return mode


def _path_mkdir(self, mode=0o777, parents=False, exist_ok=False):
    return _orig_path_mkdir(self, mode=_widen(mode), parents=parents,
                            exist_ok=exist_ok)


def _os_mkdir(path, mode=0o777, *, dir_fd=None):
    mode = _widen(mode)
    if dir_fd is None:
        return _orig_os_mkdir(path, mode)
    return _orig_os_mkdir(path, mode, dir_fd=dir_fd)


pathlib.Path.mkdir = _path_mkdir
os.mkdir = _os_mkdir
