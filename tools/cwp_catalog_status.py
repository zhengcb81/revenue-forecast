"""Read the public CWP catalog status without opening the owner's storage."""

from __future__ import annotations

import builtins
import json
import subprocess
import sys
from pathlib import Path


class CatalogStatusUnavailable(RuntimeError):
    """A CWP status check could not run to a usable public response."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def _catalog_status_cause(stderr: str) -> str | None:
    """Project only pathless causes from CWP's public failure output."""
    try:
        payload = json.loads(stderr)
    except json.JSONDecodeError:
        # Invalid config can fail before the owner emits its JSON envelope.
        tail = stderr.rstrip().rsplit("\n", 1)[-1]
        name, separator, _message = tail.partition(":")
        if not separator or "Traceback (most recent call last):" not in stderr:
            return None
        if name == "company_wiki.source_catalog.config.CatalogConfigError":
            return "CatalogConfigError"
        exception_type = getattr(builtins, name, None)
        if isinstance(exception_type, type) and issubclass(exception_type, Exception):
            return name
        return None

    if not isinstance(payload, dict) or payload.get("status") != "failed":
        return None
    code = payload.get("error_type")
    # The published CWP catalog status error taxonomy. Only the diagnostic
    # gets projected here. An unfamiliar error is still an owner failure.
    if code not in ("catalog_busy", "catalog_locked", "db_timeout", "worker_paused",
                    "legacy_evidence_archived", "fatal"):
        return None
    if code == "fatal":
        reason = payload.get("reason")
        if reason in ("catalog_missing", "catalog_unavailable"):
            code = reason
        elif "reason" not in payload and isinstance(message := payload.get("error"), str):
            # N-1 CWP releases provided only a human diagnostic for these causes.
            if message.startswith("catalog does not exist (not created, not touched):"):
                code = "catalog_missing"
            elif message.startswith("cannot open catalog read-only:"):
                code = "catalog_unavailable"
    return f"{code} (retryable)" if payload.get("retryable") is True else code


def read_catalog_status(config: Path) -> dict[str, int]:
    """Return the reported count fields; keep known public failures pathless."""
    command = [sys.executable, "-B", "-m", "company_wiki.source_catalog.cli",
               "--config", str(config), "status"]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CatalogStatusUnavailable(
            type(exc).__name__, f"CWP status command failed: {type(exc).__name__}",
        ) from exc
    if result.returncode != 0:
        cause = _catalog_status_cause(result.stderr)
        detail = f"CWP status command failed (exit {result.returncode})"
        raise CatalogStatusUnavailable(
            cause.partition(" ")[0] if cause else "owner_command_refused",
            f"{detail}: {cause}" if cause else detail,
        )

    try:
        status = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise CatalogStatusUnavailable(
            "owner_response_invalid", "CWP status returned invalid JSON",
        ) from exc
    count_keys = ("documents", "sources", "active_locations", "missing_locations")
    if not isinstance(status, dict) or any(
        type(status.get(key)) is not int or status[key] < 0 for key in count_keys
    ):
        raise CatalogStatusUnavailable(
            "owner_status_invalid", "CWP status did not report valid catalog counts",
        )
    return {key: status[key] for key in count_keys}
