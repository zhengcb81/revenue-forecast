"""Legacy filing data contracts, retained as pure test fixtures (R3).

This is the surviving subset of the removed ``scripts/filing_acquisition.py``:
only the pure data constructors used by test fixtures (and the helpers they
depend on).  The download owner — ``AcquisitionManager`` / ``AdapterRegistry`` /
``CanonicalSourceWriter`` / ``resolve_filing`` / subprocess adapters — was
deleted in R3; filing acquisition has exactly one owner,
``filing_fetch_client.py`` (which routes to filing-fetch).  This file must
never grow download capability back.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


ACQUISITION_SCHEMA_VERSION = "1.0"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?"
    r"(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$"
)
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}
_MARKETS = frozenset({"CN", "HK", "US"})


class FilingAcquisitionError(RuntimeError):
    """Raised when a filing cannot be safely reused or acquired."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _json_hash(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FilingAcquisitionError(f"{name} must be non-empty trimmed text")
    return value


def _optional_text(value: Any, name: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, name)


def _canonical_date(value: Any, name: str) -> str:
    text = _required_text(value, name)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise FilingAcquisitionError(f"{name} must be a valid YYYY-MM-DD") from exc
    if parsed.isoformat() != text:
        raise FilingAcquisitionError(f"{name} must be canonical YYYY-MM-DD")
    return text


def _canonical_utc(value: Any, name: str) -> str:
    text = _required_text(value, name)
    if not _UTC_RE.fullmatch(text):
        raise FilingAcquisitionError(f"{name} must be UTC YYYY-MM-DDTHH:MM:SSZ")
    try:
        datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise FilingAcquisitionError(f"{name} must be a valid UTC timestamp") from exc
    return text


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_component(value: str, *, limit: int = 100) -> str:
    normalized = unicodedata.normalize("NFC", _required_text(value, "path component"))
    normalized = _INVALID_WINDOWS_CHARS.sub("_", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip(" .")
    if not normalized:
        normalized = "document"
    if normalized.upper() in _RESERVED_WINDOWS_NAMES:
        normalized = "_" + normalized
    return normalized[:limit].rstrip(" .") or "document"


def _inside(path: Path, root: Path, *, name: str) -> Path:
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise FilingAcquisitionError(f"{name} escapes its configured root") from exc
    return resolved


def _redact(text: str) -> str:
    value = text
    patterns = (
        re.compile(r"(?i)(authorization\s*[:=]\s*)(\S+)"),
        re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)(\S+)"),
        re.compile(r"(?i)(token\s*[:=]\s*)(\S+)"),
    )
    for pattern in patterns:
        value = pattern.sub(r"\1[REDACTED]", value)
    return value[-2000:]


@dataclass(frozen=True)
class SourceRequest:
    entity: str
    document_kind: str
    as_of_date: str
    market: str | None = None
    security_id: str | None = None
    form_type: str | None = None
    fiscal_year: int | None = None
    fiscal_period: str | None = None
    language: str | None = None
    provider: str | None = None
    provider_document_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "entity", _required_text(self.entity, "entity"))
        object.__setattr__(
            self,
            "document_kind",
            _required_text(self.document_kind, "document_kind").lower(),
        )
        object.__setattr__(
            self, "as_of_date", _canonical_date(self.as_of_date, "as_of_date")
        )
        market = _optional_text(self.market, "market")
        if market is not None:
            market = market.upper()
            if market not in _MARKETS:
                raise FilingAcquisitionError("market must be CN, HK, or US")
        object.__setattr__(self, "market", market)
        for name in (
            "security_id",
            "form_type",
            "fiscal_period",
            "language",
            "provider_document_id",
        ):
            object.__setattr__(self, name, _optional_text(getattr(self, name), name))
        provider = _optional_text(self.provider, "provider")
        object.__setattr__(self, "provider", provider.lower() if provider else None)
        if self.fiscal_year is not None:
            if isinstance(self.fiscal_year, bool) or not isinstance(
                self.fiscal_year, int
            ):
                raise FilingAcquisitionError("fiscal_year must be an integer")
            if not 1900 <= self.fiscal_year <= 2200:
                raise FilingAcquisitionError("fiscal_year is outside supported range")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": ACQUISITION_SCHEMA_VERSION,
            "entity": self.entity,
            "market": self.market,
            "security_id": self.security_id,
            "document_kind": self.document_kind,
            "form_type": self.form_type,
            "fiscal_year": self.fiscal_year,
            "fiscal_period": self.fiscal_period,
            "language": self.language,
            "provider": self.provider,
            "provider_document_id": self.provider_document_id,
            "as_of_date": self.as_of_date,
        }

    @property
    def request_id(self) -> str:
        return "urn:revenue-forecast:source-request:sha256:" + _json_hash(
            self.to_dict()
        )


@dataclass(frozen=True)
class DownloadCandidate:
    candidate_id: str
    provider: str
    provider_document_id: str
    market: str
    entity: str
    title: str
    source_url: str
    document_kind: str
    filing_date: str
    fiscal_year: int
    form_type: str | None = None
    fiscal_period: str | None = None
    language: str | None = None
    amended: bool = False
    etag: str | None = None
    last_modified: str | None = None
    remote_size: int | None = None
    adapter_payload_json: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "provider",
            "provider_document_id",
            "market",
            "entity",
            "title",
            "source_url",
            "document_kind",
        ):
            object.__setattr__(self, name, _required_text(getattr(self, name), name))
        object.__setattr__(self, "provider", self.provider.lower())
        object.__setattr__(self, "market", self.market.upper())
        object.__setattr__(self, "document_kind", self.document_kind.lower())
        if self.market not in _MARKETS:
            raise FilingAcquisitionError("candidate market is unsupported")
        if not self.source_url.startswith("https://"):
            raise FilingAcquisitionError("candidate source_url must use HTTPS")
        object.__setattr__(
            self, "filing_date", _canonical_date(self.filing_date, "filing_date")
        )
        for name in (
            "form_type",
            "fiscal_period",
            "language",
            "etag",
            "last_modified",
            "adapter_payload_json",
        ):
            object.__setattr__(self, name, _optional_text(getattr(self, name), name))
        if isinstance(self.fiscal_year, bool) or not isinstance(self.fiscal_year, int):
            raise FilingAcquisitionError("candidate fiscal_year must be an integer")
        if not 1900 <= self.fiscal_year <= 2200:
            raise FilingAcquisitionError("candidate fiscal_year is outside range")
        if not isinstance(self.amended, bool):
            raise FilingAcquisitionError("candidate amended must be boolean")
        if self.remote_size is not None and (
            isinstance(self.remote_size, bool)
            or not isinstance(self.remote_size, int)
            or self.remote_size <= 0
        ):
            raise FilingAcquisitionError(
                "candidate remote_size must be a positive integer"
            )

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class DownloadReceipt:
    candidate_id: str
    provider: str
    provider_document_id: str
    source_url: str
    staged_path: str
    content_sha256: str
    byte_size: int
    mime_type: str
    retrieved_at: str
    http_status: int
    adapter_name: str
    adapter_version: str
    etag: str | None = None
    last_modified: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "provider",
            "provider_document_id",
            "source_url",
            "staged_path",
            "mime_type",
            "adapter_name",
            "adapter_version",
        ):
            object.__setattr__(self, name, _required_text(getattr(self, name), name))
        object.__setattr__(self, "provider", self.provider.lower())
        if not self.source_url.startswith("https://"):
            raise FilingAcquisitionError("receipt source_url must use HTTPS")
        if not _SHA256_RE.fullmatch(self.content_sha256):
            raise FilingAcquisitionError("receipt content_sha256 is invalid")
        if (
            isinstance(self.byte_size, bool)
            or not isinstance(self.byte_size, int)
            or self.byte_size <= 0
        ):
            raise FilingAcquisitionError("receipt byte_size must be positive")
        object.__setattr__(
            self,
            "retrieved_at",
            _canonical_utc(self.retrieved_at, "retrieved_at"),
        )
        if (
            isinstance(self.http_status, bool)
            or not isinstance(self.http_status, int)
            or not 100 <= self.http_status <= 599
        ):
            raise FilingAcquisitionError("receipt http_status is invalid")
        if not _SEMVER_RE.fullmatch(self.adapter_version):
            raise FilingAcquisitionError("receipt adapter_version must be semver")
        object.__setattr__(self, "etag", _optional_text(self.etag, "etag"))
        object.__setattr__(
            self, "last_modified", _optional_text(self.last_modified, "last_modified")
        )

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)
