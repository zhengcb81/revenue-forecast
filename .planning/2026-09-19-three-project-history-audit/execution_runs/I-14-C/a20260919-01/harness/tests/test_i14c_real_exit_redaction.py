"""I-14-C: pre-fix/post-fix real-exit contract checks, run by pytest in the iso venv.

These are the isolated counterexample tests for the card.  They are written to be
promotable into CW/tests/contract/ unchanged (the module imports use plain
``company_wiki.source_catalog`` so only PYTHONPATH differs) but they are NOT copied
into the product repo by this attempt.

ASCII only on stdout: the Windows console here is GBK.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent          # <attempt>/harness/tests
HARNESS = HERE.parent                            # <attempt>/harness
DRIVER = HARNESS / "drive_real_exit.py"
MARKER = "SYNTHETIC_AUDIT_TOKEN"
QUOTED_SECRET = "Q" * 300

ISA = Path(__file__).resolve().parents[2] / "iso"    # <attempt>/iso
TREE_FIXED = ISA / "product_fixed" / "src"
TREE_PREFIX = ISA / "product" / "src"
TREE_SWAPPED = ISA / "product_swapped" / "src"
CLI_DRIVER = HARNESS / "run_real_cli_exit.py"

CW = Path(os.environ.get("I14C_CW_ROOT", r"C:\Users\郑曾波\Projects\company-wiki"))
PRODUCT_SRC = Path(os.environ.get("I14C_PRODUCT_SRC", str(TREE_FIXED)))
PRODUCT_TESTS = Path(os.environ.get("I14C_TESTS_DIR", str(CW / "tests" / "contract")))

# pytest's tmp_path is redirected under the attempt dir; declare that scratch root
# so the driver's binding guard can accept it without loosening the global rule.
ATTEMPT_ROOT = HERE.parent.parent
os.environ.setdefault("I14C_RUN_ROOT", str(ATTEMPT_ROOT))


@pytest.fixture(scope="session")
def py_exe() -> str:
    return sys.executable


def run_case(tmp_path: Path, scenario: str, *, cli_exit: bool,
             src: Path | None = None) -> dict:
    run_dir = tmp_path / scenario / ("cli" if cli_exit else "raw")
    run_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # The workspace path contains non-ASCII characters; subprocess argument
    # marshalling on this host is ANSI-codepage based and mangles them, so the
    # child is explicitly put in UTF-8 mode (PYTHONUTF8 also drives its argv
    # decoding), while its own stdout/stderr stay ASCII-only by construction.
    env["PYTHONUTF8"] = "1"
    env["I14C_RUN_ROOT"] = str(ATTEMPT_ROOT)
    argv = [
        sys.executable, "-X", "utf8", "-B", str(DRIVER),
        "--scenario", scenario,
        "--run-dir", str(run_dir),
        "--src", str(src if src is not None else PRODUCT_SRC),
        "--tests-dir", str(PRODUCT_TESTS),
    ]
    if cli_exit:
        argv.append("--cli-exit")
    proc = subprocess.run(argv, cwd=str(run_dir), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    (run_dir / "stdout.txt").write_bytes(proc.stdout)
    (run_dir / "stderr.txt").write_bytes(proc.stderr)
    events_path = run_dir / "worker_process_events.jsonl"
    events = []
    if events_path.is_file():
        events = [json.loads(ln) for ln in
                  events_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.decode("utf-8", "replace"),
        "stderr": proc.stderr.decode("utf-8", "replace"),
        "events": events,
        "events_path": events_path,
        "run_dir": run_dir,
    }


def unhandled(events: list[dict]) -> dict:
    found = [e for e in events if e.get("event") == "unhandled_exception"]
    assert len(found) == 1, f"expected exactly one unhandled_exception event, got {len(found)}"
    return found[0]


# ---------------------------------------------------------------------------
# Acceptance cases: the REAL exit (run_forever + the CLI stderr envelope)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("scenario", ["token-in-message", "unknown-key-with-token",
                                      "nested-cause", "nested-cause-deep"])
def test_real_exit_never_persists_or_prints_the_marker(tmp_path, scenario):
    case = run_case(tmp_path, scenario, cli_exit=True)
    blob = json.dumps(case["events"]) + case["stdout"] + case["stderr"]
    assert MARKER not in blob, f"{scenario}: marker leaked into output or event"
    assert case["returncode"] == 3, "the exception must still be re-raised, not swallowed"


def test_real_exit_redacts_instead_of_dropping_the_field(tmp_path):
    case = run_case(tmp_path, "token-in-message", cli_exit=True)
    event = unhandled(case["events"])
    assert "<redacted>" in event["message_redacted"], (
        "the event must prove redaction ran; dropping the field would also hide the leak"
    )
    assert event["exception_type"] == "RuntimeError"


def test_real_exit_keeps_nonsensitive_diagnostics(tmp_path):
    case = run_case(tmp_path, "nested-cause", cli_exit=True)
    event = unhandled(case["events"])
    for token in ("stage=summarize", "code=llm_global_failure", "request_id=req-SYNTH-0001"):
        assert token in event["message_redacted"], f"lost diagnostic: {token}"
    assert event["cause_types"] == ["ValueError"]


def test_no_secret_exception_is_a_noop_and_not_swallowed(tmp_path):
    case = run_case(tmp_path, "plain", cli_exit=True)
    event = unhandled(case["events"])
    assert event["message_redacted"] == "document not in catalog: doc-1"
    assert event["exception_type"] == "RuntimeError"
    assert case["returncode"] == 3


def test_e4a_quoted_value_truncation_never_leaks_LOAD_BEARING(tmp_path):
    """r2/F-I14C-05: E4 must be load-bearing for R3 (redact before truncate).

    A quoted value that the 200-char cut leaves unterminated no longer matches the
    quoted alternative, and its leading quote excludes it from the bare-value
    alternative.  So a truncate-then-redact implementation leaks here while a
    redact-then-truncate implementation does not.  The r1 unquoted case did not
    distinguish the two orders and is kept separately as E4b.
    """
    case = run_case(tmp_path, "quoted-truncation-boundary", cli_exit=True)
    event = unhandled(case["events"])
    assert len(event["message_redacted"]) <= 200
    assert "Q" * 8 not in event["message_redacted"], "secret prefix survived truncation"
    assert "password" in event["message_redacted"], "the key must stay diagnosable"
    assert "<redacted>" in event["message_redacted"]


def test_e4b_unquoted_truncation_regression_only(tmp_path):
    """r1 E4, kept but explicitly labelled NON-load-bearing: this passes in both orders."""
    case = run_case(tmp_path, "truncation-boundary", cli_exit=True)
    event = unhandled(case["events"])
    assert len(event["message_redacted"]) <= 200
    assert MARKER not in event["message_redacted"]
    assert MARKER[:8] not in event["message_redacted"]


def test_e4a_order_swap_control_leaks(tmp_path):
    """Control: the SAME case against a tree whose only difference is the order.

    iso/product_swapped = iso/product_fixed with redact_and_truncate implemented as
    ``redact_text(text[:limit])``.  If this does not leak, E4a is not load-bearing and
    R3 is unproven - the control failing is as important as the case passing.
    """
    case = run_case(tmp_path, "quoted-truncation-boundary", cli_exit=True,
                    src=TREE_SWAPPED)
    event = unhandled(case["events"])
    leaked = event["message_redacted"].count("Q")
    assert leaked > 0, (
        "order-swap control did not leak, so E4a does not actually prove R3")


def test_event_order_is_preserved_on_the_unhandled_path(tmp_path):
    case = run_case(tmp_path, "token-in-message", cli_exit=True)
    order = [e.get("event") for e in case["events"]]
    assert order == ["process_starting", "session_opened", "unhandled_exception",
                     "process_exiting"]
    assert case["events"][-1]["reason"] == "unhandled_exception"


def test_reraise_path_stderr_is_clean(tmp_path):
    case = run_case(tmp_path, "token-in-message", cli_exit=False)
    assert MARKER not in case["stderr"]
    assert case["returncode"] == 3


# ---------------------------------------------------------------------------
# The isolated-helper case: kept, but explicitly NOT sufficient on its own
# ---------------------------------------------------------------------------


def test_helper_only_case_is_not_the_acceptance_evidence(tmp_path):
    """Directly calling the writer must redact too, but this is marked helper_only:
    the card's exit criterion is about the real exit above, not this call."""
    import sys as _sys

    _sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_and_truncate

    out = redact_and_truncate("Authorization: Bearer " + MARKER)
    assert MARKER not in out
    assert out == "Authorization: <redacted>"


# ---------------------------------------------------------------------------
# Frozen-rule table (positive AND negative): the rule must not be widened silently
# ---------------------------------------------------------------------------


REDACT_CASES = [
    ("Authorization: Bearer " + MARKER, False),
    ("Authorization Bearer " + MARKER, False),
    ("authorization: token " + MARKER, False),
    ("Authorization: " + MARKER, False),
    ('Authorization: "Bearer ' + MARKER + '"', False),
    ("GET /x?token=" + MARKER + "&page=2", False),
    ("token=" + MARKER, False),
    ("api_key=" + MARKER, False),
    ("password: '" + MARKER + "'", False),
    # r2 F-I14C-02: env-var style keys.  These all leaked under the r1 rule because
    # \b cannot match inside `GITHUB_TOKEN` / `my_access_token` (`_` is a word char).
    ("GITHUB_TOKEN=" + MARKER, False),
    ("my_access_token=" + MARKER, False),
    ("SLACK_BOT_TOKEN=" + MARKER, False),
    ("AWS_SECRET_ACCESS_KEY=" + MARKER, False),
    ("export GITHUB_TOKEN=" + MARKER, False),
    ("GH_TOKEN=" + MARKER, False),
    ("AWS_ACCESS_KEY_ID=" + MARKER, False),
    ("client_secret=" + MARKER, False),
    ("MY_APP_PASSWORD=" + MARKER, False),
    ("db.passwd=" + MARKER, False),
    ("AWS_SECRET_ACCESS_KEY_ID=" + MARKER, False),
    # RESIDUAL, deliberately NOT covered: space-separated flag form.  Widening the
    # separator to bare whitespace would redact ordinary diagnostics such as
    # "token expired for doc-1", which R4 forbids.  Frozen as measured, not hidden.
    ("--api-key " + MARKER, True),
    # over-redaction guard: these must NOT start matching in r2
    ("monkey=banana", False),
    ("oauth=abc123", False),
    ("secretary=alice", False),
    ("tokenizer=whitespace", False),
    ("keyboard=us", False),
    # negative: a key outside the frozen rule is NOT claimed to be covered
    ("upload failed for digest=" + MARKER, True),
    ("document not in catalog: doc-1", False),
    ("stage=summarize code=llm_global_failure request_id=req-SYNTH-0001", False),
]


@pytest.mark.parametrize("text,marker_survives", REDACT_CASES)
def test_frozen_rule_table(text, marker_survives):
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_text

    out = redact_text(text)
    assert (MARKER in out) is marker_survives, f"rule drift on: {text!r} -> {out!r}"


# ---------------------------------------------------------------------------
# E5 - the PRODUCT'S OWN CLI entry point (r2/F-I14C-03)
# ---------------------------------------------------------------------------


def run_real_cli(tmp_path: Path, shape: str, src: Path) -> dict:
    run_dir = tmp_path / "realcli" / shape / src.parent.name
    run_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    argv = [
        sys.executable, "-X", "utf8", "-B", str(CLI_DRIVER),
        "--shape", shape, "--run-dir", str(run_dir),
        "--src", str(src), "--python", sys.executable,
    ]
    proc = subprocess.run(argv, cwd=str(run_dir), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    result_path = run_dir / "result.json"
    assert result_path.is_file(), (
        f"real-CLI driver produced no result: {proc.stderr.decode('utf-8', 'replace')[:400]}")
    return json.loads(result_path.read_text(encoding="utf-8"))


def test_e5a_real_cli_credential_shaped_config_is_redacted(tmp_path):
    """cli.py:866 config resolution used to sit OUTSIDE the try/except."""
    before = run_real_cli(tmp_path, "E5a", TREE_PREFIX)
    after = run_real_cli(tmp_path, "E5a", TREE_FIXED)
    # before: bare interpreter traceback, marker on stderr
    assert before["bare_traceback_on_stderr"] is True
    assert before["marker_hits"]["stderr"] >= 1
    # after: redacted envelope, nothing leaked, no catalog created
    assert after["bare_traceback_on_stderr"] is False
    assert after["structured_envelope_on_stderr"] is True
    assert after["marker_hits"]["stderr"] == 0
    assert after["marker_hits"]["stdout"] == 0
    assert after["catalogs_created"] == []
    assert after["returncode"] == 1


def test_e5b_real_cli_bare_marker_path_is_a_NAMED_RESIDUAL(tmp_path):
    """R5 limit, frozen as a residual rather than smoothed over.

    A marker used as a plain path component is not credential-shaped, so the frozen
    rule does not redact it.  What the fix DOES buy is that the exit is now the
    structured envelope instead of a bare traceback.
    """
    before = run_real_cli(tmp_path, "E5b", TREE_PREFIX)
    after = run_real_cli(tmp_path, "E5b", TREE_FIXED)
    assert before["bare_traceback_on_stderr"] is True
    assert after["bare_traceback_on_stderr"] is False
    assert after["structured_envelope_on_stderr"] is True
    assert after["marker_hits"]["stderr"] == 1, (
        "if this became 0 the frozen rule changed; update the oracle deliberately")


def test_e5c_real_cli_argparse_path_is_a_NAMED_CARRY(tmp_path):
    """argparse echoes argv on its own error path; not the except-Exception handler."""
    result = run_real_cli(tmp_path, "E5c", TREE_FIXED)
    assert result["returncode"] == 2
    assert result["catalogs_created"] == []
    # measured, not asserted green: this is a carry, recorded in review.md
    assert result["marker_hits"]["stderr"] >= 1

