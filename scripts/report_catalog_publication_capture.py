"""Verify completed and frozen publication recorder stages, without admission."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from report_catalog_common import CatalogError
from report_catalog_research_capture import (
    CAPTURE, BoundObservation, matches_capture_path, read_capture_streams, read_timestamp, sha256_bytes,
)


def require_publication(value: Any, detail: str) -> None:
    if not value:
        raise CatalogError("research_publication_invalid", detail)


def publication_object(value: Any) -> dict:
    require_publication(isinstance(value, dict), "publication field is not an object")
    return value


def publication_capture_id(value: Any) -> str:
    require_publication(isinstance(value, str) and CAPTURE.fullmatch(value), "capture ID is invalid")
    return value


def completed_capture(
    obs: BoundObservation,
    run: Path,
    cid: str,
    started: dict,
    finished: dict,
    *,
    succeeded: bool,
) -> tuple[dict, dict[str, bytes], dict]:
    publication_capture_id(cid)
    require_publication(cid in started and cid in finished, "selected capture is missing")
    start, data = started[cid], finished[cid]
    require_publication(
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
    require_publication(
        read_timestamp(data["started_at"]) <= read_timestamp(data["finished_at"]),
        "native clock is reversed",
    )
    streams, logs = read_capture_streams(obs, run, cid, data)
    if succeeded:
        require_publication(streams["stderr"] == b"", "successful stage has native error diagnostics")
    return data, streams, logs


def frozen_capture_input(
    obs: BoundObservation, run: Path, cid: str, data: dict, expected: dict[int, Path]
) -> dict[int, bytes]:
    """Bind exact original argv, consumed argv and retained input bytes."""
    command, executed = data.get("command"), data.get("executed_command")
    rows = data.get("input_snapshots")
    require_publication(
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
        row = publication_object(row)
        indices = row.get("argument_indices")
        require_publication(
            isinstance(indices, list)
            and len(indices) == 1
            and type(indices[0]) is int
            and indices[0] in expected,
            "frozen input argument is unexpected",
        )
        indices = cast(list[int], indices)
        index = indices[0]
        require_publication(
            index not in observed
            and 0 <= index < len(command)
            and matches_capture_path(command[index], expected[index])
            and matches_capture_path(row.get("original_path"), expected[index]),
            "frozen input names another artifact",
        )
        frozen = Path(row.get("frozen_path", ""))
        consumed = Path(row.get("consumed_path", ""))
        require_publication(
            frozen.is_absolute()
            and frozen.parent == folder
            and consumed.is_absolute()
            and consumed.parent == folder,
            "retained input is outside its native capture",
        )
        raw = obs.read(frozen)
        require_publication(
            type(row.get("byte_size")) is int
            and len(raw) == row["byte_size"]
            and row.get("sha256") == sha256_bytes(raw)
            and row.get("consumed_unchanged") is True
            and row.get("consumed_after_bytes") == len(raw)
            and row.get("consumed_after_sha256") == sha256_bytes(raw)
            and obs.read(expected[index]) == raw,
            "native input bytes changed",
        )
        replacement[index] = str(consumed)
        observed[index] = raw
    require_publication(
        set(observed) == set(expected) and executed == replacement,
        "executed argv differs from its frozen inputs",
    )
    return observed


def capture_entrypoint_index(command: Any, script: Path) -> int:
    require_publication(
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
        require_publication(token not in seen, "native Python flags are duplicated")
        seen.add(token)
        index += 1
        if token == "-X":
            require_publication(
                index < len(command) and command[index] == "utf8",
                "unsupported native Python flag",
            )
            index += 1
    require_publication(
        index < len(command) and matches_capture_path(command[index], script),
        "native command is not the pinned RF entry",
    )
    return index
