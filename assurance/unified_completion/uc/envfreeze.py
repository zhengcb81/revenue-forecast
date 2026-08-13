"""Environment freeze (CA-002): machine-recorded repo triplets, upstream,
dirty allowlist, toolchain, OS, installed skills, config fingerprints and a
read-only catalog fingerprint — with an exact-equality verification gate.

Design rules (from the CA-002 card):

- The gate is **exact equality**, never "baseline descendant": any recorded
  field that differs makes the current environment stale.
- `local-only` vs `pushed` is a verifiable classification: pushed = HEAD
  exists on the remote; local_only = the remote ref exists but differs;
  unverifiable = the remote could not be reached (network/infra) — recorded,
  never guessed.
- Git `dubious ownership` / unsafe-directory errors are classified as
  infrastructure errors (``infra_errors``), never silently folded into
  "no upstream" or a fake ancestry failure.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_REPOS = {
    "revenue": lambda root: root,
    "filing": lambda root: root.parent / "filing-fetch",
    "wiki": lambda root: root.parent / "company-wiki",
}

CONFIG_SUFFIXES = (".json", ".yaml", ".yml", ".toml", ".ini")
SKILLS_DIR = Path.home() / ".agents" / "skills"


class InfraError(Exception):
    """An infrastructure failure (e.g. git dubious ownership, unreachable
    remote) that must be recorded as such, never as an ancestry mismatch."""

    def __init__(self, message: str, kind: str) -> None:
        self.kind = kind
        super().__init__(message)


def _run_git(repo: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    stderr = proc.stderr.strip()
    if "dubious ownership" in stderr or "unsafe repository" in stderr:
        raise InfraError(
            f"git unsafe-directory on {repo}: {stderr}", "git-unsafe-directory"
        )
    return proc.returncode, proc.stdout.strip(), stderr


def _version(command: list[str]) -> str:
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        return (proc.stdout or proc.stderr).strip().splitlines()[0].strip()
    except (OSError, subprocess.SubprocessError, IndexError):
        return "unavailable"


def _sha256_file(path: Path) -> str | None:
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            while chunk := fh.read(1 << 20):
                digest.update(chunk)
    except FileNotFoundError:
        return None
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _remote_head(remote_url: str, branch: str) -> str:
    """Returns the remote ref sha, or raises InfraError when unreachable.

    Timeout is deliberately short: an unreachable remote must classify as
    ``unverifiable`` quickly, never stall the equality gate."""
    try:
        proc = subprocess.run(
            ["git", "ls-remote", remote_url, f"refs/heads/{branch}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
    except subprocess.TimeoutExpired as exc:
        raise InfraError(
            f"ls-remote {remote_url} timed out after 20s", "remote-unreachable"
        ) from exc
    if proc.returncode != 0:
        raise InfraError(
            f"ls-remote {remote_url} failed: {proc.stderr.strip()[-200:]}",
            "remote-unreachable",
        )
    line = proc.stdout.strip().splitlines()
    if not line:
        raise InfraError(
            f"remote {remote_url} has no refs/heads/{branch}", "remote-ref-missing"
        )
    return line[0].split()[0]


def _repo_facts(
    repo: Path,
    remote_lookup: Callable[[str, str], str] | None = None,
) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    rc, head, _ = _run_git(repo, ["rev-parse", "HEAD"])
    if rc != 0:
        raise InfraError(f"rev-parse HEAD failed on {repo}", "git-rev-parse")
    facts["head"] = head
    _rc, branch, _ = _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    facts["branch"] = branch
    rc, upstream, _ = _run_git(
        repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]
    )
    facts["upstream"] = upstream if rc == 0 else None
    rc, remote_url, _ = _run_git(repo, ["remote", "get-url", "origin"])
    facts["remote_url"] = remote_url if rc == 0 else None

    push_state: str
    remote_sha: str | None = None
    lookup = remote_lookup if remote_lookup is not None else _remote_head
    if facts["remote_url"] is None:
        push_state = "local_only"
    else:
        try:
            remote_sha = lookup(facts["remote_url"], branch)
            push_state = "pushed" if remote_sha == head else "local_only"
        except InfraError:
            push_state = "unverifiable"
    facts["remote_ref_sha"] = remote_sha
    facts["push_state"] = push_state

    _rc, status_out, _ = _run_git(repo, ["status", "--porcelain"])
    dirty = []
    for line in status_out.splitlines():
        if not line.strip():
            continue
        dirty.append({"status": line[:2], "path": line[3:]})
    facts["dirty"] = dirty
    return facts


def _filter_dirty(facts: dict[str, Any], dirty_ignore: list[str]) -> None:
    """Remove dirty entries under any ignore prefix.  The ignore list itself is
    part of the frozen payload, so changing it is itself a drift."""
    for repo_name, repo_facts in facts.get("repos", {}).items():
        kept = []
        for entry in repo_facts.get("dirty", []):
            path = entry["path"].replace("\\", "/")
            if any(path.startswith(prefix) for prefix in dirty_ignore):
                continue
            kept.append(entry)
        repo_facts["dirty"] = kept


def _skills_facts() -> dict[str, str]:
    facts: dict[str, str] = {}
    if not SKILLS_DIR.is_dir():
        return facts
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        for name in ("SKILL.md", "skill.md"):
            candidate = skill_dir / name
            if candidate.is_file():
                facts[skill_dir.name] = _sha256_file(candidate) or "unreadable"
                break
        else:
            facts[skill_dir.name] = "absent"
    return facts


def _config_facts(repo: Path) -> dict[str, str]:
    facts: dict[str, str] = {}
    config_dir = repo / "config"
    if not config_dir.is_dir():
        return facts
    for path in sorted(config_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in CONFIG_SUFFIXES:
            digest = _sha256_file(path)
            facts[path.relative_to(repo).as_posix()] = digest or "unreadable"
    return facts


def _catalog_facts(catalog_path: Path) -> dict[str, Any]:
    """Read-only fingerprint: size, mtime, sqlite page-1 hash, schema hash.
    Opens with ``mode=ro`` (the same mode as the product's own readonly
    canary): no writes to the DB; the -wal/-shm sidecars already exist and a
    read-only connection does not modify their contents.  Failures become
    notes, never writes and never fake values."""
    facts: dict[str, Any] = {"path": catalog_path.as_posix()}
    if not catalog_path.is_file():
        facts["available"] = False
        facts["note"] = "catalog file not found"
        return facts
    stat = catalog_path.stat()
    facts["available"] = True
    facts["size_bytes"] = stat.st_size
    facts["mtime"] = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(catalog_path, "rb") as fh:
            header = fh.read(4096)
        facts["page1_sha256"] = _sha256_bytes(header)
    except OSError as exc:
        facts["page1_sha256"] = f"unreadable: {exc}"
    try:
        conn = sqlite3.connect(
            f"file:{catalog_path.as_posix()}?mode=ro", uri=True, timeout=5
        )
        try:
            schema_rows = conn.execute(
                "SELECT type, name, sql FROM sqlite_master ORDER BY rowid"
            ).fetchall()
            facts["schema_sha256"] = _sha256_bytes(
                json.dumps(schema_rows, ensure_ascii=False, default=str).encode("utf-8")
            )
            facts["schema_objects"] = len(schema_rows)
            facts["schema_version"] = conn.execute("PRAGMA schema_version").fetchone()[
                0
            ]
        finally:
            conn.close()
    except sqlite3.Error as exc:
        facts["schema_sha256"] = f"unavailable: {exc}"
    return facts


def _runtime_policy_facts(wiki_root: Path) -> dict[str, Any]:
    policy = wiki_root / ".source_catalog" / "runtime_policy.json"
    if not policy.is_file():
        return {"available": False}
    return {
        "available": True,
        "sha256": _sha256_file(policy) or "unreadable",
        "mtime": datetime.fromtimestamp(policy.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }


def collect(
    root: Path,
    remote_lookup: Callable[[str, str], str] | None = None,
    catalog_path: Path | None = None,
    dirty_ignore: list[str] | None = None,
) -> dict[str, Any]:
    """Collect the live environment facts.  ``remote_lookup`` overrides the
    network ls-remote for tests; ``catalog_path`` overrides discovery;
    ``dirty_ignore`` lists repo-relative path prefixes excluded from the dirty
    allowlist (e.g. the freeze artifact's own directory)."""
    repos: dict[str, dict[str, Any]] = {}
    infra: list[dict[str, str]] = []
    for name, resolver in DEFAULT_REPOS.items():
        repo = resolver(root)
        try:
            repos[name] = _repo_facts(repo, remote_lookup)
        except InfraError as exc:
            repos[name] = {"infra_error": exc.kind, "note": str(exc)}
            infra.append({"repo": name, "kind": exc.kind, "note": str(exc)})
    ignore = dirty_ignore or []
    _filter_dirty({"repos": repos}, ignore)
    catalog = (
        catalog_path
        if catalog_path is not None
        else root.parent / "company-wiki" / ".source_catalog" / "catalog.sqlite3"
    )
    wiki_root = root.parent / "company-wiki"
    return {
        "schema_version": 1,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "dirty_ignore": ignore,
        "os": platform.platform(),
        "repos": repos,
        "toolchain": {
            "python": _version([sys.executable, "--version"]),
            "git": _version(["git", "--version"]),
            "node": _version(["node", "--version"]),
            "sqlite3": _version(["sqlite3", "--version"]),
        },
        "skills": _skills_facts(),
        "configs": {
            name: _config_facts(repo(root)) for name, repo in DEFAULT_REPOS.items()
        },
        "runtime_policy": _runtime_policy_facts(wiki_root),
        "catalog": _catalog_facts(catalog),
        "infra_errors": infra,
    }


def freeze(root: Path, output: Path, **overrides: Any) -> str:
    """Collect and publish the environment freeze exactly once (or CAS-replace
    with ``force_sha256``).  Returns the freeze content hash."""
    from uc.casfile import cas_update, exclusive_publish

    force = overrides.pop("force_sha256", None)
    payload = collect(root, **overrides)
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    if force is not None:
        return cas_update(output, data, force)
    if not exclusive_publish(output, data):
        raise FileExistsError(
            f"environment freeze already exists at {output}; pass force_sha256 to CAS-replace"
        )
    return _sha256_bytes(data)


def verify(freeze_payload: dict[str, Any], live_payload: dict[str, Any]) -> list[str]:
    """Exact-equality gate: every recorded field must match.  Returns drift
    descriptions (empty = environment matches the freeze).  ``collected_at_utc``
    is excluded (it is a timestamp of collection, not an environment fact)."""
    frozen = {k: v for k, v in freeze_payload.items() if k != "collected_at_utc"}
    live = {k: v for k, v in live_payload.items() if k != "collected_at_utc"}
    problems: list[str] = []
    for key in sorted(set(frozen) | set(live)):
        if key not in frozen:
            problems.append(f"live has unexpected section: {key}")
        elif key not in live:
            problems.append(f"freeze section missing live: {key}")
        elif frozen[key] != live[key]:
            problems.append(f"drift in section: {key}")
    return problems
