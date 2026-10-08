"""Actual RF CLI failure handoff keeps the safe FF machine diagnostic."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import filing_fetch_client as client  # noqa: E402


def cause(code="adapter_timeout", started=True, complete=False):
    return {"schema_version": "filing-upstream-cause/1", "operation": "ensure",
            "code": code, "provider_started": started, "usage_complete": complete,
            "retry_scope": "none"}


def fake_fetch(tmp_path, diagnostic, *, exit_code=2, envelope=True):
    root = tmp_path / "fake-fetch"
    (root / "scripts").mkdir(parents=True)
    filing = {"status": "fatal", "reason": "safe producer failure", "retryable": False,
              "upstream_cause": diagnostic}
    payload = {"schema_version": "2.0", "status": "fatal", "filing": filing,
               "transcript": {"status": "not_requested"}} if envelope else {
                   "schema_version": "1.1", "status": "upstream_error",
                   "error_code": "upstream_error", "error": "safe producer failure",
                   "retryable": False, "upstream_cause": diagnostic}
    (root / "scripts" / "fetch_filing.py").write_text(
        "import json,sys\njson.load(sys.stdin)\nprint(" + repr(json.dumps(payload))
        + ")\nraise SystemExit(" + str(exit_code) + ")\n", encoding="utf-8")
    return root


@pytest.mark.parametrize("envelope,exit_code", [(True, 2), (True, 0), (False, 2), (False, 0)])
def test_library_preserves_upstream_cause_across_all_failure_shapes(tmp_path, envelope, exit_code):
    expected = cause()
    root = fake_fetch(tmp_path, expected, envelope=envelope, exit_code=exit_code)
    with pytest.raises(client._ClientError) as error:
        client.resolve_filing({"company_query": "Fixture"}, filing_fetch_root=root)
    assert getattr(error.value, "upstream_cause", None) == expected
    assert error.value.retryable is False


@pytest.mark.parametrize("started,complete", [(None, None), (True, False), (False, True)])
def test_actual_client_and_source_preparation_cli_keep_cause(tmp_path, started, complete):
    expected = cause(started=started, complete=complete)
    root = fake_fetch(tmp_path, expected)
    request = tmp_path / "request.json"
    request.write_text(json.dumps({"company_query": "Fixture"}), encoding="utf-8")
    config = tmp_path / "catalog.yaml"
    config.write_text("schema_version: '1.0'\n", encoding="utf-8")
    environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    for script, extra in [("filing_fetch_client.py", []),
                          ("source_preparation.py", ["--company-wiki-catalog-config", str(config)])]:
        completed = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts" / script),
                                    "--request-file", str(request), "--filing-fetch-root", str(root), *extra],
                                   cwd=tmp_path, env=environment, capture_output=True, text=True,
                                   encoding="utf-8", timeout=30, check=False)
        assert completed.returncode == (2 if script == "filing_fetch_client.py" else 3)
        assert not completed.stdout
        actual = json.loads(completed.stderr)
        assert actual.get("upstream_cause") == expected
        assert actual["error_code"] == ("fatal" if script == "filing_fetch_client.py" else "upstream")


@pytest.mark.parametrize("alteration", [
    {"code": "api_key=secret-fixture-value"}, {"provider_started": 1},
    {"usage_complete": []}, {"schema_version": "future-unknown"},
    {"operation": "http://private-fixture"}, {"retry_scope": "auto_recharge"},
])
def test_malformed_new_diagnostic_does_not_replace_legacy_failure(tmp_path, alteration):
    invalid = {**cause(), **alteration}
    root = fake_fetch(tmp_path, invalid)
    with pytest.raises(client._ClientError) as error:
        client.resolve_filing({"company_query": "Fixture"}, filing_fetch_root=root)
    assert getattr(error.value, "upstream_cause", None) is None
    assert error.value.status == "fatal"
    assert error.value.retryable is False
    assert "secret-fixture-value" not in str(error.value)


def test_no_new_diagnostic_keeps_existing_error_emission(capsys):
    client._emit_error("fatal", "legacy safe failure", retryable=False)
    assert json.loads(capsys.readouterr().err) == {
        "error_code": "fatal", "error": "legacy safe failure", "retryable": False}
