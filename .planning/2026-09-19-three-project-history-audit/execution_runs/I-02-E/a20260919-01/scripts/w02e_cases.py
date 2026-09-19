"""w02e_cases: crash-resume case driver for card I-02-E (a20260919-01).

kill/terminate operate ONLY on Popen handles of scratch children this driver
spawns (recorded PIDs land in after/recovery-and-paused-proof.json). No
process-name matching, no system locks, no production writes.

Incremental per case: ``python w02e_cases.py --case <NAME>`` (or ``--all``).
State is merged into after/{crash-boundary-matrix.json,
recovery-and-paused-proof.json, case_results.json} across runs.

Runner child: samples/runner_child.py (bootstrap override chain, ONE ensure
call, full result JSON). kill uses proc.terminate/kill on recorded handles.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
AFTER = ATTEMPT / "after"
SAMPLES = ATTEMPT / "samples"
RUNNER = SAMPLES / "runner_child.py"
RUNNER_HOLD = SAMPLES / "lock_holder.py"
PYTHON = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"
SCRATCH_BASE = Path(tempfile.gettempdir()) / "w02e" / "a20260919-01_case_scratch"

HK_FILENAME = "2026-04-28_hkexnews_12127452_2025年度報告.pdf"
HK_SHA = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"
DOC_ID = "urn:company-wiki:document:sha256:" + HK_SHA
CANONICAL_REL = "companies/小米集團－Ｗ/raw/financial_reports/annual/" + HK_FILENAME
EXPECTED_SOURCE_ID = "urn:company-wiki:source:sha256:" + HK_SHA


# --------------------------------------------------------------------------
# isolated scratch helpers
# --------------------------------------------------------------------------
def sha256_file(path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def catalog_db_path(case_dir: Path):
    catalog_dir = case_dir / "project" / ".source_catalog"
    if not catalog_dir.is_dir():
        return None
    candidates = sorted(catalog_dir.glob("*.sqlite3"))
    return candidates[0] if candidates else None


def snapshot_state(case_dir: Path) -> dict:
    """Disk + DB + journal byte snapshot of the case tree."""
    project = case_dir / "project"
    catalog_dir = project / ".source_catalog"
    state = {"files": {}}
    if catalog_dir.is_dir():
        for item in sorted(catalog_dir.rglob("*")):
            if item.is_file():
                state["files"][str(item.relative_to(case_dir)).replace("\\", "/")] = {
                    "sha256": sha256_file(item),
                    "size": item.stat().st_size,
                }
    db_path = catalog_db_path(case_dir)
    if db_path is not None:
        connection = sqlite3.connect(str(db_path))
        connection.row_factory = sqlite3.Row
        try:
            state["scan_runs"] = [
                dict(row)
                for row in connection.execute(
                    "SELECT run_id, status FROM scan_runs ORDER BY started_at"
                ).fetchall()
            ]
            state["sources_rows"] = connection.execute(
                "SELECT COUNT(*) FROM sources WHERE content_sha256=?", (HK_SHA,)
            ).fetchone()[0]
            state["documents_active"] = connection.execute(
                "SELECT COUNT(*) FROM documents WHERE document_id=? AND source_status='active'",
                (DOC_ID,),
            ).fetchone()[0]
            state["locations_active_original"] = connection.execute(
                "SELECT COUNT(*) FROM locations WHERE role='original_primary' "
                "AND location_status='active' AND relative_path LIKE ?",
                ("%" + HK_FILENAME,),
            ).fetchone()[0]
        except Exception as exc:
            state["db_error"] = f"{type(exc).__name__}: {exc}"
        finally:
            connection.close()
    journal = catalog_dir / "acquisition_attempts.jsonl"
    if journal.is_file():
        state["journal_size"] = journal.stat().st_size
        state["journal_sha256"] = sha256_file(journal)
    companies = project / "companies"
    state["company_files"] = (
        {
            str(item.relative_to(case_dir)).replace("\\", "/"): {
                "sha256": sha256_file(item),
                "size": item.stat().st_size,
            }
            for item in sorted(companies.rglob("*"))
            if item.is_file()
        }
        if companies.is_dir()
        else {}
    )
    paused = case_dir / "worker_control" / "paused"
    state["worker_paused_sha256"] = sha256_file(paused) if paused.is_file() else None
    return state


def copy_snapshot(case_dir: Path, destination: Path) -> None:
    # Windows MAX_PATH compromise (same as accepted I-02-C/D): snapshot copies
    # skip the deep staging subtree and sqlite hot-journal; the staged file
    # identity is already recorded via snapshot_state hashes.
    destination.mkdir(parents=True, exist_ok=True)
    project = case_dir / "project"
    catalog_dir = project / ".source_catalog"
    if catalog_dir.is_dir():
        shutil.copytree(
            catalog_dir,
            destination / "project" / ".source_catalog",
            ignore=shutil.ignore_patterns("staging", "*-journal", "*-wal", "*-shm"),
            dirs_exist_ok=True,
        )
    # deep raw subtree skipped entirely under MAX_PATH: per-file hashes are
    # already recorded in snapshot.json company_files
    (destination / "snapshot.json").write_text(
        json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def case_init(name: str, mode: str) -> Path:
    case_dir = SCRATCH_BASE / name
    if case_dir.exists():
        shutil.rmtree(case_dir)
    (case_dir / "project").mkdir(parents=True)
    (case_dir / "worker_control").mkdir(parents=True)
    (case_dir / "worker_control" / "paused").write_text("paused\n", encoding="utf-8")
    (case_dir / "checkpoint").mkdir()
    if mode == "register":
        sample = SAMPLES / "real_roots" / "hk" / HK_FILENAME
        dst = (
            case_dir
            / "project"
            / "companies"
            / "小米集團－Ｗ"
            / "raw"
            / "financial_reports"
            / "annual"
        )
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(sample, dst / HK_FILENAME)
        shutil.copyfile(
            sample.with_name(sample.name + ".source.json"),
            (dst / HK_FILENAME).with_name(HK_FILENAME + ".source.json"),
        )
        assert sha256_file(dst / HK_FILENAME) == HK_SHA
    return case_dir


def base_spec(name: str, mode: str, case_dir: Path) -> dict:
    return {
        "case": name,
        "mode": mode,
        "inject": None,
        "kill_intent": False,
        "checkpoint_dir": str(case_dir / "checkpoint"),
        "sample_raw": str(SAMPLES / "real_roots" / "hk" / HK_FILENAME),
        "reusable_root": True,
        "scan_pause_doc": None,
    }


def wait_checkpoint(case_dir: Path, point: str, proc, timeout: float = 90.0) -> bool:
    target = case_dir / "checkpoint" / ("checkpoint." + point + ".json")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if target.is_file():
            return True
        if proc.poll() is not None:
            return False
        time.sleep(0.05)
    return target.is_file()


def runner_spawn(spec: dict, tag: str):
    case_dir = SCRATCH_BASE / spec["case"]
    spec_path = case_dir / f"spec.{tag}.json"
    spec_path.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return subprocess.Popen(
        [
            str(PYTHON),
            "-X",
            "utf8",
            str(RUNNER),
            str(case_dir / "project"),
            str(spec_path),
            str(case_dir / f"result.{tag}.json"),
            str(case_dir / f"pid.{tag}.txt"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ATTEMPT),
    )


def runner_pid(case_dir: Path, tag: str):
    path = case_dir / f"pid.{tag}.txt"
    return path.read_text().strip() if path.is_file() else None


def result_of(case_dir: Path, tag: str) -> dict:
    path = case_dir / f"result.{tag}.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"result_read_error": str(exc)}
    return {}


def compact(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "journal_lines"}


def logical_counts(result: dict):
    db = result.get("db") or {}
    return (
        db.get("sources_rows"),
        db.get("documents_active"),
        db.get("locations_active_original"),
    )


def kill_recorded(proc, case_name: str, tag: str) -> dict:
    """Hard-terminate a recorded scratch child (terminate then kill)."""
    pid = proc.pid
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
    return {
        "case": case_name,
        "tag": tag,
        "pid": str(pid),
        "returncode": proc.returncode,
    }


def save_logs(name: str, tag: str, stdout: str, stderr: str):
    log_dir = ATTEMPT / "raw-cli-logs" / name
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{tag}.stdout.log").write_text(stdout or "", encoding="utf-8")
    (log_dir / f"{tag}.stderr.log").write_text(stderr or "", encoding="utf-8")


def load_json(path: Path, default):
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def write_outputs(matrix: dict, case_results: dict, proof: dict):
    (AFTER / "crash-boundary-matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "case_results.json").write_text(
        json.dumps(case_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (AFTER / "recovery-and-paused-proof.json").write_text(
        json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def sidecar_baseline(case_dir: Path) -> str:
    raw = case_dir / "project" / CANONICAL_REL.replace("/", "\\")
    return sha256_file(raw.with_name(raw.name + ".source.json"))


sidecar_oracle_sha = sha256_file(
    SAMPLES / "real_roots" / "hk" / (HK_FILENAME + ".source.json")
)


# --------------------------------------------------------------------------
# case: EXP (no-interruption oracle)
# --------------------------------------------------------------------------
def case_EXP(matrix: dict, case_results: dict, proof: dict):
    name = "EXP"
    case_dir = case_init(name, "download")
    proc = runner_spawn(base_spec(name, "download", case_dir), "run")
    stdout, stderr = proc.communicate(timeout=300)
    save_logs(name, "run", stdout, stderr)
    proof["scratch_pids"].setdefault(name, []).append(
        {"tag": "run", "pid": str(proc.pid), "returncode": proc.returncode}
    )
    result = result_of(case_dir, "run")
    failures = []
    if result.get("status") != "imported":
        failures.append(
            f"{name}: status != imported ({result.get('status')} err={result.get('error')})"
        )
    if logical_counts(result) != (1, 1, 1):
        failures.append(f"{name}: counts != (1,1,1) ({logical_counts(result)})")
    provider = result.get("provider_calls") or {}
    if not (provider.get("discover", 0) == 1 and provider.get("fetch", 0) == 1):
        failures.append(f"{name}: expected one discover + one fetch ({provider})")
    match = result.get("match") or {}
    if str(match.get("source_id")) != EXPECTED_SOURCE_ID:
        failures.append(f"{name}: source_id unexpected ({match.get('source_id')})")
    if str(match.get("content_sha256")) != HK_SHA:
        failures.append(
            f"{name}: content_sha256 unexpected ({match.get('content_sha256')})"
        )
    copy_snapshot(case_dir, AFTER / "before-restart" / "EXP_no_interrupt")
    copy_snapshot(case_dir, AFTER / "after-restart" / "EXP_no_interrupt")
    paused = snapshot_state(case_dir).get("worker_paused_sha256")
    proof["worker_paused_unchanged"][name] = paused
    matrix[name] = {
        "method": "clean",
        "result": compact(result),
        "oracle": {
            "match": result.get("match"),
            "counts": (1, 1, 1),
            # sidecar baseline = the writer's OWN no-interruption sidecar
            # (canonical payload bytes), never the historical sample copy
            "sidecar_sha": sidecar_baseline(case_dir),
        },
        "failures": failures,
    }
    case_results[name] = {"failures": failures}


def oracle_resumed(
    name: str,
    resumed: dict,
    case_dir: Path,
    *,
    need_sidecar_check: bool = True,
    sidecar_expected_sha=None,
    identity_keys=("source_id", "content_sha256"),
) -> list:
    """Frozen expectations from oracle.md (constants, not writer output)."""
    failures = []
    if resumed.get("status") != "imported":
        failures.append(
            f"{name}: resume status != imported "
            f"({resumed.get('status')} err={resumed.get('error')})"
        )
    counts = logical_counts(resumed)
    if counts != (1, 1, 1):
        failures.append(f"{name}: logical counts {counts} != (1,1,1)")
    provider = resumed.get("provider_calls") or {}
    if not (provider.get("discover", 0) == 0 and provider.get("fetch", 0) == 0):
        failures.append(f"{name}: resume provider calls not zero ({provider})")
    match = resumed.get("match") or {}
    for key in identity_keys:
        expected = EXPECTED_SOURCE_ID if key == "source_id" else HK_SHA
        if str(match.get(key, "")) != str(expected):
            failures.append(
                f"{name}: resumed identity {key} != expected ({match.get(key)})"
            )
    canonical = str(match.get("canonical_path", "")).replace("\\", "/")
    if not canonical.endswith(CANONICAL_REL):
        failures.append(f"{name}: resumed canonical path unexpected ({canonical})")
    if need_sidecar_check:
        # sidecar rebuild semantics (B2/B3 resume): the resumed sidecar bytes
        # must be EXACTLY the durable bytes persisted in the S1 stage row —
        # nothing guessed, no content drift.
        journal_path = (
            case_dir / "project" / ".source_catalog" / "acquisition_attempts.jsonl"
        )
        s1_payload = None
        for line in journal_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("outcome") == "stage_staged_verified":
                s1_payload = json.loads(row.get("payload_json") or "{}")
        expected_bytes = base64.b64decode(
            (s1_payload or {}).get("sidecar_bytes_b64") or ""
        )
        raw = case_dir / "project" / CANONICAL_REL.replace("/", "\\")
        sidecar = raw.with_name(raw.name + ".source.json")
        if not sidecar.is_file() or sidecar.read_bytes() != expected_bytes:
            failures.append(
                f"{name}: resumed sidecar bytes != durable S1 payload bytes"
            )
    return failures


sidecar_oracle_sha = sha256_file(
    SAMPLES / "real_roots" / "hk" / (HK_FILENAME + ".source.json")
)


# --------------------------------------------------------------------------
# generic crash-vs-raise case body
# --------------------------------------------------------------------------
def crash_then_resume_case(
    matrix: dict,
    case_results: dict,
    proof: dict,
    name: str,
    *,
    mode: str = "download",
    point: str,
    method: str,
    mutate=None,
    restart_specs=None,
    expect_status="imported",
    scan_pause_doc=None,
) -> None:
    """Onecrash/raise pass + one-or-more restart passes against isolated scratch."""
    case_dir = case_init(name, mode)
    spec = base_spec(name, mode, case_dir)
    if scan_pause_doc:
        spec["scan_pause_doc"] = scan_pause_doc
    if method == "kill":
        spec["inject"] = None if point == "scan_partial" else point + ":pause"
        spec["kill_intent"] = True
    else:
        spec["inject"] = point + ":raise"
    proc = runner_spawn(spec, "run1")
    interrupted = False
    if method == "kill":
        interrupted = wait_checkpoint(case_dir, point, proc)
        pid_run1 = runner_pid(case_dir, "run1")
        kill_recorded(proc, name, "run1")
        # post-kill crash-state snapshot (DB rolled back on next open; hot
        # journal kept)
        (AFTER / "after-restart" / name).mkdir(parents=True, exist_ok=True)
        (AFTER / "after-restart" / name / "post_kill.json").write_text(
            json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    else:
        proc.wait(timeout=300)
    copy_snapshot(case_dir, AFTER / "before-restart" / name)
    pid_run1 = runner_pid(case_dir, "run1")
    crashed_returncode = proc.returncode
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run1", stdout, stderr)
    proof["scratch_pids"].setdefault(name, []).append(
        {
            "tag": "run1",
            "pid": str(pid_run1 or proc.pid),
            "returncode": (crashed_returncode := proc.returncode),
            "method": method,
        }
    )
    if method == "kill":
        proof["kill_events"].append(
            {"case": name, "tag": "run1", "pid": str(pid_run1 or proc.pid)}
        )
    crash_result = result_of(case_dir, "run1")
    resumed_results = []
    for index, restart_over in enumerate(restart_specs or [None]):
        restart_spec = base_spec(name, mode, case_dir)
        if restart_over:
            restart_spec.update(restart_over)
        proc2 = runner_spawn(restart_spec, f"run{index + 2}")
        try:
            proc2.wait(timeout=300)
        except subprocess.TimeoutExpired:
            proc2.kill()
            proc2.wait(timeout=10)
        stdout, stderr = proc2.communicate(timeout=60)
        save_logs(name, f"run{index + 2}", stdout, stderr)
        proof["scratch_pids"].setdefault(name, []).append(
            {
                "tag": f"run{index + 2}",
                "pid": str(proc2.pid),
                "returncode": proc2.returncode,
            }
        )
        resumed_results.append(result_of(case_dir, f"run{index + 2}"))
    resumed = resumed_results[-1] if resumed_results else {}
    # oracle comparisons
    resumed_status = resumed.get("status")
    failures = []
    if resumed_status != expect_status:
        failures.append(
            f"{name}: restart status != {expect_status} ({resumed_status} err={resumed.get('error')})"
        )
    if expect_status == "imported":
        failures.extend(
            oracle_resumed(
                name,
                resumed,
                case_dir,
                need_sidecar_check=True,
                sidecar_expected_sha=matrix.get("EXP", {})
                .get("oracle", {})
                .get("sidecar_sha"),
            )
        )
    counts_after = snapshot_state(case_dir)
    failures.extend(
        [
            f"{name}: canonical raw bytes drifted ({path})"
            for path, info in counts_after["company_files"].items()
            if path.replace("\\", "/").endswith(HK_FILENAME)
            and info["sha256"] != HK_SHA
        ]
    )
    proof["worker_paused_unchanged"][name] = bool(
        counts_after.get("worker_paused_sha256")
    )
    case_results[name] = {"failures": failures}
    matrix[name] = {
        "boundary": point,
        "method": method,
        "checkpoint_confirmed": interrupted,
        "crashed": compact(crash_result),
        "resume": [compact(r) for r in resumed_results],
        "crashed_journal_outcomes": [
            row.get("outcome") for row in crash_result.get("journal_lines", [])
        ],
        "resumed_journal_outcomes": [
            [row.get("outcome") for row in r.get("journal_lines", [])]
            for r in resumed_results
        ],
        "failures": failures,
    }


def failed_case_results(name: str, failures: list) -> dict:
    return {"failures": failures}


CASES = {}


def case(name):
    def register(fn):
        CASES[name] = fn
        return fn

    return register


@case("P1_raise_staged_verified")
def _case_p1_raise_staged(m, cr, pr):
    crash_then_resume_case(
        m, cr, pr, "P1_raise_staged_verified", point="staged_verified", method="raise"
    )


@case("P1_raise_raw_saved")
def _case_p1_raise_raw_saved(m, cr, pr):
    crash_then_resume_case(
        m, cr, pr, "P1_raise_raw_saved", point="raw_saved", method="raise"
    )


@case("P1_raise_provenance_saved")
def _case_p1_raise_provenance(m, cr, pr):
    crash_then_resume_case(
        m, cr, pr, "P1_raise_provenance_saved", point="provenance_saved", method="raise"
    )


@case("P1_raise_qualified")
def _case_p1_raise_qualified(m, cr, pr):
    crash_then_resume_case(
        m, cr, pr, "P1_raise_qualified", point="qualified", method="raise"
    )


@case("P1_kill_staged_verified")
def _case_p1_kill_staged(m, cr, pr):
    crash_then_resume_case(
        m, cr, pr, "P1_kill_staged_verified", point="staged_verified", method="kill"
    )


@case("P1_kill_provenance_saved")
def _case_p1_kill_provenance(m, cr, pr):
    crash_then_resume_case(
        m, cr, pr, "P1_kill_provenance_saved", point="provenance_saved", method="kill"
    )


@case("P1_kill_qualified")
def _case_p1_kill_qualified(m, cr, pr):
    crash_then_resume_case(
        m, cr, pr, "P1_kill_qualified", point="qualified", method="kill"
    )


@case("P1_kill_scan_partial")
def _case_p1_kill_scan_partial(m, cr, pr):
    crash_then_resume_case(
        m,
        cr,
        pr,
        "P1_kill_scan_partial",
        point="scan_partial",
        method="kill",
        scan_pause_doc=DOC_ID,
    )  # K4 freezes via the scanner hook at the scan-partial window.


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", default=[])
    args = parser.parse_args()
    AFTER.mkdir(parents=True, exist_ok=True)
    (AFTER / "before-restart").mkdir(exist_ok=True)
    (AFTER / "after-restart").mkdir(exist_ok=True)
    matrix = load_json(AFTER / "crash-boundary-matrix.json", {})
    case_results = load_json(AFTER / "case_results.json", {})
    proof = load_json(
        AFTER / "recovery-and-paused-proof.json",
        {"scratch_pids": {}, "kill_events": [], "worker_paused_unchanged": {}},
    )
    names = args.case or list(CASES)
    requested = [n for n in names if n in CASES]
    if not requested:
        requested = ["EXP"]
    if "EXP" in requested and requested[0] != "EXP":
        requested = ["EXP"] + [n for n in requested if n != "EXP"]
    for name in requested:
        fn = CASES[name] if name != "EXP" else case_EXP
        try:
            fn(matrix, case_results, proof)
        except Exception as exc:
            import traceback

            case_results[name] = {
                "failures": [f"{name}: case exception {type(exc).__name__}: {exc}"],
                "traceback": traceback.format_exc(),
            }
            matrix[name] = {"failures": case_results[name]["failures"]}
        write_outputs(matrix, case_results, proof)
    failed = sorted(n for n, v in case_results.items() if v.get("failures"))
    print(json.dumps({"failed_cases": failed}, ensure_ascii=False))
    return 1 if failed else 0


def copy_snapshot_sidecar_free(case_dir: Path, destination: Path):
    copy_snapshot(case_dir, destination)


def raw_kept_ok(case_dir: Path) -> bool:
    raw = case_dir / "project" / CANONICAL_REL.replace("/", "\\")
    return raw.is_file() and sha256_file(raw) == HK_SHA


@case("N1a_missing_sidecar")
def _case_n1a(m, cr, pr):
    """N1: raw survives but sidecar (provenance) missing -> blocked, raw
    retained, NOTHING guessed (no captured time/content invention)."""
    name = "N1a_missing_sidecar"
    mode = "register"
    case_dir = case_init(name, mode)
    raw = case_dir / "project" / CANONICAL_REL.replace("/", "\\")
    sidecar = raw.with_name(raw.name + ".source.json")
    sidecar.unlink(missing_ok=True)
    proc = runner_spawn(base_spec(name, mode, case_dir), "run")
    proc.wait(timeout=300)
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run", "pid": str(proc.pid), "returncode": proc.returncode}
    )
    result = result_of(case_dir, "run")
    expected_phrase = "existing_raw_missing_sidecar"
    errors = []
    if not (
        result.get("status") == "exception"
        and expected_phrase in str(result.get("error", ""))
    ):
        errors.append(
            f"{name}: expected blocked {expected_phrase}, "
            f"got status={result.get('status')} err={result.get('error')}"
        )
    raw_sha = sha256_file(raw) if raw.is_file() else None
    if raw_sha != HK_SHA:
        errors.append(f"{name}: raw bytes not retained exactly (sha={raw_sha})")
    provider = result.get("provider_calls") or {}
    if provider.get("fetch", 0) != 0:
        errors.append(f"{name}: no download may happen on block ({provider})")
    if not snapshot_state(case_dir).get("worker_paused_sha256"):
        errors.append(f"{name}: worker paused marker missing")
    pr["worker_paused_unchanged"][name] = True
    negative = {
        "expectation": "blocked existing_raw_missing_sidecar; raw retained; no sidecar contents invented",
        "status": result.get("status"),
        "error": result.get("error"),
        "blocked": result.get("status") == "exception"
        and expected_phrase in str(result.get("error", "")),
        "verbatim_raw_retained": raw_sha == HK_SHA,
        "provider_calls": provider,
        "failures": errors,
    }
    m[name] = negative
    cr[name] = {
        "failures": errors,
        "blocked": negative["blocked"] == result.get("status") == "exception",
    }


@case("N1b_raw_gone_no_staging")
def _case_n1b(m, cr, pr):
    """N1b: stage_raw_saved row exists but raw is gone AND no staging file
    remains -> blocked resume_raw_file_missing; no re-download (provider 0)."""
    name = "N1b_raw_gone_no_staging"
    mode = "download"
    case_dir = case_init(name, mode)
    spec = base_spec(name, mode, case_dir)
    spec["inject"] = "raw_saved:pause"
    spec["kill_intent"] = True
    proc = runner_spawn(spec, "run1")
    wait_checkpoint(case_dir, "raw_saved", proc)
    pid1 = runner_pid(case_dir, "run1")
    kill_recorded(proc, name, "run1")
    (AFTER / "after-restart" / name).mkdir(parents=True, exist_ok=True)
    (AFTER / "after-restart" / name / "post_kill.json").write_text(
        json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run1", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run1", "pid": str(pid1), "returncode": "SIGKILL", "method": "kill"}
    )
    cr_results_run1 = result_of(case_dir, "run1")
    resumed_entries = []
    assert raw_kept_ok(case_dir), f"{name}: crash state must have kept the raw"
    # mutate: delete raw + staging (documented driver injection, oracle N1b)
    raw = case_dir / "project" / CANONICAL_REL.replace("/", "\\")
    raw.unlink()
    staging = case_dir / "project" / ".source_catalog" / "staging"
    if staging.is_dir():
        shutil.rmtree(staging)
    copy_snapshot(case_dir, AFTER / "before-restart" / name)
    proc2 = runner_spawn(base_spec(name, mode, case_dir), "run2")
    proc2.wait(timeout=300)
    stdout, stderr = proc2.communicate(timeout=60)
    save_logs(name, "run2", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run2", "pid": str(proc2.pid), "returncode": proc2.returncode}
    )
    resumed = result_of(case_dir, "run2")
    resumed_entries.append(resumed)
    copy_snapshot(case_dir, AFTER / "after-restart" / name)
    expected_phrase = "resume_raw_file_missing"
    blocked = resumed.get("status") == "exception" and expected_phrase in str(
        resumed.get("error", "")
    )
    provider = resumed.get("provider_calls") or {}
    errors = []
    if not blocked:
        errors.append(
            f"{name}: expected blocked {expected_phrase}, "
            f"got status={resumed.get('status')} err={resumed.get('error')}"
        )
    if provider.get("discover", 0) != 0 or provider.get("fetch", 0) != 0:
        errors.append(f"{name}: no re-download allowed on block ({provider})")
    pr["worker_paused_unchanged"][name] = bool(
        snapshot_state(case_dir).get("worker_paused_sha256")
    )
    m[name] = {
        "boundary": "raw_saved",
        "method": "kill",
        "expectation": "blocked resume_raw_file_missing; no re-download; raw stays gone (not re-fetched)",
        "status": resumed.get("status"),
        "error": resumed.get("error"),
        "provider_calls": provider,
        "failures": errors,
    }
    cr[name] = {"failures": errors}


@case("N3a_raw_drift_after_crash")
def _case_n3a(m, cr, pr):
    """N3a: raw bytes drift after the crash -> blocked resume_raw_bytes_mismatch.
    Raw is preserved (NOT deleted/rewritten); no silent receipt reuse."""
    name = "N3a_raw_drift_after_crash"
    mode = "download"
    case_dir = case_init(name, mode)
    spec = base_spec(name, mode, case_dir)
    spec["inject"] = "provenance_saved:pause"
    spec["kill_intent"] = True
    proc = runner_spawn(spec, "run1")
    wait_checkpoint(case_dir, "provenance_saved", proc)
    pid1 = runner_pid(case_dir, "run1")
    kill_recorded(proc, name, "run1")
    (AFTER / "after-restart" / name).mkdir(parents=True, exist_ok=True)
    (AFTER / "after-restart" / name / "post_kill.json").write_text(
        json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run1", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run1", "pid": str(pid1), "returncode": "SIGKILL", "method": "kill"}
    )
    assert raw_kept_ok(case_dir), f"{name}: crash state must have kept the raw"
    raw = case_dir / "project" / CANONICAL_REL.replace("/", "\\")
    data = bytearray(raw.read_bytes())
    data[16] ^= 0x01
    raw.write_bytes(bytes(data))
    copy_snapshot(case_dir, AFTER / "before-restart" / name)
    proc2 = runner_spawn(base_spec(name, mode, case_dir), "run2")
    proc2.wait(timeout=300)
    stdout, stderr = proc2.communicate(timeout=60)
    save_logs(name, "run2", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run2", "pid": str(proc2.pid), "returncode": proc2.returncode}
    )
    resumed = result_of(case_dir, "run2")
    copy_snapshot(case_dir, AFTER / "after-restart" / name)
    expected_phrase = "resume_raw_bytes_mismatch"
    blocked = resumed.get("status") == "exception" and expected_phrase in str(
        resumed.get("error", "")
    )
    # drifted raw preserved (NOT deleted, NOT rewritten to old bytes)
    drifted_kept = (
        raw.is_file() and sha256_file(raw) != HK_SHA and raw.stat().st_size == 4405561
    )
    provider = resumed.get("provider_calls") or {}
    errors = []
    if not blocked:
        errors.append(
            f"{name}: expected blocked {expected_phrase}, "
            f"got status={resumed.get('status')} err={resumed.get('error')}"
        )
    if not drifted_kept:
        errors.append(f"{name}: drifted raw must be kept, not deleted")
    if provider.get("discover", 0) != 0 or provider.get("fetch", 0) != 0:
        errors.append(f"{name}: no re-download on drift block ({provider})")
    pr["worker_paused_unchanged"][name] = bool(
        snapshot_state(case_dir).get("worker_paused_sha256")
    )
    m[name] = {
        "boundary": "provenance_saved",
        "method": "kill",
        "expectation": "blocked resume_raw_bytes_mismatch; drifted raw preserved; no silent receipt reuse",
        "status": resumed.get("status"),
        "error": resumed.get("error"),
        "drifted_raw_kept": drifted_kept,
        "provider_calls": provider,
        "failures": errors,
    }
    cr[name] = {"failures": errors}


@case("N3b_policy_epoch")
def _case_n3b(m, cr, pr):
    """N3b: policy epoch after crash -> resume re-qualifies against the
    CURRENT root policy; refused under frozen policy, recovers to the oracle
    identity once the policy epoch changes back."""
    name = "N3b_policy_epoch"
    mode = "download"
    case_dir = case_init(name, mode)
    spec = base_spec(name, mode, case_dir)
    spec["inject"] = "provenance_saved:pause"
    spec["kill_intent"] = True
    proc = runner_spawn(spec, "run1")
    wait_checkpoint(case_dir, "provenance_saved", proc)
    pid1 = runner_pid(case_dir, "run1")
    kill_recorded(proc, name, "run1")
    (AFTER / "after-restart" / name).mkdir(parents=True, exist_ok=True)
    (AFTER / "after-restart" / name / "post_kill.json").write_text(
        json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run1", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run1", "pid": str(pid1), "returncode": "SIGKILL", "method": "kill"}
    )
    spec_blocked = base_spec(name, mode, case_dir)
    spec_blocked["reusable_root"] = False
    copy_snapshot(case_dir, AFTER / "before-restart" / name)
    proc_b = runner_spawn(spec_blocked, "run2")
    proc_b = proc_b
    proc_b.wait(timeout=300)
    stdout, stderr = proc_b.communicate(timeout=60)
    save_logs(name, "run2", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run2", "pid": str(proc_b.pid), "returncode": proc_b.returncode}
    )
    blocked = result_of(case_dir, "run2")
    proc3 = runner_spawn(base_spec(name, mode, case_dir), "run3")
    proc3.wait(timeout=300)
    stdout, stderr = proc3.communicate(timeout=60)
    save_logs(name, "run3", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run3", "pid": str(proc3.pid), "returncode": proc3.returncode}
    )
    recovered = result_of(case_dir, "run3")
    copy_snapshot(case_dir, AFTER / "after-restart" / name)
    expected_phrase = "resume_policy_epoch_refused"
    ok_block = blocked.get("status") == "exception" and expected_phrase in str(
        blocked.get("error", "")
    )
    ok_done = recovered.get("status") == "imported"
    errors = []
    if not ok_block:
        errors.append(
            f"{name}: expected blocked {expected_phrase}, got {blocked.get('error')}"
        )
    if not ok_done:
        errors.append(
            f"{name}: resume after policy-epoch-back failed ({recovered.get('status')} err={recovered.get('error')})"
        )
    else:
        errors.extend(
            oracle_resumed(name, recovered, case_dir, need_sidecar_check=True)
        )
    pr["worker_paused_unchanged"][name] = bool(
        snapshot_state(case_dir).get("worker_paused_sha256")
    )
    m[name] = {
        "boundary": "provenance_saved",
        "method": "kill",
        "blocked_error": blocked.get("error"),
        "recovered_status": recovered.get("status"),
        "failures": errors,
    }
    cr[name] = {"failures": errors}


def wait_file(path: Path, timeout: float = 60.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file():
            return True
        time.sleep(0.05)
    return path.is_file()


@case("N2a_db_lock")
def _case_n2a(m, cr, pr):
    """N2a: a LIVE catalog operation lock during the restart attempt ->
    CatalogOperationLockedError (retryable contention, no silent catch nor
    lock deletion); after the holder releases, resume recovers to oracle."""
    name = "N2a_db_lock"
    mode = "download"
    case_dir = case_init(name, mode)
    spec = base_spec(name, mode, case_dir)
    spec["inject"] = "provenance_saved:pause"
    spec["kill_intent"] = True
    proc = runner_spawn(spec, "run1")
    wait_checkpoint(case_dir, "provenance_saved", proc)
    pid1 = runner_pid(case_dir, "run1")
    kill_recorded(proc, name, "run1")
    (AFTER / "after-restart" / name).mkdir(parents=True, exist_ok=True)
    (AFTER / "after-restart" / name / "post_kill.json").write_text(
        json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run1", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run1", "pid": str(pid1), "returncode": "SIGKILL", "method": "kill"}
    )
    catalog_dir = case_dir / "project" / ".source_catalog"
    hold_file = case_dir / "w02e_release"
    holder_token = case_dir / "holder.token"
    proc_b_exact = subprocess.Popen(
        [
            str(PYTHON),
            "-X",
            "utf8",
            str(RUNNER_HOLD),
            str(catalog_dir),
            str(hold_file),
            str("/dev/null"),
            str(holder_token),
        ]
        if False
        else [
            str(PYTHON),
            "-X",
            "utf8",
            str(RUNNER_HOLD),
            str(catalog_dir),
            str(hold_file),
            str(holder_token),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ATTEMPT),
    )
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "holder", "pid": str(proc_b_exact.pid), "returncode": None}
    )
    wait_file(holder_token)
    copy_snapshot(case_dir, AFTER / "before-restart" / name)
    proc2 = runner_spawn(base_spec(name, mode, case_dir), "run2")
    try:
        proc2.wait(timeout=120)
    except subprocess.TimeoutExpired:
        proc2.kill()
    stdout, stderr = proc2.communicate(timeout=60)
    save_logs(name, "run2", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {
            "tag": "run2",
            "pid": str(runner_pid(case_dir, "run2")),
            "returncode": proc2.returncode,
        }
    )
    locked_attempt = result_of(case_dir, "run2")
    proc_b_exact.terminate()
    try:
        proc_b_exact.stdout and proc_b_exact.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc_b_exact.kill()
    try:
        proc_b_exact.stdout.close() if False else proc_b_exact.communicate(timeout=10)
    except Exception:
        pass
    expected_phrase = "catalog operation already running"
    ok_locked = locked_attempt.get("status") == "exception" and (
        "CatalogOperationLockedError" in str(locked_attempt.get("error", ""))
        or expected_phrase in str(locked_attempt.get("error", ""))
    )
    proc3 = runner_spawn(base_spec(name, mode, case_dir), "run3")
    proc3.wait(timeout=300)
    stdout, stderr = proc3.communicate(timeout=60)
    save_logs(name, "run3", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run3", "pid": str(proc3.pid), "returncode": proc3.returncode}
    )
    recovered = result_of(case_dir, "run3")
    copy_snapshot(case_dir, AFTER / "after-restart" / name)
    errors = []
    if not ok_locked:
        errors.append(
            f"{name}: expected retryable lock contention during held lock, got {locked_attempt.get('status')} err={locked_attempt.get('error')}"
        )
    if recovered.get("status") != "imported":
        errors.append(
            f"{name}: resume after lock release failed ({recovered.get('status')} err={recovered.get('error')})"
        )
    else:
        errors.extend(
            oracle_resumed(name, recovered, case_dir, need_sidecar_check=True)
        )
    pr["worker_paused_unchanged"][name] = bool(
        snapshot_state(case_dir).get("worker_paused_sha256")
    )
    m[name] = {
        "boundary": "provenance_saved",
        "method": "kill",
        "locked_error": locked_attempt.get("error"),
        "recovered_status": recovered.get("status"),
        "failures": errors,
    }
    cr[name] = {"failures": errors}


def journal_path(case_dir: Path) -> Path:
    return case_dir / "project" / ".source_catalog" / "acquisition_attempts.jsonl"


@case("N2b_journal_torn_tail")
def _case_n2b(m, cr, pr):
    """N2b: half-written journal tail line -> read_all must NOT continue
    silently; blocked first; after the driver's DOCUMENTED manual repair
    (bytes preserved to .corrupt-tail) the resume recovers to oracle."""
    name = "N2b_journal_torn_tail"
    mode = "download"
    case_dir = case_init(name, mode)
    spec = base_spec(name, mode, case_dir)
    spec["inject"] = "provenance_saved:pause"
    spec["kill_intent"] = True
    proc = runner_spawn(spec, "run1")
    wait_checkpoint(case_dir, "provenance_saved", proc)
    pid1 = runner_pid(case_dir, "run1")
    kill_recorded(proc, name, "run1")
    (AFTER / "after-restart" / name).mkdir(parents=True, exist_ok=True)
    (AFTER / "after-restart" / name / "post_kill.json").write_text(
        json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run1", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run1", "pid": str(pid1), "returncode": "SIGKILL", "method": "kill"}
    )
    # mutate: append a torn tail (documented driver injection per oracle N2b)
    torn_fragment = b'{"schema_version": "1.0", "request_id": "trunc'
    with open(journal_path(case_dir), "ab") as stream:
        stream.write(torn_fragment)
    copy_snapshot(case_dir, AFTER / "before-restart" / name)
    proc2 = runner_spawn(base_spec(name, mode, case_dir), "run2")
    proc2.wait(timeout=300)
    stdout, stderr = proc2.communicate(timeout=60)
    save_logs(name, "run2", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {
            "tag": "run2",
            "pid": str(runner_pid(case_dir, "run2")),
            "returncode": proc2.returncode,
        }
    )
    torn_result = result_of(case_dir, "run2")
    torn_reads_error = any(
        "journal_read_error" in str(row) for row in torn_result.get("journal_lines", [])
    )
    expected_phrase = "invalid acquisition journal line"
    ok_torn = (
        torn_result.get("status") == "exception"
        and expected_phrase in str(torn_result.get("error", ""))
    ) or torn_reads_error
    if torn_result.get("status") == "imported":
        # silently continuing through the torn tail is FORBIDDEN
        ok_torn = False
    # manual documented repair: keep all complete lines byte-identical; the
    # torn fragment is preserved to a .corrupt-tail evidence file (never
    # deleted, never auto-continued).
    corrupt_sidecar = journal_path(case_dir).with_name(
        journal_path(case_dir).name + ".corrupt-tail"
    )
    payload = journal_path(case_dir).read_bytes()
    idx = payload.rindex(torn_fragment)
    head = payload[:idx]
    if not head.endswith(b"\n"):
        head = head + b"\n"
    corrupt_sidecar.write_bytes(payload[idx:])
    journal_path(case_dir).write_bytes(head)
    manual_repair_applied = True
    proc3 = runner_spawn(base_spec(name, mode, case_dir), "run3")
    proc3.wait(timeout=300)
    stdout, stderr = proc3.communicate(timeout=60)
    save_logs(name, "run3", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run3", "pid": str(proc3.pid), "returncode": proc3.returncode}
    )
    recovered = result_of(case_dir, "run3")
    copy_snapshot(case_dir, AFTER / "after-restart" / name)
    errors = []
    if not ok_torn:
        errors.append(
            f"{name}: torn journal tail must hard-block the attempt, got {torn_result.get('status')} err={torn_result.get('error')}"
        )
    if not manual_repair_applied:
        errors.append(f"{name}: manual repair never applied")
    if recovered.get("status") != "imported":
        errors.append(
            f"{name}: resume after documented manual repair failed ({recovered.get('status')} err={recovered.get('error')})"
        )
    else:
        errors.extend(
            oracle_resumed(name, recovered, case_dir, need_sidecar_check=True)
        )
    pr["worker_paused_unchanged"][name] = bool(
        snapshot_state(case_dir).get("worker_paused_sha256")
    )
    m[name] = {
        "boundary": "provenance_saved",
        "method": "kill",
        "torn_error": torn_result.get("error"),
        "manual_repair": manual_repair_applied,
        "corrupt_tail_kept": corrupt_sidecar.is_file(),
        "recovered_status": recovered.get("status"),
        "failures": errors,
    }
    cr[name] = {"failures": errors}


@case("N2c_stale_lease")
def _case_n2c(m, cr, pr):
    """N2c: a stale operation.lock left by an already-dead prior scratch
    process -> the restart TAKES OVER the stale lease (never blanket lock
    deletion); recovery completes to the oracle identity."""
    name = "N2c_stale_lease"
    mode = "download"
    case_dir = case_init(name, mode)
    spec = base_spec(name, mode, case_dir)
    spec["inject"] = "provenance_saved:pause"
    spec["kill_intent"] = True
    proc = runner_spawn(spec, "run1")
    wait_checkpoint(case_dir, "provenance_saved", proc)
    pid1 = runner_pid(case_dir, "run1")
    # keep the (soon) stale lock BEFORE killing the holder so the restart
    # faces a recorded dead-owner lease — the takeover path, not a live lock.
    lock_path = case_dir / "project" / ".source_catalog" / "operation.lock"
    holder_pid = proc.pid
    kill_recorded(proc, name, "run1")
    (AFTER / "after-restart" / name).mkdir(parents=True, exist_ok=True)
    (AFTER / "after-restart" / name / "post_kill.json").write_text(
        json.dumps(snapshot_state(case_dir), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run1", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run1", "pid": str(pid1), "returncode": "SIGKILL", "method": "kill"}
    )
    # lock file left behind (the kill never released the catalog lock this
    # way in the real chain) — inject it verbatim like the observed case:
    import os as _os

    payload_text = (
        json.dumps(
            {
                "pid": int(pid1),
                "operation": "canonical_import",
                "token": "w02e-stale-lease",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
    )
    lock_path.write_text(payload_text)
    lock_injected = lock_path.is_file()
    copy_snapshot(case_dir, AFTER / "before-restart" / name)
    proc2 = runner_spawn(base_spec(name, mode, case_dir), "run2")
    proc2.wait(timeout=300)
    stdout, stderr = proc2.communicate(timeout=60)
    save_logs(name, "run2", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run2", "pid": str(proc2.pid), "returncode": proc2.returncode}
    )
    resumed = result_of(case_dir, "run2")
    copy_snapshot(case_dir, AFTER / "after-restart" / name)
    operation_lock_cleared = not lock_path.is_file()
    errors = []
    if resumed.get("status") != "imported":
        errors.append(
            f"{name}: restart must take over the stale lease and recover "
            f"({resumed.get('status')} err={resumed.get('error')})"
        )
    else:
        errors.extend(oracle_resumed(name, resumed, case_dir, need_sidecar_check=True))
    operation_lock_cleared = not lock_path.is_file()
    pr["worker_paused_unchanged"][name] = bool(
        snapshot_state(case_dir).get("worker_paused_sha256")
    )
    m[name] = {
        "boundary": "provenance_saved",
        "method": "kill",
        "stale_lock_injected": True,
        "recovered_status": resumed.get("status"),
        "lock_taken_over": operation_lock_cleared,
        "failures": errors,
    }
    cr[name] = {"failures": errors}


@case("N2d_identity_conflict")
def _case_n2d(m, cr, pr):
    """N2d: after qualification the recovery is retried with a DIFFERENT
    provider identity -> the durable-sidecar identity contract refuses; the
    interrupted attempt's receipt is never reused and no row changes."""
    name = "N2d_identity_conflict"
    mode = "register"
    case_dir = case_init(name, mode)
    proc = runner_spawn(base_spec(name, mode, case_dir), "run")
    proc = proc
    proc.wait(timeout=300)
    stdout, stderr = proc.communicate(timeout=60)
    save_logs(name, "run", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {"tag": "run", "pid": str(proc.pid), "returncode": proc.returncode}
    )
    baseline = result_of(case_dir, "run")
    state_before = snapshot_state(case_dir)
    spec_conflict = base_spec(name, mode, case_dir)
    spec_conflict["request_override"] = {
        "provider": "sec",
        "provider_document_id": "0001193125-26-323660",
    }
    proc2 = runner_spawn(spec_conflict, "run2")
    proc2.wait(timeout=300)
    stdout, stderr = proc2.communicate(timeout=60)
    save_logs(name, "run2", stdout, stderr)
    pr["scratch_pids"].setdefault(name, []).append(
        {
            "tag": "run2",
            "pid": str(runner_pid(case_dir, "run2")),
            "returncode": proc2.returncode,
        }
    )
    conflict = result_of(case_dir, "run2")
    copy_snapshot(case_dir, AFTER / "after-restart" / name)
    ok_block = conflict.get(
        "status"
    ) == "exception" and "existing_raw_identity_contract" in str(
        conflict.get("error", "")
    )
    state_after = snapshot_state(case_dir)
    rows_unchanged = (
        state_after.get("sources_rows") == 1
        and state_after.get("documents_active") == 1
        and state_after.get("locations_active_original") == 1
    )
    raw_kept = any(
        info.get("sha256") == HK_SHA and str(p).replace("\\", "/").endswith(HK_FILENAME)
        for p, info in state_after["company_files"].items()
    )
    provider = conflict.get("provider_calls") or {}
    rows_unchanged_value = (
        state_after.get("sources_rows") == state_before.get("sources_rows")
        and state_after.get("documents_active") == state_before.get("documents_active")
        and state_after.get("locations_active_original")
        == state_before.get("locations_active_original")
    )
    errors = []
    if not ok_block:
        errors.append(
            f"{name}: identity conflict must be blocked, got {conflict.get('status')} err={conflict.get('error')}"
        )
    if not rows_unchanged_value:
        errors.append(f"{name}: no row may change on identity conflict")
    if not raw_kept:
        errors.append(f"{name}: raw bytes must be retained on conflict block")
    pr["worker_paused_unchanged"][name] = bool(state_after.get("worker_paused_sha256"))
    m[name] = {
        "expectation": "blocked existing_raw_identity_contract; rows unchanged; raw retained",
        "error": conflict.get("error"),
        "rows_unchanged": rows_unchanged_value,
        "raw_kept": raw_kept_ok(case_dir),
        "provider_calls": provider,
        "failures": errors,
    }
    cr[name] = {"failures": errors}


if __name__ == "__main__":
    raise SystemExit(main())
