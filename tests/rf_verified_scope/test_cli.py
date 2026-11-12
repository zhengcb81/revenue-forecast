"""Thin CLI, full-result output and preservation of the published import-rf-job entry."""
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from rf_verified_scope import fixtures as fx

ROOT = Path(__file__).resolve().parents[2]
IDENTITY_CLI = ROOT / "scripts" / "report_catalog_identity_cli.py"


def run_cli(monkeypatch, capsys, env, argv, *, stdin: bytes = b""):
    import report_catalog_verified_compare_cli as cli

    monkeypatch.setattr(cli, "build_catalog", lambda _root: env["catalog"])
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(stdin)))
    code = cli.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def cli_args(env, fixture: Path, command: str, *extra: str) -> list[str]:
    return [command, "--data-root", str(env["store"].root),
            "--subject-fixture", str(fixture), *extra]


def test_import_rf_job_management_entry_is_preserved(tmp_path):
    """B2 must not remove or rewrite the published RF job admission CLI."""
    child = subprocess.run([sys.executable, "-B", str(IDENTITY_CLI), "--help"],
                           cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert child.returncode == 0, child.stderr
    assert "import-rf-job" in child.stdout
    source = IDENTITY_CLI.read_text(encoding="utf-8")
    assert 'commands.add_parser("import-rf-job")' in source
    assert '"--job-sha256"' in source and '"--report-sha256"' in source
    assert "import_rf_job(" in source


def test_cli_get_bindings_compare_and_append(build_env, tmp_path, monkeypatch, capsys):
    env = build_env(tmp_path)
    fixture = tmp_path / "subjects.json"
    fx.write_subject_fixture(fixture, fx.subject_snapshot())

    code, out, err = run_cli(monkeypatch, capsys, env,
                             cli_args(env, fixture, "get-bindings", "--report-id", "R-OLD"))
    assert code == 0 and err == "", err
    view = json.loads(out)
    assert view["schema_version"] == "rf-report-scope-bindings/1"
    assert view["scope_view"]["state"] == "available"
    assert [row["binding_id"] for row in view["scope_view"]["bindings"]] == [
        env["left"]["binding_id"]]

    code, out, err = run_cli(monkeypatch, capsys, env, cli_args(env, fixture, "compare"),
                             stdin=json.dumps(env["request"]).encode("utf-8"))
    assert code == 0 and err == "", err
    payload = json.loads(out)
    assert payload["schema_version"] == "rf-verified-scope-comparison/1"
    assert [row["delta"]["value"] for row in payload["comparison"]["metrics"]] == [
        "3.000000", "3.000000"]

    fresh = build_env(tmp_path / "fresh")
    fresh["store"] = fresh["store"].__class__(tmp_path / "fresh" / "owner-data-2")
    payload = fx.evidence("R-OLD", source_witnesses=fresh["left"]["source_witnesses"],
                          coordinates=fresh["left"]["covered_coordinates"])
    code, out, err = run_cli(monkeypatch, capsys, fresh,
                             cli_args(fresh, fixture, "append-binding"),
                             stdin=json.dumps(payload).encode("utf-8"))
    assert code == 0 and err == "", err
    assert json.loads(out)["status"] == "appended"
    code, out, _ = run_cli(monkeypatch, capsys, fresh,
                           cli_args(fresh, fixture, "append-binding"),
                           stdin=json.dumps(payload).encode("utf-8"))
    assert code == 0 and json.loads(out)["status"] == "already_present"


def test_cli_emits_the_complete_result_without_a_byte_cap(build_env, tmp_path,
                                                          monkeypatch, capsys):
    long_text = "COMPLETE-SOURCE-EXCERPT-" * 60_000
    env = build_env(tmp_path, long_excerpt=long_text)
    fixture = tmp_path / "subjects.json"
    fx.write_subject_fixture(fixture, fx.subject_snapshot())
    code, out, err = run_cli(monkeypatch, capsys, env, cli_args(env, fixture, "compare"),
                             stdin=json.dumps(env["request"]).encode("utf-8"))
    assert code == 0 and err == "", err
    assert len(out.encode("utf-8")) > 1_000_000
    payload = json.loads(out)
    assert len(payload["comparison"]["metrics"]) == 2
    evidence = payload["comparison"]["scope_resolution"]["left_binding"]["source_witnesses"]
    assert any(row["excerpt"] == long_text for row in evidence)


def test_cli_refuses_unknown_or_malformed_request_by_name(build_env, tmp_path,
                                                          monkeypatch, capsys):
    env = build_env(tmp_path)
    fixture = tmp_path / "subjects.json"
    fx.write_subject_fixture(fixture, fx.subject_snapshot())
    code, out, err = run_cli(monkeypatch, capsys, env, cli_args(env, fixture, "compare"),
                             stdin=b'{"left_report_id":"R-OLD"}')
    assert code == 2 and out == ""
    assert json.loads(err)["error"]["code"] == "invalid_request"

    code, out, err = run_cli(monkeypatch, capsys, env, cli_args(env, fixture, "compare"),
                             stdin=b"{}" * 40_000)
    assert code == 2 and out == ""
    assert json.loads(err)["error"]["code"] == "input_too_large"


def test_read_only_cli_creates_no_data_root(build_env, tmp_path, monkeypatch, capsys):
    env = build_env(tmp_path)
    fixture = tmp_path / "subjects.json"
    fx.write_subject_fixture(fixture, fx.subject_snapshot())
    from report_catalog_scope_binding import ScopeBindingStore

    empty = ScopeBindingStore(tmp_path / "never-created")
    env["store"] = empty
    code, out, err = run_cli(monkeypatch, capsys, env,
                             cli_args(env, fixture, "get-bindings", "--report-id", "R-OLD"))
    assert code == 0 and err == "", err
    assert json.loads(out)["scope_view"]["state"] == "unavailable"
    assert not empty.path.exists()
