"""I-04-B iso patch: apply the SIGNED I-04-A v2 budget design to the isolated copy only.

Runs against execution_runs/I-04-B/a20260919-01/iso/filing-fetch/scripts/fetch_filing.py.
Every replacement is exact-match and reported; a miss is an error (never a silent no-op).
The production repo is untouched: this script refuses any path outside the attempt dir.

Design mapping (decision.md v2 → code):
  D1 R-P        pid liveness probe becomes a budgeted, counted consumer
  D1/D3         request stages use _request_remaining() (no 10s floor)
  D2            cleanup uses _cleanup_timeout() = max(30, 2*resume_wait + graceful)
  D3            remaining is re-read AFTER a subcall returns, before the backoff wait
  D5.3          stats: request_deadline/request_elapsed/cleanup_*/pause_action/liveness_*
"""
from __future__ import annotations

import pathlib
import sys

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ATTEMPT / "iso" / "filing-fetch" / "scripts" / "fetch_filing.py"

PATCHES: list[tuple[str, str, str]] = []


def patch(name: str, old: str, new: str) -> None:
    PATCHES.append((name, old, new))


# --- P-a: fresh remaining after the subcall returns (I-04-A D3) ---------------
patch(
    "P-a fresh-remaining-before-backoff",
    """        except FilingFetchError as exc:
            if exc.code not in _CATALOG_RETRY_CODES:
                raise
            jittered = backoff * (
""",
    """        except FilingFetchError as exc:
            if exc.code not in _CATALOG_RETRY_CODES:
                raise
            # I-04-A D3 (parent I-04 item 1): re-read the budget AFTER the subcall
            # returned.  The old code reused the value computed BEFORE the call, so a
            # subcall that consumed the whole deadline still earned a full backoff
            # sleep - 9s call + 5s stale wait = t=14 past a 10s deadline, which is
            # exactly the accident reviews/filing/tests/pure_probes.json records.
            remaining = deadline - time.monotonic()
            jittered = backoff * (
""",
)

# --- P-b: cleanup budget floor constant (I-04-A D2) --------------------------
patch(
    "P-b cleanup-budget-constant",
    """_WORKER_STATUS_TIMEOUT = 60.0
""",
    """_WORKER_STATUS_TIMEOUT = 60.0

# I-04-A D2: C = max(floor, 2*resume_wait + graceful).  A formula rather than a
# frozen constant, because --worker-resume-wait-seconds accepts any float: a fixed
# 30s would make ownership restoration time out by construction for larger values.
# Cleanup never borrows the request deadline.
_CLEANUP_BUDGET_MIN_SECONDS = 30.0
""",
)

# --- P-c: budgeted pid probe (I-04-A D1 R-P) --------------------------------
patch(
    "P-c pid-probe-budget-param",
    '''def _pid_is_alive(pid: int) -> bool:
    """Best-effort pid liveness; unknown states count as alive (conservative)."""
    if os.name == "nt":
        try:
            probe = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore[attr-defined]
                timeout=20,
            )
        except (OSError, subprocess.SubprocessError):
            return True
''',
    '''def _pid_is_alive(pid: int, *, timeout: float) -> bool:
    """Best-effort pid liveness; unknown states count as alive (conservative).

    I-04-A D1 row R-P: this spawns a real subprocess, so it is a budget consumer.
    Callers pass the phase budget (request remaining, or the cleanup budget)
    instead of the old hard-coded 20s tail; a probe timeout is re-raised so the
    caller can record it rather than silently reading "alive".
    """
    if os.name == "nt":
        try:
            probe = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore[attr-defined]
                timeout=max(0.001, timeout),
            )
        except subprocess.TimeoutExpired:
            raise
        except (OSError, subprocess.SubprocessError):
            return True
''',
)

# --- P-d: counted pruning ---------------------------------------------------
patch(
    "P-d prune-counts-probes",
    '''def _prune_pause_entries(root: Path) -> list[dict[str, Any]]:
    return [e for e in _read_pause_entries(root) if _pid_is_alive(e["pid"])]
''',
    '''def _prune_pause_entries(
    root: Path, *, timeout: float, stats: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Prune refcount entries whose pid is gone.

    I-04-A D1 R-P: the probe is counted separately from CLI calls, and a probe
    that timed out is recorded (the entry still counts as alive, conservatively).
    """
    kept: list[dict[str, Any]] = []
    for entry in _read_pause_entries(root):
        if stats is not None:
            stats["liveness_calls"] = int(stats.get("liveness_calls") or 0) + 1
        try:
            alive = _pid_is_alive(entry["pid"], timeout=timeout)
        except subprocess.TimeoutExpired:
            alive = True
            if stats is not None:
                stats["liveness_probe_failed"] = (
                    int(stats.get("liveness_probe_failed") or 0) + 1
                )
        if alive:
            kept.append(entry)
    return kept
''',
)

# --- P-e: split the request and cleanup budgets (I-04-A D1/D2) ---------------
patch(
    "P-e request-cleanup-budget-split",
    """    def _remaining(self) -> float:
        return max(
            10.0,
            min(self.deadline - time.monotonic(), _WORKER_STATUS_TIMEOUT),
        )
""",
    '''    def _request_remaining(self) -> float:
        """Budget for a REQUEST-stage subcall (I-04-A D1/D3).

        Deliberately has no floor: once the deadline has passed this is <= 0 and
        the caller must NOT issue the call.  The old ``max(10.0, ...)`` minted a
        fresh 10 second request budget after the deadline (F-D2) - a pure status
        query is still a request, so exempting it would reopen the hole.
        """
        return min(self.deadline - time.monotonic(), _WORKER_STATUS_TIMEOUT)

    def _cleanup_timeout(self) -> float:
        """Independent cleanup budget C (I-04-A D2).

        Ownership restoration is not a request: it does not borrow the request
        deadline, and it is capped by the signed formula so a user-raised
        --worker-resume-wait-seconds cannot make it time out by construction.
        """
        return max(
            _CLEANUP_BUDGET_MIN_SECONDS,
            2.0 * self.resume_wait + self.graceful,
        )
''',
)

# --- P-f: __enter__ request-stage guards -----------------------------------
patch(
    "P-f enter-request-budget",
    """        if not self.enabled:
            self.action = "disabled"
            return self
        try:
            status = self._run("worker-status", timeout=self._remaining())
""",
    """        if not self.enabled:
            self.action = "disabled"
            return self
        remaining = self._request_remaining()
        if remaining <= 0:
            # I-04-A D3: a request-stage call after the deadline is forbidden.
            # No status, no pause, and therefore no cleanup obligation.
            self.action = "deadline_exhausted"
            return self
        try:
            status = self._run("worker-status", timeout=remaining)
""",
)

patch(
    "P-f2 register-uses-request-budget",
    """                self.action = "joined"
                self._register(joined=True)
""",
    """                self.action = "joined"
                self._register(joined=True, timeout=remaining)
""",
)

patch(
    "P-f3 pause-guard-and-budget",
    """        self._first = self._register(joined=False)
        if self._first:
            try:
                self._run(
                    "worker-pause",
                    "--graceful-timeout-seconds",
                    str(self.graceful),
                    timeout=self._remaining(),
                )
""",
    """        self._first = self._register(joined=False, timeout=remaining)
        if self._first:
            pause_remaining = self._request_remaining()
            if pause_remaining <= 0:
                # The deadline ran out between register and pause: withdraw the
                # refcount entry (local file ops) and issue no request call.
                self._unregister(timeout=self._cleanup_timeout())
                self.action = "deadline_exhausted"
                return self
            try:
                self._run(
                    "worker-pause",
                    "--graceful-timeout-seconds",
                    str(self.graceful),
                    timeout=pause_remaining,
                )
""",
)

patch(
    "P-f4 pause-failure-cleanup-budget",
    """                self.action = "pause_failed"
                self._unregister()
                try:
                    self._run(
                        "worker-resume",
                        "--wait-seconds",
                        str(self.resume_wait),
                        timeout=self._remaining(),
                    )
""",
    """                self.action = "pause_failed"
                self._unregister(timeout=self._cleanup_timeout())
                try:
                    self._run(
                        "worker-resume",
                        "--wait-seconds",
                        str(self.resume_wait),
                        timeout=self._cleanup_timeout(),
                    )
""",
)

# --- P-g: register/unregister take a phase budget ---------------------------
patch(
    "P-g register-unregister-budget",
    """    def _register(self, *, joined: bool) -> bool:
        entries = _prune_pause_entries(self.root)
""",
    """    def _register(self, *, joined: bool, timeout: float) -> bool:
        entries = _prune_pause_entries(self.root, timeout=timeout, stats=self.stats)
""",
)

patch(
    "P-g2 unregister-budget",
    """    def _unregister(self) -> bool:
        entries = _prune_pause_entries(self.root)
""",
    """    def _unregister(self, *, timeout: float) -> bool:
        entries = _prune_pause_entries(self.root, timeout=timeout, stats=self.stats)
""",
)

# --- P-h: __exit__ cleanup accounting (I-04-A D2/D5) ------------------------
patch(
    "P-h exit-cleanup-accounting",
    """    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.action not in {"paused_by_us", "joined"}:
            return
        if not self._unregister():
            return  # other participants still active; keep the worker paused
        try:
            self._run(
                "worker-resume",
                "--wait-seconds",
                str(self.resume_wait),
                timeout=self._remaining(),
            )
        except FilingFetchError as exc:
""",
    """    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        # I-04-A D5: the pause outcome is reported even when no cleanup is owed.
        if self.stats is not None:
            self.stats["pause_action"] = self.action
        if self.action not in {"paused_by_us", "joined"}:
            return
        cleanup_timeout = self._cleanup_timeout()
        if not self._unregister(timeout=cleanup_timeout):
            return  # other participants still active; keep the worker paused
        cleanup_started = time.monotonic()
        if self.stats is not None:
            self.stats["cleanup_calls"] = int(self.stats.get("cleanup_calls") or 0) + 1
        try:
            self._run(
                "worker-resume",
                "--wait-seconds",
                str(self.resume_wait),
                timeout=cleanup_timeout,
            )
        except FilingFetchError as exc:
            if self.stats is not None:
                self.stats["cleanup_status"] = f"failed:{exc.code}"
""",
)

patch(
    "P-h2 exit-cleanup-status-and-elapsed",
    """                f"company_wiki.source_catalog.cli worker-resume ({exc})",
                file=sys.stderr,
            )
""",
    """                f"company_wiki.source_catalog.cli worker-resume ({exc})",
                file=sys.stderr,
            )
        else:
            if self.stats is not None:
                self.stats["cleanup_status"] = "restored"
        if self.stats is not None:
            # I-04-A D2: cleanup latency is reported separately and never counted
            # into the request deadline (the old code had one wall number).
            self.stats["cleanup_elapsed_seconds"] = round(
                time.monotonic() - cleanup_started, 3
            )
""",
)

# --- P-i: stats keys + widened annotations ---------------------------------
patch(
    "P-i normalize-stats-keys",
    '''def _normalize_stats(stats: dict[str, int] | None) -> dict[str, int]:
    """Return a mutable reconciliation stats dict (ZR-205)."""
    if stats is None:
        stats = {}
    stats.setdefault("calls", 0)
    stats.setdefault("downloads", 0)
    return stats
''',
    '''def _normalize_stats(stats: dict[str, Any] | None) -> dict[str, Any]:
    """Return a mutable reconciliation stats dict (ZR-205).

    I-04-A D5: request timing, cleanup timing and liveness probes are separate
    keys, so a cleanup tail can never be read as request latency and a probe
    process is never invisible.
    """
    if stats is None:
        stats = {}
    stats.setdefault("calls", 0)
    stats.setdefault("downloads", 0)
    stats.setdefault("liveness_calls", 0)
    stats.setdefault("liveness_probe_failed", 0)
    stats.setdefault("cleanup_calls", 0)
    stats.setdefault("cleanup_status", "not_needed")
    return stats
''',
)

# --- P-j: request window stamping + envelope fields ------------------------
patch(
    "P-j stamp-helper",
    '''def _record_download_events(stats: dict[str, int] | None, handle: dict) -> None:
''',
    '''def _stamp_request_timing(
    stats: dict[str, Any] | None, started_monotonic: float, timeout_seconds: float
) -> None:
    """Record the request window (I-04-A D5.3) on success AND on failure.

    ``request_deadline`` is the monotonic instant the request budget expires and
    ``request_elapsed`` is measured in the same monotonic frame, so both are
    comparable with the subprocess timestamps the tests record.
    """
    if stats is None:
        return
    stats["request_deadline"] = round(started_monotonic + timeout_seconds, 6)
    stats["request_elapsed"] = round(time.monotonic() - started_monotonic, 3)


def _record_download_events(stats: dict[str, Any] | None, handle: dict) -> None:
''',
)

patch(
    "P-j2 main-start-stamp",
    """        stats = {"calls": 0, "downloads": 0}
        handle = resolve_filing(
""",
    """        stats = {"calls": 0, "downloads": 0}
        started_monotonic = time.monotonic()
        handle = resolve_filing(
""",
)

patch(
    "P-j3 success-envelope-fields",
    """                "calls": stats["calls"],
                "downloads": stats["downloads"],
            }
""",
    """                "calls": stats["calls"],
                "downloads": stats["downloads"],
                "request_deadline": stats.get("request_deadline"),
                "request_elapsed": stats.get("request_elapsed"),
                "pause_action": stats.get("pause_action"),
                "cleanup_calls": stats.get("cleanup_calls", 0),
                "cleanup_elapsed_seconds": stats.get("cleanup_elapsed_seconds"),
                "cleanup_status": stats.get("cleanup_status", "not_needed"),
                "liveness_calls": stats.get("liveness_calls", 0),
                "liveness_probe_failed": stats.get("liveness_probe_failed", 0),
            }
""",
)

patch(
    "P-j4 success-path-stamp",
    """        )
        if isinstance(handle, dict) and handle.get("status") == "gap":
""",
    """        )
        _stamp_request_timing(stats, started_monotonic, args.timeout_seconds)
        if isinstance(handle, dict) and handle.get("status") == "gap":
""",
)

patch(
    "P-j5 error-path-stamp-and-fields",
    """    except FilingFetchError as exc:
        error_response: dict[str, Any] = {
""",
    """    except FilingFetchError as exc:
        _stamp_request_timing(stats, started_monotonic, args.timeout_seconds)
        error_response: dict[str, Any] = {
""",
)

patch(
    "P-j6 error-envelope-fields",
    """        if "stats" in locals():
            error_response["calls"] = stats["calls"]
            error_response["downloads"] = stats["downloads"]
""",
    """        if "stats" in locals():
            error_response["calls"] = stats["calls"]
            error_response["downloads"] = stats["downloads"]
            error_response["request_deadline"] = stats.get("request_deadline")
            error_response["request_elapsed"] = stats.get("request_elapsed")
            error_response["pause_action"] = stats.get("pause_action")
            error_response["cleanup_calls"] = stats.get("cleanup_calls", 0)
            error_response["cleanup_elapsed_seconds"] = stats.get(
                "cleanup_elapsed_seconds"
            )
            error_response["cleanup_status"] = stats.get("cleanup_status", "not_needed")
            error_response["liveness_calls"] = stats.get("liveness_calls", 0)
            error_response["liveness_probe_failed"] = stats.get(
                "liveness_probe_failed", 0
            )
""",
)


def main() -> int:
    if "execution_runs" not in str(TARGET) or "I-04-B" not in str(TARGET):
        raise SystemExit(f"refusing to patch outside the I-04-B attempt dir: {TARGET}")
    if not TARGET.is_file():
        raise SystemExit(f"target missing: {TARGET}")
    text = TARGET.read_text(encoding="utf-8")
    original = text
    failures: list[str] = []
    for name, old, new in PATCHES:
        count = text.count(old)
        if count != 1:
            failures.append(f"{name}: expected exactly 1 match, found {count}")
            continue
        text = text.replace(old, new, 1)
        print(f"applied  {name}")
    # widen the remaining stats annotations (heterogeneous values now)
    widened = text.replace("stats: dict[str, int] | None", "stats: dict[str, Any] | None")
    print(f"applied  P-k stats-annotation-widened ({text.count('stats: dict[str, int] | None')} sites)")
    text = widened
    if failures:
        print("\nFAILED PATCHES:", *failures, sep="\n  ")
        return 1
    if text == original:
        raise SystemExit("no-op patch: nothing changed")
    TARGET.write_text(text, encoding="utf-8", newline="")
    print(f"\npatched {TARGET} ({len(PATCHES)} patches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
