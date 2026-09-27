"""I-07-D fault-matrix orchestrator (F01-F06, oracle.md §2/§3 frozen plans).

Run subcommands (bound in commands.json before any judged run):
  build        build cells F01..F05 (fresh per cell) + F01 fixture config + iso/rf
  wprobe       counter-wiring self-test (zero-insert proof)
  snap         before|after|iso   (snapshot.py wrapper)
  f01..f05     execute one cell's frozen phase sequence (evidence per run)
  f06a|f06b|f06c  execute one publication sub-cell: seed -> fault -> rec1 -> rec2
  verdicts     aggregate evidence/verdicts.json (trigger counts vs oracle table)

Every product rc is recorded RAW; harness rc: 0 all evidence captured,
1 harness failure, 3 frozen expectation not met (see commands.json legend).
Product files are never modified; writes stay in ATT/** and %TEMP%\\i07d\\**.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_case as RC  # noqa: E402
from common import (  # noqa: E402
    ATTEMPT, ISO_RF, KILL_EXIT_CODE, PY, case_dir, child_env, hard_kill,
    make_input_docs, read_json, registry_path_for, sha256_file, setup_paths,
    write_json,
)

ATT = ATTEMPT
RF, CW, FF = RC.RF, RC.CW, RC.FF
SPY = ATT / "harness" / "spy"
CASES = Path(os.environ.get("TEMP", r"C:\Temp")) / "i07d" / "cases"
FIX403 = ATT / "harness" / "fixture_403_adapter.py"
FIXTURE_LOG = ATT / "evidence" / "cases" / "F01" / "fixture_log.jsonl"
SIM_META = ATT / "fixtures"
CELL_SAMPLE = {"F01": "CN-ZIJIN-2025", "F02": "HK-XIAOMI-2025",
               "F03": "HK-XIAOMI-2025", "F04": "HK-XIAOMI-2025",
               "F05": "CN-ZIJIN-2025"}
STILL_ACTIVE = 259


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_sha(path: Path):
    """Hash a raw file; while a fault holder owns it (share-none), the harness
    cannot read it either — record that explicitly instead of crashing."""
    try:
        return sha256_file(path)
    except PermissionError:
        return "UNREADABLE_HELD_BY_FAULT_FIXTURE"


def cwroot_of(case: str) -> Path:
    return CASES / case / "cwroot"


def pid_alive(pid: int) -> bool:
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(0x1000, False, int(pid))  # SYNCHRONIZE
    if not h:
        return False
    try:
        code = ctypes.c_ulong()
        if k32.GetExitCodeProcess(h, ctypes.byref(code)):
            return code.value == STILL_ACTIVE
        return False
    finally:
        k32.CloseHandle(h)


def counters_dir(case: str) -> Path:
    d = case_dir(case) / "counters"
    d.mkdir(parents=True, exist_ok=True)
    return d


def state_dir(case: str) -> Path:
    d = case_dir(case) / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def entry_env(case: str, *, sim: str | None = None, fault: str | None = None,
              fixture_log: bool = False) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(SPY), str(RF / "scripts"), str(CW / "src")])
    env["I07D_SPY_DIR"] = str(counters_dir(case))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    if sim:
        env["I07D_SIM_FROZEN_META"] = sim
    if fault:
        env["I07D_FAULT"] = fault
        env["I07D_STATE_DIR"] = str(state_dir(case))
    if fixture_log:
        env["I07D_FIXTURE_LOG"] = str(FIXTURE_LOG)
    return env


def cli_env(case: str) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(SPY), str(CW / "src")])
    env["I07D_SPY_DIR"] = str(counters_dir(case))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    return env


def verify_and_kill(state: Path, must_contain: str, timeout: float) -> dict:
    """Kill gate (oracle §5): barrier + self-written pid manifest + cmdline/cwd
    referencing the case's scratch path + alive.  Kills ONLY the registered PID."""
    out: dict = {"expected_path_substring": must_contain, "killed": {}, "timed_out": False}
    t0 = time.time()
    handled: set[int] = set()
    while time.time() - t0 < timeout:
        for b in sorted(state.glob("barrier_*.json")):
            try:
                pid = int(b.stem.split("_", 1)[1])
            except ValueError:
                continue
            if pid in handled:
                continue
            mf = state / f"pid_{pid}.json"
            if not mf.exists():
                out.setdefault("barrier_without_manifest", []).append(b.name)
                continue
            man = read_json(mf)
            argv_txt = " ".join(str(x) for x in (man.get("argv") or []))
            cwd_txt = str(man.get("cwd") or "")
            checks = {
                "manifest_present": True,
                "manifest_path_in_argv": must_contain.lower() in argv_txt.lower(),
                "manifest_path_in_cwd": must_contain.lower() in cwd_txt.lower(),
                "alive_before": pid_alive(pid),
            }
            # F04 wiki child: argv AND cwd both reference the cell (config arg +
            # cwd=company_wiki_root).  F06c writer: argv references ATT (run-dir)
            # and cwd = iso/rf (under ATT).  Both must hold (binding kill gate).
            path_ok = (checks["manifest_path_in_argv"]
                       and checks["manifest_path_in_cwd"])
            if not path_ok or not checks["alive_before"]:
                out.setdefault("gate_failed_not_killed", []).append(
                    {"pid": pid, "checks": checks})
                handled.add(pid)
                continue
            kr = hard_kill(pid, KILL_EXIT_CODE)
            time.sleep(0.6)
            checks["alive_after"] = pid_alive(pid)
            handled.add(pid)
            out["killed"][str(pid)] = {
                "barrier": str(b), "manifest": man, "checks": checks,
                "kill": kr,
                "released_marker_present": (state / f"pid_{pid}.released.json").exists(),
                "killed_at": utc(),
            }
        if out["killed"] or out.get("gate_failed_not_killed"):
            break
        time.sleep(0.1)
    if not out["killed"] and not out.get("gate_failed_not_killed"):
        out["timed_out"] = True
        out["barrier_files_at_timeout"] = [p.name for p in state.glob("barrier_*.json")]
    return out


def save_run(evd: Path, argv, cwd, env, rc, out, err, elapsed, extra,
             started_unix: float | None = None) -> dict:
    (evd / "stdout.txt").write_text(out or "", encoding="utf-8")
    (evd / "stderr.txt").write_text(err or "", encoding="utf-8")
    overrides = {k: env[k] for k in
                 ("PYTHONPATH", "I07D_SPY_DIR", "I07D_SIM_FROZEN_META",
                  "I07D_FAULT", "I07D_STATE_DIR", "I07D_FIXTURE_LOG",
                  "REVENUE_PUBLICATION_REGISTRY") if k in env}
    started_iso = (datetime.fromtimestamp(started_unix, timezone.utc).isoformat()
                   if started_unix else None)
    (evd / "argv.json").write_text(json.dumps(
        {"argv": argv, "cwd": str(cwd), "env_overrides": overrides,
         "started_at": started_iso, "recorded_after_run": utc(),
         "elapsed_seconds": round(elapsed, 3)},
        ensure_ascii=False, indent=1), encoding="utf-8")
    rec = {
        "product_returncode": rc,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_sha256": hashlib.sha256((out or "").encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256((err or "").encode()).hexdigest(),
        "refusal": RC.refusal_analysis(out or "", err or ""),
        **extra,
    }
    write_json(evd / "evidence.json", rec)
    return rec


def run_entry(case: str, label: str, *, allow: bool = False, sim: str | None = None,
              fault: str | None = False, kill: bool = False,
              kill_path: str | None = None, kill_timeout: float = 300.0,
              fixture_log: bool = False) -> dict:
    sample = CELL_SAMPLE[case]
    ident = RC.IDENT[sample]
    cwroot = cwroot_of(case)
    evd = case_dir(case) / label
    evd.mkdir(parents=True, exist_ok=True)

    req = evd / "request.json"
    req.write_text(json.dumps(RC.request_for(sample), ensure_ascii=False, indent=1),
                   encoding="utf-8")
    cwj = evd / "company_wiki.json"
    cwj.write_text(json.dumps({"schema_version": "1.0",
                               "company_wiki_root": str(cwroot)},
                              ensure_ascii=False), encoding="utf-8")

    pre_cat = RC.catalog_counts(cwroot)
    raw_path = cwroot / ident["raw"].replace("\\", os.sep)
    pre_raw = safe_sha(raw_path) if raw_path.is_file() else None
    pre_cnt = RC.counter_snapshot(counters_dir(case), f"before_{label}")

    argv = [str(PY), "-X", "utf8", "-B", str(RF / "scripts" / "source_preparation.py"),
            "--request-file", str(req), "--timeout-seconds", "300",
            "--company-wiki-config", str(cwj), "--filing-fetch-root", str(FF)]
    if allow:
        argv.append("--allow-download")
    env = entry_env(case, sim=sim, fault=fault or None, fixture_log=fixture_log)

    killrec = None
    t0 = time.time()
    if kill:
        proc = subprocess.Popen(argv, cwd=str(ATT), env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace")
        killrec = verify_and_kill(state_dir(case), kill_path or str(CASES / case),
                                  kill_timeout)
        try:
            out, err = proc.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            killrec["entry_forcefully_killed_after_timeout"] = True
        rc = proc.returncode
    else:
        cp = subprocess.run(argv, cwd=str(ATT), env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace",
                            timeout=420, check=False)
        rc, out, err = cp.returncode, cp.stdout, cp.stderr
    elapsed = time.time() - t0

    post_cnt = RC.counter_snapshot(counters_dir(case), f"after_{label}")
    post_cat = RC.catalog_counts(cwroot)
    post_raw = safe_sha(raw_path) if raw_path.is_file() else None
    success_markers = [m for m in ("reuse_receipt", "source_id", "resolution_envelope")
                       if m in (out or "")]
    extra = {
        "cell": case, "label": label, "entry": "RF/scripts/source_preparation.py",
        "sample": sample, "allow_download": allow, "simulated_provider": bool(sim),
        "armed_fault": fault or None,
        "counter_delta": {k: post_cnt["totals"].get(k, 0) - pre_cnt["totals"].get(k, 0)
                          for k in sorted(set(pre_cnt["totals"]) | set(post_cnt["totals"]))},
        "counter_totals_before": pre_cnt["totals"], "counter_totals_after": post_cnt["totals"],
        "catalog_counts_before": pre_cat, "catalog_counts_after": post_cat,
        "catalog_count_delta": {k: post_cat[k] - pre_cat.get(k, 0)
                                for k in post_cat if post_cat[k] != pre_cat.get(k, 0)},
        "raw_sha_before": pre_raw, "raw_sha_after": post_raw,
        "raw_unchanged": pre_raw == post_raw, "expected_raw_sha": ident["sha"],
        "stdout_success_markers": success_markers,
        "stdout_has_consumable_record": bool(success_markers),
        "kill_record": killrec,
        "captured_at": utc(),
    }
    rec = save_run(evd, argv, ATT, env, rc, out, err, elapsed, extra,
                   started_unix=t0)
    print(json.dumps({"cell": case, "label": label, "rc": rc,
                      "counters": extra["counter_delta"],
                      "catalog_delta": extra["catalog_count_delta"],
                      "raw_unchanged": extra["raw_unchanged"],
                      "kill": bool(killrec and killrec.get("killed")),
                      "consumable_stdout": extra["stdout_has_consumable_record"]},
                     ensure_ascii=False))
    return rec


def run_direct(case: str, label: str, which: str) -> dict:
    """F01 chain-capture diagnostics: direct fetch_filing / filing_fetch_client
    runs under the same fault to preserve the FULL envelope/stderr (the entry
    embeds only the last 800 chars)."""
    sample = CELL_SAMPLE[case]
    cwroot = cwroot_of(case)
    evd = case_dir(case) / label
    evd.mkdir(parents=True, exist_ok=True)
    req = evd / "request.json"
    req.write_text(json.dumps(RC.request_for(sample), ensure_ascii=False, indent=1),
                   encoding="utf-8")
    cwj = evd / "company_wiki.json"
    cwj.write_text(json.dumps({"schema_version": "1.0",
                               "company_wiki_root": str(cwroot)},
                              ensure_ascii=False), encoding="utf-8")
    pre_cnt = RC.counter_snapshot(counters_dir(case), f"before_{label}")
    if which == "ff":
        argv = [str(PY), "-X", "utf8", "-B", str(FF / "scripts" / "fetch_filing.py"),
                "--request-file", str(req), "--allow-download",
                "--config", str(cwj), "--timeout-seconds", "300"]
    else:  # client
        argv = [str(PY), "-X", "utf8", "-B", str(RF / "scripts" / "filing_fetch_client.py"),
                "--request-file", str(req), "--allow-download",
                "--timeout-seconds", "300", "--filing-fetch-root", str(FF),
                "--company-wiki-config", str(cwj)]
    env = entry_env(case, fixture_log=True)
    t0 = time.time()
    cp = subprocess.run(argv, cwd=str(ATT), env=env, capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        timeout=420, check=False)
    elapsed = time.time() - t0
    post_cnt = RC.counter_snapshot(counters_dir(case), f"after_{label}")
    extra = {"cell": case, "label": label, "entry": which,
             "chain_capture": True,
             "counter_delta": {k: post_cnt["totals"].get(k, 0) - pre_cnt["totals"].get(k, 0)
                               for k in sorted(set(pre_cnt["totals"]) | set(post_cnt["totals"]))},
             "captured_at": utc()}
    rec = save_run(evd, argv, ATT, env, cp.returncode, cp.stdout, cp.stderr,
                   elapsed, extra, started_unix=t0)
    print(json.dumps({"cell": case, "label": label, "which": which,
                      "rc": cp.returncode, "counters": extra["counter_delta"]},
                     ensure_ascii=False))
    return rec


def run_cli(case: str, label: str, sub: str, extra_args: list[str] | None = None,
            dump_scan_runs: bool = False) -> dict:
    cwroot = cwroot_of(case)
    evd = case_dir(case) / label
    evd.mkdir(parents=True, exist_ok=True)
    pre_cat = RC.catalog_counts(cwroot)
    pre_cnt = RC.counter_snapshot(counters_dir(case), f"before_{label}")
    ident = RC.IDENT[CELL_SAMPLE[case]]
    raw_path = cwroot / ident["raw"].replace("\\", os.sep)
    pre_raw = safe_sha(raw_path) if raw_path.is_file() else None
    argv = [str(PY), "-X", "utf8", "-B", "-m", "company_wiki.source_catalog.cli",
            "--config", str(cwroot / "config" / "source_catalog.yaml"), sub] + \
           (extra_args or [])
    env = cli_env(case)
    t0 = time.time()
    cp = subprocess.run(argv, cwd=str(cwroot), env=env, capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        timeout=600, check=False)
    elapsed = time.time() - t0
    post_cnt = RC.counter_snapshot(counters_dir(case), f"after_{label}")
    post_cat = RC.catalog_counts(cwroot)
    post_raw = safe_sha(raw_path) if raw_path.is_file() else None
    extra = {
        "cell": case, "label": label, "subcommand": sub,
        "counter_delta": {k: post_cnt["totals"].get(k, 0) - pre_cnt["totals"].get(k, 0)
                          for k in sorted(set(pre_cnt["totals"]) | set(post_cnt["totals"]))},
        "catalog_counts_before": pre_cat, "catalog_counts_after": post_cat,
        "catalog_count_delta": {k: post_cat[k] - pre_cat.get(k, 0)
                                for k in post_cat if post_cat[k] != pre_cat.get(k, 0)},
        "raw_sha_before": pre_raw, "raw_sha_after": post_raw,
        "raw_unchanged": pre_raw == post_raw,
        "started_at": utc(), "captured_at": utc(),
    }
    rec = save_run(evd, argv, cwroot, env, cp.returncode, cp.stdout, cp.stderr,
                   elapsed, extra, started_unix=t0)
    if dump_scan_runs:
        import sqlite3
        cat = cwroot / ".source_catalog" / "catalog.sqlite3"
        con = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
        con.execute("PRAGMA query_only=ON")
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute(
            "SELECT run_id,status,started_at,completed_at,report_json FROM scan_runs "
            "ORDER BY started_at")]
        con.close()
        write_json(evd / "scan_runs.json", rows)
        rec["scan_runs"] = [{k: r[k] for k in ("run_id", "status")} for r in rows]
    print(json.dumps({"cell": case, "label": label, "sub": sub,
                      "rc": cp.returncode, "counters": extra["counter_delta"],
                      "catalog_delta": extra["catalog_count_delta"],
                      "raw_unchanged": extra["raw_unchanged"]}, ensure_ascii=False))
    return rec


def start_holder(case: str, target: Path, label: str) -> subprocess.Popen:
    st = state_dir(case)
    proc = subprocess.Popen(
        [str(PY), str(ATT / "harness" / "hold_file.py"), str(target), str(st), label,
         "--max-hold", "300"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace")
    t0 = time.time()
    ready = st / f"ready_{label}.json"
    while time.time() - t0 < 30:
        if ready.exists():
            return proc
        if proc.poll() is not None:
            out, err = proc.communicate()
            raise RuntimeError(f"holder died before ready: {err or out}")
        time.sleep(0.05)
    proc.kill()
    raise RuntimeError("holder ready timeout")


def stop_holder(case: str, label: str, proc: subprocess.Popen) -> dict:
    st = state_dir(case)
    (st / f"release_{label}.json").write_text('{"release": true}', encoding="utf-8")
    try:
        out, err = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
    hold = read_json(st / f"hold_{label}.json")
    write_json(case_dir(case) / f"hold_record_{label}.json",
               {"stdout": out, "stderr": err, "hold": hold})
    return hold


def start_lock(case: str, hold_s: float) -> subprocess.Popen:
    return subprocess.Popen(
        [str(PY), str(ATT / "harness" / "lock_catalog.py"), case, str(hold_s)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace")


def wait_lock_released(case: str, proc: subprocess.Popen) -> dict:
    try:
        out, err = proc.communicate(timeout=180)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
    hold_path = case_dir(case) / "lock" / "hold.json"
    hold = read_json(hold_path) if hold_path.exists() else {"missing": True,
                                                            "stdout": out, "stderr": err}
    return hold


# ---------------------------------------------------------------- F01 config
def f01_edit_config() -> dict:
    import yaml
    cell_cfg = CASES / "F01" / "cwroot" / "config" / "source_acquisition.yaml"
    before = sha256_file(cell_cfg)
    cfg = yaml.safe_load(cell_cfg.read_text(encoding="utf-8"))
    old = dict(cfg["adapters"]["cn"])
    cfg["adapters"]["cn"]["command"] = [str(PY), str(FIX403)]
    cell_cfg.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False),
                        encoding="utf-8")
    after = sha256_file(cell_cfg)
    rec = {"config": str(cell_cfg), "sha_before": before, "sha_after": after,
           "adapter": "cn", "old_command": old.get("command"),
           "new_command": [str(PY), str(FIX403)],
           "project_root_unchanged": old.get("project_root"),
           "note": "isolated per-cell config edit (oracle §2 F01); product files untouched"}
    write_json(case_dir("F01") / "config_edit.json", rec)
    return rec


# ---------------------------------------------------------------- F05 seed
def seed_f05() -> dict:
    import sqlite3
    case = "F05"
    sample = CELL_SAMPLE[case]
    cwroot = cwroot_of(case)
    doc_id = f"urn:company-wiki:document:sha256:{RC.IDENT[sample]['sha']}"
    cat = cwroot / ".source_catalog" / "catalog.sqlite3"
    con = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    con.row_factory = sqlite3.Row
    docs = [dict(r) for r in con.execute("SELECT * FROM documents WHERE document_id=?",
                                         (doc_id,))]
    con.close()
    if not docs:
        return {"ok": False, "blocked": "scan did not register the document",
                "document_id": doc_id}
    prod = RC.Path(str(CW)) / ".source_catalog" / "catalog.sqlite3"
    pcon = sqlite3.connect(f"file:{prod}?mode=ro", uri=True)
    pcon.execute("PRAGMA query_only=ON")
    pcon.row_factory = sqlite3.Row
    arows = [dict(r) for r in pcon.execute(
        "SELECT * FROM artifacts WHERE document_id=? AND artifact_role='normalized'",
        (doc_id,))]
    summaries = [dict(r) for r in pcon.execute(
        "SELECT artifact_role FROM artifacts WHERE document_id=? AND artifact_role='summary'",
        (doc_id,))]
    pcon.close()
    if not arows:
        return {"ok": False, "blocked": "no production normalized artifact row",
                "document_id": doc_id}
    row = arows[0]
    prod_path = row["path"]
    prod_file = RC.Path(prod_path)
    if not prod_file.is_file():
        return {"ok": False, "blocked": f"normalized file missing: {prod_path}"}
    src_sha = sha256_file(prod_file)
    # relocate path into the cell
    rel = prod_path[len(str(CW)):] if prod_path.startswith(str(CW)) else None
    if rel is None:
        return {"ok": False, "blocked": "production path not under CW root",
                "path": prod_path}
    dst = cwroot / rel.lstrip("\\/")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(prod_file, dst)
    dst_sha = sha256_file(dst)
    row["path"] = str(dst)
    con = sqlite3.connect(cat)
    cols = list(row.keys())
    con.execute(f'INSERT OR IGNORE INTO artifacts ({",".join(cols)}) VALUES '
                f'({",".join("?" * len(cols))})', tuple(row[c] for c in cols))
    con.commit()
    c2 = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
    c2.execute("PRAGMA query_only=ON")
    c2.row_factory = sqlite3.Row
    cell_norm = [dict(r) for r in c2.execute(
        "SELECT artifact_id,artifact_role,path,content_sha256,status,created_at "
        "FROM artifacts WHERE document_id=? AND artifact_role='normalized'", (doc_id,))]
    cell_sum = [dict(r) for r in c2.execute(
        "SELECT artifact_id FROM artifacts WHERE document_id=? AND artifact_role='summary'",
        (doc_id,))]
    docs2 = [dict(r) for r in c2.execute(
        "SELECT document_id,primary_source_id FROM documents WHERE document_id=?",
        (doc_id,))]
    c2.close()
    con.close()
    rec = {
        "ok": True, "document_id": doc_id,
        "provenance": "production_observation_copy: artifacts row (role=normalized) + "
                      "derived file copied read-only from production; paths relocated; "
                      "role summary ABSENT BY CONSTRUCTION (partial-roles input state)",
        "production_artifact_id": row["artifact_id"],
        "production_row": {k: row[k] for k in
                           ("artifact_role", "content_sha256", "status", "created_at")},
        "file_copy": {"prod_path": prod_path, "cell_path": str(dst),
                      "prod_sha256": src_sha, "cell_sha256": dst_sha,
                      "match": src_sha == dst_sha},
        "cell_normalized_rows": cell_norm,
        "cell_summary_rows_after_seed": len(cell_sum),
        "summary_absent_by_construction": len(cell_sum) == 0,
        "document_row_after_scan": docs2,
        "production_summary_row_exists": bool(summaries),
    }
    write_json(case_dir("F05") / "f05_seed.json", rec)
    return rec


def dump_cell_state(case: str, label: str) -> dict:
    import sqlite3
    cwroot = cwroot_of(case)
    cat = cwroot / ".source_catalog" / "catalog.sqlite3"
    con = sqlite3.connect(f"file:{cat}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    con.row_factory = sqlite3.Row
    counts = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
              for (t,) in con.execute(
                  "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
    arts = [dict(r) for r in con.execute(
        "SELECT document_id,artifact_role,path,content_sha256,status,created_at "
        "FROM artifacts ORDER BY artifact_role")]
    con.close()
    derived = []
    droot = cwroot / ".source_catalog" / "derived"
    if droot.is_dir():
        for p in sorted(droot.rglob("*")):
            if p.is_file():
                derived.append({"rel": str(p.relative_to(cwroot)),
                                "sha256": sha256_file(p), "bytes": p.stat().st_size})
    rec = {"cell": case, "label": label, "captured_at": utc(),
           "catalog_counts": counts, "artifacts": arts, "derived_files": derived}
    write_json(case_dir(case) / f"state_{label}.json", rec)
    return rec


# ---------------------------------------------------------------- F06
F06_SUBS = {"f06a": "err:append_registry",
            "f06b": "err:replace:output_markdown",
            "f06c": "kill:return:before"}


def spawn_writer(sub: str, label: str, fault: str, input_path: Path,
                 run_dir: Path) -> subprocess.Popen:
    reg = registry_path_for(_f06_case(sub))
    env = child_env(reg)
    argv = [str(PY), str(ATT / "harness" / "writer.py"),
            "--run-dir", str(run_dir), "--input", str(input_path),
            "--output", str(run_dir / f"{Path(input_path).stem.replace('input_', '')}.json"),
            "--markdown", str(run_dir / f"{Path(input_path).stem.replace('input_', '')}.md"),
            "--fault", fault, "--label", label]
    return subprocess.Popen(argv, cwd=str(ISO_RF), env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace")


def _f06_case(sub: str) -> str:
    return {"f06a": "F06A", "f06b": "F06B", "f06c": "F06C"}[sub]


def run_reader(sub: str, label: str, run_dir: Path) -> dict:
    case = _f06_case(sub)
    reg = registry_path_for(case)
    out = case_dir(case) / f"{label}.json"
    env = child_env(reg)
    argv = [str(PY), str(ATT / "harness" / "d_reader.py"),
            "--run-dir", str(run_dir), "--registry", str(reg),
            "--out", str(out), "--label", label,
            "--input-p0", str(run_dir / "input_p0.json"),
            "--input-p1", str(run_dir / "input_p1.json"),
            "--json-p0", str(run_dir / "p0.json"), "--json-p1", str(run_dir / "p1.json"),
            "--md-p0", str(run_dir / "p0.md"), "--md-p1", str(run_dir / "p1.md")]
    cp = subprocess.run(argv, cwd=str(ATT), env=env, capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        timeout=120, check=False)
    (case_dir(case) / f"{label}_stdout.txt").write_text(cp.stdout or "",
                                                        encoding="utf-8")
    (case_dir(case) / f"{label}_stderr.txt").write_text(cp.stderr or "",
                                                        encoding="utf-8")
    (case_dir(case) / f"{label}_argv.json").write_text(json.dumps(
        {"argv": argv, "cwd": str(ATT), "rc": cp.returncode}, indent=1),
        encoding="utf-8")
    return read_json(out) if out.exists() else {"error": "reader produced no output",
                                                "rc": cp.returncode}


def writer_run(sub: str, label: str, fault: str, run_dir: Path,
               inputs: dict, kill: bool = False) -> dict:
    case = _f06_case(sub)
    input_path = Path(inputs["p1" if label != "seed" else "p0"])
    if kill:
        proc = spawn_writer(sub, label, fault, input_path, run_dir)
        killrec = verify_and_kill(run_dir, str(ATT), 300.0)
        try:
            out, err = proc.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            # launcher should have died with the child; if not, kill it (its
            # pid == manifest parent_pid, so still inside the manifest gate)
            mf = list(run_dir.glob("pid_*.json"))
            ppid = None
            for m in mf:
                man = read_json(m)
                if man.get("parent_pid") == proc.pid:
                    ppid = proc.pid
            if ppid:
                killrec.setdefault("launcher_kill", hard_kill(ppid, KILL_EXIT_CODE))
            out, err = proc.communicate(timeout=30)
        rc = proc.returncode
    else:
        proc = spawn_writer(sub, label, fault, input_path, run_dir)
        killrec = None
        try:
            out, err = proc.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            killrec = {"writer_timeout": True}
        rc = proc.returncode
    wdir = case_dir(case) / f"{label}_writer"
    wdir.mkdir(parents=True, exist_ok=True)
    (wdir / "stdout.txt").write_text(out or "", encoding="utf-8")
    (wdir / "stderr.txt").write_text(err or "", encoding="utf-8")
    write_json(wdir / "result.json",
               {"label": label, "fault": fault, "product_returncode": rc,
                "kill_record": killrec, "captured_at": utc(),
                "stderr_sha256": hashlib.sha256((err or "").encode()).hexdigest()})
    print(json.dumps({"f06": sub, "label": label, "fault": fault, "rc": rc,
                      "killed": bool(killrec and killrec.get("killed"))},
                     ensure_ascii=False))
    return {"rc": rc, "kill_record": killrec, "stderr": err or "", "stdout": out or ""}


def f06_runs(sub: str) -> dict:
    fault = F06_SUBS[sub]
    case = _f06_case(sub)
    cdir = case_dir(case)
    run_dir = cdir / "state"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "registry").mkdir(parents=True, exist_ok=True)
    inputs = make_input_docs(run_dir)

    readers = {}
    seed = writer_run(sub, "seed", "none", run_dir, inputs, kill=False)
    readers["reader_after_seed_p0"] = run_reader(sub, "reader_after_seed_p0", run_dir)

    fault_res = writer_run(sub, "fault", fault, run_dir, inputs,
                           kill=(sub == "f06c"))
    readers["reader_after_fault"] = run_reader(sub, "reader_after_fault", run_dir)

    rec1 = writer_run(sub, "recovery1", "none", run_dir, inputs, kill=False)
    readers["reader_after_recovery1"] = run_reader(sub, "reader_after_recovery1", run_dir)

    rec2 = writer_run(sub, "recovery2", "none", run_dir, inputs, kill=False)
    readers["reader_after_recovery2"] = run_reader(sub, "reader_after_recovery2", run_dir)
    return {"seed": seed, "fault_res": fault_res, "rec1": rec1, "rec2": rec2,
            "readers": readers}


def run_f06(sub: str) -> int:
    return verdict_f06(sub, f06_runs(sub))


def _load_writer(cdir: Path, label: str) -> dict:
    res = read_json(cdir / f"{label}_writer" / "result.json")
    return {"rc": res["product_returncode"],
            "kill_record": res.get("kill_record"),
            "stderr": (cdir / f"{label}_writer" / "stderr.txt")
                      .read_text(encoding="utf-8"),
            "stdout": (cdir / f"{label}_writer" / "stdout.txt")
                      .read_text(encoding="utf-8")}


def verdict_f06(sub: str, r: dict | None = None) -> int:
    fault = F06_SUBS[sub]
    case = _f06_case(sub)
    cdir = case_dir(case)
    run_dir = cdir / "state"
    r = r or {}
    if not r:
        missing = [lbl for lbl in ("seed", "fault", "recovery1", "recovery2")
                   if not (cdir / f"{lbl}_writer" / "result.json").exists()]
        readers_missing = [lbl for lbl in
                           ("reader_after_seed_p0", "reader_after_fault",
                            "reader_after_recovery1", "reader_after_recovery2")
                           if not (cdir / f"{lbl}.json").exists()]
        if missing or readers_missing:
            msg = {"blocked": f"missing writers={missing} readers={readers_missing}"}
            verdict = {"cell": case, "sub": sub, **msg, "all_ok": False,
                       "decided_at": utc()}
            write_json(cdir / "verdict.json", verdict)
            print(json.dumps({"f06": sub, "BLOCKED": msg["blocked"]},
                             ensure_ascii=False))
            return 2
        r = {"seed": _load_writer(cdir, "seed"),
             "fault_res": _load_writer(cdir, "fault"),
             "rec1": _load_writer(cdir, "recovery1"),
             "rec2": _load_writer(cdir, "recovery2"),
             "readers": {lbl: read_json(cdir / f"{lbl}.json") for lbl in
                         ("reader_after_seed_p0", "reader_after_fault",
                          "reader_after_recovery1",
                          "reader_after_recovery2")}}
    seed = r["seed"]
    fault_res = r["fault_res"]
    rec1 = r["rec1"]
    rec2 = r["rec2"]
    readers = r["readers"]

    # hook trace aggregation (trigger counts)
    traces = {}
    for p in sorted(run_dir.glob("hook_trace_*.jsonl")):
        pts = []
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    pts.append(json.loads(line))
                except json.JSONDecodeError:
                    pts.append({"point": "<unparseable>"})
        traces[p.name] = pts
    write_json(cdir / "hook_traces.json", traces)

    seed_p0_sha = (readers["reader_after_seed_p0"].get("packages", {})
                   .get("p0", {}))
    rec2_p0 = readers["reader_after_recovery2"].get("packages", {}).get("p0", {})
    rows_after_seed = readers["reader_after_seed_p0"].get("chain", {}).get("rows")
    rows_after_rec2 = readers["reader_after_recovery2"].get("chain", {}).get("rows")

    def trace_count(pred) -> int:
        n = 0
        for pts in traces.values():
            for pt in pts:
                if pred(pt):
                    n += 1
        return n

    trigger = {}
    if sub == "f06a":
        trigger = {"location": "publication_registry.py:_append (err hook before orig)",
                   "count": trace_count(lambda p: p.get("point") == "err_raised"
                                         and p.get("op") == "append_registry"),
                   "marker": "I-07-D injected registry failure in writer stderr",
                   "marker_in_stderr": "I-07-D injected registry failure"
                                        in fault_res["stderr"]}
    elif sub == "f06b":
        trigger = {"location": "revenue_forecast.py:_atomic_write_text 2nd member "
                               "(err:replace role=output_markdown)",
                   "count": trace_count(lambda p: p.get("point") == "err_raised"
                                         and p.get("op") == "replace"
                                         and p.get("role") == "output_markdown"),
                   "marker": "I-07-D injected replace failure in writer stderr",
                   "marker_in_stderr": "I-07-D injected replace failure"
                                        in fault_res["stderr"]}
    else:
        barrier_pids = [b.stem.split("_", 1)[1]
                        for b in run_dir.glob("barrier_*.json")]
        fault_exit_records = [f"writer_exited_{p}.json" for p in barrier_pids
                              if (run_dir / f"writer_exited_{p}.json").exists()]
        trigger = {"location": "revenue_forecast.py:main return:before (kill)",
                   "count": trace_count(lambda p: p.get("point") == "return:before"),
                   "barriers": [p.name for p in run_dir.glob("barrier_*.json")],
                   "killed": bool(fault_res["kill_record"]
                                  and fault_res["kill_record"].get("killed")),
                   "kill_record": fault_res["kill_record"],
                   "fault_writer_exit_records": fault_exit_records,
                   "clean_run_exit_records": [
                       p.name for p in sorted(run_dir.glob("writer_exited_*.json"))
                       if p.name not in fault_exit_records]}

    fa = readers["reader_after_fault"]
    checks = {
        "seed_rc0": seed["rc"] == 0,
        "seed_p0_consumable": seed_p0_sha.get("consumable") is True,
        "fault_rc_expected": fault_res["rc"] == (4242 if sub == "f06c" else 2),
        "trigger_fired": (trigger.get("count", 0) >= 1) if sub != "f06c"
                         else (trigger["count"] >= 1 and trigger["killed"]
                               and trigger["fault_writer_exit_records"] == []),
        "fault_p0_consumable": fa.get("packages", {}).get("p0", {}).get("consumable") is True,
        "fault_chain_ok": fa.get("chain", {}).get("ok") is True,
        "fault_audit_clean": (fa.get("product_authority", {}).get("audit_problems") == []),
        "no_tmp_leftover": fa.get("tmp_files") == [],
        "rec1_rc0": rec1["rc"] == 0, "rec2_rc0": rec2["rc"] == 0,
        "rec2_p1_consumable": readers["reader_after_recovery2"]
                              .get("packages", {}).get("p1", {}).get("consumable") is True,
        "rec2_p0_intact": (rec2_p0.get("json_sha256") == seed_p0_sha.get("json_sha256")
                           and rec2_p0.get("md_sha256") == seed_p0_sha.get("md_sha256")),
        "rec2_audit_clean": (readers["reader_after_recovery2"]
                             .get("product_authority", {}).get("audit_problems") == []),
        "rec2_chain_ok": readers["reader_after_recovery2"]
                         .get("chain", {}).get("ok") is True,
        "history_not_deleted": (rows_after_rec2 is not None and rows_after_seed is not None
                                and rows_after_rec2 >= rows_after_seed),
    }
    if sub == "f06a":
        checks["fault_p1_absent"] = (
            fa.get("packages", {}).get("p1", {}).get("rows_for_input") == 0
            and fa.get("packages", {}).get("p1", {}).get("json_exists") is False
            and fa.get("packages", {}).get("p1", {}).get("md_exists") is False)
        checks["fault_p1_not_consumable"] = fa.get("packages", {}) \
            .get("p1", {}).get("consumable") is False
    elif sub == "f06b":
        p1 = fa.get("packages", {}).get("p1", {})
        checks["fault_p1_half_visible_not_consumable"] = (
            p1.get("rows_for_input") == 1 and p1.get("json_exists") is True
            and p1.get("md_exists") is False and p1.get("consumable") is False)
        checks["fault_is_registered_true"] = fa.get("product_authority", {}) \
            .get("is_registered_p1") is True
    else:
        checks["fault_p1_consumable_complete"] = fa.get("packages", {}) \
            .get("p1", {}).get("consumable") is True
        checks["no_writer_stdout_ack"] = fault_res["stdout"].strip() == ""

    prod_findings = []
    ap = fa.get("product_authority", {}).get("audit_problems") or []
    if ap:
        prod_findings.append({
            "id": "F-F06-audit",
            "class": "PRODUCT FINDING — cells stay RED (frozen expectation "
                     "audit_problems==0 not met; I-09-C F12 precedent: no "
                     "re-gating to green)",
            "finding": "publication_registry.audit() reports 'unregistered "
                       "claim' for EVERY result file while its own "
                       "is_registered(claim)=true in the same fresh reader "
                       "process. Root cause: scripts/publication_registry.py:229 "
                       "`claimed not in by_generation` tests a STRING against "
                       "dict keys that are TUPLES (typed L207, unpacked L216) — "
                       "membership can never match; intended check must be "
                       "anchor-level.",
            "audit_problems_raw": ap,
            "contradiction_measured": {
                "is_registered_p0": fa.get("product_authority", {}).get("is_registered_p0"),
                "is_registered_p1": fa.get("product_authority", {}).get("is_registered_p1"),
                "registry_path_match": fa.get("product_authority", {}).get("registry_path_match"),
                "chain_ok": fa.get("chain", {}).get("ok"),
                "p1_consumable_reader_view": fa.get("packages", {}).get("p1", {}).get("consumable"),
            },
            "disposition": "OPEN product defect routed to owner (publication "
                           "registry track); recorded, not hidden; matrix row "
                           "visibility/recovery expectations measured separately",
        })
    verdict = {"cell": case, "sub": sub, "fault": fault, "trigger": trigger,
               "checks": checks, "all_ok": all(checks.values()),
               "product_findings": prod_findings,
               "writer_rcs": {"seed": seed["rc"], "fault": fault_res["rc"],
                              "recovery1": rec1["rc"], "recovery2": rec2["rc"]},
               "registry_rows": {"after_seed": rows_after_seed,
                                 "after_rec2": rows_after_rec2},
               "readers": {k: {kk: v.get("packages", {}).get(kk)
                               for kk in ("p0", "p1")} | {"chain": v.get("chain"),
                                                          "authority": v.get("product_authority")}
                           for k, v in readers.items()},
               "decided_at": utc()}
    write_json(cdir / "verdict.json", verdict)
    print(json.dumps({"f06": sub, "all_ok": verdict["all_ok"],
                      "trigger_count": trigger.get("count"),
                      "failed_checks": [k for k, v in checks.items() if not v]},
                     ensure_ascii=False))
    return 0 if verdict["all_ok"] else 3


# ---------------------------------------------------------------- cells F01-F05
def f01_runs() -> None:
    case = "F01"
    sim = str(SIM_META / "CN-ZIJIN-2025.provider.json")
    run_entry(case, "run1_entry_fault", allow=True, fixture_log=True)
    run_direct(case, "run2_ff_fault", "ff")
    run_direct(case, "run3_client_fault", "client")
    run_entry(case, "run4_recovery_entry", allow=True, sim=sim)


def verdict_f01() -> int:
    case = "F01"
    checks = {}
    flog = []
    if FIXTURE_LOG.exists():
        flog = [json.loads(l) for l in FIXTURE_LOG.read_text(encoding="utf-8").splitlines()
                if l.strip()]
    fetches = [l for l in flog if l.get("action") == "fetch"]
    discos = [l for l in flog if l.get("action") == "discover"]

    # per-run window attribution for the frozen 1..3 fetch bound (oracle §3 F01):
    # run1's true window = argv.json started_at .. started_at + elapsed_seconds
    # (pre-fix runs of this cell recorded started_at AFTER the run; fall back to
    # recorded_after_run - elapsed, which is exact for sequential runs)
    a1 = read_json(case_dir(case) / "run1_entry_fault" / "argv.json")
    e1 = read_json(case_dir(case) / "run1_entry_fault" / "evidence.json")
    if a1.get("started_at"):
        t_start = datetime.fromisoformat(a1["started_at"]).timestamp()
        if (a1.get("started_at") == a1.get("recorded_after_run")
                or "recorded_after_run" not in a1):
            # legacy evidence: started_at was written AFTER the run
            t_start -= float(e1["elapsed_seconds"])
    else:
        t_start = (datetime.fromisoformat(a1["recorded_after_run"]).timestamp()
                   - float(e1["elapsed_seconds"]))
    t_end = t_start + float(e1["elapsed_seconds"]) + 1.0
    in_run1 = lambda l: t_start - 1.0 <= float(l.get("t", 0)) <= t_end  # noqa: E731
    fetches_r1 = [l for l in fetches if in_run1(l)]
    discos_r1 = [l for l in discos if in_run1(l)]

    def contains(path: Path, needle: str) -> bool:
        return path.is_file() and needle in path.read_text(encoding="utf-8")

    ev1 = None  # e1 loaded in the window block above
    e2 = read_json(case_dir(case) / "run2_ff_fault" / "evidence.json")
    e3 = read_json(case_dir(case) / "run3_client_fault" / "evidence.json")
    e4 = read_json(case_dir(case) / "run4_recovery_entry" / "evidence.json")
    ident = RC.IDENT[CELL_SAMPLE[case]]

    checks.update({
        "trigger_fetch_ge1_le3_per_run1": 1 <= len(fetches_r1) <= 3,
        "trigger_discover_ge1_run1": len(discos_r1) >= 1,
        "trigger_fetch_ge1_total": len(fetches) >= 1,
        "fixture_window_includes_run1": bool(fetches_r1) or bool(discos_r1),
        "trigger_adapter_site_hit": (
            e1["counter_delta"].get("provider", 0) >= 1
            and e2["counter_delta"].get("provider", 0) >= 1
            and e3["counter_delta"].get("provider", 0) >= 1),
        "entry_rc3": e1["product_returncode"] == 3,
        "ff_rc2": e2["product_returncode"] == 2,
        "client_rc2": e3["product_returncode"] == 2,
        "no_consumable_stdout_fault": not e1["stdout_has_consumable_record"],
        "no_fake_raw_fault": (
            e1["raw_sha_before"] is None and e1["raw_sha_after"] is None
            and e1["catalog_count_delta"].get("documents", 0) == 0
            and e1["catalog_count_delta"].get("locations", 0) == 0
            and not e1["stdout_has_consumable_record"]),
        "trigger_calls_without_download": (
            e1["counter_delta"].get("provider", 0) >= 1
            and e1["raw_sha_after"] is None),
        "hop1_marker": contains(case_dir(case) / "run1_entry_fault" / "stderr.txt",
                                "http_403"),
        "hop3_marker": contains(case_dir(case) / "run2_ff_fault" / "stdout.txt",
                                "http_403"),
        "hop4_marker": contains(case_dir(case) / "run3_client_fault" / "stderr.txt",
                                "http_403"),
        "hop5_marker": contains(case_dir(case) / "run1_entry_fault" / "stderr.txt",
                                "http_403"),
        "hop4_retryable_field": contains(case_dir(case) / "run3_client_fault" /
                                         "stderr.txt", "retryable"),
        "recovery_downloaded": (e4["counter_delta"].get("provider", 0) >= 1
                                and e4["raw_sha_after"] is not None),
        "recovery_raw_hash_ok": e4["raw_sha_after"] == ident["sha"],
        "recovery_registered": e4["catalog_count_delta"].get("documents", 0) == 1,
        "recovery_not_pseudo_success": e4["product_returncode"] == 3
                                       and not e4["stdout_has_consumable_record"],
    })
    verdict = {"cell": case, "point": "(a) provider返回 / F01",
               "trigger": {"location": "adapter_process.py:155-178 via cell config "
                                       "fixture command (fixture_403_adapter.py)",
                           "fetch_count_total": len(fetches),
                           "fetch_count_run1_window": len(fetches_r1),
                           "count": len(fetches_r1),
                           "discover_count": len(discos),
                           "discover_count_run1_window": len(discos_r1),
                           "spy_provider_delta": {lbl: read_json(
                               case_dir(case) / lbl / "evidence.json"
                           )["counter_delta"] for lbl in
                               ("run1_entry_fault", "run2_ff_fault", "run3_client_fault",
                                "run4_recovery_entry")},
                           "fixture_log": str(FIXTURE_LOG)},
               "checks": checks, "all_ok": all(checks.values()),
               "raw_rcs": {"entry_fault": e1["product_returncode"],
                           "ff_fault": e2["product_returncode"],
                           "client_fault": e3["product_returncode"],
                           "entry_recovery": e4["product_returncode"]},
               "decided_at": utc()}
    write_json(case_dir(case) / "verdict.json", verdict)
    print(json.dumps({"cell": case, "all_ok": verdict["all_ok"],
                      "fetches_total": len(fetches),
                      "fetches_run1": len(fetches_r1),
                      "failed": [k for k, v in checks.items() if not v]},
                     ensure_ascii=False))
    return 0 if verdict["all_ok"] else 3


def run_f01() -> int:
    f01_runs()
    return verdict_f01()


def f02_runs() -> dict:
    case = "F02"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    raw_path = cwroot / ident["raw"].replace("\\", os.sep)

    proc = start_holder(case, raw_path, "f02")
    fault = run_cli(case, "scan1_fault", "scan", dump_scan_runs=True)
    hold = stop_holder(case, "f02", proc)

    nohandle = run_entry(case, "entry_nohandle", allow=False)
    rec = run_cli(case, "scan2_recovery", "scan", dump_scan_runs=True)
    after = run_entry(case, "entry_after_recovery", allow=False)
    return {"fault": fault, "hold": hold, "nohandle": nohandle,
            "rec": rec, "after": after, "raw_path": str(raw_path)}


def run_f02() -> int:
    return verdict_f02(f02_runs())


def verdict_f02(r: dict | None = None) -> int:
    case = "F02"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    r = r or {}
    raw_path = Path(r["raw_path"]) if r.get("raw_path") else (
        cwroot / ident["raw"].replace("\\", os.sep))
    fault = r.get("fault") or read_json(
        case_dir(case) / "scan1_fault" / "evidence.json")
    nohandle = r.get("nohandle") or read_json(
        case_dir(case) / "entry_nohandle" / "evidence.json")
    rec = r.get("rec") or read_json(
        case_dir(case) / "scan2_recovery" / "evidence.json")
    after = r.get("after") or read_json(
        case_dir(case) / "entry_after_recovery" / "evidence.json")
    hold = r.get("hold") or read_json(
        case_dir(case) / "hold_record_f02.json")["hold"]
    checks = {}

    sr = read_json(case_dir(case) / "scan1_fault" / "scan_runs.json")
    statuses1 = [r["status"] for r in sr]
    err_details = None
    import re
    stdout1 = (case_dir(case) / "scan1_fault" / "stdout.txt").read_text(encoding="utf-8")
    for line in stdout1.splitlines():
        line = line.strip()
        if line.startswith("{") and "errors" in line:
            try:
                doc = json.loads(line)
                err_details = doc.get("error_details") or doc.get("errors")
            except json.JSONDecodeError:
                pass
    hold_ok = hold.get("ok") is True
    sr2 = read_json(case_dir(case) / "scan2_recovery" / "scan_runs.json")
    statuses2 = [r["status"] for r in sr2]
    nohandle_err = ((case_dir(case) / "entry_nohandle" / "stderr.txt")
                    .read_text(encoding="utf-8"))
    after_err = ((case_dir(case) / "entry_after_recovery" / "stderr.txt")
                 .read_text(encoding="utf-8"))
    gating = {
        "trigger_scan_status_cwe": "completed_with_errors" in statuses1,
        "trigger_count_ge1": isinstance(err_details, (list, int))
                             and (len(err_details) >= 1 if isinstance(err_details, list)
                                  else err_details >= 1),
        "trigger_cause_text_recorded": "PermissionError" in stdout1,
        "fault_scan_rc0": fault["product_returncode"] == 0,
        "hold_window_valid": hold_ok,
        "raw_preserved": sha256_file(raw_path) == ident["sha"],
        "report_not_claiming_clean": "completed_with_errors" in statuses1,
        "nohandle_refusal": (nohandle["product_returncode"] == 3
                             and not nohandle["stdout_has_consumable_record"]
                             and "not_found" in nohandle_err
                             and "not reusable" in nohandle_err),
        "no_consumable_handle_at_fault": not nohandle["stdout_has_consumable_record"],
        "nohandle_zero_download": nohandle["counter_delta"].get("provider", 0) == 0,
        "recovery_scan_rc0": rec["product_returncode"] == 0,
        "recovery_scan_clean": statuses2[-1] == "completed",
        "recovery_usable": (after["product_returncode"] == 3
                            and "prompt injection not reviewed" in after_err),
        "recovery_no_download": rec["counter_delta"].get("provider", 0) == 0
                                and fault["counter_delta"].get("provider", 0) == 0,
        "recovery_raw_unchanged": rec["raw_unchanged"] is True,
    }
    # oracle §2 F02 mechanism prediction (frozen as a hand-reasoned PREDICTION,
    # oracle.md own rule: a wrong prediction is a finding about the model, never
    # a rewrite of the oracle).  Measured miss is recorded, not hidden, and does
    # not gate the row-level verdict (the row's binding expectation
    # 不返回可消费可handle is proven by the not_found refusal above).
    model_predictions = {
        "oracle_literal_zero_registration_rows_at_fault":
            fault["catalog_count_delta"].get("documents", 0) == 0
            and fault["catalog_count_delta"].get("locations", 0) == 0,
    }
    prediction_divergences = [k for k, v in model_predictions.items() if not v]
    checks = gating
    verdict = {"cell": case, "point": "(c) scan错误 / F02",
               "trigger": {"location": "scanner.py:964-976 -> scanner.py:1209",
                           "status": statuses1, "error_details": err_details,
                           "hold": hold,
                           "count": len(err_details) if isinstance(err_details, list)
                                    else (err_details or 0)},
               "fault_catalog_delta": fault["catalog_count_delta"],
               "checks": checks, "all_ok": all(checks.values()),
               "model_prediction_checks": model_predictions,
               "prediction_divergences": prediction_divergences,
               "prediction_divergence_note":
                   "oracle §2 mechanism prediction 'documents/locations delta 0 at "
                   "fault' MISSED: the product enumerates the sidecar and writes "
                   "rows while the raw is unreadable (documents+1 sources+1 "
                   "locations+2), BUT the source is non-reusable -> entry refusal "
                   "not_found (no consumable handle, matrix row satisfied). "
                   "Recorded per oracle's rule: a wrong prediction is a finding "
                   "about the model, never a rewrite of the oracle.",
               "raw_rcs": {"scan_fault": fault["product_returncode"],
                           "entry_nohandle": nohandle["product_returncode"],
                           "scan_recovery": rec["product_returncode"],
                           "entry_after_recovery": after["product_returncode"]},
               "decided_at": utc()}
    write_json(case_dir(case) / "verdict.json", verdict)
    print(json.dumps({"cell": case, "all_ok": verdict["all_ok"],
                      "failed": [k for k, v in checks.items() if not v]},
                     ensure_ascii=False))
    return 0 if verdict["all_ok"] else 3


def f03_runs() -> dict:
    case = "F03"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    raw_path = cwroot / ident["raw"].replace("\\", os.sep)

    lock = start_lock(case, 75.0)
    time.sleep(2.0)
    t_scan_start = time.time()
    fault = run_cli(case, "scan1_fault", "scan", dump_scan_runs=True)
    t_scan_end = time.time()
    hold = wait_lock_released(case, lock)
    rec = run_cli(case, "scan2_recovery", "scan", dump_scan_runs=True)
    return {"fault": fault, "hold": hold, "rec": rec,
            "t_scan_start": t_scan_start, "t_scan_end": t_scan_end,
            "raw_path": str(raw_path)}


def run_f03() -> int:
    return verdict_f03(f03_runs())


def verdict_f03(r: dict | None = None) -> int:
    case = "F03"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    r = r or {}
    raw_path = Path(r["raw_path"]) if r.get("raw_path") else (
        cwroot / ident["raw"].replace("\\", os.sep))
    fault = r.get("fault") or read_json(
        case_dir(case) / "scan1_fault" / "evidence.json")
    rec = r.get("rec") or read_json(
        case_dir(case) / "scan2_recovery" / "evidence.json")
    hold = r.get("hold") or read_json(case_dir(case) / "lock" / "hold.json")
    t_scan_start = r.get("t_scan_start")
    t_scan_end = r.get("t_scan_end")
    if t_scan_start is None:
        a = read_json(case_dir(case) / "scan1_fault" / "argv.json")
        t0 = datetime.fromisoformat(a["started_at"]).timestamp()
        if "recorded_after_run" not in a:
            t0 -= float(a.get("elapsed_seconds") or fault.get("elapsed_seconds", 0))
        t_scan_start = t0
        t_scan_end = t0 + float(fault.get("elapsed_seconds", 0))
    checks = {}

    err_doc = None
    for line in ((case_dir(case) / "scan1_fault" / "stderr.txt")
                 .read_text(encoding="utf-8")).splitlines():
        if line.strip().startswith("{"):
            try:
                err_doc = json.loads(line)
            except json.JSONDecodeError:
                pass
    overlap = (hold.get("locked_at") and hold.get("released")
               and hold["locked_at"] < datetime.fromtimestamp(
                   t_scan_start, timezone.utc).isoformat()
               and hold["released"] > datetime.fromtimestamp(
                   t_scan_end, timezone.utc).isoformat())
    checks.update({
        "trigger_rc1": fault["product_returncode"] == 1,
        "trigger_lock_wait_elapsed_ge25": fault["elapsed_seconds"] >= 25.0,
        "trigger_error_catalog_busy": bool(err_doc)
                                       and err_doc.get("error_type") == "catalog_busy"
                                       and err_doc.get("retryable") is True
                                       and "database is locked" in str(err_doc.get("error")),
        "lock_held_across_scan": bool(hold.get("ok")) and bool(overlap),
        "no_partial_write_at_fault": fault["catalog_count_delta"] == {},
        "fault_stdout_empty": ((case_dir(case) / "scan1_fault" / "stdout.txt")
                               .read_text(encoding="utf-8")).strip() == "",
        "raw_preserved": sha256_file(raw_path) == ident["sha"],
        "recovery_scan_rc0": rec["product_returncode"] == 0,
        "recovery_registered": rec["catalog_count_delta"].get("documents", 0) == 1
                               and rec["catalog_count_delta"].get("locations", 0) >= 1,
        "recovery_no_download": rec["counter_delta"].get("provider", 0) == 0
                                and fault["counter_delta"].get("provider", 0) == 0,
        "recovery_raw_unchanged": rec["raw_unchanged"] is True,
    })
    verdict = {"cell": case, "point": "(d) DB事务内锁等待 / F03",
               "trigger": {"location": "store.py BEGIN IMMEDIATE wait "
                                       "(busy_timeout=30000) -> error_taxonomy catalog_busy",
                           "lock_hold": hold,
                           "scan_elapsed": fault["elapsed_seconds"],
                           "scan_window_utc": [t_scan_start, t_scan_end],
                           "overlap_ok": bool(overlap), "error_doc": err_doc,
                           "count": (1 if err_doc and err_doc.get("error_type")
                                     == "catalog_busy" else 0)},
               "checks": checks, "all_ok": all(checks.values()),
               "raw_rcs": {"scan_fault": fault["product_returncode"],
                           "scan_recovery": rec["product_returncode"]},
               "decided_at": utc()}
    write_json(case_dir(case) / "verdict.json", verdict)
    print(json.dumps({"cell": case, "all_ok": verdict["all_ok"],
                      "failed": [k for k, v in checks.items() if not v]},
                     ensure_ascii=False))
    return 0 if verdict["all_ok"] else 3


def f04_runs() -> dict:
    case = "F04"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    raw_path = cwroot / ident["raw"].replace("\\", os.sep)
    sim = str(SIM_META / "HK-XIAOMI-2025.provider.json")

    fault = run_entry(case, "run1_entry_fault", allow=True, sim=sim,
                      fault="kill_before_scan", kill=True,
                      kill_path=str(CASES / case))
    rec = run_cli(case, "scan2_recovery", "scan", dump_scan_runs=True)
    after = run_entry(case, "entry_after_recovery", allow=False)
    return {"fault": fault, "rec": rec, "after": after,
            "raw_path": str(raw_path)}


def find_committed_raw(cwroot: Path) -> Path | None:
    """F04: after a canonical import the product's filename may differ from the
    manifest name (known I-07-B open item); locate the single committed PDF."""
    comp = cwroot / "companies"
    if not comp.is_dir():
        return None
    pdfs = [p for p in comp.rglob("*.pdf") if p.is_file()]
    return pdfs[0] if len(pdfs) == 1 else (pdfs[0] if pdfs else None)


def run_f04() -> int:
    return verdict_f04(f04_runs())


def verdict_f04(r: dict | None = None) -> int:
    case = "F04"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    r = r or {}
    raw_path = Path(r["raw_path"]) if r.get("raw_path") else (
        cwroot / ident["raw"].replace("\\", os.sep))
    fault = r.get("fault") or read_json(
        case_dir(case) / "run1_entry_fault" / "evidence.json")
    rec = r.get("rec") or read_json(
        case_dir(case) / "scan2_recovery" / "evidence.json")
    after = r.get("after") or read_json(
        case_dir(case) / "entry_after_recovery" / "evidence.json")
    checks = {}

    k = fault["kill_record"] or {}
    killed = k.get("killed") or {}
    first = next(iter(killed.values()), {})
    stderr1 = ((case_dir(case) / "run1_entry_fault" / "stderr.txt")
               .read_text(encoding="utf-8"))
    actual_raw = find_committed_raw(cwroot)
    provenance = (actual_raw.parent / (actual_raw.name + ".source.json")
                  if actual_raw else None)
    checks.update({
        "trigger_barrier_and_kill": len(killed) == 1 and first.get("checks", {})
                                     .get("alive_after") is False,
        "kill_gate_path_ok": first.get("checks", {}).get("manifest_path_in_argv") is True
                             and first.get("checks", {}).get("manifest_path_in_cwd") is True,
        "released_marker_absent": first.get("released_marker_present") is False,
        "product_sees_kill_rc4242": "4242" in stderr1,
        "entry_rc3": fault["product_returncode"] == 3,
        "no_consumable_stdout": not fault["stdout_has_consumable_record"],
        "raw_committed_before_kill": (actual_raw is not None
                                      and sha256_file(actual_raw) == ident["sha"]),
        "provenance_committed": provenance is not None and provenance.is_file(),
        "no_registration_at_fault": fault["catalog_count_delta"] == {},
        "fault_download_happened": fault["counter_delta"].get("provider", 0) >= 1,
        "recovery_scan_rc0": rec["product_returncode"] == 0,
        "recovery_registered": rec["catalog_count_delta"].get("documents", 0) == 1
                               and rec["catalog_count_delta"].get("locations", 0) >= 1,
        "recovery_no_download": rec["counter_delta"].get("provider", 0) == 0,
        "raw_intact_after_recovery": (actual_raw is not None
                                      and sha256_file(actual_raw) == ident["sha"]),
        "after_entry_usable_no_dl": after["product_returncode"] == 3
                                    and after["counter_delta"].get("provider", 0) == 0,
    })
    verdict = {"cell": case, "point": "(b) raw提交后scan前 / F04",
               "trigger": {"location": "canonical_writer.py:185 call boundary "
                                       "(after raw commit :181-184, before scan body)",
                           "kill_record": k, "count": len(killed),
                           "committed_raw_path": str(actual_raw) if actual_raw else None,
                           "filename_note": "canonical filename may differ from the "
                                            "manifest name (I-07-B open item); content "
                                            "sha256 asserted against the manifest value"},
               "checks": checks, "all_ok": all(checks.values()),
               "raw_rcs": {"entry_fault": fault["product_returncode"],
                           "scan_recovery": rec["product_returncode"],
                           "entry_after": after["product_returncode"]},
               "decided_at": utc()}
    write_json(case_dir(case) / "verdict.json", verdict)
    print(json.dumps({"cell": case, "all_ok": verdict["all_ok"],
                      "killed": len(killed),
                      "failed": [k2 for k2, v in checks.items() if not v]},
                     ensure_ascii=False))
    return 0 if verdict["all_ok"] else 3


def f05_runs() -> dict:
    case = "F05"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    norm_rel = (".source_catalog/derived/01/"
                f"{ident['sha']}/normalized.md")
    norm_path = cwroot / norm_rel

    setup_scan = run_cli(case, "scan0_setup", "scan", dump_scan_runs=True)
    seed = seed_f05()
    dump_cell_state(case, "before_fault")
    if not seed.get("ok"):
        return {"blocked": seed, "setup_scan": setup_scan}

    holder = start_holder(case, norm_path, "f05")
    fault = run_cli(case, "prod_sum_fault", "summarize")
    hold = stop_holder(case, "f05", holder)
    dump_cell_state(case, "after_fault")

    rec = run_cli(case, "prod_sum_recovery", "summarize")
    dump_cell_state(case, "after_recovery")
    return {"setup_scan": setup_scan, "seed": seed, "fault": fault,
            "hold": hold, "rec": rec}


def run_f05() -> int:
    return verdict_f05(f05_runs())


def verdict_f05(r: dict | None = None) -> int:
    case = "F05"
    cwroot = cwroot_of(case)
    ident = RC.IDENT[CELL_SAMPLE[case]]
    r = r or {}
    if r.get("blocked") is not None or (not r and not
                                        (case_dir(case) / "f05_seed.json").exists()):
        payload = r.get("blocked") or {"blocked": "f05_seed.json missing"}
        verdict = {"cell": case, "point": "(e) producer执行 / F05",
                   "blocked": payload, "all_ok": False, "decided_at": utc()}
        write_json(case_dir(case) / "verdict.json", verdict)
        print(json.dumps({"cell": case, "BLOCKED": payload.get("blocked")
                          if isinstance(payload, dict) else payload},
                         ensure_ascii=False))
        return 2
    checks = {}
    setup_scan = r.get("setup_scan") or read_json(
        case_dir(case) / "scan0_setup" / "evidence.json")
    seed = r.get("seed") or read_json(case_dir(case) / "f05_seed.json")
    fault = r.get("fault") or read_json(
        case_dir(case) / "prod_sum_fault" / "evidence.json")
    rec = r.get("rec") or read_json(
        case_dir(case) / "prod_sum_recovery" / "evidence.json")
    hold = r.get("hold") or read_json(
        case_dir(case) / "hold_record_f05.json")["hold"]

    def report_counts(ev: dict) -> dict:
        txt = (case_dir(case) / ev["label"] / "stdout.txt").read_text(encoding="utf-8")
        for line in txt.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    doc = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if any(k in doc for k in ("failed", "completed")):
                    return doc
        return {}

    rep_f = report_counts(fault)
    rep_r = report_counts(rec)
    st_f = read_json(case_dir(case) / "state_after_fault.json")
    st_r = read_json(case_dir(case) / "state_after_recovery.json")

    def roles(st):
        return sorted(a["artifact_role"] for a in st["artifacts"])

    norm_f = [a for a in st_f["artifacts"] if a["artifact_role"] == "normalized"]
    norm_r = [a for a in st_r["artifacts"] if a["artifact_role"] == "normalized"]
    sum_r = [a for a in st_r["artifacts"] if a["artifact_role"] == "summary"]

    fault_failed = rep_f.get("failed", None)
    rec_completed = rep_r.get("completed", None)
    cause_persisted = ("PermissionError" in
                       (case_dir(case) / "prod_sum_fault" / "stdout.txt")
                       .read_text(encoding="utf-8")
                       + (case_dir(case) / "prod_sum_fault" / "stderr.txt")
                       .read_text(encoding="utf-8")) or any(
        "PermissionError" in json.dumps(a, default=str) for a in st_f["artifacts"])

    checks.update({
        "setup_scan_rc0": setup_scan["product_returncode"] == 0,
        "seed_ok": seed.get("ok") is True,
        "seed_summary_absent": seed.get("summary_absent_by_construction") is True,
        "trigger_fault_failed_eq1": fault_failed == 1,
        "trigger_fault_rc0": fault["product_returncode"] == 0,
        "trigger_hold_window": hold.get("ok") is True,
        "trigger_summarize_called": fault["counter_delta"].get("producer", 0) >= 1,
        "no_summary_row_at_fault": roles(st_f) == ["normalized"],
        "no_summary_file_at_fault": not any(d["rel"].endswith("summary.md")
                                            for d in st_f["derived_files"]),
        "normalized_intact_at_fault": (
            len(norm_f) == 1
            and norm_f[0]["content_sha256"] == seed["production_row"]["content_sha256"]),
        "report_not_claiming_success": fault_failed == 1,
        "recovery_completed_eq1": rec_completed == 1,
        "recovery_failed_eq0": rep_r.get("failed") == 0,
        "recovery_rc0": rec["product_returncode"] == 0,
        "summary_plus1_only": len(sum_r) == 1 and len(norm_r) == 1,
        "normalized_not_reproduced": norm_f == norm_r,
        "recovery_no_download": rec["counter_delta"].get("provider", 0) == 0,
        "single_variable_lock": hold.get("ok") is True,
    })
    verdict = {"cell": case, "point": "(e) producer执行 / F05",
               "trigger": {"location": "summarizer.py:163-170 "
                                       "(read_text of normalized -> OSError -> failed+=1)",
                           "count": 1 if fault_failed == 1 else 0,
                           "hold": hold,
                           "fault_report": rep_f, "recovery_report": rep_r},
               "cause_survival": {
                   "cause_persisted_by_product": cause_persisted,
                   "verdict": "PASS" if cause_persisted else
                              "FAIL — finding F-F05-cause: summarizer.py:168 swallows "
                              "the OSError (failed counter only, no cause text recorded); "
                              "trigger proof rests on hold window + single-variable control",
               },
               "checks": checks, "all_ok": all(checks.values()),
               "raw_rcs": {"scan0": setup_scan["product_returncode"],
                           "summarize_fault": fault["product_returncode"],
                           "summarize_recovery": rec["product_returncode"]},
               "decided_at": utc()}
    write_json(case_dir(case) / "verdict.json", verdict)
    print(json.dumps({"cell": case, "all_ok": verdict["all_ok"],
                      "cause_survival": verdict["cause_survival"]["verdict"][:30],
                      "failed": [k for k, v in checks.items() if not v]},
                     ensure_ascii=False))
    return 0 if verdict["all_ok"] else 3


# ---------------------------------------------------------------- build/probes
def cmd_build() -> int:
    setup_paths()
    out = {}
    out["iso_rf"] = build_iso_rf()
    specs = [("F01", "CN-ZIJIN-2025", "state3"),
             ("F02", "HK-XIAOMI-2025", "state2"),
             ("F03", "HK-XIAOMI-2025", "state2"),
             ("F04", "HK-XIAOMI-2025", "state3"),
             ("F05", "CN-ZIJIN-2025", "state2")]
    for case, sample, state in specs:
        benv = dict(os.environ)
        benv["PYTHONPATH"] = str(CW / "src")
        benv["PYTHONUTF8"] = "1"
        benv["PYTHONIOENCODING"] = "utf-8"
        benv["PYTHONDONTWRITEBYTECODE"] = "1"
        cp = subprocess.run([sys.executable, str(ATT / "harness" / "build_iso.py"),
                             "case", case, sample, state],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=benv)
        out[case] = {"rc": cp.returncode, "stdout": (cp.stdout or "").strip()[-500:],
                     "stderr": (cp.stderr or "").strip()[-500:]}
        if cp.returncode != 0:
            print(json.dumps(out, ensure_ascii=False))
            return 1
    senv = dict(os.environ)
    senv["PYTHONUTF8"] = "1"
    senv["PYTHONIOENCODING"] = "utf-8"
    sc = subprocess.run([sys.executable, str(ATT / "harness" / "scaffold_adapters.py")],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", env=senv)
    out["scaffold"] = {"rc": sc.returncode, "stdout": sc.stdout.strip()[-500:]}
    out["f01_config"] = f01_edit_config()
    write_json(ATT / "evidence" / "build.json", out)
    print(json.dumps({"build": "ok", "cases": list(specs),
                      "scaffold_rc": sc.returncode}, ensure_ascii=False))
    return 0 if sc.returncode == 0 else 1


def build_iso_rf() -> dict:
    dst = ISO_RF
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("scripts", "config", "references", "tests"):
        shutil.copytree(RF / name, dst / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in ("CHANGELOG.md", "SKILL.md", ".gitignore"):
        if (RF / name).is_file():
            shutil.copy2(RF / name, dst / name)
    n = sum(1 for _ in dst.rglob("*") if _.is_file())
    return {"path": str(dst), "files": n,
            "source": "read-only copy of current RF (scripts/config/references/tests)",
            "product_edits": 0}


def cmd_wprobe() -> int:
    return RC.wprobe(str(ATT / "evidence" / "wprobe_tmp"))


def cmd_snap(mode: str) -> int:
    cp = subprocess.run([sys.executable, str(ATT / "harness" / "snapshot.py"), mode],
                        capture_output=True, text=True, encoding="utf-8")
    print((cp.stdout or "") + (cp.stderr or ""))
    return cp.returncode


def cmd_verdicts() -> int:
    cells = ["F01", "F02", "F03", "F04", "F05", "F06A", "F06B", "F06C"]
    out = {"card": "I-07-D", "attempt": "a20260923-01", "generated": utc(),
           "cells": {}, "trigger_counts": {}, "all_ok": True,
           "blocked": []}
    for c in cells:
        p = case_dir(c) / "verdict.json"
        if not p.exists():
            out["cells"][c] = "MISSING verdict.json"
            out["all_ok"] = False
            continue
        v = read_json(p)
        out["cells"][c] = {"all_ok": v.get("all_ok"),
                           "trigger": v.get("trigger", {}).get("count",
                                   v.get("trigger", {}).get("fetch_count", None)),
                           "failed_checks": [k for k, val in
                                             (v.get("checks") or {}).items()
                                             if not val]}
        if v.get("blocked"):
            out["blocked"].append(c)
        out["trigger_counts"][c] = out["cells"][c]["trigger"]
        if not v.get("all_ok"):
            out["all_ok"] = False
        if v.get("cause_survival"):
            out["cells"][c]["cause_survival"] = v["cause_survival"]["verdict"]
    write_json(ATT / "evidence" / "verdicts.json", out)
    print(json.dumps({"all_ok": out["all_ok"], "blocked": out["blocked"],
                      "trigger_counts": out["trigger_counts"]}, ensure_ascii=False))
    return 0 if out["all_ok"] else 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "wprobe", "snap", "f01", "f01v",
                                    "f02", "f02v", "f03", "f03v", "f04", "f04v",
                                    "f05", "f05v", "f06a", "f06b", "f06c",
                                    "f06av", "f06bv", "f06cv", "verdicts"])
    ap.add_argument("arg", nargs="?", default=None)
    ns = ap.parse_args()
    return {"build": cmd_build, "wprobe": cmd_wprobe,
            "snap": lambda: cmd_snap(ns.arg or "before"),
            "f01": run_f01, "f01v": verdict_f01,
            "f02": run_f02, "f02v": verdict_f02,
            "f03": run_f03, "f03v": verdict_f03,
            "f04": run_f04, "f04v": verdict_f04,
            "f05": run_f05, "f05v": verdict_f05,
            "f06a": lambda: run_f06("f06a"), "f06b": lambda: run_f06("f06b"),
            "f06c": lambda: run_f06("f06c"),
            "f06av": lambda: verdict_f06("f06a"),
            "f06bv": lambda: verdict_f06("f06b"),
            "f06cv": lambda: verdict_f06("f06c"),
            "verdicts": cmd_verdicts}[ns.cmd]()


if __name__ == "__main__":
    sys.exit(main())
