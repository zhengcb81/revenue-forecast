"""Self-contained, reuse-first filing acquisition for revenue-forecast.

The module intentionally depends only on the Python standard library and
external downloader CLIs.  ``company_wiki_root`` is a configurable data root;
no company-wiki Python package, CLI, source checkout, or PYTHONPATH is needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from difflib import SequenceMatcher
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from typing import Any, Mapping, Protocol, runtime_checkable
import unicodedata
from uuid import uuid4


CONFIG_SCHEMA_VERSION = "2.0"
ACQUISITION_SCHEMA_VERSION = "1.0"
SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_ROOT / "config" / "company_wiki.json"
_CONFIG_TOKEN_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?"
    r"(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$"
)
_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_SAFE_EXTENSION = re.compile(r"^\.[a-z0-9]{1,10}$")
_RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}
_MARKETS = frozenset({"CN", "HK", "US"})
_US_ANNUAL_FORMS = ("10-K", "20-F")
_US_QUARTERLY_FORMS = ("10-Q", "10-Q/A")


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
        raise FilingAcquisitionError(
            f"{name} must be UTC YYYY-MM-DDTHH:MM:SSZ"
        )
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
class AdapterCommandSpec:
    name: str
    version: str
    interface: str
    project_root: Path
    config_root: Path | None
    command: tuple[str, ...]


@dataclass(frozen=True)
class AcquisitionConfig:
    schema_version: str
    company_wiki_root: Path
    security_master_root: Path
    staging_root: Path
    timeout_seconds: float
    cn: AdapterCommandSpec
    hk: AdapterCommandSpec
    us: AdapterCommandSpec

    def adapter_spec(self, market: str) -> AdapterCommandSpec:
        normalized = _required_text(market, "market").upper()
        if normalized == "CN":
            return self.cn
        if normalized == "HK":
            return self.hk
        if normalized == "US":
            return self.us
        raise FilingAcquisitionError(f"unsupported market: {market}")


def _expand_config_text(
    value: Any,
    *,
    name: str,
    config_dir: Path,
    company_wiki_root: Path | None,
) -> str:
    text = _required_text(value, name)
    tokens = {
        "SKILL_ROOT": str(SKILL_ROOT),
        "USER_PROFILE": (
            os.environ.get("USERPROFILE")
            or os.environ.get("HOME")
            or str(config_dir)
        ),
        "PYTHON_EXECUTABLE": str(Path(sys.executable).resolve()),
        "CONFIG_DIR": str(config_dir),
    }
    if company_wiki_root is not None:
        tokens["COMPANY_WIKI_ROOT"] = str(company_wiki_root)

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token not in tokens:
            raise FilingAcquisitionError(f"unsupported config token: {token}")
        return tokens[token]

    expanded = _CONFIG_TOKEN_RE.sub(replace, text)
    if _CONFIG_TOKEN_RE.search(expanded):
        raise FilingAcquisitionError(f"{name} contains an unresolved config token")
    return expanded


def _config_path(
    value: Any,
    *,
    name: str,
    config_dir: Path,
    company_wiki_root: Path | None,
) -> Path:
    expanded = _expand_config_text(
        value,
        name=name,
        config_dir=config_dir,
        company_wiki_root=company_wiki_root,
    )
    path = Path(expanded).expanduser()
    if not path.is_absolute():
        path = config_dir / path
    return path.resolve(strict=False)


def _adapter_spec(
    value: Any,
    *,
    market: str,
    config_dir: Path,
    company_wiki_root: Path,
) -> AdapterCommandSpec:
    if not isinstance(value, dict):
        raise FilingAcquisitionError(f"adapters.{market.lower()} must be an object")
    expected = {
        "name",
        "version",
        "interface",
        "project_root",
        "config_root",
        "command",
    }
    if set(value) != expected:
        raise FilingAcquisitionError(
            f"adapters.{market.lower()} fields do not match schema"
        )
    interface = _required_text(value["interface"], "adapter.interface")
    required_interface = "json_command_v1" if market == "CN" else "dayu_cli_v1"
    if interface != required_interface:
        raise FilingAcquisitionError(
            f"{market} adapter must use {required_interface}"
        )
    version = _required_text(value["version"], "adapter.version")
    if not _SEMVER_RE.fullmatch(version):
        raise FilingAcquisitionError("adapter.version must use semantic versioning")
    raw_command = value["command"]
    if (
        not isinstance(raw_command, list)
        or not raw_command
        or not all(isinstance(item, str) and item.strip() for item in raw_command)
    ):
        raise FilingAcquisitionError("adapter.command must be a non-empty text array")
    command = tuple(
        _expand_config_text(
            item,
            name="adapter.command",
            config_dir=config_dir,
            company_wiki_root=company_wiki_root,
        )
        for item in raw_command
    )
    if any("company_wiki.source_catalog" in item for item in command):
        raise FilingAcquisitionError(
            "adapter command must not invoke company-wiki Python code"
        )
    raw_config_root = value["config_root"]
    if interface == "json_command_v1" and raw_config_root is not None:
        raise FilingAcquisitionError("CN adapter.config_root must be null")
    if interface == "dayu_cli_v1" and raw_config_root is None:
        raise FilingAcquisitionError("Dayu adapter.config_root is required")
    return AdapterCommandSpec(
        name=_required_text(value["name"], "adapter.name"),
        version=version,
        interface=interface,
        project_root=_config_path(
            value["project_root"],
            name="adapter.project_root",
            config_dir=config_dir,
            company_wiki_root=company_wiki_root,
        ),
        config_root=(
            _config_path(
                raw_config_root,
                name="adapter.config_root",
                config_dir=config_dir,
                company_wiki_root=company_wiki_root,
            )
            if raw_config_root is not None
            else None
        ),
        command=command,
    )


def load_acquisition_config(path: Path | None = None) -> AcquisitionConfig:
    selected = (path or DEFAULT_CONFIG).expanduser().resolve(strict=True)
    if not selected.is_file():
        raise FilingAcquisitionError("acquisition config must be a file")
    try:
        payload = json.loads(selected.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FilingAcquisitionError(f"invalid acquisition config: {exc}") from exc
    if not isinstance(payload, dict):
        raise FilingAcquisitionError("acquisition config must be an object")
    expected = {
        "schema_version",
        "company_wiki_root",
        "security_master_root",
        "staging_root",
        "timeout_seconds",
        "adapters",
    }
    if set(payload) != expected:
        raise FilingAcquisitionError("acquisition config fields do not match schema")
    if payload["schema_version"] != CONFIG_SCHEMA_VERSION:
        raise FilingAcquisitionError(
            f"acquisition config schema_version must be {CONFIG_SCHEMA_VERSION}"
        )
    config_dir = selected.parent
    company_root = _config_path(
        payload["company_wiki_root"],
        name="company_wiki_root",
        config_dir=config_dir,
        company_wiki_root=None,
    )
    if not company_root.is_dir():
        raise FilingAcquisitionError(
            f"configured company_wiki_root does not exist: {company_root}"
        )
    security_root = _config_path(
        payload["security_master_root"],
        name="security_master_root",
        config_dir=config_dir,
        company_wiki_root=company_root,
    )
    staging_root = _inside(
        _config_path(
            payload["staging_root"],
            name="staging_root",
            config_dir=config_dir,
            company_wiki_root=company_root,
        ),
        company_root,
        name="staging_root",
    )
    timeout = payload["timeout_seconds"]
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or timeout <= 0
    ):
        raise FilingAcquisitionError("timeout_seconds must be positive")
    adapters = payload["adapters"]
    if not isinstance(adapters, dict) or set(adapters) != {"cn", "hk", "us"}:
        raise FilingAcquisitionError("adapters must contain exact cn/hk/us fields")
    return AcquisitionConfig(
        schema_version=CONFIG_SCHEMA_VERSION,
        company_wiki_root=company_root,
        security_master_root=security_root,
        staging_root=staging_root,
        timeout_seconds=float(timeout),
        cn=_adapter_spec(
            adapters["cn"],
            market="CN",
            config_dir=config_dir,
            company_wiki_root=company_root,
        ),
        hk=_adapter_spec(
            adapters["hk"],
            market="HK",
            config_dir=config_dir,
            company_wiki_root=company_root,
        ),
        us=_adapter_spec(
            adapters["us"],
            market="US",
            config_dir=config_dir,
            company_wiki_root=company_root,
        ),
    )


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


@runtime_checkable
class DownloadAdapter(Protocol):
    name: str
    version: str

    def discover(self, request: SourceRequest) -> tuple[DownloadCandidate, ...]: ...

    def fetch(
        self, candidate: DownloadCandidate, staging_dir: Path
    ) -> DownloadReceipt: ...


@dataclass(frozen=True)
class AdapterRegistry:
    cn: DownloadAdapter
    hk: DownloadAdapter
    us: DownloadAdapter

    def __post_init__(self) -> None:
        for name in ("cn", "hk", "us"):
            adapter = getattr(self, name)
            if not isinstance(adapter, DownloadAdapter):
                raise TypeError(f"{name} must implement DownloadAdapter")

    @classmethod
    def from_mapping(cls, value: Mapping[str, DownloadAdapter]) -> "AdapterRegistry":
        if set(value) != _MARKETS:
            raise FilingAcquisitionError("adapter mapping must contain exact CN/HK/US")
        return cls(cn=value["CN"], hk=value["HK"], us=value["US"])

    @classmethod
    def from_config(cls, config: AcquisitionConfig) -> "AdapterRegistry":
        adapters: dict[str, DownloadAdapter] = {}
        for market in ("CN", "HK", "US"):
            spec = config.adapter_spec(market)
            if spec.interface == "json_command_v1":
                adapters[market] = JsonCommandAdapter(
                    spec=spec, timeout_seconds=config.timeout_seconds
                )
            else:
                adapters[market] = DayuCliAdapter(
                    spec=spec,
                    market=market,
                    timeout_seconds=config.timeout_seconds,
                )
        return cls.from_mapping(adapters)

    def for_market(self, market: str) -> DownloadAdapter:
        normalized = _required_text(market, "market").upper()
        if normalized == "CN":
            return self.cn
        if normalized == "HK":
            return self.hk
        if normalized == "US":
            return self.us
        raise FilingAcquisitionError(f"unsupported market: {market}")


def _normalize_identity(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _load_security_records(root: Path, market: str | None) -> list[dict[str, Any]]:
    markets = (market.lower(),) if market else ("cn", "hk", "us")
    records: list[dict[str, Any]] = []
    for selected in markets:
        path = root / f"{selected}.json"
        if not path.is_file():
            if market:
                raise FilingAcquisitionError(
                    f"missing security-master snapshot: {market}"
                )
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FilingAcquisitionError(
                f"invalid security-master snapshot {path}: {exc}"
            ) from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            raise FilingAcquisitionError(f"invalid security-master schema: {path}")
        if payload.get("market") != selected.upper():
            raise FilingAcquisitionError(f"security-master market mismatch: {path}")
        for item in payload["records"]:
            if not isinstance(item, dict):
                raise FilingAcquisitionError("security-master record must be an object")
            records.append(item)
    if not records:
        raise FilingAcquisitionError(
            f"no security-master snapshots found in {root}"
        )
    return records


def _resolve_identity(
    query: str,
    *,
    market: str | None,
    exchange: str | None,
    security_master_root: Path,
) -> dict[str, Any]:
    query = _required_text(query, "company_query")
    market = _optional_text(market, "market")
    market = market.upper() if market else None
    if market is not None and market not in _MARKETS:
        raise FilingAcquisitionError("market hint must be CN, HK, or US")
    exchange = _optional_text(exchange, "exchange")
    exchange = exchange.upper() if exchange else None
    normalized_query = _normalize_identity(query)
    if not normalized_query:
        raise FilingAcquisitionError("company_query has no searchable characters")
    candidates: list[tuple[float, str, dict[str, Any]]] = []
    for record in _load_security_records(security_master_root, market):
        required = (
            "canonical_name",
            "market",
            "exchange",
            "ticker",
            "security_id",
            "aliases",
            "active",
            "source_name",
            "source_url",
            "source_record_id",
        )
        if any(name not in record for name in required):
            raise FilingAcquisitionError("security-master record lacks required fields")
        if record["market"] not in _MARKETS:
            raise FilingAcquisitionError("security-master record market is unsupported")
        if market and record["market"] != market:
            continue
        if exchange and str(record["exchange"]).upper() != exchange:
            continue
        values = [
            ("official_name_exact", str(record["canonical_name"])),
            ("ticker_exact", str(record["ticker"])),
            ("ticker_exact", str(record["security_id"])),
        ]
        aliases = record["aliases"]
        if not isinstance(aliases, list):
            raise FilingAcquisitionError("security-master aliases must be an array")
        values.extend(("alias_exact", str(alias)) for alias in aliases)
        exact = next(
            (
                (basis, value)
                for basis, value in values
                if _normalize_identity(value) == normalized_query
            ),
            None,
        )
        if exact:
            candidates.append((1.0, exact[0], {**record, "matched_value": exact[1]}))
            continue
        fuzzy_values = [str(record["canonical_name"]), *(str(item) for item in aliases)]
        score, matched = max(
            (
                SequenceMatcher(
                    None, normalized_query, _normalize_identity(candidate)
                ).ratio(),
                candidate,
            )
            for candidate in fuzzy_values
            if _normalize_identity(candidate)
        )
        candidates.append((score, "strong_fuzzy", {**record, "matched_value": matched}))
    candidates.sort(
        key=lambda item: (
            -item[0],
            str(item[2]["market"]),
            str(item[2]["exchange"]),
            str(item[2]["security_id"]),
        )
    )
    exact = [item for item in candidates if item[0] == 1.0]
    if len(exact) != 1:
        if len(exact) > 1:
            raise FilingAcquisitionError("company identity is ambiguous")
        if not candidates or candidates[0][0] < 0.90:
            raise FilingAcquisitionError("company identity is missing or low confidence")
        if len(candidates) > 1 and candidates[0][0] - candidates[1][0] < 0.03:
            raise FilingAcquisitionError("company identity is ambiguous")
        selected = candidates[0]
    else:
        selected = exact[0]
    score, basis, record = selected
    if record.get("active") is not True:
        raise FilingAcquisitionError("company identity is inactive")
    source_url = _required_text(record["source_url"], "identity.source_url")
    if not source_url.startswith("https://"):
        raise FilingAcquisitionError("identity source_url must use HTTPS")
    return {
        "schema_version": "1.0",
        "canonical_name": _required_text(
            record["canonical_name"], "identity.canonical_name"
        ),
        "market": _required_text(record["market"], "identity.market").upper(),
        "exchange": _required_text(record["exchange"], "identity.exchange").upper(),
        "ticker": _required_text(record["ticker"], "identity.ticker").upper(),
        "security_id": _required_text(
            record["security_id"], "identity.security_id"
        ).upper(),
        "match_basis": basis,
        "matched_value": _required_text(
            record["matched_value"], "identity.matched_value"
        ),
        "score": round(float(score), 4),
        "verified": True,
        "active": True,
        "source_name": _required_text(record["source_name"], "identity.source_name"),
        "source_url": source_url,
        "source_record_id": _required_text(
            record["source_record_id"], "identity.source_record_id"
        ),
        "identifiers": (
            dict(record.get("identifiers", {}))
            if isinstance(record.get("identifiers", {}), dict)
            else {}
        ),
    }


def _request_from_payload(
    payload: dict[str, Any],
    *,
    config: AcquisitionConfig,
) -> tuple[SourceRequest, dict[str, Any] | None]:
    if not isinstance(payload, dict):
        raise TypeError("request must be a dict")
    allowed = {
        "company_query",
        "entity",
        "market",
        "exchange",
        "security_id",
        "document_kind",
        "as_of_date",
        "form_type",
        "fiscal_year",
        "fiscal_period",
        "language",
        "provider",
        "provider_document_id",
    }
    unknown = set(payload) - allowed
    if unknown:
        raise FilingAcquisitionError(
            "request contains unsupported fields: " + ", ".join(sorted(unknown))
        )
    identity = None
    normalized = dict(payload)
    if "company_query" in payload:
        if "entity" in payload or "security_id" in payload:
            raise FilingAcquisitionError(
                "company_query cannot be combined with entity or security_id"
            )
        identity = _resolve_identity(
            payload["company_query"],
            market=payload.get("market"),
            exchange=payload.get("exchange"),
            security_master_root=config.security_master_root,
        )
        normalized["entity"] = identity["canonical_name"]
        normalized["market"] = identity["market"]
        normalized["security_id"] = identity["security_id"]
    normalized.pop("company_query", None)
    normalized.pop("exchange", None)
    return SourceRequest(**normalized), identity


def _sidecar_raw_path(sidecar: Path, payload: dict[str, Any]) -> Path:
    configured = payload.get("canonical_path")
    if isinstance(configured, str) and configured.strip():
        return Path(configured)
    suffix = ".source.json"
    if not sidecar.name.endswith(suffix):
        raise FilingAcquisitionError("provenance sidecar name is invalid")
    return sidecar.with_name(sidecar.name[: -len(suffix)])


def _sidecar_value(payload: dict[str, Any], name: str) -> Any:
    if name in payload:
        return payload[name]
    request = payload.get("request")
    if isinstance(request, dict) and name in request:
        return request[name]
    candidate = payload.get("candidate")
    if isinstance(candidate, dict) and name in candidate:
        return candidate[name]
    receipt = payload.get("receipt")
    if isinstance(receipt, dict) and name in receipt:
        return receipt[name]
    return None


class FilesystemSourceResolver:
    """Resolve immutable raw+sidecar sources without a catalog code dependency."""

    def __init__(self, config: AcquisitionConfig):
        self.config = config

    def _sidecars(self, request: SourceRequest) -> tuple[Path, ...]:
        companies = self.config.company_wiki_root / "companies"
        if not companies.is_dir():
            return ()
        exact = companies / _safe_component(request.entity, limit=80)
        roots = [exact] if exact.is_dir() else []
        if not roots:
            roots = [
                path
                for path in companies.iterdir()
                if path.is_dir()
                and _normalize_identity(path.name) == _normalize_identity(request.entity)
            ]
        sidecars: list[Path] = []
        for root in roots:
            sidecars.extend(root.rglob("*.source.json"))
        aliases = (
            self.config.company_wiki_root
            / ".source_catalog"
            / "revenue-forecast"
            / "aliases"
        )
        if aliases.is_dir():
            sidecars.extend(aliases.glob("*.source.json"))
        return tuple(sorted(set(sidecars), key=lambda item: str(item).casefold()))

    def _load(self, sidecar: Path, request: SourceRequest) -> dict[str, Any] | None:
        try:
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FilingAcquisitionError(
                f"invalid provenance sidecar {sidecar}: {exc}"
            ) from exc
        if not isinstance(payload, dict):
            raise FilingAcquisitionError(
                f"provenance sidecar must contain an object: {sidecar}"
            )
        company = _sidecar_value(payload, "company_name") or _sidecar_value(
            payload, "entity"
        )
        if not isinstance(company, str) or _normalize_identity(
            company
        ) != _normalize_identity(request.entity):
            return None
        kind = _sidecar_value(payload, "document_kind")
        if kind != request.document_kind:
            return None
        return payload

    @staticmethod
    def _metadata(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            name: _sidecar_value(payload, name)
            for name in (
                "company_name",
                "entity",
                "market",
                "security_id",
                "source_title",
                "provider",
                "provider_document_id",
                "source_url",
                "document_kind",
                "form_type",
                "filing_date",
                "fiscal_year",
                "fiscal_period",
                "language",
                "content_sha256",
                "byte_size",
                "mime_type",
                "retrieved_at",
                "adapter_name",
                "adapter_version",
            )
        }

    def _match(
        self,
        request: SourceRequest,
        sidecar: Path,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any] | None, bool]:
        metadata = self._metadata(payload)
        sidecar_market = metadata["market"]
        sidecar_security = metadata["security_id"]
        identity_conflict = False
        if request.market and sidecar_market and str(sidecar_market).upper() != request.market:
            identity_conflict = True
        if (
            request.security_id
            and sidecar_security
            and str(sidecar_security).upper() != request.security_id.upper()
        ):
            identity_conflict = True
        if identity_conflict:
            return None, True
        if request.market and not sidecar_market:
            return None, False
        if request.security_id and not sidecar_security:
            return None, False
        filters = (
            ("fiscal_year", request.fiscal_year),
            ("fiscal_period", request.fiscal_period),
            ("form_type", request.form_type),
            ("language", request.language),
            ("provider_document_id", request.provider_document_id),
        )
        for name, expected in filters:
            if expected is not None and metadata[name] != expected:
                return None, False
        if request.provider is not None and str(metadata["provider"] or "").lower() != request.provider:
            return None, False
        filing_date = _canonical_date(metadata["filing_date"], "sidecar.filing_date")
        if date.fromisoformat(filing_date) > date.fromisoformat(request.as_of_date):
            return None, False
        try:
            raw = _sidecar_raw_path(sidecar, payload).expanduser().resolve(strict=True)
        except OSError as exc:
            raise FilingAcquisitionError(
                f"provenance canonical source is missing: {sidecar}"
            ) from exc
        raw = _inside(raw, self.config.company_wiki_root, name="canonical_path")
        if not raw.is_file():
            raise FilingAcquisitionError("provenance canonical_path is not a file")
        digest = _required_text(metadata["content_sha256"], "sidecar.content_sha256")
        if not _SHA256_RE.fullmatch(digest):
            raise FilingAcquisitionError("provenance content SHA-256 is invalid")
        if _sha256_file(raw) != digest:
            raise FilingAcquisitionError(
                f"provenance SHA-256 does not match canonical bytes: {raw}"
            )
        size = metadata["byte_size"]
        if isinstance(size, bool) or not isinstance(size, int) or size != raw.stat().st_size:
            raise FilingAcquisitionError("provenance byte_size does not match canonical bytes")
        retrieved_at = _canonical_utc(
            metadata["retrieved_at"], "sidecar.retrieved_at"
        )
        captured_date = datetime.strptime(
            retrieved_at, "%Y-%m-%dT%H:%M:%SZ"
        ).date()
        if not date.fromisoformat(filing_date) <= captured_date <= date.fromisoformat(
            request.as_of_date
        ):
            return None, False
        source_url = _required_text(metadata["source_url"], "sidecar.source_url")
        if not source_url.startswith("https://"):
            raise FilingAcquisitionError("provenance source_url must use HTTPS")
        provider = _required_text(metadata["provider"], "sidecar.provider").lower()
        provider_document_id = _required_text(
            metadata["provider_document_id"], "sidecar.provider_document_id"
        )
        title = _required_text(metadata["source_title"], "sidecar.source_title")
        location_id = "urn:revenue-forecast:location:sha256:" + _json_hash(
            {"path": str(raw), "sha256": digest}
        )
        return (
            {
                "schema_version": "1.0",
                "document_id": "urn:revenue-forecast:document:sha256:" + digest,
                "source_id": "urn:revenue-forecast:source:sha256:" + digest,
                "entity_ids": [
                    f"urn:revenue-forecast:entity:{request.market or 'UNKNOWN'}:{request.security_id or _normalize_identity(request.entity)}"
                ],
                "title": title,
                "source_type": "filing",
                "document_kind": request.document_kind,
                "published_date": filing_date,
                "fiscal_year": metadata["fiscal_year"],
                "fiscal_period": metadata["fiscal_period"],
                "form_type": metadata["form_type"],
                "language": metadata["language"],
                "provider": provider,
                "provider_document_id": provider_document_id,
                "https_url": source_url,
                "canonical_location_id": location_id,
                "canonical_path": str(raw),
                "content_sha256": digest,
                "snapshot_sha256": digest,
                "mime_type": _required_text(
                    metadata["mime_type"], "sidecar.mime_type"
                ),
                "byte_size": size,
                "retrieved_at": retrieved_at,
                "collector_name": _required_text(
                    metadata["adapter_name"], "sidecar.adapter_name"
                ),
                "collector_version": _required_text(
                    metadata["adapter_version"], "sidecar.adapter_version"
                ),
                "source_status": "active",
                "duplicate_group_id": "urn:revenue-forecast:duplicate:sha256:" + digest,
                "exact_duplicate_location_count": 1,
                "capture_ready": True,
                "missing_capture_fields": [],
                "provenance_path": str(sidecar.resolve()),
            },
            False,
        )

    def resolve(self, request: SourceRequest) -> dict[str, Any] | None:
        matches: list[dict[str, Any]] = []
        identity_conflict = False
        for sidecar in self._sidecars(request):
            payload = self._load(sidecar, request)
            if payload is None:
                continue
            match, conflict = self._match(request, sidecar, payload)
            identity_conflict = identity_conflict or conflict
            if match is not None:
                matches.append(match)
        if not matches:
            if identity_conflict:
                raise FilingAcquisitionError(
                    "existing sources conflict with requested security identity"
                )
            return None
        hashes = {item["snapshot_sha256"] for item in matches}
        if len(hashes) > 1:
            raise FilingAcquisitionError(
                "multiple non-identical reusable filings match the request"
            )
        matches.sort(key=lambda item: item["canonical_path"].casefold())
        return matches[0]


class JsonCommandAdapter:
    """Call StockInfoDLSimple through its versioned JSON CLI contract."""

    def __init__(self, *, spec: AdapterCommandSpec, timeout_seconds: float):
        self.name = spec.name
        self.version = spec.version
        self.command = spec.command
        self.project_root = spec.project_root
        self.timeout_seconds = timeout_seconds

    def _run(
        self,
        action: str,
        payload: dict[str, Any],
        *,
        extra_args: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        if not self.project_root.is_dir():
            raise FilingAcquisitionError(
                f"adapter project_root does not exist: {self.project_root}"
            )
        environment = dict(os.environ)
        environment["PYTHONUTF8"] = "1"
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        try:
            completed = subprocess.run(
                (*self.command, action, *extra_args),
                input=_canonical_json(payload),
                text=True,
                encoding="utf-8",
                errors="strict",
                capture_output=True,
                cwd=self.project_root,
                env=environment,
                timeout=self.timeout_seconds,
                check=False,
                shell=False,
                creationflags=creationflags,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise FilingAcquisitionError(
                f"adapter {self.name} {action} failed: {exc}"
            ) from exc
        if completed.returncode != 0:
            raise FilingAcquisitionError(
                f"adapter {self.name} {action} exited {completed.returncode}: "
                + _redact(completed.stderr.strip() or "no stderr")
            )
        try:
            response = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise FilingAcquisitionError(
                f"adapter {self.name} {action} stdout is not JSON"
            ) from exc
        if (
            not isinstance(response, dict)
            or response.get("schema_version") != "1.0"
            or response.get("status") != "ok"
        ):
            raise FilingAcquisitionError("adapter response schema/status is invalid")
        identity = response.get("adapter")
        if not isinstance(identity, dict) or identity != {
            "name": self.name,
            "version": self.version,
        }:
            raise FilingAcquisitionError("adapter response identity/version mismatch")
        return response

    def discover(self, request: SourceRequest) -> tuple[DownloadCandidate, ...]:
        response = self._run("discover", request.to_dict())
        values = response.get("candidates")
        if not isinstance(values, list):
            raise FilingAcquisitionError("adapter candidates must be an array")
        candidates = []
        for value in values:
            if not isinstance(value, dict):
                raise FilingAcquisitionError("adapter candidate must be an object")
            try:
                candidates.append(
                    DownloadCandidate(
                        candidate_id=value["candidate_id"],
                        provider=value["provider"],
                        provider_document_id=value["provider_document_id"],
                        market=value["market"],
                        entity=request.entity,
                        title=value["title"],
                        source_url=value["source_url"],
                        document_kind=value["document_kind"],
                        filing_date=value["filing_date"],
                        fiscal_year=value["fiscal_year"],
                        form_type=value.get("form_type"),
                        fiscal_period=value.get("fiscal_period"),
                        language=value.get("language"),
                        amended=value.get("amended", False),
                        etag=value.get("etag"),
                        last_modified=value.get("last_modified"),
                        remote_size=value.get(
                            "remote_size", value.get("content_length")
                        ),
                        adapter_payload_json=_canonical_json(value),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise FilingAcquisitionError(
                    f"invalid adapter candidate: {exc}"
                ) from exc
        return tuple(candidates)

    def fetch(
        self, candidate: DownloadCandidate, staging_dir: Path
    ) -> DownloadReceipt:
        staging_dir.mkdir(parents=True, exist_ok=True)
        response = self._run(
            "fetch",
            candidate.to_dict(),
            extra_args=("--staging-dir", str(staging_dir.resolve(strict=True))),
        )
        value = response.get("receipt")
        if not isinstance(value, dict):
            raise FilingAcquisitionError("adapter receipt must be an object")
        try:
            return DownloadReceipt(
                candidate_id=value["candidate_id"],
                provider=value["provider"],
                provider_document_id=value["provider_document_id"],
                source_url=value["source_url"],
                staged_path=value["staged_path"],
                content_sha256=value["content_sha256"],
                byte_size=value["byte_size"],
                mime_type=value["mime_type"],
                retrieved_at=value["retrieved_at"],
                http_status=value["http_status"],
                adapter_name=value["adapter_name"],
                adapter_version=value["adapter_version"],
                etag=value.get("etag"),
                last_modified=value.get("last_modified"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise FilingAcquisitionError(f"invalid adapter receipt: {exc}") from exc


@dataclass(frozen=True)
class _DayuAsset:
    source_path: Path
    content_sha256: str
    byte_size: int
    mime_type: str


class DayuCliAdapter:
    """Invoke dayu-agent CLI without importing or modifying dayu-agent."""

    def __init__(
        self,
        *,
        spec: AdapterCommandSpec,
        market: str,
        timeout_seconds: float,
    ):
        if market not in {"HK", "US"}:
            raise FilingAcquisitionError("Dayu adapter market must be HK or US")
        if spec.config_root is None:
            raise FilingAcquisitionError("Dayu adapter requires config_root")
        self.name = spec.name
        self.version = spec.version
        self.market = market
        self.command = spec.command
        self.project_root = spec.project_root
        self.config_root = spec.config_root
        self.timeout_seconds = timeout_seconds
        self._temporary: TemporaryDirectory[str] | None = None
        self._workspace: Path | None = None
        self._assets: dict[str, _DayuAsset] = {}

    @staticmethod
    def _forms(request: SourceRequest) -> tuple[str, ...]:
        if request.form_type:
            return (request.form_type,)
        if request.market == "HK":
            if request.fiscal_period:
                return (request.fiscal_period,)
            if request.document_kind == "annual_report":
                return ("FY",)
            if request.document_kind == "semi_annual_report":
                return ("H1",)
            if request.document_kind == "quarterly_report":
                return ("Q1", "Q2", "Q3", "Q4")
        if request.market == "US":
            if request.document_kind == "annual_report":
                return _US_ANNUAL_FORMS
            if request.document_kind == "quarterly_report":
                return _US_QUARTERLY_FORMS
        raise FilingAcquisitionError(
            f"Dayu CLI does not support {request.market}/{request.document_kind}"
        )

    def close(self) -> None:
        self._assets.clear()
        self._workspace = None
        temporary, self._temporary = self._temporary, None
        if temporary is not None:
            temporary.cleanup()

    def discover(self, request: SourceRequest) -> tuple[DownloadCandidate, ...]:
        if request.market != self.market:
            raise FilingAcquisitionError("request market does not match Dayu adapter")
        if not request.security_id or request.fiscal_year is None:
            raise FilingAcquisitionError(
                "Dayu download requires security_id and fiscal_year"
            )
        if not self.project_root.is_dir() or not self.config_root.is_dir():
            raise FilingAcquisitionError("configured Dayu project/config root is missing")
        self.close()
        workspace_parent = Path(os.environ.get("TEMP") or os.environ.get("TMP") or ".")
        workspace_parent = (workspace_parent / "revenue-forecast-dayu").resolve(
            strict=False
        )
        workspace_parent.mkdir(parents=True, exist_ok=True)
        self._temporary = TemporaryDirectory(
            prefix=f"dayu-{self.market.lower()}-", dir=workspace_parent
        )
        self._workspace = Path(self._temporary.name).resolve(strict=True)
        command = [
            *self.command,
            "download",
            "--ticker",
            request.security_id,
            "--forms",
            *self._forms(request),
            "--start",
            f"{request.fiscal_year}-01-01",
            "--end",
            request.as_of_date,
            "--base",
            str(self._workspace),
            "--config",
            str(self.config_root),
            "--quiet",
        ]
        environment = dict(os.environ)
        environment["PYTHONUTF8"] = "1"
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        try:
            process = subprocess.Popen(
                command,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_root,
                env=environment,
                shell=False,
                creationflags=creationflags,
            )
        except OSError as exc:
            self.close()
            raise FilingAcquisitionError(f"Dayu CLI process failed: {exc}") from exc
        candidates: tuple[DownloadCandidate, ...] = ()
        started = time.monotonic()
        while process.poll() is None and time.monotonic() - started < self.timeout_seconds:
            if (self._workspace / "portfolio").is_dir():
                candidates = self._read_candidates(request)
                if candidates:
                    break
            time.sleep(1.0)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if not candidates:
            candidates = self._read_candidates(request)
        if process.returncode not in (None, 0) and not candidates:
            detail = ""
            if process.stderr is not None:
                detail = process.stderr.read() or ""
            self.close()
            raise FilingAcquisitionError(
                f"Dayu CLI exited {process.returncode}: "
                + _redact(detail.strip() or "no stderr")
            )
        if not candidates:
            self.close()
        return candidates

    def _read_candidates(
        self, request: SourceRequest
    ) -> tuple[DownloadCandidate, ...]:
        if self._workspace is None:
            return ()
        candidates = []
        for meta_path in sorted(
            (self._workspace / "portfolio").glob("*/filings/*/meta.json")
        ):
            candidate = self._candidate_from_meta(request, meta_path)
            if candidate is not None:
                candidates.append(candidate)
        return tuple(
            sorted(
                candidates,
                key=lambda item: (
                    item.provider_document_id,
                    item.filing_date,
                    item.candidate_id,
                ),
            )
        )

    def _candidate_from_meta(
        self, request: SourceRequest, meta_path: Path
    ) -> DownloadCandidate | None:
        try:
            value = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FilingAcquisitionError(f"invalid Dayu meta {meta_path}: {exc}") from exc
        if not isinstance(value, dict) or value.get("is_deleted") is True:
            return None
        fiscal_year = value.get("fiscal_year")
        if fiscal_year != request.fiscal_year:
            return None
        fiscal_period = value.get("fiscal_period")
        if request.fiscal_period and fiscal_period != request.fiscal_period:
            return None
        form_type = _required_text(value.get("form_type"), "Dayu form_type")
        if form_type not in self._forms(request):
            return None
        filing_date = _canonical_date(value.get("filing_date"), "Dayu filing_date")
        if date.fromisoformat(filing_date) > date.fromisoformat(request.as_of_date):
            return None
        files = value.get("files")
        if not isinstance(files, list):
            raise FilingAcquisitionError("Dayu meta files must be an array")
        if self.market == "HK":
            provider = _required_text(
                value.get("source_provider"), "Dayu source_provider"
            ).lower()
            if provider != "hkexnews":
                return None
            provider_document_id = _required_text(
                value.get("source_id"), "Dayu source_id"
            )
            source_url = _required_text(value.get("source_url"), "Dayu source_url")
            entry = next(
                (
                    item
                    for item in files
                    if isinstance(item, dict)
                    and item.get("source") == "original"
                    and str(item.get("name", "")).lower().endswith(".pdf")
                ),
                None,
            )
            language = value.get("source_language") or "zh"
        else:
            provider = "sec"
            provider_document_id = _required_text(
                value.get("accession_number"), "Dayu accession_number"
            )
            primary = _required_text(
                value.get("primary_document"), "Dayu primary_document"
            )
            entry = next(
                (
                    item
                    for item in files
                    if isinstance(item, dict) and item.get("name") == primary
                ),
                None,
            )
            source_url = (
                _required_text(entry.get("source_url"), "Dayu source_url")
                if isinstance(entry, dict)
                else ""
            )
            language = "en"
        if not isinstance(entry, dict):
            raise FilingAcquisitionError("Dayu primary source is missing")
        if request.provider and request.provider != provider:
            return None
        if (
            request.provider_document_id
            and request.provider_document_id != provider_document_id
        ):
            return None
        filename = _required_text(entry.get("name"), "Dayu filename")
        source = (meta_path.parent / filename).resolve(strict=True)
        _inside(source, self._workspace, name="Dayu source")
        if not source.is_file():
            raise FilingAcquisitionError("Dayu primary source is not a file")
        size = entry.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            size = source.stat().st_size
        digest = str(entry.get("sha256") or "").strip().lower()
        if not _SHA256_RE.fullmatch(digest):
            digest = _sha256_file(source)
        if _sha256_file(source) != digest or source.stat().st_size != size:
            raise FilingAcquisitionError("Dayu primary source does not match meta")
        mime_type = str(entry.get("content_type") or "").split(";", 1)[0].strip()
        if not mime_type:
            mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        candidate_id = f"{provider}:{provider_document_id}"
        self._assets[candidate_id] = _DayuAsset(source, digest, size, mime_type)
        return DownloadCandidate(
            candidate_id=candidate_id,
            provider=provider,
            provider_document_id=provider_document_id,
            market=self.market,
            entity=request.entity,
            title=str(
                value.get("source_title")
                or f"{request.entity} {form_type} {filing_date}"
            ).strip(),
            source_url=source_url,
            document_kind=request.document_kind,
            filing_date=filing_date,
            fiscal_year=fiscal_year,
            form_type=form_type,
            fiscal_period=fiscal_period,
            language=str(language),
            amended=bool(value.get("amended", False)),
            etag=entry.get("http_etag"),
            last_modified=entry.get("http_last_modified"),
            remote_size=size,
            adapter_payload_json=_canonical_json(
                {
                    "dayu_document_id": value.get("document_id"),
                    "primary_filename": filename,
                    "content_sha256": digest,
                }
            ),
        )

    def fetch(
        self, candidate: DownloadCandidate, staging_dir: Path
    ) -> DownloadReceipt:
        asset = self._assets.get(candidate.candidate_id)
        if asset is None or self._workspace is None:
            raise FilingAcquisitionError("Dayu candidate workspace is unavailable")
        try:
            source = asset.source_path.resolve(strict=True)
            _inside(source, self._workspace, name="Dayu source")
            staging_dir.mkdir(parents=True, exist_ok=True)
            allocated = staging_dir.resolve(strict=True)
            destination = _inside(
                allocated / _safe_component(source.name, limit=180),
                allocated,
                name="Dayu staging destination",
            )
            temporary = destination.with_name(destination.name + f".{os.getpid()}.tmp")
            try:
                shutil.copyfile(source, temporary)
                if (
                    _sha256_file(temporary) != asset.content_sha256
                    or temporary.stat().st_size != asset.byte_size
                ):
                    raise FilingAcquisitionError("Dayu staged copy is inconsistent")
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)
            return DownloadReceipt(
                candidate_id=candidate.candidate_id,
                provider=candidate.provider,
                provider_document_id=candidate.provider_document_id,
                source_url=candidate.source_url,
                staged_path=str(destination),
                content_sha256=asset.content_sha256,
                byte_size=asset.byte_size,
                mime_type=asset.mime_type,
                retrieved_at=_utc_now(),
                http_status=200,
                adapter_name=self.name,
                adapter_version=self.version,
                etag=candidate.etag,
                last_modified=candidate.last_modified,
            )
        finally:
            self.close()


def _destination_subdirectory(document_kind: str) -> Path:
    mapping = {
        "annual_report": Path("financial_reports") / "annual",
        "semi_annual_report": Path("financial_reports") / "semi_annual",
        "quarterly_report": Path("financial_reports") / "quarterly",
        "prospectus": Path("prospectus"),
        "broker_research": Path("research"),
        "research": Path("research"),
        "investor_relations": Path("investor_relations"),
        "news": Path("news"),
    }
    return mapping.get(document_kind, Path("other"))


class CanonicalSourceWriter:
    """Commit validated staging bytes into immutable raw+sidecar storage."""

    def __init__(self, config: AcquisitionConfig):
        self.config = config

    def _validated_staged(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> Path:
        if candidate.entity != request.entity or candidate.market != request.market:
            raise FilingAcquisitionError("candidate identity does not match request")
        if (
            candidate.candidate_id != receipt.candidate_id
            or candidate.provider != receipt.provider
            or candidate.provider_document_id != receipt.provider_document_id
            or candidate.source_url != receipt.source_url
        ):
            raise FilingAcquisitionError("receipt does not match candidate")
        staged = Path(receipt.staged_path).resolve(strict=True)
        request_staging = (
            self.config.staging_root / request.request_id.rsplit(":", 1)[-1]
        )
        _inside(staged, request_staging, name="staged_path")
        if not staged.is_file():
            raise FilingAcquisitionError("staged_path is not a file")
        if staged.stat().st_size != receipt.byte_size:
            raise FilingAcquisitionError("staged byte_size does not match receipt")
        if _sha256_file(staged) != receipt.content_sha256:
            raise FilingAcquisitionError("staged SHA-256 does not match receipt")
        if receipt.mime_type == "application/pdf":
            with staged.open("rb") as stream:
                if stream.read(5) != b"%PDF-":
                    raise FilingAcquisitionError("staged PDF failed magic validation")
        return staged

    def _same_hash_source(
        self, digest: str, request: SourceRequest
    ) -> tuple[Path, Path | None] | None:
        companies = self.config.company_wiki_root / "companies"
        if not companies.is_dir():
            return None
        for sidecar in companies.rglob("*.source.json"):
            try:
                payload = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue
            stored = _sidecar_value(payload, "content_sha256")
            if stored != digest:
                continue
            raw = _sidecar_raw_path(sidecar, payload).resolve(strict=True)
            _inside(raw, self.config.company_wiki_root, name="canonical_path")
            if (
                raw.is_file()
                and raw.stat().st_size > 0
                and _sha256_file(raw) == digest
            ):
                return raw, sidecar
        company_dirs = [
            path
            for path in companies.iterdir()
            if path.is_dir()
            and _normalize_identity(path.name) == _normalize_identity(request.entity)
        ]
        safe_company = companies / _safe_component(request.entity, limit=80)
        if safe_company.is_dir() and safe_company not in company_dirs:
            company_dirs.append(safe_company)
        for company_dir in company_dirs:
            company_raw = company_dir / "raw"
            if not company_raw.is_dir():
                continue
            for raw in company_raw.rglob("*"):
                if (
                    raw.is_file()
                    and not raw.name.endswith(".source.json")
                    and raw.stat().st_size > 0
                    and _sha256_file(raw) == digest
                ):
                    return raw.resolve(), None
        return None

    @staticmethod
    def _extension(receipt: DownloadReceipt) -> str:
        suffix = Path(receipt.staged_path).suffix.lower()
        if _SAFE_EXTENSION.fullmatch(suffix):
            return suffix
        return {
            "application/pdf": ".pdf",
            "text/html": ".html",
            "text/plain": ".txt",
            "application/json": ".json",
        }.get(receipt.mime_type, ".bin")

    def _destination(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> Path:
        filename = "_".join(
            (
                candidate.filing_date,
                _safe_component(candidate.provider, limit=24),
                _safe_component(candidate.provider_document_id, limit=64),
                _safe_component(candidate.title, limit=90),
            )
        ) + self._extension(receipt)
        destination = (
            self.config.company_wiki_root
            / "companies"
            / _safe_component(request.entity, limit=80)
            / "raw"
            / _destination_subdirectory(candidate.document_kind)
            / filename
        )
        return _inside(
            destination, self.config.company_wiki_root, name="canonical destination"
        )

    @staticmethod
    def _payload(
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
        *,
        canonical_path: Path | None = None,
    ) -> dict[str, Any]:
        payload = {
            "schema_version": "1.0",
            "request_id": request.request_id,
            "company_name": request.entity,
            "market": request.market,
            "security_id": request.security_id,
            "source_title": candidate.title,
            "provider": candidate.provider,
            "provider_document_id": candidate.provider_document_id,
            "source_url": candidate.source_url,
            "document_kind": candidate.document_kind,
            "form_type": candidate.form_type,
            "filing_date": candidate.filing_date,
            "fiscal_year": candidate.fiscal_year,
            "fiscal_period": candidate.fiscal_period,
            "language": candidate.language,
            "amended": candidate.amended,
            "content_sha256": receipt.content_sha256,
            "byte_size": receipt.byte_size,
            "mime_type": receipt.mime_type,
            "retrieved_at": receipt.retrieved_at,
            "adapter_name": receipt.adapter_name,
            "adapter_version": receipt.adapter_version,
            "etag": receipt.etag,
            "last_modified": receipt.last_modified,
            "request": request.to_dict(),
            "candidate": candidate.to_dict(),
            "receipt": receipt.to_dict(),
        }
        if canonical_path is not None:
            payload["canonical_path"] = str(canonical_path.resolve())
            payload["assertion_type"] = "exact_content_alias"
        return payload

    @staticmethod
    def _write_immutable(path: Path, payload: dict[str, Any]) -> None:
        encoded = (_canonical_json(payload) + "\n").encode("utf-8")
        if path.exists():
            if path.read_bytes() != encoded:
                raise FilingAcquisitionError("immutable provenance sidecar conflict")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + f".{os.getpid()}.{uuid4().hex}.tmp")
        try:
            temporary.write_bytes(encoded)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    def import_staged(
        self,
        request: SourceRequest,
        candidate: DownloadCandidate,
        receipt: DownloadReceipt,
    ) -> tuple[dict[str, Any], str]:
        staged = self._validated_staged(request, candidate, receipt)
        existing = self._same_hash_source(receipt.content_sha256, request)
        resolver = FilesystemSourceResolver(self.config)
        if existing is not None:
            raw, existing_sidecar = existing
            existing_payload = (
                json.loads(existing_sidecar.read_text(encoding="utf-8"))
                if existing_sidecar is not None
                else {}
            )
            existing_company = _sidecar_value(existing_payload, "company_name")
            existing_security = _sidecar_value(existing_payload, "security_id")
            if (
                existing_sidecar is not None
                and
                _normalize_identity(str(existing_company or ""))
                == _normalize_identity(request.entity)
                and (
                    request.security_id is None
                    or str(existing_security or "").upper()
                    == request.security_id.upper()
                )
            ):
                staged.unlink()
                handle = resolver.resolve(request)
                if handle is None:
                    raise FilingAcquisitionError(
                        "exact bytes exist but provenance does not satisfy request"
                    )
                return handle, "deduplicated_after_download"
            alias_root = (
                self.config.company_wiki_root
                / ".source_catalog"
                / "revenue-forecast"
                / "aliases"
            )
            alias = alias_root / f"{request.request_id.rsplit(':', 1)[-1]}.source.json"
            self._write_immutable(
                alias,
                self._payload(
                    request, candidate, receipt, canonical_path=raw
                ),
            )
            staged.unlink()
            handle = resolver.resolve(request)
            if handle is None:
                raise FilingAcquisitionError("exact-content alias did not resolve")
            return handle, "deduplicated_after_download"
        destination = self._destination(request, candidate, receipt)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and _sha256_file(destination) != receipt.content_sha256:
            destination = destination.with_name(
                destination.stem
                + "__"
                + receipt.content_sha256[:12]
                + destination.suffix
            )
        if destination.exists():
            raise FilingAcquisitionError("canonical destination already exists")
        sidecar = destination.with_name(destination.name + ".source.json")
        raw_temporary = destination.with_name(
            destination.name + f".{os.getpid()}.{uuid4().hex}.importing"
        )
        sidecar_temporary = sidecar.with_name(
            sidecar.name + f".{os.getpid()}.{uuid4().hex}.tmp"
        )
        payload = self._payload(request, candidate, receipt)
        try:
            shutil.copyfile(staged, raw_temporary)
            if (
                raw_temporary.stat().st_size != receipt.byte_size
                or _sha256_file(raw_temporary) != receipt.content_sha256
            ):
                raise FilingAcquisitionError("temporary canonical copy is inconsistent")
            sidecar_temporary.write_text(
                _canonical_json(payload) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            os.replace(raw_temporary, destination)
            try:
                os.replace(sidecar_temporary, sidecar)
            except Exception:
                destination.unlink(missing_ok=True)
                raise
        finally:
            raw_temporary.unlink(missing_ok=True)
            sidecar_temporary.unlink(missing_ok=True)
        staged.unlink()
        handle = resolver.resolve(request)
        if handle is None:
            raise FilingAcquisitionError("new canonical source did not resolve")
        return handle, "downloaded_new"


class AcquisitionManager:
    """Resolve first; download only when explicitly authorized."""

    def __init__(
        self,
        config: AcquisitionConfig,
        adapters: AdapterRegistry | None = None,
    ):
        self.config = config
        self.adapters = adapters

    def resolve(
        self,
        request: dict[str, Any],
        *,
        allow_download: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(allow_download, bool):
            raise TypeError("allow_download must be boolean")
        normalized, identity = _request_from_payload(request, config=self.config)
        resolver = FilesystemSourceResolver(self.config)
        existing = resolver.resolve(normalized)
        if existing is not None:
            existing["request_id"] = normalized.request_id
            existing["acquisition_status"] = "reused_before_download"
            if identity is not None:
                existing["company_identity"] = identity
            return existing
        if not allow_download:
            raise FilingAcquisitionError(
                "source is not reusable; download was not authorized"
            )
        if normalized.market not in _MARKETS or not normalized.security_id:
            raise FilingAcquisitionError(
                "explicit download requires verified market and security_id"
            )
        adapters = self.adapters or AdapterRegistry.from_config(self.config)
        adapter = adapters.for_market(normalized.market)
        candidates = adapter.discover(normalized)
        if not candidates:
            raise FilingAcquisitionError("downloader found no matching filing")
        if len(candidates) != 1:
            raise FilingAcquisitionError(
                "downloader returned multiple matching filings; request is ambiguous"
            )
        candidate = candidates[0]
        if candidate.market != normalized.market or candidate.entity != normalized.entity:
            raise FilingAcquisitionError("adapter candidate identity is inconsistent")
        request_staging = _inside(
            self.config.staging_root
            / normalized.request_id.rsplit(":", 1)[-1],
            self.config.staging_root,
            name="request staging",
        )
        request_staging.mkdir(parents=True, exist_ok=True)
        receipt = adapter.fetch(candidate, request_staging)
        handle, status = CanonicalSourceWriter(self.config).import_staged(
            normalized, candidate, receipt
        )
        handle["request_id"] = normalized.request_id
        handle["acquisition_status"] = status
        if identity is not None:
            handle["company_identity"] = identity
        return handle


def resolve_filing(
    *,
    request: dict[str, Any],
    config_path: Path | None = None,
    allow_download: bool = False,
    adapters: AdapterRegistry | None = None,
) -> dict[str, Any]:
    """Return one capture-ready handle using the standalone skill runtime."""

    config = load_acquisition_config(config_path)
    return AcquisitionManager(config, adapters).resolve(
        request, allow_download=allow_download
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="revenue-filing-acquisition",
        description="Reuse or explicitly download a filing into a configured data root.",
    )
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--request-file", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="strict")
        if args.request_file is not None:
            request = json.loads(args.request_file.read_text(encoding="utf-8"))
        else:
            request = json.loads(sys.stdin.read())
        if not isinstance(request, dict):
            raise FilingAcquisitionError("request must be a JSON object")
        handle = resolve_filing(
            request=request,
            config_path=args.config,
            allow_download=args.allow_download,
        )
        json.dump(
            {
                "schema_version": "1.0",
                "status": "capture_ready",
                "handle": handle,
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    except FilingAcquisitionError as exc:
        json.dump(
            {
                "schema_version": "1.0",
                "status": "error",
                "error": _redact(str(exc)),
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 2
    except Exception as exc:
        json.dump(
            {
                "schema_version": "1.0",
                "status": "fatal",
                "error": _redact(str(exc)),
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 1


__all__ = [
    "ACQUISITION_SCHEMA_VERSION",
    "CONFIG_SCHEMA_VERSION",
    "AcquisitionConfig",
    "AcquisitionManager",
    "AdapterCommandSpec",
    "AdapterRegistry",
    "CanonicalSourceWriter",
    "DayuCliAdapter",
    "DownloadCandidate",
    "DownloadReceipt",
    "FilingAcquisitionError",
    "FilesystemSourceResolver",
    "JsonCommandAdapter",
    "SourceRequest",
    "load_acquisition_config",
    "main",
    "resolve_filing",
]


if __name__ == "__main__":
    raise SystemExit(main())
