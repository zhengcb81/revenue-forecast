"""I-14-E-APPLY: campaign v2 per-run driver (frozen in ``oracle-addendum-C.md``).

Owner ruling: OWNER_DECISIONS.md section 16, E-2 = "re-run", executed as
"shrink to 4 arms + persist after every run".  This driver replaces v1's
per-arm ``run_bench.py`` batching for the v2 campaign only; v1's harness, arm
logs and bench-*.json files are disclosed history and are never opened for
writing here (v2 logs to ``after/campaign_v2.log``).

Arms (22 pytest node invocations total, frozen in addendum C2):

  A1-fixed-quiet     fixed tree (T0/T0b interleaved), quiet, N=6, expect PASS
  A2-fixed-cpu8      fixed tree, +8 CPU burners,       N=6, expect PASS   <- the card
  A3-nonvacuity      non-vacuity node, quiet N=2 + cpu8 N=2, expect PASS
                     (PASS = the genuinely hung child WAS caught by the
                      derived timeout; RED would mean the watchdog never
                      fired -> oracle.md section 5 says report blocked)
  A4-mutant05-cpu8   mutant-derivation-0.5 tree, +8 CPU burners, N=6,
                     expect RED (the test fails again -> fix is load-bearing)

Persistence contract (addendum C3), per run and in this order:
  run -> collect events/derivation -> reap known pids -> archive basetemp ->
  APPEND one JSON line to after/campaign_v2.jsonl (flush+fsync) ->
  atomically rewrite after/campaign_v2-index.json from the JSONL.
An interruption can therefore lose at most the one in-flight run, and a
re-run skips every (arm, run) already present in the JSONL.

Basetemp retention (addendum C4, CF-I14F-X1): every run executes with a SHORT
explicit basetemp under %TEMP%\\i14eapply-v2\\<arm>-rNN\\pytest (execution path
~70 chars + the node's measured 125-char suffix stays below the 240/241
path-degradation onset), then the whole run root is COPIED into
after/campaign_v2-basetemps/<arm>-rNN and never deleted.  There is no rmtree
of any basetemp by this driver: each run gets its own fresh directory, which
pytest alone clears at that run's start.

Usage:
  python run_campaign_v2.py --plan-only          # expand the frozen plan, run nothing
  python run_campaign_v2.py                      # run everything not yet in the JSONL
  python run_campaign_v2.py --only-arm A3-...    # restrict to one arm (still skips done)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_v2 import Load  # noqa: E402
from run_bench import (collect_events, load_probe, measured_derivation,  # noqa: E402
                       reap, sweep_leftovers)

ATT = Path(__file__).resolve().parents[1]
AFTER = ATT / "after"
PY = ATT / "iso" / "venv" / "Scripts" / "python.exe"
SUITE_NAME = "test_source_catalog_worker_bootstrap.py"
SUITE_REL = Path("tests") / "contract" / SUITE_NAME

TREE_ROOTS = {
    "T0": ATT / "iso" / "T0",
    "T0b": ATT / "iso" / "T0b",
    "M05": ATT / "iso" / "mutant-derivation-0.5",
}
NODES = {
    "child_without_runtime": "test_child_without_runtime_session_is_terminated_and_restarted",
    "non_vacuity": "test_derived_hang_timeout_still_terminates_a_genuinely_hung_child",
}

GUARD_SECONDS = 180.0            # addendum C5: hard guard for one pytest run
BURNERS = 8                      # addendum C2/C5: same shape as I-14-E and v1
BURNER_EXPIRY = GUARD_SECONDS + 120.0  # self-expiring (= 300 s) even if the driver is
                                       # killed before its finally block can run

JSONL = AFTER / "campaign_v2.jsonl"
INDEX = AFTER / "campaign_v2-index.json"
SUMMARY = AFTER / "campaign_v2-summary.json"
LOG = AFTER / "campaign_v2.log"
CAPTURES = AFTER / "campaign_v2-captures"
ARTIFACTS = AFTER / "campaign_v2-artifacts"      # FLAT per-run copies (short paths)
ARCHIVES = AFTER / "campaign_v2-basetemps"       # byte-perfect zips of the run roots
TEMP_ROOT = Path(os.environ.get("TEMP", ".")) / "i14eapply-v2"
SCHEMA = "i14eapply-campaign-v2/1"

# oracle-addendum-B (I-14-E) B1 discrimination set: these files' presence/absence
# separates "path causation" from "load causation" for this node.
KEY_FILES = (
    "worker_launcher_events.jsonl",
    "worker_launcher.lock",
    "worker_control.json",
    "worker_runtime.json",
    "fake_worker_count.txt",
    "fake_behaviors.json",
    "hang_timeout_derivation.json",
)
MAX_FLAT_BYTES = 128 * 1024      # flatten small files only; big ones live in the zip
MAX_SHA_BYTES = 1024 * 1024


def _interleaved(conditions: list[str], trees: list[str]) -> list[tuple[str, str]]:
    """(condition, tree) per run index, T0/T0b interleaved as frozen in C2."""
    return list(zip(conditions, trees))


ARMS: list[dict] = [
    {
        "arm": "A1-fixed-quiet",
        "node": "child_without_runtime",
        "expect": "passed",
        "why": "R2' = 6/6 quiet no-regression for the applied fix",
        "plan": _interleaved(["quiet"] * 6, ["T0", "T0b", "T0", "T0b", "T0", "T0b"]),
    },
    {
        "arm": "A2-fixed-cpu8",
        "node": "child_without_runtime",
        "expect": "passed",
        "why": "R1' = 6/6 under +8 CPU burners - the entire purpose of the card "
               "(the v1-era band failed under load)",
        "plan": _interleaved(["cpu"] * 6, ["T0", "T0b", "T0", "T0b", "T0", "T0b"]),
    },
    {
        "arm": "A3-nonvacuity",
        "node": "non_vacuity",
        "expect": "passed",
        "why": "R3' anti-vacuity: PASS means the genuinely hung child WAS caught by "
               "the derived timeout (watchdog fired, child_started == 3); RED means "
               "the derived timeout never fired -> oracle.md section 5 => blocked",
        "plan": _interleaved(["quiet", "quiet", "cpu", "cpu"], ["T0", "T0b", "T0", "T0b"]),
    },
    {
        "arm": "A4-mutant05-cpu8",
        "node": "child_without_runtime",
        "expect": "failed",
        "why": "R4' mutation proof: reverting the derivation to the fixed 0.5 s must "
               "go RED again under the same load (fix is load-bearing)",
        "plan": _interleaved(["cpu"] * 6, ["M05", "M05", "M05", "M05", "M05", "M05"]),
    },
]
PLANNED_TOTAL = sum(len(a["plan"]) for a in ARMS)   # 6 + 6 + 4 + 6 = 22


def say(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def machine_probe() -> dict | None:
    """Load percentage + free RAM, measured AFTER burner warmup (C5)."""
    query = ("$p = (Get-CimInstance Win32_Processor | Select-Object -First 1 "
             "-ExpandProperty LoadPercentage); $o = Get-CimInstance Win32_OperatingSystem; "
             "Write-Output ('load_pct=' + $p); "
             "Write-Output ('free_mb=' + [math]::Round($o.FreePhysicalMemory/1024,1))")
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", query],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out: dict = {}
    for line in proc.stdout.splitlines():
        key, _, value = line.strip().partition("=")
        if key in ("load_pct", "free_mb") and value:
            try:
                out[key] = float(value)
            except ValueError:
                out[key] = value
    return out or None


def verdict_of(text: str, timed_out: bool, rc: int | None) -> str:
    # the guard outcome wins: if our 180 s guard killed pytest, no final tally
    # line can have been printed by a finished session.
    if timed_out:
        return "timeout"
    if "1 passed" in text:
        return "passed"
    if "1 failed" in text:
        return "failed"
    if rc not in (0, 1):
        return "error"
    return "unknown"


def first_assertion(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("E   "):
            return line.strip()[:220]
    return ""


def dir_stats(root: Path) -> dict:
    files = 0
    total = 0
    longest = ""
    for path in root.rglob("*"):
        try:
            if path.is_file():
                files += 1
                total += path.stat().st_size
                text = str(path)
                if len(text) > len(longest):
                    longest = text
        except OSError:
            continue
    return {"files": files, "bytes": total,
            "longest_path_chars": len(longest), "longest_path": longest}


def sha256_small(path: Path, limit: int = MAX_SHA_BYTES) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def package_artifacts(run_root: Path, run_id: str) -> dict:
    """Basetemp retention, addendum C4 (revised before any v2 run).

    A plain ``Copy-Item -Recurse`` of a run root into ``after/`` was measured to
    exceed Windows MAX_PATH (260): the deepest executed artifact sits ~308 chars
    below ``after/``, so a naive tree copy dies with "Could not find a part of
    the path" - i.e. it would destroy exactly the artifact-absence evidence
    CF-I14F-X1 requires.  Therefore retention is done three ways, none of which
    can be broken by path length:

      1. per-file manifest (rel path, executed absolute path + char count,
         bytes, sha256 for files <= 1 MiB)  -> stored IN the JSONL line;
      2. FLAT copies of every file <= 128 KiB under
         ``after/campaign_v2-artifacts/<run_id>/<idx>.<basename>``  (short,
         universally readable; idx -> rel path mapping lives in the manifest);
      3. a byte-perfect ZIP of the whole run root (directory structure
         preserved) at ``after/campaign_v2-basetemps/<run_id>.zip``.

    The executed tree itself in %TEMP% is never deleted either.
    """
    files = [p for p in sorted(run_root.rglob("*")) if p.is_file()]
    flat_dir = ARTIFACTS / run_id
    if flat_dir.exists():
        shutil.rmtree(flat_dir, ignore_errors=True)
    flat_dir.mkdir(parents=True, exist_ok=True)
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    zip_path = ARCHIVES / f"{run_id}.zip"
    if zip_path.exists():
        zip_path.unlink()

    entries: list[dict] = []
    key_files: dict[str, dict] = {}
    worker_logs = {"stdout": [], "stderr": []}
    flat_files = 0
    flat_errors: list[str] = []
    total_bytes = 0
    longest = ""
    for index, path in enumerate(files, 1):
        rel = str(path.relative_to(run_root))
        text = str(path)
        try:
            size = path.stat().st_size
        except OSError:
            size = None
        if size:
            total_bytes += size
        if len(text) > len(longest):
            longest = text
        entry = {"idx": index, "rel": rel, "path": text,
                 "path_chars": len(text), "bytes": size,
                 "sha256": sha256_small(path)}
        entries.append(entry)
        is_asserted = "hang-timeout-warmup" not in path.parts
        base = path.name
        if is_asserted and base in KEY_FILES and base not in key_files:
            key_files[base] = dict(entry, present=True)
        if is_asserted and base.startswith("worker_stdout-"):
            worker_logs["stdout"].append(base)
        if is_asserted and base.startswith("worker_stderr-"):
            worker_logs["stderr"].append(base)
        if size is not None and size <= MAX_FLAT_BYTES:
            try:
                shutil.copyfile(path, flat_dir / f"{index:03d}.{base}")
                flat_files += 1
            except OSError as exc:
                flat_errors.append(f"{rel}: {type(exc).__name__}: {exc}")

    for name in KEY_FILES:
        key_files.setdefault(name, {"present": False, "rel": None, "path": None,
                                    "path_chars": None, "bytes": None,
                                    "sha256": None})

    zip_error = None
    zip_entries = 0
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in files:
                zf.write(path, str(path.relative_to(run_root)))
                zip_entries += 1
    except (OSError, zipfile.BadZipFile) as exc:
        zip_error = f"{type(exc).__name__}: {exc}"

    return {
        "root": str(run_root), "root_chars": len(str(run_root)),
        "files_total": len(files), "bytes_total": total_bytes,
        "longest_path": longest, "longest_path_chars": len(longest),
        "manifest": entries,
        "key_files": key_files,
        "worker_log_files": worker_logs,
        "flat_dir": str(flat_dir), "flat_files": flat_files,
        "flat_errors": flat_errors,
        "zip": str(zip_path), "zip_bytes": (zip_path.stat().st_size
                                            if zip_path.exists() else None),
        "zip_entries": zip_entries, "zip_error": zip_error,
        "zip_covers_all_files": zip_entries == len(files),
        "executed_tree_deleted": False,
    }


def load_done() -> set[tuple[str, int]]:
    done: set[tuple[str, int]] = set()
    if not JSONL.exists():
        return done
    for line in JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue
        done.add((record.get("arm", ""), int(record.get("run", 0))))
    return done


def append_record(record: dict) -> None:
    AFTER.mkdir(parents=True, exist_ok=True)
    with JSONL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def rebuild_index(extra: dict | None = None) -> dict:
    """Rebuild after/campaign_v2-index.json from the JSONL (never ahead of it)."""
    arms = {arm["arm"]: {"planned": len(arm["plan"]), "expect": arm["expect"],
                         "recorded": 0, "passed": 0, "failed": 0, "timeout": 0,
                         "error": 0, "unknown": 0, "as_expected": 0,
                         "not_as_expected": 0,
                         "runs_as_expected": [], "runs_not_as_expected": []}
            for arm in ARMS}
    total = 0
    torn = 0
    last: dict | None = None
    raw_bytes = 0
    if JSONL.exists():
        raw_bytes = JSONL.stat().st_size
        for line in JSONL.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except ValueError:
                torn += 1
                continue
            total += 1
            last = record
            entry = arms.setdefault(record.get("arm", "?"),
                                    {"planned": 0, "expect": None, "recorded": 0,
                                     "passed": 0, "failed": 0, "timeout": 0,
                                     "error": 0, "unknown": 0, "as_expected": 0,
                                     "not_as_expected": 0, "runs_as_expected": [],
                                     "runs_not_as_expected": []})
            outcome = record.get("outcome", "unknown")
            entry["recorded"] += 1
            entry[outcome] = entry.get(outcome, 0) + 1
            bucket = ("runs_as_expected" if record.get("as_expected")
                      else "runs_not_as_expected")
            entry[bucket].append(record.get("run"))
            entry["as_expected" if record.get("as_expected")
                  else "not_as_expected"] += 1
    payload = {
        "schema": SCHEMA, "campaign": "v2",
        "oracle": "oracle-addendum-C.md (frozen 2026-09-22T07:31:56Z)",
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "jsonl": "after/campaign_v2.jsonl",
        "jsonl_lines_parseable": total,
        "jsonl_lines_torn": torn,
        "jsonl_bytes": raw_bytes,
        "planned_total": PLANNED_TOTAL,
        "recorded_total": total,
        "arms": arms,
        "last_record": (None if last is None else {
            "arm": last.get("arm"), "run": last.get("run"),
            "outcome": last.get("outcome"), "condition": last.get("condition"),
            "wall_seconds": last.get("wall_seconds"),
            "ended_utc": last.get("ended_utc")}),
        "persistence": "index rewritten atomically after every JSONL append; "
                       "rebuilt from the JSONL on start",
    }
    if extra:
        payload.update(extra)
    tmp = INDEX.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, INDEX)
    return payload


def execute_run(arm: dict, run_index: int, condition: str, tree: str) -> dict:
    arm_name = arm["arm"]
    node_key = arm["node"]
    run_id = f"{arm_name}-r{run_index:02d}"
    tree_root = TREE_ROOTS[tree]
    suite = tree_root / SUITE_REL
    launcher = tree_root / "scripts" / "source_catalog_worker.ps1"
    if not suite.exists() or not PY.exists():
        raise SystemExit(f"missing SUT or interpreter: {suite} / {PY}")

    run_root = TEMP_ROOT / run_id
    basetemp = run_root / "pytest"
    cwd = run_root / "cwd"
    if run_root.exists():
        shutil.rmtree(run_root, ignore_errors=True)
    cwd.mkdir(parents=True, exist_ok=True)
    CAPTURES.mkdir(parents=True, exist_ok=True)
    ARCHIVES.mkdir(parents=True, exist_ok=True)

    # sweep only OUR v2 root (addendum C5): never other sessions' processes
    swept_before = sweep_leftovers(TEMP_ROOT)

    load = Load(condition, BURNERS, BURNER_EXPIRY)
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    load_started = False
    timed_out = False
    rc: int | None = None
    text = ""
    machine = None
    probe: dict | None = None
    argv_pytest: list[str] | None = None
    t0 = time.perf_counter()
    try:
        load.start()
        load_started = True
        machine = machine_probe()
        probe = load_probe()
        env = {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUTF8": "1",
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "TEMP": os.environ.get("TEMP", ""),
            "TMP": os.environ.get("TMP", ""),
            "PYTHONPATH": str(tree_root / "tests" / "contract"),
        }
        argv_pytest = [str(PY), "-X", "utf8", "-B", "-m", "pytest",
                       "-p", "no:cacheprovider",
                       "--basetemp", str(basetemp),
                       "-q", f"{suite}::{NODES[node_key]}"]
        try:
            proc = subprocess.run(argv_pytest, cwd=str(cwd), env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=GUARD_SECONDS)
            rc = proc.returncode
            text = proc.stdout.decode("utf-8", "replace")
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            rc = None
            text = (exc.stdout or b"").decode("utf-8", "replace")
    finally:
        wall = time.perf_counter() - t0
        if load_started:
            load.stop()

    ended_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    outcome = verdict_of(text, timed_out, rc)
    assertion = first_assertion(text)

    capture = CAPTURES / f"{run_id}.txt"
    capture.write_text(text, encoding="utf-8")

    events = collect_events(run_root)
    derivation = measured_derivation(run_root)
    reaped = reap([events.get("launcher_pid")] +
                  [a.get("child_pid") for a in events.get("attempts", [])])
    swept_after_timeout: list[int] = []
    if timed_out:
        swept_after_timeout = sweep_leftovers(run_root)
    if reaped:
        events["reaped_pids"] = reaped
    if swept_after_timeout:
        events["swept_after_guard_timeout"] = swept_after_timeout
    if events.get("events_present"):
        shutil.copyfile(events["events_path"], CAPTURES / f"{run_id}-launcher-events.jsonl")
    if derivation.get("report_present"):
        shutil.copyfile(derivation["report_path"], CAPTURES / f"{run_id}-derivation.json")

    # ---- basetemp retention (addendum C4): package FIRST, then persist ----
    pkg = package_artifacts(run_root, run_id)
    archived = bool(pkg["zip"]) and pkg["zip_error"] is None
    archive_error = pkg["zip_error"] or (
        "; ".join(pkg["flat_errors"]) if pkg["flat_errors"] else None)

    as_expected = (outcome == arm["expect"])
    record = {
        "schema": SCHEMA, "campaign": "v2", "arm": arm_name, "run": run_index,
        "arm_expect": arm["expect"], "as_expected": as_expected,
        "node": node_key, "node_name": NODES[node_key],
        "condition": condition, "tree": tree,
        "suite": str(suite), "suite_sha256": sha256(suite),
        "launcher_sha256": sha256(launcher) if launcher.exists() else None,
        "outcome": outcome, "returncode": rc,
        "guard_seconds": GUARD_SECONDS, "guard_triggered": timed_out,
        "wall_seconds": round(wall, 3),
        "started_utc": started_utc, "ended_utc": ended_utc,
        "assertion": assertion,
        "basetemp_path": str(basetemp),
        "basetemp_archive": pkg["zip"],
        "basetemp_artifacts_dir": pkg["flat_dir"],
        "basetemp_archived": archived,
        "basetemp_archive_error": archive_error,
        "basetemp_files": pkg["files_total"], "basetemp_bytes": pkg["bytes_total"],
        "basetemp_longest_path_chars": pkg["longest_path_chars"],
        "basetemp_longest_path": pkg["longest_path"],
        "basetemp_zip_entries": pkg["zip_entries"],
        "basetemp_zip_covers_all_files": pkg["zip_covers_all_files"],
        "basetemp_flat_files": pkg["flat_files"],
        "basetemp_executed_tree_deleted": pkg["executed_tree_deleted"],
        "artifacts": pkg,
        "capture": str(capture),
        "events": {
            "events_present": events.get("events_present"),
            "events_path": events.get("events_path"),
            "child_started_count": events.get("child_started_count"),
            "child_unresponsive_count": events.get("child_unresponsive_count"),
            "watchdog_kill_uptimes": events.get("watchdog_kill_uptimes"),
            "watchdog_kill_reasons": events.get("watchdog_kill_reasons"),
            "hang_timeout_seconds_actually_used":
                events.get("hang_timeout_seconds_actually_used"),
            "child_poll_ms_actually_used": events.get("child_poll_ms_actually_used"),
            "launcher_pid": events.get("launcher_pid"),
            "reaped_pids": events.get("reaped_pids", []),
            "all_timelines_in_run": events.get("all_timelines_in_run", []),
        },
        "derivation": derivation,
        "load": load.describe(),
        "load_probe": probe,
        "machine_after_warmup": machine,
        "leftovers_swept_before": swept_before,
        "argv": argv_pytest,
    }
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-only", action="store_true",
                        help="print the frozen expansion and exit; runs nothing")
    parser.add_argument("--only-arm", default=None,
                        help="restrict to one arm name (still skips recorded runs)")
    args = parser.parse_args(argv)

    if args.plan_only:
        print(f"campaign v2 frozen plan: {len(ARMS)} arms, "
              f"{PLANNED_TOTAL} pytest node invocations")
        for arm in ARMS:
            print(f"  {arm['arm']}: node={arm['node']} expect={arm['expect']} "
                  f"N={len(arm['plan'])}")
            for i, (condition, tree) in enumerate(arm["plan"], 1):
                print(f"    run{i:02d} condition={condition:5s} tree={tree} "
                      f"suite={TREE_ROOTS[tree] / SUITE_REL}")
        return 0

    AFTER.mkdir(parents=True, exist_ok=True)
    done = load_done()
    rebuild_index({"note": "rebuilt on start from campaign_v2.jsonl"})
    say(f"CAMPAIGN V2 START planned={PLANNED_TOTAL} already_recorded={len(done)} "
        f"fixed_suite_sha={sha256(TREE_ROOTS['T0'] / SUITE_REL)} "
        f"mutant_suite_sha={sha256(TREE_ROOTS['M05'] / SUITE_REL)} "
        f"guard={GUARD_SECONDS}s burners={BURNERS} "
        f"burner_expiry={BURNER_EXPIRY:.0f}s")

    failures = 0
    try:
        for arm in ARMS:
            if args.only_arm and arm["arm"] != args.only_arm:
                continue
            say(f"ARM {arm['arm']} START N={len(arm['plan'])} "
                f"expect={arm['expect']} node={arm['node']}")
            for run_index, (condition, tree) in enumerate(arm["plan"], 1):
                if (arm["arm"], run_index) in done:
                    say(f"  {arm['arm']} run{run_index} SKIP already in campaign_v2.jsonl")
                    continue
                record = execute_run(arm, run_index, condition, tree)
                # C3 order: persist the run BEFORE anything else can eat it
                append_record(record)
                index = rebuild_index()
                say(f"  {arm['arm']} run{run_index} {condition} {tree} "
                    f"outcome={record['outcome']} expected={record['as_expected']} "
                    f"wall={record['wall_seconds']}s "
                    f"hang={record['events']['hang_timeout_seconds_actually_used']} "
                    f"starts={record['events']['child_started_count']} "
                    f"kills={record['events']['child_unresponsive_count']} "
                    f"archived={record['basetemp_archived']}"
                    f"{(' assert=' + record['assertion']) if record['assertion'] else ''}")
                if not record["as_expected"]:
                    failures += 1
                done.add((arm["arm"], run_index))
            index = rebuild_index()   # also correct when every run of the arm was skipped
            say(f"ARM {arm['arm']} DONE tally="
                f"{json.dumps({k: v for k, v in index['arms'][arm['arm']].items() if not k.startswith('runs_')}, ensure_ascii=False)}")
    except KeyboardInterrupt:
        say("CAMPAIGN V2 INTERRUPTED (KeyboardInterrupt); records persisted so far "
            f"= {len(load_done())}/{PLANNED_TOTAL}")
        rebuild_index({"note": "interrupted; rebuilt from campaign_v2.jsonl"})
        return 1
    except Exception:
        say("CAMPAIGN V2 DRIVER ERROR:\n" + traceback.format_exc())
        rebuild_index({"note": "driver error; rebuilt from campaign_v2.jsonl"})
        return 1

    final = load_done()
    index = rebuild_index({"note": "all planned runs recorded"})
    complete = len(final) >= PLANNED_TOTAL
    summary = {
        "schema": SCHEMA, "campaign": "v2",
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "planned_total": PLANNED_TOTAL, "recorded_total": len(final),
        "complete": complete,
        "runs_not_as_expected": index["recorded_total"] - sum(
            a["as_expected"] for a in index["arms"].values()),
        "arms": {name: {k: v for k, v in data.items() if not k.startswith("runs_")}
                 for name, data in index["arms"].items()},
        "expectations_met": all(
            data["not_as_expected"] == 0 and data["recorded"] == data["planned"]
            for data in index["arms"].values()),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    say(f"CAMPAIGN V2 COMPLETE recorded={len(final)}/{PLANNED_TOTAL} "
        f"not_as_expected={summary['runs_not_as_expected']} "
        f"expectations_met={summary['expectations_met']}")
    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
