"""Isolated DU11 end-to-end: public reader bytes -> consume -> public calculation.

Real layer (never faked): the RF narrative reader adapter, its byte/SHA/receipt
validator, the RF consumer, the RF input contract, the revenue calculation CLI and
the ``narrative_source_preparation.py`` read CLI.

Faked layer only: the CWP reader command behind its published module path
``company_wiki.source_catalog.narrative_transport_cli``. A local stub package is
placed on ``PYTHONPATH`` for the child process, so the real reader still starts a
real bounded child process, reads its stdout/stderr and validates every byte. The
wire it replays is the frozen public ``actual-090`` bundle already in this
repository (the synthetic ``Acme business update`` fixture).

This is a transport/contract acceptance, not real company-quality acceptance: no
original document is read, downloaded, parsed or translated, no model is called and
``socket``/``urlopen`` are hard-failed for the duration of every test.
"""
from __future__ import annotations

from copy import deepcopy
import gzip
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from company_wiki_narrative_contracts import (  # noqa: E402
    NarrativeTransportError, validate_narrative_response,
)
from company_wiki_narrative_reader import read_narrative_context  # noqa: E402
from fix_hashes import apply_hash_fixes  # noqa: E402
from source_narrative_context import consume_narrative_input  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

WIRE = ROOT / "docs/plans/shared-reading-consumer-2026-10-14/fixtures"
SENTINEL = b"DU11 RF CITATION CLOSURE SENTINEL\n"
PARAMETER = "0_base_2026"

STUB = '''\
"""Local stand-in for the published CWP narrative transport CLI."""
import sys, time
from pathlib import Path

here = Path(__file__).resolve().parent      # .../cwp-stub/company_wiki/source_catalog
replay = here.parents[2] / "replay"
sys.stdin.buffer.read()
mode = (replay / "mode.txt").read_text(encoding="utf-8").strip()
with (replay / "calls.log").open("a", encoding="utf-8") as log:
    log.write(mode + " " + " ".join(sys.argv[1:]) + "\\n")
if mode == "sleep":
    time.sleep(60)
if mode == "unavailable":
    sys.stderr.buffer.write(
        b'{"schema_version":"narrative-read-receipt/1","status":"unavailable",'
        b'"reason":"reader_unavailable"}\\n')
    sys.stderr.buffer.flush()
    raise SystemExit(2)
body = (replay / "bundle.json").read_bytes()
if mode == "bad_bytes":
    body = body[:-1] + b"X"
sys.stdout.buffer.write(body)
sys.stdout.buffer.flush()
sys.stderr.buffer.write((replay / "receipt.jsonl").read_bytes())
sys.stderr.buffer.flush()
'''


# ---------------------------------------------------------------------------
# Owned temporary tree: sentinel, existing entry, manifest, restore receipt
# ---------------------------------------------------------------------------

def snapshot(root: Path) -> dict[str, tuple[str, int]]:
    return {
        path.relative_to(root).as_posix(): (
            hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns
        )
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def _remove(root: Path, names) -> list[str]:
    removed = []
    for name in sorted(names, key=lambda item: item.count("/"), reverse=True):
        path = root / name
        if path.is_file():
            path.unlink()
            removed.append(name)
    # The snapshot records files; test-created directories are reaped here.
    for path in sorted((item for item in root.rglob("*") if item.is_dir()),
                       key=lambda item: len(item.parts), reverse=True):
        if not any(path.iterdir()):
            removed.append(path.relative_to(root).as_posix() + "/")
            path.rmdir()
    return removed


@pytest.fixture
def owned(tmp_path):
    root = tmp_path / "du11-owned"
    root.mkdir()
    (root / "sentinel.bin").write_bytes(SENTINEL)
    (root / "out").mkdir()
    (root / "out" / "existing.json").write_text('{"existing": true}\n', encoding="utf-8")
    baseline = snapshot(root)
    yield root
    after = snapshot(root)
    for name, record in baseline.items():
        assert after[name] == record, f"pre-existing entry changed: {name}"
    created = sorted(set(after) - set(baseline))
    removed = _remove(root, created)
    assert snapshot(root) == baseline
    assert sorted(path.name for path in root.iterdir()) == ["out", "sentinel.bin"]
    directory = os.environ.get("DU11_PWF_RECEIPTS")
    test_name = os.environ.get("PYTEST_CURRENT_TEST", "")
    if directory and test_name:
        Path(directory).mkdir(parents=True, exist_ok=True)
        receipt = {
            "schema_version": "du11-e2e-restore-receipt/1",
            "test": test_name,
            "owned_root": "pytest tmp_path/du11-owned",
            "initial_files": sorted(baseline),
            "initial_bytes_mtime": {name: list(record) for name, record in baseline.items()},
            "sentinel_sha256": hashlib.sha256(SENTINEL).hexdigest(),
            "created": created,
            "removed": removed,
            "restored": snapshot(root) == baseline,
            "residual_directories": sorted(path.name for path in root.iterdir()),
        }
        name = hashlib.sha256(test_name.encode("utf-8")).hexdigest()[:16]
        (Path(directory) / f"restore-{name}.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@pytest.fixture(autouse=True)
def offline_guard(monkeypatch):
    def refuse(*_args, **_kwargs):
        raise AssertionError("DU11 E2E forbids network access")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(urllib.request, "urlopen", refuse)


# ---------------------------------------------------------------------------
# Frozen public wire + local CWP-boundary package
# ---------------------------------------------------------------------------

def frozen(version: str = "090"):
    request = json.loads((WIRE / f"actual-{version}-request.json").read_bytes())
    with gzip.open(WIRE / f"actual-{version}-bundle.json.gz", "rb") as stream:
        body = stream.read()
    receipt = (WIRE / f"actual-{version}-receipt.jsonl").read_bytes()
    assert hashlib.sha256(body).hexdigest() == request["narrative_ref"]["artifact_sha256"]
    return request, body, receipt


def prepare(root: Path, wire, mode: str = "ok", monkeypatch=None):
    request, body, receipt = wire
    replay = root / "replay"
    replay.mkdir()
    (replay / "bundle.json").write_bytes(body)
    (replay / "receipt.jsonl").write_bytes(receipt)
    (replay / "mode.txt").write_text(mode, encoding="utf-8")
    stub = root / "cwp-stub" / "company_wiki" / "source_catalog"
    stub.mkdir(parents=True)
    for package in (stub.parent, stub):
        (package / "__init__.py").write_text("", encoding="utf-8")
    (stub / "narrative_transport_cli.py").write_text(STUB, encoding="utf-8")
    config = root / "catalog.json"
    config.write_text("{}", encoding="utf-8")
    if monkeypatch is not None:
        monkeypatch.setenv("PYTHONPATH", str(root / "cwp-stub"))
    return root / "cwp-stub", config


def calls(root: Path) -> list[str]:
    log = root / "replay" / "calls.log"
    return [] if not log.is_file() else log.read_text(encoding="utf-8").splitlines()


def document(value):
    data = forecast_document()
    data["as_of_date"] = value["as_of_date"]
    data["sources"][0]["capture"]["snapshot_sha256"] = value["source_ref"]["content_sha256"]
    apply_hash_fixes(data)
    return data


def narrative_binding(value):
    return {"span_id": value["evidence_spans"][1]["span_id"], "claim_id": "du11_e2e",
            "parameter_id": PARAMETER, "support_type": "rationale_support"}


def run_cli(root: Path, name: str, data: dict) -> dict:
    input_path = root / f"{name}.json"
    input_path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
    output = root / "out" / f"{name}-forecast.json"
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "revenue_forecast.py"),
         str(input_path), "--output", str(output)],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, check=False,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    return json.loads(output.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# C-1: real reader bytes -> consume -> public calculation
# ---------------------------------------------------------------------------

def test_frozen_public_wire_survives_the_real_reader_consumer_and_calculator(owned, monkeypatch):
    request, body, receipt = frozen()
    _, config = prepare(owned, (request, body, receipt), monkeypatch=monkeypatch)
    context = read_narrative_context(request, catalog_config=config)
    value = context.to_dict()
    frozen_bundle = json.loads(body)
    assert value["reading_context"] == frozen_bundle["reading_context"]
    assert value["evidence_spans"] == frozen_bundle["evidence_spans"]
    assert calls(owned) == ["ok --config " + str(config) + " --operation read"]

    data = document(value)
    baseline = run_cli(owned, "baseline", deepcopy(data))
    updated, consumed = consume_narrative_input(
        data, request=request, bindings=[narrative_binding(value)], source_id="filing",
        catalog_config=config,
    )
    assert len(calls(owned)) == 2
    assert consumed["status"] == "consumed"
    trace = consumed["citation_trace"]
    reading = frozen_bundle["reading_context"]
    assert trace["reading"]["attribution"] == "groups_only"
    assert trace["status"] == "group_only"
    assert trace["reading"]["group_count"] == 1
    assert trace["reading"]["unread"]["counts"] == reading["unread"]["counts"]
    assert trace["reading"]["unread"]["limited"] is False
    assert trace["reading"]["unread"]["structure_complete"] is False
    assert trace["reading"]["unread"]["unassigned_unit_ids"] == 1
    assert trace["reading"]["layout_complete"] is False
    assert trace["dependencies"][0]["group_id"] == reading["groups"][0]["group_id"]
    assert trace["dependencies"][0]["closure"] == "reading_group"
    assert trace["dependencies"][0]["support_evidence_ids"] is None
    assert trace["dependencies"][0]["context_evidence"] is None

    linked = run_cli(owned, "linked", updated)
    assert linked["consolidated_forecast"] == baseline["consolidated_forecast"]
    assert linked["segments"] == baseline["segments"]
    assert any(item["claim_id"] == "du11_e2e" for item in linked["evidence_claims"])
    assert linked["result_sha256"] != baseline["result_sha256"]  # the input evidence grew


def test_read_cli_exports_the_complete_validated_context(owned, monkeypatch):
    request, body, receipt = frozen()
    _, config = prepare(owned, (request, body, receipt), monkeypatch=monkeypatch)
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "narrative_source_preparation.py"),
         "--company-wiki-catalog-config", str(config.resolve())],
        cwd=str(ROOT), input=json.dumps(request).encode("utf-8"), env=dict(os.environ),
        capture_output=True, timeout=120, check=False,
    )
    assert result.returncode == 0 and result.stderr == b""
    exported = json.loads(result.stdout)
    assert exported["schema_version"] == "revenue-narrative-context/1"
    assert exported["reading_context"] == json.loads(body)["reading_context"]
    assert exported["evidence_spans"] == json.loads(body)["evidence_spans"]
    assert exported["read_receipt"]["replay_status"] == "verified"
    assert len(calls(owned)) == 1


# ---------------------------------------------------------------------------
# C-2: negative controls stay refusals, never usable evidence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mode,reason", [("bad_bytes", "artifact_bytes_mismatch"),
                                        ("unavailable", "reader_unavailable"),
                                        ("sleep", "reader_timeout")])
def test_reader_negative_controls_never_produce_evidence(owned, monkeypatch, mode, reason):
    request, body, receipt = frozen()
    _, config = prepare(owned, (request, body, receipt), mode=mode, monkeypatch=monkeypatch)
    timeout = 1.0 if mode == "sleep" else 30
    with pytest.raises(NarrativeTransportError, match=reason):
        read_narrative_context(request, catalog_config=config, timeout_seconds=timeout)
    empty = {"as_of_date": request["as_of_date"], "sources": [], "parameters": [],
             "segments": []}
    with pytest.raises(NarrativeTransportError, match=reason):
        consume_narrative_input(empty, request=request, bindings=[], source_id="filing",
                                catalog_config=config, timeout_seconds=timeout)
    assert len(calls(owned)) == 2


def test_wrong_parent_asof_or_bytes_are_refused_before_any_claim(owned, monkeypatch):
    request, body, receipt = frozen()
    _, config = prepare(owned, (request, body, receipt), monkeypatch=monkeypatch)
    wrong_asof = deepcopy(request)
    wrong_asof["as_of_date"] = "2026-09-01"
    with pytest.raises(NarrativeTransportError, match="receipt_request_mismatch"):
        read_narrative_context(wrong_asof, catalog_config=config)
    with pytest.raises(NarrativeTransportError, match="artifact_bytes_mismatch"):
        validate_narrative_response(request, body[:-1] + b"X", receipt)
    with pytest.raises(NarrativeTransportError, match="artifact_bytes_mismatch"):
        validate_narrative_response(request, body + b"\n", receipt)

    context = read_narrative_context(request, catalog_config=config)
    value = context.to_dict()
    foreign = document(value)
    foreign["sources"][0]["capture"]["snapshot_sha256"] = "2" * 64
    apply_hash_fixes(foreign)
    with pytest.raises(ValueError, match="does not bind to the input source capture"):
        consume_narrative_input(foreign, request=request, bindings=[narrative_binding(value)],
                                source_id="filing", catalog_config=config)
    stale_date = document(value)
    stale_date["as_of_date"] = "2026-09-01"
    apply_hash_fixes(stale_date)
    with pytest.raises(ValueError, match="information date does not match input"):
        consume_narrative_input(stale_date, request=request, bindings=[narrative_binding(value)],
                                source_id="filing", catalog_config=config)
