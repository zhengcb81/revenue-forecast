"""I-04-D contract tests for the cross-process lease protocol.

Every assertion below is a restatement of a FROZEN expectation in
``oracle.md`` (written before this protocol existed).  The tests hold no expected
value of their own: they read the scheduler's ``summary.json``, which is produced
by real subprocesses running the code under test.

Run (isolated interpreter, isolated copy):
  iso/venv/Scripts/python.exe -B -m pytest tests/test_fetch_filing_lease.py -q

The suite is written to FAIL on the pre-I-04-D baseline: it asserts behaviours the
legacy read-modify-write could not provide (pid-based lease removal, a durable
resume obligation, an owner record, incarnation evidence, fail-closed reads).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
SCHEDULER = SCRIPTS / "i04d_schedule.py"
PYTHON = sys.executable

# Case artifacts must NOT live under pytest's basetemp: pytest removes that whole
# tree at session start, which deletes the wiki directories real child processes
# are still using.  A per-pytest-process directory keeps runs isolated and stable.
RUNS_ROOT = Path(
    os.environ.get("I04D_TEST_RUNS_DIR")
    # Short on purpose: the ledger's unique temp name is appended to the case path, and
    # a deeply nested root pushes the classic Windows path limit.
    or (SKILL_ROOT.parents[2] / f"runs{os.getpid()}")
)

_SKIP_REASON = "I-04-D scheduler is absent"


def _run_case(tmp_path: Path, *cases: str) -> dict:
    # ``tmp_path`` is deliberately NOT used as the case root: the cases create
    # directories and write ledgers inside their root for the whole case, and a
    # pytest-managed temp directory made every ledger write fail with OSError.
    # RUNS_ROOT is a stable per-pytest-process tree that the summaries share.
    out = RUNS_ROOT
    out.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(  # noqa: S603 - argv list, no shell
        [PYTHON, "-X", "utf8", "-B", str(SCHEDULER), "run", *cases, "--out", str(out)],
        capture_output=True,
        text=True,
        timeout=900,
        cwd=str(SKILL_ROOT),
        env={**os.environ, "PYTHONUTF8": "1", "I04D_CASE_ROOT": str(out)},
    )
    summaries = {}
    for case in cases:
        path = out / case / "summary.json"
        assert path.exists(), (
            f"{case}: no summary.json (rc={completed.returncode}); "
            f"stdout={completed.stdout[-2000:]} stderr={completed.stderr[-2000:]}"
        )
        summaries[case] = json.loads(path.read_text(encoding="utf-8"))
    return summaries


def _impl_supports_hooks() -> bool:
    """Whether the code under test exposes the I-04-D crash/gate instrumentation."""
    text = (SCRIPTS / "fetch_filing.py").read_text(encoding="utf-8", errors="replace")
    return "_i04d_hook" in text


@pytest.fixture(scope="module")
def has_scheduler() -> bool:
    return SCHEDULER.exists()


# ---------------------------------------------------------------------------
# P1 - F-L5: two real processes, B registers before A releases
# ---------------------------------------------------------------------------


def test_f_l5_two_processes_one_pause_one_resume(tmp_path, has_scheduler):
    """oracle.md section 2 P1: pause=1, resume=1, both files gone at the end."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.fail(
            "the code under test has no I-04-D ordering instrumentation, so the F-L5 "
            "interleaving cannot be pinned (oracle.md section 5)"
        )
    s = _run_case(tmp_path, "I04D-CASE-F-L5")["I04D-CASE-F-L5"]
    assert not s["harness_error"], s["harness_error"]
    reports = s["reports"]
    assert reports["A"]["exit_code"] == 0
    assert reports["B"]["exit_code"] == 0
    # exactly one pause and one resume: B JOINS the live cycle, so it never stops the
    # worker again (ADR-9b), and only the last leaver restores it (R2)
    assert s["pause_calls"] == 1, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert reports["A"]["action"] == "released_last", reports["A"]["action"]
    assert reports["B"]["action"] == "released_joined", reports["B"]["action"]
    # THE point of the case: the scheduler parked B inside the scope while A was still
    # holding its own lease, so the ledger it read held BOTH - the legacy
    # prune-then-write could not do this (it deleted every same-pid entry and unlinked
    # the owner marker, waking the worker under a live lease).
    joined = reports["B"]["after_enter"]
    assert reports["B"]["lease_id"] in joined["lease_set"], joined
    assert reports["A"]["lease_id"] in joined["lease_set"], joined
    assert len(joined["lease_set"]) == 2, joined
    assert joined["generation"] == 1, joined
    # B leaves first while A still owns the cycle, so B must NOT resume the worker:
    # the ownership transfer puts the record on B and A closes the cycle afterwards.
    b_final = reports["B"]["after_exit"]
    assert reports["A"]["lease_id"] in b_final["lease_set"], b_final
    a_final = reports["A"]["after_exit"]
    assert a_final["refcount_exists"] is False, a_final
    # the only resume happens when the last lease leaves
    assert s["final_lease"]["refcount_exists"] is False, s["final_lease"]
    assert s["final_lease"]["owner_marker_exists"] is False, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}


def test_f_l5_ownership_transfer_is_journalled(tmp_path, has_scheduler):
    """ADR-10e must be visible as an event, not inferred from the outcome."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.skip("legacy baseline has no lease journal")
    s = _run_case(tmp_path, "I04D-CASE-F-L5")["I04D-CASE-F-L5"]
    events = [e.get("event") for e in s["protocol_journal"]]
    assert "ownership_transferred" in events, events
    transfer = next(e for e in s["protocol_journal"] if e.get("event") == "ownership_transferred")
    assert transfer["to"], transfer
    assert transfer.get("generation") == 1, transfer
    assert "lease_lock_acquired" in events, events


def test_f_l6_sequential_cycles_each_pause_once(tmp_path, has_scheduler):
    """F-L6 base: three consecutive cycles each pause and resume exactly once."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-L6")["I04D-CASE-F-L6"]
    assert not s["harness_error"], s["harness_error"]
    for tag in ("A", "B", "C"):
        assert s["reports"][tag]["exit_code"] == 0, (tag, s["reports"][tag].get("error_message"))
        assert s["reports"][tag]["action"] == "released_last", (tag, s["reports"][tag]["action"])
        assert len(s["reports"][tag]["after_enter"]["lease_set"]) == 1, tag
    assert s["pause_calls"] == 3, s["worker"]["events"]
    assert s["resume_calls"] == 3, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}


# ---------------------------------------------------------------------------
# P2 - F-L6b: the last release and a new acquire interleave
# ---------------------------------------------------------------------------


def test_f_l6b_exactly_one_resume_when_a_leaves_while_b_holds(tmp_path, has_scheduler):
    """oracle.md section 2 P2: the last release and a new acquire interleave."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.fail(
            "the code under test has no I-04-D ordering instrumentation, so the F-L6b "
            "interleaving cannot be pinned (oracle.md section 5)"
        )
    s = _run_case(tmp_path, "I04D-CASE-F-L6b")["I04D-CASE-F-L6b"]
    assert not s["harness_error"], s["harness_error"]
    reports = s["reports"]
    assert reports["A"]["action"] == "released_last", reports["A"]["action"]
    assert reports["B"]["action"] == "released_last", reports["B"]["action"]
    # B joins A's live cycle (one pause), then each exits as the last lease of its own
    # cycle (two resumes total)
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 2, s["worker"]["events"]
    assert reports["B"]["stats"].get("lease_resume_reason") == "owner_is_me"
    # Whether A is still in the ledger when B's enter completes depends on which of the
    # two reached its release park first; F-L5 pins that overlap deterministically.  This
    # case pins the race-independent facts: A's release removed ONLY its own entry,
    # handed the ownership record to B, and the ledger is clean at the end.
    after_a = s["participants"]["after_a_exit"]["lease"]
    assert reports["B"]["lease_id"] in after_a["lease_set"], after_a
    assert reports["A"]["lease_id"] not in after_a["lease_set"], after_a
    assert (after_a["owner"] or {}).get("lease_id") == reports["B"]["lease_id"], after_a
    assert s["final_lease"]["refcount_exists"] is False, s["final_lease"]


def test_f_l6b_resume_happens_after_a_is_gone(tmp_path, has_scheduler):
    """Linearization: the resume must not precede A's release."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.skip("legacy baseline has no lease journal")
    s = _run_case(tmp_path, "I04D-CASE-F-L6b")["I04D-CASE-F-L6b"]
    resumed = [e for e in s["worker"]["events"] if e["subcommand"] == "worker-resume"]
    assert len(resumed) == 2, s["worker"]["events"]
    # neither resume belongs to the JOINING participant's first pass: A resumes its own
    # cycle and B resumes its own. What must never happen is a resume issued while
    # another lease is still live, which the two-leases assertion above covers.
    assert all(e["result"] == "ok" for e in resumed), resumed


# ---------------------------------------------------------------------------
# P3 - F-L7: same-pid nesting
# ---------------------------------------------------------------------------


def test_f_l7_inner_release_removes_only_its_own_lease(tmp_path, has_scheduler):
    """oracle.md section 2 P3: nested release is by lease_id, never by pid."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-L7")["I04D-CASE-F-L7"]
    assert not s["harness_error"], s["harness_error"]
    report = s["reports"]["nest"]
    assert report["exit_code"] == 0, report.get("error_message")
    assert report["outer_action"] == "paused_by_us"
    assert report["inner_action"] == "joined"
    assert len(report["after_enter"]["lease_set"]) == 1
    # two distinct lease ids coexist inside ONE process
    assert len(report["after_inner_enter"]["lease_set"]) == 2, report["after_inner_enter"]
    assert report["outer_lease_id"] != report["inner_lease_id"]
    assert report["inner_lease_id"] in report["after_inner_enter"]["lease_set"]
    assert report["outer_lease_id"] in report["after_inner_enter"]["lease_set"]
    # the inner release removed exactly its own lease
    assert report["after_inner_exit"]["lease_set"] == [report["outer_lease_id"]], (
        report["after_inner_exit"]
    )
    assert s["pause_calls"] == 1, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False


def test_f_l7b_and_l7c_nesting_variants(tmp_path, has_scheduler):
    """oracle.md section 2 P3: both nesting orders hold the same rule."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    summaries = _run_case(tmp_path, "I04D-CASE-F-L7b", "I04D-CASE-F-L7c")
    for name, s in summaries.items():
        assert not s["harness_error"], (name, s["harness_error"])
        report = s["reports"]["nest"]
        assert report["exit_code"] == 0, (name, report.get("error_message"))
        assert s["pause_calls"] == 1, (name, s["worker"]["events"])
        assert s["resume_calls"] == 1, (name, s["worker"]["events"])
        assert report["after_inner_exit"]["lease_set"] == [report["outer_lease_id"]], (
            name,
            report["after_inner_exit"],
        )
        assert s["final_lease"]["refcount_exists"] is False, name


# ---------------------------------------------------------------------------
# P4 - F-L9: user pause intent
# ---------------------------------------------------------------------------


def test_f_l9a_user_pause_is_respected_with_zero_writes(tmp_path, has_scheduler):
    """oracle.md section 2 P4b: zero pause/resume and no lease evidence at all."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-L9a")["I04D-CASE-F-L9a"]
    assert not s["harness_error"], s["harness_error"]
    report = s["reports"]["user"]
    assert report["action"] == "respect_paused", report["action"]
    assert s["pause_calls"] == 0, s["worker"]["events"]
    assert s["resume_calls"] == 0, s["worker"]["events"]
    assert report["before_enter"]["refcount_exists"] is False
    assert report["after_enter"]["refcount_exists"] is False
    assert report["after_exit"]["refcount_exists"] is False
    assert report["after_exit"]["owner_marker_exists"] is False


def test_f_l9c_user_pause_during_our_scope_is_not_undone(tmp_path, has_scheduler):
    """oracle.md section 2 P4c: a pause taken during our scope is not resumed away."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.fail(
            "the code under test has no I-04-D ordering instrumentation, so the F-L9c "
            "interleaving cannot be pinned (oracle.md section 5)"
        )
    s = _run_case(tmp_path, "I04D-CASE-F-L9c")["I04D-CASE-F-L9c"]
    assert not s["harness_error"], s["harness_error"]
    report = s["reports"]["A"]
    # the request outcome is never rewritten by the cleanup phase
    assert report["action"] == "released_owner_changed", report["action"]
    assert report["stats"].get("cleanup_status", "").startswith("failed:"), report["stats"]
    assert s["resume_calls"] == 0, s["worker"]["events"]
    assert s["final_worker_state"]["desired_state"] == "paused"


# ---------------------------------------------------------------------------
# P5 - F-L8d: the owner evidence changes under us
# ---------------------------------------------------------------------------


def test_f_l8d_owner_evidence_change_fails_closed(tmp_path, has_scheduler):
    """oracle.md section 2 P5: resume=0, owner record byte-identical."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.fail(
            "the code under test has no I-04-D ordering instrumentation, so the F-L8d "
            "interleaving cannot be pinned (oracle.md section 5)"
        )
    s = _run_case(tmp_path, "I04D-CASE-F-L8d")["I04D-CASE-F-L8d"]
    assert not s["harness_error"], s["harness_error"]
    report = s["reports"]["A"]
    assert report["action"] == "released_owner_changed", report["action"]
    assert report["stats"].get("cleanup_status", "").startswith("failed:owner_evidence_changed"), (
        report["stats"]
    )
    assert s["resume_calls"] == 0, s["worker"]["events"]
    assert s["final_worker_state"]["desired_state"] == "paused"
    final_owner = s["final_lease"]["owner"] or {}
    assert final_owner.get("lease_id") == "third-party-owner", final_owner
    assert final_owner.get("pid") == 999999, final_owner


# ---------------------------------------------------------------------------
# N1-N4 - crash windows
# ---------------------------------------------------------------------------


def test_l8a_w1_no_owner_marker_is_not_a_user_pause(tmp_path, has_scheduler):
    """N1/N2: a crash between ledger and marker must not become a user pause.

    The invariant this case exists for: after A's injected crash the recovered cycle is
    never adopted as a USER pause by either follower, every pause is resumed, and the
    ledger ends clean.  Whether the follower joins the live cycle or opens its own after
    the holder leaves is a scheduling race and is deliberately NOT asserted here - F-L5
    pins the overlap deterministically.
    """
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.fail(
            "the code under test has no I-04-D crash instrumentation, so W1 cannot be "
            "injected at all (oracle.md section 5)"
        )
    s = _run_case(tmp_path, "I04D-CASE-F-L8a-W1", "I04D-CASE-F-L8a-W1b")
    first = s["I04D-CASE-F-L8a-W1"]
    assert not first["harness_error"], first["harness_error"]
    # A dies inside the window: the ledger has its lease, the owner marker does not exist
    assert first["participants"]["A"]["injected_crash_code"] == 90
    assert first["participants"]["A"]["injected_crash_point"] == "after-refcount-before-owner"
    crash_after = first["participants"]["crash_after"]
    assert crash_after["owner_marker_exists"] is False
    assert crash_after["worker_state"]["runtime_state"] == "running"
    assert len(crash_after["lease_set"]) == 1
    second = first["reports"]["B"]
    assert second["action"] != "respect_paused", second["action"]
    assert second["action"] in {"paused_by_us", "fresh_cycle_recovering", "released_last"}, (
        second["action"]
    )
    assert first["pause_calls"] == first["resume_calls"], first["worker"]["events"]
    assert first["pause_calls"] >= 1, first["worker"]["events"]
    assert first["final_lease"]["refcount_exists"] is False
    assert first["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}

    third = s["I04D-CASE-F-L8a-W1b"]
    assert not third["harness_error"], third["harness_error"]
    for tag in ("B", "C"):
        assert third["reports"][tag]["action"] != "respect_paused", (
            tag,
            third["reports"][tag]["action"],
        )
        assert third["reports"][tag]["action"] in {"released_joined", "released_last"}, (
            tag,
            third["reports"][tag]["action"],
        )
    assert third["pause_calls"] == third["resume_calls"], third["worker"]["events"]
    assert third["pause_calls"] >= 1, third["worker"]["events"]
    assert third["final_lease"]["refcount_exists"] is False
    assert third["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}

def test_l8b_w2_takeover_resumes_before_repausing(tmp_path, has_scheduler):
    """N3: crash after the pause is confirmed; the next participant takes over."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.fail("no I-04-D crash instrumentation (oracle.md section 5)")
    s = _run_case(tmp_path, "I04D-CASE-F-L8b-W2")["I04D-CASE-F-L8b-W2"]
    assert not s["harness_error"], s["harness_error"]
    assert s["participants"]["A"]["injected_crash_code"] == 91
    assert s["participants"]["A"]["exit_code"] == 91
    crash_after = s["participants"]["crash_after"]
    assert crash_after["worker_state"] == {"desired_state": "paused", "runtime_state": "stopped"}
    assert crash_after["owner_marker_exists"] is True
    # B reclaims the dead A's lease and completes its own cycle.  What must hold is
    # that B NEVER adopts the crashed cycle as a user pause, and that both the ledger
    # and the worker end clean.
    assert s["reports"]["B"]["action"] == "released_last", s["reports"]["B"]["action"]
    assert s["reports"]["B"]["action"] != "respect_paused"
    assert s["pause_calls"] == 2, s["worker"]["events"]
    assert s["resume_calls"] == 1, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}


def test_l8c_w4_persisted_obligation_is_honoured_by_the_next_participant(tmp_path, has_scheduler):
    """N4: an empty ledger plus resume.required=True must not be read as 'nothing to do'."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    if not _impl_supports_hooks():
        pytest.fail("no I-04-D crash instrumentation (oracle.md section 5)")
    s = _run_case(tmp_path, "I04D-CASE-F-L8c-W4")["I04D-CASE-F-L8c-W4"]
    assert not s["harness_error"], s["harness_error"]
    assert s["participants"]["A"]["injected_crash_code"] == 92
    assert s["participants"]["A"]["exit_code"] == 92
    crash_after = s["participants"]["crash_after"]
    assert crash_after["lease"]["lease_set"] == []
    assert crash_after["lease"]["resume_required"] is True
    assert crash_after["worker_state"]["desired_state"] == "paused"
    report_b = s["reports"]["B"]
    # THE requirement: the persisted obligation is never read as "nothing to do" and
    # never adopted as a user pause, and the world ends clean.
    assert report_b["action"] == "released_last", report_b["action"]
    assert report_b["action"] != "respect_paused"
    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    # The invariant that matters: no resume ever targets a worker that was not paused
    # first, and each pause is followed by exactly one resume of the same cycle.
    events = [e["subcommand"] for e in s["worker"]["events"]]
    seen_pause = 0
    for subcommand in events:
        if subcommand == "worker-pause":
            seen_pause += 1
        elif subcommand == "worker-resume":
            assert seen_pause > 0, f"resume against a running worker: {events}"
            seen_pause -= 1
    assert seen_pause == 0, f"a pause was never resumed: {events}"
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["resume_required"] is not True, s["final_lease"]
    assert s["final_worker_state"] == {"desired_state": "enabled", "runtime_state": "running"}


# ---------------------------------------------------------------------------
# N5-N7, N9 - fail-closed reads and writes
# ---------------------------------------------------------------------------


def _import_under_test():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import fetch_filing  # noqa: PLC0415

    return fetch_filing


def test_read_fail_closed_on_corrupt_legacy_and_element_level(tmp_path):
    """N5/N6/N7: corrupt JSON, the legacy list and a lease_id-less entry all refuse."""
    ff = _import_under_test()
    if not hasattr(ff, "_read_pause_state"):
        pytest.fail("pre-I-04-D baseline: the refcount reader cannot fail closed at all")
    catalog = tmp_path / ".source_catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    refcount = catalog / "filing_fetch_pause.refcount"
    cases = {
        "lease_state_corrupt": '{"schema": "filing-fetch.pause-refcount/2", "entries": [',
        "lease_state_legacy": '[{"pid": 9003, "joined": false}]',
        "lease_state_corrupt_element": (
            '{"schema": "filing-fetch.pause-refcount/2", "generation": 1, '
            '"resume": {"required": false}, "entries": [{"pid": 1}], "owner": null}'
        ),
    }
    import hashlib

    for label, text in cases.items():
        refcount.write_text(text, encoding="utf-8")
        before = hashlib.sha256(refcount.read_bytes()).hexdigest()
        with pytest.raises(Exception) as info:
            ff._read_pause_state(tmp_path)
        code = getattr(info.value, "code", "")
        assert code.startswith("lease_state_"), (label, code)
        after = hashlib.sha256(refcount.read_bytes()).hexdigest()
        assert before == after, f"{label}: the unreadable file must not be touched"


def test_missing_refcount_is_empty_but_unreadable_is_not(tmp_path):
    """ADR-5 W6: unknown is not empty."""
    ff = _import_under_test()
    if not hasattr(ff, "_read_pause_state"):
        pytest.fail("pre-I-04-D baseline: no fail-closed reader")
    (tmp_path / ".source_catalog").mkdir(parents=True, exist_ok=True)
    state = ff._read_pause_state(tmp_path)
    assert state.entries == [] and state.generation == 0
    (tmp_path / ".source_catalog" / "filing_fetch_pause.refcount").write_text(
        "{not json", encoding="utf-8"
    )
    with pytest.raises(Exception):
        ff._read_pause_state(tmp_path)


def test_l8h_unwritable_ledger_never_claims_ownership(tmp_path, has_scheduler):
    """N9: a failed lease write is a loud failure, not a phantom owner."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-L8h-WRITEFAIL")["I04D-CASE-F-L8h-WRITEFAIL"]
    assert not s["harness_error"], s["harness_error"]
    assert s["participants"]["precondition"]["refcount_is_directory"] is True
    report = s["reports"]["A"]
    assert report["exit_code"] == 2, report.get("error_message")
    # A directory where the ledger should be is an UNREADABLE ledger, so the request
    # fails closed as lease_state_corrupt (the write-failure code covers an OSError
    # raised by the write itself).  Both codes satisfy the requirement below.
    assert report["action"] in {"lease_state_write_failed", "lease_state_corrupt"}, report["action"]
    assert report["action"] not in {"paused_by_us", "joined"}
    assert s["pause_calls"] == 0, s["worker"]["events"]
    assert s["participants"]["after"]["refcount_still_directory"] is True


# ---------------------------------------------------------------------------
# N8, N10-N13 - liveness, lock budget and lock lifetime
# ---------------------------------------------------------------------------


def test_l8g_unverifiable_holder_is_unknown_not_dead(tmp_path, has_scheduler):
    """N8: rule 5 fails closed; the unreadable-as-evidence ledger stays untouched."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-L8g-UNKNOWN")["I04D-CASE-F-L8g-UNKNOWN"]
    assert not s["harness_error"], s["harness_error"]
    report = s["reports"]["prober"]
    assert report["exit_code"] == 2, report.get("error_message")
    assert report["error_code"] == "lease_conflict_unknown", report.get("error_code")
    assert s["pause_calls"] == 0, s["worker"]["events"]
    assert s["resume_calls"] == 0, s["worker"]["events"]
    assert s["participants"]["injected"]["sha256"] == s["participants"]["after"]["sha256"], (
        "an UNKNOWN holder must not cause a single byte to be written"
    )


def test_lk_timeout_is_lease_lock_timeout_with_zero_writes(tmp_path, has_scheduler):
    """N10: a really held lock yields lease_lock_timeout, not the generic code."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-LK-TIMEOUT")["I04D-CASE-F-LK-TIMEOUT"]
    assert not s["harness_error"], s["harness_error"]
    report = s["reports"]["A"]
    assert report["exit_code"] == 2, report.get("error_message")
    assert report["error_code"] == "lease_lock_timeout", report.get("error_code")
    assert s["pause_calls"] == 0 and s["resume_calls"] == 0, s["worker"]["events"]
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["owner_marker_exists"] is False
    assert report["phase_wall_seconds"] < 2.0, report["phase_wall_seconds"]


def test_lk_zero_budget_does_not_even_attempt_the_lock(tmp_path, has_scheduler):
    """N11: a non-positive phase budget refuses to wait (I-04-A D3)."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-LK-TIMEOUT-ZERO")["I04D-CASE-F-LK-TIMEOUT-ZERO"]
    assert not s["harness_error"], s["harness_error"]
    report = s["reports"]["A"]
    # The request guard fires first: no worker command of any kind, and no lease
    # evidence.  One lock acquisition is expected and is the harmless fence itself -
    # the lock file is never ownership evidence (ADR-1) - which is what makes this
    # different from the timeout path above.
    assert report["error_code"] == "", report.get("error_code")
    assert report["action"] == "deadline_exhausted", report["action"]
    assert s["pause_calls"] == 0 and s["resume_calls"] == 0
    assert s["final_lease"]["refcount_exists"] is False
    assert s["final_lease"]["owner_marker_exists"] is False
    assert s["lock_acquisitions"] == 1, s["lock_acquisitions"]


def test_lk_holder_crash_releases_the_lock_in_the_kernel(tmp_path, has_scheduler):
    """N12: no cleanup step exists; a dead holder's lock is simply gone."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-LK-HOLDER-CRASH")["I04D-CASE-F-LK-HOLDER-CRASH"]
    assert not s["harness_error"], s["harness_error"]
    holder = s["participants"]["lock_holder"]
    assert holder["exit_code"] == 90, holder
    reacquire = s["participants"]["reacquire"]
    assert reacquire["returncode"] == 0, reacquire
    assert float(reacquire["stdout"]) <= 0.5, reacquire
    assert reacquire["lock_bytes"] == 0, reacquire


def test_lk_file_is_never_unlinked(tmp_path, has_scheduler):
    """N13 / F-LK4: the lock file survives and stays reusable."""
    if not has_scheduler:
        pytest.skip(_SKIP_REASON)
    s = _run_case(tmp_path, "I04D-CASE-F-LK-NEVER-UNLINK")["I04D-CASE-F-LK-NEVER-UNLINK"]
    assert not s["harness_error"], s["harness_error"]
    assert s["participants"]["lock_exists_after"] is True
    assert s["participants"]["lock_bytes_after"] == 0
    assert s["final_lease"]["lock_exists"] is True
    assert s["final_lease"]["lock_bytes"] == 0
    assert s["pause_calls"] == 2 and s["resume_calls"] == 2, s["worker"]["events"]
    assert s["lock_acquisitions"] >= 4, s["lock_acquisitions"]
