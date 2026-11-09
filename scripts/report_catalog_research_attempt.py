"""Explicit admission of a sealed failed research attempt; not execution attestation.

Only the trusted management CLI calls this owner module. The original recorder
bytes and the frozen request are checked, never repaired or rewritten. No
research, calculator, source fetch, or foreign database runs here.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any, Callable, cast

from owner_file_lock import OwnerFileLock
from report_catalog import CatalogError, ReportCatalog, _assert_pathless
from filing_upstream_cause import STAGES, validated_filing_fetch_failure

SCHEMA = "rf-research-attempt-admission/1"
TERMINAL_SCHEMA = "rf-research-terminal/1"
MAX_FILE = 8 * 1024 * 1024
MAX_EVENTS = 512
MAX_OBSERVATION_BYTES = 32 * 1024 * 1024
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
HEX = re.compile(r"[a-f0-9]{64}")
CAPTURE = re.compile(r"[a-f0-9]{32}")
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


def _identifier(value: Any) -> str:
    _require(
        isinstance(value, str)
        and bool(ID.fullmatch(value))
        and value not in {".", ".."},
        "research_input_invalid",
        "research identifier is invalid",
    )
    return value


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json(raw: bytes) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(_):
        raise ValueError("non-finite JSON")

    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant
        )
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise CatalogError(
            "research_evidence_invalid", "research evidence must be strict UTF-8 JSON"
        ) from exc
    _require(
        isinstance(value, dict),
        "research_evidence_invalid",
        "research evidence must be an object",
    )
    pending = [(value, 0)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        _require(
            count <= 100_000 and depth <= 64,
            "research_evidence_invalid",
            "research JSON exceeds its structure bound",
        )
        if isinstance(item, str):
            try:
                item.encode("utf-8", errors="strict")
            except UnicodeError as exc:
                raise CatalogError(
                    "research_evidence_invalid",
                    "research JSON text is not valid Unicode",
                ) from exc
        if isinstance(item, float):
            _require(
                math.isfinite(item),
                "research_evidence_invalid",
                "research JSON number is not finite",
            )
        if isinstance(item, dict):
            pending.extend(
                (entry, depth + 1) for pair in item.items() for entry in pair
            )
        elif isinstance(item, list):
            pending.extend((entry, depth + 1) for entry in item)
    return value


def _stamp(value: Any) -> datetime:
    try:
        _require(
            isinstance(value, str),
            "research_evidence_invalid",
            "timestamp must be text",
        )
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        _require(
            result.tzinfo is not None,
            "research_evidence_invalid",
            "timestamp must include timezone",
        )
        return result.astimezone(timezone.utc)
    except (ValueError, TypeError) as exc:
        raise CatalogError("research_evidence_invalid", "timestamp is invalid") from exc


def _not_linked(root: Path, path: Path) -> Path:
    """Check every existing component before resolving the file or directory."""
    _require(
        path.is_absolute() and path.is_relative_to(root),
        "research_path_forbidden",
        "research artifact is outside its owner root",
    )
    current = root
    try:
        for part in path.relative_to(root).parts:
            current = current / part
            info = current.lstat()
            _require(
                not stat.S_ISLNK(info.st_mode)
                and not (
                    getattr(info, "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
                ),
                "research_path_forbidden",
                "research artifact cannot traverse a link",
            )
        resolved = path.resolve(strict=True)
    except CatalogError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise CatalogError(
            "research_evidence_unavailable", "research artifact is unavailable"
        ) from exc
    _require(
        resolved.is_relative_to(root),
        "research_path_forbidden",
        "research artifact escapes its root",
    )
    return resolved


class _Observation:
    def __init__(self, root: Path):
        self.root = root
        self.files: dict[Path, tuple[bytes, tuple[int, int, int]]] = {}

    def read(self, path: Path) -> bytes:
        resolved = _not_linked(self.root, path)
        try:
            before = resolved.stat()
            total = sum(
                len(value[0]) for key, value in self.files.items() if key != path
            )
            _require(
                total + before.st_size <= MAX_OBSERVATION_BYTES,
                "research_evidence_invalid",
                "research evidence exceeds its aggregate byte bound",
            )
            _require(
                stat.S_ISREG(before.st_mode) and before.st_size <= MAX_FILE,
                "research_evidence_invalid",
                "research evidence exceeds its file bound",
            )
            with resolved.open("rb") as handle:
                opened = os.fstat(handle.fileno())
                raw = handle.read(MAX_FILE + 1)
                after_open = os.fstat(handle.fileno())
            after = resolved.stat()
        except OSError as exc:
            raise CatalogError(
                "research_evidence_unavailable", "research evidence cannot be read"
            ) from exc

        def key(info):
            return (info.st_ino, info.st_size, info.st_mtime_ns)

        _require(
            key(before) == key(opened) == key(after_open) == key(after)
            and len(raw) == before.st_size,
            "research_evidence_changed",
            "research evidence changed while reading",
        )
        _not_linked(self.root, path)
        previous = self.files.get(path)
        _require(
            previous is None or previous[0] == raw,
            "research_evidence_changed",
            "research evidence changed between observations",
        )
        self.files[path] = (raw, key(after))
        return raw

    def document(self, path: Path) -> dict:
        return _json(self.read(path))

    def recheck(self) -> None:
        for path, (expected, _) in list(self.files.items()):
            _require(
                self.read(path) == expected,
                "research_evidence_changed",
                "research evidence changed before admission",
            )

    def manifest(self) -> list[dict]:
        return [
            {
                "artifact": p.relative_to(self.root).as_posix(),
                "bytes": len(raw),
                "sha256": _sha(raw),
            }
            for p, (raw, _) in sorted(self.files.items(), key=lambda pair: str(pair[0]))
        ]


def _events(
    obs: _Observation, run: Path, run_id: str, *, created: datetime, closed: datetime
) -> tuple[dict, dict]:
    raw = obs.read(run / "roles/executor/events.jsonl")
    lines = raw.splitlines()
    _require(
        0 < len(lines) <= MAX_EVENTS,
        "research_evidence_invalid",
        "research event count is out of bounds",
    )
    started: dict[str, dict] = {}
    finished: dict[str, dict] = {}
    ids: set[str] = set()
    start_headers: dict[str, datetime] = {}
    for line in lines:
        event = _json(line)
        _require(
            event.get("schema_version") == "1.0"
            and event.get("run_id") == run_id
            and event.get("role") == "executor"
            and isinstance(event.get("data"), dict),
            "research_evidence_invalid",
            "recorder event identity is invalid",
        )
        event_id = event.get("event_id")
        _require(
            isinstance(event_id, str) and event_id not in ids,
            "research_evidence_invalid",
            "recorder event ID is invalid or duplicated",
        )
        ids.add(cast(str, event_id))
        recorded = _stamp(event.get("recorded_at"))
        _require(
            created <= recorded <= closed,
            "research_evidence_invalid",
            "recorder header clock is outside the research lifetime",
        )
        kind = event.get("kind")
        if kind not in {"command_started", "command_finished"}:
            continue
        data = event["data"]
        capture_id = data.get("capture_id")
        _require(
            isinstance(capture_id, str) and CAPTURE.fullmatch(capture_id),
            "research_evidence_invalid",
            "capture ID is invalid",
        )
        mapping = started if kind == "command_started" else finished
        _require(
            capture_id not in mapping,
            "research_evidence_invalid",
            "capture event is duplicated",
        )
        if kind == "command_finished":
            _require(
                capture_id in started,
                "research_evidence_invalid",
                "capture ended before it started",
            )
        if kind == "command_started":
            _require(
                _stamp(data.get("started_at")) <= recorded,
                "research_evidence_invalid",
                "recorder start header precedes its capture start",
            )
            start_headers[capture_id] = recorded
        else:
            _require(
                start_headers[capture_id]
                <= _stamp(data.get("finished_at"))
                <= recorded,
                "research_evidence_invalid",
                "recorder headers disagree with the capture lifetime",
            )
        mapping[capture_id] = data
    _require(
        set(started) == set(finished),
        "research_not_terminal",
        "research still has an unfinished native command",
    )
    return started, finished


def _command(data: dict, expected_script: Path) -> tuple[list[str], int]:
    command = data.get("command")
    _require(
        isinstance(command, list) and all(isinstance(v, str) for v in command),
        "research_evidence_invalid",
        "capture command must be an argv",
    )
    command = cast(list[str], command)
    _require(
        len(command) >= 3
        and Path(command[0]).name.lower()
        in {"python", "python.exe", "python3", "python3.exe"},
        "research_stage_unsupported",
        "capture must invoke the fixed RF source-preparation stage",
    )
    index = 2 if command[1] == "-B" else 1
    _require(
        Path(command[index]).is_absolute()
        and Path(command[index]).resolve() == expected_script,
        "research_stage_unsupported",
        "capture is not the fixed RF source-preparation stage",
    )
    allowed = {
        "--request-file",
        "--company-wiki-config",
        "--filing-fetch-root",
        "--company-wiki-catalog-config",
        "--source-reader-receipt-version",
        "--timeout-seconds",
    }
    seen, i = set(), index + 1
    while i < len(command):
        flag = command[i]
        _require(
            flag not in seen,
            "research_diagnostic_rejected",
            "stage options cannot repeat",
        )
        seen.add(flag)
        if flag == "--result-envelope":
            i += 1
            continue
        _require(
            flag in allowed
            and i + 1 < len(command)
            and not command[i + 1].startswith("--"),
            "research_diagnostic_rejected",
            "capture uses a diagnostic or unsupported invocation",
        )
        i += 2
    _require(
        {
            "--request-file",
            "--result-envelope",
            "--company-wiki-config",
            "--company-wiki-catalog-config",
        }.issubset(seen),
        "research_diagnostic_rejected",
        "stage invocation is incomplete",
    )
    return command, command.index("--request-file") + 1


def _request_origin(obs: _Observation, run: Path, value: Any) -> Path:
    """Check raw traversal/reparse boundaries before canonical equivalence.

    Frozen bytes remain authoritative; a removed original leaf is allowed,
    while every existing path component must remain inside the owner scope.
    """
    _require(isinstance(value, str), "research_path_forbidden", "request origin must be a path")
    original = Path(value)
    boundary = run / "execution/requests"
    _require(original.is_absolute() and original.is_relative_to(boundary)
             and ".." not in original.parts,
             "research_path_forbidden", "research request must belong to this run")
    existing = original
    while True:
        try:
            existing.lstat()
            break
        except FileNotFoundError:
            _require(existing != boundary, "research_evidence_unavailable", "request scope is unavailable")
            existing = existing.parent
        except OSError as exc:
            raise CatalogError("research_evidence_unavailable", "request origin is unavailable") from exc
    _not_linked(obs.root, existing)
    resolved = original.resolve()
    _require(resolved.is_relative_to(boundary.resolve()), "research_path_forbidden",
             "research request escapes its fixed request scope")
    return resolved


def _capture_request(
    obs: _Observation,
    run: Path,
    capture_id: str,
    start: dict,
    finish: dict,
    expected_script: Path,
) -> tuple[dict, list[dict]]:
    command, argument = _command(finish, expected_script)
    _require(
        start.get("command") == command
        and start.get("executed_command") == finish.get("executed_command"),
        "research_evidence_invalid",
        "capture command changed between start and finish",
    )
    directory = run / "roles/executor/commands" / capture_id
    _not_linked(obs.root, directory)
    rows = finish.get("input_snapshots")
    _require(
        isinstance(rows, list) and len(rows) == 1 and isinstance(rows[0], dict),
        "research_evidence_invalid",
        "stage needs its one frozen request",
    )
    rows = cast(list[dict], rows)
    row = rows[0]
    command_origin = _request_origin(obs, run, command[argument])
    recorder_origin = _request_origin(obs, run, row.get("original_path"))
    _require(
        row.get("argument_indices") == [argument] and recorder_origin == command_origin,
        "research_evidence_invalid",
        "frozen request does not bind the executed argument",
    )
    frozen = Path(row.get("frozen_path", ""))
    _require(
        frozen.is_absolute() and frozen.parent == directory,
        "research_path_forbidden",
        "frozen request must belong to this capture",
    )
    raw = obs.read(frozen)
    _require(
        type(row.get("byte_size")) is int
        and row["byte_size"] == len(raw)
        and row.get("sha256") == _sha(raw)
        and row.get("consumed_unchanged") is True
        and row.get("consumed_after_bytes") == len(raw)
        and row.get("consumed_after_sha256") == _sha(raw),
        "research_evidence_invalid",
        "frozen request hash or consumed-byte observation disagrees",
    )
    consumed = Path(row.get("consumed_path", ""))
    _require(
        consumed.is_absolute() and consumed.parent == directory,
        "research_path_forbidden",
        "executed request must belong to this capture",
    )
    expected = list(command)
    expected[argument] = str(consumed)
    _require(
        finish.get("executed_command") == expected
        and finish.get("input_complete") is True
        and finish.get("input_cleanup_complete") is True,
        "research_evidence_invalid",
        "capture did not consume its verified private request",
    )
    request = _json(raw)
    _require(
        request.get("schema_version") == "2.0"
        and request.get("filing_intent") == "reuse_only"
        and request.get("mode") == "exact"
        and request.get("market") in {"CN", "HK", "US"},
        "research_diagnostic_rejected",
        "source-preparation request is not a bounded research request",
    )
    kind = request.get("document_kind")
    period = request.get("fiscal_period")
    year = request.get("fiscal_year")
    _require(
        type(year) is int
        and 1900 <= year <= 2200
        and (
            (kind == "annual_report" and period is None)
            or (kind == "semi_annual_report" and period in {"H1", "H2"})
            or (kind == "quarterly_report" and period in {"Q1", "Q2", "Q3", "Q4"})
        ),
        "research_diagnostic_rejected",
        "stage request has an invalid or unsupported filing period",
    )
    return request, rows


def _capture_logs(
    obs: _Observation, run: Path, capture_id: str, data: dict
) -> tuple[dict[str, bytes], dict]:
    summary = {}
    streams = {}
    for stream in ("stdout", "stderr"):
        path = run / "roles/executor/commands" / capture_id / (stream + ".txt")
        _require(
            data.get(stream + "_artifact") == str(path),
            "research_path_forbidden",
            "native log does not belong to this capture",
        )
        raw = obs.read(path)
        _require(
            data.get(stream + "_truncated") is False
            and type(data.get(stream + "_retained_bytes")) is int
            and type(data.get(stream + "_total_bytes")) is int
            and data.get(stream + "_total_bytes")
            == data.get(stream + "_retained_bytes")
            == len(raw),
            "research_evidence_invalid",
            "native log is truncated or its byte length disagrees",
        )
        summary[stream] = {"bytes": len(raw), "sha256": _sha(raw)}
        streams[stream] = raw
    return streams, summary


def _logs(
    obs: _Observation, run: Path, capture_id: str, data: dict, request: dict
) -> tuple[dict | None, dict]:
    streams, summary = _capture_logs(obs, run, capture_id, data)
    stderr = streams["stderr"]
    if data.get("timed_out") is True:
        return None, summary
    envelope = _json(stderr)
    _require(
        envelope.get("error_code") == "upstream"
        and isinstance(envelope.get("stage"), str)
        and envelope["stage"] in STAGES,
        "research_diagnostic_rejected",
        "stage failure lacks a structured research-stage native error",
    )
    diagnostic = json.dumps(envelope, ensure_ascii=False).lower()
    _require(
        not any(
            word in diagnostic
            for word in (
                "config_error",
                "invalid_request",
                "usage:",
                "unrecognized arguments",
                "invalid_config",
                "bad_request",
                "request_error",
                "provider_not_configured",
                "invalid_budget",
                "config is unavailable",
                "config must be a file",
                "requires company_wiki_catalog_config",
            )
        ),
        "research_diagnostic_rejected",
        "a configuration or invocation diagnostic is not a research failure",
    )
    # These are per-invocation producer observations, not model-call counts.
    # An absent or contradictory counter cannot support a zero-side-effect claim.
    for metric in ("calls", "downloads"):
        _require(
            type(envelope.get(metric)) is int and envelope[metric] >= 0,
            "research_budget_invalid",
            "native stage usage is missing or invalid",
        )
    if "filing_fetch_result" in envelope:
        nested = validated_filing_fetch_failure(envelope["filing_fetch_result"])
        _require(
            nested is not None
            and all(nested.get(key) == envelope[key] for key in ("calls", "downloads"))
            and nested.get("request_period")
            == {
                "mode": request["mode"],
                "fiscal_year": request["fiscal_year"],
                "fiscal_period": request.get("fiscal_period"),
                "as_of_date": request["as_of_date"],
            },
            "research_budget_invalid",
            "native stage usage disagrees with its complete filing-fetch result",
        )
    return envelope, summary


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
        and scope.get("root") == str(run).replace("\\", "/"),
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


def _admission_lock(root: Path, path: Path) -> OwnerFileLock:
    """Hold an owner admission lock apart from the catalog append lock."""
    if path.exists():
        _not_linked(root, path)
    lock = OwnerFileLock(path)
    try:
        if not lock.acquire():
            raise CatalogError("catalog_busy", "another research admission is active")
        _not_linked(root, path)
    except OSError as exc:
        lock.release()
        raise CatalogError("catalog_unavailable", "research admission lock is unavailable") from exc
    except BaseException:
        lock.release()
        raise
    return lock


def _admission_unlock(lock: OwnerFileLock) -> None:
    lock.release()


def _publish_seal(root: Path, seal: Path, body: bytes) -> None:
    """Publish complete immutable bytes, never a partially written final name."""
    if seal.exists():
        with _not_linked(root, seal).open("rb") as existing:
            preserved = existing.read(len(body) + 1)
        _require(
            preserved == body,
            "research_import_conflict",
            "sealed admission bytes disagree",
        )
        return
    descriptor, temporary = tempfile.mkstemp(
        prefix=".research-admission-", dir=seal.parent
    )
    staged = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        _not_linked(root, seal.parent)
        try:
            os.link(staged, seal)
        except FileExistsError:
            _require(
                _not_linked(root, seal).read_bytes() == body,
                "research_import_conflict",
                "sealed admission bytes disagree",
            )
    except OSError as exc:
        raise CatalogError(
            "catalog_unavailable", "sealed research evidence cannot be published"
        ) from exc
    finally:
        staged.unlink(missing_ok=True)


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
