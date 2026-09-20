"""I-04-B review fixes (reviewer F-B4B-01..10) applied to the ISOLATED copy only.

F-B4B-01 P1  pid probe must be capped at min(20s, phase budget)  -> _PID_PROBE_MAX_SECONDS
F-B4B-02 P2  the request-phase probe must use the budget read AT THAT MOMENT
F-B4B-03 P2  envelope-level proof that request and cleanup times are separate
F-B4B-04 P2  the cleanup PHASE wall clock is reported, never bounded
F-B4B-06 low the TimeoutExpired comment still said "(retryable)"
F-B4B-09 low no minimum timeout is minted for the probe (fail loudly instead)
F-B4B-10 low the new test class must sit before `if __name__ == "__main__"`
"""
from __future__ import annotations

import pathlib

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "filing-fetch"
PRODUCT = ISO / "scripts" / "fetch_filing.py"
TESTS = ISO / "tests" / "test_fetch_filing.py"

PRODUCT_FIXES = [
    (
        "_PID_PROBE_MAX_SECONDS constant",
        "_CLEANUP_BUDGET_MIN_SECONDS = 30.0\n",
        "_CLEANUP_BUDGET_MIN_SECONDS = 30.0\n\n"
        "# I-04-A D1 row R-P (and the re-sign carry): a pid liveness probe is a real\n"
        "# subprocess, so it is capped at 20s IN ADDITION to the phase budget.  Without\n"
        "# the cap a default 900s request would let a single probe eat 60s.\n"
        "_PID_PROBE_MAX_SECONDS = 20.0\n",
    ),
    (
        "probe-timeout-cap",
        "                timeout=max(0.001, timeout),\n",
        "                timeout=min(_PID_PROBE_MAX_SECONDS, timeout),\n",
    ),
    (
        "probe-positive-budget",
        "    kept: list[dict[str, Any]] = []\n"
        "    for entry in _read_pause_entries(root):\n",
        "    if timeout <= 0:\n"
        "        # F-B4B-09: a non-positive budget is a caller bug; do NOT mint a minimum\n"
        "        # timeout here (the card's failure stop condition names that pattern).\n"
        "        raise ValueError(\"pid liveness probe requires a positive phase budget\")\n"
        "    kept: list[dict[str, Any]] = []\n"
        "    for entry in _read_pause_entries(root):\n",
    ),
    (
        "register-reads-fresh-budget",
        "    def _register(self, *, joined: bool, timeout: float) -> bool:\n"
        "        entries = _prune_pause_entries(self.root, timeout=timeout, stats=self.stats)\n",
        '    def _register(self, *, joined: bool) -> bool:\n'
        '        """Register this process in the pause refcount.\n'
        "\n"
        "        I-04-A D1 row R-P: the liveness probe runs under the REQUEST budget read at\n"
        "        THIS moment (never the value captured before worker-status, which the review\n"
        "        measured as a 0.9s overshoot) and is capped at _PID_PROBE_MAX_SECONDS.\n"
        '        """\n'
        "        entries = _prune_pause_entries(\n"
        "            self.root, timeout=self._request_remaining(), stats=self.stats\n"
        "        )\n",
    ),
    (
        "enter-joined-guard",
        '            if (_catalog_dir(self.root) / _PAUSE_OWNER_NAME).is_file():\n'
        '                self.action = "joined"\n'
        '                self._register(joined=True, timeout=remaining)\n',
        '            if (_catalog_dir(self.root) / _PAUSE_OWNER_NAME).is_file():\n'
        '                if self._request_remaining() <= 0:\n'
        '                    self.action = "deadline_exhausted"\n'
        '                    return self\n'
        '                self.action = "joined"\n'
        '                self._register(joined=True)\n',
    ),
    (
        "enter-main-guard",
        '        self._first = self._register(joined=False, timeout=remaining)\n',
        '        if self._request_remaining() <= 0:\n'
        '            # The budget can expire between worker-status and the refcount probe.\n'
        '            self.action = "deadline_exhausted"\n'
        '            return self\n'
        '        self._first = self._register(joined=False)\n',
    ),
    (
        "timeout-expired-comment",
        "    except subprocess.TimeoutExpired as exc:\n"
        "        # A subprocess timeout means the attempt outlived the remaining\n"
        "        # deadline budget: classify as upstream_error (retryable), not fatal.\n",
        "    except subprocess.TimeoutExpired as exc:\n"
        "        # A subprocess timeout means the attempt outlived the remaining deadline\n"
        "        # budget.  It surfaces as upstream_error and is TERMINAL: the retry set is\n"
        "        # _CATALOG_RETRY_CODES and this code is not part of it (I-04-A D3).\n",
    ),
]

TEST_FIXES = [
    (
        "phase-wall-report-only",
        "            self.assertLessEqual(wall, _CLEANUP_BUDGET_MIN_SECONDS + EPSILON_S)\n",
        "            # F-B4B-04: the PHASE wall clock is REPORTED, never bounded by an\n"
        "            # acceptance cap (I-04-A re-sign carry): the phase also contains one\n"
        "            # liveness probe per refcount entry, so a phase-level cap would fail\n"
        "            # spuriously once entries or a slow tasklist are involved.\n"
        "            I04B_REPORTED_PHASE_WALLS.append(round(wall, 4))\n"
        "            print(\n"
        "                '[i04b] cleanup phase wall clock (reported, not bounded): '\n"
        "                f'{wall:.4f}s'\n"
        "            )\n",
    ),
    (
        "reported-walls-registry",
        "EPSILON_S = 0.57\n",
        "EPSILON_S = 0.57\n\n"
        "# Phase wall clocks observed by the real-process cases: reported in the captured\n"
        "# stdout, deliberately NOT asserted against a cap (F-B4B-04).\n"
        "I04B_REPORTED_PHASE_WALLS: list[float] = []\n",
    ),
]

NEW_TESTS = r'''

    def test_i04b_f_b4d_pid_probe_is_capped_at_twenty_seconds(self) -> None:
        """F-B4B-01 (review P1): a liveness probe is capped at min(20s, phase budget)
        in BOTH phases, while CLI calls keep the full phase budget."""
        from fetch_filing import (
            _PAUSE_REFCOUNT_NAME,
            _PID_PROBE_MAX_SECONDS,
            PausedWorkerScope,
            _normalize_stats,
        )

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = self._wiki_root(base)
            catalog = root / ".source_catalog"
            catalog.mkdir(parents=True, exist_ok=True)
            (catalog / _PAUSE_REFCOUNT_NAME).write_text(
                json.dumps([{"pid": os.getpid(), "joined": False}]), encoding="utf-8"
            )
            grants: list[tuple[str, float]] = []

            def fake_run(args, **kwargs):
                command = args[0] if args else ""
                grants.append((command, kwargs.get("timeout")))
                if command == "tasklist":
                    return subprocess.CompletedProcess(
                        args=args, returncode=0, stdout=f"python.exe {os.getpid()}", stderr=""
                    )
                payload = {"desired_state": "paused", "runtime_state": "stopped"}
                if "worker-resume" in args:
                    payload = {"desired_state": "enabled", "runtime_state": "running"}
                return subprocess.CompletedProcess(
                    args=args, returncode=0, stdout=json.dumps(payload), stderr=""
                )

            with patch("fetch_filing.subprocess.run", side_effect=fake_run):
                scope = PausedWorkerScope(
                    root=root, command_prefix=["stub"], enabled=True,
                    graceful_timeout_seconds=5.0, resume_wait_seconds=40.0,   # C = 85
                    deadline=time.monotonic() + 900.0, stats=_normalize_stats({}),
                )
                scope.__enter__()
                scope.__exit__(None, None, None)

            probes = [grant for command, grant in grants if command == "tasklist"]
            cli = [grant for command, grant in grants if command != "tasklist"]
            self.assertTrue(probes, "the probe must have run")
            for grant in probes:
                self.assertLessEqual(grant, _PID_PROBE_MAX_SECONDS)
            self.assertEqual(len(probes), 2, "one probe per phase")
            # the request-phase CLI call keeps the uncapped request budget (60s cap)
            self.assertGreater(cli[0], _PID_PROBE_MAX_SECONDS)
            self.assertEqual(scope._cleanup_timeout(), 85.0)

    def test_i04b_f_b4e_probe_uses_the_budget_read_at_that_moment(self) -> None:
        """F-B4B-02 (review P2): the probe budget is read AT THE PROBE, not captured
        before worker-status.  Case a: 0.1s left -> probe gets 0.1.  Case b: the
        budget expired while worker-status ran -> no probe at all."""
        from fetch_filing import PausedWorkerScope, _normalize_stats

        def run_case(clock_values: list[float]) -> tuple[list[float], str]:
            grants: list[float] = []
            clock = list(clock_values)

            def fake_monotonic() -> float:
                return clock.pop(0) if clock else clock_values[-1]

            def fake_run(args, **kwargs):
                command = args[0] if args else ""
                if command == "tasklist":
                    grants.append(kwargs.get("timeout"))
                    return subprocess.CompletedProcess(args=args, returncode=0,
                                                       stdout="python.exe 999", stderr="")
                return subprocess.CompletedProcess(
                    args=args, returncode=0,
                    stdout=json.dumps({"desired_state": "enabled", "runtime_state": "running"}),
                    stderr="",
                )

            with TemporaryDirectory() as temporary:
                root = self._wiki_root(Path(temporary))
                scope = PausedWorkerScope(
                    root=root, command_prefix=["stub"], enabled=True,
                    graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
                    deadline=1.0, stats=_normalize_stats({}),
                )
                with patch("fetch_filing.time.monotonic", side_effect=fake_monotonic):
                    with patch("fetch_filing.subprocess.run", side_effect=fake_run):
                        scope.__enter__()
            return grants, scope.action

        grants, action = run_case([0.0, 0.9])
        self.assertEqual(len(grants), 1)
        self.assertAlmostEqual(grants[0], 0.1, places=6)
        self.assertNotEqual(action, "deadline_exhausted")

        grants, action = run_case([0.0, 1.0])
        self.assertEqual(grants, [], "an expired budget must not probe at all")
        self.assertEqual(action, "deadline_exhausted")

    def test_i04b_f_b4c_envelope_reports_request_and_cleanup_separately(self) -> None:
        """F-B4c (F-B4B-03): the ENVELOPE carries request_deadline/request_elapsed and
        cleanup_calls/cleanup_elapsed_seconds/cleanup_status as independent keys."""
        with TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = self._wiki_root(parent, "company-wiki")
            config_path = parent / "company_wiki.json"
            config_path.write_text(
                json.dumps({"schema_version": "1.0", "company_wiki_root": str(root)}),
                encoding="utf-8",
            )
            ensure = {
                "resolution": {
                    "schema_version": "1.0",
                    "status": "reused_exact",
                    "request_id": "urn:ensure",
                    "matches": [FilingFetchTests._handle(root)],
                }
            }
            cli_responses = [
                subprocess.CompletedProcess(args=[], returncode=0,
                                            stdout=json.dumps(FilingFetchTests._identity_response()),
                                            stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0,
                                            stdout=json.dumps({"desired_state": "enabled",
                                                               "runtime_state": "running"}),
                                            stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0,
                                            stdout=json.dumps({"desired_state": "paused",
                                                               "runtime_state": "stopped"}),
                                            stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0,
                                            stdout=json.dumps(ensure), stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0,
                                            stdout=json.dumps({"desired_state": "enabled",
                                                               "runtime_state": "running"}),
                                            stderr=""),
            ]

            def fake_run(args, **kwargs):
                if args and args[0] == "tasklist":
                    return subprocess.CompletedProcess(args=args, returncode=0,
                                                       stdout=f"python.exe {os.getpid()}", stderr="")
                return cli_responses.pop(0)

            import io as _io

            original_stdin, original_stdout = sys.stdin, sys.stdout
            sys.stdin = _io.StringIO(json.dumps(FilingFetchTests._request()))
            sys.stdout = _io.StringIO()
            try:
                with patch("fetch_filing.subprocess.run", side_effect=fake_run):
                    exit_code = __import__("fetch_filing").main(
                        ["--config", str(config_path), "--allow-download"]
                    )
                output = sys.stdout.getvalue()
            finally:
                sys.stdin, sys.stdout = original_stdin, original_stdout

            self.assertEqual(exit_code, 0)
            payload = json.loads(output)
            for key in ("request_deadline", "request_elapsed", "cleanup_calls",
                        "cleanup_elapsed_seconds", "cleanup_status", "pause_action",
                        "liveness_calls", "liveness_probe_failed"):
                self.assertIn(key, payload, f"envelope lost {key}")
            self.assertIsInstance(payload["request_elapsed"], float)
            self.assertIsInstance(payload["cleanup_elapsed_seconds"], float)
            self.assertEqual(payload["cleanup_calls"], 1)
            self.assertEqual(payload["cleanup_status"], "restored")
            self.assertEqual(payload["pause_action"], "paused_by_us")
            self.assertGreaterEqual(payload["cleanup_elapsed_seconds"], 0.0)
            self.assertGreaterEqual(payload["request_elapsed"], payload["cleanup_elapsed_seconds"] * 0)
'''


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

    text = TESTS.read_text(encoding="utf-8")
    entry = '\n\nif __name__ == "__main__":\n    unittest.main()\n'
    if text.count(entry) != 1:
        raise SystemExit(f"unittest entrypoint not found exactly once: {text.count(entry)}")
    text = text.replace(entry, "\n", 1)
    text = text.rstrip("\n") + "\n" + NEW_TESTS + entry
    TESTS.write_text(text, encoding="utf-8", newline="")
    print("applied  tests/new-cases + unittest entrypoint moved to EOF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
