"""G3-RF-ASSURANCE quality report: failures versus diagnostics.

The historical ZR-104 layer compared five frozen dimensions against the
recomputed state and turned *any* difference into a non-zero exit.  That
made retired engineering thresholds (G2 lowered the coverage gate from
``fail_under=84`` + eight per-module floors to ``0`` + ``{}``) block a layer
that outlived them, and it made an un-checkout-out sibling repository or an
old workflow text a qualification failure.

This module turns the same computation into a REPORT with two closed sets:

``failures``
    Real problems only: a baseline payload that is not a valid ZR-104
    document (invalid configuration), a repository that IS in scope but
    cannot be read (real input corruption), an explicitly supplied input
    that is missing/unreadable, and a real process that exits non-zero.
    Non-empty means exit code 1.

``diagnostics``
    Everything the old ratchet compared numerically — coverage floors,
    complexity maxima, frozen allowlists, dead-caller counts, product-subtree
    drift, sibling-HEAD scope, old workflow text — plus every
    ``not_available`` scope.  Visible, historical, never a gate.

Nothing here writes a file.  The report never re-freezes the baseline and
never repairs a damaged one.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from uc.quality import (
    DEFAULT_REPOS,
    REPO_ORDER,
    REVENUE,
    SCHEMA_VERSION,
    UNIT,
    compute_baseline,
    strict_targets,
)

REPORT_SCHEMA = "g3-quality-report/1"
_DIMENSIONS = ("types", "coverage", "complexity", "hardcoding")

_CONFIG_KEYS = ("product_trees", "repos", "dead_callers")


# ---------------------------------------------------------------------------
# Real process probe — judged by exit code, never by text
# ---------------------------------------------------------------------------


def run_probe(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 600,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run one real process and judge it ONLY by its return code.

    A tool that exits non-zero failed, whether or not its output happens to
    contain a ``FAILED`` marker; a tool that exits zero succeeded.  Output
    text is carried along for the report but never decides the verdict.
    """
    environment = os.environ.copy()
    environment.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    environment.setdefault("PYTHONUTF8", "1")
    if env:
        environment.update(env)
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=environment,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return {
        "command": list(cmd),
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "output": output,
    }


def type_check_command(repo_name: str, root: Path) -> list[str]:
    """The repo's actual type-check command (``python -m mypy <targets>``)."""
    return [sys.executable, "-m", "mypy", *strict_targets(repo_name, root)]


# ---------------------------------------------------------------------------
# Dimension comparisons — every one of them a diagnostic
# ---------------------------------------------------------------------------


def _floor_diagnostics(
    repo_name: str,
    dimension: str,
    frozen_map: dict[str, Any],
    current_map: dict[str, Any],
    out: list[str],
) -> None:
    for key, floor in sorted(frozen_map.items()):
        if key not in current_map:
            out.append(
                f"{repo_name}/{dimension}: frozen floor for {key} lost "
                "(constraint removed from the ratchet — retired engineering "
                "threshold, diagnostic only)"
            )
        elif floor < current_map[key]:
            out.append(
                f"{repo_name}/{dimension}: frozen floor {floor} for {key} is "
                f"below the recomputed {current_map[key]} (threshold may "
                "only stay-or-rise)"
            )


def _types_diagnostics(
    repo_name: str, frozen: dict[str, Any], current: dict[str, Any], out: list[str]
) -> None:
    frozen_set = set(frozen.get("types", {}).get("strict_mypy_targets", []))
    current_set = set(current.get("types", {}).get("strict_mypy_targets", []))
    dropped = sorted(frozen_set - current_set)
    if dropped:
        out.append(
            f"{repo_name}/types: strict-mypy target set shrank — files no "
            f"longer strict-checked: {dropped} (target set may only grow)"
        )


def _coverage_diagnostics(
    repo_name: str, frozen: dict[str, Any], current: dict[str, Any], out: list[str]
) -> None:
    frozen_map: dict[str, Any] = {}
    current_map: dict[str, Any] = {}
    frozen_section = frozen.get("coverage", {})
    current_section = current.get("coverage", {})
    if "total_floor" in frozen_section and "total_floor" in current_section:
        frozen_map["total_floor"] = frozen_section["total_floor"]
        current_map["total_floor"] = current_section["total_floor"]
    frozen_map.update(frozen_section.get("per_module_floors", {}))
    current_map.update(current_section.get("per_module_floors", {}))
    frozen_map.update(frozen_section.get("floors", {}))
    current_map.update(current_section.get("floors", {}))
    _floor_diagnostics(repo_name, "coverage", frozen_map, current_map, out)


def _complexity_diagnostics(
    repo_name: str, frozen: dict[str, Any], current: dict[str, Any], out: list[str]
) -> None:
    frozen_max = frozen.get("complexity", {}).get("frozen_max", {})
    current_max = current.get("complexity", {}).get("frozen_max", {})
    for file_rel, value in sorted(frozen_max.items()):
        if file_rel not in current_max:
            out.append(
                f"{repo_name}/complexity: frozen max for {file_rel} lost "
                "(constraint removed from the ratchet)"
            )
        elif value > current_max[file_rel]:
            out.append(
                f"{repo_name}/complexity: frozen max {value} for {file_rel} "
                f"exceeds the recomputed {current_max[file_rel]} (complexity "
                "may only stay-or-fall)"
            )
    frozen_new = frozen.get("complexity", {}).get("new_file_max")
    current_new = current.get("complexity", {}).get("new_file_max")
    if (
        isinstance(frozen_new, int)
        and isinstance(current_new, int)
        and frozen_new > current_new
    ):
        out.append(
            f"{repo_name}/complexity: frozen new-file max {frozen_new} "
            f"exceeds the recomputed {current_new}"
        )


def _hardcoding_diagnostics(
    repo_name: str, frozen: dict[str, Any], current: dict[str, Any], out: list[str]
) -> None:
    frozen_section = frozen.get("hardcoding", {})
    current_section = current.get("hardcoding", {})
    removed = sorted(
        set(frozen_section.get("frozen_tokens", []))
        - set(current_section.get("frozen_tokens", []))
    )
    if removed:
        out.append(
            f"{repo_name}/hardcoding: frozen root tokens removed: {removed} "
            "(token set may only grow)"
        )
    grown = sorted(
        set(frozen_section.get("allowlist", []))
        - set(current_section.get("allowlist", []))
    )
    if grown:
        out.append(
            f"{repo_name}/hardcoding: frozen allowlist grew beyond the "
            f"recomputed set: {grown} (allowlist may only shrink)"
        )
    frozen_scan = frozen_section.get("scan")
    if frozen_scan is None:
        return
    current_scan = current_section.get("scan")
    if current_scan is None:
        out.append(
            f"{repo_name}/hardcoding: frozen scan "
            f"{frozen_scan.get('name')} is no longer computed"
        )
        return
    if frozen_scan.get("pattern") != current_scan.get("pattern") or frozen_scan.get(
        "targets"
    ) != current_scan.get("targets"):
        out.append(
            f"{repo_name}/hardcoding: frozen scan definition changed (pattern/targets)"
        )
    new_hits = [
        hit
        for hit in current_scan.get("hits", [])
        if hit not in frozen_scan.get("hits", [])
    ]
    if new_hits:
        out.append(
            f"{repo_name}/hardcoding: new hardcoded values detected by "
            f"the frozen scan: {new_hits}"
        )


def _dead_caller_diagnostics(
    frozen: dict[str, Any], current: dict[str, Any], out: list[str]
) -> None:
    if frozen.get("input_hash") and frozen.get("input_hash") != current.get(
        "input_hash"
    ):
        out.append(
            "dead_callers: CodeGraph caller-report input changed (artifact "
            "re-frozen); recorded as a historical comparison, not a gate"
        )
    frozen_repos = frozen.get("repos", {})
    current_repos = current.get("repos", {})
    for repo_name in REPO_ORDER:
        frozen_count = len(frozen_repos.get(repo_name, {}).get("targets", []))
        current_count = len(current_repos.get(repo_name, {}).get("targets", []))
        if current_count > frozen_count:
            out.append(
                f"dead_callers/{repo_name}: dead-production-caller count rose "
                f"{frozen_count} -> {current_count}: "
                f"{current_repos.get(repo_name, {}).get('targets', [])} "
                "(count may only stay-or-fall)"
            )


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def _invalid_configuration(frozen: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(frozen, dict):
        return [
            f"config: baseline payload is not a JSON object ({type(frozen).__name__})"
        ]
    if frozen.get("schema_version") != SCHEMA_VERSION:
        failures.append(
            f"config: schema_version {frozen.get('schema_version')!r} != "
            f"{SCHEMA_VERSION}"
        )
    if frozen.get("unit") != UNIT:
        failures.append(f"config: unit {frozen.get('unit')!r} != {UNIT!r}")
    for key in _CONFIG_KEYS:
        if key in frozen and not isinstance(frozen[key], dict):
            failures.append(f"config: {key} must be a JSON object")
    return failures


def _scope(root: Path, baseline: dict[str, Any]) -> dict[str, Any]:
    scope: dict[str, Any] = {}
    for repo_name in REPO_ORDER:
        repo = DEFAULT_REPOS[repo_name](root)
        if not repo.is_dir():
            scope[repo_name] = {
                "status": "not_available",
                "scope": f"repository not present: {repo}",
            }
            continue
        sections = baseline.get("repos", {}).get(repo_name, {})
        statuses = [
            sections.get(dimension, {}).get("status") for dimension in _DIMENSIONS
        ]
        if any(status == "error" for status in statuses):
            status = "error"
        elif all(status == "ok" for status in statuses):
            status = "computed"
        else:
            status = "not_available"
        scope[repo_name] = {"status": status, "scope": str(repo)}
    return scope


def _dimension_outcomes(
    repo_name: str,
    frozen_repo: dict[str, Any],
    current_repo: dict[str, Any],
    failures: list[str],
    diagnostics: list[str],
) -> None:
    for dimension in _DIMENSIONS:
        current = current_repo.get(dimension, {})
        status = current.get("status")
        if status == "error":
            failures.append(
                f"input: {repo_name}/{dimension} unreadable: {current.get('scope')}"
            )
            continue
        if status == "not_available":
            diagnostics.append(
                f"{repo_name}/{dimension}: not_available ({current.get('scope')})"
            )
            continue
        if dimension == "types":
            _types_diagnostics(repo_name, frozen_repo, current_repo, diagnostics)
        elif dimension == "coverage":
            _coverage_diagnostics(repo_name, frozen_repo, current_repo, diagnostics)
        elif dimension == "complexity":
            _complexity_diagnostics(repo_name, frozen_repo, current_repo, diagnostics)
        else:
            _hardcoding_diagnostics(repo_name, frozen_repo, current_repo, diagnostics)


def _product_tree_diagnostics(
    frozen: dict[str, Any],
    baseline: dict[str, Any],
    diagnostics: list[str],
) -> None:
    frozen_trees = frozen.get("product_trees", {})
    current_trees = baseline.get("product_trees", {})
    scopes = baseline.get("product_tree_scopes", {})
    for repo_name in REPO_ORDER:
        frozen_sha = frozen_trees.get(repo_name)
        current_sha = current_trees.get(repo_name)
        if current_sha is None:
            diagnostics.append(
                f"product_trees/{repo_name}: not_available "
                f"({scopes.get(repo_name)}); frozen value retained as a "
                f"historical comparison: {frozen_sha}"
            )
        elif frozen_sha != current_sha:
            diagnostics.append(
                f"product_trees/{repo_name}: historical comparison — frozen "
                f"{frozen_sha} != current {current_sha}"
            )


def _run_type_probe(root: Path, failures: list[str], diagnostics: list[str]) -> None:
    try:
        command = type_check_command(REVENUE, root)
    except (ValueError, OSError) as exc:
        failures.append(f"type-check: cannot resolve the type entry: {exc}")
        return
    with tempfile.TemporaryDirectory(prefix="rf-quality-types-") as cache:
        result = run_probe(
            [*command, "--cache-dir", cache],
            cwd=root,
            env={"PYTHONDONTWRITEBYTECODE": "1"},
        )
    if result["ok"]:
        diagnostics.append(f"type-check: {REVENUE} strict targets passed mypy (exit 0)")
    else:
        failures.append(
            f"type-check: process exited {result['returncode']} for "
            f"{REVENUE} strict targets"
        )


def build_report(
    root: Path,
    frozen: Any,
    *,
    run_types: bool = False,
) -> dict[str, Any]:
    """Build the quality report for ``root`` against the frozen baseline.

    Read-only: the baseline is never repaired, re-frozen or rewritten, and
    no file is produced.  ``run_types`` additionally runs the repository's
    real type command as a probe — a non-zero exit becomes a failure.
    """
    failures = _invalid_configuration(frozen)
    diagnostics: list[str] = []
    baseline: dict[str, Any] | None = None
    scope: dict[str, Any] = {}

    if not failures:
        try:
            baseline = compute_baseline(root)
        except Exception as exc:  # noqa: BLE001 - report, never crash the CLI
            failures.append(f"input: baseline recomputation failed: {exc}")

    if baseline is not None:
        scope = _scope(root, baseline)
        for repo_name in REPO_ORDER:
            frozen_repo = frozen.get("repos", {}).get(repo_name, {})
            if not isinstance(frozen_repo, dict):
                failures.append(f"config: repos/{repo_name} must be a JSON object")
                continue
            _dimension_outcomes(
                repo_name,
                frozen_repo,
                baseline["repos"][repo_name],
                failures,
                diagnostics,
            )
        _product_tree_diagnostics(frozen, baseline, diagnostics)
        dead_frozen = frozen.get("dead_callers", {})
        if isinstance(dead_frozen, dict):
            _dead_caller_diagnostics(dead_frozen, baseline["dead_callers"], diagnostics)
        current_dead = baseline["dead_callers"]
        if current_dead.get("status") == "error":
            failures.append(
                f"input: dead_callers artifact unreadable: {current_dead.get('scope')}"
            )
        if run_types:
            _run_type_probe(root, failures, diagnostics)

    return {
        "schema_version": REPORT_SCHEMA,
        "unit": UNIT,
        "root": str(root),
        "failures": failures,
        "diagnostics": diagnostics,
        "scope": scope,
        "baseline": baseline,
    }
