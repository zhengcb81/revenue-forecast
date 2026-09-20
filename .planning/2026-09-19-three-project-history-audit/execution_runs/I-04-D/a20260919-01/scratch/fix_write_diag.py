"""Make ledger write failures self-describing and keep every case root short.

The residual failures all reported ``lease_state_write_failed`` with no detail.  The
write helper now records errno/filename/window path-length so the cause is visible,
and the case roots move to a short path under the attempt (a deep
``execution_runs/I-04-D/a20260919-01/iso/filing-fetch/.i04d-test-runs-<pid>/...`` tree
plus the unique temp suffix can approach the classic Windows path limit).
"""

from __future__ import annotations

import pathlib
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)
TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

text = PATCHER.read_text(encoding="utf-8")
OLD = '''def _atomic_write_json(path: Path, payload: Any) -> None:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = _unique_tmp_path(path)
    try:
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    except OSError:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise
'''
NEW = '''class _LeaseWriteError(OSError):
    """An OSError from the ledger write, with the window it happened in."""

    def __init__(self, window: str, tmp: Path, target: Path, cause: OSError) -> None:
        super().__init__(
            f"{window}: {type(cause).__name__} errno={cause.errno} "
            f"filename={cause.filename!r} tmp_len={len(str(tmp))} "
            f"target_len={len(str(target))} target={target} ({cause})"
        )
        self.window = window
        self.cause = cause


def _atomic_write_json(path: Path, payload: Any) -> None:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise _LeaseWriteError("mkdir", path, path, exc) from exc
    tmp = _unique_tmp_path(path)
    try:
        tmp.write_text(encoded, encoding="utf-8")
    except OSError as exc:
        raise _LeaseWriteError("write_text", tmp, path, exc) from exc
    try:
        tmp.replace(path)
    except OSError as exc:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise _LeaseWriteError("replace", tmp, path, exc) from exc
'''
if OLD not in text:
    print("PATCHER PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)
PATCHER.write_text(text, encoding="utf-8")
print("write-window diagnostics installed")

# Short case roots: put them directly under the attempt, not under a deep tree.
test = TEST.read_text(encoding="utf-8")
OLD_ROOT = '''RUNS_ROOT = Path(
    os.environ.get("I04D_TEST_RUNS_DIR")
    or (SKILL_ROOT / f".i04d-test-runs-{os.getpid()}")
)'''
NEW_ROOT = '''RUNS_ROOT = Path(
    os.environ.get("I04D_TEST_RUNS_DIR")
    # Short on purpose: the ledger's unique temp name is appended to the case path, and
    # a deeply nested root pushes the classic Windows path limit.
    or (SKILL_ROOT.parents[2] / f"runs{os.getpid()}")
)'''
if OLD_ROOT not in test:
    print("TEST PATTERN NOT FOUND")
    sys.exit(1)
test = test.replace(OLD_ROOT, NEW_ROOT, 1)
TEST.write_text(test, encoding="utf-8")
print("case root shortened")
