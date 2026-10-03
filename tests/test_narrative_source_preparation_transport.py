"""Transport boundary tests use real child processes with controlled wire output."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import NarrativeTransportError  # noqa: E402
from company_wiki_narrative_reader import find_narrative_reference, read_narrative_context  # noqa: E402

GOLDEN = ROOT / "tests/fixtures/cwp_narrative_transport_v1"


def _fake(tmp_path, stdout, stderr, exit_code=0):
    script = tmp_path / "provider.py"
    script.write_text(
        "import sys\nsys.stdin.buffer.read()\n"
        f"sys.stdout.buffer.write({stdout!r})\nsys.stderr.buffer.write({stderr!r})\n"
        f"raise SystemExit({exit_code})\n", encoding="utf-8",
    )
    return [sys.executable, "-B", str(script)]


def _request():
    return json.loads((GOLDEN / "read_request.json").read_bytes())


def _receipt():
    value = json.loads((GOLDEN / "read_receipt.json").read_bytes())
    return (json.dumps(value, separators=(",", ":")) + "\n").encode()


def test_real_process_adapter_accepts_single_bound_receipt(tmp_path):
    result = read_narrative_context(
        _request(), catalog_config=tmp_path / "catalog.yaml",
        reader_command=_fake(tmp_path, (GOLDEN / "bundle.json").read_bytes(), _receipt()),
    )
    assert result.to_dict()["read_receipt"]["replay_status"] == "verified"


@pytest.mark.parametrize("mutation", ["nonzero_body", "missing_receipt", "two_receipts", "metadata_only",
                                      "wrong_echo", "unavailable"])
def test_bad_provider_wire_or_exit_never_produces_usable_context(tmp_path, mutation):
    body = (GOLDEN / "bundle.json").read_bytes()
    receipt = json.loads(_receipt())
    raw_receipt, code = _receipt(), 0
    if mutation == "nonzero_body":
        code = 2
    elif mutation == "missing_receipt":
        raw_receipt = b""
    elif mutation == "two_receipts":
        raw_receipt += raw_receipt
    elif mutation == "metadata_only":
        receipt["status"] = "metadata_only"
        raw_receipt = (json.dumps(receipt) + "\n").encode()
    elif mutation == "wrong_echo":
        receipt["as_of_date"] = "2026-08-31"
        raw_receipt = (json.dumps(receipt) + "\n").encode()
    else:
        code, body = 2, b""
        raw_receipt = b'{"schema_version":"narrative-read-receipt/1","status":"unavailable","reason":"reader_unavailable"}\n'
    with pytest.raises(NarrativeTransportError):
        read_narrative_context(
            _request(), catalog_config=tmp_path / "catalog.yaml",
            reader_command=_fake(tmp_path, body, raw_receipt, code),
        )


def test_reference_accepts_only_metadata_receipt_and_full_source_binding(tmp_path):
    ref = _request()["narrative_ref"]
    request = {"schema_version": "narrative-reference-request/1", "source_ref": ref["source_ref"]}
    receipt = {"schema_version": "narrative-read-receipt/1", "status": "metadata_only", "narrative_ref": ref}
    def encode(value):
        return (json.dumps(value) + "\n").encode()
    command = _fake(tmp_path, encode(ref), encode(receipt))
    assert find_narrative_reference(request, catalog_config=tmp_path / "catalog.yaml",
                                    reader_command=command) == ref
    bad = deepcopy(receipt)
    bad["status"] = "ok"
    with pytest.raises(NarrativeTransportError):
        find_narrative_reference(request, catalog_config=tmp_path / "catalog.yaml",
                                  reader_command=_fake(tmp_path, encode(ref), encode(bad)))
