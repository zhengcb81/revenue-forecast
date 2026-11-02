"""R7 source integrity survives representation/diagnostic/index changes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]
from company_wiki_narrative_contracts import validate_narrative_response  # noqa: E402
from contracts.evidence import canonical_sha256  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from test_assessed_narrative_consumer import assessed_wire  # noqa: E402
from test_company_wiki_narrative_reader import _resign  # noqa: E402
from test_company_wiki_source_v2 import BODY, _inputs, _build  # noqa: E402
from test_shared_reading_narrative_contract import actual  # noqa: E402
from test_summary_long_excerpt import long_summary_input  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch, tmp_path):
    monkeypatch.delenv("REVENUE_ATTESTATION_PROVIDER", raising=False)
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "index"))


@pytest.mark.parametrize("variant", ["bytes", "strings", "arrays", "depth"])
def test_valid_reading_data_has_no_independent_representation_quota(variant):
    request, body, raw_receipt = actual()
    bundle, receipt = json.loads(body), json.loads(raw_receipt)
    if variant == "bytes":
        payload = ["policy observation " * 100] * 200
    elif variant == "strings":
        payload = "policy observation " * 2000
    elif variant == "arrays":
        payload = ["diagnostic"] * 5000
    else:
        payload = "source-owned diagnostic"
        for _ in range(22):
            payload = [payload]
    bundle["reading_context"]["layout_coverage"]["additional_observations"] = payload
    body, raw_receipt = _resign(request, bundle, receipt)
    value = validate_narrative_response(request, body, raw_receipt).to_dict()
    assert value["reading_context"]["layout_coverage"]["additional_observations"] == payload
    assert value["evidence_spans"] == bundle["evidence_spans"]


def test_assessment_new_algorithm_and_diagnostic_volume_do_not_gate_source():
    request, bundle, receipt = assessed_wire()
    model = bundle["summary"]["model"]
    model["prompt_version"] = bundle["versions"]["prompt"] = "future-source-reader/19"
    report = bundle["summary_assessment"]
    report["validator"]["version"] = "source-diagnostic/19"
    report["validator"]["dependencies"]["new_observer"] = "a" * 64
    report["validator"]["implementation_sha256"] = canonical_sha256(report["validator"]["dependencies"])
    cid = bundle["summary"]["draft"]["claims"][0]["claim_id"]
    sid = bundle["evidence_spans"][0]["span_id"]
    report["diagnostics"] = [{"task_key": "t1", "claim_id": cid,
                              "source_span_id": sid, "rule_code": "new_observation"}] * 800
    report.update(diagnostic_count=800, diagnostics_limited=False,
                  diagnostic_claim_ids=[cid], known_constraint_status="diagnostics_found")
    bundle["summary"]["draft"]["claims"][0]["needs_review"] = True
    bundle["summary"]["draft"]["status"] = "needs_review"
    bundle["quality_status"] = receipt["quality_status"] = "needs_review"
    report["claims_sha256"] = canonical_sha256(bundle["summary"]["draft"]["claims"])
    body, raw_receipt = _resign(request, bundle, receipt)
    value = validate_narrative_response(request, body, raw_receipt).to_dict()
    assert value["summary_assessment"]["semantic_status"] == "not_evaluated"
    assert len(value["summary_assessment"]["diagnostics"]) == 800


@pytest.mark.parametrize("review", [{"status": "storage_error"}, "unavailable", {"status": "reviewed", "source_sha256": "f" * 64}])
def test_optional_review_damage_cannot_reject_verified_original(review):
    ref, receipt, manifest = _inputs()
    receipt["review"] = review
    record = _build(ref, receipt, manifest)
    assert record["capture"]["snapshot_sha256"] == ref["content_sha256"]
    assert record["capture"]["prompt_injection_status"] == "not_reviewed"
    assert record["company_wiki_trace"]["review_observation"]["status"] == "unavailable"


def test_complete_large_source_anchor_and_proof_are_not_length_permissions():
    from revenue_core import validate_document
    updated, claim, text = long_summary_input(50000, "核心业务提供研发支持服务。")
    validate_document(updated)
    assert claim["excerpt"] == text
    assert claim["narrative_summary_use"]["evidence_spans"][0]["raw_text"] == text


@pytest.mark.parametrize("fault", ["unavailable", "corrupt"])
def test_formal_result_does_not_depend_on_global_index_health(monkeypatch, tmp_path, fault):
    index = tmp_path / "index"
    if fault == "unavailable":
        index.write_text("not a directory", encoding="utf-8")
        monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(index / "publications.jsonl"))
    else:
        index.mkdir()
        (index / "publications.jsonl").write_text("broken old index\n", encoding="utf-8")
    result = run_forecast(forecast_document())
    assert result["publication_receipt"]["formal_output_mode"] == "formal"
    from revenue_report import validate_forecast_output
    validate_forecast_output(result)


def test_preparation_hashes_same_received_immutable_source_only_once(monkeypatch, tmp_path):
    import company_wiki_source_reader_v2 as reader
    import source_preparation as preparation
    ref, receipt, manifest = _inputs()
    monkeypatch.setattr(reader, "_run_reader", lambda *_a, **_k: subprocess.CompletedProcess(
        [], 0, BODY, json.dumps({**receipt, "manifest": manifest}).encode() + b"\n"))
    real_sha = hashlib.sha256
    calls = []
    def counted(value=b"", *args, **kwargs):
        if value is BODY:
            calls.append(value)
        return real_sha(value, *args, **kwargs)
    monkeypatch.setattr(hashlib, "sha256", counted)
    candidate = {"status": "source_candidate", "source_ref": ref,
        "byte_verification": "pending_verified_open", "document_kind": "annual_report",
        "fiscal_year": 2025, "fiscal_period": None, "resolution_outcome": "reused_existing",
        "download_events": 0}
    record = preparation._prepare_source_ref_v2(
        {"document_kind": "annual_report", "fiscal_year": 2025, "as_of_date": "2026-09-27"},
        candidate, tmp_path / "not-read.json", timeout_seconds=30)
    assert record["capture"]["snapshot_sha256"] == ref["content_sha256"]
    assert len(calls) == 1


def test_verified_context_is_immutable_and_raw_mutations_need_wire_validation():
    from company_wiki_narrative_contracts import NarrativeContext, NarrativeTransportError
    request, body, receipt = actual()
    context = validate_narrative_response(request, body, receipt)
    changed = context.to_dict()
    changed["summary"]["draft"]["claims"][0]["text"] += " unsupported claim"
    assert changed != context.to_dict()
    with pytest.raises(ValueError, match="validate_narrative_response"):
        NarrativeContext(changed)
    corrupted = bytearray(body)
    corrupted[-2] ^= 1
    with pytest.raises(NarrativeTransportError, match="artifact_bytes_mismatch"):
        validate_narrative_response(request, bytes(corrupted), receipt)


def test_explicit_transport_budget_remains_real_without_default_representation_quota():
    from company_wiki_narrative_contracts import NarrativeTransportError
    from company_wiki_narrative_process import run_bounded
    command = [sys.executable, "-c", "import sys;sys.stdin.buffer.read();sys.stdout.buffer.write(b'x'*20000)"]
    assert len(run_bounded(command, b"", stdout_limit=None, stderr_limit=None).stdout) == 20000
    with pytest.raises(NarrativeTransportError, match="reader_output_limit"):
        run_bounded(command, b"", stdout_limit=100, stderr_limit=100)


def test_index_can_be_rebuilt_from_validated_artifact_without_old_history(tmp_path):
    from publication_registry import rebuild_publications
    from revenue_report import validate_forecast_output
    result = run_forecast(forecast_document())
    artifact = tmp_path / "version-1.json"
    artifact.write_text(json.dumps(result), encoding="utf-8")
    target = tmp_path / "rebuilt" / "publications.jsonl"
    assert rebuild_publications([artifact], output_path=target) == {"indexed": 1}
    row = json.loads(target.read_text(encoding="utf-8"))
    assert row["result_sha256"] == result["result_sha256"]
    validate_forecast_output(result)
    altered = json.loads(artifact.read_text(encoding="utf-8"))
    altered["currency"] = "imaginary currency"
    artifact.write_text(json.dumps(altered), encoding="utf-8")
    previous = target.read_bytes()
    with pytest.raises(ValueError):
        rebuild_publications([artifact], output_path=target)
    assert target.read_bytes() == previous


def test_legal_short_source_anchor_is_not_rejected_by_character_count():
    from revenue_core import validate_document
    from contracts.evidence import text_sha256
    from fix_hashes import apply_hash_fixes
    document = forecast_document()
    claim = document["evidence_claims"][0]
    claim["excerpt"] = "收入12亿。"
    claim["excerpt_sha256"] = text_sha256(claim["excerpt"])
    apply_hash_fixes(document)
    validate_document(document)

@pytest.mark.parametrize("status", [[], {}])
@pytest.mark.parametrize("origin", ["review", "supplied"])
def test_optional_review_non_scalar_status_does_not_gate_source(status, origin):
    ref, receipt, manifest = _inputs()
    kwargs = {}
    if origin == "review":
        receipt["review"] = {"status": status, "source_sha256": ref["content_sha256"],
            "evidence_sha256": None, "policy_hash": None, "reviewed_at": None}
    else:
        kwargs["prompt_injection_status"] = status
    record = _build(ref, receipt, manifest, **kwargs)
    assert record["capture"]["snapshot_sha256"] == ref["content_sha256"]
    assert record["capture"]["prompt_injection_status"] == "not_reviewed"
    assert record["company_wiki_trace"]["review_observation"]["status"] == (
        "unavailable" if origin == "review" else "absent")


def test_optional_selection_trace_wrong_type_does_not_gate_verified_wire():
    request, body, raw_receipt = actual()
    bundle, receipt = json.loads(body), json.loads(raw_receipt)
    from test_shared_reading_narrative_contract import _upgrade_to_v3
    _upgrade_to_v3(bundle["reading_context"])
    trace = bundle["reading_context"]["selection_trace"]
    trace["admission"].update(count=1, admitted_count=1, samples=[{
        "unit_id": [], "package_ref": "unavailable", "status": "admitted", "reason": None,
        "fact_purpose": "source_material", "fact_reasons": [], "fact_reason_count": 0,
        "fact_reasons_limited": False, "required_unit_ids": [], "required_unit_count": 0,
        "required_unit_ids_limited": False, "priority": 1, "selected_span_id": None,
    }])
    body, raw_receipt = _resign(request, bundle, receipt)
    value = validate_narrative_response(request, body, raw_receipt).to_dict()
    assert value["source_ref"] == bundle["source_ref"]
    assert value["evidence_spans"] == bundle["evidence_spans"]
    assert value["reading_context"]["selection_trace"] == trace
    assert {"status": "unavailable", "reason": "invalid_selection_trace"} in value["reading_diagnostic_observations"]


def test_complete_research_reason_is_not_a_summary_adoption_length_permission():
    from revenue_core import validate_document
    from test_narrative_summary_usage import example, choose, consume
    request, context, document, binding, summary = example("raw")
    reason = ("The original source supports the cited parameter, subject to its stated limitations. " * 100).strip()
    updated, _ = consume(request, context, document, [choose(binding, summary, research_reason=reason)])
    claim = next(row for row in updated["evidence_claims"] if row["claim_id"] == binding["claim_id"])
    assert claim["narrative_summary_use"]["entry"]["research_reason"] == reason.strip()
    validate_document(updated)


@pytest.mark.parametrize("field", ["selection_trace", "selection_diagnostics"])
def test_optional_reading_observation_absence_is_not_source_permission(field):
    from test_shared_reading_narrative_contract import _upgrade_to_v3
    request, body, raw_receipt = actual()
    bundle, receipt = json.loads(body), json.loads(raw_receipt)
    _upgrade_to_v3(bundle["reading_context"])
    bundle["reading_context"].pop(field)
    body, raw_receipt = _resign(request, bundle, receipt)
    value = validate_narrative_response(request, body, raw_receipt).to_dict()
    assert value["evidence_spans"] == bundle["evidence_spans"]
    assert value["summary"] == bundle["summary"]
    assert field not in value["reading_context"]
    assert {"status": "absent", "reason": field + "_absent"} in value["reading_diagnostic_observations"]
