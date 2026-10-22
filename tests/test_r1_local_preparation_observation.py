"""Opaque local-IO diagnostic survives RF failure handoffs without new decisions.

The small wire fixture is FF production output frozen at 6dbb9e84; large machine
diagnostics are generated to exercise actual subprocess transport without a
sibling checkout, network, catalog scan, source originals, or provider calls.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from filing_upstream_cause import (  # noqa: E402
    failure_observation, parse_error_document, validated_filing_fetch_failure,
)

FIXTURE = ROOT / "tests/fixtures/r1_local_observation/ff-v2-failure.json"
OBSERVATION = "local_preparation_observation"


def wire(*, diagnostics: int = 0) -> dict:
    result = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if diagnostics:
        result[OBSERVATION]["diagnostics"] = [
            {"document_id": "urn:company-wiki:document:sha256:" + format(i, "064x"),
             "reason": "registered_identity_conflict", "status": "unavailable"}
            for i in range(diagnostics)
        ]
    return result


def compact(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def wrapped(payload: dict) -> dict:
    return {
        "error_code": "upstream_error",
        "error": "filing-fetch failed: status=upstream_error: budget_exceeded",
        "retryable": True,
        "upstream_cause": payload["filing"]["upstream_cause"],
        "producer_exit_code": payload["filing"]["producer_exit_code"],
        "calls": payload["calls"], "downloads": payload["downloads"],
        "companion_observation": payload["transcript"],
        "filing_fetch_result": payload,
    }


@pytest.mark.parametrize("diagnostics", [0, 600])
def test_optional_observation_copied_opaque_without_inventing_usage(diagnostics):
    payload = wire(diagnostics=diagnostics)
    # No owner enum or arithmetic in RF: a future machine reason/field remains
    # opaque, and rejected-tail observed bytes can exceed the charged bytes.
    owner = payload[OBSERVATION]["operations"][1]
    owner["reason"] = "new_owner_budget_reason"
    owner["next_owner_metric"] = {"unknown_code": "native_counter_v9"}
    actual = validated_filing_fetch_failure(payload)
    assert actual == payload
    assert actual is not payload
    actual[OBSERVATION]["operations"][1]["limits"]["max_bytes"] = 1
    assert owner["limits"]["max_bytes"] == 134217728
    observed = failure_observation(payload)
    assert observed["filing_fetch_result"] == payload
    assert observed["upstream_cause"] == payload["filing"]["upstream_cause"]
    assert observed["filing_fetch_result"][OBSERVATION]["local_io_usage"] is None
    assert observed["producer_exit_code"] == 0
    assert observed["calls"] == 3 and observed["downloads"] == 0
    assert "acquisition_observation" not in observed


def invalid(payload: dict, mutation: str) -> None:
    obs = payload[OBSERVATION]
    if mutation == "outer_type":
        payload[OBSERVATION] = []
    elif mutation == "version":
        obs["schema_version"] = "filing-local-preparation-observation/2"
    elif mutation == "scope":
        obs["usage_scope"] = "operation"
    elif mutation == "extra":
        obs["extra"] = "extra"
    elif mutation == "status_type":
        obs["status"] = False
    elif mutation == "reason_type":
        obs["reason"] = {}
    elif mutation == "bool_type":
        obs["blocks_download"] = 1
    elif mutation == "limits_type":
        obs["local_read_limits"]["max_candidates"] = True
    elif mutation == "limits_extra":
        obs["local_read_limits"]["unexpected"] = 1
    elif mutation == "operations_type":
        obs["operations"] = {}
    elif mutation == "row_type":
        obs["diagnostics"] = ["machine"]
    elif mutation == "usage_zero":
        obs["local_io_usage"] = 0
    elif mutation == "physical_key":
        obs["operations"][0]["storage_path"] = "hidden"
    elif mutation == "physical_value":
        obs["operations"][0]["version"] = "C:/hidden"
    elif mutation == "schema_path":
        obs["operations"][0]["schema_version"] = "file:///C:/Users/example/raw.pdf"
    elif mutation == "raw_body":
        obs["diagnostics"][0]["body"] = "hidden"
    elif mutation == "credentials":
        obs["operations"][0]["headers"] = {"authorization": "hidden"}
    elif mutation == "nonfinite":
        obs["operations"][0]["elapsed_seconds"] = float("nan")
    elif mutation == "depth":
        value = {"counter": 1}
        for _ in range(9):
            value = {"next": value}
        obs["operations"] = [value]
    elif mutation == "list_cap":
        obs["diagnostics"] = [{}] * 1025
    elif mutation == "dict_cap":
        obs["operations"] = [{f"k{i}": i for i in range(33)}]
    elif mutation == "string_cap":
        obs["reason"] = "a" * 257
    elif mutation == "key_cap":
        obs["operations"][0]["a" * 65] = 1
    elif mutation == "size_cap":
        obs["diagnostics"] = [
            {"code": "a" * 256, "reason": "b" * 256} for _ in range(300)
        ]
    else:
        raise AssertionError(mutation)


@pytest.mark.parametrize("mutation", [
    "outer_type", "version", "scope", "extra", "status_type", "reason_type",
    "bool_type", "limits_type", "limits_extra", "operations_type", "row_type",
    "usage_zero", "physical_key", "physical_value", "schema_path", "raw_body", "credentials",
    "nonfinite", "depth", "list_cap", "dict_cap", "string_cap", "key_cap", "size_cap",
])
def test_bad_optional_sidecar_cannot_claim_complete_but_safe_cause_survives(mutation):
    payload = wire()
    invalid(payload, mutation)
    observed = failure_observation(payload)
    assert "filing_fetch_result" not in observed
    assert observed["upstream_cause"] == payload["filing"]["upstream_cause"]
    assert observed["producer_exit_code"] == 0
    assert observed["calls"] == 3 and observed["downloads"] == 0


@pytest.mark.parametrize("as_wrapper", [False, True])
def test_large_versioned_error_decodes_whole_not_truncated(as_wrapper):
    payload = wire(diagnostics=600)
    expected = wrapped(payload) if as_wrapper else payload
    raw = json.dumps(expected, ensure_ascii=False, indent=2)
    assert len(raw.encode("utf-8")) > 65536
    assert parse_error_document(raw) == expected


@pytest.mark.parametrize("mutation", [
    "version", "physical_key", "depth", "size_cap",
])
def test_large_invalid_observation_does_not_bypass_legacy_stderr_cap(mutation):
    payload = wire(diagnostics=600)
    invalid(payload, mutation)
    raw = json.dumps(wrapped(payload), indent=2)
    assert len(raw.encode("utf-8")) > 65536
    assert parse_error_document(raw) is None


def test_legacy_base_limits_still_apply_with_large_extension():
    payload = wire()
    huge_count = 10 ** 4200
    payload["calls"] = payload["downloads"] = huge_count
    payload["filing"]["attempts"] = payload["filing"]["producer_exit_code"] = huge_count
    assert len(compact({k: v for k, v in payload.items() if k != OBSERVATION})) > 16384
    assert validated_filing_fetch_failure(payload) is None


def test_no_sibling_legacy_error_and_small_invalid_error_keep_old_safe_projection():
    payload = wire()
    del payload[OBSERVATION]
    assert validated_filing_fetch_failure(payload) == payload
    assert parse_error_document(json.dumps(wrapped(payload))) == wrapped(payload)
    assert parse_error_document(json.dumps({"error": "a" * 65536})) is None
    small = wire()
    invalid(small, "physical_key")
    parsed = parse_error_document(json.dumps(wrapped(small)))
    assert parsed is not None
    assert "filing_fetch_result" not in failure_observation(parsed)
    assert failure_observation(parsed)["upstream_cause"] == small["filing"]["upstream_cause"]


@pytest.mark.parametrize("mutation", ["oversize_raw", "truncated", "duplicate",
                                    "nonfinite", "huge_wrapper", "unknown_wrapper"])
def test_extended_decode_is_bounded_and_complete(mutation):
    raw = json.dumps(wrapped(wire(diagnostics=600)), indent=2)
    if mutation == "oversize_raw":
        raw = " " * (1024 * 1024) + raw
    elif mutation == "truncated":
        raw = raw[:-2]
    elif mutation == "duplicate":
        raw = raw.replace('"calls": 3', '"calls": 3, "calls": 3', 1)
    elif mutation == "nonfinite":
        raw = raw.replace('"calls": 3', '"calls": NaN', 1)
    elif mutation == "huge_wrapper":
        document = json.loads(raw)
        document["error"] = "a" * 20000
        raw = json.dumps(document)
    else:
        document = json.loads(raw)
        document["secret"] = "a" * 70000
        raw = json.dumps(document)
    assert parse_error_document(raw) is None


def _replay_root(tmp_path: Path, payload: dict, *, exit_code: int) -> Path:
    fake = tmp_path / "ff"
    (fake / "scripts").mkdir(parents=True)
    (fake / "error.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # Read replay from a file: never put large JSON in Windows argv/-c.
    (fake / "scripts/fetch_filing.py").write_text(
        "import pathlib,sys\n"
        "sys.stdin.read()\n"
        "sys.stdout.write((pathlib.Path(__file__).parents[1]/'error.json').read_text(encoding='utf-8'))\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    return fake


@pytest.mark.parametrize("diagnostics,exit_code", [(0, 1), (600, 2)])
@pytest.mark.parametrize("script", ["filing_fetch_client.py", "source_preparation.py"])
def test_actual_client_and_source_preparation_cli_preserve_full_wire(
    tmp_path, diagnostics, exit_code, script, record_property,
):
    payload = wire(diagnostics=diagnostics)
    original = deepcopy(payload)
    fake = _replay_root(tmp_path, payload, exit_code=exit_code)
    config = tmp_path / "catalog.yaml"
    config.write_text("{}", encoding="utf-8")
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    record_property("optional_compact_bytes", len(compact(payload[OBSERVATION])))
    record_property("ff_compact_bytes", len(compact(payload)))
    record_property("ff_pretty_bytes", (fake / "error.json").stat().st_size)
    expected_exit = 2 if script == "filing_fetch_client.py" else 3
    extra = [] if expected_exit == 2 else ["--company-wiki-catalog-config", str(config)]
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts" / script),
         "--result-envelope", "--filing-fetch-root", str(fake),
         "--timeout-seconds", "10", *extra],
        input=json.dumps({"document_kind": "semi_annual_report"}),
        cwd=tmp_path, env=env, text=True, encoding="utf-8",
        capture_output=True, timeout=30, check=False,
    )
    assert completed.returncode == expected_exit, completed.stderr
    assert not completed.stdout
    observed = json.loads(completed.stderr)
    record_property(script + "_stderr_bytes", len(completed.stderr.encode("utf-8")))
    assert observed.get("filing_fetch_result") == original
    assert observed["upstream_cause"] == original["filing"]["upstream_cause"]
    assert observed["producer_exit_code"] == 0
    assert observed["calls"] == 3 and observed["downloads"] == 0
    assert observed["companion_observation"] == original["transcript"]
    assert observed["filing_fetch_result"][OBSERVATION]["local_io_usage"] is None
    if script == "filing_fetch_client.py":
        assert observed["retryable"] is original["filing"]["retryable"]
    if diagnostics:
        assert len(completed.stderr.encode("utf-8")) > 65536

@pytest.mark.parametrize("schema", ["unknown-owner/2.1", "a" * 200 + "/2.1",
                                    "urn:owner:budget/2"])
def test_unknown_owner_schema_grammar_has_only_total_wire_length_bound(schema):
    payload = wire()
    obs = payload[OBSERVATION]
    obs["status"] = "owner_future_status"
    obs["reason"] = "file:missing"
    obs["local_read_limits"]["max_candidates"] = 512
    obs["operations"][0]["schema_version"] = schema
    assert validated_filing_fetch_failure(payload) == payload


@pytest.mark.parametrize("schema", [
    "C:/Users/example/raw.pdf", "file:///C:/Users/example/raw.pdf",
    "https://example.test/private", "file:/C:/Users/example/raw.pdf",
    "FILE:/tmp/raw.pdf", "a" * 254 + "/12",
])
def test_nested_schema_names_do_not_smuggle_paths_or_overlong_values(schema):
    payload = wire()
    payload[OBSERVATION]["operations"][0]["schema_version"] = schema
    observed = failure_observation(payload)
    assert "filing_fetch_result" not in observed
    assert observed["upstream_cause"] == payload["filing"]["upstream_cause"]


def test_physical_key_hygiene_is_case_insensitive():
    payload = wire()
    payload[OBSERVATION]["operations"][0]["PATH"] = "hidden"
    assert "filing_fetch_result" not in failure_observation(payload)

@pytest.mark.parametrize("mutation", ["physical_key", "size_cap"])
def test_actual_preparation_keeps_safe_cause_when_ff_optional_is_unsafe(tmp_path, mutation):
    payload = wire()
    invalid(payload, mutation)
    fake = _replay_root(tmp_path, payload, exit_code=2)
    config = tmp_path / "catalog.yaml"
    config.write_text("{}", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts/source_preparation.py"),
         "--result-envelope", "--filing-fetch-root", str(fake),
         "--company-wiki-catalog-config", str(config), "--timeout-seconds", "10"],
        input=json.dumps({"document_kind": "semi_annual_report"}),
        cwd=tmp_path, env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        text=True, encoding="utf-8", capture_output=True, timeout=30, check=False,
    )
    assert completed.returncode == 3 and not completed.stdout
    observed = json.loads(completed.stderr)
    assert "filing_fetch_result" not in observed
    assert observed["upstream_cause"] == payload["filing"]["upstream_cause"]
    assert observed["producer_exit_code"] == 0
    assert observed["calls"] == 3 and observed["downloads"] == 0
    assert "storage_path" not in completed.stderr
