"""M3-USAGE RF projection: acquisition-observation/1 survives both RF boundaries.

The public client CLI and the preparation CLI only validate and copy the
producer's operation observation — no recount, no fee inference, no MIME or
identity re-verification. A malformed sibling is dropped whole and never
erases the independent cause/receipt/count channels. Success envelopes pass
through unmodified (``usage stays producer-owned``).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import filing_fetch_client as client  # noqa: E402
import filing_upstream_cause as cause  # noqa: E402
import source_preparation as prep  # noqa: E402

SECRET = "synthetic-m3-secret-no-real-key"


def observation(**overrides):
    value = {
        "schema_version": "acquisition-observation/1",
        "usage_scope": "operation",
        "outcome": "failed",
        "provider_started": True,
        "usage_complete": False,
        "wire_body_bytes": 2841,
        "wire_usage_complete": False,
        "entity_body_bytes": 8192,
        "http_exchanges": 3,
        "http_exchanges_complete": False,
        "cost_usd": "0.0004",
        "http_observation": {"status_code": 200, "mime_type": "application/pdf",
                             "content_encoding": "gzip", "wire_content_length": 2841},
    }
    value.update(overrides)
    return value


def proof():
    return {"schema_version": "acquisition-failure/1", "code": "canonical_import_failed",
            "retryable": False, "provider_started": True, "usage_complete": False,
            "usage_scope": "operation",
            "acquisition_usage": {"schema_version": "1.0", "response_bytes": 36, "cost_usd": "0.03"}}


def failure_envelope(obs):
    detail = {"status": "upstream_error", "error_code": "upstream_error",
              "reason": "safe upstream failure", "retryable": False,
              "stage": "ensure", "attempts": 1, "acquisition_failure": proof(),
              "upstream_cause": {"schema_version": "filing-upstream-cause/1",
                                 "operation": "ensure", "code": "canonical_import_failed",
                                 "provider_started": True, "usage_complete": False,
                                 "retry_scope": "none"}}
    return {"schema_version": "2.0", "status": "upstream_error", "filing": detail,
            "transcript": {"status": "not_requested"}, "calls": 2, "downloads": 0,
            "acquisition_observation": obs}


def success_envelope(obs):
    sha = "c" * 64
    ref = {"schema_version": "2.0",
           "document_id": f"urn:company-wiki:document:sha256:{sha}",
           "source_id": f"urn:company-wiki:source:sha256:{sha}",
           "content_sha256": sha, "byte_size": 8192, "mime_type": "application/pdf"}
    filing = {"status": "source_candidate", "source_ref": ref,
              "byte_verification": "pending_verified_open",
              "document_kind": "annual_report", "fiscal_year": 2025,
              "fiscal_period": "FY", "resolution_outcome": "downloaded_new",
              "download_events": 1}
    result = {"schema_version": "2.0", "status": "source_candidate",
              "request_period": {"mode": "exact", "fiscal_year": 2025,
                                 "fiscal_period": "FY", "as_of_date": "2026-10-10"},
              "filing": filing,
              "transcript": {"status": "not_requested", "retryable": False},
              "calls": 2, "downloads": 1}
    if obs is not None:
        result["acquisition_observation"] = obs
    return result


def fake(tmp_path, payload, *, exit_code=2):
    root = tmp_path / "fake-fetch"
    (root / "scripts").mkdir(parents=True)
    text = "import sys\nsys.stdin.read()\n"
    text += "print(" + repr(json.dumps(payload)) + ")\n"
    text += "raise SystemExit(" + str(exit_code) + ")\n"
    (root / "scripts/fetch_filing.py").write_text(text, encoding="utf-8")
    return root


def actual_cli(root, tmp_path):
    config = tmp_path / "catalog.yaml"
    config.write_text("schema_version: '1.0'\n", encoding="utf-8")
    names = {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "COMSPEC", "TEMP", "TMP",
             "USERPROFILE", "APPDATA", "LOCALAPPDATA", "HOMEDRIVE", "HOMEPATH"}
    env = {key: value for key, value in os.environ.items() if key.upper() in names}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
    result = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts/source_preparation.py"),
         "--filing-fetch-root", str(root), "--company-wiki-catalog-config", str(config)],
        cwd=tmp_path, env=env, input='{"company_query":"Fixture"}', capture_output=True,
        text=True, encoding="utf-8", timeout=15, check=False)
    assert result.returncode == 3 and not result.stdout
    return json.loads(result.stderr)


class TestValidatedObservation:
    def test_passes_verbatim(self):
        published = observation()
        assert cause.validated_acquisition_observation(published) == published

    @pytest.mark.parametrize("mutate", [
        lambda v: v.pop("http_observation"),
        lambda v: v.update(extra=None),
        lambda v: v.update(usage_scope="invocation"),
        lambda v: v.update(outcome="invented"),
        lambda v: v.update(wire_body_bytes="2841"),
        lambda v: v.update(http_exchanges=-1),
        lambda v: v.update(cost_usd="Infinity"),
        lambda v: v.update(cost_usd=0.0004),
        lambda v: v.update(http_observation={"status_code": 200, "set-cookie": SECRET}),
    ])
    def test_any_deviation_drops_the_whole_object(self, mutate):
        value = observation()
        mutate(value)
        assert cause.validated_acquisition_observation(value) is None

    def test_null_cost_is_unknown_not_zero(self):
        assert cause.validated_acquisition_observation(
            observation(cost_usd=None))["cost_usd"] is None


class TestFailureObservation:
    def test_projects_sibling_from_envelope_top_level_and_flat(self):
        obs = observation()
        v2 = cause.failure_observation(failure_envelope(obs))
        assert v2["acquisition_observation"] == obs
        flat = {"schema_version": "1.1", "acquisition_observation": obs}
        assert cause.failure_observation(flat)["acquisition_observation"] == obs

    def test_detail_fallback_keeps_older_shapes_readable(self):
        obs = observation()
        payload = failure_envelope(None)
        payload["filing"]["acquisition_observation"] = obs
        assert cause.failure_observation(payload)["acquisition_observation"] == obs

    def test_malformed_sibling_drops_but_independent_channels_survive(self):
        v2 = cause.failure_observation(failure_envelope(observation(cost_usd="NaN")))
        assert "acquisition_observation" not in v2
        assert v2["acquisition_failure"] == proof()
        assert v2["upstream_cause"]["code"] == "canonical_import_failed"
        assert {key: v2[key] for key in ("stage", "attempts", "calls", "downloads")} == {
            "stage": "ensure", "attempts": 1, "calls": 2, "downloads": 0}


class TestActualCliBoundary:
    def test_preparation_cli_keeps_observation_counts_and_cause(self, tmp_path):
        obs = observation()
        root = fake(tmp_path, failure_envelope(obs))
        value = actual_cli(root, tmp_path)
        assert value["acquisition_observation"] == obs
        assert value["acquisition_failure"] == proof()
        assert {key: value.get(key) for key in ("stage", "attempts", "calls", "downloads")} == {
            "stage": "ensure", "attempts": 1, "calls": 2, "downloads": 0}
        assert value["error_code"] == "upstream"
        assert SECRET not in json.dumps(value)

    def test_preparation_cli_drops_malformed_observation_only(self, tmp_path):
        root = fake(tmp_path, failure_envelope(observation(http_exchanges="three")))
        value = actual_cli(root, tmp_path)
        assert "acquisition_observation" not in value
        assert value["acquisition_failure"] == proof()

    def test_client_cli_success_passes_envelope_verbatim(self, tmp_path):
        obs = observation(outcome="downloaded_new", usage_complete=True,
                          wire_usage_complete=True, http_exchanges_complete=True)
        payload = success_envelope(obs)
        root = fake(tmp_path, payload, exit_code=0)
        names = {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "COMSPEC", "TEMP", "TMP",
                 "USERPROFILE", "APPDATA", "LOCALAPPDATA", "HOMEDRIVE", "HOMEPATH"}
        env = {key: value for key, value in os.environ.items() if key.upper() in names}
        env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1")
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", str(ROOT / "scripts/filing_fetch_client.py"),
             "--filing-fetch-root", str(root), "--source-ref-v2", "--result-envelope"],
            cwd=tmp_path, env=env, input='{"company_query":"Fixture"}', capture_output=True,
            text=True, encoding="utf-8", timeout=15, check=False)
        assert result.returncode == 0, result.stderr
        value = json.loads(result.stdout)
        assert value["acquisition_observation"] == obs
        assert value["downloads"] == 1

    def test_client_cli_without_observation_adds_no_key(self, tmp_path):
        payload = success_envelope(None)
        root = fake(tmp_path, payload, exit_code=0)
        result = client.resolve_filing_result(
            {"company_query": "Fixture", "document_kind": "annual_report",
             "fiscal_year": 2025, "as_of_date": "2026-10-10", "market": "US"},
            allow_download=True, timeout_seconds=10.0, filing_fetch_root=root,
            source_ref_v2=True)
        assert "acquisition_observation" not in result


class TestReaderStageRetention:
    def test_reader_failure_retains_prior_observation_without_replay(self, tmp_path, monkeypatch):
        obs = observation(outcome="downloaded_new", usage_complete=True)
        envelope = success_envelope(obs)
        config = tmp_path / "catalog.yaml"
        config.write_text("schema_version: '1.0'\n", encoding="utf-8")
        calls = []
        monkeypatch.setattr(prep, "_run_filing_fetch",
                            lambda *args: calls.append(1) or envelope)
        monkeypatch.setattr(prep, "_prepare_source_ref_v2",
                            lambda *args, **kw: (_ for _ in ()).throw(RuntimeError("reader refused")))
        with pytest.raises(prep.FilingSourcePreparationError) as caught:
            prep.prepare_source_result({}, company_wiki_catalog_config=config)
        error = caught.value
        # The real reader-stage path re-runs failure_observation on the
        # successful FF envelope; the sibling survives alongside counts.
        assert error.acquisition_observation == obs
        assert error.calls == 2 and error.downloads == 1
        assert calls == [1]  # fetch never replayed
