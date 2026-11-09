"""Actual RF management CLI and a StockWiki protocol double on isolated synthetic data."""

import importlib.util
import json
import os
import subprocess
import sys

from .fixtures import ROOT, ANCHOR, ENT, ReportCatalog, doc, raw_json


def test_two_management_processes_replay_then_current_stock_revocation_refuses(
    case_factory,
):
    case = case_factory(real_recorder=True, version="v2")
    spec = importlib.util.spec_from_file_location(
        "publication_isolated_stock_fixture",
        ROOT / "tests/b34_source_alias/test_source_alias.py",
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    helper.REF = doc(case["run"] / "forecast/v2/input.json")["sources"][0][
        "company_wiki_trace"
    ]["source_ref"]
    code = helper.controlled_code(case["root"])
    config, listing, _ = helper._native(case["root"], code)
    config_path = case["root"] / "operator-bridge.json"
    config_path.write_bytes(
        raw_json(
            {
                "python": str(config.python),
                "cli": str(config.cli),
                "owner_root": str(config.owner_root),
                "sw_root": str(config.sw_root),
                "timeout_seconds": 20,
                "max_output_bytes": 262144,
            }
        )
    )
    # Existing managed-directory marker is deployment setup, not registration.
    (case["root"] / "artifacts/report_catalog").mkdir(parents=True)
    args = [
        sys.executable,
        "-X",
        "utf8",
        "-B",
        str(ROOT / "scripts/report_catalog_identity_cli.py"),
        "--owner-root",
        str(case["root"]),
        "import-research-publication",
        "--config",
        str(config_path),
        "--entity-id",
        ENT,
        "--listing-id",
        listing,
        "--run-id",
        case["run"].name,
        "--recorder-sha256",
        case["recorder_sha"],
        "--review-receipt-sha256",
        case["review_sha"],
        "--identity-anchor-capture-id",
        ANCHOR,
        "--deployment-snapshot",
        "pinned-reviewed.json",
        "--source-stage-failure-capture-id",
        case["failed_id"],
        "--publication-version",
        "v2",
    ]

    def execute():
        return subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            timeout=90,
            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
        )

    first = execute()
    assert first.returncode == 0, first.stderr.decode("utf-8")
    result = json.loads(first.stdout)
    catalog = ReportCatalog(root=case["root"])
    before = catalog.file.read_bytes()
    second = execute()
    assert second.returncode == 0, second.stderr.decode("utf-8")
    replay = json.loads(second.stdout)
    assert replay["replayed"] and replay["report_id"] == result["report_id"]
    assert (
        replay["catalog_revision"] == result["catalog_revision"]
        and catalog.file.read_bytes() == before
    )
    stored = catalog._index()[0][case["run"].name]
    seal = catalog._read_json(stored["source_evidence"])
    proof = seal["source_identity_binding"]
    helper.owner_action(
        code,
        {
            "action": "revoke",
            "workspace": str(config.sw_root),
            "receipt_id": proof["verified_issuer_receipt_id"],
        },
    )
    revoked = execute()
    assert revoked.returncode == 2
    assert json.loads(revoked.stderr)["error_code"] == "identity_not_resolved"
    assert catalog.file.read_bytes() == before
