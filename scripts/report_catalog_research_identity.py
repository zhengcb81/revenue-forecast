"""Trusted recorder/source anchors and pinned deployment consistency for admission.

This reads retained local owner observations. It is not OS execution attestation
and does not open source originals or execute a probe or research command.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

from report_catalog import CatalogError

if TYPE_CHECKING:
    from report_catalog_research_attempt import _Observation


PROBE_MODULES = {
    "company_wiki.source_catalog.local_reconcile": "local_reconcile.py",
    "company_wiki.source_catalog.source_query_cli": "source_query_cli.py",
    "company_wiki.source_catalog.source_reader_cli": "source_reader_cli.py",
}
PROBE_PROGRAM = """from pathlib import Path
import hashlib,json
from company_wiki.source_catalog import local_reconcile, source_query_cli, source_reader_cli
print(json.dumps({m.__name__:{"code_file":str(Path(m.__file__).resolve()),"bytes_sha256":hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()} for m in (local_reconcile,source_query_cli,source_reader_cli)},ensure_ascii=False))
"""


def _require(value: Any, detail: str) -> None:
    if not value:
        raise CatalogError("research_identity_evidence_invalid", detail)


def _object(value: Any, detail: str) -> dict:
    _require(isinstance(value, dict), detail)
    return value


def _code_hash(root: Path, relative: str) -> str:
    path = root / relative
    _require(root.is_absolute() and root.is_dir(), "pinned code root is unavailable")
    current = root
    for part in Path(relative).parts:
        current /= part
        _require(
            not current.is_symlink()
            and not getattr(current, "is_junction", lambda: False)(),
            "pinned code cannot traverse links",
        )
    _require(
        path.resolve(strict=True).is_relative_to(root.resolve(strict=True))
        and path.is_file()
        and path.stat().st_size <= 8 * 1024 * 1024,
        "pinned code file is unavailable",
    )
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    _require(
        (before.st_ino, before.st_size, before.st_mtime_ns)
        == (after.st_ino, after.st_size, after.st_mtime_ns)
        and len(raw) == before.st_size,
        "pinned code changed during observation",
    )
    return hashlib.sha256(raw).hexdigest()


def _recorded_path(value: str) -> Path:
    """Compare retained deployment paths without opening the old deployment."""
    return Path(os.path.abspath(value))


def validate_pinned_deployment(
    obs: _Observation,
    run: Path,
    snapshot_path: Path,
    scope: dict,
    terminal: dict,
    started: dict,
    finished: dict,
) -> tuple[dict, dict]:
    from report_catalog_research_attempt import _capture_logs, _json, _stamp

    value = obs.document(snapshot_path)
    selected = terminal["terminal_capture_id"]
    _require(
        value.get("schema_version") == "b34-research-pinned-deployment/1"
        and value.get("capture_id") == selected
        and selected in finished,
        "pinned deployment does not select the terminal capture",
    )
    current = finished[selected]
    command = current["command"]
    _require(
        "native_command" not in value or value["native_command"] == command,
        "pinned native argv disagrees with the retained capture",
    )
    refs = {}
    blocks = {}
    for role in ("RF", "filing_fetch", "CWP"):
        block = _object(value.get(role), "pinned deployment role is missing")
        _require(
            isinstance(block.get("source_commit"), str)
            and re.fullmatch(r"[a-f0-9]{40}", block["source_commit"]),
            "pinned deployment source commit is invalid",
        )
        code_root = Path(block.get("code_root", ""))
        _require(
            code_root.is_absolute(),
            "pinned deployment code root is invalid",
        )
        refs[role] = block["source_commit"]
        blocks[role] = block
    rf = Path(blocks["RF"]["code_root"])
    _require(
        refs["RF"] == scope.get("RF_code_commit")
        and rf.resolve() == Path(scope.get("RF_code_root", "")).resolve()
        and Path(command[2 if command[1] == "-B" else 1]).resolve()
        == (rf / "scripts/source_preparation.py").resolve(),
        "pinned RF root or source ref disagrees with the actual capture",
    )
    _require(
        "--filing-fetch-root" in command,
        "pinned FF code root needs the actual operator argument",
    )
    _require(
        _recorded_path(command[command.index("--filing-fetch-root") + 1])
        == _recorded_path(blocks["filing_fetch"]["code_root"]),
        "pinned FF root disagrees with the actual capture",
    )
    cwp = blocks["CWP"]
    cwp_root = Path(cwp["code_root"])
    config = Path(cwp.get("catalog_config", ""))
    _require(
        config.is_absolute()
        and _recorded_path(cwp.get("workspace", "")) == _recorded_path(str(config)).parents[1]
        and _recorded_path(command[command.index("--company-wiki-catalog-config") + 1])
        == _recorded_path(str(config)),
        "pinned CWP workspace/config disagrees with the actual capture",
    )
    environment = _object(
        cwp.get("operator_environment"), "pinned CWP environment is missing"
    )
    _require(
        set(environment) == {"PYTHONPATH"}
        and _recorded_path(environment["PYTHONPATH"]) == _recorded_path(str(cwp_root / "src")),
        "pinned CWP code environment is invalid",
    )
    probe_id = value.get("probe_capture_id")
    _require(
        isinstance(probe_id, str) and probe_id != selected and probe_id in finished,
        "pinned native probe is missing",
    )
    assert isinstance(probe_id, str)
    probe = finished[probe_id]
    _require(
        probe.get("child_started") is True
        and probe.get("exit_code") == 0
        and probe.get("timed_out") is False
        and probe.get("output_complete") is True
        and probe.get("input_complete") is True
        and probe.get("execution_error") is None
        and probe.get("command") == started[probe_id].get("command")
        and _stamp(probe["finished_at"]) <= _stamp(current["started_at"]),
        "pinned native probe is not a prior complete success",
    )
    probe_command = probe.get("command")
    _require(
        isinstance(probe_command, list)
        and len(probe_command) == 3
        and probe_command[1] == "-B"
        and Path(probe_command[0]).name.lower()
        in {"python", "python.exe", "python3", "python3.exe"},
        "pinned probe command is unsupported",
    )
    probe_file = Path(probe_command[2])
    _require(
        probe_file.is_absolute()
        and probe_file.parent == run / "execution"
        and probe_file.name == "probe_pinned_cwp_runtime.py",
        "pinned probe is not the fixed owner observation",
    )
    _require(
        obs.read(probe_file).replace(b"\r\n", b"\n") == PROBE_PROGRAM.encode("utf-8"),
        "pinned probe program differs from the fixed observation",
    )
    raw, _ = _capture_logs(obs, run, probe_id, probe)
    _require(raw["stderr"] == b"", "pinned probe carries unexpected diagnostics")
    modules = _json(raw["stdout"])
    _require(
        set(modules) == set(PROBE_MODULES) and modules == cwp.get("native_probe"),
        "pinned native module observation disagrees",
    )
    hashes = {}
    for name, filename in PROBE_MODULES.items():
        module = _object(modules[name], "pinned module observation is invalid")
        relative = "src/company_wiki/source_catalog/" + filename
        _require(
            set(module) == {"code_file", "bytes_sha256"}
            and _recorded_path(module["code_file"]) == _recorded_path(str(cwp_root / relative))
            and isinstance(module["bytes_sha256"], str)
            and re.fullmatch(r"[a-f0-9]{64}", module["bytes_sha256"]),
            "pinned native module observation is invalid",
        )
        hashes[name] = module["bytes_sha256"]
    _require(
        _stamp(current["finished_at"])
        <= _stamp(value.get("observed_at"))
        <= _stamp(terminal["closed_at"]),
        "pinned deployment observation clock is inconsistent",
    )
    return refs, {
        "snapshot": snapshot_path.relative_to(run).as_posix(),
        "snapshot_sha256": hashlib.sha256(obs.read(snapshot_path)).hexdigest(),
        "capture_id": selected,
        "probe_capture_id": probe_id,
        "observed_module_sha256": hashes,
        "guarantee_scope": "trusted_local_observation_not_OS_execution_attestation",
    }


def successful_capture_source(
    obs: _Observation,
    run: Path,
    capture_id: str,
    *,
    metadata: dict,
    scope: dict,
    started: dict,
    finished: dict,
    terminal_capture_id: str,
    expected_script: Path,
) -> dict:
    from report_catalog_research_attempt import (
        _capture_logs,
        _capture_request,
        _json,
        _stamp,
    )
    from contracts.company_wiki_original import validate_manifest, validate_receipt, validate_ref
    from contracts.document import validate_sources

    _require(
        isinstance(capture_id, str)
        and re.fullmatch(r"[a-f0-9]{32}", capture_id)
        and capture_id in finished
        and capture_id != terminal_capture_id,
        "identity anchor is not a prior recorded capture",
    )
    data = finished[capture_id]
    _require(
        data.get("child_started") is True
        and data.get("exit_code") == 0
        and data.get("timed_out") is False
        and data.get("output_complete") is True
        and data.get("input_complete") is True
        and data.get("execution_error") is None
        and _stamp(data["finished_at"])
        <= _stamp(finished[terminal_capture_id]["started_at"]),
        "identity anchor is not an earlier complete successful source preparation",
    )
    request, snapshots = _capture_request(
        obs, run, capture_id, started[capture_id], data, expected_script
    )
    _require(
        request.get("company_query") == metadata["company_query"]
        and request.get("as_of_date") == metadata["as_of_date"],
        "identity anchor targets a foreign company or information date",
    )
    raw, logs = _capture_logs(obs, run, capture_id, data)
    _require(
        raw["stderr"] == b"",
        "successful identity anchor carries native error diagnostics",
    )
    result = _json(raw["stdout"])
    _require(
        set(result) == {"schema_version", "source", "filing_fetch", "narrative"}
        and result.get("schema_version") == "source-preparation-result/1",
        "identity anchor is not a full source-preparation result",
    )
    source = _object(result.get("source"), "identity anchor source record is missing")
    trace = _object(
        source.get("company_wiki_trace"), "identity anchor original trace is missing"
    )
    required_trace = {"source_ref", "read_receipt", "source_manifest", "source_candidate"}
    _require(
        required_trace <= set(trace) <= required_trace | {"review_observation"},
        "identity anchor original trace fields are invalid",
    )
    as_of = date.fromisoformat(metadata["as_of_date"])
    ref = validate_ref(trace["source_ref"])
    receipt = validate_receipt(trace["read_receipt"], ref)
    manifest, _ = validate_manifest(
        trace["source_manifest"],
        ref,
        as_of,
        availability_evidence=receipt.get("availability_evidence"),
        current_read_at=receipt["read_at"],
    )
    validate_sources({"sources": [source]}, as_of, require_capture=True)
    _require(
        source.get("source_type") == "regulatory_filing"
        and source.get("source_id") == ref["source_id"]
        and source.get("url") == manifest["source_url"]
        and manifest.get("display_name") == metadata["company_query"]
        and manifest.get("market") == request["market"]
        and manifest.get("document_kind") == request["document_kind"]
        and manifest.get("fiscal_year") == request["fiscal_year"]
        and manifest.get("fiscal_period") == (request.get("fiscal_period") or "FY"),
        "identity anchor source scope disagrees with its native request",
    )
    capture = _object(
        source.get("capture"), "identity anchor source capture is missing"
    )
    _require(
        capture.get("snapshot_sha256") == ref["content_sha256"]
        and capture.get("tool_call_id") == ref["source_id"] + "|" + receipt["read_at"]
        and _stamp(data["started_at"])
        <= _stamp(receipt["read_at"])
        <= _stamp(data["finished_at"]),
        "identity anchor verified read is outside its actual native capture",
    )
    filing_fetch = _object(
        result.get("filing_fetch"), "identity anchor filing-fetch result is missing"
    )
    filing = _object(
        filing_fetch.get("filing"), "identity anchor filing-fetch candidate is missing"
    )
    _require(
        filing_fetch.get("schema_version") == "2.0"
        and filing_fetch.get("status") == "source_candidate"
        and filing_fetch.get("request_period")
        == {
            "mode": request["mode"],
            "fiscal_year": request["fiscal_year"],
            "fiscal_period": request.get("fiscal_period"),
            "as_of_date": request["as_of_date"],
        }
        and type(filing_fetch.get("calls")) is int
        and filing_fetch["calls"] >= 0
        and type(filing_fetch.get("downloads")) is int
        and filing_fetch["downloads"] == 0
        and filing.get("source_ref") == ref
        and filing.get("status") == "source_candidate"
        and filing.get("resolution_outcome") == "reused_existing"
        and filing.get("download_events") == 0
        and trace["source_candidate"]
        == {"resolution_outcome": "reused_existing", "download_events": 0},
        "identity anchor reuse/period/candidate observations disagree",
    )
    return {
        "schema_version": "rf-research-source-identity-anchor/1",
        "capture_id": capture_id,
        "primary_source_ref": ref,
        "source_record_sha256": hashlib.sha256(
            json.dumps(
                source,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest(),
        "frozen_request_sha256": snapshots[0]["sha256"],
        "native_logs": logs,
        "read_receipt_version": receipt["schema_version"],
        "RF_source_commit": scope["RF_code_commit"],
    }


def make_research_source_alias_resolver(config, *, listing_id: str | None = None):
    """A trusted adapter binds replay to the validated terminal operation time."""
    from report_catalog_source_alias import make_single_source_alias_resolver

    def resolver(entity_id: str, query: str, ref: dict, identity: dict, *, operation_as_of: str) -> dict:
        return make_single_source_alias_resolver(
            config, listing_id=listing_id, operation_as_of=operation_as_of)(entity_id, query, ref, identity)

    return resolver
