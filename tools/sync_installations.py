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

Selective installation (G5-RF-INSTALL): a repeatable ``--file <relative>``
restricts check, ``--plan`` and ``--apply`` to that subset of the installable
closure, ``--plan`` prints a zero-write ``rf-install-plan/1`` value, and
``--json`` prints exactly one ``rf-install-result/1`` value on stdout with
diagnostics on stderr.  Only files whose bytes actually differ are staged and
replaced, each replacement is a single atomic ``os.replace``, a failed batch
reports written / not-written / conflict lists without claiming a rollback,
and re-running against the current differences converges on the remainder.
This tool is an explicit engineering command: nothing here runs implicitly
while a forecast executes.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath


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

PLAN_SCHEMA = "rf-install-plan/1"
RESULT_SCHEMA = "rf-install-result/1"

_STATUS_ORDER = {"completed": 0, "partial": 1, "failed": 2}


class ScopeError(ValueError):
    """A requested ``--file`` scope entry is not an installable relative path."""


class _SourceChangedError(Exception):
    """The bytes read from the canonical source changed during this operation."""


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


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_or_none(path: Path) -> str | None:
    """SHA-256 of ``path`` when it is a readable regular file, else ``None``.

    ``None`` means "there is no regular file here".  An existing file that
    cannot be read raises, so a target whose bytes cannot be verified is never
    mistaken for an empty one and never silently overwritten.
    """
    if path.is_file():
        return _sha(path)
    return None


def _within(base: str, candidate: str) -> bool:
    base_folded = os.path.normcase(base)
    candidate_folded = os.path.normcase(candidate)
    return candidate_folded == base_folded or candidate_folded.startswith(
        base_folded + os.sep
    )


def _target_file(target: Path, relative: str) -> Path:
    """Locate ``relative`` under ``target``, rejecting an escaping link.

    A symlink or Windows reparse point on any component that leaves the
    installation target is a bad input, not a permission problem, so it is
    rejected while the whole scope is still being validated — before any
    destination is written.
    """
    base = os.path.realpath(target)
    current = target
    for part in PurePosixPath(relative).parts:
        current = current / part
        if not _within(base, os.path.realpath(current)):
            raise ScopeError(
                f"--file escapes the installation target through a link: {relative}"
            )
    return target / relative


def resolve_file_scope(canonical: Path, requested: list[str]) -> list[str]:
    """Validate, deduplicate and sort a requested ``--file`` scope.

    Every entry must be a repository-relative path that belongs to
    ``installable_files(canonical)``.  Absolute paths, ``..``, directory names
    and anything outside the closure are rejected here, so a bad scope never
    reaches a destination.
    """
    closure = {
        path.relative_to(canonical).as_posix() for path in installable_files(canonical)
    }
    chosen: set[str] = set()
    for raw in requested:
        text = str(raw).strip()
        if not text:
            raise ScopeError("--file requires a non-empty relative path")
        text = text.replace("\\", "/")
        while text.startswith("./"):
            text = text[2:]
        if text.startswith("/") or (len(text) > 1 and text[1] == ":"):
            raise ScopeError(
                f"--file must be a relative path inside the skill package: {raw}"
            )
        parts = [part for part in text.split("/") if part not in ("", ".")]
        if any(part == ".." for part in parts):
            raise ScopeError(f"--file must not contain '..': {raw}")
        relative = "/".join(parts)
        if not relative:
            raise ScopeError(f"--file must name a file: {raw}")
        source = canonical / relative
        if source.is_dir():
            raise ScopeError(f"--file names a directory: {relative}")
        if relative not in closure:
            raise ScopeError(
                f"--file is outside the installable runtime closure: {relative}"
            )
        chosen.add(relative)
    if not chosen:
        raise ScopeError("--file requires at least one path")
    return sorted(chosen)


def _scope_paths(canonical: Path, selected: list[str] | None) -> list[str]:
    if selected is not None:
        return list(selected)
    return [
        path.relative_to(canonical).as_posix() for path in installable_files(canonical)
    ]


def plan_target(
    canonical: Path, destination: Path, selected: list[str] | None = None
) -> dict:
    """Read-only per-destination plan.  Creates nothing, writes nothing.

    For every selected relative path the entry records ``operation`` (one of
    ``new`` / ``replace`` / ``unchanged``), ``before_sha256`` (``None`` when
    there is no readable installed file), ``source_sha256`` and ``size``, plus
    the target's ``selected_drift`` and ``unselected_drift`` counts.
    """
    destination = Path(destination)
    target = destination / SKILL_NAME
    scope = _scope_paths(canonical, selected)
    installed = target.is_dir()
    entries: list[dict] = []
    selected_drift = 0
    for relative in scope:
        source_bytes = (canonical / relative).read_bytes()
        source_sha = hashlib.sha256(source_bytes).hexdigest()
        if installed:
            path = _target_file(target, relative)
            exists = path.exists()
            before = _sha_or_none(path)
        else:
            exists = False
            before = None
        if before is None:
            operation = "new" if not exists else "replace"
        elif before == source_sha:
            operation = "unchanged"
        else:
            operation = "replace"
        if operation != "unchanged":
            selected_drift += 1
        entries.append(
            {
                "path": relative,
                "operation": operation,
                "before_sha256": before,
                "source_sha256": source_sha,
                "size": len(source_bytes),
            }
        )
    drift = set(installation_diff(canonical, destination))
    return {
        "destination": str(destination),
        "target": str(target),
        "installed": installed,
        "selected_drift": selected_drift,
        "unselected_drift": len(drift - set(scope)),
        "files": entries,
    }


def build_plan(
    canonical: Path, selected: list[str] | None, targets: list[dict]
) -> dict:
    """Assemble the ``rf-install-plan/1`` document for one invocation."""
    return {
        "schema": PLAN_SCHEMA,
        "canonical": str(canonical),
        "selected": _scope_paths(canonical, selected),
        "targets": list(targets),
    }


def _stage_and_replace(
    source: Path, staged: Path, final: Path, expected_sha: str
) -> None:
    """Stage ``source`` and swap it in with one atomic ``os.replace``.

    The staged bytes are hashed before they are published, so a source that
    changed while it was being copied surfaces as an explicit conflict instead
    of silently landing.  Only this file's own stage entry and its
    ``.{pid}.syncing`` sibling are touched; nothing globs the destination.
    """
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, staged)
    if _sha(staged) != expected_sha:
        raise _SourceChangedError("canonical source changed during this operation")
    final.parent.mkdir(parents=True, exist_ok=True)
    temporary = final.with_name(final.name + f".{os.getpid()}.syncing")
    try:
        shutil.copy2(staged, temporary)
        if _sha(temporary) != expected_sha:
            raise _SourceChangedError("canonical source changed during this operation")
        os.replace(temporary, final)
    finally:
        temporary.unlink(missing_ok=True)


def apply_target(canonical: Path, destination: Path, target_plan: dict) -> dict:
    """Execute one planned target, re-verifying bytes immediately before each swap.

    Nothing is written from a stale plan: the canonical source and the
    installed target are re-hashed right before the replacement, and a
    difference on either side is reported as a conflict rather than
    overwritten.  Files whose bytes already match are left completely alone —
    no staging copy, no ``os.replace``, mtime and size untouched.
    """
    destination = Path(destination)
    target = Path(target_plan["target"])
    planned = {entry["path"]: entry for entry in target_plan["files"]}
    scope = [entry["path"] for entry in target_plan["files"]]

    written: list[str] = []
    unchanged: list[str] = []
    failed: list[dict] = []
    conflicts: list[str] = []

    to_write = [
        relative for relative in scope if planned[relative]["operation"] != "unchanged"
    ]
    # ExitStack owns exactly this invocation's stage directory, so only that
    # directory is cleaned — never another process's ``.syncing`` siblings.
    with contextlib.ExitStack() as stack:
        stage: Path | None = None
        if to_write:
            destination.mkdir(parents=True, exist_ok=True)
            target.mkdir(parents=True, exist_ok=True)
            stage = (
                Path(
                    stack.enter_context(
                        tempfile.TemporaryDirectory(
                            prefix=f".{SKILL_NAME}-stage-", dir=destination
                        )
                    )
                )
                / SKILL_NAME
            )
            stage.mkdir()
        for relative in scope:
            entry = planned[relative]
            source = canonical / relative
            final = target / relative
            try:
                source_sha = _sha(source)
            except OSError as exc:
                failed.append(
                    {
                        "path": relative,
                        "reason": "read_error",
                        "detail": f"{type(exc).__name__}: {exc}",
                    }
                )
                continue
            if source_sha != entry["source_sha256"]:
                failed.append(
                    {
                        "path": relative,
                        "reason": "conflict",
                        "detail": "canonical source changed during this operation",
                    }
                )
                conflicts.append(relative)
                continue
            try:
                current_sha = _sha_or_none(final)
            except OSError as exc:
                failed.append(
                    {
                        "path": relative,
                        "reason": "conflict",
                        "detail": f"installation target unreadable: {type(exc).__name__}: {exc}",
                    }
                )
                conflicts.append(relative)
                continue
            if current_sha != entry["before_sha256"]:
                failed.append(
                    {
                        "path": relative,
                        "reason": "conflict",
                        "detail": "installation target changed during this operation",
                    }
                )
                conflicts.append(relative)
                continue
            if entry["operation"] == "unchanged":
                unchanged.append(relative)
                continue
            if stage is None:
                # unreachable: the stage is prepared exactly when a file differs
                failed.append(
                    {
                        "path": relative,
                        "reason": "write_error",
                        "detail": "staging directory unavailable for a pending write",
                    }
                )
                continue
            try:
                _stage_and_replace(
                    source, stage / relative, final, entry["source_sha256"]
                )
            except _SourceChangedError as exc:
                failed.append(
                    {"path": relative, "reason": "conflict", "detail": str(exc)}
                )
                conflicts.append(relative)
            except OSError as exc:
                failed.append(
                    {
                        "path": relative,
                        "reason": "write_error",
                        "detail": f"{type(exc).__name__}: {exc}",
                    }
                )
            else:
                written.append(relative)

    return _finish_target(
        canonical, destination, target, scope, written, unchanged, failed, conflicts
    )


def check_target(
    canonical: Path, destination: Path, selected: list[str] | None = None
) -> dict:
    """Read-only selected-scope check.

    A missing installation keeps the historical "not drifted" semantics, so a
    check never reports a target that does not exist as a failure.  An explicit
    ``--plan`` is the path that may report ``new`` there instead.
    """
    destination = Path(destination)
    target = destination / SKILL_NAME
    scope = _scope_paths(canonical, selected)
    drift = set(installation_diff(canonical, destination))
    selected_set = set(scope)
    drifted = sorted(drift & selected_set)
    drifted_set = set(drifted)
    return _finish_target(
        canonical,
        destination,
        target,
        scope,
        [],
        [relative for relative in scope if relative not in drifted_set],
        [],
        [],
        drifted=drifted,
        unselected=sorted(drift - selected_set),
    )


def _finish_target(
    canonical: Path,
    destination: Path,
    target: Path,
    scope: list[str],
    written: list[str],
    unchanged: list[str],
    failed: list[dict],
    conflicts: list[str],
    drifted: list[str] | None = None,
    unselected: list[str] | None = None,
) -> dict:
    """Recompute the real post-operation byte state and package the result."""
    if drifted is None or unselected is None:
        drift = set(installation_diff(canonical, destination))
        selected_set = set(scope)
        drifted = sorted(drift & selected_set)
        unselected = sorted(drift - selected_set)
    if not failed:
        status = "completed"
    elif written or unchanged:
        status = "partial"
    else:
        status = "failed"
    return {
        "destination": str(destination),
        "target": str(target),
        "selected": list(scope),
        "written": written,
        "unchanged": unchanged,
        "failed": failed,
        "conflicts": conflicts,
        "drifted": list(drifted),
        "remaining_selected_drift": len(drifted),
        "remaining_unselected_drift": len(unselected),
        "status": status,
    }


def build_result(mode: str, selected: list[str] | None, targets: list[dict]) -> dict:
    """Assemble the ``rf-install-result/1`` document for one invocation."""
    status = "completed"
    for entry in targets:
        if _STATUS_ORDER[entry["status"]] > _STATUS_ORDER[status]:
            status = entry["status"]
    return {
        "schema": RESULT_SCHEMA,
        "mode": mode,
        "selected": _scope_paths_from_targets(selected, targets),
        "status": status,
        "targets": list(targets),
    }


def _scope_paths_from_targets(
    selected: list[str] | None, targets: list[dict]
) -> list[str]:
    if selected is not None:
        return list(selected)
    if targets:
        return list(targets[0]["selected"])
    return []


def sync_installation(canonical: Path, destination: Path) -> dict:
    """Update the files this package owns, in place, through a tmp stage.

    Every owned file whose bytes differ is copied into a staging directory
    under ``destination`` first and then swapped in one atomic ``os.replace``.
    Owned files whose bytes already match are not touched at all.  Nothing else
    in the installation is written or removed: unknown files, user
    configuration, ``output`` and any repository-only residue left by an older
    installation all survive, and there is no whole-directory replacement.

    The per-target result is returned; if any selected file could not be
    written the incomplete state is reported by raising ``OSError``, so a
    library caller still fails loudly instead of reading a silent partial.
    """
    destination = Path(destination)
    result = apply_target(canonical, destination, plan_target(canonical, destination))
    if result["failed"]:
        detail = "; ".join(
            f"{item['path']}: {item['detail']}" for item in result["failed"]
        )
        raise OSError(
            f"incomplete installation sync at {result['target']} "
            f"({len(result['written'])} written, {len(result['failed'])} failed): {detail}"
        )
    return result


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


def _legacy_report(canonical: Path, destinations: list[Path]) -> bool:
    """The original human-readable whole-runtime report.  Returns True on drift."""
    failed = False
    expected_count = len(manifest(canonical))
    for destination in destinations:
        differences = installation_diff(canonical, destination)
        if differences:
            failed = True
            print(f"DIFF {destination}: {len(differences)} files")
            for path in differences[:50]:
                print(f"  {path}")
        else:
            print(f"MATCH {destination}: {expected_count} files")
    return failed


def _report_selected_check(targets: list[dict]) -> None:
    for entry in targets:
        if entry["remaining_selected_drift"]:
            print(
                f"DIFF {entry['destination']}: {entry['remaining_selected_drift']} of "
                f"{len(entry['selected'])} selected files"
            )
            for path in entry["drifted"][:50]:
                print(f"  {path}")
        else:
            print(
                f"MATCH {entry['destination']}: {len(entry['selected'])} selected files"
            )
        if entry["remaining_unselected_drift"]:
            print(
                f"NOTE {entry['destination']}: {entry['remaining_unselected_drift']} "
                "unselected files differ (outside --file scope)"
            )


def _report_selected_apply(targets: list[dict]) -> None:
    for entry in targets:
        print(
            f"APPLIED {entry['destination']}: {len(entry['written'])} written, "
            f"{len(entry['unchanged'])} unchanged, {len(entry['failed'])} failed "
            f"(of {len(entry['selected'])} selected)"
        )
        for item in entry["failed"]:
            print(f"  FAILED {item['path']}: {item['reason']}: {item['detail']}")
        if entry["remaining_unselected_drift"]:
            print(
                f"NOTE {entry['destination']}: {entry['remaining_unselected_drift']} "
                "unselected files differ (outside --file scope)"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check or synchronize installed revenue-forecast skills"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--apply",
        action="store_true",
        help="apply a per-file atomic sync (whole runtime unless --file selects a subset)",
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
    mode.add_argument(
        "--plan",
        action="store_true",
        help="print one zero-write rf-install-plan/1 JSON value and exit 0",
    )
    parser.add_argument(
        "--canonical", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--destination", type=Path, action="append")
    parser.add_argument(
        "--file",
        action="append",
        metavar="RELATIVE",
        help="restrict check/plan/apply to this installable relative path (repeatable)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print exactly one rf-install-result/1 JSON value on stdout",
    )
    args = parser.parse_args()

    if (args.file or args.json) and (
        args.import_from is not None or args.print_manifest
    ):
        parser.error(
            "--file/--json cannot be combined with --import-from/--print-manifest"
        )

    canonical = args.canonical.resolve()
    if args.print_manifest:
        print(json.dumps(manifest(canonical), indent=2, sort_keys=True))
        return 0

    selected: list[str] | None = None
    if args.file:
        try:
            selected = resolve_file_scope(canonical, args.file)
        except ScopeError as exc:
            parser.error(str(exc))

    if args.import_from is not None:
        import_installation(args.import_from, canonical)

    destinations = [
        Path(destination).resolve()
        for destination in unique_destinations(
            args.destination or list(DEFAULT_DESTINATIONS)
        )
    ]

    if args.plan:
        try:
            plans = [plan_target(canonical, item, selected) for item in destinations]
        except ScopeError as exc:
            parser.error(str(exc))
        print(
            json.dumps(build_plan(canonical, selected, plans), indent=2, sort_keys=True)
        )
        return 0

    if args.apply:
        try:
            # every destination is planned read-only first, so a bad scope is
            # rejected before any installation is touched
            plans = [plan_target(canonical, item, selected) for item in destinations]
        except ScopeError as exc:
            parser.error(str(exc))
        results = [
            apply_target(canonical, item, plan)
            for item, plan in zip(destinations, plans)
        ]
        if args.json:
            print(
                json.dumps(
                    build_result("apply", selected, results), indent=2, sort_keys=True
                )
            )
        elif selected is None:
            return 1 if _legacy_report(canonical, destinations) else 0
        else:
            _report_selected_apply(results)
        return 1 if any(item["remaining_selected_drift"] for item in results) else 0

    if args.json or selected is not None:
        results = [check_target(canonical, item, selected) for item in destinations]
        if args.json:
            print(
                json.dumps(
                    build_result("check", selected, results), indent=2, sort_keys=True
                )
            )
        else:
            _report_selected_check(results)
        return 1 if any(item["remaining_selected_drift"] for item in results) else 0

    return 1 if _legacy_report(canonical, destinations) else 0


if __name__ == "__main__":
    raise SystemExit(main())
