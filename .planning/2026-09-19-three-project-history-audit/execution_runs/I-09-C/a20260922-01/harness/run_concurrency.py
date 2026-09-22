"""I-09-C P-C3 concurrency runner (card 按序动作 5).

Two rounds on ONE isolated registry:
  round A — two IDENTICAL publications (same input, distinct output paths)
  round B — two DIFFERENT publications (P0 vs P1 inputs)
A continuously-reading consumer (reader_loop.py) samples the registry during
both rounds.  Afterward a fresh reader process verifies:
  * chain integrity (no fork / no break / no half line accepted)
  * logical commit count vs history rows
  * allowed audit-history rows (audit() problems must be 0)
  * whether any cross-process lock exists (frozen F5: not implemented — live
    evidence recorded here either way)

Everything runs against the isolated test registry; no real registry exists.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ATTEMPT, ISO_RF, PY, case_dir, child_env, make_input_docs,
    read_json, sha256_file, write_json,
)

HARNESS = ATTEMPT / "harness"
CASE = "PC3_concurrency"
CIRC = case_dir(CASE)
SHARED = ATTEMPT / "evidence" / "shared_inputs"


def spawn_writer(state, inp, out_json, out_md, label):
    return subprocess.Popen(
        [str(PY), str(HARNESS / "writer.py"),
         "--run-dir", str(state), "--input", str(inp),
         "--output", str(out_json), "--markdown", str(out_md),
         "--fault", "none", "--label", label],
        cwd=str(ISO_RF), env=child_env(CIRC / "state" / "registry" / "publications.jsonl"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace",
    )


def wait_all(procs, timeout=300):
    out = []
    for p in procs:
        try:
            so, se = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            so, se = p.communicate()
        out.append({"popen_pid": p.pid, "raw_returncode": p.returncode,
                    "stdout": (so or "")[:500], "stderr": (se or "")[:500]})
    return out


def main() -> int:
    if CIRC.exists():
        for root, dirs, files in os.walk(CIRC):
            for n in files + dirs:
                try:
                    os.chmod(os.path.join(root, n), 0o666)
                except OSError:
                    pass
        shutil.rmtree(CIRC, ignore_errors=True)
    state = CIRC / "state"
    state.mkdir(parents=True)
    shared = SHARED
    if not (shared / "input_p1.json").exists():
        make_input_docs(shared)
    for n in ("input_p0.json", "input_p1.json"):
        shutil.copyfile(shared / n, state / n)
    registry = state / "registry" / "publications.jsonl"
    input_hashes = {n: sha256_file(state / n) for n in ("input_p0.json", "input_p1.json")}

    # continuous reader before any publisher starts
    stop_flag = CIRC / "stop_reader"
    loop_out = CIRC / "reader_samples.jsonl"
    loop = subprocess.Popen(
        [str(PY), str(HARNESS / "reader_loop.py"),
         "--registry", str(registry), "--out", str(loop_out),
         "--stop-file", str(stop_flag), "--max-seconds", "180"],
        cwd=str(ISO_RF), env=child_env(registry),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace",
    )
    time.sleep(0.5)

    rounds = {}
    try:
        # Round A: two identical publications
        procs = [
            spawn_writer(state, state / "input_p1.json",
                         state / "identicalA.json", state / "identicalA.md", "identical_A"),
            spawn_writer(state, state / "input_p1.json",
                         state / "identicalB.json", state / "identicalB.md", "identical_B"),
        ]
        t0 = time.time()
        rounds["identical"] = {
            "spawned_pids": [p.pid for p in procs],
            "results": wait_all(procs),
            "wall_seconds": round(time.time() - t0, 2),
        }
        time.sleep(0.5)

        # Round B: two different publications
        procs = [
            spawn_writer(state, state / "input_p0.json",
                         state / "diffA_p0.json", state / "diffA_p0.md", "different_A_p0"),
            spawn_writer(state, state / "input_p1.json",
                         state / "diffB_p1.json", state / "diffB_p1.md", "different_B_p1"),
        ]
        t0 = time.time()
        rounds["different"] = {
            "spawned_pids": [p.pid for p in procs],
            "results": wait_all(procs),
            "wall_seconds": round(time.time() - t0, 2),
        }
    finally:
        time.sleep(0.5)
        stop_flag.write_text("stop\n", encoding="utf-8")
        try:
            lso, lse = loop.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            loop.kill()
            lso, lse = loop.communicate()

    # fresh reader verdict
    reader_out = CIRC / "reader_final.json"
    ro = subprocess.run(
        [str(PY), str(HARNESS / "reader.py"),
         "--run-dir", str(state), "--registry", str(registry),
         "--out", str(reader_out), "--label", "PC3_final"],
        cwd=str(ISO_RF), env=child_env(registry),
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
    )
    reader = read_json(reader_out)

    # continuous-reader samples summary
    samples = []
    if loop_out.exists():
        samples = [json.loads(ln) for ln in loop_out.read_text(encoding="utf-8").splitlines()
                   if ln.strip()]
    final_sample = samples[-1] if samples else {}
    bad_samples = [s for s in samples if not s.get("final") and not s.get("chain_ok", True)]
    committed_trace = [s.get("committed_rows_visible") for s in samples
                       if not s.get("final")]

    # lock evidence (frozen F5: not implemented — confirm on this tree)
    src = (ISO_RF / "scripts" / "publication_registry.py").read_text(encoding="utf-8")
    lock_tokens = [t for t in ("lockfile", ".lock", "msvcrt", "flock", "LockFileEx",
                               "filelock", "threading.Lock") if t in src]

    checks = []

    def check(name, expected, actual, why=""):
        checks.append({"item": name, "expected": expected, "actual": actual,
                       "ok": actual == expected, "why": why})

    chain = reader.get("chain", {})
    check("chain_intact_no_fork_no_break", True, chain.get("ok"),
          str(chain.get("problems")))
    check("product_reader_agrees", True, reader.get("product_read", {}).get("ok"),
          str(reader.get("product_read", {}).get("error")))
    p0, p1 = reader["packages"].get("p0", {}), reader["packages"].get("p1", {})
    check("p0_logical_commits", 1, p0.get("logical_commits"))
    check("p1_logical_commits", 1, p1.get("logical_commits"),
          "identical pair must not fabricate a second logical publication")
    check("p0_history_rows_allowed", True,
          p0.get("committed_rows", 0) >= 1,
          "audit history rows > 1 are allowed by I-08-A §5 / C-08; logical commits are not")
    check("p1_history_rows_allowed", True, p1.get("committed_rows", 0) >= 1)
    check("audit_problems", 0, len(reader.get("audit_problems") or []),
          "allowed audit-history rows must not be misreported")
    check("p0_consumable", True, p0.get("consumable"))
    check("p1_consumable", True, p1.get("consumable"))
    check("reader_never_accepted_broken_chain", 0, len(bad_samples),
          "continuous consumer: every sample either verified the chain or refused it")
    check("continuous_reader_ran", True, final_sample.get("final", False) or bool(samples),
          f"samples={len(samples)}")
    check("writer_exits_all_zero_or_recorded", True,
          all(r["raw_returncode"] in (0, None) for r in
              rounds["identical"]["results"] + rounds["different"]["results"]),
          str([r["raw_returncode"] for r in
               rounds["identical"]["results"] + rounds["different"]["results"]]))

    verdict = {
        "case_id": CASE,
        "card_point": "两进程同时从同链尾提交；另一个reader连续读 (P-C3)",
        "f_row": "F5/F6 相邻（并发提交 + 连续 reader）",
        "rounds": rounds,
        "input_hashes": input_hashes,
        "registry_final": {
            "exists": registry.exists(),
            "bytes": registry.stat().st_size if registry.exists() else 0,
            "rows": chain.get("rows"),
            "chain_ok": chain.get("ok"),
            "problems": chain.get("problems"),
        },
        "committed_trace_from_continuous_reader": committed_trace,
        "bad_samples": bad_samples[:20],
        "lock_evidence": {
            "lock_tokens_in_publication_registry_py": lock_tokens,
            "frozen_F5": "锁未实现 (I-09-A F5 E-column: n/a(锁未实现); I-09-B open item)",
        },
        "checks": checks,
        "all_ok": all(c["ok"] for c in checks),
        "reader_loop_stdout": (lso or "").strip(),
        "reader_loop_stderr": (lse or "").strip()[:400],
        "final_reader_stdout": ro.stdout.strip(),
    }
    write_json(CIRC / "verdict.json", verdict)
    print(f"PC3: all_ok={verdict['all_ok']} checks={len(checks)} "
          f"failed={sum(1 for c in checks if not c['ok'])} rows={chain.get('rows')} "
          f"chain_ok={chain.get('ok')} samples={len(samples)}")
    for c in checks:
        if not c["ok"]:
            print(f"  FAIL {c['item']}: exp={c['expected']} act={c['actual']} {c['why']}")
    return 0 if verdict["all_ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
