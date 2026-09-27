"""Harness-side pytest plugin.  Two jobs, both OUTSIDE the product tests.

1. **Persist every test report** (including the traceback) to a JSONL file.
   Under the load conditions this card measures, pytest's own
   ``pytest_sessionfinish`` can crash while cleaning the basetemp
   (``PermissionError: [WinError 5]`` in ``_pytest/tmpdir.py:337``), which
   happens BEFORE the terminal summary is printed — stdout alone then loses the
   test's actual failure.  This plugin writes the report out-of-band.

2. **Restore the documented Windows semantics of ``os.mkdir(mode=...)``**.
   CPython documents ``The mode argument is ignored on Windows``
   (``os.mkdir.__doc__``).  In THIS session's file sandbox that documented
   behaviour does not hold: ``os.mkdir(p, 0o700)`` / ``Path.mkdir(mode=0o700)``
   yield a directory that neither the owner, nor ``icacls``, nor
   ``Get-ChildItem`` can list (``PermissionError: [WinError 5]``), while
   ``mode=0o755/0o777/default`` yield a normal directory.  pytest creates every
   basetemp with ``basetemp.mkdir(mode=0o700)`` (``_pytest/tmpdir.py:158``) and
   every numbered dir with ``os.mkdir(new_path, 0o700)``
   (``_pytest/pathlib.py``), so without this shim ``tmp_path`` cannot be
   resolved at all and every node errors in fixture setup.
   The shim forces ``mode=0o777`` for the whole pytest process — i.e. it makes
   the call behave exactly as CPython documents.  It is applied identically to
   the red, green and mutation arms, touches no product code and no product
   test, and is disclosed in ``oracle-addendum-B.md``.

This file belongs to the attempt's **harness**: it is loaded with
``-p tside_probe`` and lives outside ``iso/**/tests/**``.
"""

from __future__ import annotations

import json
import os

_ORIG_PATH_MKDIR = None
_ORIG_OS_MKDIR = None
_SHIM_ACTIVE = False


def _install_dir_mode_shim() -> dict:
    """Force the documented Windows semantics: mode is ignored."""
    global _ORIG_PATH_MKDIR, _ORIG_OS_MKDIR, _SHIM_ACTIVE
    if _SHIM_ACTIVE:
        return {"installed": True, "already": True}
    import pathlib
    _ORIG_PATH_MKDIR = pathlib.Path.mkdir
    _ORIG_OS_MKDIR = os.mkdir

    def path_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        return _ORIG_PATH_MKDIR(self, 0o777, parents=parents, exist_ok=exist_ok)

    def os_mkdir(path, mode=0o777, *, dir_fd=None):
        return _ORIG_OS_MKDIR(path, 0o777, dir_fd=dir_fd)

    pathlib.Path.mkdir = path_mkdir
    os.mkdir = os_mkdir
    _SHIM_ACTIVE = True
    return {"installed": True, "already": False,
            "reason": "CPython documents mode as ignored on Windows; under this "
                      "session's file sandbox mode=0o700 produces a directory "
                      "nobody (owner included) can list",
            "python_version": os.sys.version.split()[0]}


def pytest_configure(config) -> None:
    result = _install_dir_mode_shim()
    path = os.environ.get("CW_REPORT_FILE")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"event": "dir_mode_shim", **result},
                                    ensure_ascii=False) + "\n")


def _sink() -> str | None:
    return os.environ.get("CW_REPORT_FILE")


def pytest_runtest_logreport(report) -> None:
    path = _sink()
    if not path:
        return
    if report.outcome == "passed" and report.when == "call":
        rec = {"when": report.when, "outcome": report.outcome,
               "duration_seconds": round(getattr(report, "duration", 0.0), 3)}
    elif report.failed:
        longrepr = str(getattr(report, "longrepr", ""))
        rec = {"when": report.when, "outcome": report.outcome,
               "duration_seconds": round(getattr(report, "duration", 0.0), 3),
               "longrepr": longrepr[:8000]}
    else:
        return
    rec["nodeid"] = report.nodeid
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
