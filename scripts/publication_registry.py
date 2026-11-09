"""Rebuildable publication discovery index, not artifact-use permission.

Each new row is independently hashed and fsync'd. A missing, corrupt, or
unwritable history cannot invalidate a self-contained, validated result.
Saved artifacts retain their own input/result hashes and validation rules;
``rebuild_publications`` reconstructs this optional index from those artifacts.
Explicit legacy lookup/audit still checks historical chained-row integrity.
No chmod or host-signature requirement is imposed by index maintenance.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contracts.evidence import ForecastInputError, canonical_sha256
from analysis.confidence import confidence_calculation_version

REGISTRY_FILE = "publications.jsonl"
ENV_REGISTRY = "REVENUE_PUBLICATION_REGISTRY"
DEFAULT_PUBLISHER = "revenue-forecast"


class RegistryError(RuntimeError):
    """Raised when the registry is missing, corrupt, or unavailable."""



def _confidence_revision(confidence: Any) -> str:
    """Use the scoring owner's finite revisions, never arbitrary group labels."""
    if not isinstance(confidence, dict):
        raise RegistryError("invalid confidence calculation version container")
    try:
        return confidence_calculation_version(confidence)
    except ForecastInputError as exc:
        raise RegistryError(str(exc)) from exc


def _entry_confidence_revision(entry: dict[str, Any]) -> str:
    # Missing means historical stable-fsum/1. Do not mutate/re-hash old rows.
    return _confidence_revision(
        {"calculation_version": entry["confidence_calculation_version"]}
        if "confidence_calculation_version" in entry else {}
    )


def registry_file() -> Path:
    """Resolve the registry path: env override (file or directory), else repo default."""
    env = os.environ.get(ENV_REGISTRY)
    if env:
        path = Path(env).expanduser()
        if path.is_dir():
            return path / REGISTRY_FILE
        return path
    return Path(__file__).resolve().parents[1] / "artifacts" / "registry" / REGISTRY_FILE


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_entries() -> list[dict[str, Any]]:
    """Read and verify every line (hash + chain).  Corrupt line -> RegistryError."""
    path = registry_file()
    if not path.exists():
        return []
    return validate_registry_text(path.read_text(encoding="utf-8"))


def validate_registry_text(text: str) -> list[dict[str, Any]]:
    """Verify legacy chained and current independent index rows."""
    entries: list[dict[str, Any]] = []
    previous: str | None = None
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RegistryError(f"registry line {lineno}: invalid JSON: {exc}") from exc
        claimed = entry.get("line_sha256")
        payload = {key: value for key, value in entry.items() if key != "line_sha256"}
        if canonical_sha256(payload) != claimed:
            raise RegistryError(f"registry line {lineno}: hash mismatch (tampered)")
        if entry.get("index_schema_version") != "publication-index/2" and entry.get("prev_line_sha256") != previous:
            raise RegistryError(
                f"registry line {lineno}: chain break (prev_line_sha256 mismatch)"
            )
        _entry_confidence_revision(entry)
        previous = claimed
        entries.append(entry)
    return entries


def _clear_read_only(path: Path) -> None:
    """Retired compatibility hook; indexes no longer change filesystem modes."""


def _append(entry: dict[str, Any]) -> dict[str, str]:
    """Append a rebuildable independent index row, never consult old authority.

    An index cannot establish source authenticity. Legacy chained rows remain
    inspectable by explicit audit, but their corruption cannot veto a new row
    or a valid self-contained forecast. No chmod or history-wide preflight.
    """
    path = registry_file()
    payload = {key: value for key, value in entry.items() if key != "line_sha256"}
    payload["index_schema_version"] = "publication-index/2"
    line = {**payload, "line_sha256": canonical_sha256(payload)}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("ab+") as handle:
            handle.seek(0, 2)
            if handle.tell():
                handle.seek(-1, 2)
                if handle.read(1) != b"\n":
                    handle.write(b"\n")
            handle.write(json.dumps(line, ensure_ascii=False, sort_keys=True).encode() + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
    except OSError:
        logging.getLogger(__name__).warning("publication_index_unavailable: validated artifact remains usable")
        return {"status": "unavailable", "reason": "publication_index_io_error"}
    return {"status": "indexed"}


def input_summary_sha256(result: dict[str, Any]) -> str:
    """Hash of the identity fields a human would use to recognize the input."""
    return canonical_sha256(
        {
            "company_name": result.get("company_name"),
            "as_of_date": result.get("as_of_date"),
            "forecast_version": result.get("forecast_version"),
        }
    )


def register_publication(
    result: dict[str, Any],
    *,
    artifact_type: str = "forecast",
    artifact_id: str | None = None,
    note: str = "run_forecast formal",
    validation_status: str = "validated",
) -> dict[str, str]:
    """Index a published artifact's anchor.  Raises RegistryError on failure.

    ZR-701: *validation_status* distinguishes explicit Draft artifacts
    (``"draft"`` — computed but not strong-validated; the entry carries no
    validated receipt anchor) from Formal artifacts (``"validated"`` —
    strong-validated publication).  The key is additive: pre-ZR-701 lines
    simply lack it and stay readable.
    """
    receipt = result.get("publication_receipt")
    return _append(
        {
            "registered_at": _utc_now_iso(),
            "input_sha256": result["input_sha256"],
            "result_sha256": result["result_sha256"],
            "receipt_sha256": canonical_sha256(receipt) if isinstance(receipt, dict) else None,
            "engine_version": result.get("engine_version"),
            "schema_version": result.get("schema_version"),
            "confidence_calculation_version": _confidence_revision(result.get("confidence", {})),
            "publisher": os.environ.get("REVENUE_PUBLISHER", DEFAULT_PUBLISHER),
            "input_summary_sha256": input_summary_sha256(result),
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "note": note,
            "validation_status": validation_status,
        }
    )


def register_snapshot(snapshot: dict[str, Any]) -> dict[str, str]:
    """Register a backtest snapshot's anchor (snapshot_id <-> input_sha256)."""
    forecast = snapshot.get("forecast_result", {})
    if not isinstance(forecast, dict):
        raise RegistryError("invalid confidence calculation version forecast container")
    revision = _confidence_revision(forecast.get("confidence", {}))
    return _append(
        {
            "registered_at": _utc_now_iso(),
            "input_sha256": snapshot["input_sha256"],
            "result_sha256": snapshot["forecast_result_sha256"],
            "receipt_sha256": canonical_sha256(snapshot["forecast_result"].get("publication_receipt"))
            if isinstance(snapshot.get("forecast_result"), dict)
            else None,
            "engine_version": snapshot.get("engine_version"),
            "schema_version": snapshot.get("forecast_schema_version"),
            "confidence_calculation_version": revision,
            "publisher": os.environ.get("REVENUE_PUBLISHER", DEFAULT_PUBLISHER),
            "input_summary_sha256": input_summary_sha256(snapshot.get("forecast_result", {})),
            "artifact_type": "snapshot",
            "artifact_id": snapshot.get("snapshot_id"),
            "note": "revenue_backtest create",
        }
    )


def lookup(input_sha256: str) -> list[dict[str, Any]]:
    """Return the full publication history of one input anchor (raises on corruption)."""
    return [entry for entry in _read_entries() if entry["input_sha256"] == input_sha256]


def is_registered(input_sha256: str) -> bool:
    """True when the anchor appears in the registry (fail-closed on corruption)."""
    return any(entry["input_sha256"] == input_sha256 for entry in _read_entries())


def audit(result_files: list[Path] | None = None, *, since: str | None = None) -> list[str]:
    """Report registry problems: corruption, same-anchor conflicts, unregistered claims."""
    problems: list[str] = []
    try:
        entries = _read_entries()
    except RegistryError as exc:
        return [str(exc)]
    if since is not None:
        entries = [entry for entry in entries if entry.get("registered_at", "") >= since]
    # Conflict = the same input anchored to different results *within one
    # engine/schema/confidence generation and artifact type* (D2 forgery).
    # Cross-version result differences (same input re-run under a newer
    # engine) and forecast-vs-snapshot pairs (different artifact types
    # referencing the same anchor) are normal history.
    by_generation: dict[tuple[str, str | None, str | None, str, str], set[str]] = {}
    for entry in entries:
        generation = (
            entry["input_sha256"],
            entry.get("engine_version"),
            entry.get("schema_version"),
            entry.get("artifact_type", "forecast"),
            _entry_confidence_revision(entry),
        )
        by_generation.setdefault(generation, set()).add(entry["result_sha256"])
    for (anchor, engine, schema, artifact_type, revision), result_hashes in by_generation.items():
        if len(result_hashes) > 1:
            problems.append(
                f"conflict: input {anchor[:16]}... (engine {engine}, schema {schema}, "
                f"{artifact_type}, confidence {revision}) registered {len(result_hashes)} distinct result hashes"
            )
    registered_anchors = {entry["input_sha256"] for entry in entries}
    for path in result_files or []:
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"unreadable result artifact {path}: {exc}")
            continue
        claimed = artifact.get("input_sha256")
        if not isinstance(claimed, str) or claimed not in registered_anchors:
            problems.append(
                f"unregistered claim: {path} anchors input "
                f"{(claimed or '?')[:16]} which was never registered"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query and audit the append-only publication registry"
    )
    command = parser.add_subparsers(dest="command", required=True)
    lookup_parser = command.add_parser("lookup", help="publication history of one input anchor")
    lookup_parser.add_argument("--input-sha", required=True)
    audit_parser = command.add_parser("audit", help="detect conflicts / corruption / unregistered claims")
    audit_parser.add_argument("--result", action="append", type=Path, help="result artifact to cross-check")
    audit_parser.add_argument("--since", help="only consider entries registered at/after this ISO timestamp")
    args = parser.parse_args()
    if args.command == "lookup":
        for entry in lookup(args.input_sha):
            print(json.dumps(entry, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "audit":
        problems = audit(args.result, since=args.since)
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    return 2


if __name__ == "__main__":
    sys.exit(main())


def rebuild_publications(result_files: list[Path], *, output_path: Path) -> dict[str, int]:
    """Rebuild discovery data from individually validated persisted artifacts.

    This explicit maintenance entry never edits the input reports or trusts an
    old index. Validation and actual output-write errors remain real failures.
    """
    from revenue_report import validate_forecast_output
    rows = []
    for path in result_files:
        result = json.loads(path.read_text(encoding="utf-8"))
        validate_forecast_output(result)
        payload = {"index_schema_version": "publication-index/2", "registered_at": _utc_now_iso(),
            "input_sha256": result["input_sha256"], "result_sha256": result["result_sha256"],
            "receipt_sha256": canonical_sha256(result["publication_receipt"]),
            "engine_version": result["engine_version"], "schema_version": result["schema_version"],
            "confidence_calculation_version": _confidence_revision(result.get("confidence", {})),
            "publisher": DEFAULT_PUBLISHER, "artifact_type": "forecast", "artifact_id": None,
            "note": "rebuilt_from_validated_artifact", "validation_status": "validated"}
        rows.append({**payload, "line_sha256": canonical_sha256(payload)})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(output_path.name + f".{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output_path)
    finally:
        temporary.unlink(missing_ok=True)
    return {"indexed": len(rows)}
