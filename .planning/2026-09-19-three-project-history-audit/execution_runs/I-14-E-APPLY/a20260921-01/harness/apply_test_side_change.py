"""I-14-E-APPLY: apply the derived-timeout test-side change to the ISOLATED copies.

The change is expressed as two exact literal substitutions on the byte-identical
copy of the production test file.  Run with --check to verify the anchors without
writing anything.

  python apply_test_side_change.py --check
  python apply_test_side_change.py --apply --targets iso/T0 iso/T0b
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
SUITE_REL = "tests/contract/test_source_catalog_worker_bootstrap.py"

ANCHOR_LEN_ANCHOR = """def test_child_without_runtime_session_is_terminated_and_restarted(tmp_path):"""

# ---------------------------------------------------------------------------
# Substitution 1: the measured-throughput derivation, inserted immediately
# before the node it serves.
# ---------------------------------------------------------------------------
OLD_0 = """import json
import os
import shutil
import subprocess
import sys
import time
"""

NEW_0 = """import json
import math
import os
import shutil
import subprocess
import sys
import time
"""

OLD_1 = '''@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell launcher integration")
def test_child_without_runtime_session_is_terminated_and_restarted(tmp_path):
    project = _prepare_fake_launcher_project(
        tmp_path,
        [
            {"sleep_seconds": 5, "exit_code": 0},
            {"exit_code": 0},
        ],
    )

    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=0.5,
        child_poll_milliseconds=100,
    )
'''

NEW_1 = '''# ---------------------------------------------------------------------------
# I-14-E-APPLY: derive the watchdog hang timeout from an in-test measurement of
# this machine's child launch latency instead of assuming it fits inside a fixed
# constant.  Measured basis (I-14-E/a20260919-01, independent window, n=111, no
# pytest and no watchdog): launch -> exit median 0.691 s quiet (24/30 >= 0.5 s)
# and 1.351 s under +8 burners (25/25), with an upper tail of 1.7-2.5 s; the same
# quantity in the frozen band was median 0.2245 s, max 0.622 s.  The 0.5 s
# constant therefore straddles the distribution it is compared against, and only
# the alignment of the exit with the poll boundary decides the outcome.
#
# The quantity the supervisor's watchdog actually compares is its own
# ``(Get-Date) - $StartedAt``, i.e. POST-``Start-Process`` uptime, so t0 is
# measured THROUGH the real launcher rather than by spawning the child directly.
# This is not an assertion loosening: ``child_started == 2`` and every semantic
# assertion of the node are unchanged, and a genuinely hung child is still
# terminated (see test_derived_hang_timeout_still_terminates_a_genuinely_hung_child).
# ---------------------------------------------------------------------------

_LAUNCH_SAMPLES = 3
_LAUNCH_MARGIN_FACTOR = 4.0
_HANG_TIMEOUT_FLOOR_SECONDS = 2.0
# Upper bound derived from the node's OWN fixture product: child #1 carries the
# ``sleep_seconds 5`` behaviour, so the watchdog must still fire well inside that
# sleep for the node's semantics ("a child with no runtime session is terminated")
# to hold.  4 s leaves >= 2 s of margin against the 5 s sleep.
_HANG_TIMEOUT_CEILING_SECONDS = 4.0


def _child_launch_latencies(project: Path) -> list[float]:
    """Launch -> end-of-that-child lifetimes recorded by the real launcher.

    A sample ends either as ``exited`` (the child finished on its own) or as
    ``child_unresponsive`` (the launcher's *default* 0.5 s watchdog killed it
    first).  Both forms bound the same quantity - how long this machine takes to
    get a child through launch to the point the watchdog is watching - so both
    count.  Returns [] when no launcher-event timeline was produced.
    """
    path = project / ".source_catalog" / "worker_launcher_events.jsonl"
    if not path.exists():
        return []
    latencies: list[float] = []
    try:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            if event.get("status") == "child_unresponsive":
                uptime = event.get("uptime_seconds")
            elif event.get("status") == "exited":
                uptime = event.get("uptime_seconds")
            else:
                continue
            if uptime is not None:
                latencies.append(float(uptime))
    except (OSError, ValueError):  # pragma: no cover - a torn timeline is not a latency
        return []
    return latencies


def _measure_child_launch_latency_samples(
    tmp_path: Path, samples: int = _LAUNCH_SAMPLES
) -> list[float]:
    """Return the observed child launch latencies, measured in-test.

    A single-behaviour (immediate exit) sentinel product is driven through the REAL
    launcher ``samples`` times.  Each launcher invocation yields one launch -> lifetime
    reading (either the child exited on its own, or the launcher's default 0.5 s
    watchdog killed it first - both bound the same quantity).
    """
    warmup_root = tmp_path / "hang-timeout-warmup"
    warmup_root.mkdir(parents=True, exist_ok=True)
    warmup = _prepare_fake_launcher_project(warmup_root, [{"exit_code": 0}])
    observed: list[float] = []
    for _ in range(max(1, samples)):
        # The launcher is allowed to exit on its own: with a single immediate-exit
        # behaviour the watchdog either lets the child go or kills it and restarts,
        # and either way the timeline records one launch -> lifetime reading.
        _run_real_worker_launcher(warmup, timeout=15, child_poll_milliseconds=100)
        observed.extend(_child_launch_latencies(warmup))
    return observed


def _measure_child_launch_latency(tmp_path: Path, samples: int = _LAUNCH_SAMPLES) -> float:
    """t0 = the MAXIMUM observed launch latency (the conservative end of the sample:
    a low draw here under-budgets the run that is actually asserted)."""
    observed = _measure_child_launch_latency_samples(tmp_path, samples)
    return max(observed) if observed else 0.0


def _derive_worker_hang_timeout_seconds(tmp_path: Path) -> int:
    """Derive the watchdog hang timeout from an in-test measurement (I-14-E item 1).

    ``max(2.0, 4 * t0)`` with t0 measured by ``_measure_child_launch_latency``,
    capped at the node's own semantic upper bound and rounded UP to whole seconds
    (the launcher takes the value as a PowerShell parameter; whole seconds remove
    any argument-formatting ambiguity, and rounding up only widens the window).

    The derivation is self-evidencing: it writes the observed samples, the derived
    value and the value the launcher is about to receive into
    ``tmp_path/hang_timeout_derivation.json`` so that a reviewer can read the
    measurement back from the run itself instead of trusting the log.
    """
    observed = _measure_child_launch_latency_samples(tmp_path)
    t0 = max(observed) if observed else 0.0
    derived = min(
        _HANG_TIMEOUT_CEILING_SECONDS,
        max(_HANG_TIMEOUT_FLOOR_SECONDS, _LAUNCH_MARGIN_FACTOR * t0),
    )
    hang_timeout_seconds = int(math.ceil(derived))
    report = {
        "node": "child_without_runtime",
        "samples_seconds": observed,
        "t0_seconds": t0,
        "aggregator": "max",
        "samples_requested": _LAUNCH_SAMPLES,
        "samples_observed": len(observed),
        "margin_factor": _LAUNCH_MARGIN_FACTOR,
        "floor_seconds": _HANG_TIMEOUT_FLOOR_SECONDS,
        "ceiling_seconds": _HANG_TIMEOUT_CEILING_SECONDS,
        "derived_before_ceiling_seconds": derived,
        "hang_timeout_seconds": hang_timeout_seconds,
        "child_poll_milliseconds": 100,
        "measured_by": "_measure_child_launch_latency (real launcher, default 0.5s watchdog)",
    }
    try:  # lenient: a report failure must never decide a test outcome
        (tmp_path / "hang_timeout_derivation.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
    except OSError:
        pass
    return hang_timeout_seconds


@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell launcher integration")
def test_child_without_runtime_session_is_terminated_and_restarted(tmp_path):
    project = _prepare_fake_launcher_project(
        tmp_path,
        [
            {"sleep_seconds": 5, "exit_code": 0},
            {"exit_code": 0},
        ],
    )

    hang_timeout_seconds = _derive_worker_hang_timeout_seconds(tmp_path)
    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=hang_timeout_seconds,
        child_poll_milliseconds=100,
    )
'''
# ---------------------------------------------------------------------------
# Substitution 2: the non-vacuity node, appended after the node above.
# ---------------------------------------------------------------------------
OLD_2 = '''    assert unresponsive["reason"] == "session_start_timeout"
    assert restarting["reason"] == "session_start_timeout"
    assert len([event for event in events if event["status"] == "child_started"]) == 2
'''

NEW_2 = '''    assert unresponsive["reason"] == "session_start_timeout"
    assert restarting["reason"] == "session_start_timeout"
    assert len([event for event in events if event["status"] == "child_started"]) == 2


@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell launcher integration")
def test_derived_hang_timeout_still_terminates_a_genuinely_hung_child(tmp_path):
    """I-14-E-APPLY non-vacuity proof: the DERIVED timeout still fires.

    The node above proves termination with a child that exits on its own, so a
    derived timeout large enough to never fire would make its assertion vacuous
    while still looking green.  Here the child that follows the restart is a
    genuinely hung one (``sleep_seconds 30``, no runtime session), so the watchdog
    MUST fire twice: once for the session-less first child and once for the hung
    child that replaced it.  That produces a THIRD ``child_started``, which is
    exactly the condition under which the node above fails.
    """
    project = _prepare_fake_launcher_project(
        tmp_path,
        [
            {"sleep_seconds": 5, "exit_code": 0},
            {"sleep_seconds": 30, "exit_code": 0},
            {"exit_code": 0},
        ],
    )

    hang_timeout_seconds = _derive_worker_hang_timeout_seconds(tmp_path)
    completed = _run_real_worker_launcher(
        project,
        timeout=15,
        worker_hang_timeout_seconds=hang_timeout_seconds,
        child_poll_milliseconds=100,
    )

    assert completed.returncode == 0, completed.stderr
    events = _launcher_events(project)
    unresponsive = [event for event in events if event["status"] == "child_unresponsive"]
    assert unresponsive, (
        "watchdog never fired: the derived hang timeout is vacuous "
        f"({hang_timeout_seconds}s)"
    )
    assert all(event["reason"] == "session_start_timeout" for event in unresponsive)
    # the kill must land just past the DERIVED budget, not at some unrelated value
    for event in unresponsive:
        assert event["uptime_seconds"] <= hang_timeout_seconds + 1.0, event
    starts = [event for event in events if event["status"] == "child_started"]
    assert len(starts) == 3, (
        "the genuinely hung child was NOT terminated -> the derived timeout is "
        f"vacuous ({hang_timeout_seconds}s, starts={len(starts)})"
    )
'''

TARGETS = [SUITE_REL]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--targets", nargs="*", default=["iso/T0", "iso/T0b"])
    parser.add_argument("--suite", default=SUITE_REL)
    args = parser.parse_args(argv)

    if not (args.apply or args.check):
        parser.error("pass --apply or --check")

    rc = 0
    for target in args.targets:
        path = ATT / target / args.suite
        text = path.read_text(encoding="utf-8")
        if OLD_1 not in text:
            print(f"ANCHOR-1 MISSING in {path}")
            rc = 1
            continue
        if text.count(OLD_0) != 1:
            print(f"IMPORT ANCHOR AMBIGUOUS in {path}: {text.count(OLD_0)}")
            rc = 1
            continue
        if text.count(OLD_1) != 1 or text.count(OLD_2) != 1:
            print(f"ANCHOR AMBIGUOUS in {path}: {text.count(OLD_1)}/{text.count(OLD_2)}")
            rc = 1
            continue
        if ANCHOR_LEN_ANCHOR not in text:
            print(f"NODE ANCHOR MISSING in {path}")
            rc = 1
            continue
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        new_text = (text.replace(OLD_0, NEW_0, 1)
                        .replace(OLD_1, NEW_1, 1)
                        .replace(OLD_2, NEW_2, 1))
        if args.apply:
            # keep the file UTF-8 without BOM and with the original newline style
            path.write_bytes(new_text.encode("utf-8"))
        after = hashlib.sha256(new_text.encode("utf-8")).hexdigest()
        print(f"{'APPLIED ' if args.apply else 'CHECK-OK'} {path}")
        print(f"  before={before}")
        print(f"  after ={after}")
        if not args.apply:
            print(f"  +{len(new_text.splitlines()) - len(text.splitlines())} lines")
    return rc


if __name__ == "__main__":
    sys.exit(main())
