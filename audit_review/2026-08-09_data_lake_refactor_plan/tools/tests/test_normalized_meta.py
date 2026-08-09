"""WU-202 RED/audit tests: META-01..12 for the NormalizedFilingMetadata v2
contract (source-independent filing facts)."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from normalized_meta import (  # noqa: E402
    validate_normalized_filing,
    canonical_hash,
    REQUIRED_FIELDS,
)


def _valid() -> dict:
    fields = {
        "schema_version": "2.0",
        "canonical_entity_id": "ent-600519",
        "display_name": "贵州茅台",
        "market": "CN",
        "security_id": "600519",
        "document_kind": "annual",
        "regulatory_form": "10-K",
        "fiscal_year": "2025",
        "period_end": "2025-12-31",
        "period_kind": "fiscal",
        "provider": "example-filing",
        "provider_document_id": "acc-2025-01",
        "source_url": "https://www.example-filing.com/600519/2025",
        "published_at": "2026-04-15",
        "filed_at": "2026-04-15",
        "accepted_at": "2026-04-16",
        "language": "zh",
        "is_amended": False,
        "revision_id": "1",
        "supersedes_document_id": None,
        "content_sha256": "c" * 64,
        "adapter_id": "sidecar_filing_v1",
        "adapter_version": "1.0.0",
        "normalization_status": "capture_ready",
        "evidence": {"fiscal_year": {"origin": "sidecar", "source_pointer": "fiscal_year"}},
    }
    fields["metadata_sha256"] = canonical_hash(fields)
    return fields


def test_meta01_missing_identity_rejected():
    fields = _valid()
    del fields["canonical_entity_id"]
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("identity" in r for r in reasons)


def test_meta02_name_only_not_strong_identity():
    fields = _valid()
    del fields["security_id"]
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("identity" in r for r in reasons)


def _with(fields: dict, **changes) -> dict:
    """Apply changes and re-bind metadata_sha256 to the new semantic fields."""
    updated = dict(fields)
    updated.update(changes)
    updated["metadata_sha256"] = canonical_hash(updated)
    return updated


def test_meta03_multiple_revisions_deterministic():
    fields = _with(_valid(), revision_id="2", supersedes_document_id="doc-1")
    ok, _ = validate_normalized_filing(fields)
    assert ok


def test_meta04_invalid_date_rejected():
    fields = _valid()
    fields["period_end"] = "2025-13-45"
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("period_end" in r for r in reasons)


def test_meta05_unknown_kind_rejected():
    fields = _valid()
    fields["document_kind"] = "mystery"
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("document_kind" in r for r in reasons)


def test_meta06_conflicting_fields_rejected():
    fields = _valid()
    fields["evidence"] = {
        "fiscal_year": {"origin": "sidecar", "asserted_value": "2024"},
    }
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("conflict" in r for r in reasons)


def test_meta07_unknown_version_fails_closed():
    fields = _valid()
    fields["schema_version"] = "99.0"
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("schema_version" in r for r in reasons)


def test_meta08_broken_evidence_pointer_rejected():
    fields = _valid()
    fields["evidence"] = {"period_end": {"origin": "sidecar", "source_pointer": "missing.field"}}
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("evidence" in r for r in reasons)


def test_meta09_content_hash_tampered_rejected():
    # content_sha256 绑定检测：篡改字段值使 metadata_sha256 不再匹配
    fields = _valid()
    fields["content_sha256"] = "0" * 64  # 保持 64-hex 格式，但 semantic hash 变化
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("metadata_sha256" in r for r in reasons)


def test_meta10_vague_name_rejected():
    fields = _valid()
    fields["canonical_entity_id"] = ""
    fields["security_id"] = ""
    fields["display_name"] = "公司"
    ok, reasons = validate_normalized_filing(fields)
    assert not ok


def test_meta11_old_reader_new_data_graceful():
    fields = _valid()
    # an old reader sees schema 2.0 data: must fail closed unless it declares
    # a supported window — the contract requires unknown-version handling
    fields["schema_version"] = "1.9"
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("schema_version" in r for r in reasons)


def test_meta12_new_reader_old_data_graceful():
    fields = _valid()
    fields["schema_version"] = "1.0"
    # a 1.0 doc lacks v2-only fields; the v2 validator must not crash and
    # must report the missing v2 requirements rather than accept silently
    for key in ("adapter_id", "adapter_version", "normalization_status",
                "metadata_sha256"):
        fields.pop(key, None)
    ok, reasons = validate_normalized_filing(fields)
    assert not ok and any("adapter" in r for r in reasons)


def test_required_fields_constant():
    assert "canonical_entity_id" in REQUIRED_FIELDS
    assert "document_kind" in REQUIRED_FIELDS
    assert "fiscal_year" in REQUIRED_FIELDS
    assert "content_sha256" in REQUIRED_FIELDS
    # non-semantic fields must NOT be in the semantic identity
    for excluded in ("root_id", "canonical_path", "scanned_at"):
        assert excluded not in REQUIRED_FIELDS


def test_canonical_hash_excludes_root_and_scan_time():
    a = _valid()
    b = dict(a)
    b["root_id"] = "company_raw"
    b["canonical_path"] = "/abs/path/x.pdf"
    b["scanned_at"] = "2026-08-09T00:00:00Z"
    assert canonical_hash(a) == canonical_hash(b)
