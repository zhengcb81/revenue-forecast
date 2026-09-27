"""ZR-105 current-triplet CI required-checks contract and gap assessor.

The contract freezes what a current-triplet CI gate MUST enforce (exact
triplet binding, affected-repo fan-out, controlled collected/skip delta);
the actual fan-out scheduling/attestation is CA-201's job (phase H), so
this module only EVALUATES the three real workflows read-only and reports
the honest gap — gaps are the expected current state and each maps to the
CA-201 successor.

Deterministic: the assessment depends only on the workflow file contents
and the frozen contract (``evaluated_at`` is wall-clock only, excluded
from the checks).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
UNIT = "ZR-105"
REPO_ROOT = Path(__file__).resolve().parents[3]
CONTROL_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = CONTROL_ROOT / "ci" / "current_triplet_contract.json"

REPOS = {
    "revenue": REPO_ROOT,
    "filing": REPO_ROOT.parent / "filing-fetch",
    "wiki": REPO_ROOT.parent / "company-wiki",
}

# repo -> workflow rel path inside its own repo
WORKFLOW_RELS = {
    "revenue": ".github/workflows/quality.yml",
    "filing": ".github/workflows/quality.yml",
    "wiki": ".github/workflows/ci.yml",
}

_SHA_RE = re.compile(r"\b[0-9a-f]{40}\b")
_CLONE_RE = re.compile(r"\bgit\s+clone\b")
_MANIFEST_RE = re.compile(r"compatibility/current\.json")
_SIBLING_CHECKOUT_RE = re.compile(
    r"ci_checkout_siblings|checkout.*sibling|actions/checkout.*path"
)
_FANOUT_MARKER_RE = re.compile(r"repository_dispatch|workflow_run")
_COLLECT_RE = re.compile(r"collect-only|--collect-only|collected")
_SKIP_RE = re.compile(r"skip")
_TRUE_SWALLOW_RE = re.compile(r"\|\|\s*true")
_BASELINE_RE = re.compile(r"baseline|delta|--tb=no.*-q.*--lf|lastfailed")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_workflow(repo_name: str, root: Path = REPO_ROOT) -> str:
    repo = REPOS[repo_name]
    return (repo / WORKFLOW_RELS[repo_name]).read_text(encoding="utf-8")


def _read_workflow_bytes(repo_name: str, root: Path = REPO_ROOT) -> bytes:
    repo = REPOS[repo_name]
    return (repo / WORKFLOW_RELS[repo_name]).read_bytes()


def _line_hits(text: str, pattern: re.Pattern) -> list[str]:
    hits: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            hits.append(f"{lineno}: {line.strip()[:120]}")
    return hits


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _check_exact_triplet_binding(
    repo_name: str, text: str, contract: dict[str, Any]
) -> dict[str, Any]:
    frozen = contract["triplet"]
    problems: list[str] = []
    if repo_name == "revenue":
        manifest_hits = _line_hits(text, _MANIFEST_RE)
        checkout_hits = _line_hits(text, _SIBLING_CHECKOUT_RE)
        if not manifest_hits or not checkout_hits:
            problems.append(
                "workflow lacks manifest-driven sibling checkout "
                f"(manifest hits: {manifest_hits}, checkout hits: {checkout_hits})"
            )
        manifest_path = REPOS["revenue"] / "compatibility" / "current.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            current = manifest.get("current_triplet", {})
            stale = {
                name: sha for name, sha in frozen.items() if current.get(name) != sha
            }
            if stale:
                problems.append(
                    f"compatibility/current.json triplet is stale vs frozen "
                    f"contract: {stale}"
                )
        else:
            problems.append("compatibility/current.json missing")
    elif repo_name == "filing":
        clone_hits = _line_hits(text, _CLONE_RE)
        pinned = _line_hits(text, _SHA_RE)
        if clone_hits and not pinned:
            problems.append(f"floating git clone without pinned sha: {clone_hits}")
        checkout_hits = _line_hits(text, _SIBLING_CHECKOUT_RE)
        if not checkout_hits:
            problems.append("no manifest-driven sibling checkout evidence")
    else:  # wiki
        if not (_line_hits(text, _SIBLING_CHECKOUT_RE) or _line_hits(text, _SHA_RE)):
            problems.append("no sibling checkout / pinned sha evidence in wiki ci.yml")
    return {
        "satisfied": not problems,
        "evidence": problems or ["workflow binds the exact triplet"],
        "successor": contract["successors"]["exact_triplet_binding"],
    }


def _check_affected_repo_fanout(text: str, contract: dict[str, Any]) -> dict[str, Any]:
    hits = _line_hits(text, _FANOUT_MARKER_RE)
    return {
        "satisfied": bool(hits),
        "evidence": hits
        or [
            "only own-repo triggers (push/pull_request); no cross-repo fan-out "
            "marker (repository_dispatch/workflow_run)"
        ],
        "successor": contract["successors"]["affected_repo_fanout"],
    }


def _check_collected_skip_delta(text: str, contract: dict[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    collect_hits = _line_hits(text, _COLLECT_RE)
    baseline_hits = _line_hits(text, _BASELINE_RE)
    if not collect_hits or not baseline_hits:
        problems.append(
            f"no collected/skip delta control (collect hits: {collect_hits}, "
            f"baseline hits: {baseline_hits})"
        )
    swallows = _line_hits(text, _TRUE_SWALLOW_RE)
    if swallows:
        problems.append(f"unconditional `|| true` swallows: {swallows}")
    return {
        "satisfied": not problems,
        "evidence": problems or ["collected/skip delta controlled"],
        "successor": contract["successors"]["collected_skip_delta_controlled"],
    }


def evaluate(
    root: Path = REPO_ROOT, contract: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Evaluate the frozen required checks against the three real workflows."""
    frozen = contract or load_contract()
    checks: dict[str, Any] = {}
    for repo_name in ("revenue", "filing", "wiki"):
        text = _read_workflow(repo_name, root)
        raw = _read_workflow_bytes(repo_name, root)
        checks[repo_name] = {
            "workflow_file": f"{repo_name}/{WORKFLOW_RELS[repo_name]}",
            "workflow_sha256": _sha256_bytes(raw),
            "checks": {
                "exact_triplet_binding": _check_exact_triplet_binding(
                    repo_name, text, frozen
                ),
                "affected_repo_fanout": _check_affected_repo_fanout(text, frozen),
                "collected_skip_delta_controlled": _check_collected_skip_delta(
                    text, frozen
                ),
            },
        }
    gaps = [
        f"{repo_name}/{check_name}"
        for repo_name, section in checks.items()
        for check_name, result in section["checks"].items()
        if not result["satisfied"]
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "unit": UNIT,
        "evaluated_at_utc": utc_now(),
        "triplet": frozen["triplet"],
        "workflow_files": frozen["workflow_files"],
        "repos": checks,
        "gaps": sorted(gaps),
        "successor": "CA-201",
    }


def assess(
    root: Path = REPO_ROOT, contract: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Evaluate + add the workflow-frozen-hash drift view (contract vs now)."""
    frozen = contract or load_contract()
    report = evaluate(root, frozen)
    drift = {}
    for repo_name in ("revenue", "filing", "wiki"):
        frozen_sha = frozen["workflow_files"][repo_name]["sha256"]
        current_sha = report["repos"][repo_name]["workflow_sha256"]
        drift[repo_name] = {
            "frozen_sha256": frozen_sha,
            "current_sha256": current_sha,
            "unchanged": frozen_sha == current_sha,
        }
    report["workflow_drift"] = drift
    return report
