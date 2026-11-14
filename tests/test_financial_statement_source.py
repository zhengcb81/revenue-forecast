"""RF research reads statements from the independent FF public process."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "scripts" / "financial_statement_source.py"
REQUEST = {
    "schema_version": "financial-statements-request/1",
    "company_query": "示例企业",
    "market": "CN",
    "statements": ["income_statement", "balance_sheet", "cash_flow"],
    "report_types": ["semi_annual"],
    "as_of_date": "2025-08-31",
    "knowledge_mode": "point_in_time",
    "fields": ["BIZTOTINCO"],
    "intent": "reuse_only",
}
REF = json.loads((ROOT / "tests/fixtures/cwp_source_ref_v2.json").read_text(encoding="utf-8"))
RESPONSE = {
    "schema_version": "financial-statements-response/1",
    "status": "complete",
    "statements": [{
        "statement_type": "income_statement",
        "reports": [{
            "period_start": "2025-01-01",
            "period_end": "2025-06-30",
            "currency": "CNY",
            "consolidation": "consolidated",
            "pit_verified": True,
            "observed_at": "2025-08-30T00:00:00Z",
            "source_ref": REF,
            "rows": [{"provider_field": "BIZTOTINCO", "value_decimal": "9123456789.000000",
                      "scale": "1", "unit": "currency", "json_pointer": "/report_list/0/amount"}],
        }],
    }],
    "usage": {"http_requests": 0},
}

STUB = """
import json, os, pathlib, sys, time
p = pathlib.Path(sys.argv[sys.argv.index('--config') + 1])
config = json.loads(p.read_bytes())
request = json.loads(sys.stdin.buffer.read())
with (p.parent / 'calls.jsonl').open('a', encoding='utf-8') as f:
    f.write(json.dumps(request, ensure_ascii=False) + '\\n')
assert pathlib.Path.cwd().name == 'empty'
assert float(sys.argv[sys.argv.index('--timeout-seconds') + 1]) == config.get('timeout', 15)
if config.get('sleep'):
    time.sleep(config['sleep'])
if config.get('diagnostics'):
    sys.stderr.buffer.write(b'\\xff' * 400_000)
sys.stdout.buffer.write(config['wire'].encode('utf-8'))
raise SystemExit(config['exit'])
"""


def launch(tmp_path, request, *, wire=None, code=0, mode="root", timeout=15, **options):
    ff = tmp_path / "独立采集"
    scripts = ff / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "fetch_statements.py").write_text(STUB, encoding="utf-8")
    config = tmp_path / "ff-owner-config.json"
    config.write_text(json.dumps({
        "wire": json.dumps(RESPONSE, ensure_ascii=False) if wire is None else wire,
        "exit": code, "timeout": timeout, **options,
    }, ensure_ascii=False), encoding="utf-8")
    empty = tmp_path / "empty"
    empty.mkdir()
    command = [
        sys.executable, "-B", "-S", "-X", "utf8", str(ENTRY),
        "--company-wiki-config", str(config), "--timeout-seconds", str(timeout),
    ]
    if mode == "root":
        command += ["--filing-fetch-root", str(ff)]
    else:
        settings = tmp_path / "rf-owner-config.json"
        settings.write_text(json.dumps({
            "schema_version": "1.0", "filing_fetch_root": str(ff)
        }), encoding="utf-8")
        command += ["--filing-fetch-root-config", str(settings)]
    env = {**os.environ, "PYTHONPATH": ""}
    completed = subprocess.run(
        command, input=json.dumps(request, ensure_ascii=False).encode("utf-8"),
        cwd=empty, env=env, capture_output=True, timeout=20, check=False,
    )
    call_log = tmp_path / "calls.jsonl"
    calls = [json.loads(line) for line in call_log.read_text(encoding="utf-8").splitlines()] \
        if call_log.exists() else []
    assert not tuple(empty.iterdir())
    return completed, calls


def response(completed):
    return json.loads(completed.stdout.decode("utf-8"))


def test_configured_statement_only_runtime_preserves_provenance_and_units(tmp_path):
    completed, calls = launch(tmp_path, REQUEST, diagnostics=True, mode="config")
    assert completed.returncode == 0, completed.stderr
    assert response(completed) == RESPONSE
    assert calls == [REQUEST]


def test_default_intent_reuses_and_explicit_intent_remains_owner_owned(tmp_path):
    implicit = {key: value for key, value in REQUEST.items() if key != "intent"}
    default, default_calls = launch(tmp_path / "default", implicit)
    assert default.returncode == 0
    assert default_calls == [REQUEST]
    acquisition = {**REQUEST, "intent": "fetch_if_missing", "acquisition_limits": {
        "max_bytes": 121000, "timeout_seconds": 8, "max_cost_usd": "0.00",
    }}
    explicit, explicit_calls = launch(tmp_path / "explicit", acquisition)
    assert explicit.returncode == 0
    assert explicit_calls == [acquisition]


@pytest.mark.parametrize(("status", "code"), [
    ("partial", 0), ("not_found", 0), ("unavailable", 0),
    ("request_error", 2), ("config_error", 2), ("upstream_error", 2), ("fatal", 1),
])
def test_named_business_and_error_statuses_pass_through(tmp_path, status, code):
    upstream = {**RESPONSE, "status": status, "retryable": False, "error": "upstream example"}
    completed, calls = launch(tmp_path, REQUEST, wire=json.dumps(upstream), code=code)
    assert completed.returncode == code, completed.stderr
    assert response(completed) == upstream
    assert calls == [REQUEST]


@pytest.mark.parametrize(("wire", "code"), [
    ('{"schema_version":"financial-statements-response/1","status":"complete","status":"unavailable"}', 0),
    ('{"schema_version":"financial-statements-response/1","status":"complete","statements":[],"x":NaN}', 0),
    (json.dumps({**RESPONSE, "schema_version": "financial-statements-response/9000"}), 0),
    (json.dumps({**RESPONSE, "statements": None}), 0),
    (json.dumps(RESPONSE), 2),
])
def test_invalid_wire_never_yields_observations(tmp_path, wire, code):
    completed, calls = launch(tmp_path, REQUEST, wire=wire, code=code)
    assert completed.returncode == 2, completed.stderr
    body = response(completed)
    assert body["status"] == "upstream_error" and "statements" not in body
    assert calls == [REQUEST]


def test_wrong_request_contract_never_launches_ff(tmp_path):
    completed, calls = launch(tmp_path, {"schema_version": "2.0"})
    assert completed.returncode == 2, completed.stderr
    assert response(completed)["status"] == "request_error"
    assert calls == []


def test_timeout_is_not_reported_as_missing_data_or_retried(tmp_path):
    completed, calls = launch(tmp_path, REQUEST, timeout=1.5, sleep=25)
    assert completed.returncode == 2, completed.stderr
    body = response(completed)
    assert body["status"] == "upstream_error" and body["reason"] == "reader_timeout"
    assert body["retryable"] is False
    assert calls == [REQUEST]
