"""W14-RF-CLEAN-CHAIN behavior tests (E01–E08) for the rewritten runner.

Every heavy test runs the REAL runner as a subprocess against the REAL
frozen three-repo chain; assertions are pinned to observed production
behavior, never to invented contracts.  These tests do not depend on any
personal production lake: the lake is the synthetic W14 fixture.

If the sibling repositories or the frozen commits are absent, the heavy
tests skip with the exact environment reason (the runner itself never skips
for that — it exits 3 ``environment_unavailable``; see
``test_missing_commit_is_environment_unavailable``).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "e2e" / "run_cross_repo_chain_e2e.py"
FIXTURES = REPO / "tests" / "fixtures" / "w14_chain"

RF_COMMIT = "599d17b89d8baee42ce203747496731ace2d0148"
CWP_COMMIT = "a31300a70215319e6bcf3a03d32b2882bdf1aeaa"
FF_COMMIT = "7f6a9268da90281c28b55d437860bc2d2b60106e"
# A historical RF product that still shapes source records differently; used
# only to prove that REAL product failure drives the whole E2E non-zero.
HISTORICAL_RF_COMMIT = "3b00b9384"

CWP_REPO = REPO.parent / "company-wiki"
FF_REPO = REPO.parent / "filing-fetch"

OFFLINE = "S2,S3,S5,S6,S4"
FULL_CHAIN_TIMEOUT = 600


def _commit_present(repo: Path, commit: str) -> bool:
    if not repo.is_dir():
        return False
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True, check=False)
    return proc.returncode == 0


def _chain_env_available() -> tuple[bool, str]:
    for role, repo, commit in (("rf", REPO, RF_COMMIT),
                               ("cwp", CWP_REPO, CWP_COMMIT),
                               ("ff", FF_REPO, FF_COMMIT)):
        if not repo.is_dir():
            return False, f"{role} repository absent: {repo}"
        if not _commit_present(repo, commit):
            return False, f"{role} commit absent: {commit}"
    return True, ""


_CHAIN_OK, _WHY = _chain_env_available()
requires_chain = pytest.mark.skipif(
    not _CHAIN_OK, reason=f"frozen chain inputs unavailable: {_WHY}")


def _run_runner(args: list[str], tmp: Path, *, cwd: Path | None = None,
                extra_env: dict | None = None, timeout: float = FULL_CHAIN_TIMEOUT):
    work = tmp / "work"
    evidence = tmp / "evidence"
    env = dict(os.environ)
    env.pop("RF_E2E_LIVE_DOWNLOAD", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), *args,
         "--rf-repo", str(REPO), "--rf-commit", RF_COMMIT,
         "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
         "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
         "--work-root", str(work), "--evidence-dir", str(evidence)],
        cwd=str(cwd or tmp), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout, check=False)
    return proc, evidence


def _latest_attempt(evidence: Path) -> Path:
    attempts = sorted(p for p in evidence.iterdir() if p.is_dir())
    assert attempts, f"no evidence attempt under {evidence}"
    return attempts[-1]


def _summary(attempt: Path) -> dict:
    return json.loads((attempt / "summary.json").read_text(encoding="utf-8"))


def _by_id(summary: dict) -> dict:
    return {s["id"]: s for s in summary["scenarios"]}


def _fake_api_keys() -> dict:
    return {"W14_TEST_API_KEY": "w14-secret-value-never-in-evidence",
            "W14_TEST_SECRET": "another-secret"}


# --------------------------------------------------------------------------
# E01 — offline by default; offline scenarios actually execute
# --------------------------------------------------------------------------

@requires_chain
def test_e01_default_offline_full_suite_executes(tmp_path):
    """Default invocation (no --live): offline, S2/S3/S5/S6/S4 all run and
    pass; no offline scenario is skipped or not_executed."""
    decoy = tmp_path / "decoy-pythonpath"
    (decoy / "company_wiki").mkdir(parents=True)
    (decoy / "company_wiki" / "__init__.py").write_text(
        "raise RuntimeError('decoy company_wiki must never be imported')",
        encoding="utf-8")
    proc, evidence = _run_runner(
        ["--scenarios", OFFLINE], tmp_path,
        extra_env={**_fake_api_keys(), "PYTHONPATH": str(decoy)})
    assert proc.returncode == 0, (
        f"runner exit {proc.returncode}\n{proc.stdout[-3000:]}"
        f"\n{proc.stderr[-2000:]}")
    attempt = _latest_attempt(evidence)
    summary = _summary(attempt)
    assert summary["live_gate"] == "never"
    assert summary["network_scope"].startswith("none")
    by = _by_id(summary)
    for sid in ("S2", "S3", "S5", "S6", "S4"):
        assert sid in by, f"{sid} not executed; ran {sorted(by)}"
        assert by[sid]["status"] == "pass", json.dumps(by[sid], ensure_ascii=False)
    # zero outbound network attempts recorded by the guard
    assert not (attempt / "net_attempts.json").exists()

    # ---- E02: provenance binds frozen commits and beats the decoy ---------
    provenance = json.loads(
        (attempt / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["import_probe"]["under_frozen_deployment"] is True
    deployed = provenance["deployment"]
    assert deployed["rf"]["requested_commit"] == RF_COMMIT
    assert deployed["cwp"]["requested_commit"] == CWP_COMMIT
    assert deployed["ff"]["requested_commit"] == FF_COMMIT
    for role in ("rf", "cwp", "ff"):
        assert deployed[role]["deployed_files"] > 0, role
    # final child provenance is written after all scenarios ran
    children = summary["child_processes"]
    assert len(children) >= 3
    cwp_root = deployed["cwp"]["deployed_root"]
    assert all(c.get("company_wiki_file", "").startswith(cwp_root)
               for c in children), [
        c.get("company_wiki_file") for c in children[:5]]

    # the guard actually EXECUTED in every child with usable wiring — a
    # silent load failure cannot masquerade as "zero events" (A-finding 1)
    installs = summary["guard_install_records"]
    assert installs and len(installs) >= len(children), len(installs)
    assert all(rec.get("wired", {}).get("urlopen") is True
               for rec in installs), installs[:3]
    assert all(rec.get("wired", {}).get("net_block") is True
               for rec in installs), installs[:3]

    # grandchildren of the real chain really ran, all from the frozen
    # deployment (E02/E03; static F7 + adversarial F3)
    joined = [" ".join(c.get("argv", [])) for c in children]
    for needle in ("source_preparation.py", "fetch_filing.py",
                   "source_reader_cli", "source_catalog"):
        assert any(needle in j for j in joined), needle
    rf_root = deployed["rf"]["deployed_root"]
    ff_root = deployed["ff"]["deployed_root"]
    script_argv0 = [str(c["argv"][0]) for c in children
                    if c.get("argv") and str(c["argv"][0]).endswith(".py")]
    assert script_argv0, "no python-script child recorded"
    off_deploy = [a for a in script_argv0
                  if not a.startswith((rf_root, ff_root, cwp_root))]
    assert not off_deploy, off_deploy

    # receipts self-bind to this exact runner/support code (F17) and the
    # production-write figure is MEASURED from this process's git verb log —
    # every verb must be read-only; a write verb would fail here (F2/F8)
    assert summary["runner_code_sha256"][
        "e2e/run_cross_repo_chain_e2e.py"]
    assert len(summary["runner_code_sha256"]) >= 6
    pw = summary["production_writes"]
    assert pw["measured"] is True and pw["count"] == 0, pw
    assert set(pw["git_verbs_used"]) <= {"rev-parse", "status", "archive"}, pw
    assert "archive" in pw["git_verbs_used"], pw
    # worktree snapshots of the shared live source repos are recorded as
    # observation receipts (external concurrent edits disclosed, not
    # attributed to this run)
    observed = summary["source_repos_observed"]
    assert set(observed) == {"rf", "cwp", "ff"}
    for role, rec in observed.items():
        assert rec["head_before"] and rec["head_after"], role

    # ---- E03: real processes with PIDs and pathless SourceRefs -----------
    pids = [p["pid"] for s in summary["scenarios"]
            for p in s.get("processes", []) if p.get("pid")]
    assert len(set(pids)) >= 3, pids
    pdf_record = json.loads(
        (attempt / "s2" / "pdf_record.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (FIXTURES / "w14_fixture_manifest.json").read_text(encoding="utf-8"))
    ref = (pdf_record.get("company_wiki_trace") or {}).get("source_ref") or {}
    assert ref.get("content_sha256") == \
        manifest["documents"]["annual_pdf"]["sha256"]
    assert (pdf_record.get("capture") or {}).get("snapshot_sha256") == \
        manifest["documents"]["annual_pdf"]["sha256"]
    receipt = (pdf_record.get("company_wiki_trace") or {}).get(
        "read_receipt") or {}
    assert str(receipt.get("document_id") or "").startswith(
        "urn:company-wiki:document:sha256:")
    assert pdf_record.get("page_or_section") == "1"
    reuse = pdf_record.get("reuse_receipt") or {}
    assert reuse.get("download_calls") == 0
    assert reuse.get("outcome") == "reused_existing"

    # ---- E04: the TXT companion is actually read, not just registered ----
    txt_record = json.loads(
        (attempt / "s2" / "txt_record.json").read_text(encoding="utf-8"))
    txt_trace = txt_record.get("company_wiki_trace") or {}
    assert (txt_trace.get("source_ref") or {}).get("content_sha256") == \
        manifest["documents"]["quarterly_txt"]["sha256"]
    txt_manifest = txt_trace.get("source_manifest") or {}
    assert txt_manifest.get("fiscal_period") == "Q3"
    assert txt_manifest.get("fiscal_year") == 2024

    # ---- E04: layered error reasons are preserved verbatim ---------------
    wrong = json.loads((attempt / "s2" / "wrong_period_refusal.json")
                       .read_text(encoding="utf-8"))
    assert wrong["rc"] == 3
    assert "no_local_match" in str(wrong["parsed"])
    assert "prompt injection" not in str(wrong["parsed"]).lower()
    empty = json.loads((attempt / "s2" / "empty_identity_refusal.json")
                       .read_text(encoding="utf-8"))
    assert empty["rc"] == 2
    assert empty["parsed"]["status"] == "request_error"
    assert "company_query" in empty["parsed"]["error"]

    # ---- E05: credentials scrubbed by NAME only; no values anywhere ------
    child_env = json.loads(
        (attempt / "child_env.json").read_text(encoding="utf-8"))
    assert "W14_TEST_API_KEY" in child_env["scrubbed_credential_names"]
    assert "W14_TEST_SECRET" in child_env["scrubbed_credential_names"]
    for evidence_file in attempt.rglob("*"):
        if not evidence_file.is_file() or \
                evidence_file.suffix not in (".json", ".txt"):
            continue
        text = evidence_file.read_text(encoding="utf-8", errors="replace")
        assert "w14-secret-value-never-in-evidence" not in text, evidence_file
        assert "another-secret" not in text, evidence_file

    # ---- S5/S6 honest refusals -------------------------------------------
    s5 = json.loads((attempt / "s5" / "refusal.json")
                    .read_text(encoding="utf-8"))
    assert s5["status"] == "not_found"
    assert s5["downloads"] == 0
    s6_unknown = json.loads((attempt / "s6" / "unknown_refusal.json")
                            .read_text(encoding="utf-8"))
    assert s6_unknown["status"] == "identity_error"
    assert s6_unknown["downloads"] == 0
    s6_amb = json.loads((attempt / "s6" / "ambiguous_refusal.json")
                        .read_text(encoding="utf-8"))
    assert s6_amb["status"] == "identity_error"
    assert "ambiguous" in s6_amb["error"]

    # ---- S3 reuse ---------------------------------------------------------
    counters = json.loads((attempt / "s3" / "counters.json")
                          .read_text(encoding="utf-8"))
    assert counters["deltas"].get("provider", 0) == 0

    # ---- S4 cleanup -------------------------------------------------------
    s4_report = json.loads((attempt / "s4" / "cleanup.json")
                           .read_text(encoding="utf-8"))
    assert s4_report["attempt_removed"] is True
    assert s4_report["work_root_restored"] is True


@requires_chain
def test_e01_s1_intentional_skip_and_retired_auto(tmp_path):
    """S1 without --live force is an intentional skip; --live auto and the
    retired env var never enable network (exit stays 0 for S1 skip)."""
    env = {**_fake_api_keys(), "RF_E2E_LIVE_DOWNLOAD": "1"}
    proc, evidence = _run_runner(
        ["--scenarios", "S1,S4", "--live", "auto"], tmp_path,
        extra_env=env, timeout=300)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    attempt = _latest_attempt(evidence)
    summary = _summary(attempt)
    assert summary["live_gate"] == "never"
    notices = " ".join(summary["live_notices"])
    assert "--live auto is retired" in notices
    assert "RF_E2E_LIVE_DOWNLOAD is retired" in notices
    by = _by_id(summary)
    assert by["S1"]["status"] == "skip"
    assert by["S1"]["reason"]["code"] == "live_gate_never"
    assert by["S4"]["status"] == "pass"
    assert not (attempt / "net_attempts.json").exists()


# --------------------------------------------------------------------------
# E02 — missing objects are named environment_unavailable, never PASS/skip
# --------------------------------------------------------------------------

def test_missing_commit_is_environment_unavailable(tmp_path):
    """A missing commit object is a named environment gap: exit 3, an
    environment_unavailable message naming the object, and no scenario
    pretending to pass or skip."""
    evidence = tmp_path / "evidence"
    env = dict(os.environ)
    env.pop("RF_E2E_LIVE_DOWNLOAD", None)
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER),
         "--scenarios", "S2,S3,S5,S6",
         "--rf-repo", str(REPO), "--rf-commit", "0" * 40,
         "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
         "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
         "--work-root", str(tmp_path / "work"),
         "--evidence-dir", str(evidence)],
        cwd=str(tmp_path), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120, check=False)
    assert proc.returncode == 3, (
        f"expected exit 3 for missing commit, got {proc.returncode}\n"
        f"{proc.stdout[-1500:]}")
    attempt = _latest_attempt(evidence)
    summary = _summary(attempt)
    assert summary["environment_unavailable"].startswith(
        "environment_unavailable")
    assert "0" * 40 in summary["environment_unavailable"]
    # no scenario pretended to pass or skip
    assert summary["statuses"] == {}


def test_healthy_probe_binds_import_to_frozen_deployment(tmp_path):
    """The probe FAILURE branch (named environment_unavailable, exit 3) is
    covered by test_missing_commit_is_environment_unavailable; this test
    pins the healthy path it claims: probe rc==0 with company_wiki bound to
    the frozen deployment (W14 F13 — no rc-in-(0,3) vacuous acceptance)."""
    proc, evidence = _run_runner(["--scenarios", "S4"], tmp_path, timeout=300)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-1000:]
    attempt = _latest_attempt(evidence)
    provenance = json.loads(
        (attempt / "provenance.json").read_text(encoding="utf-8"))
    assert provenance["import_probe"]["rc"] == 0
    assert provenance["import_probe"]["under_frozen_deployment"] is True
    summary = _summary(attempt)
    assert summary["statuses"] == {"S4": "pass"}, summary["statuses"]


# --------------------------------------------------------------------------
# E05 — the offline guard demonstrably blocks and records
# --------------------------------------------------------------------------

def test_netguard_blocks_and_records_a_real_attempt(tmp_path):
    """Detector non-vacuity: with the guard installed, a child attempting a
    non-loopback connect is refused and the attempt is recorded (no packet
    leaves the machine — the block fires before connect)."""
    sys.path.insert(0, str(REPO / "e2e"))
    from replay_support import netguard
    guard = tmp_path / "guard"
    netguard.materialize_guard(guard)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(guard)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["RF_E2E_SPY_DIR"] = str(guard)
    env["RF_E2E_NET_BLOCK"] = "1"
    env["RF_E2E_NETLOG"] = str(guard / "net_attempts.jsonl")
    child = (
        "import socket\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "try:\n"
        "    s.connect(('203.0.113.1', 443))\n"
        "    print('CONNECTED')\n"
        "except OSError as exc:\n"
        "    print('BLOCKED', type(exc).__name__)\n"
    )
    proc = subprocess.run([sys.executable, "-c", child], env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=60, check=False)
    assert "BLOCKED" in proc.stdout, proc.stdout + proc.stderr
    assert "CONNECTED" not in proc.stdout
    attempts = netguard.net_attempts(guard)
    assert len(attempts) == 1
    assert attempts[0]["host"] == "203.0.113.1"
    # loopback stays allowed for the harness itself
    loop = subprocess.run(
        [sys.executable, "-c",
         "import socket;s=socket.socket();s.bind(('127.0.0.1',0));"
         "print('LOOP_OK', s.getsockname()[1])"],
        env=env, capture_output=True, text=True, encoding="utf-8",
        timeout=60, check=False)
    assert loop.stdout.startswith("LOOP_OK"), loop.stdout + loop.stderr


# --------------------------------------------------------------------------
# E06 — caller directories survive success; evidence history is kept
# --------------------------------------------------------------------------

@requires_chain
def test_e06_work_root_and_evidence_history_preserved(tmp_path):
    work = tmp_path / "work"
    evidence = tmp_path / "evidence"
    work.mkdir()
    sentinel = work / "user-sentinel.txt"
    sentinel.write_text("owner data", encoding="utf-8")
    prior = evidence / "attempt-20260101-000000Z-000001"
    prior.mkdir(parents=True)
    (prior / "summary.json").write_text('{"history": 1}', encoding="utf-8")

    env = dict(os.environ)
    env.pop("RF_E2E_LIVE_DOWNLOAD", None)
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--scenarios", "S4",
         "--rf-repo", str(REPO), "--rf-commit", RF_COMMIT,
         "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
         "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
         "--work-root", str(work), "--evidence-dir", str(evidence)],
        cwd=str(tmp_path), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=300, check=False)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    assert sentinel.read_text(encoding="utf-8") == "owner data"
    assert json.loads((prior / "summary.json").read_text(
        encoding="utf-8")) == {"history": 1}
    assert [p.name for p in work.iterdir()] == ["user-sentinel.txt"]
    new_attempts = [p for p in evidence.iterdir() if p != prior]
    assert len(new_attempts) == 1, "evidence must gain exactly one attempt"
    assert (new_attempts[0] / "summary.json").is_file()


# --------------------------------------------------------------------------
# E07 — same semantics from two different absolute roots
# --------------------------------------------------------------------------

@requires_chain
def test_e07_two_roots_same_semantics_one_with_unicode_and_spaces(tmp_path):
    first = tmp_path / "plain-root"
    second = tmp_path / "中文 根目录 with spaces"
    decoy = tmp_path / "polluted"
    (decoy / "company_wiki").mkdir(parents=True)
    (decoy / "company_wiki" / "__init__.py").write_text(
        "raise RuntimeError('decoy company_wiki must never be imported')",
        encoding="utf-8")
    external_cwd = tmp_path / "external cwd"
    external_cwd.mkdir()
    semantics = []
    for root in (first, second):
        env = dict(os.environ)
        env.pop("RF_E2E_LIVE_DOWNLOAD", None)
        env["PYTHONPATH"] = str(decoy)  # developer pollution to defeat
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--live", "never",
             "--scenarios", OFFLINE,
             "--rf-repo", str(REPO), "--rf-commit", RF_COMMIT,
             "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
             "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
             "--work-root", str(root / "work"),
             "--evidence-dir", str(root / "evidence")],
            cwd=str(external_cwd), env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=FULL_CHAIN_TIMEOUT, check=False)
        assert proc.returncode == 0, (
            f"run under {root} failed: {proc.returncode}\n"
            f"{proc.stdout[-3000:]}\n{proc.stderr[-2000:]}")
        attempt = _latest_attempt(root / "evidence")
        summary = _summary(attempt)
        assert summary["statuses"] == {
            "S2": "pass", "S3": "pass", "S5": "pass", "S6": "pass",
            "S4": "pass"}, summary["statuses"]
        semantics.append(json.loads(
            (attempt / "summary_semantic.json").read_text(encoding="utf-8")))
    assert semantics[0] == semantics[1]


# --------------------------------------------------------------------------
# product failure drives the whole E2E non-zero (no narrowed assertions)
# --------------------------------------------------------------------------

@requires_chain
def test_real_product_failure_makes_suite_nonzero(tmp_path):
    """Frozen-commit provenance, not fixed-hash permission: running the SAME
    scenario set against a historical RF product whose record contract
    differs makes S2 genuinely fail and the whole run exit 1."""
    if not _commit_present(REPO, HISTORICAL_RF_COMMIT):
        pytest.skip(
            f"historical product commit absent (shallow clone?): "
            f"{HISTORICAL_RF_COMMIT}")
    work = tmp_path / "work"
    evidence = tmp_path / "evidence"
    env = dict(os.environ)
    env.pop("RF_E2E_LIVE_DOWNLOAD", None)
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--live", "never",
         "--scenarios", "S2,S4",
         "--rf-repo", str(REPO), "--rf-commit", HISTORICAL_RF_COMMIT,
         "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
         "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
         "--work-root", str(work), "--evidence-dir", str(evidence)],
        cwd=str(tmp_path), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=FULL_CHAIN_TIMEOUT,
        check=False)
    assert proc.returncode == 1, (
        f"expected exit 1 for a real product failure, got {proc.returncode}\n"
        f"{proc.stdout[-3000:]}")
    attempt = _latest_attempt(evidence)
    summary = _summary(attempt)
    by = _by_id(summary)
    assert by["S2"]["status"] == "fail"
    # the failure must be the record-contract checks this test exists for —
    # not an unrelated earlier breakage drifting under the same banner
    expected = ("s2.pdf_record_sha", "s2.pdf_capture_sha",
                "s2.pdf_read_receipt_document", "s2.txt_consumed_sha",
                "s2.txt_consumed_period", "s2.txt_consumed_year")
    failed_names = [f.split(":", 1)[0] for f in by["S2"]["failures"]]
    assert any(name in expected for name in failed_names),         by["S2"]["failures"]
    assert by["S4"]["status"] == "pass"  # cleanup still honored on failure


# --------------------------------------------------------------------------
# positive controls: the offline spy and the exit contract are not vacuous
# --------------------------------------------------------------------------

def test_provider_counter_spy_fires_on_real_loopback_request(tmp_path):
    """W14 A-finding 1: prove the provider counter spy is alive.  A child
    under the guard makes ONE real loopback HTTP request (explicitly allowed
    local use) and the event must be recorded before delegation; non-loopback
    stays blocked (covered by test_netguard_blocks_and_records...)."""
    import http.server
    import threading

    sys.path.insert(0, str(REPO / "e2e"))
    from replay_support import netguard
    guard = tmp_path / "guard"
    netguard.materialize_guard(guard)

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # noqa: ARG002  keep test output quiet
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(guard)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["RF_E2E_SPY_DIR"] = str(guard)
        env["RF_E2E_NET_BLOCK"] = "1"
        env["RF_E2E_NETLOG"] = str(guard / "net_attempts.jsonl")
        child = (
            "import urllib.request\n"
            f"with urllib.request.urlopen('http://127.0.0.1:{port}/', "
            "timeout=10) as r:\n"
            "    r.read(16)\n"
            "print('LOOPBACK_OK')\n"
        )
        proc = subprocess.run([sys.executable, "-c", child], env=env,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=60, check=False)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "LOOPBACK_OK" in proc.stdout
        events = [json.loads(ln) for ln in
                  (guard / "events.jsonl").read_text(encoding="utf-8")
                  .splitlines() if ln.strip()]
        provider = [e for e in events if e.get("counter") == "provider"]
        assert provider, "provider spy did not fire on a real urlopen"
        assert any("urlopen" in str(e.get("qualname")) for e in provider)
        installs = [json.loads(ln) for ln in
                    (guard / "install.jsonl").read_text(encoding="utf-8")
                    .splitlines() if ln.strip()]
        assert installs and installs[-1]["wired"]["urlopen"] is True
        # loopback is explicitly allowed: no net attempt recorded
        assert not (guard / "net_attempts.jsonl").exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_exit_code_mapping_offline_skip_is_incomplete():
    """E01/F16: a skip on ANY offline scenario makes the whole run non-zero;
    only S1 may honestly skip without --live force."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "w14_runner_under_test", RUNNER)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    assert runner.compute_exit_code({"S2": "pass", "S3": "pass",
                                     "S5": "pass", "S6": "pass",
                                     "S4": "pass"}) == 0
    assert runner.compute_exit_code({"S1": "skip", "S4": "pass"}) == 0
    # offline skip = incomplete, never a hidden pass
    assert runner.compute_exit_code({"S2": "skip"}) == 1
    assert runner.compute_exit_code({"S2": "fail", "S4": "pass"}) == 1
    assert runner.compute_exit_code(
        {"S1": "environment_unavailable"}) == 3
    assert runner.compute_exit_code({}) == 0
