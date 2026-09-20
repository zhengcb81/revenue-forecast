"""I-04-B: fix the two real-process cases to normalise their stats dict.

The first RED run showed F-B4b failing with KeyError('calls') - an author bug in the
case, not the product defect.  A test that fails for the wrong reason proves nothing,
so the fixture is corrected BEFORE the product patch is applied, and the RED run is
repeated to capture the honest reasons.
"""
from __future__ import annotations

import pathlib

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
ISO_TESTS = ATTEMPT / "iso" / "filing-fetch" / "tests" / "test_fetch_filing.py"

REPLACEMENTS = [
    (
        "from fetch_filing import _CLEANUP_BUDGET_MIN_SECONDS, PausedWorkerScope",
        "from fetch_filing import (\n"
        "            _CLEANUP_BUDGET_MIN_SECONDS,\n"
        "            _normalize_stats,\n"
        "            PausedWorkerScope,\n"
        "        )",
        "F-B4 import",
    ),
    (
        '        from fetch_filing import PausedWorkerScope\n\n'
        '        with TemporaryDirectory() as temporary:\n'
        '            base = Path(temporary)\n'
        '            root = self._wiki_root(base)\n'
        '            stub = base / "slow_status_stub.py"',
        '        from fetch_filing import PausedWorkerScope, _normalize_stats\n\n'
        '        with TemporaryDirectory() as temporary:\n'
        '            base = Path(temporary)\n'
        '            root = self._wiki_root(base)\n'
        '            stub = base / "slow_status_stub.py"',
        "F-B4b import",
    ),
    (
        '            stats: dict = {}\n'
        '            scope = PausedWorkerScope(\n'
        '                root=root, command_prefix=[sys.executable, "-X", "utf8", "-B", str(stub)],\n'
        '                enabled=True, graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,\n'
        '                deadline=time.monotonic() + 30.0, stats=stats,\n'
        '            )',
        '            stats: dict = _normalize_stats({})\n'
        '            scope = PausedWorkerScope(\n'
        '                root=root, command_prefix=[sys.executable, "-X", "utf8", "-B", str(stub)],\n'
        '                enabled=True, graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,\n'
        '                deadline=time.monotonic() + 30.0, stats=stats,\n'
        '            )',
        "F-B4 stats",
    ),
    (
        '            budget = 0.6\n'
        '            stats: dict = {}\n',
        '            budget = 0.6\n'
        '            stats: dict = _normalize_stats({})\n',
        "F-B4b stats",
    ),
]


def main() -> int:
    if "I-04-B" not in str(ISO_TESTS):
        raise SystemExit("refusing to touch a test file outside the I-04-B attempt")
    text = ISO_TESTS.read_text(encoding="utf-8")
    problems = []
    for old, new, label in REPLACEMENTS:
        count = text.count(old)
        if count != 1:
            problems.append(f"{label}: expected 1 match, found {count}")
            continue
        text = text.replace(old, new, 1)
        print(f"applied {label}")
    if problems:
        print("FAILED:", *problems, sep="\n  ")
        return 1
    ISO_TESTS.write_text(text, encoding="utf-8", newline="")
    print("fixtures corrected; re-run the RED pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
