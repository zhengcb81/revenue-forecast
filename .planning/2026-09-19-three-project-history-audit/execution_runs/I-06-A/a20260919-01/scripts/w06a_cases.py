"""W06A driver: cross-process demand registration cases for I-06-A.

Three case groups, each run against its OWN clone of the isolated product
tree (iso/rf for the pristine baseline, iso/rf_fixed for the candidate):

  B*  baseline: real source-preparation CLI, not_reviewed source, two
      independent processes with the same request.
  C*  candidate: same, plus a query from a THIRD process, a changed-source
      re-request, a broken store, and a paused worker.
  P*  paused-worker before/after bytes around every candidate call.

Nothing here writes outside the attempt (clones, scratch DBs and logs are all
inside it or under %TEMP%\\w06a).

  <py> -X utf8 -B scripts/w06a_cases.py <tag> <tree: baseline|candidate>
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples"
ISO = ATTEMPT / "iso"
PY = Path(sys.executable)
SCRATCH = Path(
    os.environ.get("W06A_SCRATCH", r"C:\Users\郑曾波\AppData\Local\Temp\w06a")
) / "a20260919-01"

REQUEST = SAMPLES / "request.json"
HANDLE = SAMPLES / "handle.json"
FF_ROOT = ISO / "ff"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    """Independent of the candidate store's own key derivation."""
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def decode_stream(raw: bytes) -> tuple[str, str]:
    """UTF-8 when the child spoke UTF-8, else the Windows ANSI code page.

    A Python OSError raised while formatting a path uses the platform's ANSI
    code page for the path fragment, so a failure message can carry non-UTF-8
    bytes.  The bytes are never dropped: the decoding used is recorded.
    """
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace"), "gbk"


def tree_root(kind: str) -> Path:
    return ISO / ("rf" if kind == "baseline" else "rf_fixed")


def run_cli(
    *,
    tag: str,
    case: str,
    tree: Path,
    handle_path: Path,
    env_extra: dict[str, str] | None = None,
    request_path: Path | None = None,
) -> dict:
    """One REAL source-preparation CLI invocation in its own process."""
    case_dir = ATTEMPT / tag / "cli-logs" / case
    case_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["W06A_HANDLE_JSON"] = str(handle_path)
    env["PYTHONPATH"] = str(tree / "scripts") + os.pathsep + str(ISO / "cw" / "src")
    if env_extra:
        env.update(env_extra)
    argv = [
        str(PY),
        "-X",
        "utf8",
        "-B",
        str(tree / "scripts" / "source_preparation.py"),
        "--request-file",
        str(request_path or REQUEST),
        "--filing-fetch-root",
        str(FF_ROOT),
        "--timeout-seconds",
        "30",
    ]
    completed = subprocess.run(
        argv,
        cwd=str(tree),
        capture_output=True,
        text=False,
        env=env,
        timeout=120,
        check=False,
    )
    stdout, stdout_encoding = decode_stream(completed.stdout)
    stderr, stderr_encoding = decode_stream(completed.stderr)
    (case_dir / "argv.json").write_text(
        json.dumps({"argv": argv, "cwd": str(tree)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (case_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
    (case_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
    (case_dir / "stderr.raw.bin").write_bytes(completed.stderr)
    record = {
        "case": case,
        "returncode": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        "stdout_encoding": stdout_encoding,
        "stderr_encoding": stderr_encoding,
        "log_dir": str(case_dir),
        "env_extra": sorted((env_extra or {}).keys()),
    }
    (case_dir / "result.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return record


def query_store(
    *, tag: str, case: str, tree: Path, db: Path, request_path: Path | None = None
) -> dict:
    """A SEPARATE process asks the durable store what demands exist."""
    case_dir = ATTEMPT / tag / "query-logs" / case
    case_dir.mkdir(parents=True, exist_ok=True)
    argv = [
        str(PY),
        "-X",
        "utf8",
        "-B",
        "-m",
        "processing_demand_store",
        "list",
        "--database",
        str(db),
    ]
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(tree / "scripts")
    completed = subprocess.run(
        argv,
        cwd=str(tree),
        capture_output=True,
        text=False,
        env=env,
        timeout=120,
        check=False,
    )
    stdout, stdout_encoding = decode_stream(completed.stdout)
    stderr, stderr_encoding = decode_stream(completed.stderr)
    (case_dir / "argv.json").write_text(
        json.dumps({"argv": argv, "cwd": str(tree)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (case_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
    (case_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
    payload = None
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        payload = None
    record = {
        "case": case,
        "returncode": completed.returncode,
        "payload": payload,
        "stderr": stderr,
        "stdout_encoding": stdout_encoding,
        "stderr_encoding": stderr_encoding,
        "log_dir": str(case_dir),
    }
    (case_dir / "result.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return record


def store_rows(db: Path) -> list[dict]:
    """Read the demand table with plain sqlite3 (independent of the store API)."""
    import sqlite3

    if not db.is_file():
        return []
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        return [
            dict(row)
            for row in connection.execute(
                "SELECT * FROM processing_demands ORDER BY demand_id"
            )
        ]
    finally:
        connection.close()


def paused_snapshot(control: Path) -> dict:
    return {
        "path": str(control),
        "exists": control.is_file(),
        "sha256": sha256_file(control) if control.is_file() else None,
        "bytes": control.read_text(encoding="utf-8") if control.is_file() else None,
    }


def write_paused_control(path: Path, desired_state: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "desired_state": desired_state,
                "updated_at": "2026-09-19T00:00:00Z",
                "updated_by": "I-06-A/a20260919-01 fixture",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    tag = sys.argv[1] if len(sys.argv) > 1 else "before"
    kind = sys.argv[2] if len(sys.argv) > 2 else "baseline"
    tree = tree_root(kind)
    out_dir = ATTEMPT / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    work = SCRATCH / f"{kind}-{tag}"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    db = work / "processing_demands.sqlite3"
    paused_control = work / "worker_control.json"
    write_paused_control(paused_control, "paused")
    paused_before = paused_snapshot(paused_control)

    # a cloned filing-fetch root whose script resolves the handle from a
    # DIFFERENT source file for the "changed source hash" case
    handle_b = json.loads(HANDLE.read_text(encoding="utf-8"))
    source_b = work / "source_bytes_changed.txt"
    source_b.write_text(
        "EMERALD-MINING-2025-ANNUAL-REPORT-BYTES (fixture; RE-ISSUED)\n",
        encoding="utf-8",
        newline="\n",
    )
    handle_b["snapshot_sha256"] = sha256_file(source_b)
    handle_b["canonical_path"] = str(source_b)
    handle_b_path = work / "handle_changed.json"
    handle_b_path.write_text(
        json.dumps(handle_b, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    store_env = {
        "RF_W06_DEMAND_STORE": str(db),
        "RF_W06_WORKER_CONTROL": str(paused_control),
        "RF_W06_ROLE_SET": "normalized,sections",
    }

    results: dict = {
        "tag": tag,
        "tree": kind,
        "tree_path": str(tree),
        "python": str(PY),
        "demand_store": str(db),
        "worker_control": str(paused_control),
        "paused_before": paused_before,
        "source_bytes_sha256": sha256_file(SAMPLES / "source_bytes.txt"),
        "changed_source_bytes_sha256": sha256_file(source_b),
        "handle_path": str(HANDLE),
        "changed_handle_path": str(handle_b_path),
        "cases": {},
    }

    if kind == "baseline":
        first = run_cli(tag=tag, case="b1-first-run", tree=tree, handle_path=HANDLE)
        second = run_cli(tag=tag, case="b2-second-process", tree=tree, handle_path=HANDLE)
        results["cases"] = {"b1_first_run": first, "b2_second_process": second}
        results["store_rows_after"] = store_rows(db)
        results["paused_after"] = paused_snapshot(paused_control)
        results["paused_unchanged"] = results["paused_after"] == paused_before
    else:
        first = run_cli(
            tag=tag, case="c1-first-run", tree=tree, handle_path=HANDLE,
            env_extra=store_env,
        )
        query1 = query_store(
            tag=tag, case="c2-second-process-query", tree=tree, db=db
        )
        second = run_cli(
            tag=tag, case="c3-repeated-request", tree=tree, handle_path=HANDLE,
            env_extra=store_env,
        )
        query2 = query_store(
            tag=tag, case="c4-query-after-repeat", tree=tree, db=db
        )
        changed = run_cli(
            tag=tag, case="c5-changed-source-hash", tree=tree,
            handle_path=handle_b_path, env_extra=store_env,
        )
        query3 = query_store(
            tag=tag, case="c6-query-after-change", tree=tree, db=db
        )
        broken = run_cli(
            tag=tag, case="c7-store-unwritable", tree=tree, handle_path=HANDLE,
            env_extra={
                **store_env,
                # a store path UNDER a regular file: mkdir/open must fail, and
                # the candidate must refuse instead of falling back to memory
                "RF_W06_DEMAND_STORE": str(HANDLE / "d.sqlite3"),
            },
        )
        # probe8: SAME source bytes / policy / role set, DIFFERENT request
        # fields.  The candidate's idempotency key does not include the
        # request, so this is where it can silently absorb a different task.
        request_b = json.loads(REQUEST.read_text(encoding="utf-8"))
        request_b["entity"] = "另一个实体"
        request_b["as_of_date"] = "2026-10-31"
        request_b_path = work / "request_changed.json"
        request_b_path.write_text(
            json.dumps(request_b, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        other_request = run_cli(
            tag=tag, case="c8-same-source-different-request", tree=tree,
            handle_path=HANDLE, env_extra=store_env, request_path=request_b_path,
        )
        query4 = query_store(
            tag=tag, case="c9-query-after-different-request", tree=tree, db=db
        )
        # probe9 (reviewer F-I06A-01): SAME source / policy / roles, ONLY
        # as_of_date changed (2026-09-19 -> 2027-03-31).
        request_c = json.loads(REQUEST.read_text(encoding="utf-8"))
        request_c["as_of_date"] = "2027-03-31"
        request_c_path = work / "request_asof_changed.json"
        request_c_path.write_text(
            json.dumps(request_c, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        asof_request = run_cli(
            tag=tag, case="c10-same-source-asof-only-changed", tree=tree,
            handle_path=HANDLE, env_extra=store_env, request_path=request_c_path,
        )
        query5 = query_store(
            tag=tag, case="c11-query-after-asof-change", tree=tree, db=db
        )
        results["request_hashes"] = {
            "original": canonical_sha256(json.loads(REQUEST.read_text(encoding="utf-8"))),
            "entity_and_asof_changed": canonical_sha256(request_b),
            "asof_only_changed": canonical_sha256(request_c),
        }
        results["cases"] = {
            "c1_first_run": first,
            "c2_second_process_query": query1,
            "c3_repeated_request": second,
            "c4_query_after_repeat": query2,
            "c5_changed_source_hash": changed,
            "c6_query_after_change": query3,
            "c7_store_unwritable": broken,
            "c8_same_source_different_request": other_request,
            "c9_query_after_different_request": query4,
            "c10_same_source_asof_only_changed": asof_request,
            "c11_query_after_asof_change": query5,
        }
        results["store_rows_after"] = store_rows(db)
        results["paused_after"] = paused_snapshot(paused_control)
        results["paused_unchanged"] = results["paused_after"] == paused_before

    (out_dir / f"case_results_{kind}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "tag": tag,
        "tree": kind,
        "returncodes": {
            key: value["returncode"] for key, value in results["cases"].items()
        },
        "store_rows": len(results["store_rows_after"]),
        "paused_unchanged": results["paused_unchanged"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
