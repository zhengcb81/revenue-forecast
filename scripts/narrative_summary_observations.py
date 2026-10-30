"""Consume bounded CWP summary observations without importing its implementation.

RF checks this published wire envelope and keeps its limitations. Source task
classification, prose diagnostics and locator replay remain CWP responsibilities.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import re
from types import MappingProxyType
from typing import Any

from contracts.evidence import canonical_sha256

ASSESSED_SCHEMAS = frozenset({"narrative-bundle/2.1", "narrative-bundle/3.1"})
# Historical public alias; decisions use the explicit recipe catalog below.
PROMPT = "reading-source-scoped/4.2.0"
_BASE_DEPENDENCIES = frozenset(
    {
        "matching",
        "task_plan",
        "admission",
        "scoped_view",
        "encoding",
        "claim_roles",
        "assessment",
    }
)
_BASE_RULES = frozenset(
    {
        "possible_attribution_loss",
        "possible_negation_degree_loss",
        "possible_modality_mismatch",
        "unmatched_claim_scope",
        "ambiguous_claim_scope",
    }
)


@dataclass(frozen=True)
class _WireRecipe:
    prompt: str
    assessor: str
    dependencies: frozenset[str]
    rules: frozenset[str]
    producer: str = "1.1.0"
    plan_max_claims: int = 40


# Only published wire compatibility is registered. No CWP implementation or
# source-frame logic is imported or executed by this consumer.
_WIRE_RECIPES = MappingProxyType(
    {
        PROMPT: _WireRecipe(
            PROMPT, "source-summary-assessment/1.0.0", _BASE_DEPENDENCIES, _BASE_RULES
        ),
        "reading-source-scoped/4.3.0": _WireRecipe(
            "reading-source-scoped/4.3.0",
            "source-summary-assessment/1.1.0",
            _BASE_DEPENDENCIES | {"assertion_frames"},
            _BASE_RULES
            | {
                "possible_current_action_as_future",
                "possible_project_capacity_basis_loss",
            },
        ),
    }
)
_FIELDS = {
    "schema_version",
    "validator",
    "source_plan_sha256",
    "plan_max_claims",
    "source_admission_sha256",
    "claims_sha256",
    "scope",
    "source_admitted_task_keys",
    "requested_task_keys",
    "emitted_task_keys",
    "missing_requested_task_keys",
    "budget_deferred_task_keys",
    "excluded_tasks",
    "requested_emission_complete",
    "admitted_emission_complete",
    "subfact_coverage_status",
    "semantic_status",
    "known_constraint_status",
    "diagnostics",
    "diagnostic_count",
    "diagnostics_limited",
    "diagnostic_claim_ids",
}


def _require(condition: bool) -> None:
    if not condition:
        raise ValueError("invalid_summary_observation")


def _sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def validate_summary_observation(bundle: dict) -> dict | None:
    summary = bundle["summary"]
    model = summary["model"]
    prompt = (
        model["prompt_version"] if model is not None else bundle["versions"]["prompt"]
    )
    assessed = bundle["schema_version"] in ASSESSED_SCHEMAS
    recipe = _WIRE_RECIPES.get(prompt) if isinstance(prompt, str) else None
    _require(assessed == (recipe is not None))
    if not assessed:
        _require("summary_assessment" not in bundle)
        return None
    if recipe is None:
        raise ValueError("invalid_summary_observation")
    _require(
        bundle["versions"]["prompt"] == recipe.prompt
        and bundle["versions"]["bundle_producer"] == recipe.producer
    )
    if summary["status"] == "summary_not_needed":
        _require(
            model is None
            and summary["draft"] is None
            and bundle.get("summary_assessment") is None
        )
        _require(
            bundle["quality_status"] == "skipped_no_narrative"
            and not bundle["evidence_spans"]
            and bundle["versions"]["model"] is None
        )
        return None
    report = bundle.get("summary_assessment")
    if not isinstance(report, dict) or set(report) != _FIELDS:
        raise ValueError("invalid_summary_observation")
    _require(
        len(
            json.dumps(
                report,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode()
        )
        <= 65536
    )
    _require(
        report["schema_version"] == "summary-assessment/1"
        and report["plan_max_claims"] == recipe.plan_max_claims
    )
    _require(type(report["plan_max_claims"]) is int)
    _require(report["scope"] == "selected_source_tasks_only")
    _require(
        report["semantic_status"]
        == report["subfact_coverage_status"]
        == "not_evaluated"
    )
    _require(bundle["versions"]["model"] == model["model_id"])
    draft = summary["draft"]
    _require(isinstance(draft, dict))
    claims = draft["claims"]
    _require(
        all(
            _sha(report[name])
            for name in (
                "source_plan_sha256",
                "source_admission_sha256",
                "claims_sha256",
            )
        )
    )
    _require(report["claims_sha256"] == canonical_sha256(claims))
    validator = report["validator"]
    _require(
        isinstance(validator, dict)
        and set(validator) == {"version", "implementation_sha256", "dependencies"}
    )
    _require(
        validator["version"] == recipe.assessor
        and _sha(validator["implementation_sha256"])
    )
    _require(
        isinstance(validator["dependencies"], dict) and bool(validator["dependencies"])
    )
    _require(
        all(
            isinstance(key, str) and _sha(value)
            for key, value in validator["dependencies"].items()
        )
    )
    _require(set(validator["dependencies"]) == recipe.dependencies)
    _require(
        validator["implementation_sha256"]
        == canonical_sha256(validator["dependencies"])
    )
    _require(
        bundle["quality_status"]
        == ("needs_review" if draft["status"] == "needs_review" else "verified")
    )
    keys = {}
    for name in (
        "source_admitted_task_keys",
        "requested_task_keys",
        "emitted_task_keys",
        "missing_requested_task_keys",
        "budget_deferred_task_keys",
    ):
        rows = report[name]
        _require(
            isinstance(rows, list)
            and all(
                isinstance(key, str) and re.fullmatch(r"t[1-9][0-9]*", key)
                for key in rows
            )
        )
        _require(len(rows) == len(set(rows)))
        keys[name] = set(rows)
    admitted, requested, emitted = (
        keys[name]
        for name in (
            "source_admitted_task_keys",
            "requested_task_keys",
            "emitted_task_keys",
        )
    )
    _require(emitted <= requested <= admitted)
    _require(
        keys["missing_requested_task_keys"] == requested - emitted
        and keys["budget_deferred_task_keys"] == admitted - requested
    )
    for name, expected in (
        ("requested_emission_complete", emitted == requested),
        ("admitted_emission_complete", emitted == admitted),
    ):
        _require(type(report[name]) is bool and report[name] == expected)
    _require(isinstance(report["excluded_tasks"], list))
    excluded_keys: set[str] = set()
    for row in report["excluded_tasks"]:
        _require(
            isinstance(row, dict) and row.get("status") in ("unavailable", "duplicate")
        )
        fields = {"task_key", "status", "reason"} | (
            {"representative"} if row["status"] == "duplicate" else set()
        )
        _require(set(row) == fields)
        _require(
            isinstance(row["task_key"], str)
            and re.fullmatch(r"t[1-9][0-9]*", row["task_key"]) is not None
        )
        _require(row["task_key"] not in admitted | excluded_keys)
        excluded_keys.add(row["task_key"])
        _require(
            isinstance(row["reason"], str)
            and re.fullmatch(r"[a-z][a-z0-9_]{0,79}", row["reason"]) is not None
        )
        if row["status"] == "duplicate":
            _require(
                isinstance(row["representative"], str)
                and row["representative"] in admitted
            )
    diagnostics = report["diagnostics"]
    count = report["diagnostic_count"]
    _require(isinstance(diagnostics, list) and len(diagnostics) <= 64)
    _require(type(count) is int and count >= len(diagnostics))
    _require(
        type(report["diagnostics_limited"]) is bool
        and report["diagnostics_limited"] == (count > len(diagnostics))
    )
    _require(
        report["known_constraint_status"]
        == ("diagnostics_found" if count else "no_known_violation")
    )
    risks = report["diagnostic_claim_ids"]
    by_id = {claim["claim_id"]: claim for claim in claims}
    _require(
        isinstance(risks, list)
        and all(isinstance(key, str) and key in by_id for key in risks)
    )
    _require(len(risks) == len(set(risks)) and bool(risks) == bool(count))
    for row in diagnostics:
        _require(
            isinstance(row, dict)
            and set(row) == {"task_key", "claim_id", "source_span_id", "rule_code"}
        )
        rule = row["rule_code"]
        _require(
            row["claim_id"] in risks and isinstance(rule, str) and rule in recipe.rules
        )
        if rule in {"unmatched_claim_scope", "ambiguous_claim_scope"}:
            _require(row["task_key"] is None and row["source_span_id"] is None)
        else:
            _require(isinstance(row["task_key"], str) and row["task_key"] in requested)
            _require(
                isinstance(row["source_span_id"], str)
                and row["source_span_id"]
                in {span["span_id"] for span in bundle["evidence_spans"]}
            )
    if count or not report["requested_emission_complete"]:
        _require(
            draft["status"] == "needs_review"
            and bundle["quality_status"] == "needs_review"
        )
    _require(all(by_id[key]["needs_review"] is True for key in risks))
    return deepcopy(report)
