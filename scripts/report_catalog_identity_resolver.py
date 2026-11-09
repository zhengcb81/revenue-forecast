"""Owner-installed trusted StockWiki identity resolver (G-RF-ID-01).

This module is the thin trusted bridge between ``report_catalog.import_w09``
and the StockWiki public dashboard identity bridge CLI.  It creates no
identity authority: it launches the owner-deployed public CLI with a fixed
argv, then binds the returned evidence to the *actual* response — the
lookup hash is recomputed from the response payload itself, so caller JSON
or a self-claimed hash can never masquerade as a StockWiki resolution.

Trust rules pinned by the dashboard extension card:

* The interpreter, owner root and CLI endpoint come only from a trusted
  deployment config file (``RF_IDENTITY_BRIDGE_CONFIG`` or an explicit
  path) — never from a Dashboard DTO or caller identity JSON.  The CLI must
  live inside the configured owner code root. Optional ``sw_root`` pins an
  existing business workspace and selects the fixed public identity CLI; when
  absent, the original owner CLI default is preserved.
* Fixed argv and stdin, bounded timeout and output size, no shell, no
  network, no cross-repo import, no direct database or glob access.
* Fail closed on every anomaly: nonzero exit, invalid JSON, schema drift,
  subject mismatch, path leakage, oversized output, timeout, or a receipt
  hash that does not reproduce from the actual payload.
* Only ``resolution_status == "resolved"`` yields evidence; honest negatives
  (``not_found``, ``multi_listing_unscoped``, ``identity_not_verified``,
  ``owner_evidence_unavailable``, ``no_active_listing``) and
  ``owner_offline`` surface as distinct named refusals.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

BRIDGE_SCHEMA_VERSION = "stockwiki.dashboard_identity/1"
ENV_CONFIG = "RF_IDENTITY_BRIDGE_CONFIG"
MAX_CONFIG_BYTES = 65536
TIMEOUT_FLOOR_SECONDS = 1
TIMEOUT_CEILING_SECONDS = 60
DEFAULT_TIMEOUT_SECONDS = 20
OUTPUT_FLOOR_BYTES = 4096
OUTPUT_CEILING_BYTES = 1048576
DEFAULT_MAX_OUTPUT_BYTES = 262144

RESOLVED_STATUSES_NON_NEGATIVE = (
    "multi_listing_unscoped",
    "identity_not_verified",
    "owner_evidence_unavailable",
    "no_active_listing",
    "not_found",
)

_ENTITY_ID_RE = re.compile(
    r"^ENT_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_LISTING_ID_RE = re.compile(
    r"^LST_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_PATH_RE = re.compile(r"(?:[A-Za-z]:[\\/]|\\\\|/(?:Users|home|tmp|var)/)")
_PYTHON_NAMES = {"python.exe", "python", "python3.exe", "python3", "py.exe"}


class IdentityBridgeError(Exception):
    """A named fail-closed refusal from the trusted identity seam."""

    def __init__(self, error_code: str, detail: str = "") -> None:
        self.error_code = error_code
        self.detail = detail
        super().__init__(f"{error_code}: {detail}" if detail else error_code)


@dataclass(frozen=True)
class BridgeConfig:
    """Trusted deployment configuration for the StockWiki bridge CLI."""

    python: Path
    cli: Path
    owner_root: Path
    timeout_seconds: int
    max_output_bytes: int
    sw_root: Path | None = None


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _bounded_read(path: Path, limit: int) -> bytes:
    data = path.open("rb").read(limit + 1)
    if len(data) > limit:
        raise IdentityBridgeError("bridge_config_too_large", "deployment config exceeds its bound")
    return data


def load_bridge_config(path: str | Path | None = None) -> BridgeConfig:
    """Load and strictly validate the trusted deployment config."""
    location = Path(path) if path is not None else None
    if location is None:
        raw_env = os.environ.get(ENV_CONFIG)
        if not raw_env:
            raise IdentityBridgeError(
                "bridge_config_unavailable",
                "no trusted identity bridge config: set " + ENV_CONFIG,
            )
        location = Path(raw_env)
    if not location.is_file():
        raise IdentityBridgeError("bridge_config_unavailable", "deployment config file missing")
    try:
        config = json.loads(_bounded_read(location, MAX_CONFIG_BYTES).decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise IdentityBridgeError("bridge_config_invalid", exc.__class__.__name__) from exc
    if not isinstance(config, dict):
        raise IdentityBridgeError("bridge_config_invalid", "config must be a JSON object")
    for key in ("python", "cli", "owner_root"):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise IdentityBridgeError("bridge_config_invalid", f"{key} must be a non-empty string")
        if not Path(value).is_absolute():
            raise IdentityBridgeError("bridge_config_invalid", f"{key} must be absolute")
    python = Path(config["python"])
    cli = Path(config["cli"])
    owner_root = Path(config["owner_root"])
    if python.name.lower() not in _PYTHON_NAMES or not python.is_file():
        raise IdentityBridgeError("bridge_config_invalid", "python interpreter is not trusted")
    resolved_cli = cli.resolve()
    resolved_root = owner_root.resolve()
    if not resolved_root.is_dir():
        raise IdentityBridgeError("bridge_config_invalid", "owner_root is not a directory")
    if resolved_cli.suffix != ".py" or not resolved_cli.is_relative_to(resolved_root):
        raise IdentityBridgeError(
            "bridge_config_invalid", "bridge CLI must be a .py inside the owner root"
        )
    sw_root = None
    if "sw_root" in config:
        workspace = config["sw_root"]
        if not isinstance(workspace, str) or not workspace.strip() or "\x00" in workspace:
            raise IdentityBridgeError("bridge_config_invalid", "sw_root must be an absolute existing directory")
        candidate = Path(workspace)
        if not candidate.is_absolute():
            raise IdentityBridgeError("bridge_config_invalid", "sw_root must be an absolute existing directory")
        try:
            sw_root = candidate.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            raise IdentityBridgeError("bridge_config_invalid", "sw_root must be an absolute existing directory") from exc
        if not sw_root.is_dir():
            raise IdentityBridgeError("bridge_config_invalid", "sw_root must be an absolute existing directory")
        # The explicit workspace protocol belongs only to the fixed public CLI.
        if resolved_cli != resolved_root / "dashboard_identity_bridge_cli.py" or not resolved_cli.is_file():
            raise IdentityBridgeError("bridge_config_invalid", "sw_root requires the fixed public identity CLI")
    timeout_raw = config.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
    output_raw = config.get("max_output_bytes", DEFAULT_MAX_OUTPUT_BYTES)
    if not isinstance(timeout_raw, int) or isinstance(timeout_raw, bool):
        raise IdentityBridgeError("bridge_config_invalid", "timeout_seconds must be an integer")
    if not isinstance(output_raw, int) or isinstance(output_raw, bool):
        raise IdentityBridgeError("bridge_config_invalid", "max_output_bytes must be an integer")
    timeout = min(max(timeout_raw, TIMEOUT_FLOOR_SECONDS), TIMEOUT_CEILING_SECONDS)
    output = min(max(output_raw, OUTPUT_FLOOR_BYTES), OUTPUT_CEILING_BYTES)
    return BridgeConfig(
        python=python, cli=resolved_cli, owner_root=resolved_root,
        timeout_seconds=timeout, max_output_bytes=output, sw_root=sw_root,
    )


def _require_id(value: str, pattern: re.Pattern[str], code: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise IdentityBridgeError(code, "identifier must be a prefixed UUIDv4")
    return value


def _assert_pathless(value: Any) -> None:
    if isinstance(value, dict):
        for child in value.values():
            _assert_pathless(child)
    elif isinstance(value, list):
        for child in value:
            _assert_pathless(child)
    elif isinstance(value, str) and _PATH_RE.search(value):
        raise IdentityBridgeError("bridge_path_leak", "bridge response contains a physical locator")


def _payload_sha256(payload: dict[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "lookup_receipt_sha256"}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def _stderr_code(raw: bytes) -> str | None:
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError):
        return None
    if isinstance(decoded, dict) and isinstance(decoded.get("error_code"), str):
        return decoded["error_code"]
    return None


def resolve_identity(
    entity_id: str, *, config: BridgeConfig, listing_id: str | None = None
) -> dict[str, Any]:
    """Perform one real public lookup and return verified evidence, fail closed."""
    _require_id(entity_id, _ENTITY_ID_RE, "identity_input_invalid")
    if listing_id is not None:
        _require_id(listing_id, _LISTING_ID_RE, "identity_input_invalid")
    argv = [str(config.python), str(config.cli), "resolve", "--entity-id", entity_id]
    if listing_id is not None:
        argv += ["--listing-id", listing_id]
    if config.sw_root is not None:
        argv += ["--root", str(config.sw_root)]
    try:
        completed = subprocess.run(
            argv, stdin=subprocess.DEVNULL, capture_output=True,
            timeout=config.timeout_seconds, cwd=config.owner_root,
        )
    except subprocess.TimeoutExpired as exc:
        raise IdentityBridgeError("bridge_timeout", "identity bridge exceeded its time bound") from exc
    except OSError as exc:
        raise IdentityBridgeError("bridge_unavailable", exc.__class__.__name__) from exc
    if completed.returncode != 0:
        raise IdentityBridgeError(
            "bridge_error", _stderr_code(completed.stderr) or f"exit_{completed.returncode}"
        )
    stdout = completed.stdout or b""
    if len(stdout) > config.max_output_bytes:
        raise IdentityBridgeError("bridge_output_too_large", "identity bridge exceeded its size bound")
    try:
        response = json.loads(stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise IdentityBridgeError("bridge_response_invalid", "response is not JSON") from exc
    if not isinstance(response, dict):
        raise IdentityBridgeError("bridge_response_invalid", "response must be a JSON object")
    if response.get("schema_version") != BRIDGE_SCHEMA_VERSION:
        raise IdentityBridgeError("bridge_schema_mismatch", repr(response.get("schema_version")))
    if response.get("command") != "resolve" or response.get("authority") != "stockwiki":
        raise IdentityBridgeError("bridge_response_invalid", "response is not a stockwiki resolve")
    if response.get("entity_id") != entity_id:
        raise IdentityBridgeError("identity_subject_mismatch", "response resolves a different entity")
    entity_block = response.get("entity")
    if not isinstance(entity_block, dict):
        raise IdentityBridgeError("bridge_response_invalid", "resolve must carry an entity block")
    if entity_block.get("entity_id") != entity_id:
        raise IdentityBridgeError("identity_subject_mismatch", "entity block names another subject")
    _assert_pathless(response)
    claimed = response.get("lookup_receipt_sha256")
    if not isinstance(claimed, str) or not _HEX64_RE.fullmatch(claimed):
        raise IdentityBridgeError("bridge_receipt_forged", "receipt hash is not a sha256")
    if _payload_sha256(response) != claimed:
        raise IdentityBridgeError("bridge_receipt_forged", "receipt hash does not bind this response")
    status = response.get("resolution_status")
    if status == "owner_offline":
        raise IdentityBridgeError("identity_owner_offline", "stockwiki identity owner is offline")
    if status != "resolved":
        if status not in RESOLVED_STATUSES_NON_NEGATIVE:
            raise IdentityBridgeError("bridge_response_invalid", f"unknown resolution_status {status!r}")
        raise IdentityBridgeError("identity_not_resolved", str(status))
    display_name = response.get("display_name")
    source_revision = response.get("source_revision")
    if not isinstance(display_name, str) or not display_name.strip():
        raise IdentityBridgeError("bridge_response_invalid", "resolved response lacks a display name")
    if not isinstance(source_revision, str) or not source_revision.strip():
        raise IdentityBridgeError("bridge_response_invalid", "resolved response lacks a data revision")
    return {
        "authority": "stockwiki",
        "entity_id": entity_id,
        "resolution_status": "resolved",
        "source_revision": source_revision,
        "lookup_receipt_sha256": claimed,
        "display_name": display_name,
    }


def make_identity_resolver(
    config: BridgeConfig, *, listing_id: str | None = None
) -> Callable[[str], dict[str, Any]]:
    """Build the owner-installed callback ``import_w09`` demands."""

    def resolver(entity_id: str) -> dict[str, Any]:
        return resolve_identity(entity_id, config=config, listing_id=listing_id)

    return resolver


def _main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin probe helper
    args = argv if argv is not None else sys.argv[1:]
    entity_id = args[0]
    listing_id = args[1] if len(args) > 1 else None
    config = load_bridge_config()
    evidence = resolve_identity(entity_id, config=config, listing_id=listing_id)
    print(_canonical(evidence))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
