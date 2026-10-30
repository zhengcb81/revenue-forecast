"""Finite confidence revisions are a registry generation, not a new input."""
from copy import deepcopy
import json
from pathlib import Path
import stat
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]
import publication_registry as registry  # noqa: E402
from analysis.confidence import calculate_confidence  # noqa: E402
from contracts.evidence import canonical_sha256  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_registry(tmp_path, monkeypatch):
    path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(path))
    return path


def result(revision="source-evidence/2", result_sha="b" * 64):
    return {"input_sha256": "a" * 64, "result_sha256": result_sha,
            "engine_version": "4.3.0", "schema_version": "3.7",
            "confidence": {"calculation_version": revision}}


def test_actual_same_input_old_and_new_native_outputs_are_distinct_generations(monkeypatch):
    import revenue_core
    from revenue_report import validate_published_forecast
    from test_recognition_bridge import forecast_document
    data = forecast_document()
    with monkeypatch.context() as local:
        local.setattr(revenue_core, "calculate_confidence", lambda *args:
            calculate_confidence(*args, calculation_version="stable-fsum/1"))
        old = revenue_core.run_forecast(data)
    new = revenue_core.run_forecast(data)
    validate_published_forecast(old, data)
    validate_published_forecast(new, data)
    assert old["input_sha256"] == new["input_sha256"]
    assert old["forecast_version"] == new["forecast_version"]
    assert old["result_sha256"] != new["result_sha256"]
    assert registry.audit() == []
    history = registry.lookup(old["input_sha256"])
    assert {item["confidence_calculation_version"] for item in history} == {
        "stable-fsum/1", "source-evidence/2"}
    assert registry.audit() == []


def test_duplicate_new_revision_no_conflict_but_different_hash_same_revision_conflicts():
    registry.register_publication(result())
    registry.register_publication(result())
    assert registry.audit() == []
    registry.register_publication(result(result_sha="c" * 64))
    assert any("conflict" in problem and "source-evidence/2" in problem for problem in registry.audit())


def test_historical_missing_revision_stays_legacy_without_rewriting_old_line(isolated_registry):
    registry.register_publication(result("stable-fsum/1"))
    entry = registry.lookup("a" * 64)[0]
    entry.pop("confidence_calculation_version", None)
    entry.pop("line_sha256")
    entry["line_sha256"] = canonical_sha256(entry)
    isolated_registry.chmod(stat.S_IWRITE | stat.S_IREAD)
    isolated_registry.write_text(json.dumps(entry) + "\n", encoding="utf-8")
    old_bytes = isolated_registry.read_bytes()
    registry.register_publication(result())
    assert isolated_registry.read_bytes().startswith(old_bytes)
    assert "confidence_calculation_version" not in registry.lookup("a" * 64)[0]
    assert registry.audit() == []
    registry.register_publication(result("stable-fsum/1", "c" * 64))
    assert any("conflict" in problem and "stable-fsum/1" in problem for problem in registry.audit())


@pytest.mark.parametrize("revision", [None, "unknown/9", "", [], {}])
def test_registration_rejects_invalid_revision_before_appending(revision, isolated_registry):
    registry.register_publication(result())
    before = isolated_registry.read_bytes()
    with pytest.raises(registry.RegistryError, match="confidence calculation version"):
        registry.register_publication(result(revision))
    assert isolated_registry.read_bytes() == before


@pytest.mark.parametrize("revision", [None, "unknown/9", "", [], {}])
def test_audit_rejects_hash_valid_bad_revision_not_a_separate_generation(revision):
    # Build a hash-valid malformed row, as historical JSONL is untrusted input.
    registry._append({"input_sha256": "a" * 64, "result_sha256": "b" * 64,
                      "confidence_calculation_version": revision})
    assert any("confidence calculation version" in problem for problem in registry.audit())
    with pytest.raises(registry.RegistryError, match="confidence calculation version"):
        registry.lookup("a" * 64)


@pytest.mark.parametrize("revision", ["stable-fsum/1", "source-evidence/2"])
def test_snapshot_uses_nested_actual_forecast_revision_not_outer_label(revision):
    nested = result(revision)
    snapshot = {"input_sha256": nested["input_sha256"],
        "forecast_result_sha256": nested["result_sha256"], "forecast_result": nested,
        "engine_version": "4.3.0", "forecast_schema_version": "3.7",
        "confidence_calculation_version": "pretend/99", "snapshot_id": "neutral"}
    frozen = deepcopy(snapshot)
    registry.register_snapshot(snapshot)
    assert registry.lookup("a" * 64)[0]["confidence_calculation_version"] == revision
    assert snapshot == frozen
    assert registry.audit() == []


def test_snapshot_generations_can_coexist_and_same_generation_still_conflicts():
    for revision, sha in (("stable-fsum/1", "b" * 64), ("source-evidence/2", "c" * 64)):
        nested = result(revision, sha)
        registry.register_snapshot({"input_sha256": nested["input_sha256"],
            "forecast_result_sha256": sha, "forecast_result": nested})
    assert registry.audit() == []
    registry.register_snapshot({"input_sha256": "a" * 64,
        "forecast_result_sha256": "d" * 64, "forecast_result": result()})
    assert any("conflict" in problem for problem in registry.audit())


def test_reordering_otherwise_valid_rows_still_breaks_chain(isolated_registry):
    registry.register_publication(result("stable-fsum/1"))
    registry.register_publication(result())
    lines = isolated_registry.read_text("utf-8").splitlines()
    isolated_registry.chmod(stat.S_IWRITE | stat.S_IREAD)
    isolated_registry.write_text("\n".join(reversed(lines)) + "\n", encoding="utf-8")
    assert any("chain break" in problem for problem in registry.audit())


def test_missing_confidence_legacy_fixture_is_recorded_as_stable_revision():
    value = result()
    value.pop("confidence")
    registry.register_publication(value)
    assert registry.lookup("a" * 64)[0]["confidence_calculation_version"] == "stable-fsum/1"


@pytest.mark.parametrize("revision", [None, "unknown/9", [], {}])
def test_snapshot_rejects_unknown_actual_nested_revision(revision, isolated_registry):
    with pytest.raises(registry.RegistryError, match="confidence calculation version"):
        registry.register_snapshot({"input_sha256": "a" * 64,
            "forecast_result_sha256": "b" * 64, "forecast_result": result(revision)})
    assert not isolated_registry.exists()


@pytest.mark.parametrize("confidence", [None, [], "source-evidence/2"])
def test_malformed_confidence_container_cannot_claim_legacy(confidence, isolated_registry):
    malformed = result()
    malformed["confidence"] = confidence
    with pytest.raises(registry.RegistryError, match="confidence calculation version"):
        registry.register_publication(malformed)
    assert not isolated_registry.exists()
