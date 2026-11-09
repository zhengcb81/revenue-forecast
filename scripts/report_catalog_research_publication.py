"""Explicit owner admission of a reviewed research publication and native stages.

All reads are of one fixed owner run. This does not execute research, acquire
sources, trust business-supplied aliases, or attest OS execution. The trusted
operator selects an independent review by its exact bytes SHA; native, source,
registry, artifact, clock, budget, identity and append checks remain mandatory.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Callable, cast

from contracts.document import validate_sources
from publication_registry import canonical_sha256
from report_catalog import (
    CatalogError,
    ReportCatalog,
    _assert_pathless,
    _frozen_reporting_scale,
    _read_registry_file,
)
from report_catalog_research_attempt import (
    CAPTURE,
    HEX,
    _Observation,
    MAX_FILE,
    _admission_lock,
    _admission_unlock,
    _capture_logs,
    _capture_request,
    _events,
    _identifier,
    _json,
    _logs,
    _not_linked,
    _publish_seal,
    _stamp,
)
from report_catalog_research_identity import (
    successful_capture_source,
    validate_pinned_deployment,
)
from revenue_report import render_markdown

SCHEMA = "rf-research-publication-admission/1"
CLOSURE_SCHEMA = "rf-research-publication/1"
REVIEW_SCHEMA = "rf-research-publication-review/1"
CLOSURE_FIELDS = {
    "schema_version",
    "publication_version",
    "run_id",
    "parent_research_attempt_id",
    "status",
    "closed_at",
    "compute_capture_id",
    "validate_capture_id",
    "snapshot_capture_id",
    "source_stage_failure_capture_id",
    "recovery_capture_id",
    "research_manifest_sha256",
    "review_receipt_sha256",
}
REVIEW_FIELDS = {
    "schema_version",
    "publication_version",
    "run_id",
    "parent_research_attempt_id",
    "status",
    "reviewer",
    "reviewed_at",
    "report_sha256",
    "research_manifest_sha256",
    "captures",
    "coverage_acceptance",
    "artifacts",
}
ARTIFACTS = (
    "forecast/input.json",
    "forecast/forecast.json",
    "forecast/forecast.md",
    "snapshots/v1.json",
    "registry/publications.jsonl",
    "execution/step-ledger.json",
    "execution/budget-observation.json",
    "execution/scope.json",
    "roles/executor/events.jsonl",
)


def publication_layout(version: str = "v1") -> dict:
    _need(
        isinstance(version, str) and re.fullmatch(r"v[1-9][0-9]{0,2}", version),
        "publication version must be one v1..v999 basename",
    )
    forecast = "forecast" if version == "v1" else "forecast/" + version
    execution = "execution" if version == "v1" else "execution/publications/" + version
    result: dict = {
        "version": version,
        "input": forecast + "/input.json",
        "forecast": forecast + "/forecast.json",
        "markdown": forecast + "/forecast.md",
        "snapshot": "snapshots/" + version + ".json",
        "closure": execution + "/publication.json",
        "review": execution + "/publication-review.json",
    }
    result["artifacts"] = (
        result["input"],
        result["forecast"],
        result["markdown"],
        result["snapshot"],
        *ARTIFACTS[4:],
    )
    return result


def _need(value: Any, detail: str) -> None:
    if not value:
        raise CatalogError("research_publication_invalid", detail)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _object(value: Any) -> dict:
    _need(isinstance(value, dict), "publication field is not an object")
    return value


def _capture_id(value: Any) -> str:
    _need(isinstance(value, str) and CAPTURE.fullmatch(value), "capture ID is invalid")
    return value


def _equal_path(value: Any, expected: Path) -> bool:
    return (
        isinstance(value, str)
        and Path(value).is_absolute()
        and not any(part in {".", ".."} for part in re.split(r"[\\/]", value))
        and Path(value) == expected
    )


def _complete(
    obs: _Observation,
    run: Path,
    cid: str,
    started: dict,
    finished: dict,
    *,
    succeeded: bool,
) -> tuple[dict, dict[str, bytes], dict]:
    _capture_id(cid)
    _need(cid in started and cid in finished, "selected capture is missing")
    start, data = started[cid], finished[cid]
    _need(
        data.get("child_started") is True
        and data.get("input_complete") is True
        and data.get("output_complete") is True
        and data.get("input_cleanup_complete") is True
        and data.get("execution_error") is None
        and data.get("timed_out") is False
        and type(data.get("exit_code")) is int
        and ((data["exit_code"] == 0) if succeeded else data["exit_code"] not in {0, 2})
        and start.get("command") == data.get("command")
        and start.get("executed_command") == data.get("executed_command")
        and start.get("started_at") == data.get("started_at"),
        "selected native stage is incomplete or contradicts its status",
    )
    _need(
        _stamp(data["started_at"]) <= _stamp(data["finished_at"]),
        "native clock is reversed",
    )
    streams, logs = _capture_logs(obs, run, cid, data)
    if succeeded:
        _need(streams["stderr"] == b"", "successful stage has native error diagnostics")
    return data, streams, logs


def _frozen(
    obs: _Observation, run: Path, cid: str, data: dict, expected: dict[int, Path]
) -> dict[int, bytes]:
    """Bind exact original argv, consumed argv and retained input bytes."""
    command, executed = data.get("command"), data.get("executed_command")
    rows = data.get("input_snapshots")
    _need(
        isinstance(command, list)
        and isinstance(executed, list)
        and isinstance(rows, list)
        and len(rows) == len(expected),
        "native frozen inputs are incomplete",
    )
    command = cast(list[str], command)
    executed = cast(list[str], executed)
    rows = cast(list[dict], rows)
    folder = run / "roles/executor/commands" / cid
    replacement = list(command)
    observed: dict[int, bytes] = {}
    for row in rows:
        row = _object(row)
        indices = row.get("argument_indices")
        _need(
            isinstance(indices, list)
            and len(indices) == 1
            and type(indices[0]) is int
            and indices[0] in expected,
            "frozen input argument is unexpected",
        )
        indices = cast(list[int], indices)
        index = indices[0]
        _need(
            index not in observed
            and 0 <= index < len(command)
            and _equal_path(command[index], expected[index])
            and _equal_path(row.get("original_path"), expected[index]),
            "frozen input names another artifact",
        )
        frozen = Path(row.get("frozen_path", ""))
        consumed = Path(row.get("consumed_path", ""))
        _need(
            frozen.is_absolute()
            and frozen.parent == folder
            and consumed.is_absolute()
            and consumed.parent == folder,
            "retained input is outside its native capture",
        )
        raw = obs.read(frozen)
        _need(
            type(row.get("byte_size")) is int
            and len(raw) == row["byte_size"]
            and row.get("sha256") == _sha(raw)
            and row.get("consumed_unchanged") is True
            and row.get("consumed_after_bytes") == len(raw)
            and row.get("consumed_after_sha256") == _sha(raw)
            and obs.read(expected[index]) == raw,
            "native input bytes changed",
        )
        replacement[index] = str(consumed)
        observed[index] = raw
    _need(
        set(observed) == set(expected) and executed == replacement,
        "executed argv differs from its frozen inputs",
    )
    return observed


def _script_index(command: Any, script: Path) -> int:
    _need(
        isinstance(command, list)
        and 2 <= len(command) <= 32
        and all(isinstance(x, str) and "\x00" not in x for x in command)
        and Path(command[0]).name.lower()
        in {"python", "python.exe", "python3", "python3.exe"},
        "native command is not the fixed Python stage",
    )
    index = 1
    seen = set()
    while index < len(command) and command[index] in {"-B", "-u", "-X"}:
        token = command[index]
        _need(token not in seen, "native Python flags are duplicated")
        seen.add(token)
        index += 1
        if token == "-X":
            _need(
                index < len(command) and command[index] == "utf8",
                "unsupported native Python flag",
            )
            index += 1
    _need(
        index < len(command) and _equal_path(command[index], script),
        "native command is not the pinned RF entry",
    )
    return index


def _forecast_stage(
    obs: _Observation,
    run: Path,
    cid: str,
    kind: str,
    scope: dict,
    started: dict,
    finished: dict,
    layout: dict,
) -> tuple[dict, dict]:
    data, streams, logs = _complete(obs, run, cid, started, finished, succeeded=True)
    script = "revenue_backtest.py" if kind == "snapshot" else "revenue_forecast.py"
    command = data["command"]
    index = _script_index(command, Path(scope["RF_code_root"]) / "scripts" / script)
    position = index + (2 if kind == "snapshot" else 1)
    if kind == "snapshot":
        _need(command[index + 1] == "create", "snapshot stage is not create")
    _need(
        position < len(command)
        and _equal_path(command[position], run / layout["input"]),
        "RF stage input is not the fixed publication input",
    )
    options = command[position + 1 :]
    parsed = {}
    cursor = 0
    while cursor < len(options):
        flag = options[cursor]
        _need(flag not in parsed, "native RF options are duplicated")
        if flag in {"--validate-only", "--verbose"}:
            parsed[flag] = True
            cursor += 1
        else:
            _need(
                flag in {"--output", "--markdown", "--version"}
                and cursor + 1 < len(options),
                "native RF option is unsupported",
            )
            parsed[flag] = options[cursor + 1]
            cursor += 2
    if kind == "validate":
        _need(
            set(parsed) in ({"--validate-only"}, {"--validate-only", "--verbose"})
            and streams["stdout"].strip() == b"valid",
            "input/output validation did not succeed",
        )
    elif kind == "compute":
        _need(
            set(parsed) == {"--output", "--markdown"}
            and _equal_path(parsed["--output"], run / layout["forecast"])
            and _equal_path(parsed["--markdown"], run / layout["markdown"])
            and streams["stdout"].strip() == b"",
            "compute output arguments are incompatible",
        )
    else:
        _need(
            set(parsed) == {"--version", "--output"}
            and isinstance(parsed["--version"], str)
            and bool(parsed["--version"])
            and _equal_path(parsed["--output"], run / layout["snapshot"])
            and streams["stdout"].strip() == b"",
            "snapshot arguments are incompatible",
        )
    _frozen(obs, run, cid, data, {position: run / layout["input"]})
    return data, logs


def _budget_and_events(
    obs: _Observation,
    run: Path,
    metadata: dict,
    scope: dict,
    closure: dict,
    recorder_sha: str,
) -> tuple[dict, dict, dict]:
    _need(
        isinstance(recorder_sha, str) and HEX.fullmatch(recorder_sha),
        "trusted recorder SHA is required",
    )
    _need(
        metadata.get("schema_version") == "1.0"
        and metadata.get("run_id") == run.name
        and scope.get("schema_version") == "b34-research-attempt-scope/1"
        and scope.get("run_id") == run.name
        and scope.get("root") == run.as_posix()
        and scope.get("company_query") == metadata.get("company_query")
        and scope.get("as_of_date") == metadata.get("as_of_date")
        and scope.get("attempt_id") == closure["parent_research_attempt_id"],
        "research run/scope identity disagrees",
    )
    _need(
        isinstance(metadata.get("company_query"), str)
        and bool(metadata["company_query"])
        and isinstance(scope.get("RF_code_commit"), str)
        and re.fullmatch(r"[a-f0-9]{40}", scope["RF_code_commit"])
        and Path(scope.get("RF_code_root", "")).is_absolute(),
        "research scope is incomplete",
    )
    created, closed = _stamp(metadata["created_at"]), _stamp(closure["closed_at"])
    _need(
        created <= closed <= datetime.now(timezone.utc) + timedelta(seconds=5),
        "publication lifetime is invalid",
    )
    started, finished = _events(obs, run, run.name, created=created, closed=closed)
    budget = obs.document(run / "execution/budget-observation.json")
    limits = _object(scope.get("limits"))
    _need(
        budget.get("schema_version") == "b34-research-budget/1"
        and budget.get("state") in {"SUCCEEDED", "SUCCEEDED_WITH_DECLARED_GAPS"}
        and budget.get("native_total_budget_seconds")
        == limits.get("native_total_timeout_seconds")
        and budget.get("per_capture_budget_seconds")
        == limits.get("native_call_timeout_seconds"),
        "research budget has not closed successfully",
    )
    for field, limit in (
        ("new_source_downloads", "new_source_downloads"),
        ("paid_external_model_calls", "external_paid_model_calls"),
        ("web_search_requests_used", "web_search_requests"),
        ("official_body_open_requests_used", "official_body_reads"),
    ):
        _need(
            type(budget.get(field)) is int
            and type(limits.get(limit)) is int
            and 0 <= budget[field] <= limits[limit],
            "research resource counters are invalid",
        )
    _need(
        budget["new_source_downloads"] == 0
        and budget["paid_external_model_calls"] == 0,
        "this admission version requires the declared zero-download/provider scope",
    )
    rows = budget.get("recorded_captures")
    _need(
        isinstance(rows, list) and all(isinstance(x, dict) for x in rows),
        "native budget rows are invalid",
    )
    rows = cast(list[dict], rows)
    indexed = {x.get("capture_id"): x for x in rows}
    _need(
        len(indexed) == len(rows) and set(indexed) == set(finished),
        "native budget omits or duplicates captures",
    )
    total = 0.0
    for cid, frame in finished.items():
        start = started[cid]
        producer = _object(frame.get("runtime_observation"))
        _need(
            start.get("started_at") == frame.get("started_at")
            and producer == start.get("runtime_observation")
            and producer.get("capture_tool_sha256") == recorder_sha
            and created
            <= _stamp(producer.get("observed_at"))
            <= _stamp(frame["started_at"]),
            "native capture start or producer observation differs between frames or falls outside its lifetime",
        )
        seconds = (
            _stamp(frame["finished_at"]) - _stamp(frame["started_at"])
        ).total_seconds()
        timeout = frame.get("timeout_seconds")
        _need(
            type(timeout) in {int, float}
            and math.isfinite(timeout)
            and 0 < timeout <= limits["native_call_timeout_seconds"]
            and start.get("timeout_seconds") == timeout
            and 0 <= seconds <= timeout + 1,
            "native clock or per-call resource bound disagrees",
        )
        row = indexed[cid]
        _need(
            type(row.get("elapsed_seconds")) in {int, float}
            and math.isfinite(row["elapsed_seconds"])
            and abs(row["elapsed_seconds"] - seconds) <= 0.001,
            "native elapsed budget is not the recorded clock",
        )
        for target, source in (
            ("child_started", "child_started"),
            ("child_exit", "exit_code"),
            ("timed_out", "timed_out"),
            ("input_complete", "input_complete"),
            ("output_complete", "output_complete"),
        ):
            _need(
                type(row.get(target)) is type(frame.get(source))
                and row.get(target) == frame.get(source),
                "native budget status disagrees with its capture",
            )
        total += seconds
    measured = budget.get("native_capture_elapsed_seconds")
    _need(
        type(measured) in {int, float}
        and math.isfinite(cast(float, measured))
        and abs(total - cast(float, measured)) <= 0.001 * max(1, len(finished))
        and total <= limits["native_total_timeout_seconds"],
        "aggregate native budget disagrees",
    )
    return started, finished, budget


def _review(
    obs: _Observation,
    run: Path,
    metadata: dict,
    scope: dict,
    closure: dict,
    ledger: dict,
    receipt_sha: str,
    finished: dict,
    layout: dict,
) -> dict:
    _need(
        isinstance(receipt_sha, str) and HEX.fullmatch(receipt_sha),
        "trusted review receipt SHA is required",
    )
    raw = obs.read(run / layout["review"])
    review = _json(raw)
    _need(
        _sha(raw) == receipt_sha == closure.get("review_receipt_sha256")
        and set(review) == REVIEW_FIELDS
        and review.get("schema_version") == REVIEW_SCHEMA
        and review.get("publication_version") == layout["version"]
        and review.get("run_id") == run.name
        and review.get("status") == "accepted"
        and review.get("parent_research_attempt_id") == scope["attempt_id"]
        and review.get("research_manifest_sha256")
        == closure["research_manifest_sha256"]
        and isinstance(review.get("report_sha256"), str)
        and HEX.fullmatch(review["report_sha256"])
        and isinstance(review.get("reviewer"), str)
        and bool(review["reviewer"].strip())
        and review["reviewer"] != scope.get("harness"),
        "independent review receipt does not bind this publication",
    )
    reviewed = _stamp(review["reviewed_at"])
    _need(
        max(_stamp(x["finished_at"]) for x in finished.values())
        <= reviewed
        <= _stamp(closure["closed_at"]),
        "review predates native completion or postdates closure",
    )
    quality = review.get("coverage_acceptance")
    _need(
        isinstance(quality, dict)
        and set(quality) == {"research_workflow", "source_capture", "model_quality"}
        and quality["research_workflow"] is True
        and quality["source_capture"] is True
        and quality["model_quality"]
        in {"conditional_scenarios", "full_operating_research"},
        "complete workflow/source/model review is missing",
    )
    expected_captures = {
        "compute": closure["compute_capture_id"],
        "validate": closure["validate_capture_id"],
        "snapshot": closure["snapshot_capture_id"],
        "source_failure": closure["source_stage_failure_capture_id"],
        "recovery": closure["recovery_capture_id"],
    }
    _need(
        review.get("captures") == expected_captures,
        "review selects different native stages",
    )
    artifacts = _object(review.get("artifacts"))
    _need(
        set(artifacts) == set(layout["artifacts"]), "review artifact set is incomplete"
    )
    for relative in layout["artifacts"]:
        bound = _object(artifacts[relative])
        value = obs.read(run / relative)
        _need(
            set(bound) == {"sha256", "byte_size"}
            and type(bound.get("byte_size")) is int
            and bound["byte_size"] == len(value)
            and bound.get("sha256") == _sha(value),
            "review artifact bytes changed",
        )
    _need(
        ledger.get("state") == "SUCCEEDED"
        and ledger.get("terminal_research_failure") is False
        and isinstance(ledger.get("steps"), list)
        and 0 < len(ledger["steps"]) <= 64
        and all(isinstance(step, dict) for step in ledger["steps"]),
        "research workflow has not completed",
    )
    return {
        "receipt_sha256": receipt_sha,
        "reviewer": review["reviewer"],
        "reviewed_at": review["reviewed_at"],
        "report_sha256": review["report_sha256"],
        "coverage_acceptance": quality,
    }


def _recovery(
    obs: _Observation,
    run: Path,
    closure: dict,
    source_input: dict,
    anchor: dict,
    started: dict,
    finished: dict,
) -> dict:
    cid = _capture_id(closure["recovery_capture_id"])
    data, streams, logs = _complete(obs, run, cid, started, finished, succeeded=True)
    command = data["command"]
    index = _script_index(command, run / "execution/build_live_release_source.py")
    fixed = {
        "--web-body": run / "execution/web-capture-q3-2026/source.markdown",
        "--web-response": run / "execution/web-capture-q3-2026/tool-response.json",
        "--web-observation": run
        / "execution/web-capture-q3-2026/acquisition-observation.json",
        "--annual-source": run / "execution/annual2025-source-record.json",
        "--output": run / "execution/company-release-q3-2026-source.json",
    }
    _need(
        len(command[index + 1 :]) == 2 * len(fixed),
        "source recovery command is not the retained producer",
    )
    frozen = {}
    for flag, path in fixed.items():
        _need(
            command.count(flag) == 1, "source recovery option is missing or duplicated"
        )
        position = command.index(flag) + 1
        _need(
            position < len(command) and _equal_path(command[position], path),
            "source recovery targets another artifact",
        )
        if flag != "--output":
            frozen[position] = path
    _frozen(obs, run, cid, data, frozen)
    obs.read(
        run / "execution/build_live_release_source.py"
    )  # retained only, never executed as authority
    body = obs.read(fixed["--web-body"])
    transport = obs.read(fixed["--web-response"])
    response = _json(transport)
    observation = obs.document(fixed["--web-observation"])
    event = obs.document(run / "execution/company-release-capture-event.json")
    source = obs.document(fixed["--output"])
    result = _json(streams["stdout"])
    annual = obs.document(fixed["--annual-source"])
    _need(
        canonical_sha256(annual) == anchor["source_record_sha256"],
        "recovery names a different annual identity anchor",
    )
    _need(
        isinstance(response.get("results"), list)
        and len(response["results"]) == 1
        and response.get("failed_results") == []
        and isinstance(response["results"][0], dict),
        "official web capture is not a complete successful tool response",
    )
    page = response["results"][0]
    _need(
        isinstance(page.get("raw_content"), str)
        and page["raw_content"].encode("utf-8") == body
        and source.get("source_type") == "company_release"
        and source.get("url") == page.get("url")
        and source.get("title") == page.get("title"),
        "official source does not bind the captured page",
    )
    capture = _object(source.get("capture"))
    host = _object(capture.get("host_receipt"))
    _need(
        set(event)
        == {
            "tool",
            "request_id",
            "request",
            "response_artifact_sha256",
            "retrieved_markdown_sha256",
            "recorded_at",
            "raw_artifact_kind",
        }
        and event["response_artifact_sha256"] == _sha(transport)
        and event["retrieved_markdown_sha256"] == _sha(body)
        and event["request_id"]
        == observation.get("request_id")
        == response.get("request_id")
        == capture.get("tool_call_id")
        and event["tool"] == observation.get("tool") == capture.get("tool_name")
        and event["request"] == observation.get("request")
        and _object(event["request"]).get("query_omitted") is True
        and event["request"].get("urls") == [source["url"]]
        and event["request"].get("format") == "markdown"
        and event["raw_artifact_kind"]
        == "tool-returned complete markdown; not raw HTML"
        and capture.get("snapshot_sha256") == _sha(body)
        and host.get("event_sha256") == canonical_sha256(event)
        and host.get("timestamp") == event["recorded_at"]
        and _stamp(event["recorded_at"]) <= _stamp(data["started_at"]),
        "web source event, body, transport or receipt disagree",
    )
    sources = source_input.get("sources")
    _need(
        isinstance(sources, list)
        and len(sources) == 2
        and {canonical_sha256(x) for x in sources}
        == {canonical_sha256(annual), canonical_sha256(source)},
        "published input does not consume the validated annual and official web sources",
    )
    validate_sources(
        {"sources": sources},
        datetime.fromisoformat(source_input["as_of_date"]).date(),
        require_capture=True,
    )
    _need(
        result.get("status") == "source_record_validated"
        and result.get("source") == source
        and result.get("sources_validated")
        == [annual["source_id"], source["source_id"]]
        and result.get("body_bytes") == len(body)
        and result.get("transport_bytes") == len(transport),
        "recovery native result disagrees with the actual source",
    )
    _need(
        any(
            source["source_id"] in p.get("source_ids", [])
            for p in source_input.get("parameters", [])
        ),
        "new official source is unused in the published model",
    )
    return {
        "capture_id": cid,
        "source_id": source["source_id"],
        "snapshot_sha256": _sha(body),
        "transport_sha256": _sha(transport),
        "capture_event_sha256": canonical_sha256(event),
        "source_record_sha256": canonical_sha256(source),
        "native_logs": logs,
        "attestation": "as_declared_in_source_no_OS_execution_claim",
    }


def _prepare(
    catalog: ReportCatalog,
    run_id: str,
    recorder_sha: str,
    review_sha: str,
    anchor_id: str,
    deployment_snapshot: str,
    failed_id: str | None,
    publication_version: str,
    source_evidence: str | None = None,
) -> tuple[dict, dict, dict, dict, list, _Observation]:
    layout = publication_layout(publication_version)
    root = catalog.root
    _need(root.is_absolute() and root.is_dir(), "publication owner root is unavailable")
    run = root / "delivery" / _identifier(run_id)
    _not_linked(root, run)
    _need(
        not (run / "execution/terminal.json").exists(),
        "a whole-failed terminal cannot be relabelled as successful research",
    )
    obs = _Observation(root)
    metadata = obs.document(run / "run.json")
    scope = obs.document(run / "execution/scope.json")
    closure = obs.document(run / layout["closure"])
    _need(
        set(closure) == CLOSURE_FIELDS
        and closure.get("schema_version") == CLOSURE_SCHEMA
        and closure.get("publication_version") == publication_version
        and closure.get("run_id") == run_id
        and closure.get("status") == "succeeded"
        and closure.get("source_stage_failure_capture_id") == failed_id,
        "publication closure is not the selected successful research",
    )
    ids = [
        _capture_id(closure[k])
        for k in (
            "compute_capture_id",
            "validate_capture_id",
            "snapshot_capture_id",
            "recovery_capture_id",
        )
    ]
    _need(
        len(set(ids)) == len(ids), "publication stages must be distinct actual captures"
    )
    ledger_raw = obs.read(run / "execution/step-ledger.json")
    ledger = _json(ledger_raw)
    _need(
        closure.get("research_manifest_sha256") == _sha(ledger_raw)
        and ledger.get("schema_version") == "b34-research-step-ledger/1"
        and ledger.get("run_id") == run_id,
        "research ledger is not the frozen publication ledger",
    )
    started, finished, budget = _budget_and_events(
        obs, run, metadata, scope, closure, recorder_sha
    )
    review = _review(
        obs, run, metadata, scope, closure, ledger, review_sha, finished, layout
    )
    compute, compute_logs = _forecast_stage(
        obs,
        run,
        closure["compute_capture_id"],
        "compute",
        scope,
        started,
        finished,
        layout,
    )
    validation, validation_logs = _forecast_stage(
        obs,
        run,
        closure["validate_capture_id"],
        "validate",
        scope,
        started,
        finished,
        layout,
    )
    snapshot_stage, snapshot_logs = _forecast_stage(
        obs,
        run,
        closure["snapshot_capture_id"],
        "snapshot",
        scope,
        started,
        finished,
        layout,
    )
    _need(
        _stamp(validation["finished_at"]) <= _stamp(compute["started_at"])
        and _stamp(compute["finished_at"]) <= _stamp(snapshot_stage["started_at"]),
        "validation, compute and snapshot stages are out of order",
    )
    source_input = obs.document(run / layout["input"])
    snapshot_argv = snapshot_stage["command"]
    _need(
        snapshot_argv[snapshot_argv.index("--version") + 1]
        == source_input.get("forecast_version"),
        "snapshot native version differs from the frozen input",
    )
    result = obs.document(run / layout["forecast"])
    snapshot = obs.document(run / layout["snapshot"])
    _need(
        source_input.get("company_name")
        == metadata["company_query"]
        == result.get("company_name")
        and source_input.get("as_of_date")
        == metadata["as_of_date"]
        == result.get("as_of_date")
        and canonical_sha256(source_input) == result.get("input_sha256")
        and result.get("forecast_years") == scope.get("target_forecast_years")
        and result.get("currency") == scope.get("currency"),
        "frozen forecast identity, horizon or input anchor disagrees",
    )
    _need(
        ledger.get("result_report")
        == {
            "input_sha256": result["input_sha256"],
            "result_sha256": result["result_sha256"],
            "snapshot_id": snapshot.get("snapshot_id"),
        },
        "successful workflow does not name this immutable forecast and snapshot",
    )
    _need(
        obs.read(run / layout["markdown"]) == render_markdown(result).encode("utf-8"),
        "Markdown is not the owner's rendering of the frozen forecast",
    )
    registry_path = run / "registry/publications.jsonl"
    obs.read(registry_path)
    registry = _read_registry_file(registry_path)

    def matches(entry: dict, kind: str, frame: dict) -> bool:
        return (
            entry.get("artifact_type") == kind
            and entry.get("input_sha256") == result["input_sha256"]
            and entry.get("result_sha256")
            == (
                snapshot["forecast_result_sha256"]
                if kind == "snapshot"
                else result["result_sha256"]
            )
            and entry.get("schema_version") == result.get("schema_version")
            and entry.get("engine_version") == result.get("engine_version")
            and _stamp(frame["started_at"])
            <= _stamp(entry.get("registered_at"))
            <= _stamp(frame["finished_at"])
        )

    forecasts = [
        x
        for x in registry
        if matches(x, "forecast", compute) and x.get("validation_status") == "validated"
    ]
    snapshots = [
        x
        for x in registry
        if matches(x, "snapshot", snapshot_stage)
        and x.get("artifact_id") == snapshot.get("snapshot_id")
    ]
    _need(
        len(forecasts) == 1 and len(snapshots) == 1,
        "formal forecast/snapshot registry publication is missing or ambiguous",
    )
    expected_script = Path(scope["RF_code_root"]) / "scripts/source_preparation.py"
    anchor = successful_capture_source(
        obs,
        run,
        _capture_id(anchor_id),
        metadata=metadata,
        scope=scope,
        started=started,
        finished=finished,
        terminal_capture_id=closure["compute_capture_id"],
        expected_script=expected_script.resolve(),
    )
    if source_evidence is None:
        recovery = _recovery(obs, run, closure, source_input, anchor, started, finished)
    else:
        from report_catalog_research_publication_sources import validate_source_evidence

        recovery = validate_source_evidence(
            obs, run, closure, source_input, anchor, started, finished,
            scope=scope, layout=layout, manifest_name=source_evidence,
        )
    _need(
        _stamp(finished[closure["recovery_capture_id"]]["finished_at"])
        <= _stamp(validation["started_at"]),
        "model validation predates its actual alternative source capture",
    )
    _need(
        isinstance(deployment_snapshot, str)
        and re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.json", deployment_snapshot
        ),
        "one trusted deployment snapshot basename is required",
    )
    pin_path = run / "execution" / deployment_snapshot
    pin = obs.document(pin_path)
    pin_id = _capture_id(pin.get("capture_id"))
    _need(
        pin_id in finished and pin_id in started,
        "selected deployment capture is missing",
    )
    pin_data = finished[pin_id]
    pin_request, _ = _capture_request(
        obs, run, pin_id, started[pin_id], pin_data, expected_script.resolve()
    )
    _need(
        pin_request.get("company_query") == metadata["company_query"]
        and pin_request.get("as_of_date") == metadata["as_of_date"],
        "pinned source execution targets another research",
    )
    code_refs, deployment = validate_pinned_deployment(
        obs,
        run,
        pin_path,
        scope,
        {"terminal_capture_id": pin_id, "closed_at": closure["closed_at"]},
        started,
        finished,
    )
    stage_failure = None
    if failed_id is not None:
        _need(
            _capture_id(failed_id) == pin_id,
            "failed source stage does not use the selected verified deployment",
        )
        failed, _, failed_logs = _complete(
            obs, run, failed_id, started, finished, succeeded=False
        )
        envelope, _ = _logs(obs, run, failed_id, failed, pin_request)
        _need(
            envelope is not None and envelope.get("downloads") == 0,
            "failed source stage usage is unknown",
        )
        assert envelope is not None
        cause = envelope.get("source_failure_reason") or _object(
            envelope.get("upstream_cause")
        ).get("code")
        _need(
            isinstance(cause, str) and re.fullmatch(r"[a-z0-9_]{1,128}", cause),
            "source stage has no bounded native reason",
        )
        _need(
            _stamp(failed["finished_at"])
            <= _stamp(finished[closure["recovery_capture_id"]]["started_at"]),
            "alternative source was not a later recovery from this failed stage",
        )
        stage_failure = {
            "attempt_id": failed_id,
            "status": "failed",
            "stage": "source_preparation",
            "started_at": failed["started_at"],
            "ended_at": failed["finished_at"],
            "error_code": "source_preparation." + cast(str, cause),
            "native_usage": {
                "calls": envelope["calls"],
                "downloads": envelope["downloads"],
            },
            "native_logs": failed_logs,
        }
    company = {
        "entity_id": "PENDING",
        "listing_id": None,
        "analysis_subject_id": None,
        "resolution_status": "resolved",
        "display_name": metadata["company_query"],
    }
    report_id = "rf-" + canonical_sha256(
        {
            "input_sha256": result["input_sha256"],
            "result_sha256": result["result_sha256"],
            "bytes_sha256": _sha(obs.read(run / layout["forecast"])),
        }
    )
    report = {
        "report_id": report_id,
        "run_id": run_id,
        "attempt_id": closure["compute_capture_id"],
        "company": company,
        "artifact_kind": "revenue_forecast",
        "artifact_revision": result["forecast_version"],
        "input_sha256": result["input_sha256"],
        "result_sha256": result["result_sha256"],
        "created_at": forecasts[0]["registered_at"],
        "status": "validated",
        "schema_version": result["schema_version"],
        "engine_version": result["engine_version"],
        "information_as_of": result["as_of_date"],
        "forecast_horizon": f"{min(result['forecast_years'])}-{max(result['forecast_years'])}",
        "supersedes_report_id": None,
        "missing_reason": None,
        "reporting_currency": result["currency"],
        "reporting_scale": _frozen_reporting_scale(result),
        "forecast_artifact": catalog.artifact_ref(run / layout["forecast"]),
        "input_artifact": catalog.artifact_ref(run / layout["input"]),
        "markdown_artifact": catalog.artifact_ref(run / layout["markdown"]),
        "snapshot_artifact": catalog.artifact_ref(run / layout["snapshot"]),
        "snapshot_id": snapshot["snapshot_id"],
    }
    # The original strong engine/output/snapshot checks remain the authority.
    catalog._validate_report_artifact(report)
    stages = ([] if stage_failure is None else [stage_failure]) + [
        {
            "attempt_id": closure["compute_capture_id"],
            "status": "succeeded",
            "stage": "forecast_compute",
            "started_at": compute["started_at"],
            "ended_at": compute["finished_at"],
            "error_code": None,
            "native_logs": compute_logs,
        }
    ]
    summary = {
        "schema_version": SCHEMA,
        "publication_version": publication_version,
        "run_id": run_id,
        "parent_research_attempt_id": closure["parent_research_attempt_id"],
        "status": "succeeded",
        "closed_at": closure["closed_at"],
        "company_query": metadata["company_query"],
        "as_of_date": metadata["as_of_date"],
        "recorder_sha256": recorder_sha,
        "review": review,
        "report_id": report_id,
        "identity_anchor": anchor,
        "source_recovery": recovery,
        "native_stages": stages,
        "validation_capture": {
            "capture_id": closure["validate_capture_id"],
            "native_logs": validation_logs,
        },
        "snapshot_capture": {
            "capture_id": closure["snapshot_capture_id"],
            "native_logs": snapshot_logs,
        },
        "code_refs": code_refs,
        "pinned_deployment": deployment,
        "harness_LLM_usage": budget.get("harness_LLM_usage"),
        "harness_LLM_cost": budget.get("harness_LLM_cost"),
        "guarantee_scope": "trusted_local_reviewed_management_consistency_not_OS_attestation_or_durable_job",
    }
    return metadata, summary, report, scope, stages, obs


def import_research_publication(
    catalog: ReportCatalog,
    *,
    run_id: str,
    entity_id: str,
    identity_resolver: Callable[[str], dict],
    recorder_sha256: str,
    review_receipt_sha256: str,
    identity_anchor_capture_id: str,
    deployment_snapshot: str,
    source_alias_resolver: Callable[..., dict],
    listing_id: str | None = None,
    analysis_subject_id: str | None = None,
    source_stage_failure_capture_id: str | None = None,
    publication_version: str = "v1",
    source_evidence: str | None = None,
) -> dict:
    """Register a reviewed genuine research result, never execute it here."""
    _need(
        analysis_subject_id is None,
        "research publication has no verified analysis-subject scope",
    )
    try:
        metadata, summary, report, scope, stages, obs = _prepare(
            catalog,
            run_id,
            recorder_sha256,
            review_receipt_sha256,
            identity_anchor_capture_id,
            deployment_snapshot,
            source_stage_failure_capture_id,
            publication_version,
            source_evidence,
        )
    except CatalogError:
        raise
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        RecursionError,
        IndexError,
    ) as exc:
        raise CatalogError(
            "research_publication_invalid",
            "publication evidence has invalid typed fields",
        ) from exc
    _need(
        callable(identity_resolver) and callable(source_alias_resolver),
        "trusted identity/source alias adapters are required",
    )
    identity = identity_resolver(entity_id)
    _need(
        isinstance(identity, dict)
        and identity.get("authority") == "stockwiki"
        and identity.get("entity_id") == entity_id
        and identity.get("resolution_status") == "resolved"
        and isinstance(identity.get("source_revision"), str)
        and bool(identity["source_revision"])
        and isinstance(identity.get("lookup_receipt_sha256"), str)
        and HEX.fullmatch(identity["lookup_receipt_sha256"]),
        "trusted canonical identity is not resolved",
    )
    proof_time = (
        _stamp(summary["closed_at"])
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    ref = summary["identity_anchor"]["primary_source_ref"]
    binding = source_alias_resolver(
        entity_id, metadata["company_query"], ref, identity, operation_as_of=proof_time
    )
    _need(isinstance(binding, dict), "trusted source identity binding is unavailable")
    company = {
        "entity_id": entity_id,
        "listing_id": listing_id,
        "analysis_subject_id": None,
        "resolution_status": "resolved",
        "display_name": metadata["company_query"],
    }
    report["company"] = company
    summary.update(
        company={
            k: company[k] for k in ("entity_id", "listing_id", "analysis_subject_id")
        },
        identity_evidence=identity,
        source_identity_binding=binding,
        input_observations=obs.manifest(),
    )
    _assert_pathless(summary)
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
    _need(len(body) <= MAX_FILE, "publication sealed facts exceed their byte bound")
    seal_sha = _sha(body)
    managed = (catalog.root / "artifacts/report_catalog").resolve()
    _need(
        managed.is_relative_to(catalog.root) and catalog.file.is_relative_to(managed),
        "publication requires the managed owner catalog",
    )
    for parent in (
        catalog.root / "artifacts",
        catalog.root / "artifacts/report_catalog",
    ):
        if parent.exists() or parent.is_symlink():
            _not_linked(catalog.root, parent)

    def freshness() -> None:
        obs.recheck()
        if source_evidence is not None:
            from report_catalog_research_publication_sources import recheck_native_modules

            recheck_native_modules(scope, summary["source_recovery"]["native_modules"])
        _need(
            identity_resolver(entity_id) == identity,
            "canonical identity changed before append",
        )
        _need(
            source_alias_resolver(
                entity_id,
                metadata["company_query"],
                ref,
                identity,
                operation_as_of=proof_time,
            )
            == binding,
            "source identity changed before append",
        )
        obs.recheck()

    freshness()
    managed.mkdir(parents=True, exist_ok=True)
    _not_linked(catalog.root, managed)
    descriptor = _admission_lock(
        catalog.root, managed / "research-publication-import.lock"
    )
    try:
        old_runs, old_attempts, old_reports, _ = catalog._index()
        if run_id in old_runs:
            _need(
                old_runs[run_id].get("artifact_revision") == seal_sha
                and report["report_id"] in old_reports
                and old_reports[report["report_id"]] == report
                and all(
                    (run_id, stage["attempt_id"]) in old_attempts for stage in stages
                ),
                "immutable publication IDs already name different evidence",
            )
            catalog.get_report(report["report_id"])
            freshness()
            return {
                "schema_version": SCHEMA,
                "run_id": run_id,
                "report_id": report["report_id"],
                "status": "succeeded",
                "evidence_sha256": seal_sha,
                "catalog_revision": catalog._index()[3],
                "registered": {"runs": [], "attempts": [], "reports": []},
                "replayed": True,
            }
        _need(
            report["report_id"] not in old_reports,
            "stable report ID already belongs to a different run",
        )
        evidence = managed / "evidence"
        evidence.mkdir(exist_ok=True)
        _not_linked(catalog.root, evidence)
        seal = evidence / ("research-publication-" + seal_sha + ".json")
        _publish_seal(catalog.root, seal, body)
        attempts = []
        native_items = []
        for stage in stages:
            sid = stage["attempt_id"]
            recovered = stage["stage"] == "source_preparation"
            receipt = {
                "schema_version": "rf-native-stage-receipt/1",
                "run_id": run_id,
                "attempt_id": sid,
                "status": stage["status"],
                "stage": stage["stage"],
                "publication_evidence_sha256": seal_sha,
            }
            raw = (
                json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
            ).encode()
            stage_seal = evidence / ("research-stage-" + _sha(raw) + ".json")
            _publish_seal(catalog.root, stage_seal, raw)
            attempts.append(
                {
                    "run_id": run_id,
                    "attempt_id": sid,
                    "status": stage["status"],
                    "started_at": stage["started_at"],
                    "ended_at": stage["ended_at"],
                    "report_ids": [] if recovered else [report["report_id"]],
                    "error_code": stage["error_code"],
                    "source_evidence": {
                        "kind": "attempt_receipt_json",
                        "artifact": catalog.artifact_ref(stage_seal),
                    },
                }
            )
            native_items.append(
                {
                    "attempt_id": sid,
                    "stage": stage["stage"],
                    "recovery_status": "recovered_by_alternative_official_source"
                    if recovered
                    else None,
                    "recovery_capture_id": summary["source_recovery"]["capture_id"]
                    if recovered
                    else None,
                }
            )
        run_record = {
            "run_id": run_id,
            "parent_run_id": None,
            "company": company,
            "source_as_of": metadata["as_of_date"],
            "created_at": metadata["created_at"],
            "status": "succeeded",
            "scenario_set": ["low", "base", "high"],
            "reporting_currency": report["reporting_currency"],
            "model_metadata": {
                "engine_version": report["engine_version"],
                "research_package": "B34-reviewed-research",
                "research_quality": summary["review"]["coverage_acceptance"][
                    "model_quality"
                ],
                "native_attempts": {
                    "schema_version": "rf-native-attempts/1",
                    "parent_research_attempt_id": summary["parent_research_attempt_id"],
                    "items": native_items,
                },
            },
            "artifact_revision": seal_sha,
            "source_snapshot_refs": [ref],
            "source_evidence": catalog.artifact_ref(seal),
        }
        receipt = catalog.add_records(
            runs=[run_record],
            attempts=attempts,
            reports=[report],
            before_append=freshness,
        )
        return {
            "schema_version": SCHEMA,
            "run_id": run_id,
            "report_id": report["report_id"],
            "status": "succeeded",
            "evidence_sha256": seal_sha,
            "catalog_revision": receipt["catalog_revision"],
            "registered": {
                "runs": [run_id],
                "attempts": [x["attempt_id"] for x in attempts],
                "reports": [report["report_id"]],
            },
            "replayed": False,
        }
    finally:
        _admission_unlock(descriptor)
