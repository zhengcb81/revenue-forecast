"""Plan-input manifest: build a machine manifest from the frozen specs and
re-verify every frozen input offline.

The expected hashes are NOT hardcoded here.  They are parsed, at build and at
verify time, from the frozen specification tables themselves:

- ``audit_review/README.md`` §13         — 8 authoritative hashes with paths
- ``.../PLAN_MANIFEST.md`` §3 + §4       — 14 content files + 5 annex hashes
- ``.../input_snapshot.md``              — 30 input files (17 old FCAP + 13 zijin)

The annex (§4) table carries hashes but no paths; each annex hash is resolved
against the README §13 path map (the two ``scenario_matrix.md`` files have
distinct hashes, so the match is unambiguous).  Spec sources cross-check each
other before they are trusted: input_snapshot.md must match the hash recorded
in PLAN_MANIFEST §3, and the zijin PLAN_MANIFEST.md must match the hash
recorded in input_snapshot.md.  Every entry is frozen as
``path, size, mtime, SHA-256`` and re-verifiable offline.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from uc.casfile import cas_update, exclusive_publish, sha256_bytes, sha256_file

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MTIME_FMT = "%Y-%m-%d %H:%M:%S"

# Frozen-spec source locations relative to the repo root.
README_PATH = Path("audit_review/README.md")
PLAN_MANIFEST_PATH = Path(
    "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/PLAN_MANIFEST.md"
)
INPUT_SNAPSHOT_PATH = Path(
    "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/input_snapshot.md"
)
ZIJIN_PLAN_MANIFEST_PATH = Path(
    "audit_review/2026-08-13_zijin_data_lake_remediation_plan/PLAN_MANIFEST.md"
)

# input_snapshot.md section heading -> base dir for the rows below it.
SNAPSHOT_SECTIONS = {
    "2026-08-09_full_completion_assurance_plan": Path(
        "audit_review/2026-08-09_full_completion_assurance_plan"
    ),
    "2026-08-13_zijin_data_lake_remediation_plan": Path(
        "audit_review/2026-08-13_zijin_data_lake_remediation_plan"
    ),
}

CONTENT_BASE_DIR = Path("audit_review/2026-08-13_three_repo_completion_rebaseline_plan")

EXPECTED_ANNEX_COUNT = 5


@dataclass
class ManifestEntry:
    rel_path: str
    sha256: str
    size: int | None = None
    mtime: str | None = None


@dataclass
class SpecSource:
    rel_path: str
    role: str
    sha256: str  # hash of the source file itself, frozen at build time


@dataclass
class Manifest:
    schema_version: int
    built_at_utc: str
    repo_root: str
    sources: list[SpecSource]
    entries: list[ManifestEntry]
    control_page_sha256: str
    extra: dict[str, Any] = field(default_factory=dict)


class ManifestError(Exception):
    """A frozen spec table is unreadable, ambiguous, or self-inconsistent."""


def _table_rows(markdown: str) -> list[list[str]]:
    """Extract markdown table data rows (skip the |---|---| separator)."""
    rows: list[list[str]] = []
    for line in markdown.splitlines():
        if "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def _norm(rel: str | Path) -> str:
    """Normalize a repo-relative path to forward slashes (cross-table key)."""
    return str(rel).replace("\\", "/")


def _cell(cells: list[str], index: int) -> str:
    try:
        return cells[index].strip().strip("`")
    except IndexError as exc:
        raise ManifestError(f"table row missing cell {index}: {cells!r}") from exc


def _parse_readme_hashes(text: str) -> dict[str, str]:
    """README §13: ``path -> sha256`` for the 8 authoritative annex rows."""
    path_to_hash: dict[str, str] = {}
    for cells in _table_rows(text):
        if len(cells) < 3:
            continue
        digest = _cell(cells, 2)
        if not SHA256_RE.fullmatch(digest):
            continue
        path_to_hash[_norm(_cell(cells, 1))] = digest
    if not path_to_hash:
        raise ManifestError("README §13 yielded no hash rows")
    return path_to_hash


def _parse_plan_manifest(text: str) -> tuple[list[ManifestEntry], list[str]]:
    """PLAN_MANIFEST §3 content rows (name|bytes|sha) and §4 annex hashes in
    table order (the §4 hash column is the second cell)."""
    content: list[ManifestEntry] = []
    annex_hashes: list[str] = []
    for cells in _table_rows(text):
        digest_col2 = _cell(cells, 2) if len(cells) >= 3 else ""
        digest_col1 = _cell(cells, 1) if len(cells) >= 2 else ""
        if SHA256_RE.fullmatch(digest_col2):
            name = _cell(cells, 0)
            size_text = cells[1].strip().replace(",", "")
            size = int(size_text) if size_text.isdigit() else None
            content.append(ManifestEntry(rel_path=name, sha256=digest_col2, size=size))
        elif SHA256_RE.fullmatch(digest_col1):
            annex_hashes.append(digest_col1)
    if not content:
        raise ManifestError("PLAN_MANIFEST §3 yielded no content rows")
    if len(annex_hashes) != EXPECTED_ANNEX_COUNT:
        raise ManifestError(
            f"PLAN_MANIFEST §4 annex rows: {len(annex_hashes)} "
            f"!= expected {EXPECTED_ANNEX_COUNT}"
        )
    return content, annex_hashes


def _parse_input_snapshot(text: str) -> list[ManifestEntry]:
    """input_snapshot.md: two sections of ``| file | bytes | sha | mtime |``."""
    entries: list[ManifestEntry] = []
    current_base: Path | None = None
    for line in text.splitlines():
        section = re.match(r"^##\s+`([0-9][0-9_a-z-]+)`\s*$", line)
        if section and section.group(1) in SNAPSHOT_SECTIONS:
            current_base = SNAPSHOT_SECTIONS[section.group(1)]
            continue
        if current_base is None or "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        digest = _cell(cells, 2)
        if not SHA256_RE.fullmatch(digest):
            continue
        name = _cell(cells, 0)
        size_text = _cell(cells, 1).replace(",", "")
        size = int(size_text) if size_text.isdigit() else None
        mtime = _cell(cells, 3) if len(cells) >= 4 else None
        entries.append(
            ManifestEntry(
                rel_path=_norm(current_base / name),
                sha256=digest,
                size=size,
                mtime=mtime,
            )
        )
    if not entries:
        raise ManifestError("input_snapshot.md yielded no rows")
    return entries


def load_spec_tables(repo_root: Path) -> tuple[list[SpecSource], list[ManifestEntry]]:
    """Read the frozen spec files and merge their entries.

    Duplicate rel_paths must agree exactly; annex hashes must resolve to
    README §13 paths; the spec sources cross-check each other's hashes.
    """
    readme_path = repo_root / README_PATH
    plan_manifest_path = repo_root / PLAN_MANIFEST_PATH
    snapshot_path = repo_root / INPUT_SNAPSHOT_PATH

    readme_text = readme_path.read_text(encoding="utf-8")
    plan_text = plan_manifest_path.read_text(encoding="utf-8")
    snapshot_text = snapshot_path.read_text(encoding="utf-8")

    path_to_hash = _parse_readme_hashes(readme_text)
    content, annex_hashes = _parse_plan_manifest(plan_text)
    snapshot_entries = _parse_input_snapshot(snapshot_text)

    # Resolve annex hashes (§4, no paths) against README §13 (paths).
    annex_entries: list[ManifestEntry] = []
    for annex_hash in annex_hashes:
        matches = [p for p, h in path_to_hash.items() if h == annex_hash]
        if len(matches) != 1:
            raise ManifestError(
                f"annex hash {annex_hash[:12]}… matches {len(matches)} README §13 "
                "path(s); expected exactly 1"
            )
        annex_entries.append(ManifestEntry(rel_path=matches[0], sha256=annex_hash))

    # Spec-source cross-checks (refuse to build from inconsistent specs).
    snapshot_hash_on_disk = sha256_file(snapshot_path)
    content_by_name = {entry.rel_path: entry for entry in content}
    if "input_snapshot.md" in content_by_name:
        expected_snapshot_hash = content_by_name["input_snapshot.md"].sha256
        if snapshot_hash_on_disk != expected_snapshot_hash:
            raise ManifestError(
                "input_snapshot.md hash does not match PLAN_MANIFEST §3 "
                f"({expected_snapshot_hash[:12]}… expected)"
            )
    zijin_manifest = next(
        (
            entry
            for entry in snapshot_entries
            if entry.rel_path.endswith("/PLAN_MANIFEST.md")
        ),
        None,
    )
    if zijin_manifest is not None:
        zijin_disk = sha256_file(repo_root / ZIJIN_PLAN_MANIFEST_PATH)
        if zijin_disk != zijin_manifest.sha256:
            raise ManifestError(
                "zijin PLAN_MANIFEST.md hash does not match input_snapshot.md"
            )

    merged: dict[str, ManifestEntry] = {}
    for entry in [
        *(ManifestEntry(rel_path=p, sha256=h) for p, h in path_to_hash.items()),
        *snapshot_entries,
        *(
            ManifestEntry(
                rel_path=_norm(CONTENT_BASE_DIR / entry.rel_path),
                sha256=entry.sha256,
                size=entry.size,
            )
            for entry in content
        ),
        *annex_entries,
    ]:
        existing = merged.get(entry.rel_path)
        if existing is not None:
            if existing.sha256 != entry.sha256 or (
                existing.size is not None
                and entry.size is not None
                and existing.size != entry.size
            ):
                raise ManifestError(
                    f"cross-source mismatch for {entry.rel_path}: "
                    f"{existing.sha256[:12]}… vs {entry.sha256[:12]}…"
                )
            if existing.size is None and entry.size is not None:
                existing.size = entry.size
            if existing.mtime is None and entry.mtime is not None:
                existing.mtime = entry.mtime
            continue
        merged[entry.rel_path] = entry

    sources = [
        SpecSource(_norm(README_PATH), "control-page-hashes", sha256_file(readme_path)),
        SpecSource(
            _norm(PLAN_MANIFEST_PATH), "plan-manifest", sha256_file(plan_manifest_path)
        ),
        SpecSource(
            _norm(INPUT_SNAPSHOT_PATH), "input-snapshot", sha256_file(snapshot_path)
        ),
    ]
    return sources, sorted(merged.values(), key=lambda e: e.rel_path)


def build(repo_root: Path, output: Path, force_sha256: str | None = None) -> str:
    """Build the machine manifest and publish it to ``output``.

    Publish is exclusive (bootstrap) unless ``force_sha256`` holds the current
    manifest hash, in which case the write is a CAS update.
    """
    sources, entries = load_spec_tables(repo_root)
    now = datetime.now(timezone.utc).isoformat()
    readme_hash = sha256_file(repo_root / README_PATH)
    manifest = Manifest(
        schema_version=1,
        built_at_utc=now,
        repo_root=str(repo_root),
        sources=sources,
        entries=entries,
        control_page_sha256=readme_hash,
    )
    payload = json.dumps(
        {
            "schema_version": manifest.schema_version,
            "built_at_utc": manifest.built_at_utc,
            "repo_root": manifest.repo_root,
            "control_page_sha256": manifest.control_page_sha256,
            "sources": [
                {"rel_path": s.rel_path, "role": s.role, "sha256": s.sha256}
                for s in manifest.sources
            ],
            "entries": [
                {
                    "rel_path": e.rel_path,
                    "sha256": e.sha256,
                    "size": e.size,
                    "mtime": e.mtime,
                }
                for e in manifest.entries
            ],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    if force_sha256 is not None:
        return cas_update(output, payload, force_sha256)
    if not exclusive_publish(output, payload):
        raise ManifestError(
            f"manifest already exists at {output}; pass its hash as force_sha256 "
            "to CAS-replace, or remove it for a fresh bootstrap"
        )
    return sha256_bytes(payload)


def _file_mtime_str(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime(MTIME_FMT)


def verify(repo_root: Path, manifest_path: Path) -> list[str]:
    """Re-verify every frozen input offline.  Returns drift descriptions
    (empty list = no drift).  Raises ManifestError on structural problems."""
    payload: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ManifestError(
            f"unsupported manifest schema {payload.get('schema_version')!r}"
        )
    problems: list[str] = []

    for source in payload.get("sources", []):
        path = repo_root / source["rel_path"]
        try:
            actual = sha256_file(path)
        except FileNotFoundError:
            problems.append(f"spec source missing: {source['rel_path']}")
            continue
        if actual != source["sha256"]:
            problems.append(
                f"spec source drift: {source['rel_path']} "
                f"({source['sha256'][:12]}… -> {actual[:12]}…)"
            )

    for entry in payload.get("entries", []):
        path = repo_root / entry["rel_path"]
        try:
            actual = sha256_file(path)
        except FileNotFoundError:
            problems.append(f"frozen input missing: {entry['rel_path']}")
            continue
        if actual != entry["sha256"]:
            problems.append(
                f"hash drift: {entry['rel_path']} "
                f"({entry['sha256'][:12]}… -> {actual[:12]}…)"
            )
        size = entry.get("size")
        if size is not None:
            try:
                if path.stat().st_size != int(size):
                    problems.append(
                        f"size drift: {entry['rel_path']} "
                        f"({size} -> {path.stat().st_size})"
                    )
            except OSError:
                problems.append(f"frozen input unreadable: {entry['rel_path']}")
        mtime = entry.get("mtime")
        if mtime:
            try:
                if _file_mtime_str(path) != mtime:
                    problems.append(
                        f"mtime drift: {entry['rel_path']} "
                        f"({mtime} -> {_file_mtime_str(path)})"
                    )
            except OSError:
                problems.append(f"frozen input unreadable: {entry['rel_path']}")

    readme_hash = payload.get("control_page_sha256")
    if readme_hash:
        actual_readme: str | None
        try:
            actual_readme = sha256_file(repo_root / README_PATH)
        except FileNotFoundError:
            actual_readme = None
        if actual_readme != readme_hash:
            problems.append(
                f"control page drift: {README_PATH} "
                f"({readme_hash[:12]}… -> {(actual_readme or 'missing')[:12]}…)"
            )
    return problems
