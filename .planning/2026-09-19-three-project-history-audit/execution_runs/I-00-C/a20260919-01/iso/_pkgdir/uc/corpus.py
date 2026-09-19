"""ZR-003 golden corpus registry and verifier.

A golden corpus registry registers production counterexample samples as a
desensitized set: the committed JSON carries only anchor names, relative
paths, content hashes and expected entity/role/period metadata.  Sample
bytes and absolute user paths never enter the repository.

``verify_golden_corpus`` re-reads every sample through read-only open calls
and recomputes sha256 + size; any drift (tamper, missing file, unresolved
anchor, leaked bytes inside a scanned directory) is returned as a problem
string.  Missing samples/anchor roots surface as explicit problems
(blocked-style semantics) instead of crashes, per the ZR-003 registry's
"样本缺失=>blocked" rule.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
REPO_ROOT = Path(__file__).resolve().parents[3]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_anchor(
    anchor: dict[str, Any],
    *,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> Path | None:
    """Resolve an anchor definition to a filesystem root, or None."""
    kind = anchor.get("kind")
    env = os.environ if environ is None else environ
    if kind == "repo_relative":
        return (repo_root / str(anchor["path"])).resolve(strict=False)
    if kind == "explicit":
        return Path(str(anchor["path"])).expanduser().resolve(strict=False)
    if kind == "env":
        value = env.get(str(anchor["var"]))
        if not value:
            return None
        return Path(value).expanduser().resolve(strict=False)
    if kind == "local_config":
        config_path = anchor.get("config")
        if not config_path:
            return None
        full = (repo_root / str(config_path)).resolve(strict=False)
        if not full.exists():
            return None
        data = json.loads(full.read_text(encoding="utf-8"))
        value = data.get(str(anchor.get("key")))
        if not value:
            return None
        return Path(str(value)).expanduser().resolve(strict=False)
    return None


def verify_golden_corpus(
    corpus_path: Path,
    *,
    leak_scan_dirs: list[Path] | None = None,
    repo_root: Path = REPO_ROOT,
    environ: dict[str, str] | None = None,
) -> list[str]:
    """Verify a golden corpus registry.  Returns problems (empty = OK)."""
    if not corpus_path.exists():
        return [f"corpus registry missing: {corpus_path}"]
    problems: list[str] = []
    try:
        data = json.loads(corpus_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"corpus unreadable: {exc}"]
    if not isinstance(data, dict):
        return ["corpus root is not an object"]
    if data.get("schema_version") != SCHEMA_VERSION:
        return [f"schema_version {data.get('schema_version')!r} != {SCHEMA_VERSION}"]

    anchors = data.get("anchors") or {}
    roots: dict[str, Path | None] = {}
    for name, definition in anchors.items():
        roots[name] = resolve_anchor(definition, repo_root=repo_root, environ=environ)

    samples = data.get("samples") or []
    for sample in samples:
        sample_id = sample.get("sample_id", "<unnamed>")
        anchor_name = sample.get("anchor")
        root = roots.get(anchor_name)
        if root is None:
            problems.append(f"{sample_id}: anchor {anchor_name!r} unresolved")
            continue
        rel = sample.get("rel_path", "")
        path = (root / rel).resolve(strict=False) if rel else None
        if path is None or not path.is_file():
            problems.append(f"{sample_id}: sample missing: {anchor_name}/{rel}")
            continue
        size_before = path.stat().st_size
        mtime_before = path.stat().st_mtime_ns
        digest = _sha256_file(path)
        size_after = path.stat().st_size
        mtime_after = path.stat().st_mtime_ns
        if digest != sample.get("sha256"):
            problems.append(f"{sample_id}: sha256 mismatch ({digest[:16]}...)")
        if size_before != sample.get("byte_size"):
            problems.append(
                f"{sample_id}: byte_size drift ({size_before} != {sample.get('byte_size')})"
            )
        if (size_before, mtime_before) != (size_after, mtime_after):
            problems.append(f"{sample_id}: file changed while being verified")

    sample_hashes = {sample.get("sha256") for sample in samples}
    for directory in leak_scan_dirs or []:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            digest = _sha256_file(path)
            if digest in sample_hashes:
                problems.append(
                    f"sample bytes leaked into scanned dir: {path} ({digest})"
                )
    return problems
