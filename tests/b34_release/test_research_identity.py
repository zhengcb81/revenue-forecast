"""Controlled retained-recorder fixtures; no real research or owner workspace writes."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from b34_admin.test_research_attempt import (  # noqa: E402
    fixture_run,
    native_events,
    save_events,
    sync_budget,
    identity,
    ENT,
    LISTING,
    RECORDER_SHA,
    write,
)
from test_company_wiki_source_v2 import BODY, _inputs, _candidate  # noqa: E402
from company_wiki_source_v2 import build_revenue_source_record_from_verified_read  # noqa: E402
from report_catalog import CatalogError, ReportCatalog  # noqa: E402
import report_catalog_research_identity as ri  # noqa: E402
import report_catalog_research_attempt as admission  # noqa: E402
from report_catalog_identity_resolver import (  # noqa: E402
    BridgeConfig,
    make_identity_resolver,
    IdentityBridgeError,
)

ANCHOR = "b" * 32
PROBE = "d" * 32
CANONICAL = "无锡药明康德新药开发股份有限公司"


def doc(path):
    return json.loads(path.read_text(encoding="utf-8"))


def shift_stamp(value, seconds):
    return (datetime.fromisoformat(value) + timedelta(seconds=seconds)).isoformat()


def logs(run, frame, stdout, stderr=b""):
    folder = run / "roles/executor/commands" / frame["capture_id"]
    folder.mkdir(parents=True, exist_ok=True)
    for stream, raw in [("stdout", stdout), ("stderr", stderr)]:
        path = folder / (stream + ".txt")
        path.write_bytes(raw)
        frame.update(
            {
                stream + "_artifact": str(path),
                stream + "_total_bytes": len(raw),
                stream + "_retained_bytes": len(raw),
                stream + "_truncated": False,
            }
        )


def anchored(root):
    run = fixture_run(root)
    base = native_events(run)
    anchor = deepcopy(base)
    terminal = deepcopy(base)
    for event in terminal:
        event["recorded_at"] = shift_stamp(event["recorded_at"], 20)
        data = event["data"]
        for key in ["started_at", "finished_at"]:
            if key in data:
                data[key] = shift_stamp(data[key], 20)
        data["runtime_observation"]["observed_at"] = data["started_at"]
    for event in anchor:
        event["event_id"] += "-anchor"
        event["recorded_at"] = shift_stamp(event["recorded_at"], 2)
        data = event["data"]
        data["capture_id"] = ANCHOR
        for key in ["started_at", "finished_at"]:
            if key in data:
                data[key] = shift_stamp(data[key], 2)
        data["runtime_observation"]["observed_at"] = data["started_at"]
        folder = run / "roles/executor/commands" / ANCHOR
        folder.mkdir(parents=True, exist_ok=True)
        for row in data["input_snapshots"]:
            old = Path(row["frozen_path"])
            row["frozen_path"] = str(folder / old.name)
            Path(row["frozen_path"]).write_bytes(old.read_bytes())
            row["consumed_path"] = str(folder / Path(row["consumed_path"]).name)
        data["executed_command"][4] = data["input_snapshots"][0]["consumed_path"]
    receipt_time = shift_stamp(anchor[0]["data"]["started_at"], 0.5)
    ref, receipt, manifest = deepcopy(_inputs())
    ref["document_id"] = "urn:company-wiki:document:sha256:" + ref["content_sha256"]
    ref["source_id"] = "urn:company-wiki:source:sha256:" + ref["content_sha256"]
    for block in (receipt, manifest):
        block.update(document_id=ref["document_id"], source_id=ref["source_id"])
    manifest.update(
        source_url=None,
        published_date=None,
        retrieved_at=None,
        display_name="药明康德",
        market="CN",
        security_id="603259",
        document_kind="annual_report",
        fiscal_year=2025,
        fiscal_period="FY",
    )
    receipt.update(
        schema_version="2.2",
        read_at=receipt_time,
        availability_evidence={
            "schema_version": "source-availability-evidence/1",
            "source_sha256": ref["content_sha256"],
            "available_by": "2026-11-01",
            "basis": "current_verified_open",
            "evidence_ref": "urn:fixture:read",
            "locator": "capture/read_at",
        },
    )
    candidate = _candidate(ref, manifest)
    candidate.update(resolution_outcome="reused_existing", download_events=0)
    source = build_revenue_source_record_from_verified_read(
        source_ref=ref,
        read_receipt=receipt,
        source_bytes=BODY,
        source_manifest=manifest,
        source_candidate=candidate,
        as_of_date="2026-11-01",
        source_type="regulatory_filing",
        publisher="Official issuer",
        page_or_section="1",
    )
    result = {
        "schema_version": "source-preparation-result/1",
        "source": source,
        "filing_fetch": {
            "schema_version": "2.0",
            "status": "source_candidate",
            "request_period": {
                "mode": "exact",
                "fiscal_year": 2025,
                "fiscal_period": None,
                "as_of_date": "2026-11-01",
            },
            "filing": {
                "status": "source_candidate",
                "source_ref": ref,
                "resolution_outcome": "reused_existing",
                "download_events": 0,
            },
            "calls": 2,
            "downloads": 0,
        },
        "narrative": None,
    }
    success = anchor[-1]["data"]
    success["exit_code"] = 0
    logs(run, success, json.dumps(result).encode())
    save_events(run, anchor + terminal)
    closure = doc(run / "execution/terminal.json")
    closure["closed_at"] = shift_stamp(closure["closed_at"], 20)
    write(run / "execution/terminal.json", closure)
    sync_budget(run)
    return run, result


def canonical(entity):
    result = identity(entity)
    result["display_name"] = CANONICAL
    return result


def controlled_alias(entity, query, ref, evidence, *, operation_as_of=None):
    return {
        "entity_id": entity,
        "frozen_company_label": query,
        "canonical_name": evidence["display_name"],
        "primary_source_ref": ref, "operation_as_of": operation_as_of,
    }


def bound_admit(root, run, **kwargs):
    return admission.import_research_attempt(
        ReportCatalog(root=root),
        run_id=run.name,
        entity_id=ENT,
        listing_id=LISTING,
        identity_resolver=kwargs.pop("identity_resolver", canonical),
        source_alias_resolver=kwargs.pop("source_alias_resolver", controlled_alias),
        identity_anchor_capture_id=kwargs.pop("identity_anchor_capture_id", ANCHOR),
        recorder_sha256=RECORDER_SHA,
        **kwargs,
    )


def test_prior_complete_source_keeps_unknowns_and_original_query(root_case):
    root, run, result = root_case
    before = {p: p.read_bytes() for p in run.rglob("*") if p.is_file()}
    receipt = bound_admit(root, run)
    assert receipt["registered"]["reports"] == []
    assert all(p.read_bytes() == raw for p, raw in before.items())
    seal = next((root / "artifacts/report_catalog/evidence").iterdir())
    sealed = doc(seal)
    assert sealed["company_query"] == "药明康德"
    assert sealed["source_identity_binding"]["canonical_name"] == CANONICAL
    assert (
        sealed["identity_anchor"]["primary_source_ref"]
        == result["source"]["company_wiki_trace"]["source_ref"]
    )
    assert (
        result["source"]["url"] is None and result["source"]["published_date"] is None
    )


@pytest.fixture
def root_case(tmp_path):
    run, result = anchored(tmp_path)
    return tmp_path, run, result


@pytest.mark.parametrize(
    "mutation",
    [
        "absent",
        "foreign",
        "failed",
        "hash",
        "stdout_sha",
        "scope",
        "capture",
        "read_clock",
        "download",
    ],
)
def test_anchor_counterexamples_refuse_before_catalog(root_case, mutation):
    root, run, result = root_case
    if mutation == "absent":
        with pytest.raises(CatalogError):
            bound_admit(root, run, identity_anchor_capture_id=None)
        return
    if mutation == "foreign":
        with pytest.raises(CatalogError):
            bound_admit(root, run, identity_anchor_capture_id="f" * 32)
        return
    values = native_events(run)
    data = values[1]["data"]
    if mutation == "failed":
        data["exit_code"] = 3
    elif mutation == "hash":
        data["input_snapshots"][0]["sha256"] = "0" * 64
    elif mutation == "stdout_sha":
        data["stdout_retained_bytes"] += 1
    else:
        if mutation == "scope":
            result["source"]["company_wiki_trace"]["source_manifest"][
                "display_name"
            ] = "其他公司"
        elif mutation == "capture":
            result["source"]["capture"]["snapshot_sha256"] = "0" * 64
        elif mutation == "read_clock":
            result["source"]["company_wiki_trace"]["read_receipt"]["read_at"] = (
                shift_stamp(data["finished_at"], 1)
            )
        elif mutation == "download":
            result["filing_fetch"]["downloads"] = 1
        logs(run, data, json.dumps(result).encode())
    save_events(run, values)
    sync_budget(run)
    with pytest.raises(CatalogError):
        bound_admit(root, run)
    assert not (root / "artifacts").exists()


def pin_deployment(root, run):
    values = native_events(run)
    probe_events = deepcopy(values[:2])
    probe_file = run / "execution/probe_pinned_cwp_runtime.py"
    probe_file.write_text(ri.PROBE_PROGRAM, encoding="utf-8")
    cwp = root / "cwp-code"
    ff = root / "ff-code"
    ff.mkdir()
    native = {}
    for module, filename in ri.PROBE_MODULES.items():
        path = cwp / "src/company_wiki/source_catalog" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# isolated controlled code " + filename, encoding="utf-8")
        native[module] = {
            "code_file": str(path),
            "bytes_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    for event in probe_events:
        event["event_id"] += "-probe"
        data = event["data"]
        data["capture_id"] = PROBE
        data["command"] = data["executed_command"] = [
            sys.executable,
            "-B",
            str(probe_file),
        ]
        data["input_snapshots"] = []
        event["recorded_at"] = shift_stamp(event["recorded_at"], 3)
        for key in ["started_at", "finished_at"]:
            if key in data:
                data[key] = shift_stamp(data[key], 3)
        data["runtime_observation"]["observed_at"] = data["started_at"]
    logs(run, probe_events[1]["data"], json.dumps(native).encode())
    workspace = root / "cwp-workspace"
    config = workspace / "config/source_catalog.yaml"
    config.parent.mkdir(parents=True)
    config.write_text("# controlled config", encoding="utf-8")
    for event in values[-2:]:
        event["data"]["command"] += ["--filing-fetch-root", str(ff)]
        event["data"]["executed_command"] += ["--filing-fetch-root", str(ff)]
        event["data"]["command"][
            event["data"]["command"].index("--company-wiki-catalog-config") + 1
        ] = str(config)
        event["data"]["executed_command"][
            event["data"]["executed_command"].index("--company-wiki-catalog-config") + 1
        ] = str(config)
    save_events(run, values[:2] + probe_events + values[-2:])
    sync_budget(run)
    selected = values[-1]["data"]["capture_id"]
    snapshot = {
        "schema_version": "b34-research-pinned-deployment/1",
        "capture_id": selected,
        "probe_capture_id": PROBE,
        "observed_at": shift_stamp(values[-1]["data"]["finished_at"], 0.1),
        "RF": {"source_commit": "1" * 40, "code_root": str(ROOT)},
        "filing_fetch": {"source_commit": "2" * 40, "code_root": str(ff)},
        "CWP": {
            "source_commit": "3" * 40,
            "code_root": str(cwp),
            "workspace": str(workspace),
            "catalog_config": str(config),
            "operator_environment": {"PYTHONPATH": str(cwp / "src")},
            "native_probe": native,
        },
    }
    write(run / "execution/pinned-reviewed.json", snapshot)
    closure = doc(run / "execution/terminal.json")
    closure["code_refs"] = {"RF": "1" * 40, "filing_fetch": "2" * 40, "CWP": "3" * 40}
    write(run / "execution/terminal.json", closure)
    return snapshot


def test_pinned_admission_reads_rf_owned_observations_only(root_case, monkeypatch):
    root, run, _ = root_case
    pin_deployment(root, run)
    observed_owner_roots = (root / "cwp-code", root / "cwp-workspace", root / "ff-code")
    original = Path.open

    def guarded_open(path, *args, **kwargs):
        assert not any(path.is_relative_to(external) for external in observed_owner_roots)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    bound_admit(root, run, deployment_snapshot="pinned-reviewed.json")
    assert ReportCatalog(root=root).file.exists()


def test_explicit_pinned_snapshot_preserves_wrong_historical_observation(root_case):
    root, run, _ = root_case
    pin_deployment(root, run)
    old = {
        "schema_version": "b34-research-deployment-update/1",
        "RF": {"HEAD": "9" * 40},
    }
    write(run / "execution/deployment-update-ff-reviewed.json", old)
    wrong = {
        "schema_version": "b34-research-pinned-deployment/1",
        "capture_id": "f" * 32,
    }
    write(run / "execution/deployment-cwp-pinned.json", wrong)
    before = (run / "execution/deployment-cwp-pinned.json").read_bytes()
    bound_admit(root, run, deployment_snapshot="pinned-reviewed.json")
    assert (run / "execution/deployment-cwp-pinned.json").read_bytes() == before


@pytest.mark.parametrize(
    "mutation",
    [
        "selected",
        "RF_root",
        "FF_root",
        "module_hash",
        "module_path",
        "environment",
        "probe_failed",
        "probe_program",
        "snapshot_escape",
    ],
)
def test_pinned_snapshot_counterexamples_refuse(root_case, mutation):
    root, run, _ = root_case
    pin = pin_deployment(root, run)
    if mutation == "snapshot_escape":
        with pytest.raises(CatalogError):
            bound_admit(root, run, deployment_snapshot="../pinned-reviewed.json")
        return
    if mutation == "selected":
        pin["capture_id"] = "f" * 32
    elif mutation in {"RF_root", "FF_root"}:
        pin["RF" if mutation == "RF_root" else "filing_fetch"]["code_root"] = str(root)
    elif mutation in {"module_hash", "module_path"}:
        module = next(iter(pin["CWP"]["native_probe"].values()))
        module["bytes_sha256" if mutation == "module_hash" else "code_file"] = "0" * 64
    elif mutation == "environment":
        pin["CWP"]["operator_environment"]["PYTHONPATH"] = str(root)
    elif mutation == "probe_failed":
        values = native_events(run)
        next(
            e
            for e in values
            if e["kind"] == "command_finished" and e["data"]["capture_id"] == PROBE
        )["data"]["exit_code"] = 3
        save_events(run, values)
        sync_budget(run)
    elif mutation == "probe_program":
        (run / "execution/probe_pinned_cwp_runtime.py").write_text(
            "print('fake')", encoding="utf-8"
        )
    write(run / "execution/pinned-reviewed.json", pin)
    with pytest.raises(CatalogError):
        bound_admit(root, run, deployment_snapshot="pinned-reviewed.json")
    assert not (root / "artifacts").exists()


def test_cli_has_explicit_trusted_operator_flags():
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-B",
            str(ROOT / "scripts/report_catalog_identity_cli.py"),
            "import-research-attempt",
            "--help",
        ],
        capture_output=True,
        timeout=20,
    )
    assert result.returncode == 0
    assert (
        b"--identity-anchor-capture-id" in result.stdout
        and b"--deployment-snapshot" in result.stdout
    )


@pytest.mark.parametrize("late_revoke", [False, True])
def test_real_isolated_stockwiki_public_alias_accepts_single_record_anchor(
    root_case, monkeypatch, late_revoke
):
    root, run, result = root_case
    spec = importlib.util.spec_from_file_location(
        "isolated_alias_fixture", ROOT / "tests/b34_source_alias/test_source_alias.py"
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    code = helper.controlled_code(root)
    response = helper.owner_action(
        code,
        {
            "action": "create",
            "workspace": str(root / "sw-owner"),
            "entity": ENT,
            "security": helper.SEC,
            "canonical": CANONICAL,
            "alias": "药明康德",
            "source_id": result["source"]["source_id"],
        },
    )
    listing = response["entity"]["selected_listing_id"]
    config = BridgeConfig(
        python=Path(sys.executable),
        cli=code / "dashboard_identity_bridge_cli.py",
        owner_root=code,
        sw_root=root / "sw-owner",
        timeout_seconds=20,
        max_output_bytes=262144,
    )

    def execute():
        return admission.import_research_attempt(
            ReportCatalog(root=root),
            run_id=run.name,
            entity_id=ENT,
            listing_id=listing,
            identity_resolver=make_identity_resolver(config, listing_id=listing),
            source_alias_resolver=ri.make_research_source_alias_resolver(
                config, listing_id=listing
            ),
            recorder_sha256=RECORDER_SHA,
            identity_anchor_capture_id=ANCHOR,
        )

    if late_revoke:
        import report_catalog_source_alias as alias

        proof = alias._read_proof(
            config,
            {
                "entity_id": ENT,
                "listing_id": listing,
                "as_of": datetime.now(timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z"),
            },
        )
        receipt_id = proof["owner_package"]["payload"]["verified_issuer_receipt_id"]
        original = ReportCatalog._validate_attempt_source

        def revoke_after_validation(self, attempt):
            original(self, attempt)
            assert self.file.with_name(self.file.name + ".lock").exists()
            helper.owner_action(
                code,
                {
                    "action": "revoke",
                    "workspace": str(config.sw_root),
                    "receipt_id": receipt_id,
                },
            )

        monkeypatch.setattr(
            ReportCatalog, "_validate_attempt_source", revoke_after_validation
        )
        with pytest.raises(IdentityBridgeError):
            execute()
        assert not ReportCatalog(root=root).file.exists()
        assert (
            not ReportCatalog(root=root).file.with_name("catalog.jsonl.lock").exists()
        )
    else:
        first = execute()
        assert first["registered"]["reports"] == []
        assert execute() == first


def test_final_guard_rechecks_retained_capture_after_local_validation(
    root_case, monkeypatch
):
    root, run, result = root_case
    original = ReportCatalog._validate_attempt_source

    def change_after_validation(self, attempt):
        original(self, attempt)
        (run / "roles/executor/commands" / ANCHOR / "stdout.txt").write_bytes(
            b"changed source record"
        )

    monkeypatch.setattr(
        ReportCatalog, "_validate_attempt_source", change_after_validation
    )
    with pytest.raises(CatalogError, match="changed"):
        bound_admit(root, run)
    assert not ReportCatalog(root=root).file.exists()


def test_final_guard_rechecks_retained_probe_after_last_alias_lookup(root_case):
    root, run, _ = root_case
    pin_deployment(root, run)
    calls = 0

    def moving_alias(entity, query, ref, identity, *, operation_as_of=None):
        nonlocal calls
        calls += 1
        if calls > 1:
            (run / "roles/executor/commands" / PROBE / "stdout.txt").write_bytes(b"drift")
        return controlled_alias(entity, query, ref, identity, operation_as_of=operation_as_of)

    with pytest.raises(CatalogError, match="changed"):
        bound_admit(
            root,
            run,
            deployment_snapshot="pinned-reviewed.json",
            source_alias_resolver=moving_alias,
        )
    assert not ReportCatalog(root=root).file.exists()


def test_recorder_canonical_original_path_and_raw_argv_slashes_match(root_case):
    root, run, _ = root_case
    values = native_events(run)
    for event in values:
        row = event["data"]["input_snapshots"][0]
        index = row["argument_indices"][0]
        event["data"]["command"][index] = Path(event["data"]["command"][index]).as_posix()
    save_events(run, values)
    assert bound_admit(root, run)["registered"]["reports"] == []
