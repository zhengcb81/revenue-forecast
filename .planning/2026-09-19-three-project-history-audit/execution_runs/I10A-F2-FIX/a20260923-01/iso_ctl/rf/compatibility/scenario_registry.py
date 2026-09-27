"""FC-102: scenario registry loader + validator.

The machine-readable single source for the 95 mandatory E2E/audit scenarios
declared in ``scenario_matrix.md``. Each scenario decomposes its declared
tiers into independent tier entries (T1/T2/T3/T4 are NOT substitutable), and
cross-process tiers require ``process_count >= 3`` — a test claiming E2E with
``process_count < 3`` is a forbidden fake-E2E.

This module loads ``compatibility/scenario_registry.json`` and validates the
internal invariants. It is consumed by ``tests/test_scenario_registry.py`` and
the later scenario-coverage gate (FC-1003 / FC-1101). The hard
"every-mandatory-ID-covered-by-a-real-test" gate is a Phase-10 concern; FC-102
delivers the registry + this integrity validator.
"""

from __future__ import annotations

import json
from pathlib import Path

SCHEMA_VERSION = "1.0"
REGISTRY_PATH = Path(__file__).resolve().parent / "scenario_registry.json"

VALID_TIERS = ("T0", "T1", "T2", "T3", "T4")
CROSS_PROCESS_TIERS = ("T1", "T2", "T3", "T4")
EXPECTED_TOTAL = 95

SIDE_EFFECT_KEYS = (
    "provider_discover_calls",
    "provider_fetch_calls",
    "canonical_write_calls",
    "external_root_write_calls",
    "parser_calls",
    "llm_calls",
    "artifact_read_calls",
)

REQUIRED_SCENARIO_FIELDS = (
    "id",
    "category",
    "declared_tiers",
    "tier_entries",
    "must_result",
    "substitutability",
)

REQUIRED_TIER_ENTRY_FIELDS = (
    "owner_fc",
    "process_count",
    "fixture_or_sample_id",
    "oracle",
    "side_effect_budget",
    "timeout_seconds",
    "freshness_window",
    "evidence_path",
)

_HEX = set("0123456789abcdef")


def load(path: Path | None = None) -> dict:
    target = path or REGISTRY_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def _is_full_sha1(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(c in _HEX for c in value.lower())
    )


def validate(data: dict) -> list[str]:
    """Return invariant violations; empty list means the registry is valid."""
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

    total = data.get("total_mandatory")
    if total != EXPECTED_TOTAL:
        problems.append(f"total_mandatory must be {EXPECTED_TOTAL}, got {total!r}")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        problems.append("scenarios must be a list")
        return problems

    if len(scenarios) != EXPECTED_TOTAL:
        problems.append(f"scenarios must contain {EXPECTED_TOTAL} entries, got {len(scenarios)}")

    seen: set[str] = set()
    for scen in scenarios:
        if not isinstance(scen, dict):
            problems.append("scenario entry is not an object")
            continue
        sid = scen.get("id", "<missing>")
        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in scen or scen[field] in (None, ""):
                problems.append(f"{sid}: missing/empty required field {field!r}")
        if isinstance(sid, str):
            if sid in seen:
                problems.append(f"duplicate scenario id {sid!r}")
            seen.add(sid)
        declared = scen.get("declared_tiers")
        if not isinstance(declared, list) or not declared:
            problems.append(f"{sid}: declared_tiers must be a non-empty list")
            continue
        for t in declared:
            if t not in VALID_TIERS:
                problems.append(f"{sid}: invalid tier {t!r} (valid: {VALID_TIERS})")
        entries = scen.get("tier_entries")
        if not isinstance(entries, dict):
            problems.append(f"{sid}: tier_entries must be an object")
            continue
        if set(entries) != set(declared):
            problems.append(
                f"{sid}: tier_entries keys {sorted(entries)} != declared_tiers {sorted(declared)}"
            )
        for tier, entry in entries.items():
            if not isinstance(entry, dict):
                problems.append(f"{sid}.{tier}: entry must be an object")
                continue
            for field in REQUIRED_TIER_ENTRY_FIELDS:
                if field not in entry:
                    problems.append(f"{sid}.{tier}: missing field {field!r}")
                elif field == "freshness_window":
                    # None is a valid value: unit/T1 tiers have no freshness window.
                    continue
                elif entry[field] in (None, ""):
                    problems.append(f"{sid}.{tier}: empty field {field!r}")
            pc = entry.get("process_count")
            expected_pc = 1 if tier == "T0" else 3
            if not isinstance(pc, int) or pc < 1:
                problems.append(f"{sid}.{tier}: process_count must be a positive int, got {pc!r}")
            elif tier in CROSS_PROCESS_TIERS and pc < 3:
                problems.append(
                    f"{sid}.{tier}: cross-process tier claims E2E with process_count={pc} (<3) — fake E2E"
                )
            elif tier == "T0" and pc != 1:
                problems.append(f"{sid}.{tier}: T0 (unit) process_count must be 1, got {pc}")
            budget = entry.get("side_effect_budget")
            if isinstance(budget, dict):
                for key, val in budget.items():
                    if key not in SIDE_EFFECT_KEYS:
                        problems.append(f"{sid}.{tier}: unknown side-effect key {key!r}")
                    if not (val == 0 or val == "scenario-defined"):
                        problems.append(
                            f"{sid}.{tier}.{key}: budget must be 0 or 'scenario-defined', got {val!r}"
                        )
            else:
                problems.append(f"{sid}.{tier}: side_effect_budget must be an object")
    return problems


def ids(data: dict) -> list[str]:
    return [s.get("id", "") for s in data.get("scenarios", []) if isinstance(s, dict)]
