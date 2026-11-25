"""Collect read-only local audit metadata.

Git working-tree status, tool versions, config digests, and explicitly
requested diagnostic roots are reported as JSON. The legacy --catalog
option reports the unavailable cross-owner section. Catalog state is
available from company-wiki's public interface.
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
            ["git", "--no-optional-locks", "-C", str(cwd), *args],
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


def collect_catalog(catalog_requested: bool) -> dict:
    result = {
        "schema_version": None,
        "size_bytes": None,
        "recent_scan_status": None,
        "roots": [],
        "error": None,
        "status": "not_requested",
        "reason": None,
    }
    if catalog_requested:
        result.update(
            status="unavailable",
            reason="catalog_owner_interface_required",
            error="Legacy catalog probe retired. Use the company-wiki public interface.",
        )
    return result


def collect_roots(probe_roots: list[Path]) -> dict:
    out: dict[str, dict] = {}
    for root in probe_roots:
        out[str(root)] = {"realpath": str(root.resolve())}
    return out


def main() -> int:
    # FC-1205: preserve deterministic UTF-8 for local paths and Git output.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")

    parser = argparse.ArgumentParser(description="Read-only audit baseline capture")
    parser.add_argument("--read-only", action="store_true",
                        help="legacy acknowledgment (the tool is read-only)")
    parser.add_argument("--catalog", type=Path, default=None, help="legacy option (catalog section is reported as unavailable)")
    parser.add_argument("--config", type=Path, action="append", default=[], help="config file to hash")
    parser.add_argument("--repos", type=Path, action="append", default=[], help="git repo dirs")
    parser.add_argument("--probe-roots", type=Path, action="append", default=[], help="roots to resolve")
    args = parser.parse_args()
    baseline = {
        "repos": collect_repos(args.repos),
        "environment": collect_environment(),
        "configs": collect_configs(args.config),
        "catalog": collect_catalog(args.catalog is not None),
        "roots": collect_roots(args.probe_roots),
    }
    print(json.dumps(baseline, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
