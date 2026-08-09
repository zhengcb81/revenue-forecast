"""WU-204 RED/audit tests: artifact DAG invalidation + selection (B-01..12)."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from artifact_dag import (  # noqa: E402
    ROLE_DEPENDENCIES,
    invalidate,
    select_artifacts,
    bundle_snapshot_match,
)


def _artifact(role: str, **overrides) -> dict:
    base = {
        "role": role,
        "artifact_hash": f"h-{role}",
        "input_document_hash": "doc-hash",
        "parent_artifact_hash": None,
        "producer_name": "producer",
        "producer_version": "1.0",
        "schema_version": "2.0",
        "prompt_hash": "p1",
        "model_hash": "m1",
        "config_hash": "c1",
        "created_at": "2026-01-01",
        "status": "completed",
    }
    base.update(overrides)
    return base


def _valid_bundle() -> list[dict]:
    normalized = _artifact("normalized")
    markdown = _artifact("markdown", parent_artifact_hash="h-normalized")
    summary = _artifact("summary", parent_artifact_hash="h-markdown")
    sections = _artifact("sections", parent_artifact_hash="h-normalized")
    analysis = _artifact("consumer_analysis", parent_artifact_hash="h-summary")
    return [normalized, markdown, summary, sections, analysis]


def test_b01_original_hash_change_invalidates_all():
    artifacts = _valid_bundle()
    affected = invalidate(artifacts, "original", change="document_hash")
    assert set(affected) == {"normalized", "markdown", "summary", "sections",
                             "consumer_analysis"}


def test_b02_summary_producer_change_recomputes_summary_and_downstream_only():
    artifacts = _valid_bundle()
    affected = invalidate(artifacts, "summary", change="producer_version")
    assert set(affected) == {"summary", "consumer_analysis"}


def test_b03_parser_change_invalidates_md_and_downstream():
    artifacts = _valid_bundle()
    affected = invalidate(artifacts, "normalized", change="producer_version")
    # normalized producer 变 → normalized 及其全部下游按 DAG 失效
    assert set(affected) == {"normalized", "markdown", "summary", "sections",
                             "consumer_analysis"}


def test_b04_consumer_analysis_change_recomputes_only_analysis():
    artifacts = _valid_bundle()
    affected = invalidate(artifacts, "consumer_analysis", change="config_hash")
    assert affected == ["consumer_analysis"]


def test_b05_input_hash_mismatch_not_reused():
    artifacts = _valid_bundle()
    artifacts[2]["input_document_hash"] = "tampered"
    selected, rejected = select_artifacts(artifacts, document_hash="doc-hash")
    assert "summary" in rejected
    assert "normalized" in selected and "markdown" in selected


def test_b06_retired_filing_rejects_all_artifacts():
    artifacts = _valid_bundle()
    selected, rejected = select_artifacts(artifacts, document_hash="doc-hash",
                                          filing_status="retired")
    assert selected == []
    assert len(rejected) == len(artifacts)


def test_b07_retired_artifact_not_reused_but_original_ok():
    artifacts = _valid_bundle()
    artifacts[3]["status"] = "retired"  # sections retired
    selected, rejected = select_artifacts(artifacts, document_hash="doc-hash")
    assert "sections" in rejected
    assert "normalized" in selected


def test_b08_unknown_schema_fails_closed():
    artifacts = _valid_bundle()
    artifacts[1]["schema_version"] = "99.0"
    selected, rejected = select_artifacts(artifacts, document_hash="doc-hash")
    assert "markdown" in rejected


def test_b09_snapshot_mismatch_stale_bundle():
    assert not bundle_snapshot_match(filing_snapshot="s1", artifact_snapshot="s2")
    assert bundle_snapshot_match(filing_snapshot="s1", artifact_snapshot="s1")


def test_b10_deterministic_selection_order():
    artifacts = _valid_bundle()
    s1, r1 = select_artifacts(artifacts, document_hash="doc-hash")
    s2, r2 = select_artifacts(artifacts, document_hash="doc-hash")
    assert s1 == s2 and r1 == r2


def test_b12_role_dependencies_constant():
    assert ROLE_DEPENDENCIES["consumer_analysis"] == ["summary"]
    assert "markdown" in ROLE_DEPENDENCIES["summary"]
