"""W14-RF-CLEAN-CHAIN: portable offline cross-repo chain E2E runner.

Drives the REAL production chain of three frozen repos against a synthetic
two-document lake, with no personal production lake, no credentials, and no
outbound network:

    RF scripts/source_preparation.py  (frozen RF commit)
      -> FF scripts/fetch_filing.py   (frozen FF commit)
        -> CWP company_wiki.source_catalog.* public CLIs (frozen CWP commit)

Scenario IDs are unchanged from the historical suite:

  S1  live provider download — ONLY with an explicit ``--live force``
      (this batch never runs it; without force it is an honest skip)
  S2  fixture lake built through the PUBLIC CWP scan -> FF offline resolve
      (annual PDF) -> RF source_preparation SUCCESS -> the TXT companion
      document consumed through the same real chain -> error paths
      (wrong period, empty identity) keep their original layered reasons
  S3  second run over the same originals: zero downloads, zero provider
      calls, zero catalog mutations, byte-identical lake tree
  S5  unknown provider document id -> structured refusal, exit 2
  S6  unknown company / ambiguous alias -> honest structured refusal
  S4  restore invariants: only the owned attempt directory is cleaned;
      caller directories, fixtures, and evidence receipts are preserved

Exit codes: 0 all selected scenarios pass (S1 intentional skip allowed);
            1 any scenario fail;
            2 usage error;
            3 environment_unavailable (named, with the concrete gap —
              never a PASS and never a skip).

Usage:
    python e2e/run_cross_repo_chain_e2e.py
        --rf-repo PATH --rf-commit SHA
        --cwp-repo PATH --cwp-commit SHA
        --ff-repo PATH --ff-commit SHA
        [--scenarios S2,S3,S5,S6,S4] [--live never|force|auto(retired)]
        [--work-root DIR] [--evidence-dir DIR] [--fixture-root DIR]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from replay_support import cleanup as cleanup_mod          # noqa: E402
from replay_support import fixtures as fixtures_mod        # noqa: E402
from replay_support import netguard, observe               # noqa: E402
from replay_support.deploy import (                        # noqa: E402
    READ_ONLY_GIT_VERBS, DeployError, FrozenDeployment, RepoSpec,
    git_operations, repo_activity, repo_head,
)

RUN_STAMP = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
SCENARIO_ORDER = ["S1", "S2", "S3", "S5", "S6", "S4"]
EXIT_PASS, EXIT_FAIL, EXIT_USAGE, EXIT_ENV = 0, 1, 2, 3
LIVE_ENV_VAR = "RF_E2E_LIVE_DOWNLOAD"


# --------------------------------------------------------------------------
# shared bookkeeping
# --------------------------------------------------------------------------

class Scenario:
    def __init__(self, sid: str):
        self.id = sid
        self.status = "pass"
        self.reason: dict | None = None
        self.checks: dict = {}
        self.failures: list[str] = []
        self.processes: list[dict] = []
        self.t0 = time.monotonic()

    def check(self, name: str, condition: bool, detail="") -> None:
        self.checks[name] = bool(condition)
        if not condition:
            self.failures.append(f"{name}: {detail}" if detail else name)

    def equal(self, name: str, actual, expected) -> None:
        self.check(name, actual == expected,
                   f"expected {expected!r}, got {actual!r}")

    def skip(self, code: str, detail: str) -> None:
        self.status = "skip"
        self.reason = {"code": code, "detail": detail}

    def fail(self, code: str, detail: str) -> None:
        self.status = "fail"
        self.reason = {"code": code, "detail": detail}

    def env_unavailable(self, detail: str) -> None:
        self.status = "environment_unavailable"
        self.reason = {"code": "environment_unavailable", "detail": detail}

    def finish(self) -> dict:
        if self.failures and self.status == "pass":
            self.status = "fail"
            self.reason = {"code": "check_failed",
                           "detail": "; ".join(self.failures)[:1500]}
        return {"id": self.id, "status": self.status, "reason": self.reason,
                "checks": self.checks, "failures": self.failures,
                "processes": self.processes,
                "elapsed_s": round(time.monotonic() - self.t0, 3)}


# --------------------------------------------------------------------------
# chain subprocess argv builders (frozen deployment roots only)
# --------------------------------------------------------------------------

def _ff_argv(deployment, config: Path, request_file: Path, *,
             allow_download: bool = False) -> list:
    argv = [sys.executable, "-X", "utf8", "-B",
            str(deployment.ff_scripts / "fetch_filing.py"),
            "--config", str(config), "--request-file", str(request_file),
            "--timeout-seconds", "60"]
    if allow_download:
        argv.append("--allow-download")
    return argv


def _prep_argv(deployment, request_file: Path, ff_config: Path,
               lake_config: Path) -> list:
    return [sys.executable, "-X", "utf8", "-B",
            str(deployment.rf_scripts / "source_preparation.py"),
            "--request-file", str(request_file),
            "--timeout-seconds", "120",
            "--company-wiki-config", str(ff_config),
            "--company-wiki-catalog-config", str(lake_config),
            "--filing-fetch-root", str(deployment.roots["ff"])]


# --------------------------------------------------------------------------
# shared S2/S3/S5/S6 state: the synthetic lake
# --------------------------------------------------------------------------

def _lake_state(ctx) -> dict:
    if "lake" in ctx:
        return ctx["lake"]
    attempt = ctx["attempt"]
    wiki_root = attempt.path / "lake" / "wiki"
    ev = ctx["evidence"]
    build = fixtures_mod.build_lake(
        wiki_root, ctx["fixture_root"], ctx["deployment"].cwp_src,
        env=ctx["env"])
    identity = ctx["manifest"]["identity"]
    ff_config = ev / "ff_config.json"
    ff_config.parent.mkdir(parents=True, exist_ok=True)
    ff_config.write_text(json.dumps(
        {"schema_version": "1.0", "company_wiki_root": str(wiki_root)},
        ensure_ascii=False), encoding="utf-8")
    observe.write_json(ev / "s2" / "lake_build.json", {
        "wiki_root_name": wiki_root.name,
        "catalog_counts": observe.catalog_counts(build.catalog_path),
        "docs": {k: d.__dict__ for k, d in build.docs.items()},
        "scan_returncode": build.scan_returncode,
        "scan_pid": build.scan_pid,
    })
    ctx["lake"] = {"build": build, "ff_config": ff_config,
                   "wiki_root": wiki_root, "identity": identity,
                   "as_of": ctx["manifest"]["as_of_date"]}
    return ctx["lake"]


def _write_request(ctx, name: str, payload: dict) -> Path:
    path = ctx["evidence"] / name
    observe.write_json(path, payload)
    return path


def _base_request(lake: dict, **overrides) -> dict:
    identity = lake["identity"]
    request = {
        "schema_version": "1.1",
        "company_query": identity["ticker"],
        "market": identity["market"],
        "document_kind": "annual_report",
        "fiscal_year": 2024,
        "as_of_date": lake["as_of"],
    }
    request.update(overrides)
    return request


def _last_doc(run: dict) -> dict:
    return run["docs"][-1] if run["docs"] else {}


def _stderr_doc(run: dict) -> dict:
    docs = observe.parse_json_docs(run["stderr"])
    return docs[-1] if docs else {}


# --------------------------------------------------------------------------
# S2 — offline chain success (PDF + TXT) plus preserved error paths
# --------------------------------------------------------------------------

def s2_offline_chain(ctx) -> dict:
    sc = Scenario("S2")
    ev = ctx["evidence"] / "s2"
    try:
        lake = _lake_state(ctx)
    except fixtures_mod.FixtureError as exc:
        sc.fail("lake_build_failed", f"{type(exc).__name__}: {exc}")
        return sc.finish()
    except Exception as exc:  # noqa: BLE001
        sc.fail("lake_build_failed",
                f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-600:]}")
        return sc.finish()
    build = lake["build"]

    # registration happened through the PUBLIC scan CLI (E03)
    sc.equal("s2.scan_exit", build.scan_returncode, 0)
    counts = observe.catalog_counts(build.catalog_path)
    sc.check("s2.documents_registered", counts.get("documents", 0) >= 2,
             str(counts))

    # ---- PDF: FF offline resolve -> RF source_preparation success --------
    pdf = build.docs["annual_pdf"]
    run_a = observe.run_cmd(
        _ff_argv(ctx["deployment"], lake["ff_config"],
                 _write_request(ctx, "s2_request_pdf.json",
                                _base_request(lake))),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=90.0,
        tag="s2_ff_resolve_pdf", ev_dir=ev)
    sc.processes.append({"tag": run_a["tag"], "pid": run_a["pid"]})
    sc.equal("s2.pdf_ff_exit", run_a["rc"], 0)
    payload_a = _last_doc(run_a)
    sc.equal("s2.pdf_ff_status", payload_a.get("status"), "capture_ready")
    sc.equal("s2.pdf_ff_downloads", payload_a.get("downloads"), 0)
    handle = payload_a.get("handle") or {}
    sc.equal("s2.pdf_ff_byte_size", handle.get("byte_size"), pdf.byte_size)
    sc.equal("s2.pdf_ff_snapshot_sha", handle.get("snapshot_sha256"),
             pdf.sha256)
    sc.equal("s2.pdf_ff_pdoc", handle.get("provider_document_id"),
             pdf.provider_document_id)

    run_b = observe.run_cmd(
        _prep_argv(ctx["deployment"], ctx["evidence"] / "s2_request_pdf.json",
                   lake["ff_config"], build.config_path),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=150.0,
        tag="s2_source_prep_pdf", ev_dir=ev)
    sc.processes.append({"tag": run_b["tag"], "pid": run_b["pid"]})
    sc.equal("s2.pdf_prep_exit", run_b["rc"], 0)
    record = _last_doc(run_b)
    if run_b["rc"] == 0 and record:
        trace = record.get("company_wiki_trace") or {}
        source_ref = trace.get("source_ref") or record.get("source_ref") or {}
        sc.equal("s2.pdf_record_sha", source_ref.get("content_sha256"),
                 pdf.sha256)
        sc.equal("s2.pdf_capture_sha",
                 (record.get("capture") or {}).get("snapshot_sha256"),
                 pdf.sha256)
        receipt = trace.get("read_receipt") or {}
        sc.check("s2.pdf_read_receipt_document",
                 bool(str(receipt.get("document_id") or "").strip()),
                 str(receipt)[:200])
        reuse = record.get("reuse_receipt") or {}
        sc.equal("s2.pdf_reuse_downloads", reuse.get("download_calls"), 0)
        sc.equal("s2.pdf_reuse_outcome", reuse.get("outcome"),
                 "reused_existing")
        sc.check("s2.pdf_locator", record.get("page_or_section") == "1",
                 str(record.get("page_or_section")))
        sc.check("s2.pdf_source_type",
                 record.get("source_type") == "regulatory_filing",
                 str(record.get("source_type")))
        observe.write_json(ev / "pdf_record.json", record)
    else:
        sc.check("s2.pdf_record_parsed", False,
                 (run_b["stdout"] + run_b["stderr"])[-400:])

    # ---- TXT companion: same real chain, bytes actually consumed ---------
    txt = build.docs["quarterly_txt"]
    txt_request = _base_request(
        lake, document_kind="quarterly_report", fiscal_year=txt.fiscal_year)
    run_c = observe.run_cmd(
        _ff_argv(ctx["deployment"], lake["ff_config"],
                 _write_request(ctx, "s2_request_txt.json", txt_request)),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=90.0,
        tag="s2_ff_resolve_txt", ev_dir=ev)
    sc.processes.append({"tag": run_c["tag"], "pid": run_c["pid"]})
    sc.equal("s2.txt_ff_exit", run_c["rc"], 0)
    payload_c = _last_doc(run_c)
    sc.equal("s2.txt_ff_status", payload_c.get("status"), "capture_ready")
    sc.equal("s2.txt_ff_downloads", payload_c.get("downloads"), 0)
    handle_c = payload_c.get("handle") or {}
    sc.equal("s2.txt_ff_snapshot_sha", handle_c.get("snapshot_sha256"),
             txt.sha256)

    run_d = observe.run_cmd(
        _prep_argv(ctx["deployment"], ctx["evidence"] / "s2_request_txt.json",
                   lake["ff_config"], build.config_path),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=150.0,
        tag="s2_source_prep_txt", ev_dir=ev)
    sc.processes.append({"tag": run_d["tag"], "pid": run_d["pid"]})
    sc.equal("s2.txt_prep_exit", run_d["rc"], 0)
    record_d = _last_doc(run_d)
    if run_d["rc"] == 0 and record_d:
        trace_d = record_d.get("company_wiki_trace") or {}
        source_ref_d = trace_d.get("source_ref") or {}
        # actually READ, not merely registered: the verified-open manifest
        # must bind the TXT fixture bytes and period
        sc.equal("s2.txt_consumed_sha", source_ref_d.get("content_sha256"),
                 txt.sha256)
        manifest_d = trace_d.get("source_manifest") or {}
        sc.equal("s2.txt_consumed_period",
                 manifest_d.get("fiscal_period"), txt.fiscal_period)
        sc.equal("s2.txt_consumed_year", manifest_d.get("fiscal_year"),
                 txt.fiscal_year)
        observe.write_json(ev / "txt_record.json", record_d)
    else:
        sc.check("s2.txt_record_parsed", False,
                 (run_d["stdout"] + run_d["stderr"])[-400:])

    # ---- preserved error paths: original layered reasons (E04) -----------
    wrong = _base_request(lake, fiscal_year=1999)
    run_e = observe.run_cmd(
        _prep_argv(ctx["deployment"],
                   _write_request(ctx, "s2_request_wrong_period.json", wrong),
                   lake["ff_config"], build.config_path),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=120.0,
        tag="s2_wrong_period", ev_dir=ev)
    sc.processes.append({"tag": run_e["tag"], "pid": run_e["pid"]})
    refusal = _last_doc(run_e) or _stderr_doc(run_e)
    observe.write_json(ev / "wrong_period_refusal.json", {
        "rc": run_e["rc"], "stdout": run_e["stdout"][-800:],
        "stderr": run_e["stderr"][-800:], "parsed": refusal})
    sc.check("s2.wrong_period_nonzero", run_e["rc"] != 0,
             f"rc={run_e['rc']}")
    sc.check("s2.wrong_period_original_reason",
             bool(str(refusal.get("error") or refusal.get("reason") or "")),
             str(refusal)[:300])
    sc.check("s2.wrong_period_no_review_gate",
             "prompt injection" not in str(refusal).lower(),
             str(refusal)[:300])

    empty = _base_request(lake, company_query="")
    run_f = observe.run_cmd(
        _ff_argv(ctx["deployment"], lake["ff_config"],
                 _write_request(ctx, "s2_request_empty_query.json", empty)),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=90.0,
        tag="s2_empty_identity", ev_dir=ev)
    sc.processes.append({"tag": run_f["tag"], "pid": run_f["pid"]})
    empty_doc = _last_doc(run_f) or _stderr_doc(run_f)
    observe.write_json(ev / "empty_identity_refusal.json", {
        "rc": run_f["rc"], "parsed": empty_doc,
        "stdout": run_f["stdout"][-400:], "stderr": run_f["stderr"][-400:]})
    sc.equal("s2.empty_identity_exit", run_f["rc"], 2)
    sc.equal("s2.empty_identity_status", empty_doc.get("status"),
             "request_error")
    sc.check("s2.empty_identity_original_reason",
             "company_query" in str(empty_doc.get("error") or ""),
             str(empty_doc)[:300])
    return sc.finish()


# --------------------------------------------------------------------------
# S3 — second run over the same originals
# --------------------------------------------------------------------------

def s3_second_run(ctx) -> dict:
    sc = Scenario("S3")
    ev = ctx["evidence"] / "s3"
    try:
        lake = _lake_state(ctx)
    except Exception as exc:  # noqa: BLE001
        sc.fail("lake_state_unavailable", f"{type(exc).__name__}: {exc}")
        return sc.finish()
    build = lake["build"]
    baseline_counters = netguard.counter_totals(ctx["guard_dir"])
    pre_counts = observe.catalog_counts(build.catalog_path)
    content_pre = observe.catalog_content_sha(build.catalog_path)
    tree_pre = observe.tree_snapshot(lake["wiki_root"])

    for key, request_name in (("annual_pdf", "s2_request_pdf.json"),
                              ("quarterly_txt", "s2_request_txt.json")):
        doc = build.docs[key]
        run = observe.run_cmd(
            _ff_argv(ctx["deployment"], lake["ff_config"],
                     ctx["evidence"] / request_name),
            cwd=ctx["attempt"].path, env=ctx["env"], timeout=90.0,
            tag=f"s3_ff_resolve_{key}", ev_dir=ev)
        sc.processes.append({"tag": run["tag"], "pid": run["pid"]})
        payload = _last_doc(run)
        sc.equal(f"s3.{key}_ff_exit", run["rc"], 0)
        sc.equal(f"s3.{key}_status", payload.get("status"), "capture_ready")
        sc.equal(f"s3.{key}_downloads", payload.get("downloads"), 0)
        handle = payload.get("handle") or {}
        sc.equal(f"s3.{key}_sha", handle.get("snapshot_sha256"), doc.sha256)

    rerun = observe.run_cmd(
        _prep_argv(ctx["deployment"], ctx["evidence"] / "s2_request_pdf.json",
                   lake["ff_config"], build.config_path),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=150.0,
        tag="s3_source_prep_pdf", ev_dir=ev)
    sc.processes.append({"tag": rerun["tag"], "pid": rerun["pid"]})
    sc.equal("s3.pdf_prep_exit", rerun["rc"], 0)
    record = _last_doc(rerun)
    reuse = record.get("reuse_receipt") or {}
    sc.equal("s3.pdf_reuse_outcome", reuse.get("outcome"), "reused_existing")
    sc.equal("s3.pdf_reuse_downloads", reuse.get("download_calls"), 0)

    post_counters = netguard.counter_totals(ctx["guard_dir"])
    deltas = {k: post_counters.get(k, 0) - baseline_counters.get(k, 0)
              for k in sorted(set(baseline_counters) | set(post_counters))}
    post_counts = observe.catalog_counts(build.catalog_path)
    content_post = observe.catalog_content_sha(build.catalog_path)
    tree_post = observe.tree_snapshot(lake["wiki_root"])
    observe.write_json(ev / "counters.json", {
        "baseline_after_s2": baseline_counters,
        "after_s3": post_counters, "deltas": deltas})
    sc.equal("s3.zero_provider_calls", deltas.get("provider", 0), 0)
    sc.equal("s3.zero_catalog_row_delta",
             observe.catalog_delta(pre_counts, post_counts), {})
    sc.equal("s3.catalog_content_unchanged", content_post, content_pre)
    sc.equal("s3.lake_tree_unchanged", tree_post, tree_pre)
    attempts = netguard.net_attempts(ctx["guard_dir"])
    if attempts:
        observe.write_json(ev / "net_attempts.json", attempts)
    sc.equal("s3.zero_blocked_net_attempts", len(attempts), 0)
    return sc.finish()


# --------------------------------------------------------------------------
# S5 / S6 — honest structured refusals
# --------------------------------------------------------------------------

def s5_bad_filing(ctx) -> dict:
    sc = Scenario("S5")
    ev = ctx["evidence"] / "s5"
    try:
        lake = _lake_state(ctx)
    except Exception as exc:  # noqa: BLE001
        sc.fail("lake_state_unavailable", f"{type(exc).__name__}: {exc}")
        return sc.finish()
    request = _base_request(lake, provider_document_id="does-not-exist-000")
    run = observe.run_cmd(
        _ff_argv(ctx["deployment"], lake["ff_config"],
                 _write_request(ctx, "s5_request.json", request)),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=90.0,
        tag="s5_fetch", ev_dir=ev)
    sc.processes.append({"tag": run["tag"], "pid": run["pid"]})
    payload = _last_doc(run)
    sc.equal("s5.exit_code", run["rc"], 2)
    sc.equal("s5.structured_not_found", payload.get("status"), "not_found")
    sc.check("s5.error_present",
             bool(str(payload.get("error") or payload.get("reason") or "")),
             str(payload)[:300])
    sc.check("s5.no_handle", "handle" not in payload, "handle present")
    sc.equal("s5.zero_downloads", payload.get("downloads"), 0)
    observe.write_json(ev / "refusal.json", payload)
    return sc.finish()


def s6_company_not_found(ctx) -> dict:
    sc = Scenario("S6")
    ev = ctx["evidence"] / "s6"
    try:
        lake = _lake_state(ctx)
    except Exception as exc:  # noqa: BLE001
        sc.fail("lake_state_unavailable", f"{type(exc).__name__}: {exc}")
        return sc.finish()

    unknown = _base_request(lake, company_query="不存在的夹具公司-XYZ-999")
    run = observe.run_cmd(
        _ff_argv(ctx["deployment"], lake["ff_config"],
                 _write_request(ctx, "s6_request_unknown.json", unknown)),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=90.0,
        tag="s6_unknown_company", ev_dir=ev)
    sc.processes.append({"tag": run["tag"], "pid": run["pid"]})
    payload = _last_doc(run)
    sc.equal("s6.unknown_exit", run["rc"], 2)
    sc.check("s6.unknown_structured_status",
             payload.get("status") in ("identity_error", "not_found",
                                       "ambiguous"),
             f"status={payload.get('status')}: {str(payload)[:300]}")
    sc.check("s6.unknown_honest_reason",
             bool(str(payload.get("error") or payload.get("reason") or "")),
             str(payload)[:300])
    sc.check("s6.unknown_no_handle", "handle" not in payload, "handle present")
    observe.write_json(ev / "unknown_refusal.json", payload)

    ambiguous = _base_request(
        lake, company_query=lake["identity"]["ambiguous_alias"])
    run2 = observe.run_cmd(
        _ff_argv(ctx["deployment"], lake["ff_config"],
                 _write_request(ctx, "s6_request_ambiguous.json", ambiguous)),
        cwd=ctx["attempt"].path, env=ctx["env"], timeout=90.0,
        tag="s6_ambiguous_alias", ev_dir=ev)
    sc.processes.append({"tag": run2["tag"], "pid": run2["pid"]})
    payload2 = _last_doc(run2)
    observe.write_json(ev / "ambiguous_refusal.json", payload2)
    sc.check("s6.ambiguous_refused", run2["rc"] != 0
             and payload2.get("status") in ("ambiguous", "identity_error",
                                            "not_found"),
             f"rc={run2['rc']} payload={str(payload2)[:300]}")
    sc.check("s6.ambiguous_no_handle", "handle" not in payload2,
             "handle present")
    return sc.finish()


# --------------------------------------------------------------------------
# S4 — restore invariants
# --------------------------------------------------------------------------

def s4_restore_invariants(ctx) -> dict:
    sc = Scenario("S4")
    ev = ctx["evidence"] / "s4"
    attempt = ctx["attempt"]

    fixture_after = {
        p.name: observe.sha256_file(p)
        for p in sorted(ctx["fixture_root"].glob("*")) if p.is_file()}
    sc.equal("s4.fixtures_unchanged", fixture_after, ctx["fixture_hashes"])
    # persist the actual before/after hash maps, not just the boolean (F3)
    observe.write_json(ev / "restore.json", {
        "fixture_before": ctx["fixture_hashes"],
        "fixture_after": fixture_after,
        "fixtures_unchanged": fixture_after == ctx["fixture_hashes"]})

    # freeze process/network evidence BEFORE the owned scratch (which holds
    # the guard directory) is removed — evidence must outlive the cleanup
    ctx["final_child_processes"] = netguard.child_provenance(ctx["guard_dir"])
    ctx["final_counter_totals"] = netguard.counter_totals(ctx["guard_dir"])
    ctx["final_net_attempts"] = netguard.net_attempts(ctx["guard_dir"])
    ctx["final_install_records"] = netguard.install_records(ctx["guard_dir"])
    observe.write_json(ctx["evidence"] / "processes.json", {
        "child_processes": ctx["final_child_processes"],
        "counter_totals": ctx["final_counter_totals"],
        "net_attempts": ctx["final_net_attempts"],
        "guard_installs": ctx["final_install_records"]})

    evidence_files_before = {
        p.relative_to(ctx["evidence"]).as_posix()
        for p in ctx["evidence"].rglob("*") if p.is_file()}
    report = attempt.cleanup()
    evidence_files_after = {
        p.relative_to(ctx["evidence"]).as_posix()
        for p in ctx["evidence"].rglob("*") if p.is_file()}
    observe.write_json(ev / "cleanup.json", report)
    ctx["s4_ran"] = True
    ctx["cleanup_compact"] = {
        "when": "s4",
        "attempt_removed": report["attempt_removed"],
        "work_root_restored": report["work_root_restored"],
        "attempt_path": report["attempt_path"],
    }
    sc.check("s4.attempt_removed", report["attempt_removed"], str(report))
    sc.check("s4.work_root_restored", report["work_root_restored"],
             str(report["work_root_remaining"]))
    sc.check("s4.evidence_intact",
             evidence_files_before <= evidence_files_after,
             f"missing after cleanup: "
             f"{sorted(evidence_files_before - evidence_files_after)}")

    attempts = ctx["final_net_attempts"]
    if attempts:
        observe.write_json(ev / "net_attempts.json", attempts)
    if ctx["gate"] != "force":
        sc.equal("s4.zero_blocked_net_attempts", len(attempts), 0)

    heads_now = {role: repo_head(spec.repo)
                 for role, spec in ctx["deployment"].specs.items()}
    # HEAD equality of these LIVE SHARED worktrees is not attributable to
    # this run: concurrent sessions commit in them mid-window (observed
    # 2026-10-24).  The attributable no-write guarantee is this process's
    # own git verb log, asserted here and again from the receipt in tests.
    write_ops = [op for op in git_operations()
                 if op["verb"] not in READ_ONLY_GIT_VERBS]
    observe.write_json(ev / "source_repo_heads.json", {
        "before": ctx["repo_heads"], "after": heads_now,
        "head_advanced_externally": {
            role: heads_now[role] != ctx["repo_heads"][role]
            for role in ctx["repo_heads"]},
        "git_write_ops_by_this_run": write_ops,
        "note": "shared live worktrees: HEAD moves during the window are "
                "external-session activity; this run issues only read-only "
                "git verbs (asserted)"})
    sc.equal("s4.no_write_git_verbs_by_this_run", write_ops, [])
    sc.check("s4.source_repo_heads_recorded",
             set(heads_now) == {"rf", "cwp", "ff"}, str(heads_now))
    return sc.finish()


# --------------------------------------------------------------------------
# S1 — live provider download (explicit --live force only)
# --------------------------------------------------------------------------

def s1_download_verify_delete(ctx) -> dict:
    sc = Scenario("S1")
    ev = ctx["evidence"] / "s1"
    if ctx["gate"] != "force":
        sc.skip("live_gate_never",
                "--live force not requested: no network attempted")
        observe.write_json(ev / "deletion_proof.json", {
            "network_allowed": False, "gate": ctx["gate"],
            "post_absent": True, "asserted": True})
        return sc.finish()

    root = os.environ.get("RF_E2E_STOCKINFO_ROOT")
    if not root or not (Path(root) / "src" /
                        "company_wiki_adapter_cli.py").is_file():
        sc.env_unavailable(
            "live download tool absent: RF_E2E_STOCKINFO_ROOT must point at "
            "the StockInfoDLSimple checkout for --live force")
        return sc.finish()
    spec = importlib.util.spec_from_file_location(
        "ff_isolated_wiki", ctx["deployment"].ff_isolated_wiki)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    wiki_dir = ctx["attempt"].path / "s1-wiki"
    try:
        wiki = module.IsolatedWiki(wiki_dir)
        wiki.use_production_adapters()
    except Exception as exc:  # noqa: BLE001
        sc.env_unavailable(f"isolated wiki build failed: {exc}")
        return sc.finish()
    sc.check("s1.wiki_built", wiki_dir.is_dir(), str(wiki_dir))
    removed = ctx["attempt"].rmtree_owned(wiki_dir)
    observe.write_json(ev / "deletion_proof.json", {
        "network_allowed": True, "gate": "force",
        "post_absent": removed, "asserted": removed})
    sc.check("s1.teardown_temp_absent", removed, str(wiki_dir))
    return sc.finish()


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def _live_gate(cli_choice: str) -> tuple[str, list[str]]:
    notices = []
    env_value = os.environ.get(LIVE_ENV_VAR)
    if env_value is not None:
        notices.append(
            f"{LIVE_ENV_VAR} is retired; network requires --live force "
            f"(ignored value length {len(env_value)})")
    if cli_choice == "auto":
        notices.append("--live auto is retired; treated as never")
        return "never", notices
    return cli_choice, notices


def compute_exit_code(statuses: dict) -> int:
    """Map scenario statuses to the documented exit contract (E01/F16).

    - any environment_unavailable -> 3;
    - any offline scenario (everything except S1) that is not PASS —
      including skip/not_executed — is incomplete -> 1 (S1 may honestly
      skip when --live force was not requested);
    - any fail -> 1; otherwise 0.
    """
    if "environment_unavailable" in statuses.values():
        return EXIT_ENV
    if any(status != "pass"
           for sid, status in statuses.items() if sid != "S1"):
        return EXIT_FAIL
    if "fail" in statuses.values():
        return EXIT_FAIL
    return EXIT_PASS


def _roots_overlap(a: Path, b: Path) -> bool:
    return a == b or a in b.parents or b in a.parents


def runner_code_sha() -> dict:
    """sha256 of the runner + every support module (receipt self-binding,
    W14 F17): evidence ties back to the exact reviewed code."""
    out: dict[str, str] = {}
    me = Path(__file__).resolve()
    out[me.relative_to(REPO).as_posix()] = observe.sha256_file(me)
    for path in sorted((HERE / "replay_support").glob("*.py")):
        out[path.relative_to(REPO).as_posix()] = observe.sha256_file(path)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenarios", default=",".join(SCENARIO_ORDER),
                        help="comma list from S1,S2,S3,S4,S5,S6; selection "
                             "is canonicalized to the frozen order (S4 last)")
    parser.add_argument("--live", choices=("auto", "never", "force"),
                        default="never",
                        help="offline by default; auto is retired -> never; "
                             "only force permits S1 network")
    parser.add_argument("--rf-repo", type=Path, required=True)
    parser.add_argument("--rf-commit", required=True)
    parser.add_argument("--cwp-repo", type=Path, required=True)
    parser.add_argument("--cwp-commit", required=True)
    parser.add_argument("--ff-repo", type=Path, required=True)
    parser.add_argument("--ff-commit", required=True)
    parser.add_argument("--work-root", type=Path, default=None,
                        help="isolation parent (NOT deleted; an exclusive "
                             "attempt-<stamp> child is created per run)")
    parser.add_argument("--evidence-dir", type=Path, default=None,
                        help="evidence parent (per-run attempt subdirectory; "
                             "history is never overwritten)")
    parser.add_argument("--fixture-root", type=Path,
                        default=REPO / "tests" / "fixtures" / "w14_chain")
    args = parser.parse_args(argv)

    selected = [s.strip().upper() for s in args.scenarios.split(",")
                if s.strip()]
    unknown = [s for s in selected if s not in SCENARIO_ORDER]
    if unknown:
        print(f"ERROR: unknown scenario(s): {unknown}", file=sys.stderr)
        return EXIT_USAGE
    # historical behavior kept: selection runs in the frozen canonical order
    # (S4 restores invariants, so it is always last when selected)
    ordered = [s for s in SCENARIO_ORDER if s in selected]

    gate, notices = _live_gate(args.live)
    work_root = (args.work_root or Path(tempfile.gettempdir()) /
                 f"rf_w14_chain_{RUN_STAMP}").resolve()
    evidence_root = (args.evidence_dir or
                     HERE / ".runs" / "w14_chain" / RUN_STAMP).resolve()
    fixture_root = args.fixture_root.resolve()
    if _roots_overlap(work_root, evidence_root):
        print("ERROR: --work-root and --evidence-dir must be disjoint "
              "directories (E06: evidence must survive scratch cleanup); "
              f"got {work_root} and {evidence_root}", file=sys.stderr)
        return EXIT_USAGE

    started = time.monotonic()
    attempt = cleanup_mod.AttemptSpace(work_root, evidence_root)
    try:
        attempt.allocate()
    except cleanup_mod.CleanupViolation as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE
    evidence = attempt.evidence_dir()

    summary: dict = {
        "run_id": RUN_STAMP,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "runner_source": str(Path(__file__).resolve()),
        "runner_code_sha256": runner_code_sha(),
        "runner_cwd": str(Path.cwd()),
        "fixture_root": str(fixture_root),
        "live_gate": gate,
        "live_notices": notices,
        "scenarios": [],
        "statuses": {},
    }
    # shared scenario context; S4 freezes final process evidence here before
    # the owned scratch (which holds the guard directory) is removed
    ctx: dict = {}
    specs = {"rf": RepoSpec("rf", args.rf_repo.resolve(), args.rf_commit),
             "cwp": RepoSpec("cwp", args.cwp_repo.resolve(), args.cwp_commit),
             "ff": RepoSpec("ff", args.ff_repo.resolve(), args.ff_commit)}

    def _finish(exit_code: int) -> int:
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        summary["total_elapsed_s"] = round(time.monotonic() - started, 3)
        summary["exit_code"] = exit_code
        if "final_child_processes" in ctx:
            summary["child_processes"] = ctx["final_child_processes"]
        else:
            summary["child_processes"] = netguard.child_provenance(guard_dir)
        if "final_install_records" in ctx:
            summary["guard_install_records"] = ctx["final_install_records"]
        elif guard_dir.is_dir():
            summary["guard_install_records"] = netguard.install_records(
                guard_dir)
        else:
            summary["guard_install_records"] = []
        # E06: every terminal path cleans only its own attempt — when S4 did
        # not run (early failure or selection without S4) clean here, before
        # reading anything else from the scratch
        if ctx.get("s4_ran"):
            summary["cleanup"] = ctx.get("cleanup_compact", {})
        else:
            report = attempt.cleanup()
            observe.write_json(evidence / "early_cleanup.json", report)
            summary["cleanup"] = {
                "when": "finish",
                "attempt_removed": report["attempt_removed"],
                "work_root_restored": report["work_root_restored"],
                "attempt_path": report["attempt_path"],
            }
        # measured source-repo activity (F2/F8): HEAD + porcelain compared
        # across the whole run — not a hardcoded constant
        try:
            activity_after = {role: repo_activity(spec.repo)
                              for role, spec in specs.items()}
        except DeployError as exc:  # git vanished mid-run: report, don't hide
            activity_after = {"error": str(exc)}
        before = ctx.get("activity_before") or {}
        observed = {}
        for role, snap in before.items():
            after_role = activity_after.get(role) or {}
            delta = {}
            for key in ("tracked_changes", "untracked_added"):
                added = sorted(set(after_role.get(key) or [])
                               - set(snap.get(key) or []))
                gone = sorted(set(snap.get(key) or [])
                              - set(after_role.get(key) or []))
                if added or gone:
                    delta[key] = {"added": added, "removed": gone}
            observed[role] = {
                "head_before": snap.get("head"),
                "head_after": after_role.get("head"),
                "head_stable": after_role.get("head") == snap.get("head"),
                "worktree_diff_observed": delta,
            }
        # OBSERVATION (receipt, not pass/fail): these live worktrees are
        # shared with other running sessions, whose edits appear here and
        # cannot be attributed to this run — disclosed in the handoff.
        summary["source_repos_observed"] = observed
        # MEASURED, attributable production-write figure: every git verb
        # this process issued (all must be read-only); a write verb here is
        # a real finding the tests assert against (W14 F2/F8).
        ops = git_operations()
        write_ops = [op for op in ops
                     if op["verb"] not in READ_ONLY_GIT_VERBS]
        summary["production_writes"] = {
            "measured": True,
            "basis": "git verb log of this runner process",
            "git_verbs_used": sorted({op["verb"] for op in ops}),
            "write_git_ops": write_ops,
            "count": len(write_ops),
        }
        observe.write_json(evidence / "summary.json", summary)
        if "final_net_attempts" in ctx:
            attempts = ctx["final_net_attempts"]
        else:
            attempts = netguard.net_attempts(guard_dir)
        if attempts:
            observe.write_json(evidence / "net_attempts.json", attempts)
        observe.write_json(
            evidence / "summary_semantic.json",
            observe.semantic_projection(summary))
        for result in summary["scenarios"]:
            line = f"E2E-{result['id']}: {result['status'].upper()}"
            if result.get("reason"):
                line += f" reason={result['reason'].get('code')}"
            print(line, flush=True)
        print(f"E2E EXIT {exit_code} (total "
              f"{summary['total_elapsed_s']}s) evidence={evidence}",
              flush=True)
        return exit_code

    # ---- deployment (E02): frozen objects or a named environment gap -----
    guard_dir = attempt.path / "guard"
    netguard.materialize_guard(guard_dir)
    scratch = attempt.path / "deploy"
    try:
        # read-only pre-run snapshot of the three source worktrees (F8)
        ctx["activity_before"] = {role: repo_activity(spec.repo)
                                  for role, spec in specs.items()}
        deployment = FrozenDeployment(
            scratch, specs["rf"], specs["cwp"], specs["ff"]).build()
    except DeployError as exc:
        print(f"E2E-ENV: {exc}", file=sys.stderr)
        summary["environment_unavailable"] = str(exc)
        return _finish(EXIT_ENV)

    env, env_evidence = netguard.chain_env(
        deployment, guard_dir, net_block=gate != "force")
    observe.write_json(evidence / "child_env.json", env_evidence)
    for notice in notices:
        print(f"[w14] notice: {notice}", flush=True)

    # provenance: real import roots + repo heads (E02/E03)
    try:
        probe = subprocess.run(
            [sys.executable, "-c",
             "import company_wiki,sys;print(company_wiki.__file__);"
             "print(sys.version)"],
            env=env, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60, check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        # a probe that cannot even start is a named environment gap with
        # full bookkeeping — never a bare traceback with a stranded attempt
        detail = (f"import probe failed to execute: "
                  f"{type(exc).__name__}: {exc}")
        print(f"E2E-ENV: {detail}", file=sys.stderr)
        summary["environment_unavailable"] = detail
        return _finish(EXIT_ENV)
    import_root = (probe.stdout.splitlines() or [""])[0].strip()
    frozen_import_root = str(deployment.cwp_src) in import_root
    repo_heads = {role: repo_head(spec.repo)
                  for role, spec in deployment.specs.items()}
    observe.write_json(evidence / "provenance.json", {
        "deployment": deployment.provenance,
        "import_probe": {"stdout": probe.stdout[:400],
                         "rc": probe.returncode,
                         "company_wiki_file": import_root,
                         "under_frozen_deployment": frozen_import_root},
        "repo_heads": repo_heads,
        "child_provenance": netguard.child_provenance(guard_dir),
        "counter_totals": netguard.counter_totals(guard_dir),
    })
    if not frozen_import_root:
        print(f"E2E-ENV: import probe resolved company_wiki outside the "
              f"frozen deployment: {import_root}", file=sys.stderr)
        summary["environment_unavailable"] = (
            f"import probe resolved company_wiki outside the frozen "
            f"deployment: {import_root}")
        return _finish(EXIT_ENV)

    # fixtures (E04): manifest-bound; divergence is a fixture failure
    try:
        manifest = fixtures_mod.load_manifest(fixture_root)
    except fixtures_mod.FixtureError as exc:
        print(f"E2E-FIXTURE: {exc}", file=sys.stderr)
        summary["fixture_failure"] = str(exc)
        return _finish(EXIT_FAIL)
    fixture_hashes = {p.name: observe.sha256_file(p)
                      for p in sorted(fixture_root.glob("*")) if p.is_file()}

    ctx.update({"attempt": attempt, "evidence": evidence,
                "deployment": deployment, "env": env, "guard_dir": guard_dir,
                "gate": gate, "fixture_root": fixture_root,
                "manifest": manifest, "fixture_hashes": fixture_hashes,
                "repo_heads": repo_heads})
    funcs = {"S1": s1_download_verify_delete, "S2": s2_offline_chain,
             "S3": s3_second_run, "S5": s5_bad_filing,
             "S6": s6_company_not_found, "S4": s4_restore_invariants}

    for sid in ordered:
        print(f"[w14] running {sid} ...", flush=True)
        try:
            result = funcs[sid](ctx)
        except Exception as exc:  # noqa: BLE001
            failed = Scenario(sid)
            failed.fail("harness_exception", f"{type(exc).__name__}: {exc}")
            observe.write_text(evidence / f"{sid}_exception.txt",
                               traceback.format_exc())
            result = failed.finish()
        summary["scenarios"].append(result)
        summary["statuses"][sid] = result["status"]
        print(f"[w14] {sid}: {result['status'].upper()} "
              f"[{result['elapsed_s']}s]", flush=True)

    exit_code = compute_exit_code(summary["statuses"])
    summary["network_scope"] = ("none (offline gate)" if gate != "force"
                                else "S1 explicit live download only")
    return _finish(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
