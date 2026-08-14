"""ZR-104 quality baseline: freeze and verify a three-repo quality ratchet.

Freezes, per repo (revenue / filing / wiki), the five quality dimensions
that already exist as separate machine assets — the strict-mypy target set
(CI workflow commands), coverage floors (existing ratchet configs/tests),
complexity (wiki FC-1204 per-file frozen max; revenue/filing enforced on
new/changed critical functions only), root hardcoding (wiki FC-1201 frozen
allowlist; revenue FC-1101 workflow-pin scan), and dead production callers
(CA-003 CodeGraph caller report) — into one machine-verifiable baseline
bound to the current triplet.

Design rules (ZR-104, phase C):

- Every value is machine-computed by :func:`compute_baseline` from the
  repos and the toolchain at freeze time AND at verify time.  No value in
  the baseline is hand-written except structural metadata (schema, unit,
  the fixed frozen-at constant, file paths, the max-complexity constant).
- The baseline is bound to an exact triplet (git HEADs); verify requires
  exact equality (re-freeze after deliberate review when the triplet moves).
- Ratchet semantics: the frozen baseline must *match-or-improve* the
  recomputed state — the frozen value must be at least as strict as the
  value recomputed today.  A baseline that was weakened (coverage floor
  lowered, allowlist grown, complexity max raised, strict target dropped,
  dead caller hidden) is rejected with named violations; a baseline that
  was strengthened verifies green.
- :func:`freeze` writes the baseline once and refuses to overwrite without
  ``force`` (CAS replace); :func:`check_critical_complexity` is the AST
  McCabe gate for new/changed critical functions (no third-party deps).
"""

from __future__ import annotations

import ast
import configparser
import hashlib
import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any, Callable

from uc.casfile import cas_update, exclusive_publish, sha256_bytes, sha256_file

SCHEMA_VERSION = 1
UNIT = "ZR-104"
# Fixed constant (deterministic freezes): the baseline never carries a
# wall-clock timestamp, so two freezes of the same state are byte-identical.
FROZEN_AT_UTC = "2026-08-14T00:00:00+00:00"

# New/changed critical functions must stay at or below this complexity
# (wiki FC-1204 NEW_FILE_MAX == 10; revenue/filing enforce on new/changed
# critical functions only — no whole-repo number is invented here).
NEW_FILE_MAX = 10
MAX_CRITICAL_COMPLEXITY = 10

REPO_ORDER = ("revenue", "filing", "wiki")

DEFAULT_REPOS: dict[str, Callable[[Path], Path]] = {
    "revenue": lambda root: root,
    "filing": lambda root: root.parent / "filing-fetch",
    "wiki": lambda root: root.parent / "company-wiki",
}

# Per-repo CI workflow that carries the strict-mypy command — the machine
# source of the frozen strict target set.
WORKFLOW_RELPATHS = {
    "revenue": ".github/workflows/quality.yml",
    "filing": ".github/workflows/quality.yml",
    "wiki": ".github/workflows/ci.yml",
}

CODEGRAPH_ARTIFACT_REL = Path("codegraph") / "codegraph_freeze.json"

_MYPY_LINE = re.compile(r"python\s+-m\s+mypy\s+(.+?)\s*$")

_DECISION_NODES = (
    ast.If,
    ast.For,
    ast.While,
    ast.And,
    ast.Or,
    ast.ExceptHandler,
    ast.comprehension,
    ast.Assert,
    ast.With,
)


# ---------------------------------------------------------------------------
# Small source-reading helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path, description: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"{description} missing: {path}") from exc


def git_head(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if proc.returncode != 0:
        raise ValueError(
            f"git rev-parse HEAD failed on {repo}: {proc.stderr.strip()[-200:]}"
        )
    return proc.stdout.strip()


def _top_level_assignments(source: str) -> dict[str, ast.AST]:
    tree = ast.parse(source)
    out: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out[target.id] = node.value
    return out


def _literal_dict(node: ast.AST) -> dict[str, Any]:
    value = ast.literal_eval(node)
    if not isinstance(value, dict):
        raise ValueError(f"expected dict literal, got {type(value).__name__}")
    return {str(key): item for key, item in value.items()}


def _string_collection(node: ast.AST) -> list[str]:
    """String literals from a tuple/set/list or ``frozenset({...})`` literal."""
    if isinstance(node, (ast.Tuple, ast.Set, ast.List)):
        return [
            elt.value
            for elt in node.elts
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        ]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "frozenset"
        and node.args
    ):
        return _string_collection(node.args[0])
    return []


def _canonical_hash(*parts: Any) -> str:
    payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, default=list)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Dimension computation (one shared source for freeze AND verify)
# ---------------------------------------------------------------------------


def _mypy_target_tokens(workflow_text: str) -> list[str]:
    tokens: list[str] = []
    for line in workflow_text.splitlines():
        match = _MYPY_LINE.search(line)
        if match:
            tokens.extend(match.group(1).split())
    return tokens


def strict_targets(repo_name: str, root: Path) -> list[str]:
    """Resolve the repo's CI strict-mypy command to a sorted file set
    (relative paths).  Directories are expanded to their ``*.py`` files."""
    repo = DEFAULT_REPOS[repo_name](root)
    workflow = repo / WORKFLOW_RELPATHS[repo_name]
    tokens = _mypy_target_tokens(_read_text(workflow, f"{repo_name} CI workflow"))
    if not tokens:
        raise ValueError(f"no `python -m mypy` command found in {workflow}")
    resolved: list[str] = []
    for token in tokens:
        candidate = repo / token
        if candidate.is_dir():
            resolved.extend(
                path.relative_to(repo).as_posix()
                for path in sorted(candidate.rglob("*.py"))
            )
        elif candidate.is_file():
            resolved.append(candidate.relative_to(repo).as_posix())
        else:
            raise ValueError(f"strict-mypy target does not exist: {candidate}")
    return sorted(set(resolved))


def _revenue_coverage(root: Path) -> dict[str, Any]:
    rc = root / ".coveragerc"
    parser = configparser.ConfigParser()
    parser.read(rc, encoding="utf-8")
    try:
        total = float(parser.get("report", "fail_under"))
    except (configparser.Error, ValueError) as exc:
        raise ValueError(f".coveragerc fail_under unreadable: {exc}") from exc
    gates = root / "tools" / "run_coverage_gates.py"
    assigns = _top_level_assignments(_read_text(gates, "revenue coverage gates"))
    if "PER_MODULE_MINIMUM" not in assigns:
        raise ValueError("PER_MODULE_MINIMUM missing from tools/run_coverage_gates.py")
    return {
        "kind": "config-frozen-floor",
        "total_floor": total,
        "per_module_floors": dict(
            sorted(_literal_dict(assigns["PER_MODULE_MINIMUM"]).items())
        ),
        "sources": {
            ".coveragerc": "[report] fail_under",
            "tools/run_coverage_gates.py": "PER_MODULE_MINIMUM",
        },
    }


def _filing_coverage(root: Path) -> dict[str, Any]:
    pyproject = DEFAULT_REPOS["filing"](root) / "pyproject.toml"
    try:
        with open(pyproject, "rb") as fh:
            data = tomllib.load(fh)
        total = float(data["tool"]["coverage"]["report"]["fail_under"])
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"filing pyproject fail_under unreadable: {exc}") from exc
    return {
        "kind": "config-frozen-floor",
        "total_floor": total,
        "per_module_floors": {},
        "sources": {"pyproject.toml": "[tool.coverage.report] fail_under"},
    }


def _wiki_coverage(root: Path) -> dict[str, Any]:
    test = (
        DEFAULT_REPOS["wiki"](root)
        / "tests"
        / "contract"
        / "test_fc1204_coverage_ratchet.py"
    )
    assigns = _top_level_assignments(_read_text(test, "wiki FC-1204 coverage ratchet"))
    floors: dict[str, Any] = {}
    for name in ("TIER1", "TIER2", "FROZEN"):
        if name not in assigns:
            raise ValueError(f"{name} missing from {test}")
        floors.update(_literal_dict(assigns[name]))
    return {
        "kind": "per-module-branch-ratchet",
        "floors": dict(sorted(floors.items())),
        "source": "tests/contract/test_fc1204_coverage_ratchet.py",
    }


def _wiki_complexity(root: Path) -> dict[str, Any]:
    test = (
        DEFAULT_REPOS["wiki"](root)
        / "tests"
        / "contract"
        / "test_fc1204_complexity_ratchet.py"
    )
    assigns = _top_level_assignments(
        _read_text(test, "wiki FC-1204 complexity ratchet")
    )
    if "FROZEN_MAX" not in assigns or "NEW_FILE_MAX" not in assigns:
        raise ValueError(f"FROZEN_MAX/NEW_FILE_MAX missing from {test}")
    new_file_max = ast.literal_eval(assigns["NEW_FILE_MAX"])
    return {
        "kind": "per-file-frozen-max",
        "new_file_max": int(new_file_max),
        "frozen_max": dict(sorted(_literal_dict(assigns["FROZEN_MAX"]).items())),
        "source": "tests/contract/test_fc1204_complexity_ratchet.py",
    }


def _scan_pins(root: Path, pattern: str, targets: list[str]) -> list[dict[str, Any]]:
    regex = re.compile(pattern)
    hits: list[dict[str, Any]] = []
    for rel in targets:
        path = root.parent / rel
        if not path.is_file():
            continue
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for pin in regex.findall(line):
                hits.append({"target": rel, "line": line_no, "pin": pin})
    return hits


def _wiki_hardcoding(root: Path) -> dict[str, Any]:
    gate = (
        DEFAULT_REPOS["wiki"](root)
        / "src"
        / "company_wiki"
        / "source_catalog"
        / "architecture_gate.py"
    )
    assigns = _top_level_assignments(_read_text(gate, "wiki architecture gate"))
    if (
        "_ROOT_HARDCODE_TOKENS" not in assigns
        or "_ROOT_HARDCODE_ALLOWED_FILES" not in assigns
    ):
        raise ValueError(
            "FC-1201 root-hardcode constants missing from architecture_gate.py"
        )
    tokens = sorted(_string_collection(assigns["_ROOT_HARDCODE_TOKENS"]))
    allowlist = sorted(_string_collection(assigns["_ROOT_HARDCODE_ALLOWED_FILES"]))
    return {
        "frozen_tokens": tokens,
        "allowlist": allowlist,
        "source_hash": _canonical_hash(tokens, allowlist),
        "source": "src/company_wiki/source_catalog/architecture_gate.py "
        "(FC-1201 frozen allowlist)",
    }


def _revenue_hardcoding(root: Path) -> dict[str, Any]:
    # FC-1101: CI workflows must be manifest-driven — no hardcoded sibling
    # commit pins (the only hardcoding gate revenue has).  Root/company
    # token allowlists do not exist in revenue product code.
    test = root / "tests" / "test_fc1101_ci_manifest.py"
    assigns = _top_level_assignments(_read_text(test, "revenue FC-1101 gate"))
    pattern: str | None = None
    pattern_node = assigns.get("SHA1")
    if pattern_node is not None and isinstance(pattern_node, ast.Call):
        if pattern_node.args and isinstance(pattern_node.args[0], ast.Constant):
            first = pattern_node.args[0].value
            if isinstance(first, str):
                pattern = first
    if pattern is None:
        raise ValueError(
            "SHA1 pin regex not extractable from tests/test_fc1101_ci_manifest.py"
        )
    targets = [
        "revenue-forecast/.github/workflows/quality.yml",
        "filing-fetch/.github/workflows/quality.yml",
    ]
    return {
        "frozen_tokens": [],
        "allowlist": [],
        "source_hash": _canonical_hash([], []),
        "scan": {
            "name": "fc1101_workflow_sha_pins",
            "pattern": pattern,
            "targets": targets,
            "hits": _scan_pins(root, pattern, targets),
        },
        "note": "no root/company hardcode allowlist exists in revenue; the "
        "existing architecture gate (FC-1101) forbids hardcoded sibling "
        "commit pins in CI workflows — frozen here",
    }


def _filing_hardcoding(_root: Path) -> dict[str, Any]:
    return {
        "frozen_tokens": [],
        "allowlist": [],
        "source_hash": _canonical_hash([], []),
        "note": "no root/company hardcode allowlist gate exists in filing-fetch "
        "(FC-501 policy containment is enforced via snapshot consumption, "
        "not a token allowlist)",
    }


def _dead_callers(control_root: Path) -> dict[str, Any]:
    artifact = control_root / CODEGRAPH_ARTIFACT_REL
    text = _read_text(artifact, "CodeGraph caller report")
    payload = json.loads(text)
    targets = payload.get("caller_report", {}).get("targets", {})
    repos: dict[str, Any] = {}
    for repo_name in REPO_ORDER:
        repo_targets = targets.get(repo_name, {})
        dead = sorted(symbol for symbol, hits in repo_targets.items() if not hits)
        if dead:
            repos[repo_name] = {"kind": "frozen", "targets": dead}
        else:
            repos[repo_name] = {"kind": "none-registered", "targets": []}
    notes: dict[str, str] = {}
    for symbol in repos["wiki"]["targets"]:
        notes[f"wiki.{symbol}"] = (
            "registered as CA-003 MISSING-001 (required symbol absent from "
            "product code)"
        )
    return {
        "artifact_relpath": CODEGRAPH_ARTIFACT_REL.as_posix(),
        "input_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "repos": repos,
        "notes": notes,
    }


def compute_baseline(root: Path) -> dict[str, Any]:
    """Recompute the full baseline from the repos and the toolchain.  This
    is the SINGLE computation shared by freeze and verify — the baseline
    JSON must never carry a number that this function cannot reproduce."""
    triplet: dict[str, str] = {}
    repos: dict[str, Any] = {}
    for repo_name in REPO_ORDER:
        triplet[repo_name] = git_head(DEFAULT_REPOS[repo_name](root))
        repos[repo_name] = {
            "types": {"strict_mypy_targets": strict_targets(repo_name, root)},
            "coverage": _coverage_for(repo_name, root),
            "complexity": _complexity_for(repo_name, root),
            "hardcoding": _hardcoding_for(repo_name, root),
        }
    control_root = Path(__file__).resolve().parents[1]
    return {
        "schema_version": SCHEMA_VERSION,
        "unit": UNIT,
        "frozen_at": FROZEN_AT_UTC,
        "triplet": triplet,
        "repos": repos,
        "dead_callers": _dead_callers(control_root),
    }


def _coverage_for(repo_name: str, root: Path) -> dict[str, Any]:
    if repo_name == "revenue":
        return _revenue_coverage(root)
    if repo_name == "filing":
        return _filing_coverage(root)
    return _wiki_coverage(root)


def _complexity_for(repo_name: str, root: Path) -> dict[str, Any]:
    if repo_name == "wiki":
        return _wiki_complexity(root)
    return {
        "kind": "enforced-on-new/changed-only",
        "max_complexity": MAX_CRITICAL_COMPLEXITY,
        "note": f"no whole-repo complexity gate exists in this repo; "
        f"uc.quality.check_critical_complexity() enforces complexity <= "
        f"{MAX_CRITICAL_COMPLEXITY} on new/changed critical functions "
        "(no whole-repo number is invented)",
    }


def _hardcoding_for(repo_name: str, root: Path) -> dict[str, Any]:
    if repo_name == "wiki":
        return _wiki_hardcoding(root)
    if repo_name == "revenue":
        return _revenue_hardcoding(root)
    return _filing_hardcoding(root)


# ---------------------------------------------------------------------------
# Freeze / verify
# ---------------------------------------------------------------------------


def freeze(root: Path, output: Path, force: bool = False) -> str:
    """Compute and publish the baseline once; refuses to overwrite an
    existing baseline unless ``force`` (CAS replace with the current hash).
    Returns the baseline content hash."""
    payload = compute_baseline(root)
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    if force and output.is_file():
        return cas_update(output, data, sha256_file(output))
    if not exclusive_publish(output, data):
        raise FileExistsError(
            f"quality baseline already exists at {output}; pass --force to CAS-replace"
        )
    return sha256_bytes(data)


def _verify_floor_map(
    repo_name: str,
    dimension: str,
    frozen_map: dict[str, Any],
    current_map: dict[str, Any],
    problems: list[str],
) -> None:
    for key, floor in sorted(frozen_map.items()):
        if key not in current_map:
            problems.append(
                f"{repo_name}/{dimension}: frozen floor for {key} lost "
                "(constraint removed from the ratchet)"
            )
        elif floor < current_map[key]:
            problems.append(
                f"{repo_name}/{dimension}: frozen floor {floor} for {key} is "
                f"below the recomputed {current_map[key]} (threshold may "
                "only stay-or-rise)"
            )


def _verify_types(
    repo_name: str, fr: dict[str, Any], cr: dict[str, Any], problems: list[str]
) -> None:
    frozen_set = set(fr.get("types", {}).get("strict_mypy_targets", []))
    current_set = set(cr.get("types", {}).get("strict_mypy_targets", []))
    dropped = sorted(frozen_set - current_set)
    if dropped:
        problems.append(
            f"{repo_name}/types: strict-mypy target set shrank — files no "
            f"longer strict-checked: {dropped} (target set may only grow)"
        )


def _verify_coverage(
    repo_name: str, fr: dict[str, Any], cr: dict[str, Any], problems: list[str]
) -> None:
    fc = fr.get("coverage", {})
    cc = cr.get("coverage", {})
    frozen_map: dict[str, Any] = {}
    current_map: dict[str, Any] = {}
    if "total_floor" in fc and "total_floor" in cc:
        frozen_map["total_floor"] = fc["total_floor"]
        current_map["total_floor"] = cc["total_floor"]
    frozen_map.update(fc.get("per_module_floors", {}))
    current_map.update(cc.get("per_module_floors", {}))
    frozen_map.update(fc.get("floors", {}))
    current_map.update(cc.get("floors", {}))
    _verify_floor_map(repo_name, "coverage", frozen_map, current_map, problems)


def _verify_complexity(
    repo_name: str, fr: dict[str, Any], cr: dict[str, Any], problems: list[str]
) -> None:
    fc = fr.get("complexity", {})
    cc = cr.get("complexity", {})
    frozen_max = fc.get("frozen_max", {})
    current_max = cc.get("frozen_max", {})
    for file_rel, frozen in sorted(frozen_max.items()):
        if file_rel not in current_max:
            problems.append(
                f"{repo_name}/complexity: frozen max for {file_rel} lost "
                "(constraint removed from the ratchet)"
            )
        elif frozen > current_max[file_rel]:
            problems.append(
                f"{repo_name}/complexity: frozen max {frozen} for {file_rel} "
                f"exceeds the recomputed {current_max[file_rel]} (complexity "
                "may only stay-or-fall)"
            )
    if (
        "new_file_max" in fc
        and "new_file_max" in cc
        and fc["new_file_max"] > cc["new_file_max"]
    ):
        problems.append(
            f"{repo_name}/complexity: frozen new-file max {fc['new_file_max']} "
            f"exceeds the recomputed {cc['new_file_max']}"
        )


def _verify_hardcoding(
    repo_name: str, fr: dict[str, Any], cr: dict[str, Any], problems: list[str]
) -> None:
    fc = fr.get("hardcoding", {})
    cc = cr.get("hardcoding", {})
    removed_tokens = sorted(
        set(fc.get("frozen_tokens", [])) - set(cc.get("frozen_tokens", []))
    )
    if removed_tokens:
        problems.append(
            f"{repo_name}/hardcoding: frozen root tokens removed: "
            f"{removed_tokens} (token set may only grow)"
        )
    frozen_allowlist = set(fc.get("allowlist", []))
    current_allowlist = set(cc.get("allowlist", []))
    grown = sorted(frozen_allowlist - current_allowlist)
    if grown:
        problems.append(
            f"{repo_name}/hardcoding: frozen allowlist grew beyond the "
            f"recomputed set: {grown} (allowlist may only shrink)"
        )
    frozen_scan = fc.get("scan")
    current_scan = cc.get("scan")
    if frozen_scan is not None:
        if current_scan is None:
            problems.append(
                f"{repo_name}/hardcoding: frozen scan "
                f"{frozen_scan.get('name')} is no longer computed"
            )
            return
        if frozen_scan.get("pattern") != current_scan.get("pattern") or frozen_scan.get(
            "targets"
        ) != current_scan.get("targets"):
            problems.append(
                f"{repo_name}/hardcoding: frozen scan definition changed "
                "(pattern/targets)"
            )
        new_hits = [
            hit
            for hit in current_scan.get("hits", [])
            if hit not in frozen_scan.get("hits", [])
        ]
        if new_hits:
            problems.append(
                f"{repo_name}/hardcoding: new hardcoded values detected by "
                f"the frozen scan: {new_hits}"
            )


def _verify_dead_callers(
    frozen: dict[str, Any], current: dict[str, Any], problems: list[str]
) -> None:
    if frozen.get("input_hash") != current.get("input_hash"):
        problems.append(
            "dead_callers: CodeGraph caller-report input changed (artifact "
            "re-frozen); re-freeze the quality baseline to bind the new report"
        )
    frozen_repos = frozen.get("repos", {})
    current_repos = current.get("repos", {})
    for repo_name in REPO_ORDER:
        frozen_count = len(frozen_repos.get(repo_name, {}).get("targets", []))
        current_count = len(current_repos.get(repo_name, {}).get("targets", []))
        if current_count > frozen_count:
            problems.append(
                f"dead_callers/{repo_name}: dead-production-caller count rose "
                f"{frozen_count} -> {current_count}: "
                f"{current_repos.get(repo_name, {}).get('targets', [])} "
                "(count may only stay-or-fall)"
            )


def verify(root: Path, frozen: dict[str, Any]) -> list[str]:
    """Recompute the baseline and compare it against the frozen payload.

    PASS (empty list) only when the frozen baseline is bound to the current
    triplet AND every ratchet dimension matches-or-improves the recomputed
    state.  Returns named violations; any entry means exit-code 1 for the
    ``quality-verify`` CLI gate.
    """
    problems: list[str] = []
    if frozen.get("schema_version") != SCHEMA_VERSION:
        problems.append(
            f"schema: schema_version {frozen.get('schema_version')!r} != "
            f"{SCHEMA_VERSION}"
        )
    if frozen.get("unit") != UNIT:
        problems.append(f"schema: unit {frozen.get('unit')!r} != {UNIT!r}")
    current = compute_baseline(root)
    for repo_name in REPO_ORDER:
        frozen_sha = frozen.get("triplet", {}).get(repo_name)
        current_sha = current["triplet"][repo_name]
        if frozen_sha != current_sha:
            problems.append(
                f"triplet/{repo_name}: frozen {frozen_sha} != current HEAD "
                f"{current_sha} (baseline is bound to a triplet; re-freeze "
                "after deliberate review)"
            )
    for repo_name in REPO_ORDER:
        fr = frozen.get("repos", {}).get(repo_name, {})
        cr = current["repos"][repo_name]
        _verify_types(repo_name, fr, cr, problems)
        _verify_coverage(repo_name, fr, cr, problems)
        _verify_complexity(repo_name, fr, cr, problems)
        _verify_hardcoding(repo_name, fr, cr, problems)
    _verify_dead_callers(
        frozen.get("dead_callers", {}), current["dead_callers"], problems
    )
    return problems


# ---------------------------------------------------------------------------
# Critical-function complexity gate (AST McCabe, no third-party deps)
# ---------------------------------------------------------------------------


def _mccabe(node: ast.AST) -> int:
    """Cyclomatic-complexity decision points under *node*; nested functions
    are counted in their own scope, not inside their enclosing function."""
    total = 0
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        total += _mccabe(child)
    if isinstance(node, _DECISION_NODES):
        total += 1
    if isinstance(node, ast.BoolOp):
        total += len(node.values) - 1
    return total


def check_critical_complexity(
    file_text: str, max_complexity: int = MAX_CRITICAL_COMPLEXITY
) -> list[str]:
    """Flag every function (including methods) whose cyclomatic complexity
    exceeds ``max_complexity``.  Complexity = 1 + decision points
    (if/for/while/and/or/except/comprehension/assert/with, BoolOp n-1) —
    the same vocabulary as the wiki FC-1204 complexity ratchet.  Returns
    sorted ``"name:line: ..."`` violation strings (empty = gate green)."""
    try:
        tree = ast.parse(file_text)
    except SyntaxError as exc:
        return [f"unparseable source: {exc}"]
    violations: list[tuple[int, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = 1 + _mccabe(node)
            if complexity > max_complexity:
                violations.append((node.lineno, node.name, complexity))
    violations.sort()
    return [
        f"{name}:{lineno}: cyclomatic complexity {cc} > {max_complexity}"
        for lineno, name, cc in violations
    ]
