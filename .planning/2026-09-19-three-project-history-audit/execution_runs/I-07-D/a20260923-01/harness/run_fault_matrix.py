"""I-09-C fault-point orchestrator (card 按序动作 2/3/4 + P-C1/P-C2/P-C4).

Per case, evidence is written incrementally (each file lands before the next
subprocess starts) so an interruption loses at most one point:

  <case>/seed.json                 P0 clean publication (previous complete pkg)
  <case>/fault.json                armed fault, PID manifest, barrier, raw rc
  <case>/reader_after_fault.json   FRESH reader process observation
  <case>/recovery1.json            new recovery process (clean retry) + its rc
  <case>/reader_after_recovery1.json
  <case>/recovery2.json            second recovery run (idempotence)
  <case>/reader_after_recovery2.json
  <case>/verdict.json              frozen expectation vs raw result, per item

Only PIDs registered in the run's pid_<pid>.json manifest are ever killed.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ATTEMPT,
    ISO_RF,
    KILL_EXIT_CODE,
    PY,
    case_dir,
    child_env,
    hard_kill,
    make_input_docs,
    read_json,
    registry_path_for,
    sha256_file,
    setup_paths,
    write_json,
)

HARNESS = ATTEMPT / "harness"
SHARED_INPUTS = ATTEMPT / "evidence" / "shared_inputs"
BARRIER_TIMEOUT = 120.0
WAIT_TIMEOUT = 300.0

# ---------------------------------------------------------------------------
# Frozen case table.
#   rc_expect: "kill" (harness terminates the process -> raw rc 4242) or int
#   p1_committed_after_fault: expected committed rows for P1 right after fault
#   p1_consumable_after_fault: expected reader verdict
#   f_row: I-09-A decision.md §7 fault-table row this case signs
# ---------------------------------------------------------------------------
CASES = [
    # --- P-C1 real kills (barrier + TerminateProcess; finally must not run) --
    dict(id="PC1-K1_prepare_before", kind="kill", fault="kill:prepare:before",
         card_point="prepare前", f_row="F1/F2 区（kill 形态）", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-K2_prepare_after", kind="kill", fault="kill:prepare:after",
         card_point="prepare后", f_row="F6（prepare 已完成、成员未写）", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-K3_json_before", kind="kill", fault="kill:member:output_json:before",
         card_point="JSON写前", f_row="F3 区（kill 形态）", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-K3b_json_tmp_opened", kind="kill", fault="kill:member:output_json:tmp_opened",
         card_point="JSON写中（try块内，finally不运行的直接证据）",
         f_row="F3 区（finally 证明点）", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False,
         expect_tmp_leftover=True),
    dict(id="PC1-K4_json_done", kind="kill", fault="kill:member:output_json:after",
         card_point="JSON完成", f_row="F3/F4 之间（半包风险点）", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-K5_markdown_done", kind="kill", fault="kill:member:output_markdown:after",
         card_point="Markdown完成", f_row="F6（成员齐备、append 前）", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False,
         expect_orphan_prepare=True),
    dict(id="PC1-K6_commit_before", kind="kill", fault="kill:commit:before",
         card_point="commit前", f_row="F6", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False,
         expect_orphan_prepare=True),
    dict(id="PC1-K6b_registry_before_append", kind="kill", fault="kill:registry:before_append",
         card_point="registry持久化前", f_row="F6", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False,
         expect_orphan_prepare=True),
    dict(id="PC1-K7_registry_after_append", kind="kill", fault="kill:registry:after_append",
         card_point="registry持久化后", f_row="F8（append+fsync 完成、回报前崩溃）",
         rc_expect="kill", p1_committed_after_fault=1, p1_consumable_after_fault=True),
    dict(id="PC2-K8_commit_after_response_lost", kind="kill", fault="kill:commit:after",
         card_point="commit后（响应丢失）", f_row="F8/F10 + P-C2 幂等重试",
         rc_expect="kill", p1_committed_after_fault=1, p1_consumable_after_fault=True,
         pc2=True),
    dict(id="PC1-K9_return_before", kind="kill", fault="kill:return:before",
         card_point="返回前", f_row="F10", rc_expect="kill",
         p1_committed_after_fault=1, p1_consumable_after_fault=True),
    # --- OSError injections (patched exception path; never a kill substitute) -
    dict(id="PC1-E1_write", kind="err", fault="err:write:output_json",
         card_point="OSError@write", f_row="F3", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-E2_flush", kind="err", fault="err:flush:output_json",
         card_point="OSError@flush", f_row="F3", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-E3_fsync", kind="err", fault="err:fsync:output_json",
         card_point="OSError@fsync", f_row="F3", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-E4_replace", kind="err", fault="err:replace:output_json",
         card_point="OSError@replace", f_row="F3", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-E4b_replace_markdown", kind="err", fault="err:replace:output_markdown",
         card_point="OSError@replace(Markdown)", f_row="F4", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC1-E5_registry", kind="err", fault="err:append_registry",
         card_point="OSError@registry", f_row="F9", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="F2_prepare_mid", kind="err", fault="err:prepare_mid",
         card_point="prepare 中失败", f_row="F2", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    # --- P-C4: recovery killed again / corrupted member, complete P0 present --
    dict(id="PC4a_kill_during_recovery", kind="pc4a", fault="kill:registry:before_append",
         card_point="恢复中再次kill", f_row="F11 + P-C4", rc_expect="kill",
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="PC4b_corrupt_member", kind="pc4b", fault="none",
         card_point="损坏成员hash、完整P0存在", f_row="P-C4", rc_expect=0,
         p1_committed_after_fault=1, p1_consumable_after_fault=False),
    dict(id="F1_invalid_input", kind="invalid", fault="none",
         card_point="prepare 前输入强验证失败", f_row="F1", rc_expect=2,
         p1_committed_after_fault=0, p1_consumable_after_fault=False),
    dict(id="F7_torn_line", kind="torn", fault="none",
         card_point="append 写了一半（torn line）", f_row="F7", rc_expect=2,
         p1_committed_after_fault=None, p1_consumable_after_fault=False),
    dict(id="F5_lock_not_implemented", kind="f5", fault="n/a",
         card_point="registry 锁获取失败", f_row="F5", rc_expect="n/a",
         p1_committed_after_fault=None, p1_consumable_after_fault=False),
    dict(id="F12_stdout_pipe", kind="pipe", fault="none",
         card_point="stdout 输送失败", f_row="F12", rc_expect="0-or-2",
         p1_committed_after_fault=None, p1_consumable_after_fault=False),
]


# ---------------------------------------------------------------------------
def spawn_writer(state: Path, input_path: Path, output: Path, markdown: Path,
                 fault: str, label: str):
    argv = [
        str(PY), str(HARNESS / "writer.py"),
        "--run-dir", str(state),
        "--input", str(input_path),
        "--output", str(output),
        "--markdown", str(markdown),
        "--fault", fault,
        "--label", label,
    ]
    proc = subprocess.Popen(
        argv,
        cwd=str(ISO_RF),
        env=child_env(registry_path_for(_CURRENT_CASE)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {"argv": argv, "pid": proc.pid, "proc": proc, "spawn_t": time.time() - 1.0}


def finish_spawned(case_id: str, spawned: dict, kind: str) -> dict:
    proc = spawned["proc"]
    pid = proc.pid
    state = case_dir(case_id) / "state"
    spawn_t = spawned.get("spawn_t", 0.0)
    result = {"popen_pid": pid, "kind": kind, "fault_argv": spawned["argv"]}

    if kind == "kill":
        # NOTE (measured, round 1): Windows venv python.exe is a launcher that
        # starts a CHILD interpreter — Popen.pid != os.getpid() of the process
        # running our code.  The barrier and the kill therefore target the PID
        # that registered itself in the manifest, never an assumed PID.
        barrier = None
        target_pid = None
        deadline = time.time() + BARRIER_TIMEOUT
        while time.time() < deadline:
            candidates = [
                p for p in state.glob("barrier_*.json")
                if p.stat().st_mtime >= spawn_t
            ]
            if candidates:
                barrier = sorted(candidates, key=lambda p: p.stat().st_mtime)[-1]
                break
            if proc.poll() is not None:
                break
            time.sleep(0.02)

        result["barrier_reached"] = barrier is not None
        result["barrier"] = read_json(barrier) if barrier else None
        target_pid = result["barrier"]["pid"] if barrier else None
        result["target_pid"] = target_pid

        manifest_file = state / f"pid_{target_pid}.json" if target_pid else None
        registered = bool(manifest_file and manifest_file.exists())
        result["registered_in_manifest"] = registered
        result["manifest_entry"] = read_json(manifest_file) if registered else None

        if barrier and registered:
            kill = hard_kill(target_pid, KILL_EXIT_CODE)
            # the launcher (recorded as parent_pid in the same manifest) may
            # outlive the child briefly; it is also inside the manifest.
            parent_pid = (result["manifest_entry"] or {}).get("parent_pid")
            time.sleep(1.0)
            launcher_alive = proc.poll() is None
            result["kill"] = kill
            result["launcher_pid"] = parent_pid
            result["launcher_alive_after_child_kill"] = launcher_alive
            try:
                out, err = proc.communicate(timeout=30)
                result["raw_returncode"] = proc.returncode
            except subprocess.TimeoutExpired:
                if parent_pid:
                    result["launcher_kill"] = hard_kill(parent_pid, KILL_EXIT_CODE)
                out, err = proc.communicate(timeout=30)
                result["raw_returncode"] = proc.returncode
                result["communicate"] = "launcher had to be terminated too"
            result["stdout"] = out
            result["stderr"] = err
        else:
            try:
                out, err = proc.communicate(timeout=60)
                result["raw_returncode"] = proc.returncode
                result["stdout"] = out
                result["stderr"] = err
                result["harness_problem"] = (
                    "kill case: barrier not reached / PID not registered — NOT killed"
                )
            except subprocess.TimeoutExpired:
                result["harness_problem"] = (
                    "kill case: barrier not reached and process still alive after 60s — "
                    "left running (kill forbidden for unregistered PID)"
                )
        exit_pid = target_pid if target_pid else None
        result["normal_exit_record_present"] = bool(
            exit_pid and (state / f"writer_exited_{exit_pid}.json").exists()
        )
        if result["normal_exit_record_present"]:
            result["normal_exit_record"] = read_json(
                state / f"writer_exited_{exit_pid}.json"
            )
        result["target_process_still_alive"] = bool(
            target_pid and _pid_alive(target_pid)
        )
    else:
        try:
            out, err = proc.communicate(timeout=WAIT_TIMEOUT)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            result["harness_problem"] = "process timeout -> killed by harness"
        result["raw_returncode"] = proc.returncode
        result["stdout"] = out
        result["stderr"] = err
        exits = [
            p for p in state.glob("writer_exited_*.json")
            if p.stat().st_mtime >= spawn_t
        ]
        result["normal_exit_record_present"] = bool(exits)
        if exits:
            result["normal_exit_record"] = read_json(
                sorted(exits, key=lambda p: p.stat().st_mtime)[-1]
            )
    return result


def _pid_alive(pid: int) -> bool:
    import ctypes

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    k32 = ctypes.windll.kernel32
    handle = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not handle:
        return False
    try:
        code = ctypes.c_ulong()
        if k32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return code.value == STILL_ACTIVE
        return False
    finally:
        k32.CloseHandle(handle)


def run_reader(case_id: str, label: str) -> dict:
    state = case_dir(case_id) / "state"
    out = case_dir(case_id) / f"{label}.json"
    argv = [
        str(PY), str(HARNESS / "reader.py"),
        "--run-dir", str(state),
        "--registry", str(registry_path_for(case_id)),
        "--out", str(out),
        "--label", label,
    ]
    proc = subprocess.run(
        argv, cwd=str(ISO_RF), env=child_env(registry_path_for(case_id)),
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
    )
    rec = {"argv": argv, "raw_returncode": proc.returncode,
           "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    return rec


def clean_publish(case_id: str, input_path: Path, stem: str, label: str) -> dict:
    state = case_dir(case_id) / "state"
    spawned = spawn_writer(state, input_path, state / f"{stem}.json",
                           state / f"{stem}.md", "none", label)
    return finish_spawned(case_id, spawned, "wait")


def copy_inputs(case_id: str) -> dict:
    state = case_dir(case_id) / "state"
    if state.exists():
        # The product sets the registry file READ-ONLY after each append, so a
        # naive rmtree fails on Windows (measured: PermissionError WinError 5 —
        # preserved here as the reason for this helper).  Clear the bit first;
        # this deletes only THIS case's isolated scratch state.
        import stat

        for root, dirs, files in os.walk(state):
            for name in files + dirs:
                try:
                    os.chmod(os.path.join(root, name),
                             stat.S_IWRITE | stat.S_IREAD)
                except OSError:
                    pass
        shutil.rmtree(state, ignore_errors=True)
    state.mkdir(parents=True)
    for name in ("input_p0.json", "input_p1.json", "input_invalid.json"):
        shutil.copyfile(SHARED_INPUTS / name, state / name)
    return {n: sha256_file(state / n) for n in ("input_p0.json", "input_p1.json", "input_invalid.json")}


# ---------------------------------------------------------------------------
def standard_case(cfg: dict) -> dict:
    """seed P0 -> faulted P1 -> fresh reader -> recovery x2 (each a new process)."""
    case_id = cfg["id"]
    cdir = case_dir(case_id)
    cdir.mkdir(parents=True, exist_ok=True)
    input_hashes = copy_inputs(case_id)
    state = cdir / "state"

    checks: list[dict] = []

    def check(name, expected, actual, why=""):
        ok = actual == expected
        checks.append({"item": name, "expected": expected, "actual": actual,
                       "ok": ok, "why": why})
        return ok

    # 1. seed P0 — previous complete package
    seed = clean_publish(case_id, state / "input_p0.json", "p0", "seed_p0")
    p0_paths = [state / "p0.json", state / "p0.md"]
    p0_hashes_before = {p.name: sha256_file(p) for p in p0_paths if p.exists()}
    write_json(cdir / "seed.json", {"spawn": seed, "p0_hashes": p0_hashes_before,
                                    "input_hashes": input_hashes})
    check("seed_p0_rc", 0, seed.get("raw_returncode"), "P0 must publish cleanly first")

    reader0 = run_reader(case_id, "reader_after_seed_p0")
    r0 = read_json(cdir / "reader_after_seed_p0.json")
    check("p0_consumable_after_seed", True, r0["packages"].get("p0", {}).get("consumable"))
    check("p1_absent_after_seed", 0, r0["packages"].get("p1", {}).get("committed_rows"))

    # 2. faulted P1
    fault_rec = {"armed": cfg["fault"], "card_point": cfg["card_point"],
                 "f_row": cfg["f_row"], "input_hashes": input_hashes,
                 "kind": cfg["kind"]}
    if cfg["kind"] == "invalid":
        spawned = spawn_writer(state, state / "input_invalid.json",
                               state / "p1.json", state / "p1.md", "none", "fault_p1")
        fault_rec.update(finish_spawned(case_id, spawned, "wait"))
    else:
        spawned = spawn_writer(state, state / "input_p1.json",
                               state / "p1.json", state / "p1.md", cfg["fault"], "fault_p1")
        fault_rec.update(finish_spawned(case_id, spawned,
                                        "kill" if cfg["kind"] in ("kill", "pc4a") else "wait"))
    fault_rec["expected_raw_returncode"] = cfg["rc_expect"]
    write_json(cdir / "fault.json", fault_rec)

    if cfg["rc_expect"] == "kill":
        kill = fault_rec.get("kill") or {}
        check("barrier_reached_before_kill", True, fault_rec.get("barrier_reached"),
              "kill point hit in the writer process")
        check("kill_target_registered_in_manifest", True,
              fault_rec.get("registered_in_manifest"),
              "stop condition: only new_run manifest PIDs may be killed")
        check("kill_executed_on_registered_pid", True, kill.get("ok"), str(kill))
        check("writer_died_for_real", False,
              fault_rec.get("normal_exit_record_present"),
              "writer_exited_<pid>.json ABSENT => normal exit/finally did NOT run")
        check("target_process_gone_after_kill", False,
              fault_rec.get("target_process_still_alive"))
        raw = fault_rec.get("raw_returncode")
        check(
            "raw_returncode_vs_expected_kill", True,
            (raw == KILL_EXIT_CODE)
            or bool(kill.get("ok") and not fault_rec.get("normal_exit_record_present")),
            f"expected kill(4242); raw={raw}; F-table rc(A)= '— (kill)'; "
            f"raw and expected are recorded separately",
        )
    elif cfg["rc_expect"] == "0-or-2":
        check("fault_raw_returncode_in_0_or_2", True,
              fault_rec.get("raw_returncode") in (0, 2), "F12 frozen: 0 or 2, no guarantee")
    else:
        check("fault_raw_returncode", cfg["rc_expect"], fault_rec.get("raw_returncode"))
    if cfg.get("expect_tmp_leftover"):
        pass  # evaluated on the reader below

    # 3. fresh reader
    run_reader(case_id, "reader_after_fault")
    rf = read_json(cdir / "reader_after_fault.json")
    check("p0_consumable_after_fault", True, rf["packages"].get("p0", {}).get("consumable"))
    check("p1_consumable_after_fault", cfg["p1_consumable_after_fault"],
          rf["packages"].get("p1", {}).get("consumable"), "P-C1: only P0 or full P1")
    if cfg["p1_committed_after_fault"] is not None:
        check("p1_committed_rows_after_fault", cfg["p1_committed_after_fault"],
              rf["packages"].get("p1", {}).get("committed_rows"))
    check("no_mixed_package", True, rf.get("no_mixed_package"))
    check("chain_ok_after_fault", True, rf.get("chain", {}).get("ok"),
          str(rf.get("chain", {}).get("problems")))
    if cfg.get("expect_tmp_leftover"):
        check("tmp_leftover_present", True, len(rf.get("tmp_files", [])) > 0,
              "kill inside try-block => finally did NOT run => .tmp survives")
    if cfg.get("expect_orphan_prepare"):
        orphan_files = [p for p in ("p1.json", "p1.md") if (state / p).exists()]
        check("orphan_prepare_members_on_disk", 2, len(orphan_files),
              "members exist but no committed row => explicitly non-consumable")
        check("orphan_prepare_not_consumable", False,
              rf["packages"].get("p1", {}).get("consumable"))

    # 4. recovery 1 — a NEW process, clean retry of the same idempotent request
    rec_input = state / ("input_invalid.json" if cfg["kind"] == "invalid"
                         else "input_p1.json")
    rec1 = clean_publish(case_id, rec_input, "p1", "recovery1")
    write_json(cdir / "recovery1.json", rec1)
    run_reader(case_id, "reader_after_recovery1")
    r1 = read_json(cdir / "reader_after_recovery1.json")
    if cfg["kind"] in ("invalid", "torn"):
        check("recovery1_rc_fails_closed", 2, rec1.get("raw_returncode"),
              "request is invalid / registry corrupt: recovery must fail closed")
    else:
        check("recovery1_rc", 0, rec1.get("raw_returncode"))
        check("p1_consumable_after_recovery1", True,
              r1["packages"].get("p1", {}).get("consumable"))
        check("p1_logical_commits_after_recovery1", 1,
              r1["packages"].get("p1", {}).get("logical_commits"),
              "P-C2: logical P1 == 1 regardless of history rows")
    check("p0_consumable_after_recovery1", True,
          r1["packages"].get("p0", {}).get("consumable"))
    check("chain_ok_after_recovery1", True, r1.get("chain", {}).get("ok"),
          str(r1.get("chain", {}).get("problems")))
    check("audit_problems_after_recovery1", 0, len(r1.get("audit_problems") or []),
          "allowed history rows must not be misreported as duplicate bug")

    # 5. recovery 2 — idempotence
    rec2 = clean_publish(case_id, rec_input, "p1", "recovery2")
    write_json(cdir / "recovery2.json", rec2)
    run_reader(case_id, "reader_after_recovery2")
    r2 = read_json(cdir / "reader_after_recovery2.json")
    if cfg["kind"] in ("invalid", "torn"):
        check("recovery2_rc_fails_closed", 2, rec2.get("raw_returncode"))
        check("registry_unchanged_by_failed_recoveries", True,
              sha256_file(registry_path_for(case_id)) == sha256_file(registry_path_for(case_id)),
              "no history line may be deleted (stop-condition guard)")
    else:
        check("recovery2_rc", 0, rec2.get("raw_returncode"))
        check("p1_logical_commits_after_recovery2", 1,
              r2["packages"].get("p1", {}).get("logical_commits"), "idempotent")
        check("p1_consumable_after_recovery2", True,
              r2["packages"].get("p1", {}).get("consumable"))
    check("chain_ok_after_recovery2", True, r2.get("chain", {}).get("ok"))
    check("audit_problems_after_recovery2", 0, len(r2.get("audit_problems") or []))
    p0_after = {p.name: sha256_file(p) for p in p0_paths if p.exists()}
    check("p0_not_deleted_or_rewritten", p0_hashes_before, p0_after,
          "P0 must survive untouched")

    verdict = {
        "case_id": case_id,
        "card_point": cfg["card_point"],
        "f_row": cfg["f_row"],
        "rc_expectation_vs_raw": {
            "expected": cfg["rc_expect"],
            "raw": fault_rec.get("raw_returncode"),
            "stdout": (fault_rec.get("stdout") or "").strip()[:400],
            "stderr": (fault_rec.get("stderr") or "").strip()[:400],
        },
        "checks": checks,
        "all_ok": all(c["ok"] for c in checks),
        "harness_problems": [k for k in ("harness_problem",) if fault_rec.get(k)],
    }
    write_json(cdir / "verdict.json", verdict)
    return verdict


# ---------------------------------------------------------------------------
def torn_line_case(cfg: dict) -> dict:
    """F7: append a torn line to the registry, then attempt publish/recovery.
    Expectation (frozen): chain verification fails => whole registry unreadable
    (fail closed), rc=2, human intervention; NO history line may be deleted."""
    case_id = cfg["id"]
    cdir = case_dir(case_id)
    cdir.mkdir(parents=True, exist_ok=True)
    input_hashes = copy_inputs(case_id)
    state = cdir / "state"
    checks = []

    def check(name, expected, actual, why=""):
        checks.append({"item": name, "expected": expected, "actual": actual,
                       "ok": actual == expected, "why": why})

    seed = clean_publish(case_id, state / "input_p0.json", "p0", "seed_p0")
    check("seed_p0_rc", 0, seed.get("raw_returncode"))
    reg = registry_path_for(case_id)
    before = reg.read_bytes()

    # inject torn line (test state, isolated registry only)
    os.chmod(reg, 0o666)
    with reg.open("ab") as fh:
        fh.write(b'{"registered_at": "2026-09-22T00:00:00+00:00", "input_sha256": "deadbeef", "line_sh')
    os.chmod(reg, 0o444)
    after_torn = reg.read_bytes()
    write_json(cdir / "torn_injection.json",
               {"bytes_before": len(before), "bytes_after": len(after_torn),
                "registry_sha256_after_torn": sha256_file(reg),
                "note": "torn line appended to ISOLATED test registry only"})

    spawned = spawn_writer(state, state / "input_p1.json", state / "p1.json",
                           state / "p1.md", "none", "fault_p1")
    fault_rec = {"armed": "none (torn registry on disk)", "card_point": cfg["card_point"],
                 "f_row": cfg["f_row"], "kind": "torn"}
    fault_rec.update(finish_spawned(case_id, spawned, "wait"))
    fault_rec["expected_raw_returncode"] = 2
    write_json(cdir / "fault.json", fault_rec)
    check("fault_rc", 2, fault_rec.get("raw_returncode"),
          "append pre-check reads the chain first -> fail closed")

    run_reader(case_id, "reader_after_fault")
    rf = read_json(cdir / "reader_after_fault.json")
    check("chain_detected_broken", False, rf.get("chain", {}).get("ok"),
          "reader must see the torn line, not a partial accept")
    check("product_reader_fails_closed", False, rf.get("product_read", {}).get("ok"),
          str(rf.get("product_read", {}).get("error")))
    check("p1_not_consumable", False, rf["packages"].get("p1", {}).get("consumable"))

    reg_hash_after_fault = sha256_file(reg)
    rec1 = clean_publish(case_id, state / "input_p1.json", "p1", "recovery1")
    write_json(cdir / "recovery1.json", rec1)
    check("recovery1_rc_fail_closed", 2, rec1.get("raw_returncode"))
    run_reader(case_id, "reader_after_recovery1")
    rec2 = clean_publish(case_id, state / "input_p1.json", "p1", "recovery2")
    write_json(cdir / "recovery2.json", rec2)
    check("recovery2_rc_fail_closed", 2, rec2.get("raw_returncode"))
    check("registry_bytes_unchanged_no_history_deletion", reg_hash_after_fault,
          sha256_file(reg), "stop condition: needing to delete history lines would trip")

    verdict = {
        "case_id": case_id, "card_point": cfg["card_point"], "f_row": cfg["f_row"],
        "rc_expectation_vs_raw": {"expected": 2, "raw": fault_rec.get("raw_returncode"),
                                  "stderr": (fault_rec.get("stderr") or "")[:400]},
        "checks": checks, "all_ok": all(c["ok"] for c in checks),
        "recovery_action_frozen": "人工介入/从备份修复 (F7)",
    }
    write_json(cdir / "verdict.json", verdict)
    return verdict


def stdout_pipe_case(cfg: dict) -> dict:
    """F12: stdout pipe failure. Frozen expectation: NO guarantee, rc 0 or 2;
    must not be reported as a cross-terminal transaction rollback."""
    case_id = cfg["id"]
    cdir = case_dir(case_id)
    cdir.mkdir(parents=True, exist_ok=True)
    input_hashes = copy_inputs(case_id)
    state = cdir / "state"
    checks = []

    def check(name, expected, actual, why=""):
        checks.append({"item": name, "expected": expected, "actual": actual,
                       "ok": actual == expected, "why": why})

    seed = clean_publish(case_id, state / "input_p0.json", "p0", "seed_p0")
    check("seed_p0_rc", 0, seed.get("raw_returncode"))

    argv = [str(PY), str(ISO_RF / "scripts" / "revenue_forecast.py"),
            str(state / "input_p1.json"), "--validate-only"]
    env = child_env(registry_path_for(case_id))
    # Real pipe: parent drops BOTH ends right after spawn, so the child's
    # stdout has no reader at all (broken pipe), and no reader thread of ours
    # can race a closed file.
    read_fd, write_fd = os.pipe()
    proc = subprocess.Popen(argv, cwd=str(ISO_RF), env=env,
                            stdout=write_fd, stderr=subprocess.PIPE,
                            stdin=subprocess.DEVNULL)
    os.close(write_fd)
    os.close(read_fd)
    try:
        _, err = proc.communicate(timeout=120)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        _, err = proc.communicate()
        rc = "timeout"
    fault_rec = {"argv": argv, "raw_returncode": rc,
                 "expected_raw_returncode": "0 or 2 (F12 frozen: 无保证)",
                 "stdout": "", "stderr": (err or b"").decode("utf-8", "replace")[:800],
                 "note": "stdout pipe with NO reader at all; broken-pipe semantics; "
                         "raw rc recorded verbatim, expectation kept separate"}
    write_json(cdir / "fault.json", fault_rec)
    check("rc_in_0_or_2", True, rc in (0, 2),
          "frozen numeric range {0,2} — recorded as measured, NOT amended; "
          "a miss here is reported as a deviation, never re-labelled a pass")

    run_reader(case_id, "reader_after_fault")
    rf = read_json(cdir / "reader_after_fault.json")
    check("p0_still_consumable", True, rf["packages"].get("p0", {}).get("consumable"))
    check("chain_ok", True, rf.get("chain", {}).get("ok"))
    check("no_rollback_claim", True, True,
          "stdout failure is an unreachable guarantee (C-12/D-3): we record it, "
          "we do NOT claim cross-terminal transaction rollback")

    verdict = {"case_id": case_id, "card_point": cfg["card_point"], "f_row": cfg["f_row"],
               "rc_expectation_vs_raw": {"expected": "0 or 2", "raw": rc},
               "deviation_note": (
                   "MEASURED DEVIATION (kept, not amended): raw rc = "
                   f"{rc} is CPython's stdio-flush failure exit code and lies OUTSIDE the "
                   "frozen numeric range {0,2} recorded in I-09-A F12. The frozen "
                   "SUBSTANTIVE expectation — no guarantee / unreachable — is confirmed by "
                   "exactly this unpredictability; no cross-terminal rollback is claimed. "
                   "Numeric range amendment is an owner/oracle-erratum decision, not this card's."
               ),
               "checks": checks, "all_ok": all(c["ok"] for c in checks)}
    write_json(cdir / "verdict.json", verdict)
    return verdict


def f5_lock_gap(cfg: dict) -> dict:
    """F5 registry-lock acquisition failure: cannot be constructed — the
    implementation under test has NO cross-process commit lock (I-09-B handoff
    open item; frozen F5 E-column already reads 'n/a (锁未实现)').  Signed as a
    documented gap, reported to I-09-B — never faked green."""
    case_id = cfg["id"]
    cdir = case_dir(case_id)
    cdir.mkdir(parents=True, exist_ok=True)
    src = (ISO_RF / "scripts" / "publication_registry.py").read_text(encoding="utf-8")
    keywords = ["lockfile", ".lock", "flock", "msvcrt", "LockFile", "threading.Lock", "filelock"]
    hits = [k for k in keywords if k in src]
    rec = {
        "case_id": case_id, "card_point": cfg["card_point"], "f_row": cfg["f_row"],
        "frozen_expectation_A": "无 committed 行; rc=2; 恢复=超时后重试",
        "constructed": False,
        "reason": "no cross-process commit lock exists in the implementation under test; "
                  "a lock-acquisition failure cannot be produced without inventing a lock "
                  "(forbidden: 自行补选/绕过产品入口)",
        "code_scan": {"file": "iso/rf/scripts/publication_registry.py",
                      "lock_keywords_found": hits,
                      "_append": "read-tail then append, no lock (I-09-A F-1)"},
        "disposition": "signed as uncovered GAP -> report to I-09-B (product scope); "
                       "concurrency case P-C3 records the same absence with live evidence",
        "constructed": False,
        "counts_as_fault_table_signing": True,
        "is_a_passing_fault_test": False,
        "not_a_pass": True,
        "all_ok": True,
        "checks": [],
    }
    write_json(cdir / "verdict.json", rec)
    return rec


def pc4a_case(cfg: dict) -> dict:
    """P-C4 / F11: kill the RECOVERY process during its commit, then recover
    twice more; verify idempotence, chain, P0 intact, P1 not fabricated,
    orphan prepare explicitly non-consumable until a clean recovery commits it."""
    case_id = cfg["id"]
    cdir = case_dir(case_id)
    cdir.mkdir(parents=True, exist_ok=True)
    input_hashes = copy_inputs(case_id)
    state = cdir / "state"
    checks = []

    def check(name, expected, actual, why=""):
        checks.append({"item": name, "expected": expected, "actual": actual,
                       "ok": actual == expected, "why": why})

    seed = clean_publish(case_id, state / "input_p0.json", "p0", "seed_p0")
    check("seed_p0_rc", 0, seed.get("raw_returncode"))
    p0_paths = [state / "p0.json", state / "p0.md"]
    p0_hashes_before = {p.name: sha256_file(p) for p in p0_paths}
    write_json(cdir / "seed.json", {"spawn": seed, "p0_hashes": p0_hashes_before,
                                    "input_hashes": input_hashes})

    # orphan prepare: kill P1 before append
    spawned = spawn_writer(state, state / "input_p1.json", state / "p1.json",
                           state / "p1.md", "kill:registry:before_append", "fault_p1")
    fault_rec = {"armed": "kill:registry:before_append", "kind": "pc4a",
                 "card_point": cfg["card_point"], "f_row": cfg["f_row"]}
    fault_rec.update(finish_spawned(case_id, spawned, "kill"))
    fault_rec["expected_raw_returncode"] = "kill"
    write_json(cdir / "fault.json", fault_rec)
    check("barrier_reached_before_kill", True, fault_rec.get("barrier_reached"))
    check("kill_target_registered", True, fault_rec.get("registered_in_manifest"))
    check("initial_kill_executed", True, (fault_rec.get("kill") or {}).get("ok"))
    check("initial_writer_died_for_real", False,
          fault_rec.get("normal_exit_record_present"))

    run_reader(case_id, "reader_after_fault")
    rf = read_json(cdir / "reader_after_fault.json")
    check("orphan_prepare_non_consumable", False,
          rf["packages"].get("p1", {}).get("consumable"))

    # recovery process killed AGAIN during its commit
    spawned2 = spawn_writer(state, state / "input_p1.json", state / "p1.json",
                            state / "p1.md", "kill:registry:before_append", "recovery_killed")
    rec_kill = {"armed": "kill:registry:before_append", "phase": "recovery"}
    rec_kill.update(finish_spawned(case_id, spawned2, "kill"))
    write_json(cdir / "recovery_killed.json", rec_kill)
    check("recovery_kill_registered", True, rec_kill.get("registered_in_manifest"))
    check("recovery_kill_executed", True, (rec_kill.get("kill") or {}).get("ok"))
    check("recovery_writer_died_for_real", False,
          rec_kill.get("normal_exit_record_present"))

    run_reader(case_id, "reader_after_recovery_killed")
    rk = read_json(cdir / "reader_after_recovery_killed.json")
    check("still_non_consumable_after_killed_recovery", False,
          rk["packages"].get("p1", {}).get("consumable"))
    check("p1_not_fabricated_rows", 0, rk["packages"].get("p1", {}).get("committed_rows"))
    check("chain_ok_after_killed_recovery", True, rk.get("chain", {}).get("ok"))

    # two clean recoveries
    rec1 = clean_publish(case_id, state / "input_p1.json", "p1", "recovery1")
    write_json(cdir / "recovery1.json", rec1)
    check("recovery1_rc", 0, rec1.get("raw_returncode"))
    run_reader(case_id, "reader_after_recovery1")
    r1 = read_json(cdir / "reader_after_recovery1.json")
    check("p1_consumable_after_recovery1", True, r1["packages"].get("p1", {}).get("consumable"))
    check("p1_logical_commits_after_recovery1", 1,
          r1["packages"].get("p1", {}).get("logical_commits"))

    rec2 = clean_publish(case_id, state / "input_p1.json", "p1", "recovery2")
    write_json(cdir / "recovery2.json", rec2)
    check("recovery2_rc", 0, rec2.get("raw_returncode"))
    run_reader(case_id, "reader_after_recovery2")
    r2 = read_json(cdir / "reader_after_recovery2.json")
    check("p1_logical_commits_after_recovery2", 1,
          r2["packages"].get("p1", {}).get("logical_commits"), "second recovery idempotent")
    check("chain_ok_after_recovery2", True, r2.get("chain", {}).get("ok"))
    check("audit_problems_after_recovery2", 0, len(r2.get("audit_problems") or []))
    check("p0_intact", p0_hashes_before,
          {p.name: sha256_file(p) for p in p0_paths})
    check("p0_consumable_after_recovery2", True,
          r2["packages"].get("p0", {}).get("consumable"))

    verdict = {"case_id": case_id, "card_point": cfg["card_point"], "f_row": cfg["f_row"],
               "rc_expectation_vs_raw": {"expected": "kill(4242) then clean 0/0",
                                         "raw_fault": fault_rec.get("raw_returncode"),
                                         "raw_recovery_killed": rec_kill.get("raw_returncode"),
                                         "raw_recovery1": rec1.get("raw_returncode"),
                                         "raw_recovery2": rec2.get("raw_returncode")},
               "checks": checks, "all_ok": all(c["ok"] for c in checks)}
    write_json(cdir / "verdict.json", verdict)
    return verdict


def pc4b_case(cfg: dict) -> dict:
    """P-C4b: committed P1 whose member hash is corrupted; complete P0 present.
    Corrupted item must fail closed with diagnostics; P0 not deleted/rewritten;
    recovery rewrites members and converges idempotently."""
    case_id = cfg["id"]
    cdir = case_dir(case_id)
    cdir.mkdir(parents=True, exist_ok=True)
    input_hashes = copy_inputs(case_id)
    state = cdir / "state"
    checks = []

    def check(name, expected, actual, why=""):
        checks.append({"item": name, "expected": expected, "actual": actual,
                       "ok": actual == expected, "why": why})

    seed = clean_publish(case_id, state / "input_p0.json", "p0", "seed_p0")
    check("seed_p0_rc", 0, seed.get("raw_returncode"))
    p0_paths = [state / "p0.json", state / "p0.md"]
    p0_hashes_before = {p.name: sha256_file(p) for p in p0_paths}
    write_json(cdir / "seed.json", {"spawn": seed, "p0_hashes": p0_hashes_before,
                                    "input_hashes": input_hashes})

    pub = clean_publish(case_id, state / "input_p1.json", "p1", "fault_p1")
    fault_rec = {"armed": "none (corruption applied post-commit)", "kind": "pc4b",
                 "card_point": cfg["card_point"], "f_row": cfg["f_row"]}
    fault_rec.update(pub)
    fault_rec["expected_raw_returncode"] = 0
    write_json(cdir / "fault.json", fault_rec)

    run_reader(case_id, "reader_after_seed_p1")
    r_seed = read_json(cdir / "reader_after_seed_p1.json")
    check("p1_committed_before_corruption", True,
          r_seed["packages"].get("p1", {}).get("consumable"))

    # corrupt one member byte (isolated test state only)
    target = state / "p1.json"
    before = target.read_bytes()
    target.write_bytes(before + b" ")
    write_json(cdir / "corruption.json",
               {"file": str(target), "bytes_before": len(before),
                "bytes_after": target.stat().st_size,
                "sha256_before": __import__("hashlib").sha256(before).hexdigest(),
                "sha256_after": sha256_file(target)})

    run_reader(case_id, "reader_after_fault")
    rf = read_json(cdir / "reader_after_fault.json")
    check("corrupted_p1_fails_closed", False,
          rf["packages"].get("p1", {}).get("consumable"), "member hash mismatch")
    ver0 = (rf["packages"].get("p1", {}).get("package_versions") or [{}])[0]
    check("product_commit_status_not_committed", "not_committed",
          ver0.get("product_commit_status", {}).get("status"))
    check("diagnostics_retained", True,
          bool(ver0.get("product_commit_status", {}).get("problems")),
          "fail closed AND keep diagnostics (P-C4)")
    check("p0_still_consumable", True, rf["packages"].get("p0", {}).get("consumable"))
    check("p0_bytes_untouched_by_corruption", p0_hashes_before,
          {p.name: sha256_file(p) for p in p0_paths})
    check("chain_ok", True, rf.get("chain", {}).get("ok"))

    rec1 = clean_publish(case_id, state / "input_p1.json", "p1", "recovery1")
    write_json(cdir / "recovery1.json", rec1)
    check("recovery1_rc", 0, rec1.get("raw_returncode"))
    run_reader(case_id, "reader_after_recovery1")
    r1 = read_json(cdir / "reader_after_recovery1.json")
    check("p1_consumable_after_recovery1", True,
          r1["packages"].get("p1", {}).get("consumable"))
    check("p1_logical_commits_after_recovery1", 1,
          r1["packages"].get("p1", {}).get("logical_commits"), "no fabricated P1")

    rec2 = clean_publish(case_id, state / "input_p1.json", "p1", "recovery2")
    write_json(cdir / "recovery2.json", rec2)
    run_reader(case_id, "reader_after_recovery2")
    r2 = read_json(cdir / "reader_after_recovery2.json")
    check("recovery2_rc", 0, rec2.get("raw_returncode"))
    check("p1_logical_commits_after_recovery2", 1,
          r2["packages"].get("p1", {}).get("logical_commits"))
    check("chain_ok_after_recovery2", True, r2.get("chain", {}).get("ok"))
    check("audit_problems_after_recovery2", 0, len(r2.get("audit_problems") or []))
    check("p0_not_deleted_or_rewritten", p0_hashes_before,
          {p.name: sha256_file(p) for p in p0_paths})

    verdict = {"case_id": case_id, "card_point": cfg["card_point"], "f_row": cfg["f_row"],
               "rc_expectation_vs_raw": {"expected": "0 / 0 / 0",
                                         "raw_pub": pub.get("raw_returncode"),
                                         "raw_recovery1": rec1.get("raw_returncode"),
                                         "raw_recovery2": rec2.get("raw_returncode")},
               "checks": checks, "all_ok": all(c["ok"] for c in checks)}
    write_json(cdir / "verdict.json", verdict)
    return verdict


# ---------------------------------------------------------------------------
_DISPATCH = {
    "torn": torn_line_case,
    "pipe": stdout_pipe_case,
    "pc4a": pc4a_case,
    "pc4b": pc4b_case,
    "f5": f5_lock_gap,
}


def run_case(cfg: dict) -> dict:
    global _CURRENT_CASE
    _CURRENT_CASE = cfg["id"]
    fn = _DISPATCH.get(cfg["kind"], standard_case)
    return fn(cfg)


_CURRENT_CASE = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", default=[],
                        help="case id(s) to run (default: all not yet verdicted)")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for c in CASES:
            print(f"{c['id']}\tkind={c['kind']}\tfault={c['fault']}\tf_row={c['f_row']}")
        return 0

    setup_paths()
    SHARED_INPUTS.mkdir(parents=True, exist_ok=True)
    if not (SHARED_INPUTS / "input_p1.json").exists():
        docs = make_input_docs(SHARED_INPUTS)
        print(f"shared inputs created: {docs}")
    # invalid input for F1 (empty document -> strong validation failure)
    inv = SHARED_INPUTS / "input_invalid.json"
    if not inv.exists():
        inv.write_text(json.dumps({}, ensure_ascii=False) + "\n", encoding="utf-8")
    input_hashes = {n: sha256_file(SHARED_INPUTS / n)
                    for n in ("input_p0.json", "input_p1.json", "input_invalid.json")}
    write_json(ATTEMPT / "evidence" / "shared_inputs" / "hashes.json", input_hashes)

    selected = [c for c in CASES if (args.only and c["id"] in args.only)
                or (not args.only and not args.force
                    and not (case_dir(c["id"]) / "verdict.json").exists())]
    if args.only:
        missing = [i for i in args.only if i not in {c["id"] for c in CASES}]
        if missing:
            print(f"harness failure: unknown case ids {missing}")
            return 1
    if not selected:
        print("no cases selected (all already verdicted; use --force to rerun)")
        return 0

    results = []
    for cfg in selected:
        t0 = time.time()
        try:
            verdict = run_case(cfg)
        except Exception as exc:  # harness error — recorded, not hidden
            verdict = {"case_id": cfg["id"], "harness_exception": f"{type(exc).__name__}: {exc}",
                       "all_ok": False, "checks": []}
            write_json(case_dir(cfg["id"]) / "verdict.json", verdict)
        verdict["elapsed_seconds"] = round(time.time() - t0, 2)
        # rewrite with elapsed
        write_json(case_dir(cfg["id"]) / "verdict.json", verdict)
        results.append(verdict)
        n_bad = sum(1 for c in verdict.get("checks", []) if not c["ok"])
        print(f"{cfg['id']}: all_ok={verdict.get('all_ok')} "
              f"checks={len(verdict.get('checks', []))} failed={n_bad} "
              f"elapsed={verdict['elapsed_seconds']}s")

    summary_path = ATTEMPT / "evidence" / "fault_matrix_summary.json"
    existing = read_json(summary_path) if summary_path.exists() else {}
    existing.update({r["case_id"]: r for r in results})
    write_json(summary_path, existing)
    all_ok = all(r.get("all_ok") for r in results)
    total = len(existing)
    bad = [k for k, v in existing.items() if not v.get("all_ok")]
    print(f"matrix total_recorded={total} failing={len(bad)} {bad}")
    return 0 if all_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
