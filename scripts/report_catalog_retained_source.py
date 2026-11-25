"""Verify the retained response bytes used by publication and source readback."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
import re
from typing import Protocol, cast

from publication_registry import canonical_sha256
from report_catalog_common import require


EVENT_KIND = "retained_tool_response_raw_bytes"


class RetainedSourceReader(Protocol):
    def read(self, path: Path) -> bytes: ...

    def document(self, path: Path) -> dict: ...


def _need(value: object, detail: str) -> None:
    require(bool(value), "research_publication_invalid", detail)


def _object(value: object) -> dict:
    _need(isinstance(value, dict), "publication field is not an object")
    return cast(dict, value)


def _relative(value: object) -> str:
    _need(isinstance(value, str) and 0 < len(value) <= 200,
          "source response artifact is invalid")
    assert isinstance(value, str)
    parts = value.split("/")
    _need(not any(part in {"", ".", ".."} for part in parts)
          and all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", p) for p in parts)
          and not PurePosixPath(value).is_absolute()
          and parts[0] == "research" and value.endswith(".json"),
          "source response must be one relative research JSON artifact")
    return value


def retained_response(obs: RetainedSourceReader, run: Path, source: dict, row: dict) -> bytes:
    """Verify raw response, body and explicitly declared unsigned event reference."""
    _need(set(row) == {"source_id", "kind", "source_record_sha256",
                      "response_artifact", "transport_sha256", "snapshot_sha256",
                      "event_reference_kind", "event_sha256"},
          "retained response evidence fields differ")
    _need(row["kind"] == "retained_tool_response"
          and row["source_id"] == source.get("source_id")
          and row["source_record_sha256"] == canonical_sha256(source)
          and row["event_reference_kind"] == EVENT_KIND,
          "source record or event reference kind differs")
    raw = obs.read(run / _relative(row["response_artifact"]))
    response = obs.document(run / row["response_artifact"])
    pages = response.get("results")
    _need(isinstance(pages, list) and len(pages) == 1
          and response.get("failed_results") == [],
          "retained response is not one complete successful tool result")
    page = _object(pages[0])
    text = page.get("raw_content")
    _need(isinstance(text, str) and bool(text.strip()), "retained tool body is empty")
    body = text.encode("utf-8", errors="strict")
    capture = _object(source.get("capture"))
    host = _object(capture.get("host_receipt"))
    _need(source.get("source_type") == "company_release"
          and source.get("url") == page.get("url")
          and source.get("title") == page.get("title")
          and isinstance(response.get("request_id"), str)
          and bool(response["request_id"].strip())
          and capture.get("tool_call_id") == response["request_id"]
          and capture.get("tool_name") == "tavily_extract"
          and capture.get("capture_method") == "api_response"
          and host.get("tool_name") == "tavily_extract"
          and host.get("action") == "tool_body_read"
          and row["snapshot_sha256"] == capture.get("snapshot_sha256") == hashlib.sha256(body).hexdigest()
          and row["transport_sha256"] == row["event_sha256"]
          == host.get("event_sha256") == hashlib.sha256(raw).hexdigest(),
          "retained response does not bind source URL/title/tool/body/transport/event")
    return body
