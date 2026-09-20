"""Rework r2h — replace both failing test functions wholesale."""

from __future__ import annotations

import pathlib
import re
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)

NEW_W1 = '''def test_l8a_w1_no_owner_marker_is_not_a_user_pause(tmp_path, has_scheduler):
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
'''

text = TEST.read_text(encoding="utf-8")
pattern = re.compile(
    r"^def test_l8a_w1_no_owner_marker_is_not_a_user_pause\(tmp_path, has_scheduler\):\n"
    r"(?:.*?\n)*?\n\n",
    re.MULTILINE,
)
match = pattern.search(text)
if not match:
    print("W1 TEST NOT FOUND")
    sys.exit(1)
text = text[: match.start()] + NEW_W1 + "\n" + text[match.end() :]
TEST.write_text(text, encoding="utf-8")
print("test_l8a_w1... replaced wholesale")
