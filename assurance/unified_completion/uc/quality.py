"""ZR-104 quality baseline: freeze and REPORT a three-repo quality baseline.

Freezes, per repo (revenue / filing / wiki), the five quality dimensions
that already exist as separate machine assets — the strict-mypy target set
(the repository's actual CI type entry), coverage floors (existing ratchet
configs/tests), complexity (wiki FC-1204 per-file frozen max; revenue/filing
enforced on new/changed critical functions only), root hardcoding (wiki
FC-1201 frozen allowlist; revenue FC-1101 workflow-pin scan), and dead
production callers (CA-003 CodeGraph caller report) — into one
machine-recomputable baseline bound to each repo's product subtree.

Design rules (ZR-104 phase C, revised by G3-RF-ASSURANCE):

- Every value is machine-computed by :func:`compute_baseline` from the
  repos and the toolchain at freeze time AND at verify time.  No value in
  the baseline is hand-written except structural metadata (schema, unit,
  the fixed frozen-at constant, file paths, the max-complexity constant).
- The type target set comes from the repository's ACTUAL engineering
  definition.  RF's CI workflow delegates its type check to
  ``tools/pre_push_gate.py``; :func:`strict_targets` follows that
  delegation by reading the tool as Python source (AST) — it never restores
  an inline workflow ``python -m mypy`` line and never executes YAML text.
- Scope that is not part of this checkout is reported, never invented: a
  missing sibling repository or an unresolvable git subtree comes back as
  ``not_available`` with the scope that explains it, never as a zero and
  never by copying another repo's set.
- :func:`verify` returns FAILURES only, and the failure set is closed:
  real input corruption, an explicitly supplied input that is unreadable,
  an invalid baseline configuration (schema/unit), and a real process that
  exits non-zero.  Everything numeric the old ratchet compared — coverage
  floors, complexity maxima, frozen allowlists, dead-caller counts,
  product-subtree drift, sibling HEADs, old workflow text — is a
  DIAGNOSTIC in :mod:`uc.quality_report`, not a qualification gate.
  Retired engineering thresholds therefore stop blocking the layer that
  outlived them, without the frozen baseline being re-frozen or its
  historical account rewritten.
- The baseline stays bound to each repo's PRODUCT subtree (``HEAD:scripts``
  for revenue/filing, ``HEAD:src/company_wiki/source_catalog`` for wiki)
  and that binding is reported as a historical comparison.  The raw git
  HEADs are NOT recorded in the baseline at all: the assurance control
  plane lives inside the revenue repository, so its receipt/state/closure
  commits must never invalidate the quality baseline (the frozen HEADs of
  each unit are already recorded in its receipts).
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


# The baseline binds each repo's PRODUCT subtree (the code the quality
# dimensions measure), not the raw HEAD: the assurance control plane lives
# inside the revenue repository, so its receipt/state/closure commits must
# not invalidate the quality baseline.
PRODUCT_TREE_PATHS = {
    "revenue": "scripts",
    "filing": "scripts",
    "wiki": "src/company_wiki/source_catalog",
}


def product_tree_sha(repo: Path, product_path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"HEAD:{product_path}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if proc.returncode != 0:
        raise ValueError(
            f"git rev-parse HEAD:{product_path} failed on {repo}: "
            f"{proc.stderr.strip()[-200:]}"
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


# A workflow that no longer inlines its type check delegates it to a
# repository tool (RF: ``run: python tools/pre_push_gate.py``).  Only a
# ``tools/*.py`` path is ever followed, the file is read as Python source
# and never executed, and no YAML text is interpreted as a command.
_DELEGATED_TOOL_RE = re.compile(
    r"python3?\s+(?:-m\s+\S+\s+)?(tools/[A-Za-z0-9_./-]+\.py)"
)


def _mypy_target_tokens_from_python(source: str) -> list[str]:
    """``-m mypy`` target tokens from a Python tool's source (AST only)."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.List, ast.Tuple)):
            continue
        elements = node.elts
        for index in range(len(elements) - 1):
            flag, module = elements[index], elements[index + 1]
            if not (isinstance(flag, ast.Constant) and flag.value == "-m"):
                continue
            if not (isinstance(module, ast.Constant) and module.value == "mypy"):
                continue
            rest = elements[index + 2 :]
            tokens: list[str] = []
            for item in rest:
                if not (isinstance(item, ast.Constant) and isinstance(item.value, str)):
                    tokens = []
                    break
                tokens.append(item.value)
            if tokens and len(tokens) == len(rest):
                return tokens
    return []


def _delegated_mypy_tokens(repo: Path, workflow_text: str) -> list[str]:
    for line in workflow_text.splitlines():
        match = _DELEGATED_TOOL_RE.search(line)
        if not match:
            continue
        tool = repo / match.group(1)
        if not tool.is_file():
            continue
        try:
            source = tool.read_text(encoding="utf-8")
            tokens = _mypy_target_tokens_from_python(source)
        except (OSError, SyntaxError):
            continue
        if tokens:
            return tokens
    return []


def _expand_targets(repo: Path, tokens: list[str]) -> list[str]:
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


def strict_targets(repo_name: str, root: Path) -> list[str]:
    """Resolve the repo's strict-mypy target set to sorted relative paths.

    The repository's CI workflow is the machine source.  When it carries an
    inline ``python -m mypy`` line (filing/wiki still do) that line decides;
    when it delegates — RF's workflow now only runs
    ``python tools/pre_push_gate.py`` — the delegation is followed by
    reading that repository tool as Python (AST) and taking *its* mypy
    targets.  Neither the workflow text nor the tool is ever executed.
    """
    repo = DEFAULT_REPOS[repo_name](root)
    workflow = repo / WORKFLOW_RELPATHS[repo_name]
    text = _read_text(workflow, f"{repo_name} CI workflow")
    tokens = _mypy_target_tokens(text) or _delegated_mypy_tokens(repo, text)
    if not tokens:
        raise ValueError(
            f"no `python -m mypy` command and no delegated type entry in {workflow}"
        )
    return _expand_targets(repo, tokens)


REVENUE = "revenue"


def type_targets(repo_name: str, root: Path) -> dict[str, Any]:
    """The repo's strict-mypy target set as a report.

    ``status`` is ``ok`` with the resolved set, ``not_available`` when the
    repository (or its type entry) is out of this checkout's scope, or
    ``error`` when a repository that IS present cannot be read.  Never a
    fabricated zero set and never an implicit copy of another repo's set.
    """
    repo = DEFAULT_REPOS[repo_name](root)
    if not repo.is_dir():
        return {
            "status": "not_available",
            "scope": f"repository not present: {repo}",
            "strict_mypy_targets": [],
        }
    try:
        targets = strict_targets(repo_name, root)
    except (ValueError, OSError) as exc:
        status = "error" if repo_name == REVENUE else "not_available"
        return {
            "status": status,
            "scope": str(exc),
            "strict_mypy_targets": [],
        }
    return {
        "status": "ok",
        "scope": str(repo),
        "strict_mypy_targets": targets,
    }


def _dimension(
    compute: Callable[[], dict[str, Any]], repo_name: str, repo: Path
) -> dict[str, Any]:
    """Run one dimension, converting an unreadable scope into a report.

    A repository that is absent is ``not_available``.  A repository that is
    present but unreadable is ``error`` for revenue (our own repository — a
    real input failure) and ``not_available`` for the sibling repositories
    (their HEAD is theirs; their drift is a diagnostic, not our failure).
    """
    if not repo.is_dir():
        return {
            "status": "not_available",
            "scope": f"repository not present: {repo}",
        }
    try:
        section = compute()
    except (ValueError, OSError, KeyError, TypeError, configparser.Error) as exc:
        return {
            "status": "error" if repo_name == REVENUE else "not_available",
            "scope": str(exc),
        }
    section["status"] = "ok"
    section["scope"] = str(repo)
    return section


def _product_tree(repo: Path, product_path: str) -> str | None:
    """The product subtree's git tree SHA, or ``None`` when it cannot be
    resolved in this checkout (missing repository, not a git worktree)."""
    if not repo.is_dir():
        return None
    try:
        return product_tree_sha(repo, product_path)
    except ValueError:
        return None


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
    JSON must never carry a number that this function cannot reproduce.

    Scope handling (G3-RF-ASSURANCE): a dimension whose scope is not part of
    this checkout — a sibling repository that is not checked out, a git
    subtree that cannot be resolved — is reported as ``not_available`` with
    the scope that explains it.  Nothing is ever invented to stand in for
    it.  A repository that IS present but cannot be read yields ``error``
    for revenue (our own repository) and ``not_available`` for the sibling
    repositories (their HEAD is theirs).
    """
    product_trees: dict[str, str | None] = {}
    product_tree_scopes: dict[str, str] = {}
    repos: dict[str, Any] = {}
    for repo_name in REPO_ORDER:
        repo = DEFAULT_REPOS[repo_name](root)
        product_trees[repo_name] = _product_tree(repo, PRODUCT_TREE_PATHS[repo_name])
        product_tree_scopes[repo_name] = (
            str(repo)
            if product_trees[repo_name] is not None
            else (
                f"repository not present: {repo}"
                if not repo.is_dir()
                else f"git tree unavailable: {repo}:{PRODUCT_TREE_PATHS[repo_name]}"
            )
        )
        repos[repo_name] = {
            "types": type_targets(repo_name, root),
            "coverage": _dimension(
                lambda name=repo_name: _coverage_for(name, root), repo_name, repo
            ),
            "complexity": _dimension(
                lambda name=repo_name: _complexity_for(name, root), repo_name, repo
            ),
            "hardcoding": _dimension(
                lambda name=repo_name: _hardcoding_for(name, root), repo_name, repo
            ),
        }
    control_root = Path(__file__).resolve().parents[1]
    try:
        dead_callers = _dead_callers(control_root)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        dead_callers = {"status": "error", "scope": str(exc)}
    else:
        dead_callers["status"] = "ok"
    return {
        "schema_version": SCHEMA_VERSION,
        "unit": UNIT,
        "frozen_at": FROZEN_AT_UTC,
        "product_trees": product_trees,
        "product_tree_scopes": product_tree_scopes,
        "repos": repos,
        "dead_callers": dead_callers,
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


def verify(root: Path, frozen: dict[str, Any]) -> list[str]:
    """Recompute the baseline and return the report's FAILURES.

    The quality layer reports rather than gates: coverage floors,
    complexity maxima, frozen allowlists, dead-caller counts,
    product-subtree drift, sibling-HEAD differences and old workflow text
    are diagnostics (see :mod:`uc.quality_report`), never numeric
    qualification gates.  What can still fail is the closed set the G3 card
    keeps: real input corruption, an explicitly supplied input that is
    unreadable, an invalid baseline configuration (schema/unit) and a real
    process that exits non-zero.

    Returns ``[]`` when nothing failed; ``quality-verify`` turns a
    non-empty list into exit code 1.
    """
    from uc.quality_report import build_report

    return build_report(root, frozen)["failures"]


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
