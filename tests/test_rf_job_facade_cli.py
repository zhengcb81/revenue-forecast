"""RF public CLI through the actual RF stages and controlled public source ports."""

import json
import os
from pathlib import Path
import subprocess
import sys

from test_company_wiki_source_v2 import BODY, _inputs
from test_rf_job_facade import _request


ROOT = Path(__file__).resolve().parents[1]


def _run(*args, request=None):
    return subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts/rf_job_cli.py"), *args],
        input=None if request is None else json.dumps(request, ensure_ascii=False),
        capture_output=True, text=True, encoding="utf-8", timeout=60,
        env=dict(os.environ, PYTHONUTF8="1", PYTHON_DOTENV_DISABLED="1"),
        check=False,
    )


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _deployment(tmp_path):
    ref, receipt, manifest = _inputs()
    manifest["display_name"] = "Test Co"
    manifest["fiscal_period"] = "FY"
    candidate = {"status": "source_candidate", "source_ref": ref,
                 "byte_verification": "pending_verified_open",
                 "document_kind": "annual_report", "fiscal_year": 2025, "fiscal_period": "FY",
                 "resolution_outcome": "reused_existing", "download_events": 0}

    ff = tmp_path / "ff"
    (ff / "scripts").mkdir(parents=True)
    _write_json(ff / "scripts/reply.json", {"schema_version": "2.0", "status": "source_candidate",
                                           "filing": candidate, "calls": 1, "downloads": 0})
    (ff / "scripts/fetch_filing.py").write_text(
        'from pathlib import Path\nimport json,sys\n'
        'request=json.load(sys.stdin)\n'
        'assert request["company_query"]=="Test Co" and request["filing_intent"]=="reuse_only"\n'
        'assert "--allow-download" not in sys.argv\n'
        'sys.stdout.buffer.write(Path(__file__).with_name("reply.json").read_bytes())\n',
        encoding="utf-8",
    )
    config = tmp_path / "connector.json"
    config.write_text("{}", encoding="utf-8")
    body = tmp_path / "body.pdf"
    body.write_bytes(BODY)
    _write_json(tmp_path / "receipt.json", dict(receipt, manifest=manifest))
    reader = tmp_path / "reader.py"
    reader.write_text(
        'from pathlib import Path\nimport sys\n'
        'args=sys.argv[1:]\n'
        'assert args[args.index("--purpose")+1]=="filing_reuse"\n'
        'root=Path(__file__).parent\n'
        'sys.stdout.buffer.write((root/"body.pdf").read_bytes())\n'
        'sys.stderr.buffer.write((root/"receipt.json").read_bytes()+b"\\n")\n',
        encoding="utf-8",
    )
    deployment = tmp_path / "deployment.json"
    _write_json(deployment, {
        "schema_version": "rf-job-deployment/1",
        "stages": {
            "source": {"filing_fetch_root": str(ff), "company_wiki_config": str(config),
                       "company_wiki_catalog_config": str(config),
                       "source_reader_command": [sys.executable, "-B", str(reader)],
                       "request_template": {"schema_version": "2.0", "market": "US",
                                            "document_kind": "annual_report", "fiscal_year": 2025,
                                            "mode": "exact", "filing_intent": "reuse_only"}},
            "compute": {}, "publication": {},
        },
        "limits": {"refs": {"unit-drill-0usd": {"max_cost_usd": "0.00", "max_new_downloads": 0}}},
    })
    return deployment, body


def test_public_job_runs_actual_engine_then_replays_and_refuses_changed_source(tmp_path):
    deployment, body = _deployment(tmp_path)
    owner = tmp_path / "owner"
    owner.mkdir()
    argv = ("--owner-root", str(owner), "--deployment-config", str(deployment))
    request = _request()
    first = _run(*argv, "submit", request=request)
    assert first.returncode == 0, first.stderr
    job = json.loads(first.stdout)
    view = job["job_view"]
    assert view["status"] == "succeeded", view
    assert view["cost"] == {"currency": "USD", "value": "0.00"}
    assert [stage["status"] for stage in view["stages"]] == ["completed"] * 3
    assert str(owner) not in first.stdout
    job_id = job["owner_job_id"]
    get_status = _run("--owner-root", str(owner), "get-status", "--job-id", job_id)
    assert json.loads(get_status.stdout)["job_view"]["status"] == "succeeded"
    assert job_id in {item["owner_job_id"] for item in json.loads(_run(*argv, "list-jobs").stdout)["jobs"]}

    body.write_bytes(b"x" * len(BODY))
    replay = json.loads(_run(*argv, "submit", request=request).stdout)
    assert replay["owner_job_id"] == job_id
    assert replay["job_view"]["idempotent_replay"] is True
    failure = _run(*argv, "submit", request=dict(request, idempotency_key="changed-source"))
    assert failure.returncode == 0, failure.stderr
    stages = json.loads(failure.stdout)["job_view"]["stages"]
    assert [stage["status"] for stage in stages] == ["failed", "pending", "pending"]


def test_malformed_deployment_arguments_return_pathless_named_error():
    result = _run("--owner-root", "get-status", "--owner-root", "--job-id", "rfjob-test")
    assert result.returncode == 2 and result.stdout == ""
    assert json.loads(result.stderr)["error"]["code"] == "owner_root_invalid"


def test_public_job_id_never_becomes_an_owner_path(tmp_path):
    for args in (("get-status", "--job-id", "../other"),
                 ("act", "--job-id", "../other", "--action", "reconcile")):
        result = _run("--owner-root", str(tmp_path), *args)
        assert result.returncode == 2 and result.stdout == ""
        assert json.loads(result.stderr)["error"]["code"] == "owner_job_id_invalid"
        assert str(tmp_path) not in result.stderr
    assert not (tmp_path / "artifacts").exists()
