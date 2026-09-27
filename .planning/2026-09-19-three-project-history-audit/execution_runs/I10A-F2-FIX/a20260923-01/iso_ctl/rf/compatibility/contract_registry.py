"""FC-101: contract ownership registry loader + validator.

The seven data-lake contracts (RootPolicySnapshot, NormalizedFilingMetadata,
ResolutionEnvelope, AcquisitionTrace, SourceBundle, ArtifactHandle,
ActivationSnapshot) must each have exactly ONE owning repo. company-wiki owns
all seven; filing-fetch and revenue-forecast only consume and must never
re-declare ownership or grow a second policy/allowlist strategy source.

This module loads ``compatibility/contract_registry.json`` and validates the
single-ownership + version/compat/deletion invariants. It is the machine-
readable single source of truth consumed by ``tests/test_contract_registry.py``
and, later, the receipt/closure validator (FC-103) and triplet manifest
(FC-104). Kept dependency-free (stdlib only) so it can run anywhere the
validator runs.
"""

from __future__ import annotations

import json
from pathlib import Path

SCHEMA_VERSION = "1.0"
REGISTRY_PATH = Path(__file__).resolve().parent / "contract_registry.json"

# Closed set: the seven data-lake contracts whose ownership FC-101 freezes.
# Adding an eighth requires a new FC that extends this tuple.
MANDATORY_CONTRACTS = (
    "RootPolicySnapshot",
    "NormalizedFilingMetadata",
    "ResolutionEnvelope",
    "AcquisitionTrace",
    "SourceBundle",
    "ArtifactHandle",
    "ActivationSnapshot",
)

REQUIRED_CONTRACT_FIELDS = (
    "owner_repo",
    "version",
    "introduced_by_fc",
    "consumed_by_repos",
    "n_minus_1_supported",
    "compat_window",
    "deletion_deadline",
    "deletion_deadline_fc_gate",
    "canonical_doc_path",
)

_HEX = set("0123456789abcdef")


def load(path: Path | None = None) -> dict:
    """Load and return the contract registry JSON."""
    target = path or REGISTRY_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def _is_full_sha1(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(c in _HEX for c in value.lower())
    )


def validate(data: dict) -> list[str]:
    """Return invariant violations; an empty list means the registry is valid.

    Structural checks only (single owner per contract, required fields, closed
    contract set, full triplet hashes). The semantic invariant "all seven are
    owned by company-wiki" is asserted separately by the test suite so that a
    future multi-owner architecture is not silently blocked by a hard-coded
    repo name inside the validator.
    """
    problems: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION!r}")

    triplet = data.get("frozen_at_triplet")
    if not isinstance(triplet, dict) or set(triplet) != {"revenue", "filing", "wiki"}:
        problems.append("frozen_at_triplet must have exactly keys {revenue, filing, wiki}")
    else:
        for repo, digest in triplet.items():
            if not _is_full_sha1(digest):
                problems.append(f"frozen_at_triplet.{repo} must be a 40-char hex SHA-1")

    if not data.get("strategy_source_invariant"):
        problems.append("strategy_source_invariant must be a non-empty string")

    contracts = data.get("contracts")
    if not isinstance(contracts, dict) or not contracts:
        problems.append("contracts must be a non-empty object")
        return problems

    names = set(contracts)
    for missing in set(MANDATORY_CONTRACTS) - names:
        problems.append(f"missing mandatory contract {missing!r}")
    for extra in names - set(MANDATORY_CONTRACTS):
        problems.append(
            f"unexpected contract {extra!r}; the registry is a closed set of "
            f"the seven data-lake contracts"
        )

    for name, spec in contracts.items():
        if not isinstance(spec, dict):
            problems.append(f"{name}: spec must be an object")
            continue
        for field in REQUIRED_CONTRACT_FIELDS:
            if spec.get(field) in (None, ""):
                problems.append(f"{name}: missing/empty required field {field!r}")
        owner = spec.get("owner_repo")
        if isinstance(owner, (list, tuple)):
            problems.append(
                f"{name}: owner_repo must be a single repo — a second entry is a "
                f"forbidden second strategy source"
            )
        elif not isinstance(owner, str) or not owner:
            problems.append(f"{name}: owner_repo must be a single non-empty string")
        consumers = spec.get("consumed_by_repos")
        if not isinstance(consumers, list) or not consumers:
            problems.append(f"{name}: consumed_by_repos must be a non-empty list")
        if isinstance(owner, str) and isinstance(consumers, list) and owner in consumers:
            problems.append(f"{name}: owner_repo must not appear in its own consumed_by_repos")
    return problems
