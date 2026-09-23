"""FIX-W06-GAPS P6 scenario runner: concurrent receipt writes (red/green).

Adapted from OPEN5-DOUBT-PROBE scripts/p6_concurrent_receipt_writes.py
(Phases A / A2 / B kept) with the oracle P6-A/P6-B assertion set:
  Phase A : 8 concurrent single writes on one document_id —
            every outcome is either an acknowledged CAS-won write or a DEFINED
            rejection (count conservation, zero silent drops) AND read-back
            proves every acknowledged write (audit trail); under default
            timeout the writes succeed with zero lock exceptions (red line).
  Phase A2: connect timeout=0 — contention errors surface as
            PromptInjectionReviewError "store busy/lock timeout: ..." (never a
            bare sqlite3.OperationalError).
  Phase B : interleaved writers + readers — zero tearing / zero reader
            exceptions (red line, both phases).

Usage: python -X utf8 -B s_p6_concurrent.py --pkg-dir <dir with prompt_injection.py> --out <evidence.txt>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
from pathlib import Path

LOG: list[str] = []
RESULTS: dict = {}
PY = sys.executable


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


WRITER = r'''
import hashlib, importlib.util, inspect, json, os, sqlite3, sys, time
from pathlib import Path
tmp = Path(os.environ["GAPS_P6_TMP"])
sys.path.insert(0, str(tmp))
import pi_pkg.prompt_injection as mod
mode, owner, doc = sys.argv[1], sys.argv[2], sys.argv[3]
timeout = float(os.environ.get("GAPS_P6_TIMEOUT", "5.0"))
go = tmp / "go.flag"
(tmp / f"ready.{owner}").write_text("1", encoding="utf-8")
while not go.exists():
    time.sleep(0.001)
payload = f"scan evidence payload for {owner}"
evidence_sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
out = {"owner": owner, "mode": mode, "writes": 0, "errors": [], "error_types": []}
try:
    c = sqlite3.connect(str(tmp / "catalog.sqlite3"), timeout=timeout)
    try:
        kwargs = dict(
            status="not_detected", reviewer=owner, evidence_sha256=evidence_sha,
            now="2026-09-22T00:00:00Z",
            source_sha256=hashlib.sha256(("src" + owner).encode()).hexdigest(),
            policy_hash=hashlib.sha256(("pol" + owner).encode()).hexdigest(),
            evidence_payload=payload,
        )
        sig = inspect.signature(mod.record_prompt_injection_review)
        kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        mod.record_prompt_injection_review(c, doc, **kwargs)
        c.commit()
        out["writes"] += 1
        out["evidence_sha256"] = evidence_sha
    except BaseException as exc:
        out["errors"].append(f"{type(exc).__name__}: {exc}")
        out["error_types"].append(type(exc).__name__)
        out["evidence_sha256"] = evidence_sha
    finally:
        c.close()
except BaseException as exc:
    out["errors"].append(f"{type(exc).__name__}: {exc}")
    out["error_types"].append(type(exc).__name__)
print(json.dumps(out, ensure_ascii=False))
'''


READER = r'''
import importlib.util, json, os, sqlite3, sys, time
from pathlib import Path
tmp = Path(os.environ["GAPS_P6_TMP"])
sys.path.insert(0, str(tmp))
import pi_pkg.prompt_injection as mod
owner, doc = sys.argv[1], sys.argv[2]
stop = tmp / "stop.flag"
class Shim:
    def fetchone(self, sql, params=()):
        c = sqlite3.connect(str(tmp / "catalog.sqlite3"), timeout=5.0)
        try:
            return c.execute(sql, params).fetchone()
        finally:
            c.close()
out = {"owner": owner, "reads": 0, "none_results": 0, "receipt_results": 0, "errors": []}
while not stop.exists():
    try:
        r = mod.read_prompt_injection_review(Shim(), doc)
        out["reads"] += 1
        if r is None:
            out["none_results"] += 1
        else:
            out["receipt_results"] += 1
            if not isinstance(r, dict) or r.get("schema_version") != "1.0":
                out["errors"].append(f"torn read: {r!r}")
    except BaseException as exc:
        out["errors"].append(f"{type(exc).__name__}: {exc}")
print(json.dumps(out, ensure_ascii=False))
'''


def spawn(args: list[str], script: str, argv: list[str], tmp: Path) -> subprocess.Popen:
    return subprocess.Popen([args, "-X", "utf8", "-B", "-c", script, *argv],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=dict(os.environ, GAPS_P6_TMP=str(tmp)))


def collect(procs: list[subprocess.Popen]) -> list[dict]:
    outs = []
    for p in procs:
        stdout, stderr = p.communicate(timeout=60)
        try:
            parsed = json.loads(stdout.decode("utf-8", "replace").strip().splitlines()[-1])
        except Exception:
            parsed = {"raw_stdout": stdout.decode("utf-8", "replace"),
                      "raw_stderr": stderr.decode("utf-8", "replace")}
        parsed["rc"] = p.returncode
        outs.append(parsed)
    return outs


def fresh_db(tmp: Path) -> None:
    db = tmp / "catalog.sqlite3"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(str(db))
    con.execute("CREATE TABLE documents (document_id TEXT PRIMARY KEY, metadata_json TEXT)")
    for name in ("doc-a", "doc-race", "doc-mix"):
        con.execute("INSERT INTO documents VALUES(?,?)", (name, "{}"))
    con.commit()
    con.close()


def go_sync(tmp: Path, owners: list[str]) -> None:
    for p in tmp.glob("ready.*"):
        p.unlink()
    go = tmp / "go.flag"
    if go.exists():
        go.unlink()
    deadline = time.time() + 10
    while time.time() < deadline and not all(
            (tmp / f"ready.{o}").exists() for o in owners):
        time.sleep(0.001)
    time.sleep(0.05)
    go.write_text("go", encoding="utf-8")


def final_state(tmp: Path, doc: str) -> dict:
    con = sqlite3.connect(str(tmp / "catalog.sqlite3"))
    row = con.execute(
        "SELECT metadata_json FROM documents WHERE document_id=?", (doc,)).fetchone()
    con.close()
    meta = json.loads(row[0] or "{}")
    audit = meta.get("prompt_injection_review_audit")
    return {
        "metadata_json_keys": sorted(meta.keys()),
        "receipt": meta.get("prompt_injection_review"),
        "receipt_key_count": sum(1 for k in meta if "prompt_injection" in k),
        "audit_entries": len(audit) if isinstance(audit, list) else 0,
        "audit_evidence_sha256s": [e.get("evidence_sha256") for e in audit]
        if isinstance(audit, list) else [],
    }


def classify(outs: list[dict]) -> dict:
    acks = [o for o in outs if o.get("writes")]
    rejected = [o for o in outs if not o.get("writes") and o.get("errors")]
    undefined = [o for o in outs if not o.get("writes") and not o.get("errors")]
    bare_sqlite = [e for o in outs for t, e in zip(o.get("error_types", []), o.get("errors", []))
                   if t.startswith("sqlite3") or t.startswith("OperationalError")]
    defined_errors = [(t, e) for o in outs
                      for t, e in zip(o.get("error_types", []), o.get("errors", []))]
    return {"acks": len(acks), "defined_rejections": len(rejected),
            "undefined_outcomes": len(undefined),
            "count_conservation": len(acks) + len(rejected) == len(outs),
            "bare_sqlite_errors": bare_sqlite,
            "all_errors": defined_errors}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    TMP = Path(os.environ["TEMP"]) / "fix-w06-gaps" / "p6"
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    pkg = TMP / "pi_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    for f in args.pkg_dir.glob("*.py"):
        shutil.copy2(f, pkg / f.name)
    log(f"target pkg-dir : {args.pkg_dir}")
    for f in sorted(pkg.glob("*.py")):
        log(f"    {f.name} sha256={hashlib.sha256(f.read_bytes()).hexdigest()}")
    log()

    # ---------------- Phase A: 8 concurrent writers, default timeout --------
    fresh_db(TMP)
    owners = [f"w{i}" for i in range(8)]
    procs = [spawn(PY, WRITER, ["single", o, "doc-race"], TMP) for o in owners]
    go_sync(TMP, owners)
    outs = collect(procs)
    log("=== Phase A: 8 concurrent single writes, same document_id='doc-race' ===")
    for o in outs:
        log(f"    {json.dumps(o, ensure_ascii=False)}")
    fin = final_state(TMP, "doc-race")
    log(f"    final row: {json.dumps(fin, ensure_ascii=False)}")
    cls = classify(outs)
    acked_shas = {o.get("evidence_sha256") for o in outs if o.get("writes")}
    audit_shas = set(fin["audit_evidence_sha256s"])
    every_ack_traced = acked_shas <= audit_shas
    every_write_traced_or_rejected = (
        audit_shas | {o.get("evidence_sha256") for o in outs if not o.get("writes")}
        ) >= {o.get("evidence_sha256") for o in outs}
    RESULTS["P6A_concurrent_writes"] = {
        "maps_06": "Phase A / SUMMARY P6-A lost_write_count=7 (silent last-writer-wins displacement)",
        "processes": outs,
        "classification": cls,
        "final_state": fin,
        "acked_evidence_sha256s": sorted(s for s in acked_shas if s),
        "audit_proves_every_acknowledged_write": every_ack_traced,
        "every_write_traced_or_defined_rejected": every_write_traced_or_rejected,
        "expect": "count conservation (acks + defined rejections == attempts), zero silent drops; "
                  "read-back (audit trail) proves every acknowledged write; "
                  "under default timeout writes succeed with zero lock exceptions (red line)",
        "ok": (cls["count_conservation"] and cls["undefined_outcomes"] == 0
               and not cls["bare_sqlite_errors"] and every_ack_traced
               and every_write_traced_or_rejected
               and cls["acks"] == 8 and cls["defined_rejections"] == 0),
    }
    log()

    # ---------------- Phase A2: timeout=0 (lock exposure) -------------------
    fresh_db(TMP)
    os.environ["GAPS_P6_TIMEOUT"] = "0.0"
    procs = [spawn(PY, WRITER, ["tight", o, "doc-race"], TMP) for o in owners]
    go_sync(TMP, owners)
    outs0 = collect(procs)
    os.environ.pop("GAPS_P6_TIMEOUT", None)
    log("=== Phase A2: 8 concurrent writes, connect timeout=0.0 (lock exposed) ===")
    for o in outs0:
        log(f"    {json.dumps(o, ensure_ascii=False)}")
    fin0 = final_state(TMP, "doc-race")
    log(f"    final row: {json.dumps(fin0, ensure_ascii=False)}")
    cls0 = classify(outs0)
    wrapped = all(t == "PromptInjectionReviewError"
                  for t, _ in cls0["all_errors"])
    busy_texts = all(e.split(": ", 1)[1].startswith("store busy/lock timeout: ")
                     for _, e in cls0["all_errors"])
    RESULTS["P6B_lock_errors_wrapped"] = {
        "maps_06": "Phase A2 / SUMMARY P6-A2: 7/8 bare sqlite3.OperationalError 'database is locked'",
        "processes": outs0,
        "classification": cls0,
        "final_state": fin0,
        "expect": "all contention errors surface as PromptInjectionReviewError "
                  '"store busy/lock timeout: ..." (never bare sqlite3.*)',
        "ok": bool(cls0["all_errors"]) and not cls0["bare_sqlite_errors"] and wrapped and busy_texts,
    }
    log()

    # ---------------- Phase B: interleaved writers + readers ----------------
    fresh_db(TMP)
    stop = TMP / "stop.flag"
    if stop.exists():
        stop.unlink()
    readers = [spawn(PY, READER, [f"r{i}", "doc-mix"], TMP) for i in range(4)]
    writers = [spawn(PY, WRITER, ["mix", f"m{i}", "doc-mix"], TMP) for i in range(4)]
    go_sync(TMP, [f"m{i}" for i in range(4)])
    w_outs = collect(writers)
    time.sleep(0.3)
    stop.write_text("stop", encoding="utf-8")
    r_outs = collect(readers)
    log("=== Phase B: 4 writers + 4 readers interleaved on 'doc-mix' ===")
    for o in w_outs + r_outs:
        log(f"    {json.dumps(o, ensure_ascii=False)}")
    finb = final_state(TMP, "doc-mix")
    log(f"    final row: {json.dumps(finb, ensure_ascii=False)}")
    torn = [e for o in r_outs for e in o.get("errors", [])]
    clsb = classify(w_outs)
    RESULTS["P6_REDLINE_interleaved_reads"] = {
        "maps_06": "Phase B / SUMMARY P6-B: 658 interleaved reads, zero tearing, zero exceptions (MUST stay green)",
        "writers": w_outs, "readers": r_outs,
        "writer_classification": clsb,
        "final_state": finb,
        "torn_or_crashing_reads": torn,
        "ok": not torn and clsb["count_conservation"] and clsb["undefined_outcomes"] == 0,
    }
    log()

    log("=== SUMMARY ===")
    log(json.dumps(RESULTS, ensure_ascii=False, indent=2, default=str))
    for name, res in RESULTS.items():
        log(f"    {name}: {'PASS' if res.get('ok') else 'FAIL'}")
    overall = all(v.get("ok") for v in RESULTS.values())
    log(f"P6 SCENARIOS: {'PASS' if overall else 'FAIL'}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {args.out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
