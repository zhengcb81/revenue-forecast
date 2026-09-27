"""FC-104: current compatibility manifest + frozen command registry validator.

The manifest (``current.json``) pins the three-repo remotes, the frozen FCAP
baseline triplet (the immovable floor), the current triplet, the contract
versions, the Python/platform matrix, and the hashes of the contract,
scenario, and command registries. CI and local runners must consume only this
manifest — no scattered commits inside workflows.

Two hard gates:

1. **Registry tamper detection** — each sha256 in the manifest must equal the
   actual file hash (contract / scenario / command registry).
2. **Baseline descendant invariant** — every repo's HEAD must be the frozen
   baseline commit or a descendant of it. A sibling reset below the frozen
   baseline makes the manifest go RED.

``command_registry.json`` freezes the real commands (id, owner, argv, tier,
timeout, write/network budget, expected collected baseline). Commands whose
baseline has not yet been measured on the current branch must honestly say
``pending-first-measurement``; they are never fabricated.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

SCHEMA_VERSION = "1.0"
REGISTRY_PATH = Path(__file__).resolve().parent / "current.json"
COMMAND_REGISTRY_PATH = Path(__file__).resolve().parent / "command_registry.json"
CONTRACT_REGISTRY_PATH = Path(__file__).resolve().parent / "contract_registry.json"
SCENARIO_REGISTRY_PATH = Path(__file__).resolve().parent / "scenario_registry.json"

# The FCAP-2026-08-09-r2 frozen main-branch baseline. Never moved; if the
# real repos ever reset below this, the manifest must fail.
FROZEN_BASELINE = {
    "revenue": "3ce9cc4d3ea91b15aad42eff1f55b72a44834dd7",
    "filing": "c9799b722a97376f9717bcfacfa0685135dcbd15",
    "wiki": "109a1a6a77d7f4b37f849207fbd9e5d8caf2bc07",
}

REPOS = ("revenue", "filing", "wiki")
# owner_repo in the command registry uses the real repo names.
VALID_OWNER_REPOS = ("revenue-forecast", "filing-fetch", "company-wiki")
REPO_DIRS = {
    "revenue": Path(__file__).resolve().parents[2] / "revenue-forecast",
    "filing": Path(__file__).resolve().parents[2] / "filing-fetch",
    "wiki": Path(__file__).resolve().parents[2] / "company-wiki",
}
VALID_TIERS = ("T0", "T1", "T2", "T3", "T4")
VALID_WRITES = ("temp_only", "read_only_check", "isolated_audit_output", "authorized_apply")
_HEX = set("0123456789abcdef")


def load_manifest(path: Path | None = None) -> dict:
    target = path or REGISTRY_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def load_command_registry(path: Path | None = None) -> dict:
    target = path or COMMAND_REGISTRY_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_sha1(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(c in _HEX for c in value.lower())
    )


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in _HEX for c in value.lower())
    )


def _is_descendant(baseline: str, head: str, repo_dir: Path) -> bool:
    """True when ``head`` is ``baseline`` or a descendant (merge-base gate)."""
    if baseline == head:
        return True
    proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline, head],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    return proc.returncode == 0


def validate_manifest(data: dict) -> list[str]:
    """Return manifest invariant violations; empty list means valid."""
    problems: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION!r}")

    remotes = data.get("remotes")
    if not isinstance(remotes, dict) or set(remotes) != set(REPOS):
        problems.append(f"remotes must have exactly keys {set(REPOS)}")
    elif any(not remotes.get(r) for r in REPOS):
        problems.append("remotes must be non-empty for all three repos")

    baseline = data.get("frozen_baseline_triplet")
    if baseline != FROZEN_BASELINE:
        problems.append("frozen_baseline_triplet does not match the FCAP frozen baseline")

    current = data.get("current_triplet")
    if not isinstance(current, dict) or set(current) != set(REPOS):
        problems.append(f"current_triplet must have exactly keys {set(REPOS)}")
    else:
        for repo in REPOS:
            if not _is_sha1(current.get(repo)):
                problems.append(f"current_triplet.{repo} must be a 40-char hex SHA-1")

    versions = data.get("contract_versions")
    if not isinstance(versions, dict):
        problems.append("contract_versions must be an object")
    else:
        registry = json.loads(CONTRACT_REGISTRY_PATH.read_text(encoding="utf-8"))
        for name, spec in registry.get("contracts", {}).items():
            if versions.get(name) != spec.get("version"):
                problems.append(
                    f"contract_versions.{name} = {versions.get(name)!r} != "
                    f"contract_registry version {spec.get('version')!r}"
                )

    checks = (
        ("contract_registry_sha256", CONTRACT_REGISTRY_PATH),
        ("scenario_registry_sha256", SCENARIO_REGISTRY_PATH),
        ("command_registry_sha256", COMMAND_REGISTRY_PATH),
    )
    for key, path in checks:
        actual = _sha256(path)
        declared = data.get(key)
        if not _is_sha256(declared):
            problems.append(f"{key} must be a 64-char hex SHA-256")
        elif declared != actual:
            problems.append(f"{key} tamper detected: manifest {declared[:10]}... != file {actual[:10]}...")

    for repo in REPOS:
        head = current.get(repo) if isinstance(current, dict) else None
        if _is_sha1(head) and not _is_descendant(FROZEN_BASELINE[repo], head, REPO_DIRS[repo]):
            problems.append(
                f"{repo} HEAD {head[:10]}... is not a descendant of the frozen baseline "
                f"{FROZEN_BASELINE[repo][:10]}... (reset/regression detected)"
            )
    return problems


def validate_command_registry(data: dict) -> list[str]:
    """Return command-registry invariant violations; empty list means valid."""
    problems: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION!r}")
    commands = data.get("commands")
    if not isinstance(commands, list) or not commands:
        problems.append("commands must be a non-empty list")
        return problems
    seen: set[str] = set()
    for cmd in commands:
        if not isinstance(cmd, dict):
            problems.append("command entry is not an object")
            continue
        cid = cmd.get("id", "<missing>")
        if cid in seen:
            problems.append(f"duplicate command id {cid!r}")
        seen.add(cid)
        if not cid:
            problems.append("command id missing")
        if cmd.get("owner_repo") not in VALID_OWNER_REPOS:
            problems.append(f"{cid}: owner_repo must be one of {sorted(VALID_OWNER_REPOS)}")
        if not isinstance(cmd.get("argv"), list) or not cmd.get("argv"):
            problems.append(f"{cid}: argv must be a non-empty list")
        if cmd.get("tier") not in VALID_TIERS:
            problems.append(f"{cid}: tier {cmd.get('tier')!r} invalid")
        if not isinstance(cmd.get("expected_min_collected"), int) or cmd["expected_min_collected"] < 0:
            problems.append(f"{cid}: expected_min_collected must be a non-negative int")
        writes = cmd.get("writes")
        if isinstance(writes, list):
            for w in writes:
                if w not in VALID_WRITES:
                    problems.append(f"{cid}: invalid write budget {w!r}")
        else:
            problems.append(f"{cid}: writes must be a list")
        if not isinstance(cmd.get("network"), bool):
            problems.append(f"{cid}: network must be a bool")
        observed = cmd.get("observed")
        if observed == "pending-first-measurement":
            continue
        if not (isinstance(observed, str) and len(observed) == 10 and observed[4] == "-"):
            problems.append(f"{cid}: observed must be an ISO date or 'pending-first-measurement'")
    return problems
