"""I-04-B condition C1 (review R2-01): remove the guard->_register double-read race.

The reviewer reproduced a (microsecond) window: `__enter__` read the budget for its
guard, then `_register` read it AGAIN; if the clock crossed the deadline in between, the
internal `ValueError` escaped `__enter__` (action stayed "none") and main() turned it into
fatal/exit 1 instead of the correct deadline_exhausted.

Fix: the caller reads the budget ONCE, immediately before the call, and passes it in.
`_prune_pause_entries` keeps its `timeout <= 0` assertion as an internal invariant check
that is now unreachable from the request path.
Plus: the boundary sub-case the condition asks for (three-value clock).
"""
from __future__ import annotations

import pathlib

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
PRODUCT = ATTEMPT / "iso" / "filing-fetch" / "scripts" / "fetch_filing.py"
TESTS = ATTEMPT / "iso" / "filing-fetch" / "tests" / "test_fetch_filing.py"

PRODUCT_FIXES = [
    (
        "register-takes-the-guarded-budget",
        '    def _register(self, *, joined: bool) -> bool:\n'
        '        """Register this process in the pause refcount.\n'
        '\n'
        '        I-04-A D1 row R-P: the liveness probe runs under the REQUEST budget read at\n'
        '        THIS moment (never the value captured before worker-status, which the review\n'
        '        measured as a 0.9s overshoot) and is capped at _PID_PROBE_MAX_SECONDS.\n'
        '        """\n'
        '        entries = _prune_pause_entries(\n'
        '            self.root, timeout=self._request_remaining(), stats=self.stats\n'
        '        )\n',
        '    def _register(self, *, joined: bool, timeout: float) -> bool:\n'
        '        """Register this process in the pause refcount.\n'
        '\n'
        '        I-04-A D1 row R-P: the liveness probe runs under the REQUEST budget that the\n'
        '        caller read IMMEDIATELY BEFORE this call (never the value captured before\n'
        '        worker-status, which the review measured as a 0.9s overshoot) and is capped\n'
        '        at _PID_PROBE_MAX_SECONDS.  Taking the budget as an argument - rather than\n'
        '        re-reading it here - closes the double-read window the round-2 review found:\n'
        '        a second read could return a non-positive value and raise out of __enter__\n'
        '        instead of degrading to deadline_exhausted.\n'
        '        """\n'
        '        entries = _prune_pause_entries(self.root, timeout=timeout, stats=self.stats)\n',
    ),
    (
        "joined-path-guard-reads-once",
        '            if (_catalog_dir(self.root) / _PAUSE_OWNER_NAME).is_file():\n'
        '                if self._request_remaining() <= 0:\n'
        '                    self.action = "deadline_exhausted"\n'
        '                    return self\n'
        '                self.action = "joined"\n'
        '                self._register(joined=True)\n',
        '            if (_catalog_dir(self.root) / _PAUSE_OWNER_NAME).is_file():\n'
        '                probe_budget = self._request_remaining()\n'
        '                if probe_budget <= 0:\n'
        '                    self.action = "deadline_exhausted"\n'
        '                    return self\n'
        '                self.action = "joined"\n'
        '                self._register(joined=True, timeout=probe_budget)\n',
    ),
    (
        "main-path-guard-reads-once",
        '        if self._request_remaining() <= 0:\n'
        '            # The budget can expire between worker-status and the refcount probe.\n'
        '            self.action = "deadline_exhausted"\n'
        '            return self\n'
        '        self._first = self._register(joined=False)\n',
        '        probe_budget = self._request_remaining()\n'
        '        if probe_budget <= 0:\n'
        '            # The budget can expire between worker-status and the refcount probe.\n'
        '            self.action = "deadline_exhausted"\n'
        '            return self\n'
        '        self._first = self._register(joined=False, timeout=probe_budget)\n',
    ),
    (
        "prune-assertion-is-an-invariant",
        '    if timeout <= 0:\n'
        '        # F-B4B-09: a non-positive budget is a caller bug; do NOT mint a minimum\n'
        '        # timeout here (the card\'s failure stop condition names that pattern).\n'
        '        raise ValueError("pid liveness probe requires a positive phase budget")\n',
        '    if timeout <= 0:\n'
        '        # F-B4B-09 + R2-01: a non-positive budget is a caller bug, and the request\n'
        '        # path cannot reach it (its guards read the budget once, immediately before\n'
        '        # the call).  Do NOT mint a minimum timeout here - fail loudly instead.\n'
        '        raise ValueError("pid liveness probe requires a positive phase budget")\n',
    ),
]

TEST_FIXES = [
    (
        "b4e-register-call-sites",
        '            scope._register(joined=False)\n',
        '            scope._register(joined=False, timeout=scope._request_remaining())\n',
    ),
    (
        "b4d-register-call-site",
        '            scope = PausedWorkerScope(\n'
        '                root=root, command_prefix=["stub"], enabled=True,\n'
        '                graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,\n'
        '                deadline=time.monotonic() + 30.0, stats=stats,\n'
        '            )\n'
        '            scope._register(joined=False)\n',
        '            scope = PausedWorkerScope(\n'
        '                root=root, command_prefix=["stub"], enabled=True,\n'
        '                graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,\n'
        '                deadline=time.monotonic() + 30.0, stats=stats,\n'
        '            )\n'
        '            scope._register(joined=False, timeout=scope._request_remaining())\n',
    ),
    (
        "b4e-race-boundary-subcase",
        '        grants, action = run_case([0.0, 1.0])\n'
        '        self.assertEqual(grants, [], "an expired budget must not probe at all")\n'
        '        self.assertEqual(action, "deadline_exhausted")\n',
        '        grants, action = run_case([0.0, 1.0])\n'
        '        self.assertEqual(grants, [], "an expired budget must not probe at all")\n'
        '        self.assertEqual(action, "deadline_exhausted")\n'
        '\n'
        '        # R2-01 boundary (review condition C1): a clock that jumps past the deadline\n'
        '        # between the guard read and the probe must degrade to deadline_exhausted -\n'
        '        # never let an internal assertion escape __enter__ as a fatal error.\n'
        '        grants, action = run_case([0.0, 5.0, 100.0])\n'
        '        self.assertEqual(grants, [5.0], "the probe uses the budget read once")\n'
        '        self.assertNotEqual(action, "none")\n'
        '        grants, action = run_case([0.0, 100.0, 100.0])\n'
        '        self.assertEqual(grants, [])\n'
        '        self.assertEqual(action, "deadline_exhausted")\n',
    ),
]


def patch(path: pathlib.Path, fixes, label: str) -> list[str]:
    if "I-04-B" not in str(path):
        raise SystemExit(f"refusing to edit outside the I-04-B attempt: {path}")
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    for name, old, new in fixes:
        count = text.count(old)
        if count != 1:
            problems.append(f"{label}/{name}: expected 1 match, found {count}")
            continue
        text = text.replace(old, new, 1)
        print(f"applied  {label}/{name}")
    if not problems:
        path.write_text(text, encoding="utf-8", newline="")
    return problems


def main() -> int:
    problems = patch(PRODUCT, PRODUCT_FIXES, "product")
    problems += patch(TESTS, TEST_FIXES, "tests")
    if problems:
        print("FAILED:", *problems, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
