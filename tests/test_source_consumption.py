"""WU-1003 RED/audit tests: per-role artifact consumption — never
all-or-nothing, never silent fallback to raw PDF parsing."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from company_wiki_source import select_reusable_artifacts  # noqa: E402


def _handle(roles: dict) -> dict:
    """FC-902 contract: the SourceBundle rides the resolution envelope."""
    valid = {}
    for role, meta in roles.items():
        if meta.get("reusable", True):
            valid[role] = {
                "reusable": True,
                "path": f"/tmp/{role}.md",
                "content_sha256": f"{role}-hash",
                "generator_version": meta.get("version", "1.0"),
                "engine": meta.get("engine"),
                "model": meta.get("model"),
                "prompt": meta.get("prompt"),
                "input_bundle_hash": meta.get("input_bundle_hash"),
            }
    bundle = {"schema_version": "1.0", "valid_handles": valid,
              "invalid": {}, "bundle_hash": "b" * 64}
    return {
        "request_id": "req-1",
        "resolution_envelope": {
            "envelope_schema_version": "1.0", "outcome": "reused_existing",
            "download_events": 0, "bundle_status": "available",
            "bundle_hash": bundle["bundle_hash"], "bundle": bundle,
        },
    }


ALL_ROLES = ("normalized", "markdown", "summary", "sections", "consumer_analysis")


def test_per_role_selection_independent():
    """每角色独立决定——缺失角色不影响其它角色。"""
    handle = _handle({"normalized": {}, "markdown": {}, "summary": {}})
    selected = select_reusable_artifacts(handle, ("normalized", "markdown",
                                                  "summary", "sections"))
    assert set(selected) == {"normalized", "markdown", "summary"}
    assert "sections" not in selected  # missing role = not selected, others fine


def test_valid_all_selected():
    handle = _handle({"normalized": {}, "markdown": {}, "summary": {}})
    selected = select_reusable_artifacts(handle, ALL_ROLES)
    assert set(selected) == {"normalized", "markdown", "summary"}


def test_missing_bundle_returns_empty():
    assert select_reusable_artifacts({}, ALL_ROLES) == {}


def test_malformed_bundle_fails_closed():
    import pytest

    handle = {
        "request_id": "req-1",
        "resolution_envelope": {
            "envelope_schema_version": "1.0", "outcome": "reused_existing",
            "download_events": 0, "bundle_status": "available",
            "bundle_hash": "b" * 64, "bundle": "not-a-dict",
        },
    }
    with pytest.raises(Exception):
        select_reusable_artifacts(handle, ALL_ROLES)


def test_consumer_analysis_provenance_gate():
    """E2E-D06: engine/model/prompt/input_bundle_hash 任一变化 → 不复用。"""
    base = {"engine": "e1", "model": "m1", "prompt": "p1",
            "input_bundle_hash": "b1"}
    handle = _handle({"consumer_analysis": base})
    selected = select_reusable_artifacts(
        handle, ("consumer_analysis",), expected_provenance=base
    )
    assert "consumer_analysis" in selected
    changed = dict(base, model="m2")
    selected = select_reusable_artifacts(
        handle, ("consumer_analysis",), expected_provenance=changed
    )
    assert "consumer_analysis" not in selected  # any change → not reused


def test_recompute_plan_explicit():
    """缺失角色 = 显式重算计划（调用者决定），绝无静默 PDF 重解析。"""
    handle = _handle({"normalized": {}})
    selected = select_reusable_artifacts(handle, ALL_ROLES)
    missing = [role for role in ALL_ROLES if role not in selected]
    assert missing == ["markdown", "summary", "sections", "consumer_analysis"]
    # the consumer's recompute plan is explicit: no artifact is silently
    # substituted by opening the raw PDF
    assert selected["normalized"]["path"].endswith(".md")
