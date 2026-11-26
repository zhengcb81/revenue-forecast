"""Read immutable recorder evidence for RF's reports and admission services."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
from typing import Any, cast

from filing_upstream_cause import STAGES, validated_filing_fetch_failure
from report_catalog_common import CatalogError, require as _require

MAX_FILE = 8 * 1024 * 1024
MAX_EVENTS = 512
MAX_OBSERVATION_BYTES = 32 * 1024 * 1024
HEX = re.compile(r"[a-f0-9]{64}")
CAPTURE = re.compile(r"[a-f0-9]{32}")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


def research_identifier(value: Any) -> str:
    _require(
        isinstance(value, str) and bool(_ID.fullmatch(value)) and value not in {".", ".."},
        "research_input_invalid", "research identifier is invalid",
    )
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def matches_capture_path(value: Any, expected: Path) -> bool:
    """Compare an absolute recorded path using the host filesystem's path rules."""
    return (
        isinstance(value, str)
        and Path(value).is_absolute()
        and not any(part in {".", ".."} for part in re.split(r"[\\/]", value))
        and Path(value) == expected
    )


def read_recorded_object(raw: bytes) -> dict:
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


def read_timestamp(value: Any) -> datetime:
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


def owned_unlinked_path(root: Path, path: Path) -> Path:
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


class BoundObservation:
    def __init__(self, root: Path):
        self.root = root
        self.files: dict[Path, tuple[bytes, tuple[int, int, int]]] = {}

    def read(self, path: Path) -> bytes:
        resolved = owned_unlinked_path(self.root, path)
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
        owned_unlinked_path(self.root, path)
        previous = self.files.get(path)
        _require(
            previous is None or previous[0] == raw,
            "research_evidence_changed",
            "research evidence changed between observations",
        )
        self.files[path] = (raw, key(after))
        return raw

    def document(self, path: Path) -> dict:
        return read_recorded_object(self.read(path))

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
                "sha256": sha256_bytes(raw),
            }
            for p, (raw, _) in sorted(self.files.items(), key=lambda pair: str(pair[0]))
        ]


def read_recorded_events(
    obs: BoundObservation, run: Path, run_id: str, *, created: datetime, closed: datetime
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
        event = read_recorded_object(line)
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
        recorded = read_timestamp(event.get("recorded_at"))
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
                read_timestamp(data.get("started_at")) <= recorded,
                "research_evidence_invalid",
                "recorder start header precedes its capture start",
            )
            start_headers[capture_id] = recorded
        else:
            _require(
                start_headers[capture_id]
                <= read_timestamp(data.get("finished_at"))
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


def _request_origin(obs: BoundObservation, run: Path, value: Any) -> Path:
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
    owned_unlinked_path(obs.root, existing)
    resolved = original.resolve()
    _require(resolved.is_relative_to(boundary.resolve()), "research_path_forbidden",
             "research request escapes its fixed request scope")
    return resolved


def read_source_capture_request(
    obs: BoundObservation,
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
    owned_unlinked_path(obs.root, directory)
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
        and row.get("sha256") == sha256_bytes(raw)
        and row.get("consumed_unchanged") is True
        and row.get("consumed_after_bytes") == len(raw)
        and row.get("consumed_after_sha256") == sha256_bytes(raw),
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
    request = read_recorded_object(raw)
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


def read_capture_streams(
    obs: BoundObservation, run: Path, capture_id: str, data: dict
) -> tuple[dict[str, bytes], dict]:
    summary = {}
    streams = {}
    for stream in ("stdout", "stderr"):
        path = run / "roles/executor/commands" / capture_id / (stream + ".txt")
        _require(
            matches_capture_path(data.get(stream + "_artifact"), path),
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
        summary[stream] = {"bytes": len(raw), "sha256": sha256_bytes(raw)}
        streams[stream] = raw
    return streams, summary


def read_source_failure(
    obs: BoundObservation, run: Path, capture_id: str, data: dict, request: dict
) -> tuple[dict | None, dict]:
    streams, summary = read_capture_streams(obs, run, capture_id, data)
    stderr = streams["stderr"]
    if data.get("timed_out") is True:
        return None, summary
    envelope = read_recorded_object(stderr)
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
