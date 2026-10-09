"""W08 actual RF CLI: truthful observations survive failure without raw text."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import source_preparation as prep  # noqa: E402

SECRET = "synthetic-w08-secret-no-real-key"


def proof(complete=True, count=17):
    return {"schema_version": "acquisition-failure/1", "code": "canonical_import_failed", "retryable": False,
            "provider_started": True, "usage_complete": complete, "usage_scope": "operation",
            "acquisition_usage": None if count is None else {"schema_version": "1.0", "response_bytes": count, "cost_usd": "0.03"}}


def failure(*, v2=True, complete=True, count=17):
    dto = proof(complete, count)
    detail = {"status": "upstream_error", "error_code": "upstream_error", "reason": "safe upstream failure", "retryable": False,
              "stage": "ensure", "attempts": 1, "acquisition_failure": dto,
              "upstream_cause": {"schema_version": "filing-upstream-cause/1", "operation": "ensure", "code": dto["code"],
                                 "provider_started": True, "usage_complete": complete, "retry_scope": "none"}}
    return {"schema_version": "2.0", "status": "upstream_error", "filing": detail, "transcript": {"status": "not_requested"},
            "calls": 2, "downloads": 0} if v2 else {"schema_version": "1.1", **detail, "calls": 2, "downloads": 0}


def fake(tmp_path, payload, *, exit_code=2, stderr=None):
    root = tmp_path / "fake-fetch"
    (root / "scripts").mkdir(parents=True)
    text = "import sys\nsys.stdin.read()\n"
    if stderr is None:
        text += "print(" + repr(json.dumps(payload)) + ")\n"
    else:
        text += "sys.stderr.write(" + repr(stderr) + ")\n"
    text += "raise SystemExit(" + str(exit_code) + ")\n"
    (root / "scripts/fetch_filing.py").write_text(text, encoding="utf-8")
    return root


def actual_cli(root, tmp_path, *, client_only=False):
    config = tmp_path / "catalog.yaml"
    config.write_text("schema_version: '1.0'\n", encoding="utf-8")
    names = {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "COMSPEC", "TEMP", "TMP", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "HOMEDRIVE", "HOMEPATH"}
    env = {key: value for key, value in os.environ.items() if key.upper() in names}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
    script = "filing_fetch_client.py" if client_only else "source_preparation.py"
    options = ["--source-ref-v2", "--result-envelope"] if client_only else ["--company-wiki-catalog-config", str(config)]
    result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts" / script),
                             "--filing-fetch-root", str(root), *options],
                            cwd=tmp_path, env=env, input='{"company_query":"Fixture"}', capture_output=True,
                            text=True, encoding="utf-8", timeout=15, check=False)
    assert result.returncode == (2 if client_only else 3) and not result.stdout
    return json.loads(result.stderr)


@pytest.mark.parametrize("v2,exit_code", [(True, 2), (True, 0), (False, 2), (False, 0)])
@pytest.mark.parametrize("complete,count", [(True, 17), (False, 36), (None, None)])
def test_actual_cli_keeps_exact_scoped_usage_phase_and_counts(tmp_path, v2, exit_code, complete, count):
    payload = failure(v2=v2, complete=complete, count=count)
    root = fake(tmp_path, payload, exit_code=exit_code)
    value = actual_cli(root, tmp_path)
    assert value.get("acquisition_failure") == proof(complete, count)
    assert {key: value.get(key) for key in ("stage", "attempts", "calls", "downloads")} == {
        "stage": "ensure", "attempts": 1, "calls": 2, "downloads": 0}
    assert value["upstream_cause"]["usage_complete"] is complete
    assert value["error_code"] == "upstream"


@pytest.mark.parametrize("wire", ["top_error", "stderr", "success_reason"])
def test_actual_cli_no_raw_secret_even_with_valid_cause(tmp_path, wire):
    payload = failure()
    unsafe = "https://invalid/?api_key=" + SECRET
    if wire == "top_error":
        payload["error"] = unsafe
    elif wire == "success_reason":
        payload["filing"]["reason"] = unsafe
    root = fake(tmp_path, payload, exit_code=0 if wire == "success_reason" else 2,
                stderr=unsafe if wire == "stderr" else None)
    value = actual_cli(root, tmp_path)
    assert SECRET not in json.dumps(value) and "https://invalid" not in json.dumps(value)
    if wire != "stderr":
        assert value["upstream_cause"]["code"] == "canonical_import_failed"


@pytest.mark.parametrize("alteration", [{"usage_scope": "invocation"}, {"code": SECRET}, {"provider_started": 1},
    {"acquisition_usage": {"schema_version": "1.0", "response_bytes": True, "cost_usd": "0"}},
    {"acquisition_usage": {"schema_version": "1.0", "response_bytes": 2, "cost_usd": "Infinity"}}, {"extra": SECRET}])
def test_malformed_observation_cannot_erase_valid_independent_cause(tmp_path, alteration):
    payload = failure()
    payload["filing"]["acquisition_failure"].update(alteration)
    root = fake(tmp_path, payload)
    value = actual_cli(root, tmp_path)
    assert value.get("acquisition_failure") is None
    assert value["upstream_cause"]["code"] == "canonical_import_failed"
    assert SECRET not in json.dumps(value)


@pytest.mark.parametrize("code", ["local_metadata_gap", "no_registered_local_source"])
def test_local_metadata_and_absent_original_are_distinct(tmp_path, code):
    payload = failure()
    detail = payload["filing"]
    detail.pop("acquisition_failure")
    detail["stage"] = "local_prepare"
    detail["upstream_cause"] = {"schema_version": "filing-upstream-cause/1", "operation": "local_prepare", "code": code,
                                "provider_started": False, "usage_complete": True, "retry_scope": "none"}
    root = fake(tmp_path, payload)
    value = actual_cli(root, tmp_path)
    assert value["upstream_cause"] == detail["upstream_cause"]
    assert value["stage"] == "local_prepare" and value["calls"] == 2


def test_reader_failure_retains_prior_observations_without_replaying_fetch(tmp_path, monkeypatch):
    config = tmp_path / "catalog.yaml"
    config.write_text("schema_version: '1.0'\n", encoding="utf-8")
    value = {"schema_version": "2.0", "status": "source_candidate", "filing": {"status": "source_candidate"}, "calls": 2, "downloads": 1}
    called = []
    monkeypatch.setattr(prep, "_run_filing_fetch", lambda *args: called.append(1) or value)
    monkeypatch.setattr(prep, "_prepare_source_ref_v2", lambda *args, **kw: (_ for _ in ()).throw(RuntimeError("reader refused")))
    with pytest.raises(prep.FilingSourcePreparationError) as caught:
        prep.prepare_source_result({}, company_wiki_catalog_config=config)
    assert caught.value.calls == 2 and caught.value.downloads == 1 and caught.value.stage == "source_reader"
    assert called == [1] and getattr(caught.value, "acquisition_failure", None) is None


@pytest.mark.parametrize("v2", [True, False])
@pytest.mark.parametrize("exit_code", [2, 0])
@pytest.mark.parametrize("mime_type", ["text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/x-company-custom"])
def test_public_client_projects_candidates_as_dtos_not_arbitrary_nested_bodies(tmp_path, v2, exit_code, mime_type):
    payload = failure(v2=v2)
    detail = payload["filing"] if v2 else payload
    payload["status"] = detail["status"] = "ambiguous"
    detail["error_code"] = "ambiguous"
    sha = "a" * 64
    ref = {"schema_version": "2.0", "document_id": "urn:company-wiki:document:sha256:" + sha,
           "source_id": "urn:company-wiki:source:sha256:" + sha, "content_sha256": sha,
           "byte_size": 25, "mime_type": mime_type}
    identity = {"ticker": "GOOGL", "canonical_name": "Alphabet Inc.", "market": "US", "exchange": "NASDAQ"}
    detail["candidates"] = [
        {"error": "https://invalid/?api_key=" + SECRET},
        {**identity, "diagnostics": {"nested": {"authorization": SECRET}}, "source_url": "https://invalid/?api_key=" + SECRET},
        {"source_ref": ref, "debug": [{"provider_key": SECRET}]},
        {"source_ref": {**ref, "extra": SECRET}},
        {**identity, "canonical_name": "https://invalid/?api_key=" + SECRET},
        {**identity, "market": {"error": SECRET}},
        {"source_ref": {**ref, "mime_type": [SECRET]}},
    ]
    root = fake(tmp_path, payload, exit_code=exit_code)
    value = actual_cli(root, tmp_path, client_only=True)
    assert value.get("candidates") == [identity, {"source_ref": ref}]
    assert SECRET not in json.dumps(value) and "https://invalid" not in json.dumps(value)
    assert value["error_code"] == "ambiguous" and value["upstream_cause"] == detail["upstream_cause"]
    assert value["acquisition_failure"] == detail["acquisition_failure"]
    assert value["calls"] == 2 and value["downloads"] == 0
