"""I-04-B: append the new deadline/cleanup timing cases to the ISOLATED test file.

Idempotent (refuses to append twice). Every case is hermetic: no wiki, no provider,
no real worker - the only real process used is a stub written into a TemporaryDirectory.

Cases map to the card's table:
  F-B1  model clock: a 9s call past a 10s deadline cannot earn a 5s backoff
  F-B2a deadline already passed -> ZERO request-stage calls (no 10s floor)
  F-B2b only 0.2s left -> the subprocess timeout is <= 0.2, never 10
  F-B3  fatal/worker_paused with ample budget -> no auto-retry, code preserved
  F-B5  first call succeeds / worker stopped or user-paused -> no extra calls
"""
from __future__ import annotations

import pathlib

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
ISO_TESTS = ATTEMPT / "iso" / "filing-fetch" / "tests" / "test_fetch_filing.py"
MARKER = "# --- I-04-B deadline/cleanup budget cases (added by the I-04-B attempt) ---"

BLOCK = "\n\n" + MARKER + R'''

class I04BDeadlineBudgetTests(unittest.TestCase):
    """Signed I-04-A v2 design, verified on the isolated copy.

    The model-clock cases state plainly that they are MATHEMATICAL verification of
    the budget rules (they drive a virtual monotonic clock); the real-process
    evidence lives in the attempt's scripts/i04b_real_timing.py.
    """

    @staticmethod
    def _wiki_root(parent: Path) -> Path:
        root = parent / "company-wiki"
        config = root / "config"
        config.mkdir(parents=True)
        (config / "source_catalog.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")
        return root

    def test_i04b_f_b1_backoff_cannot_pass_the_deadline(self) -> None:
        """F-B1 (model clock): deadline 10, the first call consumes 9 and raises
        catalog_busy.  Frozen expectation: the backoff is clamped by the budget
        RE-READ AFTER the call (=1), exactly one attempt happens, and the request
        never runs past the deadline.  The old code reused the pre-call budget and
        slept 5s to t=14 (pure_probes: budget=10, elapsed=14)."""
        from fetch_filing import _run_company_wiki_json_retry

        clock = {"t": 0.0}
        granted: list[float] = []

        def fake_monotonic() -> float:
            return clock["t"]

        def fake_sleep(seconds: float) -> None:
            clock["t"] += seconds

        def fake_call(*, command, root, timeout_seconds, action, stats=None):
            granted.append(timeout_seconds)
            clock["t"] += 9.0
            raise FilingFetchError("catalog busy", code="catalog_busy", stage=action)

        with patch("fetch_filing.time.monotonic", side_effect=fake_monotonic):
            with patch("fetch_filing.time.sleep", side_effect=fake_sleep) as sleep:
                with patch("fetch_filing._run_company_wiki_json", side_effect=fake_call):
                    with patch("fetch_filing.random.uniform", return_value=0.0):
                        with self.assertRaises(FilingFetchError) as ctx:
                            _run_company_wiki_json_retry(
                                command=["stub"], root=Path("."), action="identify",
                                deadline=10.0,
                            )
        self.assertEqual(ctx.exception.code, "upstream_error")
        self.assertEqual(granted, [10.0], "exactly one subcall may be issued")
        self.assertEqual(sleep.call_args_list, [call(1.0)],
                         "backoff must use the budget re-read after the call")
        self.assertLessEqual(clock["t"], 10.0, "the request must not run past the deadline")

    def test_i04b_f_b2a_no_request_stage_call_after_the_deadline(self) -> None:
        """F-B2 (model clock): now=100 with deadline=90.  The framework must issue
        ZERO request-stage calls - the old max(10.0, min(-10, 60)) minted a fresh
        10s budget and sent worker-status anyway."""
        from fetch_filing import PausedWorkerScope

        with TemporaryDirectory() as temporary:
            root = self._wiki_root(Path(temporary))
            scope = PausedWorkerScope(
                root=root, command_prefix=["stub"], enabled=True,
                graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
                deadline=90.0, stats={},
            )
            with patch("fetch_filing.time.monotonic", return_value=100.0):
                with patch.object(PausedWorkerScope, "_run") as run:
                    entered = scope.__enter__()
            self.assertIs(entered, scope)
            run.assert_not_called()
            self.assertEqual(scope.action, "deadline_exhausted")

    def test_i04b_f_b2b_tiny_remainder_is_not_inflated_to_ten_seconds(self) -> None:
        """F-B2 (model clock): 0.2s of budget left must reach the subprocess as
        <=0.2, never as a 10s floor."""
        from fetch_filing import PausedWorkerScope

        with TemporaryDirectory() as temporary:
            root = self._wiki_root(Path(temporary))
            scope = PausedWorkerScope(
                root=root, command_prefix=["stub"], enabled=True,
                graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
                deadline=100.2, stats={},
            )
            with patch("fetch_filing.time.monotonic", return_value=100.0):
                with patch.object(
                    PausedWorkerScope, "_run", return_value={"runtime_state": "stopped"}
                ) as run:
                    scope.__enter__()
            self.assertEqual(run.call_count, 1)
            granted = run.call_args.kwargs["timeout"]
            self.assertLessEqual(granted, 0.2 + 1e-9)
            self.assertGreater(granted, 0.0)
            self.assertEqual(scope.action, "worker_stopped")

    def test_i04b_f_b3_nonretryable_codes_are_not_retried(self) -> None:
        """F-B3 (model clock): worker_paused / fatal with plenty of budget must
        fail immediately - one call, no sleep, original classification kept."""
        from fetch_filing import _run_company_wiki_json_retry

        for code in ("worker_paused", "fatal"):
            with self.subTest(code=code):
                clock = {"t": 0.0}
                calls: list[float] = []

                def fake_call(*, command, root, timeout_seconds, action, stats=None,
                              _code=code):
                    calls.append(timeout_seconds)
                    clock["t"] += 1.0
                    raise FilingFetchError(_code, code=_code, stage=action)

                with patch("fetch_filing.time.monotonic", side_effect=lambda: clock["t"]):
                    with patch("fetch_filing.time.sleep") as sleep:
                        with patch("fetch_filing._run_company_wiki_json", side_effect=fake_call):
                            with self.assertRaises(FilingFetchError) as ctx:
                                _run_company_wiki_json_retry(
                                    command=["stub"], root=Path("."), action="resolve",
                                    deadline=100.0,
                                )
                self.assertEqual(ctx.exception.code, code)
                self.assertEqual(len(calls), 1)
                sleep.assert_not_called()

    def test_i04b_f_b5_no_extra_calls_when_the_worker_is_not_running(self) -> None:
        """F-B5: a stopped worker (and a user-paused worker) must not trigger a
        pause, a resume, or any retry."""
        from fetch_filing import PausedWorkerScope

        with TemporaryDirectory() as temporary:
            root = self._wiki_root(Path(temporary))
            stopped = PausedWorkerScope(
                root=root, command_prefix=["stub"], enabled=True,
                graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
                deadline=time.monotonic() + 30.0, stats={},
            )
            with patch.object(
                PausedWorkerScope, "_run", return_value={"runtime_state": "stopped"}
            ) as run:
                stopped.__enter__()
                stopped.__exit__(None, None, None)
            self.assertEqual(stopped.action, "worker_stopped")
            self.assertEqual([c.args[0] for c in run.call_args_list], ["worker-status"])

            user_paused = PausedWorkerScope(
                root=root, command_prefix=["stub"], enabled=True,
                graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
                deadline=time.monotonic() + 30.0, stats={},
            )
            with patch.object(
                PausedWorkerScope, "_run",
                return_value={"runtime_state": "running", "desired_state": "paused"},
            ) as run:
                user_paused.__enter__()
                user_paused.__exit__(None, None, None)
            self.assertEqual(user_paused.action, "respect_paused")
            self.assertEqual([c.args[0] for c in run.call_args_list], ["worker-status"])

    def test_i04b_f_b4_cleanup_is_budgeted_measured_and_separate(self) -> None:
        """F-B4 (real controlled process, no wiki/provider): the cleanup branch
        runs a REAL subprocess under the independent cleanup budget C, records its
        own elapsed time, and never merges it into the request window."""
        from fetch_filing import _CLEANUP_BUDGET_MIN_SECONDS, PausedWorkerScope

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = self._wiki_root(base)
            stub = base / "resume_stub.py"
            stub.write_text(
                "import json, sys, time\n"
                "time.sleep(0.30)\n"
                "print(json.dumps({'status': 'running'}))\n"
                "sys.exit(0)\n",
                encoding="utf-8",
            )
            stats: dict = {}
            scope = PausedWorkerScope(
                root=root, command_prefix=[sys.executable, "-X", "utf8", "-B", str(stub)],
                enabled=True, graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
                deadline=time.monotonic() + 30.0, stats=stats,
            )
            scope._register(joined=False, timeout=scope._request_remaining())
            scope.action = "paused_by_us"
            started = time.monotonic()
            scope.__exit__(None, None, None)
            wall = time.monotonic() - started

            self.assertEqual(stats.get("cleanup_calls"), 1)
            self.assertEqual(stats.get("cleanup_status"), "restored")
            self.assertEqual(stats.get("pause_action"), "paused_by_us")
            measured = stats.get("cleanup_elapsed_seconds")
            self.assertIsNotNone(measured)
            self.assertGreaterEqual(measured, 0.25)
            self.assertLessEqual(measured, _CLEANUP_BUDGET_MIN_SECONDS + EPSILON_S)
            self.assertLessEqual(wall, _CLEANUP_BUDGET_MIN_SECONDS + EPSILON_S)
            # the cleanup number is its own key: nothing folds it into the request
            self.assertNotIn("request_elapsed", stats)

    def test_i04b_f_b4b_real_timeout_matches_the_remaining_budget(self) -> None:
        """F-B4 (real controlled process): a real subprocess gets exactly the
        remaining budget as its timeout, and the observed wall clock stays within
        budget + epsilon."""
        from fetch_filing import PausedWorkerScope

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = self._wiki_root(base)
            stub = base / "slow_status_stub.py"
            stub.write_text(
                "import json, time\n"
                "time.sleep(3.0)\n"
                "print(json.dumps({'runtime_state': 'running'}))\n",
                encoding="utf-8",
            )
            budget = 0.6
            stats: dict = {}
            scope = PausedWorkerScope(
                root=root, command_prefix=[sys.executable, "-X", "utf8", "-B", str(stub)],
                enabled=True, graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
                deadline=time.monotonic() + budget, stats=stats,
            )
            started = time.monotonic()
            scope.__enter__()
            observed = time.monotonic() - started
            self.assertEqual(scope.action, "no_status")
            self.assertLessEqual(observed, budget + EPSILON_S)
            self.assertGreaterEqual(observed, budget * 0.5)
'''

HEADER = '''
# I-04-B: epsilon signed (temporarily) by I-04-A D4; the pre-committed re-measurement
# program runs before any real-process acceptance is quoted (see the attempt's
# design_measurements evidence).  Timing cases below compare against this value.
EPSILON_S = 0.4
'''


def main() -> int:
    if "execution_runs" not in str(ISO_TESTS) or "I-04-B" not in str(ISO_TESTS):
        raise SystemExit(f"refusing to touch a test file outside the I-04-B attempt: {ISO_TESTS}")
    text = ISO_TESTS.read_text(encoding="utf-8")
    if MARKER in text:
        raise SystemExit("I-04-B block already present; refusing to append twice")
    if "import time" not in text.split("SKILL_ROOT")[0]:
        text = text.replace("import sys\nimport unittest\n", "import sys\nimport time\nimport unittest\n", 1)
    text = text.replace(
        "from fetch_filing import (  # noqa: E402\n",
        HEADER.lstrip("\n") + "\nfrom fetch_filing import (  # noqa: E402\n",
        1,
    )
    ISO_TESTS.write_text(text + BLOCK, encoding="utf-8", newline="")
    print(f"appended I-04BDeadlineBudgetTests to {ISO_TESTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
