"""Tests for G-RF-DEPLOY-ROOT-01.

The owner workspace used here is a real ``ReportCatalog`` over a real frozen
forecast-engine artifact. It lives in a temporary directory that is
deliberately apart from the code checkout, so the trusted deployment seam is
exercised against separated code and data roots. Nothing here is production
data: the frozen artifact is produced by the owner engine inside the test.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import report_catalog_cli as catalog_cli  # noqa: E402
import report_catalog_compare_cli as compare_cli  # noqa: E402
from owner_file_lock import OwnerFileLock  # noqa: E402
from publication_registry import canonical_sha256  # noqa: E402
from report_catalog import ReportCatalog  # noqa: E402
from report_catalog_deployment import (DeploymentError, MANAGED_CATALOG_DIRECTORY,  # noqa: E402
                                       READ_ONLY_COMMANDS, WRITE_COMMANDS,
                                       build_catalog, managed_catalog_directory,
                                       resolve_owner_root, split_owner_root)
from revenue_core import run_forecast  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

ENTITY_ID = "ENT-deploy"
RUN_ID = "run-deploy"
ATTEMPT_ID = "attempt-ok"
LEFT_REPORT_ID = "rf-deploy"
RIGHT_REPORT_ID = "rf-deploy-2"


class BinaryInput:
    """Minimal stdin stand-in with the byte buffer the compare CLI reads."""

    def __init__(self, raw: bytes):
        self.buffer = io.BytesIO(raw)


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, allow_nan=False),
                    encoding="utf-8")


def _owner_workspace(root: Path) -> dict[str, Any]:
    """Register one real owner run/attempt/two reports inside ``root``.

    The catalog is written to the managed location of ``root`` so the public
    deployment seam finds it without any injected catalog file.
    """
    catalog = ReportCatalog(root=root)
    data = forecast_document()
    data["forecast_version"] = "deploy-root-test-v1"
    result = run_forecast(data)
    _write(root / "input.json", data)
    _write(root / "report.json", result)
    _write(root / "receipt-success.json", {"attempt_id": ATTEMPT_ID, "status": "succeeded"})
    company = {"entity_id": ENTITY_ID, "listing_id": "LST-deploy",
               "analysis_subject_id": "subject-deploy", "resolution_status": "resolved",
               "display_name": result["company_name"]}
    run = {"run_id": RUN_ID, "parent_run_id": None, "company": company,
           "source_as_of": result["as_of_date"], "created_at": "2026-10-29T12:00:00Z",
           "status": "partial", "scenario_set": ["low", "base", "high"],
           "reporting_currency": result["currency"], "model_metadata": {},
           "artifact_revision": "deploy-root-test-v1", "source_snapshot_refs": []}
    attempt = {"run_id": RUN_ID, "attempt_id": ATTEMPT_ID, "status": "succeeded",
               "started_at": "2026-10-29T12:00:00Z", "ended_at": "2026-10-29T12:01:00Z",
               "report_ids": [LEFT_REPORT_ID], "error_code": None,
               "source_evidence": {"kind": "attempt_receipt_json",
                                   "artifact": catalog.artifact_ref(root / "receipt-success.json")}}
    report = {"report_id": LEFT_REPORT_ID, "run_id": RUN_ID, "attempt_id": ATTEMPT_ID,
              "company": company, "artifact_kind": "revenue_forecast",
              "artifact_revision": "deploy-root-test-v1", "input_sha256": result["input_sha256"],
              "result_sha256": result["result_sha256"], "created_at": "2026-10-29T12:01:00Z",
              "status": "validated", "schema_version": result["schema_version"],
              "engine_version": result["engine_version"], "information_as_of": result["as_of_date"],
              "forecast_horizon": "2026-2027", "supersedes_report_id": None,
              "missing_reason": None, "reporting_currency": result["currency"],
              "reporting_scale": 6, "forecast_artifact": catalog.artifact_ref(root / "report.json"),
              "input_artifact": catalog.artifact_ref(root / "input.json")}
    second = {**report, "report_id": RIGHT_REPORT_ID, "created_at": "2026-10-29T12:03:00Z"}
    attempt["report_ids"] = [LEFT_REPORT_ID, RIGHT_REPORT_ID]
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report, second])
    return {"catalog": catalog, "result": result, "run": run, "attempt": attempt,
            "report": report, "second": second}


def _compare_request() -> bytes:
    return json.dumps({"left_report_id": LEFT_REPORT_ID, "right_report_id": RIGHT_REPORT_ID,
                       "scenario": "base", "metric_ids": ["revenue"]}).encode("utf-8")


def _file_set(root: Path) -> dict[str, tuple[str, int]]:
    """Return the relative path, byte SHA and size of every file under ``root``."""
    seen: dict[str, tuple[str, int]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            seen[path.relative_to(root).as_posix()] = (hashlib.sha256(data).hexdigest(), len(data))
    return seen


def _stderr_payload(capsys) -> dict[str, Any]:
    return json.loads(capsys.readouterr().err)


# -- the trusted deployment argument -----------------------------------------


def test_split_owner_root_removes_only_the_option_and_keeps_the_command():
    assert split_owner_root(["list-reports", "--entity-id", "E"]) == (None, ["list-reports", "--entity-id", "E"])
    assert split_owner_root(["--owner-root", "/owner", "compare"]) == ("/owner", ["compare"])
    assert split_owner_root(["--owner-root=/owner", "compare"]) == ("/owner", ["compare"])


def test_split_owner_root_refuses_a_repeated_or_valueless_option():
    with pytest.raises(DeploymentError) as error:
        split_owner_root(["--owner-root", "/a", "--owner-root", "/b"])
    assert error.value.code == "owner_root_invalid"
    with pytest.raises(DeploymentError) as error:
        split_owner_root(["compare", "--owner-root"])
    assert error.value.code == "owner_root_invalid"
    with pytest.raises(DeploymentError) as error:
        split_owner_root(["--owner-root", "--entity-id", "E"])
    assert error.value.code == "owner_root_invalid"


@pytest.mark.parametrize("argv", [
    ["--owner-root"],
    ["--owner-root", "--entity-id", ENTITY_ID, "list-reports"],
    ["--owner-root", "list-reports", "--entity-id", ENTITY_ID],
    ["--owner-root=", "list-reports", "--entity-id", ENTITY_ID],
])
def test_a_malformed_owner_root_is_a_named_json_failure_not_a_usage_error(capsys, monkeypatch, argv):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    assert catalog_cli.main(argv) == 2
    emitted = capsys.readouterr()
    assert emitted.out == ""
    error = json.loads(emitted.err)
    assert error["schema_version"] == "rf-report-catalog/1"
    assert error["error"]["code"] == "owner_root_invalid"
    assert "usage:" not in emitted.err


def test_a_malformed_owner_root_is_a_named_json_failure_in_the_compare_cli(capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    for argv in (["--owner-root"], ["--owner-root", "--flag", "compare"], ["--owner-root", "compare"]):
        assert compare_cli.main(argv) == 2
        emitted = capsys.readouterr()
        assert emitted.out == ""
        error = json.loads(emitted.err)
        assert error["schema_version"] == "rf-report-comparison/1"
        assert error["error"]["code"] == "owner_root_invalid"


def test_an_unknown_command_is_still_invalid_command_in_the_compare_cli(capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    assert compare_cli.main(["compare", "--catalog-file", "x"]) == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"]["code"] == "invalid_command"


def test_managed_catalog_directory_matches_the_owner_core_location(tmp_path, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    catalog = ReportCatalog(root=tmp_path)
    assert catalog.file == managed_catalog_directory(tmp_path) / "catalog.jsonl"
    assert MANAGED_CATALOG_DIRECTORY == ("artifacts", "report_catalog")


def test_resolve_owner_root_names_every_failure_without_echoing_the_path(tmp_path):
    with pytest.raises(DeploymentError) as error:
        resolve_owner_root("relative/owner")
    assert error.value.code == "owner_root_invalid"
    assert "relative/owner" not in error.value.message
    with pytest.raises(DeploymentError) as error:
        resolve_owner_root(str(tmp_path / "absent"))
    assert error.value.code == "owner_root_absent"
    assert "absent" not in error.value.message
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(DeploymentError) as error:
        resolve_owner_root(str(plain))
    assert error.value.code == "owner_root_missing"
    with pytest.raises(DeploymentError) as error:
        resolve_owner_root("")
    assert error.value.code == "owner_root_invalid"


def test_resolve_owner_root_accepts_an_owner_workspace_with_spaces_and_unicode(tmp_path):
    root = tmp_path / "owner workspace 空间"
    (root / "artifacts" / "report_catalog").mkdir(parents=True)
    assert resolve_owner_root(str(root)) == root.resolve()
    assert build_catalog(resolve_owner_root(str(root))) is not None


def test_build_catalog_keeps_the_code_root_default_when_no_root_is_given():
    assert resolve_owner_root(None) is None
    assert build_catalog(resolve_owner_root(None)) is None


def test_every_command_is_classified_as_read_only_or_write():
    assert WRITE_COMMANDS == {"import-w09"}
    assert READ_ONLY_COMMANDS == {"list-runs", "list-reports", "get-run", "get-report",
                                   "get-model", "get-attempt", "get-calculation",
                                   "get-calculation-trace", "get-source-snapshot"}
    assert not READ_ONLY_COMMANDS & WRITE_COMMANDS


# -- positive: two public CLIs read one separate owner workspace --------------


def test_both_public_clis_read_the_same_separate_owner_workspace(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner workspace 空间"
    data_root.mkdir()
    built = _owner_workspace(data_root)

    assert catalog_cli.main(["--owner-root", str(data_root), "list-reports",
                             "--entity-id", ENTITY_ID]) == 0
    listing = json.loads(capsys.readouterr().out)
    assert listing["schema_version"] == "rf-report-catalog/1"
    assert [row["report_id"] for row in listing["items"]] == [RIGHT_REPORT_ID, LEFT_REPORT_ID]
    assert listing["page"]["total"] == 2
    revision = listing["catalog_revision"]
    assert len(revision) == 64

    assert catalog_cli.main(["--owner-root", str(data_root), "get-report",
                             "--report-id", LEFT_REPORT_ID]) == 0
    exact = json.loads(capsys.readouterr().out)
    assert exact["catalog_revision"] == revision
    assert exact["view"]["report"]["report_id"] == LEFT_REPORT_ID
    assert exact["view"]["report"]["run_id"] == RUN_ID
    assert exact["view"]["report"]["result_sha256"] == built["result"]["result_sha256"]

    monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(_compare_request()))
    assert compare_cli.main(["--owner-root", str(data_root), "compare"]) == 0
    comparison = json.loads(capsys.readouterr().out)
    assert comparison["schema_version"] == "rf-report-comparison/1"
    assert comparison["catalog_revisions"] == {"left": revision, "right": revision}
    assert comparison["comparison"]["left_report_id"] == LEFT_REPORT_ID
    assert comparison["comparison"]["right_report_id"] == RIGHT_REPORT_ID
    rows = comparison["comparison"]["metrics"]
    assert rows and all(row["comparable"] for row in rows)
    assert {row["left"]["provenance"]["artifact_id"] for row in rows} == {LEFT_REPORT_ID}
    assert {row["right"]["provenance"]["artifact_id"] for row in rows} == {RIGHT_REPORT_ID}
    assert {row["left"]["provenance"]["run_id"] for row in rows} == {RUN_ID}


def test_both_public_clis_read_the_same_original_artifact_bytes(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    built = _owner_workspace(data_root)

    digest = hashlib.sha256((data_root / "report.json").read_bytes()).hexdigest()
    assert digest == built["report"]["forecast_artifact"]["bytes_sha256"]

    assert catalog_cli.main(["--owner-root", str(data_root), "get-report",
                             "--report-id", LEFT_REPORT_ID]) == 0
    exact = json.loads(capsys.readouterr().out)
    assert exact["view"]["report"]["input_sha256"] == built["report"]["input_sha256"]
    assert exact["view"]["report"]["result_sha256"] == built["report"]["result_sha256"]

    monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(_compare_request()))
    assert compare_cli.main(["--owner-root", str(data_root), "compare"]) == 0
    comparison = json.loads(capsys.readouterr().out)
    rows = comparison["comparison"]["metrics"]
    assert {row["left"]["number"]["fiscal_year"] for row in rows} == {
        row["right"]["number"]["fiscal_year"] for row in rows}
    assert all(row["left"]["number"]["currency"] == built["result"]["currency"] for row in rows)


def test_the_code_tree_default_root_is_unchanged_when_no_owner_root_is_given(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)

    assert catalog_cli.main(["get-report", "--report-id", LEFT_REPORT_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["schema_version"] == "rf-report-catalog/1"
    assert error["error"]["code"] == "not_found"

    monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(_compare_request()))
    assert compare_cli.main(["compare"]) == 2
    error = _stderr_payload(capsys)
    assert error["schema_version"] == "rf-report-comparison/1"
    assert error["error"]["code"] == "not_found"


def test_an_owner_workspace_without_registered_reports_returns_zero_rows(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    (data_root / "artifacts" / "report_catalog").mkdir(parents=True)

    assert catalog_cli.main(["--owner-root", str(data_root), "list-reports",
                             "--entity-id", ENTITY_ID]) == 0
    listing = json.loads(capsys.readouterr().out)
    assert listing["items"] == []
    assert listing["page"]["total"] == 0
    assert listing["snapshot"]["state"] == "empty"
    assert listing["catalog_revision"] == "0" * 64


@pytest.mark.parametrize("command,extra", [
    ("list-runs", ["--entity-id", ENTITY_ID]),
    ("list-reports", ["--entity-id", ENTITY_ID]),
    ("get-run", ["--run-id", RUN_ID]),
    ("get-report", ["--report-id", LEFT_REPORT_ID]),
    ("get-model", ["--report-id", LEFT_REPORT_ID]),
    ("get-attempt", ["--run-id", RUN_ID, "--attempt-id", ATTEMPT_ID]),
])
def test_the_owner_root_serves_every_read_only_command(tmp_path, capsys, monkeypatch, command, extra):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)

    assert catalog_cli.main(["--owner-root", str(data_root), command] + extra) == 0
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["schema_version"] == "rf-report-catalog/1"
    assert "error" not in emitted


def test_the_owner_root_serves_the_exact_calculation_command(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)

    assert catalog_cli.main(["--owner-root", str(data_root), "get-report",
                             "--report-id", LEFT_REPORT_ID]) == 0
    node_ids = json.loads(capsys.readouterr().out)["view"]["calculation_node_ids"]
    assert node_ids

    assert catalog_cli.main(["--owner-root", str(data_root), "get-calculation",
                             "--report-id", LEFT_REPORT_ID, "--node-id", node_ids[0]]) == 0
    calculation = json.loads(capsys.readouterr().out)
    assert calculation["schema_version"] == "rf-report-catalog/1"
    assert calculation["calculation"]["node_id"] == node_ids[0]
    assert calculation["calculation"]["trace_state"] in {"partial", "unavailable"}


# -- negative: the deployment argument stays trusted and bounded -------------


def test_a_relative_owner_root_is_refused_by_name(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)
    monkeypatch.chdir(data_root)

    assert catalog_cli.main(["--owner-root", "owner-root-relative", "list-reports",
                             "--entity-id", ENTITY_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "owner_root_invalid"
    assert "owner-root-relative" not in json.dumps(error)


def test_an_absent_owner_root_is_refused_by_name(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    missing = tmp_path / "absent owner"

    assert catalog_cli.main(["--owner-root", str(missing), "list-reports",
                             "--entity-id", ENTITY_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "owner_root_absent"
    assert "absent owner" not in error["error"]["message"]
    assert str(missing) not in json.dumps(error)


def test_an_owner_root_that_is_not_a_directory_is_refused(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    plain = tmp_path / "a-file"
    plain.write_text("x", encoding="utf-8")

    assert catalog_cli.main(["--owner-root", str(plain), "list-reports",
                             "--entity-id", ENTITY_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "owner_root_invalid"
    assert str(plain) not in json.dumps(error)


def test_a_wrong_owner_root_without_a_managed_catalog_is_refused(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()

    assert catalog_cli.main(["--owner-root", str(unrelated), "list-reports",
                             "--entity-id", ENTITY_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "owner_root_missing"
    assert str(unrelated) not in json.dumps(error)


def test_the_compare_cli_refuses_the_same_owner_root_failures(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(_compare_request()))

    assert compare_cli.main(["--owner-root", str(tmp_path / "absent"), "compare"]) == 2
    assert _stderr_payload(capsys)["error"]["code"] == "owner_root_absent"

    assert compare_cli.main(["--owner-root", "relative", "compare"]) == 2
    assert _stderr_payload(capsys)["error"]["code"] == "owner_root_invalid"

    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    assert compare_cli.main(["--owner-root", str(unrelated), "compare"]) == 2
    assert _stderr_payload(capsys)["error"]["code"] == "owner_root_missing"


def test_the_write_command_refuses_the_owner_root_and_writes_nothing(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)
    before = _file_set(data_root)

    assert catalog_cli.main(["--owner-root", str(data_root), "import-w09",
                             "--entity-id", ENTITY_ID,
                             "--identity-evidence-json", "{}"]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "owner_root_write_forbidden"
    assert str(data_root) not in json.dumps(error)
    assert _file_set(data_root) == before


def test_a_business_request_cannot_select_the_root(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)

    for field in ("owner_root", "root", "catalog", "catalog_file", "env", "command"):
        payload = json.dumps({"left_report_id": LEFT_REPORT_ID, "right_report_id": RIGHT_REPORT_ID,
                              "scenario": "base", "metric_ids": ["revenue"],
                              field: str(data_root)}).encode("utf-8")
        monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(payload))
        assert compare_cli.main(["--owner-root", str(data_root), "compare"]) == 2
        error = _stderr_payload(capsys)
        assert error["error"]["code"] == "invalid_request"
        assert str(data_root) not in json.dumps(error)


def test_duplicate_json_keys_are_refused_with_the_owner_root(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)

    payload = b'{"left_report_id":"rf-deploy","left_report_id":"rf-deploy"}'
    monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(payload))
    assert compare_cli.main(["--owner-root", str(data_root), "compare"]) == 2
    assert _stderr_payload(capsys)["error"]["code"] == "invalid_json"


def test_a_tampered_artifact_is_refused_by_both_clis(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)
    (data_root / "report.json").write_text("{}", encoding="utf-8")

    assert catalog_cli.main(["--owner-root", str(data_root), "get-report",
                             "--report-id", LEFT_REPORT_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "artifact_sha_mismatch"
    assert "report.json" not in json.dumps(error)

    monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(_compare_request()))
    assert compare_cli.main(["--owner-root", str(data_root), "compare"]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "incompatible"
    assert "report.json" not in json.dumps(error)


def test_an_artifact_locator_that_escapes_the_owner_root_is_refused(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)
    outside = tmp_path / "outside.json"
    _write(outside, {"schema_version": "rf-report-catalog/1"})

    catalog_file = data_root / "artifacts" / "report_catalog" / "catalog.jsonl"
    lines = [json.loads(line) for line in catalog_file.read_text(encoding="utf-8").splitlines()]
    for entry in lines:
        for record in entry.get("reports", []):
            record["forecast_artifact"]["relative_path"] = "../outside.json"
    previous = None
    rebuilt = []
    for entry in lines:
        payload = {key: value for key, value in entry.items() if key != "line_sha256"}
        payload["prev_line_sha256"] = previous
        line = {**payload, "line_sha256": canonical_sha256(payload)}
        previous = line["line_sha256"]
        rebuilt.append(json.dumps(line, ensure_ascii=False, sort_keys=True, allow_nan=False))
    catalog_file.write_text("\n".join(rebuilt) + "\n", encoding="utf-8")

    assert catalog_cli.main(["--owner-root", str(data_root), "get-report",
                             "--report-id", LEFT_REPORT_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "invalid_artifact_ref"
    assert "outside.json" not in json.dumps(error)


def test_the_catalog_environment_rule_is_not_widened_by_the_owner_root(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)
    other_root = tmp_path / "other"
    (other_root / "artifacts" / "report_catalog").mkdir(parents=True)

    monkeypatch.setenv("REVENUE_REPORT_CATALOG",
                       str(other_root / "artifacts" / "report_catalog" / "catalog.jsonl"))
    assert catalog_cli.main(["--owner-root", str(data_root), "list-reports",
                             "--entity-id", ENTITY_ID]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "catalog_path_forbidden"
    assert str(other_root) not in json.dumps(error)

    inside = data_root / "artifacts" / "report_catalog" / "catalog.jsonl"
    monkeypatch.setenv("REVENUE_REPORT_CATALOG", str(inside))
    assert catalog_cli.main(["--owner-root", str(data_root), "list-reports",
                             "--entity-id", ENTITY_ID]) == 0
    assert json.loads(capsys.readouterr().out)["page"]["total"] == 2


def test_out_of_bounds_requests_stay_named_under_the_owner_root(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)
    before = _file_set(data_root)

    for limit in ("0", "101"):
        assert catalog_cli.main(["--owner-root", str(data_root), "list-reports",
                                 "--entity-id", ENTITY_ID, "--limit", limit]) == 2
        error = _stderr_payload(capsys)
        assert error["error"]["code"] == "invalid_limit"
        assert str(data_root) not in json.dumps(error)

    assert catalog_cli.main(["--owner-root", str(data_root), "list-reports",
                             "--entity-id", ENTITY_ID, "--cursor", "not-a-cursor"]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "invalid_cursor"
    assert str(data_root) not in json.dumps(error)

    monkeypatch.setattr(compare_cli.sys, "stdin",
                        BinaryInput(b"x" * (compare_cli.MAX_INPUT_BYTES + 1)))
    assert compare_cli.main(["--owner-root", str(data_root), "compare"]) == 2
    error = _stderr_payload(capsys)
    assert error["error"]["code"] == "input_too_large"
    assert str(data_root) not in json.dumps(error)
    lock_path = data_root / "artifacts" / "report_catalog" / "catalog.jsonl.lock"
    assert _file_set(data_root) == before
    assert not OwnerFileLock(lock_path).is_locked()


def test_metadata_reads_leave_the_owner_workspace_byte_identical(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    data_root = tmp_path / "owner"
    data_root.mkdir()
    _owner_workspace(data_root)
    before = _file_set(data_root)

    assert catalog_cli.main(["--owner-root", str(data_root), "list-runs",
                             "--entity-id", ENTITY_ID]) == 0
    capsys.readouterr()
    assert catalog_cli.main(["--owner-root", str(data_root), "list-reports",
                             "--entity-id", ENTITY_ID]) == 0
    capsys.readouterr()
    assert catalog_cli.main(["--owner-root", str(data_root), "get-report",
                             "--report-id", LEFT_REPORT_ID]) == 0
    capsys.readouterr()
    monkeypatch.setattr(compare_cli.sys, "stdin", BinaryInput(_compare_request()))
    assert compare_cli.main(["--owner-root", str(data_root), "compare"]) == 0
    capsys.readouterr()

    assert _file_set(data_root) == before
    lock_path = data_root / "artifacts" / "report_catalog" / "catalog.jsonl.lock"
    assert not OwnerFileLock(lock_path).is_locked()


# -- the real public command line, in a separate process ----------------------


def test_public_cli_subprocess_reads_the_owner_workspace_from_the_code_tree(tmp_path):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("REVENUE_REPORT_CATALOG", raising=False)
    try:
        data_root = tmp_path / "owner workspace"
        data_root.mkdir()
        _owner_workspace(data_root)

        listing = subprocess.run(
            [sys.executable, "-B", "scripts/report_catalog_cli.py", "--owner-root", str(data_root),
             "list-reports", "--entity-id", ENTITY_ID, "--limit", "5"],
            capture_output=True, cwd=ROOT, timeout=120, env=dict(os.environ),
        )
        assert listing.returncode == 0
        payload = json.loads(listing.stdout.decode("utf-8"))
        assert [row["report_id"] for row in payload["items"]] == [RIGHT_REPORT_ID, LEFT_REPORT_ID]

        comparison = subprocess.run(
            [sys.executable, "-B", "scripts/report_catalog_compare_cli.py", "--owner-root",
             str(data_root), "compare"],
            input=_compare_request(), capture_output=True, cwd=ROOT, timeout=120,
            env=dict(os.environ),
        )
        assert comparison.returncode == 0
        result = json.loads(comparison.stdout.decode("utf-8"))
        assert result["catalog_revisions"] == {"left": payload["catalog_revision"],
                                                "right": payload["catalog_revision"]}

        refused = subprocess.run(
            [sys.executable, "-B", "scripts/report_catalog_cli.py", "--owner-root",
             str(tmp_path / "absent"), "list-reports", "--entity-id", ENTITY_ID],
            capture_output=True, cwd=ROOT, timeout=120, env=dict(os.environ),
        )
        assert refused.returncode == 2
        error = json.loads(refused.stderr.decode("utf-8"))
        assert error["error"]["code"] == "owner_root_absent"
        assert str(tmp_path) not in refused.stderr.decode("utf-8")
    finally:
        monkeypatch.undo()
