"""CodeGraph freshness freeze (CA-003): bind each repo's CodeGraph index to an
exact git commit and generate machine-readable production caller reports.

Design rules (from the CA-003 card):

- The index window is EXCLUSIVE: freezing refuses to run while any
  ``*.lock`` file exists in a repo's ``.codegraph/`` directory.
- Every repo record carries ``indexed_commit`` (the git HEAD at index time);
  verification requires exact equality — never "up to date" self-reports.
- Verification re-runs sentinel queries: symbols recorded as deleted must
  yield zero hits, core symbols must still resolve.
- The caller report maps the nine required targets to their query hits and
  registers the known RuntimeContext/runtime_policy bypass call sites as
  blocking findings (fixes belong to phase C/D work units, not this card).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from uc.casfile import cas_update, exclusive_publish, sha256_bytes

DEFAULT_REPOS = {
    "revenue": lambda root: root,
    "filing": lambda root: root.parent / "filing-fetch",
    "wiki": lambda root: root.parent / "company-wiki",
}

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

CALLER_TARGETS = {
    "revenue": [
        "prepare_source",  # source preparation entrypoint
        "publication_registry",  # publication registry writes
        "daily_t2_runner",  # dynamic runner (representative)
        "closure_gate",  # dynamic runner (representative)
    ],
    "filing": [
        "validate_handle",  # filing handle validation
        "_handle_from_resolution",  # filing handle resolution
    ],
    "wiki": [
        "CatalogStore",  # writer initializer (read-path hazard)
        "_scan_root_v1",  # v1 scanner
        "RootPolicy",  # root policy flags
        "artifact_bindings",  # shadow binding table
        "ProcessingDemand",  # required but expected missing (registered)
        "SourceResolver",  # resolver with runtime_policy default
    ],
}

# Sentinel matching is kind-filtered: the sentinel NAMES appear as string
# literals inside this module and the freeze payload, which fuzzy query
# matches as variable nodes — only real code objects count as present.
ABSENT_KINDS = {"function", "class", "method", "module"}
PRESENT_KINDS = {"function", "class", "method", "file", "module"}

DEFAULT_SENTINELS = {
    "absent": {
        "revenue": ["accuracy_tracker"],
        "filing": [
            "__definitely_absent_zzz"
        ],  # no historical symbol deletions; absence-oracle probe
        "wiki": ["reuse_latest_policy"],
    },
    "present": {
        "revenue": ["prepare_source", "publication_registry"],
        "filing": ["validate_handle"],
        "wiki": ["SourceResolver", "CatalogStore"],
    },
}

# Known runtime_policy bypass call sites (audit + CA-003 preflight 发现 11).
# These are REGISTERED as blocking findings; fixes belong to phase C/D.
RUNTIME_POLICY_BYPASSES = [
    {
        "repo": "wiki",
        "file": "src/company_wiki/source_catalog/acquisition.py",
        "lines": [308, 396],
        "pattern": "SourceResolver(self.catalog).resolve(...) without runtime_policy",
    },
    {
        "repo": "wiki",
        "file": "src/company_wiki/source_catalog/canonical_writer.py",
        "lines": [157, 205],
        "pattern": "SourceResolver(self.catalog).resolve(...) without runtime_policy",
    },
    {
        "repo": "wiki",
        "file": "src/company_wiki/source_catalog/close_gap.py",
        "lines": [403],
        "pattern": "SourceResolver(self.catalog).resolve(...) without runtime_policy",
    },
]


class IndexLockError(Exception):
    """Another index writer holds a .codegraph lock; the exclusive window is closed."""


class CodeGraphError(Exception):
    """The codegraph CLI failed."""


def _cli_path() -> Path:
    override = os.environ.get("CODEGRAPH_CLI")
    if override:
        return Path(override)
    return Path.home() / "nodejs" / "codegraph.ps1"


def _shell() -> str:
    """Resolve a PowerShell host for running the .ps1 CLI (Python subprocess
    PATH may differ from the interactive shell's)."""
    candidate = shutil.which("pwsh")
    if candidate:
        return candidate
    for fixed in (
        r"C:\Program Files\PowerShell\7\pwsh.exe",
        r"C:\Program Files\PowerShell\7-preview\pwsh.exe",
    ):
        if Path(fixed).is_file():
            return fixed
    return "powershell.exe"  # Windows PowerShell 5.1 fallback


def _cg(args: list[str], cwd: Path | None = None, timeout: int = 3600) -> str:
    """Run the codegraph CLI via a PowerShell host; returns clean
    (ANSI-stripped) stdout."""
    proc = subprocess.run(
        [
            _shell(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(_cli_path()),
            *args,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        cwd=str(cwd) if cwd else None,
    )
    if proc.returncode != 0:
        raise CodeGraphError(
            f"codegraph {' '.join(args[:2])} rc={proc.returncode}: "
            f"{proc.stderr.strip()[-300:]}"
        )
    return _ANSI_RE.sub("", proc.stdout)


def codegraph_version() -> str:
    return _cg(["--version"], timeout=120).strip().splitlines()[0].strip()


def _git_head(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if proc.returncode != 0:
        raise CodeGraphError(f"git rev-parse failed on {repo}")
    return proc.stdout.strip()


def _assert_exclusive(repo: Path) -> None:
    cg_dir = repo / ".codegraph"
    if cg_dir.is_dir():
        locks = [p for p in cg_dir.iterdir() if p.name.endswith(".lock")]
        if locks:
            raise IndexLockError(
                f"codegraph lock present in {repo}: {[p.name for p in locks]}"
            )


def index_repo(repo: Path, force: bool = True) -> dict[str, Any]:
    """Exclusive re-index of one repo; returns the machine status record."""
    _assert_exclusive(repo)
    _cg(["index", "-f", "-q", str(repo)])
    status_raw = _cg(["status", "-j", str(repo)], timeout=600)
    status = json.loads(status_raw)
    return {
        "path": str(repo),
        "indexed_commit": _git_head(repo),
        "codegraph_version": codegraph_version(),
        "file_count": status.get("fileCount"),
        "node_count": status.get("nodeCount"),
        "edge_count": status.get("edgeCount"),
        "db_size_bytes": status.get("dbSizeBytes"),
        "backend": status.get("backend"),
    }


def _query_hits(repo: Path, symbol: str) -> list[dict[str, Any]]:
    raw = _cg(["query", "-j", symbol, "-p", str(repo), "-l", "50"], timeout=600)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    hits: list[dict[str, Any]] = []
    for item in payload:
        node = item.get("node") if isinstance(item, dict) else None
        if not isinstance(node, dict):
            continue
        hits.append(
            {
                "name": node.get("name"),
                "kind": node.get("kind"),
                "file": node.get("filePath"),
                "line": node.get("startLine"),
            }
        )
    return hits


def build_caller_report(root: Path) -> dict[str, Any]:
    """Query hits per target plus the registered bypass findings."""
    targets: dict[str, Any] = {}
    for repo_name, symbols in CALLER_TARGETS.items():
        repo = DEFAULT_REPOS[repo_name](root)
        targets[repo_name] = {symbol: _query_hits(repo, symbol) for symbol in symbols}
    return {
        "targets": targets,
        "runtime_policy_bypass_findings": RUNTIME_POLICY_BYPASSES,
        "blocking_findings_registered": [
            {
                "id": "BYPASS-001",
                "severity": "blocking",
                "summary": "SourceResolver default-constructs runtime_policy=None at "
                "acquisition.py:308/396, canonical_writer.py:157/205, close_gap.py:403 — "
                "resolve may run v2 while ensure/close-gap re-resolve falls back to v1. "
                "Fix belongs to phase C/D work units; registered here per CA-003.",
            }
        ],
    }


def freeze(
    root: Path,
    output: Path,
    sentinels: dict[str, Any] | None = None,
    force_sha256: str | None = None,
) -> str:
    """Exclusive three-repo re-index + caller report; publish the freeze once
    (or CAS-replace with force_sha256)."""
    repos: dict[str, dict[str, Any]] = {}
    for name, resolver in DEFAULT_REPOS.items():
        repos[name] = index_repo(resolver(root))
    payload = {
        "schema_version": 1,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "codegraph_version": codegraph_version(),
        "repos": repos,
        "sentinels": sentinels or DEFAULT_SENTINELS,
        "caller_report": build_caller_report(root),
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    if force_sha256 is not None:
        return cas_update(output, data, force_sha256)
    if not exclusive_publish(output, data):
        raise FileExistsError(
            f"codegraph freeze already exists at {output}; pass force_sha256 to CAS-replace"
        )
    return sha256_bytes(data)


def verify(root: Path, freeze_path: Path) -> list[str]:
    """Exact-equality verification: indexed commits, index statistics, sentinel
    queries.  Returns drift descriptions (empty = fresh)."""
    payload = json.loads(freeze_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"unsupported freeze schema {payload.get('schema_version')!r}")
    problems: list[str] = []
    for repo_name, record in payload.get("repos", {}).items():
        repo = DEFAULT_REPOS[repo_name](root)
        head = _git_head(repo)
        if head != record["indexed_commit"]:
            problems.append(
                f"{repo_name}: indexed_commit {record['indexed_commit'][:12]}… "
                f"!= current HEAD {head[:12]}…"
            )
        status_raw = _cg(["status", "-j", str(repo)], timeout=600)
        try:
            status = json.loads(status_raw)
        except json.JSONDecodeError:
            problems.append(f"{repo_name}: status output unreadable")
            continue
        stat_fields = {
            "fileCount": "file_count",
            "nodeCount": "node_count",
            "edgeCount": "edge_count",
        }
        for status_field, record_field in stat_fields.items():
            if status.get(status_field) != record.get(record_field):
                problems.append(
                    f"{repo_name}: index statistic drift: {status_field} "
                    f"{status.get(status_field)} != {record.get(record_field)}"
                )
    sentinels = payload.get("sentinels", {})
    for repo_name, symbols in sentinels.get("absent", {}).items():
        repo = DEFAULT_REPOS[repo_name](root)
        for symbol in symbols:
            hits = [h for h in _query_hits(repo, symbol) if h["kind"] in ABSENT_KINDS]
            if hits:
                problems.append(
                    f"{repo_name}: deleted symbol '{symbol}' present in index: "
                    f"{hits[:3]}"
                )
    for repo_name, symbols in sentinels.get("present", {}).items():
        repo = DEFAULT_REPOS[repo_name](root)
        for symbol in symbols:
            hits = [h for h in _query_hits(repo, symbol) if h["kind"] in PRESENT_KINDS]
            if not hits:
                problems.append(
                    f"{repo_name}: core symbol '{symbol}' missing from index"
                )
    return problems
