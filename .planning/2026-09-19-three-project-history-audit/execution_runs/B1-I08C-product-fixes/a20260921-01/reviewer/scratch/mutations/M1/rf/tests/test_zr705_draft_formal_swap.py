"""ZR-705 acceptance tests: draft/formal separation + swap/rehash attack
gate (REV-06~08).

  C1  draft can render without publishing: render_markdown works on a
      draft result; draft results never register in the publication
      registry (entry count unchanged).
  C2  formal strong gate + signature: formal receipt carries non-empty
      gate_ids + attestation_status in {host_signed, unattested};
      build_publication_receipt without a VerificationContext raises
      TypeError (no self-issued formal receipts).
  C3  swap attacks fail (REV-08a): draft receipt flipped to
      formal_output_mode="formal" is rejected (gate_ids mismatch); a
      downgraded formal receipt (formal_output_mode="draft" with non-empty
      gate_ids, receipt_sha256 recomputed) is rejected by the ZR-705
      mode/state consistency gate.
  C4  rehash attack fails (REV-08b): mutating a result value makes
      validated_payload_sha256 mismatch -> validate_publication_receipt
      rejects; recomputing receipt_sha256 does not repair it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.evidence import canonical_sha256  # noqa: E402
from revenue_forecast import prepare_forecast  # noqa: E402
from revenue_publication import (  # noqa: E402
    build_publication_receipt,
    validate_publication_receipt,
)
from revenue_report import render_markdown  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


# ---------------------------------------------------------------------------
# C1 — draft renders, never publishes
# ---------------------------------------------------------------------------


def test_c1_draft_renders_without_publishing(tmp_path, monkeypatch):
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    draft = prepare_forecast(forecast_document(), mode="draft")
    # render works on a draft result
    markdown = render_markdown(draft)
    assert "# " in markdown
    # draft does not publish: no registry file created
    assert not reg_path.exists()


def test_c1_draft_receipt_marks_draft_mode():
    draft = prepare_forecast(forecast_document(), mode="draft")
    receipt = draft["publication_receipt"]
    assert receipt["formal_output_mode"] == "draft"
    assert receipt["gate_ids"] == []


# ---------------------------------------------------------------------------
# C2 — formal strong gate + signature
# ---------------------------------------------------------------------------


def test_c2_formal_receipt_has_gates_and_attestation(tmp_path, monkeypatch):
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    formal = prepare_forecast(forecast_document())
    receipt = formal["publication_receipt"]
    assert receipt["formal_output_mode"] == "formal"
    assert receipt["gate_ids"]  # non-empty strong gates
    assert receipt["attestation_status"] in {"host_signed", "unattested"}
    validate_publication_receipt(formal)  # valid formal passes


def test_c2_formal_receipt_cannot_be_self_issued(tmp_path, monkeypatch):
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    formal = prepare_forecast(forecast_document())
    with pytest.raises(TypeError):
        build_publication_receipt(formal)  # no VerificationContext


# ---------------------------------------------------------------------------
# C3 — swap attacks fail (REV-08a)
# ---------------------------------------------------------------------------


def test_c3_draft_flipped_to_formal_rejected(tmp_path, monkeypatch):
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    draft = prepare_forecast(forecast_document(), mode="draft")
    draft["publication_receipt"]["formal_output_mode"] = "formal"
    with pytest.raises(Exception) as excinfo:
        validate_publication_receipt(draft)
    assert "gate_ids mismatch" in str(excinfo.value)


def test_c3_formal_downgraded_to_draft_rejected(tmp_path, monkeypatch):
    """REV-08a fix: a downgraded formal receipt (formal_output_mode
    flipped to 'draft', non-empty gate_ids, receipt_sha256 recomputed)
    must be rejected by the mode/state consistency gate."""
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    formal = prepare_forecast(forecast_document())
    receipt = dict(formal["publication_receipt"])
    receipt["formal_output_mode"] = "draft"
    receipt["receipt_sha256"] = canonical_sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )
    downgraded = dict(formal)
    downgraded["publication_receipt"] = receipt
    with pytest.raises(Exception) as excinfo:
        validate_publication_receipt(downgraded)
    assert "draft mode must have empty gate_ids" in str(excinfo.value)


# ---------------------------------------------------------------------------
# C4 — rehash attack fails (REV-08b)
# ---------------------------------------------------------------------------


def test_c4_mutated_result_payload_rejected(tmp_path, monkeypatch):
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    formal = prepare_forecast(forecast_document())
    # mutate a real value deep in the payload (base terminal_revenue + 1)
    mutated = dict(formal)
    mutated["consolidated_forecast"] = dict(mutated["consolidated_forecast"])
    base = dict(mutated["consolidated_forecast"]["base"])
    base["terminal_revenue"] = base["terminal_revenue"] + 1.0
    mutated["consolidated_forecast"]["base"] = base
    with pytest.raises(Exception) as excinfo:
        validate_publication_receipt(mutated)
    assert "validated_payload_sha256 mismatch" in str(excinfo.value)


def test_c4_rehash_does_not_repair(tmp_path, monkeypatch):
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    formal = prepare_forecast(forecast_document())
    mutated = dict(formal)
    mutated["consolidated_forecast"] = dict(mutated["consolidated_forecast"])
    base = dict(mutated["consolidated_forecast"]["base"])
    base["terminal_revenue"] = base["terminal_revenue"] + 1.0
    mutated["consolidated_forecast"]["base"] = base
    # recompute receipt_sha256 — payload mismatch must still reject
    receipt = dict(mutated["publication_receipt"])
    receipt["receipt_sha256"] = canonical_sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )
    mutated["publication_receipt"] = receipt
    with pytest.raises(Exception) as excinfo:
        validate_publication_receipt(mutated)
    assert "validated_payload_sha256 mismatch" in str(excinfo.value)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
