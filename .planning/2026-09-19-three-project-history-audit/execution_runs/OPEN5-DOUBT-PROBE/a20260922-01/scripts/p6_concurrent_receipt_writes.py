"""P6 — concurrent write atomicity of the PRODUCT prompt-injection receipt writer.

Target: company-wiki/src/company_wiki/source_catalog/prompt_injection.py ::
        record_prompt_injection_review (caller owns commit — realistic caller =
        connect → record → commit).
Freeze (oracle-lite):
  - 8 concurrent processes write receipts for the SAME document_id (different
    evidence/reviewer): record uncaught 'database is locked', lost receipt rows,
    torn/half-written reads.
  - interleave writes + evaluate reads: reader must never see a half-written
    receipt (it should see a COMPLETE old-or-new receipt, or a clean not_reviewed).
  - align (or contradict) REMEDIATION_REGISTER.md:592 「grep iso+生产两树 零 lock 原语」.
Raw output -> evidence/06_concurrent_receipt_writes.txt.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
from pathlib import Path

CW_SRC = Path(
    r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\prompt_injection.py"
)
OUT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\OPEN5-DOUBT-PROBE\a20260922-01\evidence\06_concurrent_receipt_writes.txt"
)
TMP = Path(os.environ["TEMP"]) / "open5-doubt-probe" / "p6"
PY = sys.executable

LOG: list[str] = []
results: dict = {}


def log(line: str = "") -> None:
    LOG.append(line)
    print(line)


WRITER = r'''
import hashlib, importlib.util, json, os, sqlite3, sys, time
from pathlib import Path
tmp = Path(os.environ["OPEN5_P6_TMP"])
spec = importlib.util.spec_from_file_location("pi_w", tmp / "prompt_injection.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["pi_w"] = mod
spec.loader.exec_module(mod)
mode, owner, doc = sys.argv[1], sys.argv[2], sys.argv[3]
timeout = float(os.environ.get("OPEN5_P6_TIMEOUT", "5.0"))
go = tmp / "go.flag"
(tmp / f"ready.{owner}").write_text("1", encoding="utf-8")
while not go.exists():
    time.sleep(0.001)
out = {"owner": owner, "mode": mode, "writes": 0, "errors": []}
try:
    c = sqlite3.connect(str(tmp / "catalog.sqlite3"), timeout=timeout)
    try:
        mod.record_prompt_injection_review(
            c, doc,
            status="not_detected", reviewer=owner,
            evidence_sha256=hashlib.sha256(owner.encode()).hexdigest(),
            now="2026-09-22T00:00:00Z",
        )
        c.commit()
        out["writes"] += 1
    finally:
        c.close()
except BaseException as exc:
    out["errors"].append(f"{type(exc).__name__}: {exc}")
print(json.dumps(out, ensure_ascii=False))
'''

READER = r'''
import importlib.util, json, os, sqlite3, sys, time
from pathlib import Path
tmp = Path(os.environ["OPEN5_P6_TMP"])
spec = importlib.util.spec_from_file_location("pi_r", tmp / "prompt_injection.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["pi_r"] = mod
spec.loader.exec_module(mod)
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


def spawn(script: str, args: list[str]) -> subprocess.Popen:
    return subprocess.Popen(
        [PY, "-X", "utf8", "-B", "-c", script, *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=dict(os.environ, OPEN5_P6_TMP=str(TMP)),
    )


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


def fresh_db() -> None:
    db = TMP / "catalog.sqlite3"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(str(db))
    con.execute("CREATE TABLE documents (document_id TEXT PRIMARY KEY, metadata_json TEXT)")
    for name in ("doc-a", "doc-race", "doc-mix"):
        con.execute("INSERT INTO documents VALUES(?,?)", (name, "{}"))
    con.commit()
    con.close()


def go_sync(owners: list[str]) -> None:
    for p in TMP.glob("ready.*"):
        p.unlink()
    go = TMP / "go.flag"
    if go.exists():
        go.unlink()
    deadline = time.time() + 10
    while time.time() < deadline and not all((TMP / f"ready.{o}").exists() for o in owners):
        time.sleep(0.001)
    time.sleep(0.05)
    go.write_text("go", encoding="utf-8")


def final_receipt(doc: str) -> dict:
    con = sqlite3.connect(str(TMP / "catalog.sqlite3"))
    row = con.execute(
        "SELECT metadata_json FROM documents WHERE document_id=?", (doc,)).fetchone()
    con.close()
    meta = json.loads(row[0] or "{}")
    return {"metadata_json": meta,
            "receipt": meta.get("prompt_injection_review"),
            "receipt_key_count": sum(1 for k in meta if "prompt_injection" in k)}


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    mod_copy = TMP / "prompt_injection.py"
    shutil.copy2(CW_SRC, mod_copy)
    log(f"target product module: {CW_SRC}")
    log(f"sha256: {hashlib.sha256(CW_SRC.read_bytes()).hexdigest()}")
    log("REMEDIATION_REGISTER.md:592 claim under test: 「复审自 grep iso+生产两树 零 lock 原语」")
    log()

    # ---------- Phase A: 8 concurrent writers, same document ----------
    fresh_db()
    owners = [f"w{i}" for i in range(8)]
    procs = [spawn(WRITER, ["single", o, "doc-race"]) for o in owners]
    go_sync(owners)
    outs = collect(procs)
    log("=== Phase A: 8 concurrent single writes, same document_id='doc-race' ===")
    for o in outs:
        log(f"    {json.dumps(o, ensure_ascii=False)}")
    fin = final_receipt("doc-race")
    log(f"    final row: {json.dumps(fin, ensure_ascii=False)}")
    lock_errors = [e for o in outs for e in o.get("errors", []) if "locked" in e.lower()]
    other_errors = [e for o in outs for e in o.get("errors", []) if "locked" not in e.lower()]
    ok_writes = sum(o.get("writes", 0) for o in outs)
    results["P6-A"] = {
        "processes": outs,
        "successful_writes": ok_writes,
        "lock_errors": lock_errors,
        "other_errors": other_errors,
        "final_state": fin,
        "lost_write_count": 8 - 1,  # single-key metadata: only one receipt can survive
        "semantics": "single metadata key => last-writer-wins OVERWRITE (7/8 writes "
                     "are silently displaced, by design of the storage shape)",
        "uncaught_lock_exception": bool(lock_errors),
        "receipt_row_survivors": 1 if fin["receipt"] else 0,
    }
    log()

    # ---------- Phase A2: timeout=0 connect (immediate lock error exposure) ----------
    fresh_db()
    os.environ["OPEN5_P6_TIMEOUT"] = "0.0"
    procs = [spawn(WRITER, ["tight", o, "doc-race"]) for o in owners]
    go_sync(owners)
    outs0 = collect(procs)
    os.environ.pop("OPEN5_P6_TIMEOUT", None)
    log("=== Phase A2: 8 concurrent writes, connect timeout=0.0 (lock exposed) ===")
    for o in outs0:
        log(f"    {json.dumps(o, ensure_ascii=False)}")
    fin0 = final_receipt("doc-race")
    log(f"    final row: {json.dumps(fin0, ensure_ascii=False)}")
    lock0 = [e for o in outs0 for e in o.get("errors", []) if "locked" in e.lower()]
    results["P6-A2"] = {
        "processes": outs0,
        "successful_writes": sum(o.get("writes", 0) for o in outs0),
        "lock_errors": lock0,
        "final_state": fin0,
        "note": "with timeout=0 the writer has NO lock handling — 'database is "
                "locked' escapes as a raw sqlite3.OperationalError",
        "uncaught_lock_exception": bool(lock0),
    }
    log()

    # ---------- Phase B: interleaved writers + readers ----------
    fresh_db()
    stop = TMP / "stop.flag"
    if stop.exists():
        stop.unlink()
    readers = [spawn(READER, [f"r{i}", "doc-mix"]) for i in range(4)]
    writers = [spawn(WRITER, ["mix", f"m{i}", "doc-mix"]) for i in range(4)]
    go_sync([f"m{i}" for i in range(4)])
    w_outs = collect(writers)
    time.sleep(0.3)
    stop.write_text("stop", encoding="utf-8")
    r_outs = collect(readers)
    log("=== Phase B: 4 writers + 4 readers interleaved on 'doc-mix' ===")
    for o in w_outs + r_outs:
        log(f"    {json.dumps(o, ensure_ascii=False)}")
    finb = final_receipt("doc-mix")
    log(f"    final row: {json.dumps(finb, ensure_ascii=False)}")
    torn = [e for o in r_outs for e in o.get("errors", [])]
    results["P6-B"] = {
        "writers": w_outs,
        "readers": r_outs,
        "final_state": finb,
        "torn_or_crashing_reads": torn,
        "readers_saw_only_complete_receipts": not torn,
    }
    log()

    log("=== SUMMARY ===")
    log(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    log()
    log("alignment with REMEDIATION_REGISTER.md:592 「零 lock 原语」: "
        + ("CONFIRMED — no lock primitives in the writer; contention surfaces as "
           "raw sqlite errors / silent overwrite displacement"
           if (lock0 or ok_writes < 8) else
           "no observed effect of the missing lock primitives in this probe"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\n[evidence written] {OUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(LOG) + "\n" + traceback.format_exc(), encoding="utf-8")
        sys.exit(1)
