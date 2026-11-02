"""D4-02: the RF consumption entry uses the same replaceable narrative reader.

The producer below is a synthetic, standalone script in its own directory. It is
started by an isolated interpreter (``-I -S``), so no ``company_wiki`` package, no
``PYTHONPATH`` and no site-packages are reachable: a successful consumption can
only come from the connection the caller supplied. It replays the frozen public
narrative wire and every byte is still validated by the unchanged RF reader. No
network, original document, model call or paid service is involved.
"""
from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
import urllib.request
from copy import deepcopy
from pathlib import Path
from typing import NamedTuple

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from company_wiki_narrative_contracts import (  # noqa: E402
    NarrativeTransportError, _context_from_verified, canonical_bytes, validate_narrative_response,
)
from company_wiki_narrative_reader import read_narrative_context  # noqa: E402
from fix_hashes import apply_hash_fixes  # noqa: E402
from revenue_core import run_forecast, validate_document  # noqa: E402
from source_narrative_context import consume_narrative_input  # noqa: E402
from test_company_wiki_source_reader_v2 import _ref  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

GOLDEN = ROOT / "tests/fixtures/cwp_narrative_transport_v1"
PARAMETER = "0_base_2026"
CLAIM = "d4-port-consumption"

PRODUCER = '''\
"""Synthetic narrative producer: stdin request in, bundle/receipt out."""
import hashlib
import json
import os
import sys
from pathlib import Path

home = Path(__file__).resolve().parent
wire = home / "wire"
request = sys.stdin.buffer.read()
try:
    import company_wiki  # noqa: F401
except ImportError as exc:
    cwp_import = type(exc).__name__
else:
    cwp_import = "imported"
with (wire / "calls.jsonl").open("a", encoding="utf-8") as log:
    log.write(json.dumps({
        "request_sha256": hashlib.sha256(request).hexdigest(),
        "pythonpath": os.environ.get("PYTHONPATH"),
        "cwp_import": cwp_import,
        "cwp_modules": sorted(name for name in sys.modules if name.split(".")[0] == "company_wiki"),
        "sys_path": sys.path,
        "argv": sys.argv[1:],
    }) + "\\n")
mode = (wire / "mode.txt").read_text(encoding="utf-8").strip()
refusal = (b'{"schema_version":"narrative-read-receipt/1","status":"unavailable",'
           b'"reason":"reader_unavailable"}\\n')
if mode == "unavailable":
    sys.stderr.buffer.write(refusal)
    raise SystemExit(2)
if mode == "crash_on_stderr":
    sys.stderr.buffer.write(b"Traceback (most recent call last):\\nRuntimeError\\n")
    raise SystemExit(2)
if mode == "body_on_refusal":
    sys.stdout.buffer.write((wire / "bundle.json").read_bytes())
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(refusal)
    raise SystemExit(2)
body = (wire / "bundle.json").read_bytes()
if mode == "bad_bytes":
    body = body[:-1] + b"X"
sys.stdout.buffer.write(body)
sys.stdout.buffer.flush()
if mode != "empty_receipt":
    sys.stderr.buffer.write((wire / "receipt.jsonl").read_bytes())
sys.stderr.buffer.flush()
'''


@pytest.fixture(autouse=True)
def offline_and_path_free(monkeypatch):
    """No network, and no inherited PYTHONPATH the producer could import from."""

    def refuse(*_args, **_kwargs):
        raise AssertionError("D4-02 consumption must stay offline")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(urllib.request, "urlopen", refuse)
    monkeypatch.delenv("PYTHONPATH", raising=False)


# ---------------------------------------------------------------------------
# Frozen public wire, retargeted to the RF source fixture
# ---------------------------------------------------------------------------

def _golden(name):
    return json.loads((GOLDEN / name).read_bytes())


def _retargeted_wire(source_ref=None):
    """Keep the public wire, point its parent at the RF fixture's source bytes."""
    ref = deepcopy(_ref() if source_ref is None else source_ref)
    request = _golden("read_request.json")
    bundle = json.loads((GOLDEN / "bundle.json").read_bytes())
    receipt = _golden("read_receipt.json")
    request["narrative_ref"]["source_ref"] = deepcopy(ref)
    bundle["source_ref"] = deepcopy(ref)
    span = bundle["evidence_spans"][0]
    span["source_id"] = ref["source_id"]
    span["output_sha256"] = hashlib.sha256(canonical_bytes({
        "raw_text": span["raw_text"], "structured_value": span["structured_value"]})).hexdigest()
    span["span_id"] = "urn:company-wiki:evidence-span:sha256:" + hashlib.sha256(canonical_bytes({
        "source_id": span["source_id"], "locator": span["locator"],
        "output_sha256": span["output_sha256"]})).hexdigest()
    draft = bundle["summary"]["draft"]
    draft["source_id"], draft["source_sha256"] = ref["source_id"], ref["content_sha256"]
    draft["claims"][0]["evidence_ids"] = [span["span_id"]]
    lineage = bundle["transcript_lineage"]
    lineage.update(original_source_id=ref["source_id"], original_sha256=ref["content_sha256"],
                   original_byte_size=ref["byte_size"], original_mime_type=ref["mime_type"],
                   text_sha256=ref["content_sha256"], text_byte_size=ref["byte_size"])
    binding = bundle["transcript_byte_bindings"][0]
    binding["evidence_id"] = span["span_id"]
    binding["source_byte_ranges"] = [{"start": 0, "end": 57}]
    for key in ("document_id", "source_id", "content_sha256", "byte_size", "mime_type"):
        receipt["manifest"][key] = ref[key]
    receipt["narrative_ref"]["source_ref"] = deepcopy(ref)
    # Published before the RF information date; the read itself stays after both.
    request["as_of_date"] = receipt["as_of_date"] = "2026-07-12"
    receipt["manifest"]["published_date"] = "2026-06-01"
    receipt["manifest"]["retrieved_at"] = "2026-06-02T00:00:00Z"
    receipt["read_at"] = "2026-07-01T00:00:00Z"
    body = canonical_bytes(bundle)
    request["narrative_ref"]["artifact_sha256"] = hashlib.sha256(body).hexdigest()
    request["narrative_ref"]["byte_size"] = len(body)
    receipt["narrative_ref"] = deepcopy(request["narrative_ref"])
    return request, body, canonical_bytes(receipt) + b"\n"


def _producer(root, body, receipt, mode="ok"):
    """Own directory, own name, own interpreter; the payload sits beside it."""
    wire = root / "wire"
    wire.mkdir(parents=True)
    (wire / "bundle.json").write_bytes(body)
    (wire / "receipt.jsonl").write_bytes(receipt)
    (wire / "mode.txt").write_text(mode, encoding="utf-8")
    script = root / "independent_summary_producer.py"
    script.write_text(PRODUCER, encoding="utf-8")
    return [sys.executable, "-I", "-S", "-B", str(script)], wire


def _calls(wire):
    log = wire / "calls.jsonl"
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def _document(value):
    data = forecast_document()
    data["as_of_date"] = value["as_of_date"]
    data["sources"][0]["capture"]["snapshot_sha256"] = value["source_ref"]["content_sha256"]
    apply_hash_fixes(data)
    return data


def _binding(value, parameter_id=PARAMETER):
    return {"span_id": value["evidence_spans"][0]["span_id"], "claim_id": CLAIM,
            "parameter_id": parameter_id, "support_type": "rationale_support"}


class Port(NamedTuple):
    request: dict
    command: list[str]
    wire: Path
    config: Path
    value: dict  # the same context the public verification produces


def _port(tmp_path, mode="ok"):
    request, body, receipt = _retargeted_wire()
    command, wire = _producer(tmp_path / "producer-home", body, receipt, mode)
    config = tmp_path / "opaque-reader.handle"
    config.write_text("{}", encoding="utf-8")
    value = validate_narrative_response(request, body, receipt).to_dict()
    return Port(request, command, wire, config, value)


# ---------------------------------------------------------------------------
# C-1: an explicit connection reads the same verified context
# ---------------------------------------------------------------------------

def test_d4_explicit_producer_port_matches_the_public_reader_verification(tmp_path, monkeypatch):
    port = _port(tmp_path)
    # A company_wiki package is placed on PYTHONPATH: the port must still not reach it.
    stub = tmp_path / "on-pythonpath" / "company_wiki"
    stub.mkdir(parents=True)
    (stub / "__init__.py").write_text(
        "raise AssertionError('the consumption port imported company_wiki')\n", encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", str(stub.parent))
    context = read_narrative_context(port.request, catalog_config=port.config,
                                     reader_command=port.command)
    assert context.to_dict() == port.value
    assert context.to_dict()["read_receipt"]["replay_status"] == "verified"
    calls = _calls(port.wire)
    assert len(calls) == 1
    assert calls[0]["request_sha256"] == hashlib.sha256(canonical_bytes(port.request)).hexdigest()
    assert calls[0]["argv"] == ["--config", str(port.config), "--operation", "read"]
    assert calls[0]["pythonpath"] == str(stub.parent)  # visible, and still not importable
    assert calls[0]["cwp_import"] == "ModuleNotFoundError"
    assert calls[0]["cwp_modules"] == []
    assert not any("company_wiki" in entry or "site-packages" in entry
                   for entry in calls[0]["sys_path"])
    assert str(ROOT) not in calls[0]["sys_path"]


def test_d4_one_consumption_reads_once_and_reaches_claim_parameter_formula_report(tmp_path):
    request, command, wire, config, value = _port(tmp_path)
    data = _document(value)
    validate_document(data)
    baseline = run_forecast(data)
    updated, consumed = consume_narrative_input(
        data, request=request, bindings=[_binding(value)], source_id="filing",
        catalog_config=config, reader_command=command,
    )
    assert len(_calls(wire)) == 1  # one selection, one actual read
    assert consumed["status"] == "consumed"
    claim = next(item for item in updated["evidence_claims"] if item["claim_id"] == CLAIM)
    assert claim["content_sha256"] == value["source_ref"]["content_sha256"]
    assert claim["excerpt"] == value["evidence_spans"][0]["raw_text"]
    parameter = next(item for item in updated["parameters"] if item["parameter_id"] == PARAMETER)
    assert CLAIM in parameter["claim_ids"] and "filing" in parameter["source_ids"]
    dependency = consumed["dependencies"][0]
    assert dependency["claim_id"] == CLAIM and dependency["parameter_id"] == PARAMETER
    assert dependency["source_sha256"] == value["source_ref"]["content_sha256"]
    assert dependency["formula_refs"][0]["output"] == "recognized_revenue"
    validate_document(updated)
    linked = run_forecast(updated)
    assert linked["consolidated_forecast"] == baseline["consolidated_forecast"]
    assert linked["segments"] == baseline["segments"]
    assert CLAIM in [item["claim_id"] for item in linked["evidence_claims"]]


def test_d4_verified_context_binds_without_a_second_read_or_request(tmp_path):
    request, command, wire, config, value = _port(tmp_path)
    data = _document(value)
    read = read_narrative_context(request, catalog_config=config, reader_command=command)
    handed, handed_receipt = consume_narrative_input(
        data, request=request, bindings=[_binding(value)], source_id="filing", context=read)
    assert len(_calls(wire)) == 1
    assert handed_receipt["status"] == "consumed"
    reread, reread_receipt = consume_narrative_input(
        data, request=request, bindings=[_binding(value)], source_id="filing",
        catalog_config=config, reader_command=command)
    assert len(_calls(wire)) == 2
    assert handed == reread and handed_receipt == reread_receipt
    with pytest.raises(ValueError, match="verified NarrativeContext"):
        consume_narrative_input(data, request=request, bindings=[_binding(value)],
                                source_id="filing", context=read.to_dict())
    stale = {**request, "as_of_date": "2026-07-13"}
    with pytest.raises(ValueError, match="does not match the requested reference"):
        consume_narrative_input(data, request=stale, bindings=[_binding(value)],
                                source_id="filing", context=read)
    other_issuer = {**request, "expected_source": {
        **request["expected_source"], "security_id": "OTHER"}}
    with pytest.raises(ValueError, match="does not match the requested source"):
        consume_narrative_input(data, request=other_issuer, bindings=[_binding(value)],
                                source_id="filing", context=read)
    with pytest.raises(ValueError, match="cannot be combined with a reader connection"):
        consume_narrative_input(data, request=request, bindings=[_binding(value)],
                                source_id="filing", catalog_config=config, context=read)
    foreign = deepcopy(data)
    foreign["sources"][0]["capture"]["snapshot_sha256"] = "a" * 64
    with pytest.raises(ValueError, match="does not bind to the input source capture"):
        consume_narrative_input(foreign, request=request, bindings=[_binding(value)],
                                source_id="filing", context=read)
    with pytest.raises(ValueError, match="catalog configuration or a verified context"):
        consume_narrative_input(data, request=request, bindings=[_binding(value)],
                                source_id="filing")
    assert len(_calls(wire)) == 2


def test_d4_explicit_port_still_refuses_another_source_hash_or_information_date(tmp_path):
    request, command, wire, config, value = _port(tmp_path)
    data = _document(value)
    foreign = deepcopy(data)
    foreign["sources"][0]["capture"]["snapshot_sha256"] = "a" * 64
    with pytest.raises(ValueError, match="does not bind to the input source capture"):
        consume_narrative_input(foreign, request=request, bindings=[_binding(value)],
                                source_id="filing", catalog_config=config,
                                reader_command=command)
    stale = deepcopy(data)
    stale["as_of_date"] = "2026-07-13"
    with pytest.raises(ValueError, match="information date does not match input"):
        consume_narrative_input(stale, request=request, bindings=[_binding(value)],
                                source_id="filing", catalog_config=config,
                                reader_command=command)
    with pytest.raises(ValueError, match="unique claim and a used parameter"):
        consume_narrative_input(data, request=request,
                                bindings=[_binding(value, "not_a_parameter")],
                                source_id="filing", catalog_config=config,
                                reader_command=command)
    assert len(_calls(wire)) == 3
    assert foreign["evidence_claims"] == data["evidence_claims"] == stale["evidence_claims"]


def test_d4_another_narrative_source_or_unverified_receipt_is_refused(tmp_path):
    request, command, wire, config, value = _port(tmp_path)
    data = _document(value)
    other_ref = {**_ref(), "byte_size": 62, "content_sha256": "b" * 64,
                 "document_id": "urn:company-wiki:document:sha256:" + "b" * 64,
                 "source_id": "urn:company-wiki:source:sha256:" + "b" * 64}
    other_request, other_body, other_receipt = _retargeted_wire(other_ref)
    other = validate_narrative_response(other_request, other_body, other_receipt)
    assert other.to_dict()["source_ref"]["content_sha256"] == other_ref["content_sha256"]
    with pytest.raises(ValueError, match="does not match the requested reference"):
        consume_narrative_input(data, request=request, bindings=[_binding(value)],
                                source_id="filing", context=other)
    with pytest.raises(ValueError, match="does not bind to the input source capture"):
        consume_narrative_input(data, request=other_request,
                                bindings=[_binding(other.to_dict())],
                                source_id="filing", context=other)
    unverified = _context_from_verified({**value, "read_receipt": {
        **value["read_receipt"], "replay_status": "metadata_only"}})
    with pytest.raises(ValueError, match="no verified read receipt"):
        consume_narrative_input(data, request=request, bindings=[_binding(value)],
                                source_id="filing", context=unverified)
    assert _calls(wire) == []


def test_d4_a_string_reader_command_is_refused_as_a_command(tmp_path):
    request, _command_line, _wire_dir, config, _value = _port(tmp_path)
    with pytest.raises(NarrativeTransportError) as raised:
        read_narrative_context(request, catalog_config=config, reader_command="python")
    assert (raised.value.status, raised.value.reason) == ("blocked", "invalid_reader_command")


@pytest.mark.parametrize("mode,status,reason", [
    ("body_on_refusal", "unavailable", "partial_body_on_refusal"),
    ("unavailable", "unavailable", "reader_unavailable"),
    ("crash_on_stderr", "blocked", "invalid_json"),
    ("bad_bytes", "blocked", "artifact_bytes_mismatch"),
    ("empty_receipt", "blocked", "invalid_json"),
])
def test_d4_producer_port_refusals_are_named_and_never_become_evidence(tmp_path, mode, status, reason):
    request, command, wire, config, value = _port(tmp_path, mode)
    data = _document(value)
    before = deepcopy(data)
    with pytest.raises(NarrativeTransportError) as raised:
        consume_narrative_input(data, request=request, bindings=[_binding(value)],
                                source_id="filing", catalog_config=config,
                                reader_command=command)
    assert (raised.value.status, raised.value.reason) == (status, reason)
    assert data == before and len(_calls(wire)) == 1


def test_d4_projected_context_handover_checks_the_issuer_constraint():
    from test_w04_public_consumer import _consumption_data, projected_wire

    request, body, raw = projected_wire()
    context = validate_narrative_response(request, body, raw)
    value = context.to_dict()
    data = _consumption_data(value["parent_source_refs"][1])
    binding = {"span_id": value["evidence_spans"][0]["span_id"], "claim_id": CLAIM,
               "parameter_id": "qualitative", "support_type": "rationale_support"}
    updated, receipt = consume_narrative_input(
        data, request=request, bindings=[binding], source_id="source-alias", context=context)
    assert receipt["status"] == "consumed"
    assert CLAIM in [item["claim_id"] for item in updated["evidence_claims"]]
    other_issuer = {**request, "expected_issuer": {"market": "US", "security_id": "OTHER"}}
    with pytest.raises(ValueError, match="does not match the requested issuer"):
        consume_narrative_input(data, request=other_issuer, bindings=[binding],
                                source_id="source-alias", context=context)


# ---------------------------------------------------------------------------
# C-2: both public tools forward the same connection
# ---------------------------------------------------------------------------

def _write_assembly_fixture(root, request, binding, document):
    from company_wiki_source_v2 import build_revenue_source_record_from_verified_read
    from test_company_wiki_source_reader_v2 import BODY, _receipt

    data = document
    raw_receipt = _receipt()
    manifest = raw_receipt.pop("manifest")
    candidate = {"status": "source_candidate", "source_ref": _ref(),
                 "byte_verification": "pending_verified_open",
                 "document_kind": manifest["document_kind"], "fiscal_year": manifest["fiscal_year"],
                 "fiscal_period": manifest["fiscal_period"],
                 "resolution_outcome": "reused_existing", "download_events": 0}
    source = build_revenue_source_record_from_verified_read(
        source_ref=_ref(), read_receipt=raw_receipt, source_bytes=BODY, source_manifest=manifest,
        source_candidate=candidate, as_of_date=data["as_of_date"], source_type="regulatory_filing",
        publisher="synthetic producer fixture", page_or_section="1")
    source_id = source["source_id"]

    def rekey(value):
        if isinstance(value, dict):
            return {key: rekey(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rekey(item) for item in value]
        return source_id if value == "filing" else value

    data = rekey(data)
    data["sources"][0] = source
    for claim in data["evidence_claims"]:
        if claim["source_id"] == source_id:
            claim["content_sha256"] = source["capture"]["snapshot_sha256"]
            claim["capture_receipt_sha256"] = source["capture"]["receipt_sha256"]
    preparation = {"schema_version": "source-preparation-result/1", "source": source,
                   "filing_fetch": None, "narrative": None}
    research = data.pop("operating_research")
    payloads = {"input": data, "research": research, "preparation": preparation,
                "discovery": {"schema_version": "synthetic-discovery-receipt/1", "items": [],
                              "coverage_complete": False},
                "narrative": request, "bindings": [binding]}
    for name, value in payloads.items():
        (root / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return data, source_id


def test_d4_build_auditable_case_forwards_the_narrative_reader_port(tmp_path):
    from test_research_evidence_roles import calibrated_document

    request, command, wire, config, value = _port(tmp_path)
    data, source_id = _write_assembly_fixture(
        tmp_path, request, _binding(value, "0_base_2026"), calibrated_document())
    output = tmp_path / "assembled"
    run = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "tools/build_auditable_case.py"),
         "--company", "synthetic", "--input", str(tmp_path / "input.json"),
         "--research", str(tmp_path / "research.json"),
         "--preparation", str(tmp_path / "preparation.json"),
         "--discovery", str(tmp_path / "discovery.json"), "--as-of", data["as_of_date"],
         "--output-root", str(output), "--narrative-request", str(tmp_path / "narrative.json"),
         "--bindings", str(tmp_path / "bindings.json"), "--source-id", source_id,
         "--catalog-config", str(config),
         "--narrative-reader-command-json", json.dumps(command)],
        capture_output=True, text=True, encoding="utf-8", timeout=300, check=False,
    )
    assert run.returncode == 0, run.stderr[-2000:]
    assert len(_calls(wire)) == 1
    assembly = json.loads((output / "assembly.json").read_text(encoding="utf-8"))
    assert assembly["narrative_status"] == "consumed"
    consumption = json.loads((output / "narrative-consumption.json").read_text(encoding="utf-8"))
    assert consumption["dependencies"][0]["parameter_id"] == "0_base_2026"
    linked = json.loads((output / "linked-input.json").read_text(encoding="utf-8"))
    assert CLAIM in [item["claim_id"] for item in linked["evidence_claims"]]
    parameter = next(item for item in linked["parameters"] if item["parameter_id"] == "0_base_2026")
    assert CLAIM in parameter["claim_ids"]
    validate_document(linked)


def test_d4_run_narrative_consumption_e2e_forwards_the_narrative_reader_port(tmp_path):
    request, command, wire, config, value = _port(tmp_path)
    data = _document(value)
    for name, payload in (("input", data), ("narrative", request), ("bindings", [_binding(value)])):
        (tmp_path / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    output = tmp_path / "consumed"
    run = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "tools/run_narrative_consumption_e2e.py"),
         "--input", str(tmp_path / "input.json"),
         "--narrative-request", str(tmp_path / "narrative.json"),
         "--bindings", str(tmp_path / "bindings.json"), "--source-id", "filing",
         "--catalog-config", str(config), "--output-root", str(output),
         "--narrative-reader-command-json", json.dumps(command)],
        capture_output=True, text=True, encoding="utf-8", timeout=300, check=False,
    )
    assert run.returncode == 0, run.stderr[-2000:]
    assert len(_calls(wire)) == 1
    consumption = json.loads((output / "consumption.json").read_text(encoding="utf-8"))
    assert consumption["status"] == "consumed"
    linked = json.loads((output / "linked-input.json").read_text(encoding="utf-8"))
    validate_document(linked)
    result = run_forecast(linked)
    assert CLAIM in [item["claim_id"] for item in result["evidence_claims"]]


# ---------------------------------------------------------------------------
# C-3: the compatible default stays, and it is the same route the reader takes
# ---------------------------------------------------------------------------

def test_d4_default_reader_route_is_unchanged_when_no_port_is_given(tmp_path):
    from company_wiki_narrative_reader import _command

    request, _command_line, _wire_dir, config, value = _port(tmp_path)
    assert _command(config, "read", None)[1:4] == [
        "-B", "-m", "company_wiki.source_catalog.narrative_transport_cli"]
    data = _document(value)
    before = deepcopy(data)
    try:
        read_narrative_context(request, catalog_config=config)
    except NarrativeTransportError as exc:
        default_refusal = (exc.status, exc.reason)
    else:
        default_refusal = None
    if default_refusal is None:  # a local CWP deployment is installed here
        updated, consumed = consume_narrative_input(
            data, request=request, bindings=[_binding(value)], source_id="filing",
            catalog_config=config)
        assert consumed["status"] == "consumed" and updated != before
    else:
        with pytest.raises(NarrativeTransportError) as raised:
            consume_narrative_input(data, request=request, bindings=[_binding(value)],
                                    source_id="filing", catalog_config=config)
        assert (raised.value.status, raised.value.reason) == default_refusal
        assert data == before
