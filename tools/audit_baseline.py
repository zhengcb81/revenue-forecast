"""WU-0.1: capture a read-only audit baseline for the three repositories.

Usage::

    python tools/audit_baseline.py --read-only [--catalog PATH] [--config PATH]...
                                    [--repos PATH]... [--probe-roots PATH]...

The ``--read-only`` flag is mandatory; without it the tool refuses to run.
Output is a single JSON document on stdout with::

    repos        git HEAD + dirty files per repo
    environment  python/pytest/ruff/sqlite versions
    configs      sha256 per config file
    catalog      user_version, size, recent scan status, roots (mode=ro)
    roots        resolved realpath per probe root

The catalog is opened with a ``file:...?mode=ro`` URI; any write attempt
raises ``OperationalError``.  The tool never creates or modifies files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(cwd: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            # FC-1205 (PORT-01): text=True defaults to the locale codepage
            # (GBK) on Chinese Windows while git emits UTF-8 — explicit
            # decode with replacement, never a hard UnicodeDecodeError.
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def collect_repos(repos: list[Path]) -> dict:
    out: dict[str, dict] = {}
    for repo in repos:
        head = _git(repo, "rev-parse", "HEAD")
        dirty_raw = _git(repo, "status", "--porcelain")
        dirty = dirty_raw.splitlines() if dirty_raw else []
        out[repo.name] = {"head": head, "dirty_files": dirty}
    return out


def collect_environment() -> dict:
    def version_of(cmd: list[str]) -> str | None:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        return proc.stdout.strip().splitlines()[0] if proc.returncode == 0 else None

    return {
        "python": sys.version.split()[0],
        "pytest": version_of([sys.executable, "-m", "pytest", "--version"]),
        "ruff": version_of(["ruff", "--version"]),
        "sqlite": sqlite3.sqlite_version,
    }


def collect_configs(configs: list[Path]) -> dict:
    out: dict[str, str] = {}
    for path in configs:
        if path.is_file():
            out[str(path)] = _sha256(path)
    return out


def open_catalog_readonly(catalog: Path) -> sqlite3.Connection:
    """Open the catalog with a read-only URI; any write raises OperationalError."""
    uri = f"file:{catalog}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.execute("PRAGMA query_only = ON")  # belt-and-suspenders: no writes
    return con


def collect_catalog(catalog: Path | None) -> dict:
    if catalog is None or not catalog.is_file():
        return {"schema_version": None, "size_bytes": None,
                "recent_scan_status": None, "roots": [], "error": "catalog missing"}
    con = open_catalog_readonly(catalog)
    error = None
    try:
        schema_version = con.execute("PRAGMA user_version").fetchone()[0]
        size_bytes = catalog.stat().st_size
        roots = []
        recent = None
        try:
            for row in con.execute("SELECT root_id, kind, path, priority FROM roots ORDER BY priority"):
                roots.append({"root_id": row[0], "kind": row[1], "path": row[2], "priority": row[3]})
        except sqlite3.OperationalError as exc:
            roots = []
            error = f"roots query failed: {exc}"
        try:
            row = con.execute("SELECT status FROM scan_runs ORDER BY rowid DESC LIMIT 1").fetchone()
            if row:
                recent = row[0]
        except sqlite3.OperationalError as exc:
            recent = None
            error = f"scan_runs query failed: {exc}"
        return {
            "schema_version": schema_version,
            "size_bytes": size_bytes,
            "recent_scan_status": recent,
            "roots": roots,
            "error": error,
        }
    finally:
        con.close()


def collect_roots(probe_roots: list[Path]) -> dict:
    out: dict[str, dict] = {}
    for root in probe_roots:
        out[str(root)] = {"realpath": str(root.resolve())}
    return out


def main() -> int:
    # FC-1205 (PORT-01): the baseline JSON carries non-ASCII paths (Chinese
    # user name); force UTF-8 on the child side so any reader — pytest or a
    # consumer — decodes the stream deterministically (fetch_filing pattern).
    # FC-1205 (PORT-01): the baseline JSON carries non-ASCII paths (Chinese
    # user name); force UTF-8 on the child side so any reader — pytest or a
    # consumer — decodes the stream deterministically (fetch_filing pattern).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")

    parser = argparse.ArgumentParser(description="Read-only audit baseline capture")
    parser.add_argument("--read-only", action="store_true",
                        help="mandatory: confirms read-only operation")
    parser.add_argument("--catalog", type=Path, default=None, help="path to catalog.sqlite3")
    parser.add_argument("--config", type=Path, action="append", default=[], help="config file to hash")
    parser.add_argument("--repos", type=Path, action="append", default=[], help="git repo dirs")
    parser.add_argument("--probe-roots", type=Path, action="append", default=[], help="roots to resolve")
    args = parser.parse_args()
    if not args.read_only:
        print("refusing to run: the --read-only flag is mandatory", file=sys.stderr)
        return 2
    baseline = {
        "repos": collect_repos(args.repos),
        "environment": collect_environment(),
        "configs": collect_configs(args.config),
        "catalog": collect_catalog(args.catalog),
        "roots": collect_roots(args.probe_roots),
    }
    print(json.dumps(baseline, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
