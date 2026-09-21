"""I-14-D: the narrowed-semantics oracle as pytest cases.

The narrow_must/keep_must tables are IMPORTED from harness/run_i14d_oracle.py so
the frozen oracle exists in exactly one place.  RED on the base tree (run with
I14C_PRODUCT_SRC=<attempt>/iso/product_base/src), GREEN on the narrow tree.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from run_i14d_oracle import CASES, C13_TAIL, M, RM, R  # the frozen oracle tables

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
ISA = HARNESS.parent / "iso"
DRIVER = HARNESS / "drive_real_exit.py"
ATTEMPT_ROOT = HARNESS.parent

PRODUCT_SRC = Path(os.environ.get(
    "I14C_PRODUCT_SRC", str(ISA / "product_narrow" / "src")))
CW = Path(os.environ.get("I14C_CW_ROOT", r"C:\Users\郑曾波\Projects\company-wiki"))
PRODUCT_TESTS = Path(os.environ.get("I14C_TESTS_DIR", str(CW / "tests" / "contract")))

# r2: the reviewer's synthetic 39-char credential, the same literal the oracle (N5c/N5d),
# the rule table (cred-auth-split-*) and drive_real_exit.py's `bearer-newline` scenario use.
REVIEWER_SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"

NARROW_MUST = [c for c in CASES if c[1] == "narrow_must"]
KEEP_MUST = [c for c in CASES if c[1] == "keep_must"]


def _redact_text():
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_text
    return redact_text


def _redact_and_truncate():
    sys.path.insert(0, str(PRODUCT_SRC))
    from company_wiki.source_catalog.observability import redact_and_truncate
    return redact_and_truncate


@pytest.mark.parametrize("case", NARROW_MUST, ids=[c[0] for c in NARROW_MUST])
def test_i14d_narrow_must(case):
    case_id, _kind, text, expected, contains, expect_len = case
    out = _redact_text()(text)
    assert out == expected, f"{case_id}: {text!r} -> {out!r}, expected {expected!r}"
    assert all(c in out for c in contains)
    if expect_len is not None:
        assert len(out) == expect_len


@pytest.mark.parametrize("case", KEEP_MUST, ids=[c[0] for c in KEEP_MUST])
def test_i14d_keep_must(case):
    case_id, _kind, text, expected, contains, expect_len = case
    out = _redact_text()(text)
    assert out == expected, f"{case_id}: {text!r} -> {out!r}, expected {expected!r}"


# ---------------------------------------------------------------------------
# N4: the NEW E4b baseline (numbers hand-computed in oracle.md section 2)
# ---------------------------------------------------------------------------

E4B_INPUT = "start-" + ("x" * 170) + " token=" + M + " " + ("y" * 120)


def test_i14d_e4b_input_length():
    assert len(E4B_INPUT) == 325


def test_i14d_e4b_pretruncation_length_is_314():
    assert len(_redact_text()(E4B_INPUT)) == 314


def test_i14d_reviewer_c13_pair_112_in_98_out():
    """The I-14-C reviewer's own 24-char marker: 112 in -> 98 out (was 34 out)."""
    text = "upload failed for token=" + RM + C13_TAIL
    assert len(text) == 112
    out = _redact_and_truncate()(text)
    assert out == "upload failed for token=" + R + C13_TAIL
    assert len(out) == 98
    for kept in ("doc=17", "stage=summarize", "code=llm_global_failure",
                 "request_id=req-1"):
        assert kept in out, f"diagnostic lost: {kept}"


def _run_real_exit(tmp_path: Path, scenario: str) -> dict:
    """Drive the REAL worker exit through the unchanged I-14-C driver."""
    run_dir = tmp_path / scenario
    run_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["I14C_RUN_ROOT"] = str(tmp_path.parent)
    argv = [sys.executable, "-X", "utf8", "-B", str(DRIVER),
            "--scenario", scenario, "--run-dir", str(run_dir),
            "--src", str(PRODUCT_SRC),
            "--tests-dir", str(PRODUCT_TESTS)]
    proc = subprocess.run(argv, cwd=str(run_dir), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=180)
    (run_dir / "stdout.txt").write_bytes(proc.stdout)
    (run_dir / "stderr.txt").write_bytes(proc.stderr)
    events_path = run_dir / "worker_process_events.jsonl"
    events = []
    if events_path.is_file():
        events = [json.loads(ln) for ln in
                  events_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return {"returncode": proc.returncode, "stderr": proc.stderr.decode("utf-8", "replace"),
            "events": events}


def test_i14d_e4b_real_exit_new_baseline_200(tmp_path):
    """The persisted E4b message is now cut by the 200 cap (was 193, no cut)."""
    case = _run_real_exit(tmp_path, "truncation-boundary")
    event = next(e for e in case["events"] if e.get("event") == "unhandled_exception")
    msg = event["message_redacted"]
    assert len(msg) == 200
    assert M not in msg and M[:8] not in msg
    assert msg.startswith("start-" + "x" * 170 + " token=" + R + " ")
    # CORRECTION 1 of oracle.md: char 194 is the separating SPACE, so chars
    # 195..200 are the first 6 y's (an earlier draft asserted 7 y's).
    assert msg[193] == " ", "char 194 is the space that followed the value"
    assert msg.endswith(" " + "y" * 6), "chars 195..200 must be the first 6 y's"
    assert case["returncode"] == 3, "the exception must still be re-raised"


# ---------------------------------------------------------------------------
# r2 / review F-REV-D-01: the auth newline-split family at the REAL exit
# ---------------------------------------------------------------------------

def test_i14d_auth_scheme_newline_real_exit_keeps_secret_out_and_diagnostics_in(tmp_path):
    """The r1 tree persisted the wrapped credential; the r1 base tree deleted `doc=17`.

    Both halves of the card's exit clause have to hold on this input at once, and it has
    to hold at the REAL worker exit (`worker.py` -> `redact_and_truncate`), not only in
    the helper.  The credential is the reviewer's synthetic 39-char one, which shares no
    substring with this attempt's marker, so a marker-only grep cannot pass this test.
    """
    case = _run_real_exit(tmp_path, "bearer-newline")
    event = next(e for e in case["events"] if e.get("event") == "unhandled_exception")
    msg = event["message_redacted"]
    assert REVIEWER_SECRET not in msg, "the wrapped credential was persisted in plaintext"
    assert REVIEWER_SECRET[:12] not in msg, "credential prefix survived"
    assert msg == "Authorization: " + R + "\ndoc=17"
    assert "doc=17" in msg, "C13 half: the diagnostic key must survive the credential"
    assert case["returncode"] == 3, "the exception must still be re-raised"
