"""Judged subprocess execution and evidence helpers (W14 E03/E07)."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import time
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1,
                               default=str), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or "", encoding="utf-8")


def parse_json_docs(text: str) -> list[dict]:
    """Parse structured JSON from a stream: pretty-printed final object first,
    then the compact single-line fallback (refusal envelopes)."""
    raw = (text or "").strip()
    if raw.startswith("{") and raw.endswith("}"):
        try:
            doc = json.loads(raw)
            if isinstance(doc, dict):
                return [doc]
        except json.JSONDecodeError:
            pass
    docs = []
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return docs


def run_cmd(argv, *, cwd: Path, env: dict, timeout: float,
            tag: str, ev_dir: Path) -> dict:
    """One judged subprocess with PID capture; full evidence persisted."""
    t0 = time.monotonic()
    argv = [str(a) for a in argv]
    pid = None
    timed_out = False
    try:
        proc = subprocess.Popen(
            argv, cwd=str(cwd), env=env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8",
            errors="replace")
        pid = proc.pid
        try:
            out, err = proc.communicate(timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            out, err = proc.communicate() or ("", "")
            rc = -9
    except OSError as exc:
        out = err = ""
        rc = -8
        err = f"{type(exc).__name__}: {exc}"
    elapsed = round(time.monotonic() - t0, 3)
    ev_dir.mkdir(parents=True, exist_ok=True)
    write_json(ev_dir / f"{tag}_argv.json", {
        "argv": argv, "cwd": str(cwd), "pid": pid,
        "timeout_seconds": timeout, "timed_out": timed_out,
        "elapsed_seconds": elapsed, "returncode": rc,
    })
    write_text(ev_dir / f"{tag}_stdout.txt", out or "")
    write_text(ev_dir / f"{tag}_stderr.txt", err or "")
    return {"tag": tag, "pid": pid, "rc": rc, "stdout": out or "",
            "stderr": err or "", "timed_out": timed_out,
            "elapsed": elapsed, "docs": parse_json_docs(out or ""),
            "argv": argv}


def catalog_counts(catalog: Path) -> dict:
    """Row counts of an ISOLATED catalog only (ro, query_only)."""
    con = sqlite3.connect(f"file:{catalog}?mode=ro", uri=True)
    con.execute("PRAGMA query_only=ON")
    tabs = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    counts = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
              for t in tabs}
    con.close()
    return counts


def catalog_delta(before: dict, after: dict) -> dict:
    return {k: after.get(k, 0) - before.get(k, 0)
            for k in sorted(set(before) | set(after))
            if after.get(k, 0) != before.get(k, 0)}


VOLATILE_CATALOG_FILES = (
    "catalog.sqlite3", "catalog.sqlite3-shm", "catalog.sqlite3-wal",
    "operation.lock", "operation.lock.acquire",
    "filing_fetch_pause.refcount", "filing_fetch_pause.owner",
)


def tree_snapshot(root: Path, *, exclude_dirs=(".pytest_cache", "__pycache__"),
                  hash_files=True, exclude_files=VOLATILE_CATALOG_FILES) -> dict:
    """{relpath: {size, mtime_ticks, sha256?}} for files under root."""
    out: dict = {}
    if not root.exists():
        return out
    if root.is_file():
        out[root.name] = _file_record(root, hash_files)
        return out
    for p in sorted(root.rglob("*")):
        rel_parts = p.relative_to(root).parts
        if any(part in exclude_dirs for part in rel_parts):
            continue
        if p.is_file():
            if p.name in exclude_files:
                continue
            out[p.relative_to(root).as_posix()] = _file_record(p, hash_files)
    return out


def _file_record(p: Path, hash_files: bool) -> dict:
    st = p.stat()
    rec = {"size": st.st_size, "mtime_ticks": st.st_mtime}
    if hash_files:
        rec["sha256"] = sha256_file(p)
    return rec


# Fields that legitimately differ between two runs of the same scenario:
# PIDs, absolute temp paths, wall-clock times and stamps.  Everything else a
# cross-directory comparison sees must be semantically identical (E07).
VOLATILE_SEMANTIC_KEYS = ("run_id", "started_at", "finished_at",
                          "total_elapsed_s", "elapsed_s", "pid", "interpreter")
_VOLATILE_PATH_HINTS = ("scratch", "attempt", "temp", "work", "evidence")


def semantic_projection(summary: dict) -> dict:
    """Stable projection of a run summary for cross-run comparison."""
    out: dict = {"exit_code": summary.get("exit_code"),
                 "statuses": summary.get("statuses"),
                 "scenarios": {}}
    for scenario in summary.get("scenarios", []):
        checks = {
            name: _scrub(value)
            for name, value in sorted(scenario.get("checks", {}).items())
            if name not in VOLATILE_SEMANTIC_KEYS
        }
        out["scenarios"][scenario["id"]] = {
            "status": scenario.get("status"),
            "reason_code": (scenario.get("reason") or {}).get("code"),
            "checks": checks,
        }
    return out


def _scrub(value):
    if isinstance(value, str):
        lowered = value.lower()
        if any(hint in lowered for hint in _VOLATILE_PATH_HINTS) and (
                "/" in value or "\\" in value or ":" in value):
            return "<path>"
        return value
    if isinstance(value, dict):
        return {k: _scrub(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_scrub(v) for v in value]
    return value
