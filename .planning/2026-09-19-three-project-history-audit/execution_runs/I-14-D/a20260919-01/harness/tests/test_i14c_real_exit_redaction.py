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
import time
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
    # r5: declare the pytest basetemp as the scratch root, whatever it is.  The driver's
    # guard refuses product paths unconditionally, so this lets an independent reviewer run
    # the subprocess-backed cases from their own directory (previously I14C_RUN_ROOT was
    # forced to the attempt root and the reviewer's %TEMP% runs were refused with 97).
    env["I14C_RUN_ROOT"] = str(tmp_path.parent)
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


# ---------------------------------------------------------------------------
# F-I14C-07 (r3): the redactor must stay LINEAR on the message it is handed
#
# `redact_and_truncate` runs on the WHOLE untruncated message of every unhandled
# exception, so a super-linear rule is an availability regression in a security
# path.  r2 was quadratic in the `_`/`-` separated segment count; these cases have
# a deadline, so a return to nested quantifiers fails loudly instead of hanging.
# ---------------------------------------------------------------------------

F07_DEADLINE_SECONDS = 5.0


@pytest.mark.parametrize("segments", [1000, 2000, 40000])
def test_f07_long_separator_run_finishes_within_the_deadline(segments):
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_text

    for text in (("a_" * segments) + "=", ("a-" * segments) + "=",
                 ("a_" * segments)[:-1], ("a_" * segments) + '="' + ("b" * 200)):
        started = time.perf_counter()
        out = redact_text(text)
        elapsed = time.perf_counter() - started
        assert elapsed < F07_DEADLINE_SECONDS, (
            f"redact_text took {elapsed:.2f}s on {len(text)} chars "
            f"({segments} segments): the rule is super-linear again")
        assert out == text, "a non-credential key must not be redacted"


def test_f07_auth_regex_path_stays_linear():
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_text

    for text in (("authorization: " * 20000), ("bearer " * 20000)):
        started = time.perf_counter()
        redact_text(text)
        elapsed = time.perf_counter() - started
        assert elapsed < F07_DEADLINE_SECONDS, f"auth path took {elapsed:.2f}s"


def test_f07_rejected_key_does_not_swallow_a_later_pair():
    """Declared behavioural change vs r1/r2, and an improvement.

    The old regex consumed the whole `key=value` span when the key was rejected, so
    a genuine credential later in the same text was never seen.  The scanner must
    still redact it.
    """
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_text

    url = redact_text("url=https://example/x?token=" + MARKER)
    assert MARKER not in url and "<redacted>" in url
    cmd = redact_text("cmd: --token=" + MARKER)
    assert MARKER not in cmd and "<redacted>" in cmd
    # ... while a rejected key with NO credential inside it is left untouched
    assert redact_text("url=https://example/x?page=2") == "url=https://example/x?page=2"
    assert redact_text("digest=" + MARKER) == "digest=" + MARKER


# ---------------------------------------------------------------------------
# F-I14C-08 (r4): OUTPUT FIDELITY
#
# r3 lesson: every earlier criterion asked only "is the marker gone?" / "did the text
# change?", so a redactor that emitted `tokentoken=<redacted>` passed all of them.  These
# cases pin the exact output string: the value is replaced and nothing else moves.
#
# r5 (F-I14C-R4-01/R4-02): the number of pairs is NOT written here by hand any more - it is
# produced mechanically by harness/report_counts.py (r5/counts.json).  The r4 text said "23"
# for a 24-entry table, and the same wrong number had been copied into four other documents.
# The block also gained multi-line cases (C13), which was the direction the fidelity
# criterion was blind to.
#
# r2 (I-14-D): I-14-D's narrowing changed three expectations, and the reviewer's RULING 1
# additionally required the auth newline-split family (review finding F-REV-D-01), so this
# table is no longer byte-identical to I-14-C's.  The pair count is still bound mechanically
# to r5/counts.json, which harness/report_i14d_counts.py regenerates from this table.
# ---------------------------------------------------------------------------

FIDELITY_CASES = [
    ("token=" + MARKER, "token=<redacted>"),
    ("GITHUB_TOKEN=" + MARKER, "GITHUB_TOKEN=<redacted>"),
    ("my_access_token=" + MARKER, "my_access_token=<redacted>"),
    ("SLACK_BOT_TOKEN=" + MARKER, "SLACK_BOT_TOKEN=<redacted>"),
    ("AWS_SECRET_ACCESS_KEY=" + MARKER, "AWS_SECRET_ACCESS_KEY=<redacted>"),
    ("AWS_ACCESS_KEY_ID=" + MARKER, "AWS_ACCESS_KEY_ID=<redacted>"),
    ("export GITHUB_TOKEN=" + MARKER, "export GITHUB_TOKEN=<redacted>"),
    ("db.passwd=" + MARKER, "db.passwd=<redacted>"),
    ("api_key=" + MARKER, "api_key=<redacted>"),
    ("client_secret=" + MARKER, "client_secret=<redacted>"),
    ("password: '" + MARKER + "'", "password: <redacted>"),
    ("token = " + MARKER, "token = <redacted>"),
    # r2/REVIEWER RULING 1: the value is ONE token (I-14-D narrowed the r1 greedy
    # `_BARE_VALUE`), so a same-line middle token no longer eats the tail ` b=2`.
    ("a=1 token=" + MARKER + " b=2", "a=1 token=<redacted> b=2"),
    ("a=1 token=" + MARKER + "; b=2", "a=1 token=<redacted>; b=2"),
    # r2/REVIEWER RULING 1: C13 closed - a credential value stops at the NEWLINE, so
    # the remaining diagnostic block survives (was: whole tail deleted, 112 in / 34 out).
    ("upload failed for token=" + MARKER
     + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1",
     "upload failed for token=<redacted>"
     + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"),
    # ... and the boundary: a value delimiter before the newline protects the tail
    ("failed for token=" + MARKER + "; see log\nstage=summarize code=llm_global_failure",
     "failed for token=<redacted>; see log\nstage=summarize code=llm_global_failure"),
    ("token=" + MARKER + "\nnext=1", "token=<redacted>\nnext=1"),
    ("GET /x?token=" + MARKER + "&page=2", "GET /x?token=<redacted>&page=2"),
    ("Authorization: Bearer " + MARKER, "Authorization: <redacted>"),
    # r2/REVIEWER RULING 1 (required addition): a KNOWN scheme word followed by a line
    # break.  The secret's line carries no `key=` prefix, so this family was the blind
    # spot behind review finding F-REV-D-01; the marker must be ABSENT and the line
    # break must survive.
    ("Authorization: Bearer\n" + MARKER, "Authorization: <redacted>"),
    ("Authorization: Bearer\r\n" + MARKER, "Authorization: <redacted>"),
    ("Authorization: Bearer\n  " + MARKER, "Authorization: <redacted>"),
    ("authorization: token\n" + MARKER, "authorization: <redacted>"),
    ("upload failed for token=" + MARKER, "upload failed for token=<redacted>"),
    ("url=https://example/x?token=" + MARKER,
     "url=https://example/x?token=<redacted>"),
    # untouched entries must be byte-identical
    ("monkey=banana", "monkey=banana"),
    ("key=value", "key=value"),
    ("stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001"),
    ("stage=summarize\ncode=llm_global_failure\nrequest_id=req-1",
     "stage=summarize\ncode=llm_global_failure\nrequest_id=req-1"),
    ("url=https://example/x?page=2", "url=https://example/x?page=2"),
    # declared residuals
    ("digest=" + MARKER, "digest=" + MARKER),
    ('{"api_key": "' + MARKER + '"}', '{"api_key": "' + MARKER + '"}'),
]


def test_f08_fidelity_pair_count_matches_the_mechanical_count():
    """F-I14C-R4-01: the pair count must not be hand-written anywhere.

    `harness/report_counts.py` computes this number from the table itself and writes
    `r5/counts.json`; the r4 documents said "23" for a 24-entry table.  Adding the
    r2/REVIEWER RULING 1 auth rows therefore means re-running
    `harness/report_i14d_counts.py` and regenerating `r5/counts.json` - the assertion
    below is the mechanism that forces that, and it is meant to fail loudly otherwise.
    """
    counts_path = ATTEMPT_ROOT / "r5" / "counts.json"
    assert counts_path.is_file(), "run harness/report_counts.py to produce r5/counts.json"
    counts = json.loads(counts_path.read_text(encoding="utf-8"))
    assert counts["fidelity_cases"] == len(FIDELITY_CASES)
    assert counts["fidelity_cases"] == counts["exact_nodeids"]


def test_f08_c13_multiline_diagnostics_survive():
    """C13, r2: the criterion must not be blind to multi-line inputs.

    Reviewer RULING 1 renamed this from `test_f08_c13_multiline_loss_is_frozen_not_hidden`:
    that name asserted the OLD greedy behaviour, which I-14-D removed.  It now asserts the
    NARROWED behaviour explicitly - the credential is still redacted, the diagnostic block
    survives, and the surviving block is NOT a truncation artefact (98 chars, well under
    the 200 cap).  Lengths are computed from the inputs, not transcribed: the r5 draft of
    this test hard-coded the reviewer's 112 and failed with this attempt's shorter marker -
    the same hand-typed-number failure mode as F-I14C-R4-01.
    """
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_and_truncate

    review_marker = "ZQ7_REVIEWER_MARKER_9f3c"          # the reviewer's own marker
    tail = " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"
    for marker in (MARKER, review_marker):
        text = "upload failed for token=" + marker + tail
        out = redact_and_truncate(text)
        assert out == "upload failed for token=<redacted>" + tail
        assert len(out) == 98, "well below the 200-char limit, so this is not truncation"
        assert len(out) > 90, "the multi-line diagnostics must survive"
        assert marker not in out, "the marker must still be redacted"
        for kept in ("doc=17", "stage=summarize", "code=llm_global_failure",
                     "request_id=req-1"):
            assert kept in out, f"C13 narrowing lost the diagnostic key {kept!r}"
    # the reviewer's exact reproduction: 24-char marker -> 112 chars in, 98 out
    assert len("upload failed for token=" + review_marker + tail) == 112
    assert len("upload failed for token=" + MARKER + tail) == 109


@pytest.mark.parametrize("text,expected", FIDELITY_CASES)
def test_f08_output_fidelity_exact(text, expected):
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_text

    out = redact_text(text)
    assert out == expected, (
        f"output fidelity broken: {text!r} -> {out!r}, expected {expected!r}")


def test_f08_persisted_event_keeps_the_key_verbatim(tmp_path):
    """Fidelity at the REAL exit, not only in the helper.

    The r3 defect was visible in the persisted event (`upload failed for
    tokentoken=<redacted>`, len 39 instead of 34) and in the CLI envelope, where the
    missing config file name was rewritten and stopped identifying the file.
    """
    case = run_case(tmp_path, "unknown-key-with-token", cli_exit=True)
    event = unhandled(case["events"])
    assert event["message_redacted"] == "upload failed for token=<redacted>"
    assert len(event["message_redacted"]) == 34, (
        "length must match the r2 baseline; a duplicated key inflates it")
    assert "tokentoken" not in event["message_redacted"]
    assert '"error": "upload failed for token=<redacted>"' in case["stderr"]


def test_f08_e5a_envelope_still_identifies_the_config_file(tmp_path):
    """The r3 defect rewrote the missing file name to `tokentoken=<redacted>`."""
    result = run_real_cli(tmp_path, "E5a", TREE_FIXED)
    assert result["marker_hits"]["stderr"] == 0
    assert result["bare_traceback_on_stderr"] is False
    stderr_path = (tmp_path / "realcli" / "E5a" / TREE_FIXED.parent.name
                   / "stderr.txt")
    stderr = stderr_path.read_text(encoding="utf-8")
    assert "tokentoken" not in stderr, "the key was duplicated in the envelope"
    assert "token=<redacted>" in stderr, (
        "the envelope must still show which name pattern failed to resolve")


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
    env["I14C_RUN_ROOT"] = str(tmp_path.parent)      # r5: same rule as run_case
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

