"""Owned runtime inventory shared by RF diagnostics and installation tooling.

This module lives inside the distributed runtime. It reads only the previously
owned skill files and never includes output, tests, tools or cache residue.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT_FILES = (".gitignore", "CHANGELOG.md", "SKILL.md")
ROOT_DIRECTORIES = ("agents", "config", "references", "scripts")
IGNORED_PARTS = {"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
# Historical engineering fixture now lives under tools/legacy/. Existing
# installations may retain the old copy; it is neither owned nor imported.
RETIRED_RUNTIME_FILES = {"scripts/processing_demand.py"}


def installable_files(root: Path) -> list[Path]:
    """Return the closed file set owned by this skill's runtime package."""
    files = [root / name for name in ROOT_FILES]
    for directory in ROOT_DIRECTORIES:
        base = root / directory
        if not base.is_dir():
            raise FileNotFoundError(f"missing installable directory: {base}")
        files.extend(path for path in base.rglob("*")
            if path.is_file() and not (set(path.relative_to(root).parts) & IGNORED_PARTS)
            and path.relative_to(root).as_posix() not in RETIRED_RUNTIME_FILES
            and path.suffix not in {".pyc", ".pyo"})
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing installable file: {missing[0]}")
    return sorted(set(files))


def manifest(root: Path) -> dict[str, str]:
    """Bind both the owned path inventory and each actual file's bytes."""
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in installable_files(root)}


def manifest_sha256(root: Path) -> str:
    content = json.dumps(manifest(root), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(content).hexdigest()
