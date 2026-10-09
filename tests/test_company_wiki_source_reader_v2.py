"""RF's opt-in reader consumes CWP's verified-open producer golden.

Success receipt: CWP 822a43a; corrected bad-SHA refusal: CWP 7760b09.
The FF envelope is not frozen, so these tests do not switch RF's default route.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
FIXTURES = ROOT / "tests" / "fixtures"
BODY = "正文🙂 Revenue increased. EXPORT-V2-RAW-BYTES-SENTINEL End".encode("utf-8")
RECEIPT_SHA256 = "b27dccb3d8f4adf101d8f66b8feb1dcc98b987ec7993fbcc9c995f865f3d5869"
BAD_SHA_RECEIPT_SHA256 = "daed1b192dab90daf50bc2c9a3dc92695009944f51457177374cc77e0d53a0b5"


def _reader():
    try:
        return importlib.import_module("company_wiki_source_reader_v2")
    except ModuleNotFoundError:
        pytest.fail("RF verified-open 2.1 reader has not been integrated")


def _ref() -> dict:
    return json.loads((FIXTURES / "cwp_source_ref_v2.json").read_text(encoding="utf-8"))


def _receipt() -> dict:
    path = FIXTURES / "cwp_verified_open_receipt_normalized.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == RECEIPT_SHA256
    receipt = json.loads(path.read_text(encoding="utf-8"))
    receipt["policy_sha256"] = "a" * 64
    receipt["source_read_policy_sha256"] = "b" * 64
    receipt["read_at"] = "2026-02-21T12:00:00+00:00"
    return receipt


def _open(tmp_path: Path, **kwargs):
    return _reader().open_source_version_v2(
        source_ref=_ref(),
        catalog_config=tmp_path / "source_catalog.yaml",
        as_of_date="2026-07-18",
        expected_fiscal_year=2025,
        **kwargs,
    )


def test_unreviewed_receipt_with_verified_raw_bytes_is_consumable(monkeypatch, tmp_path):
    assert len(BODY) == 62
    assert hashlib.sha256(BODY).hexdigest() == _ref()["content_sha256"]
    receipt = _receipt()
    assert receipt["review"] is None

    def fake_run(command, **kwargs):
        assert "company_wiki.source_catalog.source_reader_cli" in command
        assert "--source-root" not in command
        assert command[command.index("--purpose") + 1] == "filing_reuse"
        assert command[command.index("--document-id") + 1] == _ref()["document_id"]
        assert command[command.index("--source-id") + 1] == _ref()["source_id"]
        assert command[command.index("--content-sha256") + 1] == _ref()["content_sha256"]
        assert command[command.index("--config") + 1] == str(tmp_path / "source_catalog.yaml")
        assert kwargs["shell"] is False
        return subprocess.CompletedProcess(
            command, 0, BODY, (json.dumps(receipt) + "\n").encode("utf-8"),
        )

    monkeypatch.setattr("subprocess.run", fake_run)
    body, read_receipt, manifest = _open(tmp_path)
    assert body == BODY
    assert read_receipt["review"] is None
    assert manifest["fiscal_year"] == 2025
    assert manifest["period_end"] == "2025-12-31"
    assert "canonical_path" not in str((read_receipt, manifest))


def test_same_size_tampered_bytes_are_rejected(monkeypatch, tmp_path):
    receipt = _receipt()

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command, 0, BODY[:-1] + b"X", (json.dumps(receipt) + "\n").encode(),
        )

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(_reader().SourceVersionTransportError, match="SHA-256") as caught:
        _open(tmp_path)
    assert caught.value.source_failure_reason == "source_bytes_mismatch"


@pytest.mark.parametrize(
    ("as_of_date", "expected_fiscal_year"),
    (("2026-02-19", 2025), ("2026-07-18", 2024)),
)
def test_verified_bytes_still_need_as_of_and_period(
    monkeypatch, tmp_path, as_of_date, expected_fiscal_year,
):
    receipt = _receipt()

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command, 0, BODY, (json.dumps(receipt) + "\n").encode(),
        )

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(_reader().SourceVersionTransportError) as caught:
        _reader().open_source_version_v2(
            source_ref=_ref(), catalog_config=tmp_path / "source_catalog.yaml",
            as_of_date=as_of_date, expected_fiscal_year=expected_fiscal_year,
        )
    assert caught.value.source_failure_reason == ("fiscal_year_mismatch" if expected_fiscal_year != 2025 else "source_publication_after_asof")


def test_wrong_version_refusal_never_falls_back_to_a_local_path(monkeypatch, tmp_path):
    path = FIXTURES / "cwp_verified_open_bad_sha.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == BAD_SHA_RECEIPT_SHA256
    calls = 0

    def fake_run(command, **_kwargs):
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(command, 2, b"", path.read_bytes())

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(_reader().SourceVersionTransportError, match="expected_version_mismatch"):
        _open(tmp_path)
    assert calls == 1


@pytest.mark.parametrize(
    ("field", "value"),
    (("source_id", "urn:wrong-source"), ("content_sha256", "0" * 64)),
)
def test_receipt_identity_mismatch_is_rejected(monkeypatch, tmp_path, field, value):
    receipt = _receipt()
    receipt[field] = value

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command, 0, BODY, (json.dumps(receipt) + "\n").encode(),
        )

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(_reader().SourceVersionTransportError, match="receipt"):
        _open(tmp_path)


def test_manifest_identity_mismatch_is_rejected(monkeypatch, tmp_path):
    receipt = _receipt()
    receipt["manifest"]["source_id"] = "urn:wrong-source"

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(
            command, 0, BODY, (json.dumps(receipt) + "\n").encode(),
        )

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(_reader().SourceVersionTransportError, match="manifest source_id"):
        _open(tmp_path)


def test_duplicate_receipt_field_is_rejected(monkeypatch, tmp_path):
    receipt = _receipt()
    wire = json.dumps(receipt)
    wire = wire.replace('"schema_version": "2.1",', '"schema_version": "2.1", "status": "ok",')

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, BODY, (wire + "\n").encode())

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(_reader().SourceVersionTransportError, match="duplicate JSON key"):
        _open(tmp_path)


def test_refusal_with_partial_bytes_is_rejected(monkeypatch, tmp_path):
    refusal = (FIXTURES / "cwp_verified_open_bad_sha.json").read_bytes()

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(command, 2, BODY[:4], refusal)

    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(_reader().SourceVersionTransportError, match="partial bytes"):
        _open(tmp_path)


def test_null_original_retrieval_is_preserved(monkeypatch, tmp_path):
    receipt = _receipt()
    receipt["manifest"]["retrieved_at"] = None
    monkeypatch.setattr("subprocess.run", lambda command, **kw:
                        subprocess.CompletedProcess(command, 0, BODY,
                            (json.dumps(receipt) + "\n").encode()))
    body, read_receipt, manifest = _open(tmp_path)
    assert body == BODY
    assert manifest["retrieved_at"] is None
    assert read_receipt["read_at"] == receipt["read_at"]
