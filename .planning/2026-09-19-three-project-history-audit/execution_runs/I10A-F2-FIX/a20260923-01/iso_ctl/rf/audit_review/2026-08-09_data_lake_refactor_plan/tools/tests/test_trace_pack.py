"""WU-104 RED/audit tests: CHR-01..04 for the v1 trace pack."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from trace_pack import (  # noqa: E402
    TraceResult,
    canonical_trace,
    trace_diff,
    check_known_bad_owners,
)


def test_chr01_identical_runs_same_canonical_hash():
    t1 = TraceResult(exit_code=0, stdout_sha256="abc", stderr_sha256="def", duration_ms=12)
    t2 = TraceResult(exit_code=0, stdout_sha256="abc", stderr_sha256="def", duration_ms=15)
    assert canonical_trace(t1) == canonical_trace(t2)  # duration excluded


def test_chr01_different_output_changes_hash():
    t1 = TraceResult(exit_code=0, stdout_sha256="abc", stderr_sha256="def", duration_ms=12)
    t2 = TraceResult(exit_code=0, stdout_sha256="xyz", stderr_sha256="def", duration_ms=12)
    assert canonical_trace(t1) != canonical_trace(t2)


def test_chr02_trace_diff_detects_changes():
    golden = {"cmd-a": {"exit": 0, "stdout": "aaa", "stderr": "sss"}}
    assert trace_diff(golden, {"cmd-a": {"exit": 0, "stdout": "aaa", "stderr": "sss"}}) == []
    diffs = trace_diff(golden, {"cmd-a": {"exit": 1, "stdout": "aaa", "stderr": "sss"}})
    assert any("exit" in d for d in diffs)
    diffs = trace_diff(golden, {"cmd-a": {"exit": 0, "stdout": "bbb", "stderr": "sss"}})
    assert any("stdout" in d for d in diffs)
    # candidate removed entirely
    diffs = trace_diff(golden, {})
    assert any("cmd-a" in d and "missing" in d for d in diffs)
    # unexpected new candidate (CHR-02 addition direction)
    diffs = trace_diff(golden, {"cmd-a": {"exit": 0, "stdout": "aaa", "stderr": "sss"},
                                "cmd-new": {"exit": 0, "stdout": "x", "stderr": "y"}})
    assert any("cmd-new" in d and "unexpected" in d for d in diffs)


def test_chr03_known_bad_requires_owner():
    known_bad = {"kb-1": "scanner 错误 reason code X", "kb-2": "resolver 误报 Y"}
    mapping = {"kb-1": "WU-501"}
    problems = check_known_bad_owners(known_bad, mapping)
    assert any("kb-2" in p for p in problems)
    assert check_known_bad_owners(known_bad, {"kb-1": "WU-501", "kb-2": "WU-602"}) == []


def test_chr04_trace_targets_are_offline():
    """Trace commands must not touch real roots/network/LLM: the declared
    target list is the closed allowlist, and every target must be an offline
    CLI (--help / dry-run / doctor without production catalog)."""
    from trace_pack import TRACE_TARGETS

    assert TRACE_TARGETS, "trace targets must be declared"
    for target in TRACE_TARGETS:
        assert target["offline"], f"{target['name']} must be declared offline"
        args = target["argv"]
        assert (
            "--help" in args
            or any("config_doctor" in arg for arg in args)
            or any("dry" in arg for arg in args)
        ), f"{target['name']} argv must be an offline-only invocation"
