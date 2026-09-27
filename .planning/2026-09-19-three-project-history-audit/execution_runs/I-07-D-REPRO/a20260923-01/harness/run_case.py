"""I-07-D frozen-argv runner: one judged run of the REAL entry (or one stage
command), with counter baselines/deltas, post-state capture, stage parsing and
C4 deep verification. Writes only under the attempt dir.

Usage:
  run_case.py entry <case_id> <run_no> [allow_download] [sim=<meta_json>]
  run_case.py stage <case_id> <run_no> scan            # product scan CLI (registration stage)
  run_case.py wprobe <probe_dir>                       # counter wiring self-test
  run_case.py live <out_json>                          # provider reachability probe

Product rc is recorded raw; the harness exits 0 whenever evidence was captured.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
FF = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
PY = ATT / "iso" / "venv" / "Scripts" / "python.exe"
SPY = ATT / "harness" / "spy"
CASES_ROOT = Path(os.environ.get("TEMP", r"C:\Temp")) / "i07d" / "cases"

SAMPLES = {
    "S-CN-1": "CN-ZIJIN-2025", "S-HK-1": "HK-XIAOMI-2025", "S-US-1": "US-MSFT-2026",
    "S-CN-2": "CN-ZIJIN-2025", "S-HK-2": "HK-XIAOMI-2025", "S-US-2": "US-MSFT-2026",
    "S-CN-3": "CN-ZIJIN-2025", "S-HK-3": "HK-XIAOMI-2025", "S-US-3": "US-MSFT-2026",
    "REGFAIL-HK": "HK-XIAOMI-2025", "REGFAIL-US": "US-MSFT-2026",
}
IDENT = {
    "CN-ZIJIN-2025": {
        "sha": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
        "market": "CN", "fy": 2025, "query": "601899", "provider": "cninfo",
        "provider_document_id": "1225023658", "published": "2026-03-20",
        "entity_dir": "紫金矿业",
        "raw": "companies\\紫金矿业\\raw\\financial_reports\\annual\\2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf",
    },
    "HK-XIAOMI-2025": {
        "sha": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
        "market": "HK", "fy": 2025, "query": "1810", "provider": "hkexnews",
        "provider_document_id": "12127452", "published": "2026-04-28",
        "entity_dir": "小米集團－Ｗ",
        "raw": "companies\\小米集團－Ｗ\\raw\\financial_reports\\annual\\2026-04-28_hkexnews_12127452_2025年度報告.pdf",
    },
    "US-MSFT-2026": {
        "sha": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
        "market": "US", "fy": 2026, "query": "MSFT", "provider": "sec",
        "provider_document_id": "0001193125-26-323660", "published": "2026-07-29",
        "entity_dir": "MICROSOFT CORP",
        "raw": "companies\\MICROSOFT CORP\\raw\\financial_reports\\annual\\2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
    },
}


def sha(p: Path) -> str | None:
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def request_for(sample: str) -> dict:
    i = IDENT[sample]
    return {"document_kind": "annual_report", "market": i["market"],
            "as_of_date": "2026-09-18", "fiscal_year": i["fy"],
            "company_query": i["query"], "schema_version": "1.1"}


def catalog_counts(cwroot: Path) -> dict:
    cat = cwroot / ".source_catalog" / "catalog.sqlite3"
    con = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    tabs = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    counts = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tabs}
    con.close()
    return counts


def counter_snapshot(spy_dir: Path, label: str) -> dict:
    ev = spy_dir / "events.jsonl"
    lines = [json.loads(l) for l in ev.read_text(encoding="utf-8").splitlines() if l.strip()] \
        if ev.is_file() else []
    totals: dict = {}
    for e in lines:
        totals[e["counter"]] = totals.get(e["counter"], 0) + 1
    snap = {"label": label, "captured_at": datetime.now(timezone.utc).isoformat(),
            "event_lines": len(lines), "totals": totals}
    (spy_dir / f"{label}.json").write_text(
        json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    return snap


def parse_json_docs(text: str) -> list[dict]:
    docs = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return docs


RECOVERY_FIELDS = ("error_code", "error_type", "retryable", "candidates", "next_action",
                   "required", "missing", "gap_plan", "reason", "hint", "status", "reason")


def refusal_analysis(stdout: str, stderr: str) -> dict:
    """C2.2 parser: extract structured actionable-recovery content from the
    refusal documents (both streams), asserting presence/shape."""
    out = {"stdout_docs": parse_json_docs(stdout), "stderr_docs": parse_json_docs(stderr)}
    found = {}
    for d in out["stdout_docs"] + out["stderr_docs"]:
        for k, v in d.items():
            found.setdefault(k, v)
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    found.setdefault(f"{k}.{k2}", v2)
    present = {k: found[k] for k in sorted(found)}
    actionable: dict = {}
    for k in ("candidates", "next_action", "required", "missing", "gap_plan", "hint"):
        if k in found and found[k]:
            actionable[k] = found[k]
    structured_ok = bool(actionable) and all(
        (isinstance(actionable[k], (str, list)) and actionable[k]) for k in actionable)
    generic = {k: found.get(k) for k in ("error_code", "error_type", "status", "retryable", "reason")
               if k in found}
    explicit_missing = None
    msg = str(found.get("error") or "")
    if msg:
        explicit_missing = {"message": msg[:600],
                            "names_missing": any(w in msg for w in (
                                "not reviewed", "no existing source", "missing",
                                "not reusable", "required", "blocked", "not allowed"))}
    out["parsed_fields"] = present
    out["actionable_recovery_fields"] = actionable
    out["structured_actionable_present"] = structured_ok
    out["generic_error_fields"] = generic
    out["explicit_missing_info"] = explicit_missing
    return out


def stages(evidence: dict, cwroot: Path, sample: str, pre_counts: dict,
           post_counts: dict) -> dict:
    """Per-stage verdicts raw→注册→资格→review→适用工件→实际消费."""
    doc_id = f"urn:company-wiki:document:sha256:{IDENT[sample]['sha']}"
    stdout = evidence.get("stdout", "")
    recs = parse_json_docs(stdout)
    record = recs[-1] if recs else None
    is_record = isinstance(record, dict) and "reuse_receipt" in record
    pre_doc = pre_counts.get("documents", 0)
    post_doc = post_counts.get("documents", 0)
    st: dict = {}
    st["raw"] = {
        "raw_exists_after": (cwroot / IDENT[sample]["raw"].replace("\\", os.sep)).is_file()
        if (cwroot / "companies").exists() else False,
        "raw_sha256_after": sha(cwroot / IDENT[sample]["raw"].replace("\\", os.sep))
        if (cwroot / "companies").exists() else None,
        "expected_sha256": IDENT[sample]["sha"],
    }
    st["raw"]["pass"] = st["raw"]["raw_sha256_after"] == IDENT[sample]["sha"] or (
        st["raw"]["raw_sha256_after"] is None and evidence.get("state") == "state3")
    st["注册"] = {"documents_pre": pre_doc, "documents_post": post_doc,
                "delta": post_doc - pre_doc,
                "note": "resolve path cannot scan (code-map Q2); registration stage is scan-only",
                "pass": None}
    st["资格"] = {"record_emitted": is_record, "pass": is_record}
    st["review"] = {"pass": None}
    st["适用工件"] = {"pass": None}
    st["实际消费"] = {"pass": bool(is_record)}
    if is_record:
        rr = record.get("reuse_receipt") or {}
        env = (evidence.get("handle_envelope") or {})
        st["review"]["pass"] = rr.get("prompt_injection_status") not in (None, "not_reviewed")
        st["review"]["value"] = rr.get("prompt_injection_status")
        st["适用工件"]["artifact_read"] = rr.get("artifact_read")
        st["适用工件"]["artifact_read_events_n"] = len(rr.get("artifact_read_events") or [])
        st["适用工件"]["pass"] = bool(rr.get("artifact_read")) and bool(
            rr.get("artifact_read_events"))
        st["实际消费"]["record_keys"] = sorted(record.keys())
        st["资格"]["envelope_outcome"] = rr.get("outcome")
        st["资格"]["download_calls"] = rr.get("download_calls")
    return st


def deep_verify(evidence: dict, sample: str) -> dict:
    """C4: values from real reads — only when a RevenueSourceRecord exists."""
    recs = [d for d in parse_json_docs(evidence.get("stdout", ""))
            if isinstance(d, dict) and "reuse_receipt" in d]
    out = {"performed": bool(recs)}
    if not recs:
        out["skip_reason"] = "no RevenueSourceRecord emitted (refusal path) — C4.2 arm applies"
        return out
    rec = recs[-1]
    i = IDENT[sample]
    trace = rec.get("company_wiki_trace") or {}
    cap = rec.get("capture") or {}
    checks = {}
    canonical = trace.get("canonical_path")
    checks["canonical_path_exists"] = bool(canonical) and Path(canonical).is_file()
    checks["rehash_matches_snapshot"] = (
        sha(Path(canonical)) == cap.get("snapshot_sha256")) if checks["canonical_path_exists"] else None
    checks["document_id_urn_is_frozen_sha"] = (
        str(trace.get("document_id")) == f"urn:company-wiki:document:sha256:{i['sha']}")
    checks["provider_matches"] = trace.get("provider") == i["provider"]
    checks["provider_document_id_matches"] = (
        str(trace.get("provider_document_id")) == i["provider_document_id"])
    checks["published_date"] = rec.get("published_date")
    checks["accessed_date"] = rec.get("accessed_date")
    checks["as_of"] = evidence.get("as_of_date")
    checks["period_order_ok"] = bool(
        checks["published_date"] and checks["accessed_date"] and checks["as_of"]
        and checks["published_date"] <= checks["accessed_date"] <= checks["as_of"])
    # independent recomputation of the product's documented canonicalization
    def canon_sha(value):
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()
    host = cap.get("host_receipt")
    if isinstance(host, dict) and "receipt_sha256" in host:
        tmp = dict(host)
        expect_host = tmp.pop("receipt_sha256")
        checks["host_receipt_sha256_recomputed_ok"] = canon_sha(tmp) == expect_host
    if isinstance(cap.get("receipt_sha256"), str):
        tmp = dict(cap)
        expect_cap = tmp.pop("receipt_sha256")
        checks["capture_receipt_sha256_recomputed_ok"] = canon_sha(tmp) == expect_cap
    rr = rec.get("reuse_receipt") or {}
    checks["artifact_read_events_values"] = [
        {"role": e.get("role"), "bytes_read": e.get("bytes_read"),
         "sha_eq": e.get("content_sha256_actual") == e.get("content_sha256_declared")}
        for e in (rr.get("artifact_read_events") or [])]
    checks["all_reads_verified_values"] = bool(checks["artifact_read_events_values"]) and all(
        v["sha_eq"] for v in checks["artifact_read_events_values"])
    out["checks"] = checks
    return out


def run_entry(case_id: str, run_no: int, allow: bool, sim: str | None) -> int:
    sample = SAMPLES[case_id]
    ident = IDENT[sample]
    cwroot = CASES_ROOT / case_id / "cwroot"
    ev_dir = ATT / "evidence" / "cases" / case_id / f"run{run_no}"
    ev_dir.mkdir(parents=True, exist_ok=True)
    spy_dir = ATT / "evidence" / "cases" / case_id / "counters"
    spy_dir.mkdir(parents=True, exist_ok=True)

    req = request_for(sample)
    req_path = ev_dir / "request.json"
    req_path.write_text(json.dumps(req, ensure_ascii=False, indent=1), encoding="utf-8")
    iso_json = ev_dir / "company_wiki.json"
    iso_json.write_text(json.dumps({
        "schema_version": "1.0",
        "company_wiki_root": str(CASES_ROOT / case_id / "cwroot"),
    }, ensure_ascii=False), encoding="utf-8")

    pre_counts = catalog_counts(cwroot)
    pre_raw = sha(cwroot / ident["raw"].replace("\\", os.sep)) if (cwroot / "companies").exists() else None
    pre_counter = counter_snapshot(spy_dir, f"before_run{run_no}")

    argv = [str(PY), "-X", "utf8", "-B", str(RF / "scripts" / "source_preparation.py"),
            "--request-file", str(req_path),
            "--timeout-seconds", "300",
            "--company-wiki-config", str(iso_json),
            "--filing-fetch-root", str(FF)]
    if allow:
        argv.append("--allow-download")

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SPY), str(RF / "scripts"), str(CW / "src")])
    env["I07D_SPY_DIR"] = str(spy_dir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    if sim:
        env["I07D_SIM_FROZEN_META"] = sim

    t0 = time.monotonic()
    proc = subprocess.run(argv, cwd=str(ATT), env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=420, check=False)
    elapsed = round(time.monotonic() - t0, 3)

    (ev_dir / "stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
    (ev_dir / "stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    (ev_dir / "argv.json").write_text(json.dumps(
        {"argv": argv, "cwd": str(ATT),
         "env_overrides": {k: env[k] for k in
                           ("PYTHONPATH", "I07D_SPY_DIR", "I07D_SIM_FROZEN_META")
                           if k in env}},
        ensure_ascii=False, indent=1), encoding="utf-8")

    post_counter = counter_snapshot(spy_dir, f"after_run{run_no}")
    post_counts = catalog_counts(cwroot)
    post_raw = sha(cwroot / ident["raw"].replace("\\", os.sep)) if (cwroot / "companies").exists() else None

    evidence = {
        "case_id": case_id, "sample": sample, "run": run_no,
        "entry": "RF/scripts/source_preparation.py (real entry, I-00-B argv form)",
        "allow_download": allow, "simulated_provider_fixture": sim,
        "product_returncode": proc.returncode,
        "elapsed_seconds": elapsed,
        "stdout_sha256": hashlib.sha256((proc.stdout or "").encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256((proc.stderr or "").encode()).hexdigest(),
        "stdout": proc.stdout, "stderr": proc.stderr,
        "as_of_date": "2026-09-18",
        "counter_delta": {k: post_counter["totals"].get(k, 0) - pre_counter["totals"].get(k, 0)
                          for k in sorted(set(pre_counter["totals"]) | set(post_counter["totals"]))},
        "counter_totals_before": pre_counter["totals"],
        "counter_totals_after": post_counter["totals"],
        "catalog_counts_before": pre_counts,
        "catalog_counts_after": post_counts,
        "catalog_count_delta": {k: post_counts[k] - pre_counts.get(k, 0)
                                for k in post_counts if post_counts[k] != pre_counts.get(k, 0)},
        "raw_sha_before": pre_raw, "raw_sha_after": post_raw,
        "raw_unchanged": pre_raw == post_raw,
        "expected_raw_sha": ident["sha"],
        "refusal": refusal_analysis(proc.stdout or "", proc.stderr or ""),
    }
    evidence["stages"] = stages(evidence, cwroot, sample, pre_counts, post_counts)
    evidence["deep_verification"] = deep_verify(evidence, sample)
    (ev_dir / "evidence.json").write_text(
        json.dumps({k: v for k, v in evidence.items() if k != "stdout"}, ensure_ascii=False,
                   indent=1, default=str), encoding="utf-8")

    delta = evidence["counter_delta"]
    print(json.dumps({
        "case": case_id, "run": run_no, "rc": proc.returncode,
        "allow": allow, "sim": bool(sim),
        "counters": delta,
        "catalog_delta": evidence["catalog_count_delta"],
        "raw_unchanged": evidence["raw_unchanged"],
        "stages_pass": {k: (v.get("pass") if isinstance(v, dict) else v)
                        for k, v in evidence["stages"].items()},
        "structured_actionable": evidence["refusal"]["structured_actionable_present"],
        "deep_verify": evidence["deep_verification"].get("checks",
            evidence["deep_verification"].get("skip_reason")),
    }, ensure_ascii=False, default=str))
    return 0


def run_scan_stage(case_id: str, run_no: int) -> int:
    """Registration stage: the product's own `cli scan` (the only registration
    entry in the code map), invoked exactly the way fetch_filing builds it."""
    cwroot = CASES_ROOT / case_id / "cwroot"
    ev_dir = ATT / "evidence" / "cases" / case_id / f"scan{run_no}"
    ev_dir.mkdir(parents=True, exist_ok=True)
    spy_dir = ATT / "evidence" / "cases" / case_id / "counters"
    spy_dir.mkdir(parents=True, exist_ok=True)
    pre_counts = catalog_counts(cwroot)
    pre_counter = counter_snapshot(spy_dir, f"before_scan{run_no}")
    argv = [str(PY), "-X", "utf8", "-B", "-m", "company_wiki.source_catalog.cli",
            "--config", str(cwroot / "config" / "source_catalog.yaml"), "scan"]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SPY), str(CW / "src")])
    env["I07D_SPY_DIR"] = str(spy_dir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    t0 = time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=str(cwroot), env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=300, check=False)
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        rc, out, err = -9, (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""), \
            ((exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")) + "\nTIMEOUT"
    elapsed = round(time.monotonic() - t0, 3)
    (ev_dir / "stdout.txt").write_text(out or "", encoding="utf-8")
    (ev_dir / "stderr.txt").write_text(err or "", encoding="utf-8")
    (ev_dir / "argv.json").write_text(json.dumps({"argv": argv, "cwd": str(cwroot)}, indent=1),
                                      encoding="utf-8")
    post_counter = counter_snapshot(spy_dir, f"after_scan{run_no}")
    post_counts = catalog_counts(cwroot)
    rec = {
        "case_id": case_id, "stage": "注册(scan)", "run": run_no,
        "product_returncode": rc, "elapsed_seconds": elapsed,
        "counter_delta": {k: post_counter["totals"].get(k, 0) - pre_counter["totals"].get(k, 0)
                          for k in sorted(set(pre_counter["totals"]) | set(post_counter["totals"]))},
        "catalog_counts_before": pre_counts, "catalog_counts_after": post_counts,
        "catalog_count_delta": {k: post_counts[k] - pre_counts.get(k, 0)
                                for k in post_counts if post_counts[k] != pre_counts.get(k, 0)},
        "stdout_head": (out or "")[:2000], "stderr_head": (err or "")[:2000],
        "refusal": refusal_analysis(out or "", err or ""),
    }
    (ev_dir / "evidence.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    print(json.dumps({"case": case_id, "scan": run_no, "rc": rc,
                      "counters": rec["counter_delta"],
                      "catalog_delta": rec["catalog_count_delta"],
                      "structured_actionable": rec["refusal"]["structured_actionable_present"]},
                     ensure_ascii=False, default=str))
    return 0


def wprobe(probe_dir: str) -> int:
    """C1.3 wiring self-test: each wrapped entry increments its counter on a
    real invocation with NO database INSERT anywhere (throwaway empty catalog
    row counts must be unchanged)."""
    p = Path(probe_dir)
    p.mkdir(parents=True, exist_ok=True)
    spy = p / "spy"
    spy.mkdir(exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SPY), str(RF / "scripts"), str(CW / "src")])
    env["I07D_SPY_DIR"] = str(spy)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # empty product-schema catalog to prove zero INSERTs during the probe
    if str(CW / "src") not in sys.path:
        sys.path.insert(0, str(CW / "src"))
    cat = p / "probe_catalog.sqlite3"
    if cat.exists():
        cat.unlink()
    from company_wiki.source_catalog.store import CatalogStore
    store = CatalogStore(cat)
    store._initialize()
    before = catalog_counts_dir(cat)
    code = r'''
import json, sys, traceback
results = {}
def attempt(name, fn):
    try:
        fn()
        results[name] = {"raised": False}
    except Exception as exc:
        results[name] = {"raised": True, "exc": type(exc).__name__}
import company_wiki.source_catalog.service as service
import company_wiki.source_catalog.resolver as resolver
attempt("scan:SourceCatalog.scan", lambda: service.SourceCatalog.scan(None))
attempt("read:resolver._sha256_of_file", lambda: resolver._sha256_of_file(None))
import company_wiki.source_catalog.scanner as scanner
attempt("scan:scanner.scan_catalog", lambda: scanner.scan_catalog(None))
import company_wiki_source
attempt("read:verify_artifact_reads", lambda: company_wiki_source.verify_artifact_reads(None, None))
import company_wiki.source_catalog.adapter_process as ap
attempt("provider:JsonCommandAdapter.discover", lambda: ap.JsonCommandAdapter.discover(None))
try:
    import requests
    attempt("provider:Session.request", lambda: requests.sessions.Session().request(None))
except Exception as exc:
    results["provider:Session.request"] = {"raised": True, "exc": "import:" + type(exc).__name__}
print(json.dumps(results, ensure_ascii=False))
'''
    proc = subprocess.run([str(PY), "-X", "utf8", "-B", "-c", code], cwd=str(ATT),
                          env=env, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=180, check=False)
    after = catalog_counts_dir(cat)
    wiring = json.loads((spy / "wiring.json").read_text(encoding="utf-8")) \
        if (spy / "wiring.json").is_file() else {}
    ev = spy / "events.jsonl"
    events = [json.loads(l) for l in ev.read_text(encoding="utf-8").splitlines() if l.strip()] \
        if ev.is_file() else []
    totals: dict = {}
    for e in events:
        totals[e["counter"]] = totals.get(e["counter"], 0) + 1
    report = {
        "probe_invocations": proc.stdout.strip()[-4000:],
        "probe_stderr": proc.stderr.strip()[-1500:],
        "probe_returncode": proc.returncode,
        "wiring": wiring,
        "counter_totals_after_probe": totals,
        "catalog_rowcounts_before": before,
        "catalog_rowcounts_after": after,
        "zero_insert_proof": before == after,
        "verdict": {
            "provider_wired": totals.get("provider", 0) > 0,
            "scan_wired": totals.get("scan", 0) > 0,
            "read_wired": totals.get("read", 0) > 0,
            "producer_wired": any(v.get("status") == "wrapped" and v.get("counter") == "producer"
                                  for v in wiring.values()),
            "producer_note": ("producer entries cannot be invoked inertly without a real "
                              "document; wiring is proven by wrap status, invocation proof "
                              "comes from case runs (expected 0 invocations on valid reuse)"),
        },
    }
    outp = ATT / "evidence" / "wprobe.json"
    outp.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"written": str(outp), "totals": totals,
                      "zero_insert": before == after, "rc": proc.returncode},
                     ensure_ascii=False))
    return 0


def catalog_counts_dir(cat: Path) -> dict:
    con = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    tabs = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    counts = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tabs}
    con.close()
    return counts


def live_probe(out_json: str) -> int:
    """C5: HTTPS reachability of the three provider hosts with auth-target
    recording (header NAMES only). No bodies saved."""
    import requests as rq
    targets = [
        {"market": "CN", "provider": "cninfo", "url": "https://www.cninfo.com.cn/",
         "auth_target": "https://www.cninfo.com.cn (public site; no credentials sent)"},
        {"market": "HK", "provider": "hkexnews", "url": "https://www.hkexnews.hk/",
         "auth_target": "https://www.hkexnews.hk (public site; no credentials sent)"},
        {"market": "US", "provider": "sec", "url": "https://www.sec.gov/",
         "auth_target": "https://www.sec.gov (SEC requires a descriptive User-Agent; "
                        "header NAME recorded, value not stored)",
         "headers": {"User-Agent": "revenue-forecast-i07d-audit/1.0 (contact: local-audit)"}},
    ]
    results = []
    for t in targets:
        rec = {k: t[k] for k in ("market", "provider", "url", "auth_target")}
        rec["request_header_names"] = sorted(t.get("headers", {}))
        t0 = time.monotonic()
        try:
            resp = rq.get(t["url"], headers=t.get("headers"), timeout=10,
                          allow_redirects=True, stream=True)
            rec["status"] = resp.status_code
            rec["reachable"] = resp.status_code < 500
            rec["elapsed_s"] = round(time.monotonic() - t0, 2)
            rec["final_host"] = str(resp.url)[:200]
            resp.close()
        except Exception as exc:  # noqa: BLE001
            rec["reachable"] = False
            rec["error"] = f"{type(exc).__name__}: {exc}"[:300]
            rec["elapsed_s"] = round(time.monotonic() - t0, 2)
        results.append(rec)
    payload = {"probed_at": datetime.now(timezone.utc).isoformat(),
               "network_scope": "live reachability only (card clause 5 case evidence); "
                                "no downloads, no manifest re-download",
               "results": results,
               "unreachable_markets": [r["market"] for r in results if not r["reachable"]]}
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def main() -> int:
    mode = sys.argv[1]
    if mode == "entry":
        return run_entry(sys.argv[2], int(sys.argv[3]),
                         "allow_download" in sys.argv,
                         next((a.split("=", 1)[1] for a in sys.argv if a.startswith("sim=")), None))
    if mode == "stage":
        return run_scan_stage(sys.argv[2], int(sys.argv[3]))
    if mode == "wprobe":
        return wprobe(sys.argv[2])
    if mode == "live":
        return live_probe(sys.argv[2])
    raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    sys.exit(main())
