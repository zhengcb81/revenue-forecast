"""Hash-check or atomically synchronize the installable revenue skill."""

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
ROOT_DIRECTORIES = ("agents", "config", "references", "scripts", "tests")
IGNORED_PARTS = {"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
PRESERVED_INSTALLATION_DIRECTORIES = {"output"}


def installable_files(root: Path) -> list[Path]:
    """Return the closed set of files that belongs in an installed copy."""
    files = [root / name for name in ROOT_FILES]
    for directory in ROOT_DIRECTORIES:
        base = root / directory
        if not base.is_dir():
            raise FileNotFoundError(f"missing installable directory: {base}")
        files.extend(
            path for path in base.rglob("*")
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
        and not (
            set(path.relative_to(root).parts)
            & PRESERVED_INSTALLATION_DIRECTORIES
        )
        and path.suffix not in {".pyc", ".pyo"}
    }


def installation_diff(canonical: Path, destination: Path) -> list[str]:
    expected = manifest(canonical)
    target = destination / SKILL_NAME
    if not target.is_dir():
        return ["<missing installation>"]
    actual = _installed_manifest(target)
    keys = sorted(set(expected) | set(actual))
    return [key for key in keys if expected.get(key) != actual.get(key)]


def sync_installation(canonical: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / SKILL_NAME
    with tempfile.TemporaryDirectory(prefix=f".{SKILL_NAME}-stage-", dir=destination) as directory:
        staged = Path(directory) / SKILL_NAME
        staged.mkdir()
        for path in installable_files(canonical):
            relative = path.relative_to(canonical)
            output = staged / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, output)
        backup = destination / f".{SKILL_NAME}-backup-{os.getpid()}"
        if backup.exists():
            shutil.rmtree(backup)
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(staged, target)
            if backup.exists():
                for directory in PRESERVED_INSTALLATION_DIRECTORIES:
                    preserved = backup / directory
                    restored = target / directory
                    if preserved.exists() and not restored.exists():
                        os.replace(preserved, restored)
        except Exception:
            if backup.exists() and not target.exists():
                os.replace(backup, target)
            raise
        if backup.exists():
            shutil.rmtree(backup)


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
    parser = argparse.ArgumentParser(description="Check or synchronize installed revenue-forecast skills")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="apply an atomic whole-skill sync")
    mode.add_argument("--print-manifest", action="store_true", help="print the canonical SHA-256 manifest")
    mode.add_argument(
        "--import-from",
        type=Path,
        help="import an installed skill into the canonical repository",
    )
    parser.add_argument("--canonical", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destination", type=Path, action="append")
    args = parser.parse_args()
    canonical = args.canonical.resolve()
    if args.print_manifest:
        print(json.dumps(manifest(canonical), indent=2, sort_keys=True))
        return 0
    if args.import_from is not None:
        import_installation(args.import_from, canonical)
    destinations = unique_destinations(
        args.destination
        or [Path.home() / ".agents" / "skills", Path.home() / ".claude" / "skills"]
    )
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
