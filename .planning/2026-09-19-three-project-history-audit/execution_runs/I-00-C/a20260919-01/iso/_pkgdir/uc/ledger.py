"""Side-effect ledger and independent oracle (CA-106).

A JSONL journal of side-effect events (provider/parser/LLM/worker/artifact
reads, DB/DDL/migration/commit writes, lock waits, root fingerprints).  The
oracle derives evidence from the OS/filesystem (root file count/bytes/mtime
snapshots, sqlite size/mtime) rather than trusting the subject's own summary.

Privacy: full paths are never stored — each entry carries the path's SHA-256
plus its basename, so privacy holds while hashes remain verifiable.

Single writer: appends go through the unit lock (uc.lock) so concurrent
writers cannot interleave records.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENTRY_KINDS = {
    "provider_discover",
    "provider_fetch",
    "canonical_write",
    "external_root_write",
    "parser_call",
    "llm_call",
    "artifact_read",
    "db_write",
    "ddl",
    "migration",
    "commit",
    "lock_wait",
    "root_fingerprint",
}


def _path_token(path: str | Path) -> dict[str, str]:
    raw = str(path)
    return {
        "path_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "basename": Path(raw).name,
    }


def root_fingerprint(root: Path) -> dict[str, Any]:
    """OS-level snapshot: file count, bytes, mtime bounds, per-file tokens."""
    if not root.is_dir():
        return {"path": _path_token(root), "exists": False}
    files = sorted(p for p in root.rglob("*") if p.is_file())
    return {
        "path": _path_token(root),
        "exists": True,
        "file_count": len(files),
        "total_bytes": sum(p.stat().st_size for p in files),
        "mtime_min": min((p.stat().st_mtime for p in files), default=0.0),
        "mtime_max": max((p.stat().st_mtime for p in files), default=0.0),
        "file_tokens": [_path_token(p) for p in files],
    }


def diff_fingerprints(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Independent oracle verdict over two root snapshots."""
    before_tokens = {t["path_sha256"] for t in before.get("file_tokens", [])}
    after_tokens = {t["path_sha256"] for t in after.get("file_tokens", [])}
    return {
        "path": before.get("path"),
        "file_count_delta": after.get("file_count", 0) - before.get("file_count", 0),
        "bytes_delta": after.get("total_bytes", 0) - before.get("total_bytes", 0),
        "added_files": len(after_tokens - before_tokens),
        "removed_files": len(before_tokens - after_tokens),
        "unchanged": not (
            after.get("file_count") != before.get("file_count")
            or after.get("total_bytes") != before.get("total_bytes")
            or before_tokens != after_tokens
        ),
    }


def append_entry(
    ledger_path: Path,
    kind: str,
    role: str | None,
    detail: dict[str, Any] | None,
) -> None:
    """Append one entry; single-writer discipline is the caller's lock duty."""
    if kind not in ENTRY_KINDS:
        raise ValueError(f"unknown ledger kind: {kind!r}")
    entry = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "role": role,
        "detail": detail or {},
    }
    with open(ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def read_ledger(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def count_by_kind(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["kind"]] = counts.get(entry["kind"], 0) + 1
    return counts


def verify_summary(
    entries: list[dict[str, Any]],
    declared: dict[str, int],
) -> list[str]:
    """Compare declared side-effect counts against the ledger.  Declared keys
    must match exactly; extra ledger events are reported (never dropped)."""
    problems: list[str] = []
    measured = count_by_kind(entries)
    for key, value in sorted(declared.items()):
        if measured.get(key, 0) != value:
            problems.append(
                f"declared {key}={value} but ledger measured {measured.get(key, 0)}"
            )
    for key in sorted(set(measured) - set(declared)):
        problems.append(f"ledger has {measured[key]} unclaimed {key} event(s)")
    return problems
