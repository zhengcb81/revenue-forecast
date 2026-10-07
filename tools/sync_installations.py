"""Hash-check or atomically synchronize the installable revenue skill.

Packaging responsibility (G3-RF-ASSURANCE): the package is delimited by what
the skill's own entry points actually need — ``SKILL.md``, ``agents/``,
``config/``, ``references/`` and ``scripts/``.  Repository engineering
controls (``tools/``, ``tests/``, ``assurance/``, ``audit_review/``,
``.github/``) stay in the repository: an installation that was byte-equal
to a copy of them was never thereby usable, and copying the engineering
control plane into every installation is not a fix.  A static closure scan
of the shipped runtime confirms nothing under it imports or opens
``tests/`` or ``tools/``.

``check`` (the default) never writes.  An explicit ``--apply`` updates only
the files this package owns, staging them under a tmp directory and
replacing them one at a time, so unknown files, user configuration,
``output`` and any repository-only residue already on disk survive.
``installation_diff`` compares the responsible runtime only: residue is
neither drift nor a licence to keep shipping it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


SKILL_NAME = "revenue-forecast"
ROOT_FILES = (".gitignore", "CHANGELOG.md", "SKILL.md")
# The runtime closure of the skill entry points.  ``tests/`` is deliberately
# absent: the repository's engineering tests read repo-only ``tools/`` and
# are not part of a distribution package.
ROOT_DIRECTORIES = ("agents", "config", "references", "scripts")
IGNORED_PARTS = {"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
PRESERVED_INSTALLATION_DIRECTORIES = {"output"}
# Phase 6 B3 (F-08): every supported install root is a default check target so
# a drift in any one of them cannot be silently missed.
DEFAULT_DESTINATIONS = (
    Path.home() / ".agents" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".codex" / "skills",
)


def installable_files(root: Path) -> list[Path]:
    """Return the closed set of files this skill package owns.

    That set is the runtime closure of the skill's entry points: the root
    files plus ``agents/``, ``config/``, ``references/`` and ``scripts/``.
    Repository-only engineering controls are never part of it.
    """
    files = [root / name for name in ROOT_FILES]
    for directory in ROOT_DIRECTORIES:
        base = root / directory
        if not base.is_dir():
            raise FileNotFoundError(f"missing installable directory: {base}")
        files.extend(
            path
            for path in base.rglob("*")
            if path.is_file()
            and not (set(path.relative_to(root).parts) & IGNORED_PARTS)
            and path.suffix not in {".pyc", ".pyo"}
        )
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing installable file: {missing[0]}")
    return sorted(set(files))


def manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in installable_files(root)
    }


def _installed_manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
        and not (set(path.relative_to(root).parts) & IGNORED_PARTS)
        and not (set(path.relative_to(root).parts) & PRESERVED_INSTALLATION_DIRECTORIES)
        and path.suffix not in {".pyc", ".pyo"}
    }


def installation_diff(canonical: Path, destination: Path) -> list[str]:
    """Drift of the RESPONSIBLE runtime only.

    Only files this package owns are compared.  Anything else in the
    installation — old repository-only residue, user configuration,
    ``output`` — is outside the comparison: it is neither drift nor a
    licence to keep shipping it.  Owned files that are missing or whose
    bytes differ are reported.
    """
    expected = manifest(canonical)
    target = destination / SKILL_NAME
    if not target.is_dir():
        # No installation at this target = nothing to drift (CI runners and
        # fresh machines have no copies; pre-commit on the author machine does).
        return []
    actual = _installed_manifest(target)
    return sorted(key for key, digest in expected.items() if actual.get(key) != digest)


def sync_installation(canonical: Path, destination: Path) -> None:
    """Update the files this package owns, in place, through a tmp stage.

    Every owned file is copied into a staging directory under ``destination``
    first and then swapped in one atomic ``os.replace``.  Nothing else in the
    installation is written or removed: unknown files, user configuration,
    ``output`` and any repository-only residue left by an older installation
    all survive, and there is no whole-directory replacement.
    """
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / SKILL_NAME
    with tempfile.TemporaryDirectory(
        prefix=f".{SKILL_NAME}-stage-", dir=destination
    ) as directory:
        staged = Path(directory) / SKILL_NAME
        staged.mkdir()
        for path in installable_files(canonical):
            relative = path.relative_to(canonical)
            output = staged / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, output)
        target.mkdir(parents=True, exist_ok=True)
        for source in staged.rglob("*"):
            if not source.is_file():
                continue
            final = target / source.relative_to(staged)
            final.parent.mkdir(parents=True, exist_ok=True)
            temporary = final.with_name(final.name + f".{os.getpid()}.syncing")
            try:
                shutil.copy2(source, temporary)
                os.replace(temporary, final)
            finally:
                temporary.unlink(missing_ok=True)


def import_installation(source: Path, canonical: Path) -> None:
    """Copy the installable skill surface into a canonical source repository.

    Repository-only files such as ``tools/`` remain untouched. Canonical files
    absent from the source are not deleted; callers must audit the resulting
    Git diff before committing.
    """

    source = source.resolve(strict=True)
    canonical = canonical.resolve(strict=True)
    if source == canonical:
        raise ValueError("source installation and canonical root must differ")
    with tempfile.TemporaryDirectory(prefix=f".{SKILL_NAME}-import-") as directory:
        staged_root = Path(directory) / SKILL_NAME
        staged_root.mkdir()
        for path in installable_files(source):
            relative = path.relative_to(source)
            staged = staged_root / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, staged)
        for staged in staged_root.rglob("*"):
            if not staged.is_file():
                continue
            relative = staged.relative_to(staged_root)
            output = canonical / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(output.name + f".{os.getpid()}.importing")
            try:
                shutil.copy2(staged, temporary)
                os.replace(temporary, output)
            finally:
                temporary.unlink(missing_ok=True)


def unique_destinations(destinations: list[Path]) -> list[Path]:
    """Deduplicate destinations that resolve to the same installed skill."""

    result: list[Path] = []
    seen: set[Path] = set()
    for destination in destinations:
        resolved = destination.resolve()
        target = (resolved / SKILL_NAME).resolve(strict=False)
        if target in seen:
            continue
        seen.add(target)
        result.append(resolved)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check or synchronize installed revenue-forecast skills"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--apply", action="store_true", help="apply an atomic whole-skill sync"
    )
    mode.add_argument(
        "--print-manifest",
        action="store_true",
        help="print the canonical SHA-256 manifest",
    )
    mode.add_argument(
        "--import-from",
        type=Path,
        help="import an installed skill into the canonical repository",
    )
    parser.add_argument(
        "--canonical", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--destination", type=Path, action="append")
    args = parser.parse_args()
    canonical = args.canonical.resolve()
    if args.print_manifest:
        print(json.dumps(manifest(canonical), indent=2, sort_keys=True))
        return 0
    if args.import_from is not None:
        import_installation(args.import_from, canonical)
    destinations = unique_destinations(args.destination or list(DEFAULT_DESTINATIONS))
    if args.apply:
        for destination in destinations:
            sync_installation(canonical, destination.resolve())
    failed = False
    expected_count = len(manifest(canonical))
    for destination in destinations:
        differences = installation_diff(canonical, destination.resolve())
        if differences:
            failed = True
            print(f"DIFF {destination}: {len(differences)} files")
            for path in differences[:50]:
                print(f"  {path}")
        else:
            print(f"MATCH {destination}: {expected_count} files")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
