"""Explicit admission of a sealed failed research attempt; not execution attestation.

Only the trusted management CLI calls this owner module. The original recorder
bytes and the frozen request are checked, never repaired or rewritten. No
research, calculator, source fetch, or foreign database runs here.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any, Callable, cast

from report_catalog_common import CatalogError, assert_pathless

from report_catalog_research_capture import (
    MAX_FILE, HEX, BoundObservation as _Observation,
    read_recorded_object as _json,
    matches_capture_path,
    read_timestamp as _stamp,
    owned_unlinked_path as _not_linked,
    sha256_bytes as _sha,
    read_recorded_events as _events,
    read_source_capture_request as _capture_request,
    read_source_failure as _logs,
    research_identifier as _identifier,
)
from report_catalog_research_seal import (
    acquire_admission_lock as _admission_lock,
    release_admission_lock as _admission_unlock,
    write_admission_seal as _publish_seal,
)

if TYPE_CHECKING:
    from report_catalog import ReportCatalog

SCHEMA = "rf-research-attempt-admission/1"
TERMINAL_SCHEMA = "rf-research-terminal/1"
TERMINAL_FIELDS = {
    "schema_version",
    "run_id",
    "attempt_id",
    "status",
    "terminal_stage",
    "terminal_capture_id",
    "reason_code",
    "closed_at",
    "research_manifest_sha256",
    "code_refs",
    "source_budget",
}


def _require(condition: Any, code: str, detail: str) -> None:
    if not condition:
        raise CatalogError(code, detail)


def _closure_input(
    catalog: ReportCatalog,
    run_id: str,
    recorder_sha256: str,
    *,
    identity_anchor_capture_id: str | None = None,
    deployment_snapshot: str | None = None,
) -> tuple[dict, dict, _Observation]:
    _require(
        isinstance(recorder_sha256, str) and HEX.fullmatch(recorder_sha256),
        "research_producer_invalid",
        "trusted recorder SHA256 is required",
    )
    root = catalog.root
    run = root / "delivery" / _identifier(run_id)
    _not_linked(root, run)
    obs = _Observation(root)
    metadata = obs.document(run / "run.json")
    scope = obs.document(run / "execution/scope.json")
    ledger_raw = obs.read(run / "execution/step-ledger.json")
    ledger = _json(ledger_raw)
    budget = obs.document(run / "execution/budget-observation.json")
    terminal = obs.document(run / "execution/terminal.json")
    _require(
        set(terminal) == TERMINAL_FIELDS
        and terminal.get("schema_version") == TERMINAL_SCHEMA
        and terminal.get("run_id") == run_id
        and terminal.get("status") == "failed",
        "research_terminal_invalid",
        "terminal closure is not the supported failed-research contract",
    )
    attempt_id = _identifier(terminal.get("attempt_id"))
    _require(
        terminal.get("terminal_stage") == "source_preparation",
        "research_stage_unsupported",
        "only terminal source-preparation failures are supported",
    )
    _require(
        metadata.get("schema_version") == "1.0"
        and metadata.get("run_id") == run_id
        and scope.get("schema_version") == "b34-research-attempt-scope/1"
        and scope.get("run_id") == run_id
        and scope.get("attempt_id") == attempt_id
        and matches_capture_path(scope.get("root"), run),
        "research_evidence_invalid",
        "run and scope identity disagree",
    )
    _require(
        ledger.get("schema_version") == "b34-research-step-ledger/1"
        and ledger.get("run_id") == run_id
        and ledger.get("state") == "FAILED"
        and ledger.get("terminal_research_failure") is True
        and ledger.get("current_stage") == "source_preparation"
        and terminal.get("research_manifest_sha256") == _sha(ledger_raw),
        "research_not_terminal",
        "research ledger has not sealed a terminal failure",
    )
    _require(
        scope.get("company_query") == metadata.get("company_query")
        and scope.get("as_of_date") == metadata.get("as_of_date")
        and isinstance(metadata.get("company_query"), str)
        and bool(metadata["company_query"]),
        "research_evidence_invalid",
        "run company or information date disagrees",
    )
    try:
        _require(
            datetime.fromisoformat(metadata["as_of_date"]).date().isoformat()
            == metadata["as_of_date"],
            "research_evidence_invalid",
            "information cutoff must be an ISO date",
        )
    except (ValueError, TypeError, KeyError) as exc:
        raise CatalogError(
            "research_evidence_invalid", "information cutoff is invalid"
        ) from exc
    _require(
        budget.get("schema_version") == "b34-research-budget/1"
        and str(budget.get("state", "")).startswith("FAILED")
        and terminal.get("source_budget") == scope.get("limits"),
        "research_not_terminal",
        "research budget is not terminal or its scope changed",
    )
    limits = scope.get("limits")
    _require(
        isinstance(limits, dict) and bool(limits),
        "research_evidence_invalid",
        "research limits are missing",
    )
    limits = cast(dict, limits)
    for observed, allowed in (
        ("new_source_downloads", "new_source_downloads"),
        ("paid_external_model_calls", "external_paid_model_calls"),
        ("web_search_requests_used", "web_search_requests"),
        ("official_body_open_requests_used", "official_body_reads"),
        ("native_capture_elapsed_seconds", "native_total_timeout_seconds"),
    ):
        a, b = budget.get(observed), limits.get(allowed)
        _require(
            type(a)
            in ({int, float} if observed == "native_capture_elapsed_seconds" else {int})
            and type(b)
            in ({int, float} if observed == "native_capture_elapsed_seconds" else {int})
            and 0 <= cast(int | float, a) <= cast(int | float, b),
            "research_budget_invalid",
            "research budget observation exceeds or lacks its limit",
        )
    refs = {"RF": scope.get("RF_code_commit")}
    pinned_path = (
        run
        / "execution"
        / (
            "deployment-cwp-pinned.json"
            if deployment_snapshot is None
            else _identifier(deployment_snapshot)
        )
    )
    pinned = deployment_snapshot is not None or pinned_path.exists()
    deployment_path = run / "execution/deployment-update-ff-reviewed.json"
    if not pinned and deployment_path.exists():
        deployment = obs.document(deployment_path)
        _require(
            deployment.get("RF", {}).get("HEAD") == refs["RF"],
            "research_evidence_invalid",
            "RF code observation changed",
        )
        refs.update(
            filing_fetch=deployment.get("filing_fetch", {}).get("HEAD"),
            CWP=deployment.get("CWP", {}).get("HEAD"),
        )
    expected_script = (
        Path(scope.get("RF_code_root", "")) / "scripts/source_preparation.py"
    )
    _require(
        expected_script.is_absolute() and expected_script.is_file(),
        "research_evidence_invalid",
        "observed RF source-preparation entry is unavailable",
    )
    _require(
        expected_script.stat().st_size <= MAX_FILE,
        "research_evidence_invalid",
        "observed stage script exceeds its bound",
    )
    _require(
        _sha(expected_script.read_bytes())
        == _sha((Path(__file__).parent / "source_preparation.py").read_bytes()),
        "research_evidence_invalid",
        "observed source-preparation code differs from the installed owner stage",
    )
    created = _stamp(metadata.get("created_at"))
    closed = _stamp(terminal.get("closed_at"))
    _require(
        created <= closed <= datetime.now(timezone.utc),
        "research_evidence_invalid",
        "research lifetime is inconsistent",
    )
    started, finished = _events(obs, run, run_id, created=created, closed=closed)
    # Independent consistency checks bind the budget summary to native events,
    # rather than trusting the summary's own elapsed/exit assertions.
    native_seconds = 0.0
    indexed_budget = {}
    for row in budget.get("recorded_captures", []):
        _require(
            isinstance(row, dict)
            and isinstance(row.get("capture_id"), str)
            and row["capture_id"] not in indexed_budget,
            "research_budget_invalid",
            "capture budget rows are invalid or duplicated",
        )
        indexed_budget[row["capture_id"]] = row
    _require(
        set(indexed_budget) == set(finished),
        "research_budget_invalid",
        "capture budget omits or invents native execution",
    )
    for key, native in finished.items():
        first = started[key]
        begin_time, end_time = (
            _stamp(native.get("started_at")),
            _stamp(native.get("finished_at")),
        )
        _require(
            first.get("started_at") == native.get("started_at")
            and created <= begin_time <= end_time <= closed,
            "research_evidence_invalid",
            "capture start and finish clocks disagree",
        )
        producer = native.get("runtime_observation")
        _require(
            isinstance(producer, dict)
            and producer == first.get("runtime_observation")
            and producer.get("capture_tool_sha256") == recorder_sha256
            and created <= _stamp(producer.get("observed_at")) <= begin_time,
            "research_producer_invalid",
            "capture does not match the trusted recorder producer",
        )
        elapsed = (end_time - begin_time).total_seconds()
        native_seconds += elapsed
        observed = indexed_budget[key]
        _require(
            type(observed.get("elapsed_seconds")) in {int, float}
            and abs(observed["elapsed_seconds"] - elapsed) <= 0.001
            and observed.get("child_started") == native.get("child_started")
            and observed.get("child_exit") == native.get("exit_code")
            and observed.get("timed_out") == native.get("timed_out")
            and observed.get("input_complete") == native.get("input_complete")
            and observed.get("output_complete") == native.get("output_complete"),
            "research_budget_invalid",
            "capture budget disagrees with native execution",
        )
        _require(
            type(native.get("timeout_seconds")) in {int, float}
            and 0
            < native["timeout_seconds"]
            <= limits.get("native_call_timeout_seconds", 0),
            "research_budget_invalid",
            "native command exceeds its configured per-call timeout",
        )
    _require(
        abs(budget["native_capture_elapsed_seconds"] - native_seconds)
        <= 0.001 * max(1, len(finished)),
        "research_budget_invalid",
        "total native elapsed time disagrees with event clocks",
    )
    selected = terminal.get("terminal_capture_id")
    _require(
        isinstance(selected, str) and selected in finished,
        "research_terminal_invalid",
        "terminal capture was not recorded",
    )
    selected = cast(str, selected)
    deployment_lineage = None
    if pinned:
        from report_catalog_research_identity import validate_pinned_deployment

        refs, deployment_lineage = validate_pinned_deployment(
            obs, run, pinned_path, scope, terminal, started, finished
        )
    _require(
        terminal.get("code_refs") == refs
        and all(
            isinstance(v, str) and re.fullmatch(r"[a-f0-9]{40}", v)
            for v in refs.values()
        ),
        "research_evidence_invalid",
        "terminal code refs do not match recorder deployment observations",
    )
    steps = ledger.get("steps")
    _require(
        isinstance(steps, list) and all(isinstance(step, dict) for step in steps),
        "research_terminal_invalid",
        "research step ledger is invalid",
    )
    steps = cast(list[dict], steps)
    selected_steps = [
        step
        for step in steps
        if isinstance(step.get("native_failure_refs"), list)
        and selected in step["native_failure_refs"]
    ]
    _require(
        bool(selected_steps)
        and all(step.get("state") == "FAILED" for step in selected_steps),
        "research_terminal_invalid",
        "terminal failure is absent from an unrecovered failed research step",
    )
    data = finished[selected]
    _require(
        data.get("child_started") is True
        and data.get("input_complete") is True
        and type(data.get("exit_code")) is int
        and data["exit_code"] != 0
        and data["exit_code"] != 2,
        "research_diagnostic_rejected",
        "terminal capture is not a real native research-stage failure",
    )
    timed_out = data.get("timed_out") is True
    _require(
        (timed_out and data.get("exit_code") == 124)
        or (
            data.get("timed_out") is False
            and data.get("output_complete") is True
            and data.get("execution_error") is None
        ),
        "research_evidence_invalid",
        "terminal capture is incomplete or contradictory",
    )
    request, _ = _capture_request(
        obs, run, selected, started[selected], data, expected_script.resolve()
    )
    _require(
        request.get("company_query") == metadata["company_query"]
        and request.get("as_of_date") == metadata["as_of_date"],
        "research_evidence_invalid",
        "captured request targets a different research company or information date",
    )
    end = _stamp(data.get("finished_at"))
    begin = _stamp(data.get("started_at"))
    if timed_out:
        warnings = data.get("warnings")
        _require(
            data.get("output_complete") is False
            and type(data.get("timeout_seconds")) in {int, float}
            and (end - begin).total_seconds() >= data["timeout_seconds"] - 0.01
            and isinstance(warnings, list)
            and all(isinstance(item, str) for item in warnings)
            and not any(
                "stream still open" in item or "capture error" in item
                for item in warnings
            ),
            "research_evidence_invalid",
            "native timeout clock or capture completeness is inconsistent",
        )
    _require(
        created <= begin <= end <= closed <= datetime.now(timezone.utc),
        "research_evidence_invalid",
        "research clocks are inconsistent",
    )
    for other, later in finished.items():
        _require(
            _stamp(later.get("finished_at")) <= closed,
            "research_not_terminal",
            "native execution continued after the alleged terminal closure",
        )
        if other == selected or _stamp(later.get("finished_at")) <= end:
            continue
        command = later.get("command", [])
        if not any(
            isinstance(v, str) and v.endswith("source_preparation.py") for v in command
        ):
            continue
        later_request, _ = _capture_request(
            obs, run, other, started[other], later, expected_script.resolve()
        )
        _require(
            later_request != request,
            "research_failure_recovered",
            "selected failure was superseded by a later same-request execution",
        )
    envelope, logs = _logs(obs, run, selected, data, request)
    if timed_out:
        reason = "source_preparation_timeout"
    else:
        assert envelope is not None
        _require(
            envelope["downloads"] == 0
            and envelope["downloads"] <= budget["new_source_downloads"]
            and envelope["downloads"] <= limits["new_source_downloads"],
            "research_budget_invalid",
            "native downloads contradict the research budget or scope",
        )
        reason = envelope["error_code"]
    _require(
        isinstance(reason, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", reason),
        "research_terminal_invalid",
        "native reason code is not a pathless identifier",
    )
    _require(
        terminal.get("reason_code") == reason,
        "research_terminal_invalid",
        "terminal reason does not match native failure evidence",
    )
    anchor = None
    if identity_anchor_capture_id is not None:
        from report_catalog_research_identity import successful_capture_source

        anchor = successful_capture_source(
            obs,
            run,
            identity_anchor_capture_id,
            metadata=metadata,
            scope=scope,
            started=started,
            finished=finished,
            terminal_capture_id=selected,
            expected_script=expected_script.resolve(),
        )
    summary = {
        "schema_version": "rf-research-attempt-seal/1",
        "run_id": run_id,
        "attempt_id": attempt_id,
        "status": "failed",
        "company_query": metadata["company_query"],
        "as_of_date": metadata["as_of_date"],
        "terminal_stage": "source_preparation",
        "capture_id": selected,
        "reason_code": reason,
        "recorder_sha256": recorder_sha256,
        "native_error_stage": None if envelope is None else envelope.get("stage"),
        "native_usage": {
            "scope": "selected_source_preparation_invocation",
            "calls": None if envelope is None else envelope["calls"],
            "downloads": None if envelope is None else envelope["downloads"],
        },
        "started_at": data["started_at"],
        "ended_at": data["finished_at"],
        "closed_at": terminal["closed_at"],
        "code_refs": refs,
        "source_budget": limits,
        "harness_LLM_usage": budget.get("harness_LLM_usage"),
        "harness_LLM_cost": budget.get("harness_LLM_cost"),
        "logs": logs,
        "guarantee_scope": "trusted_local_management_consistency_not_OS_attestation_or_durable_job",
    }
    if anchor is not None:
        summary["identity_anchor"] = anchor
    if deployment_lineage is not None:
        summary["pinned_deployment"] = deployment_lineage
    return metadata, summary, obs


def _public_receipt(line: dict, run_id: str, attempt_id: str, seal_sha: str) -> dict:
    return {
        "schema_version": SCHEMA,
        "run_id": run_id,
        "attempt_id": attempt_id,
        "status": "failed",
        "catalog_revision": line["line_sha256"],
        "evidence_sha256": seal_sha,
        "registered": {"runs": [run_id], "attempts": [attempt_id], "reports": []},
        "scope": "failed_research_attempt_only_not_report_publication",
    }


def import_research_attempt(
    catalog: ReportCatalog,
    *,
    run_id: str,
    entity_id: str,
    identity_resolver: Callable[[str], dict],
    recorder_sha256: str,
    listing_id: str | None = None,
    analysis_subject_id: str | None = None,
    identity_anchor_capture_id: str | None = None,
    deployment_snapshot: str | None = None,
    source_alias_resolver: Callable[..., dict] | None = None,
) -> dict:
    """Admit one actually terminal failed research attempt through the owner."""
    _require(
        analysis_subject_id is None,
        "research_scope_unsupported",
        "research recorder has no verified analysis-subject scope",
    )
    try:
        metadata, summary, obs = _closure_input(
            catalog,
            run_id,
            recorder_sha256,
            identity_anchor_capture_id=identity_anchor_capture_id,
            deployment_snapshot=deployment_snapshot,
        )
    except CatalogError:
        raise
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        raise CatalogError(
            "research_evidence_invalid", "research evidence has invalid typed fields"
        ) from exc
    _require(
        callable(identity_resolver),
        "identity_resolver_unavailable",
        "research import needs the trusted public resolver",
    )
    identity = identity_resolver(entity_id)
    _require(
        isinstance(identity, dict)
        and identity.get("authority") == "stockwiki"
        and identity.get("entity_id") == entity_id
        and identity.get("resolution_status") == "resolved"
        and isinstance(identity.get("display_name"), str)
        and bool(identity["display_name"])
        and isinstance(identity.get("source_revision"), str)
        and bool(identity["source_revision"])
        and isinstance(identity.get("lookup_receipt_sha256"), str)
        and HEX.fullmatch(identity["lookup_receipt_sha256"]),
        "identity_unverified",
        "research company differs from trusted canonical identity",
    )
    binding = None
    proof_as_of = _stamp(summary["closed_at"]).isoformat(timespec="seconds").replace("+00:00", "Z")
    anchor = summary.get("identity_anchor")
    if anchor is not None:
        _require(
            callable(source_alias_resolver),
            "identity_unverified",
            "research source anchor requires the trusted public source alias resolver",
        )
        assert source_alias_resolver is not None
        binding = source_alias_resolver(
            entity_id, metadata["company_query"], anchor["primary_source_ref"], identity,
            operation_as_of=proof_as_of
        )
        _require(
            isinstance(binding, dict),
            "identity_unverified",
            "source identity binding is invalid",
        )
        summary["source_identity_binding"] = binding
    else:
        _require(
            identity["display_name"] == metadata["company_query"],
            "identity_unverified",
            "research company differs from trusted canonical identity; a verified source anchor is required",
        )

    def check_freshness() -> None:
        obs.recheck()
        _require(
            identity_resolver(entity_id) == identity,
            "identity_unverified",
            "canonical identity changed before admission",
        )
        if binding is not None:
            assert source_alias_resolver is not None and anchor is not None
            _require(
                source_alias_resolver(
                    entity_id,
                    metadata["company_query"],
                    anchor["primary_source_ref"],
                    identity,
                    operation_as_of=proof_as_of,
                )
                == binding,
                "identity_unverified",
                "source identity binding changed before admission",
            )

        obs.recheck()

    summary["company"] = {
        "entity_id": entity_id,
        "listing_id": listing_id,
        "analysis_subject_id": analysis_subject_id,
    }
    summary["identity_evidence"] = identity
    summary["input_observations"] = obs.manifest()
    assert_pathless(summary)
    body = (
        json.dumps(
            summary,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    _require(
        len(body) <= MAX_FILE,
        "research_evidence_invalid",
        "sealed facts exceed their byte bound",
    )
    seal_sha = _sha(body)
    managed = (catalog.root / "artifacts/report_catalog").resolve()
    _require(
        managed.is_relative_to(catalog.root) and catalog.file.is_relative_to(managed),
        "catalog_path_forbidden",
        "research admission requires the managed owner catalog",
    )
    attempt_id = summary["attempt_id"]
    # No directory or lock is created until evidence and the initial identity lookup pass.
    obs.recheck()
    managed.mkdir(parents=True, exist_ok=True)
    lock = managed / "research-attempt-import.lock"
    fd = _admission_lock(catalog.root, lock)
    try:
        entries = catalog._entries()
        for line in entries:
            existing_runs = [
                r for r in line.get("runs", []) if r.get("run_id") == run_id
            ]
            existing_attempts = [
                a
                for a in line.get("attempts", [])
                if a.get("run_id") == run_id and a.get("attempt_id") == attempt_id
            ]
            if not existing_runs and not existing_attempts:
                continue
            _require(
                len(existing_runs) == len(existing_attempts) == 1
                and existing_attempts[0]
                .get("source_evidence", {})
                .get("artifact", {})
                .get("bytes_sha256")
                == seal_sha,
                "research_import_conflict",
                "research IDs already bind different admission evidence",
            )
            catalog.get_attempt(run_id, attempt_id)
            check_freshness()
            return _public_receipt(line, run_id, attempt_id, seal_sha)
        obs.recheck()
        _require(
            identity_resolver(entity_id) == identity,
            "identity_unverified",
            "canonical identity changed before admission",
        )
        evidence_dir = managed / "evidence"
        evidence_dir.mkdir(exist_ok=True)
        _not_linked(catalog.root, evidence_dir)
        seal = evidence_dir / ("research-attempt-" + seal_sha + ".json")
        _publish_seal(catalog.root, seal, body)
        obs.recheck()
        company = {
            "entity_id": entity_id,
            "listing_id": listing_id,
            "analysis_subject_id": analysis_subject_id,
            "resolution_status": "resolved",
            "display_name": metadata["company_query"],
        }
        run = {
            "run_id": run_id,
            "parent_run_id": None,
            "company": company,
            "source_as_of": metadata["as_of_date"],
            "created_at": metadata["created_at"],
            "status": "failed",
            "scenario_set": [],
            "reporting_currency": None,
            "model_metadata": {"reason": "research_failed_before_forecast_publication"},
            "artifact_revision": seal_sha,
            "source_snapshot_refs": [],
            "source_evidence": catalog.artifact_ref(seal),
        }
        attempt = {
            "run_id": run_id,
            "attempt_id": attempt_id,
            "status": "failed",
            "started_at": summary["started_at"],
            "ended_at": summary["ended_at"],
            "report_ids": [],
            "error_code": summary["reason_code"],
            "source_evidence": {
                "kind": "attempt_receipt_json",
                "artifact": catalog.artifact_ref(seal),
            },
        }
        receipt = catalog.add_records(
            runs=[run], attempts=[attempt], reports=[], before_append=check_freshness
        )
        return _public_receipt(
            {"line_sha256": receipt["catalog_revision"]}, run_id, attempt_id, seal_sha
        )
    finally:
        _admission_unlock(fd)
