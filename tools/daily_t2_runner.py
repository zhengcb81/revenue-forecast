"""Run RF's daily assurance against company-wiki's public read-only commands."""
from __future__ import annotations

if __package__:
    from .rf_owner_runtime import DiagnosticParser, Invocation, exit_cli, observed_entry
else:
    from rf_owner_runtime import DiagnosticParser, Invocation, exit_cli, observed_entry

from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import time

if __package__:
    from .cwp_catalog_status import CatalogStatusUnavailable, read_catalog_status
else:
    from cwp_catalog_status import CatalogStatusUnavailable, read_catalog_status

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT.parent / "company-wiki" / "config" / "source_catalog.yaml"
DEFAULT_REPORT_ROOT = PROJECT_ROOT / "assurance" / "runs"
OWNER_EXPORT = "company_wiki.source_catalog.source_export_v2_cli"


def _object(body: bytes | str) -> dict:
    try:
        value = json.loads(body)
    except (TypeError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _code(value: object, fallback: str) -> str:
    if isinstance(value, str) and value.isascii() and value.isidentifier() and value.islower():
        return value
    return fallback


def _identity_multiset(refs: object) -> Counter[tuple[str, str, str, int, str]] | None:
    if not isinstance(refs, list):
        return None
    identities = []
    for ref in refs:
        if not isinstance(ref, dict):
            return None
        document_id = ref.get("document_id")
        source_id = ref.get("source_id")
        sha = ref.get("content_sha256")
        size = ref.get("byte_size")
        media = ref.get("mime_type")
        if not (isinstance(document_id, str) and document_id
                and isinstance(source_id, str) and source_id
                and isinstance(sha, str) and sha
                and type(size) is int and size > 0
                and isinstance(media, str) and media):
            return None
        identities.append((document_id, source_id, sha, size, media))
    return Counter(identities)


def _verify_sources(config: Path, source_refs: list[dict]) -> tuple[dict, dict | None]:
    argv = [sys.executable, "-B", "-m", OWNER_EXPORT, "--config", str(config)]
    body = json.dumps({
        "schema_version": "2.0",
        "source_refs": source_refs,
        "evidence_spans": [],
    }).encode("utf-8")
    try:
        response = subprocess.run(argv, input=body, capture_output=True, timeout=60, check=False)
    except subprocess.TimeoutExpired:
        return {}, {"status": "unavailable", "reason": "owner_command_timeout"}
    except OSError:
        return {}, {"status": "unavailable", "reason": "owner_command_unavailable"}

    if response.returncode:
        reason = _object(response.stderr)
        return {}, {
            "status": _code(reason.get("status"), "unavailable"),
            "reason": _code(reason.get("reason"), "owner_command_refused"),
        }
    result = _object(response.stdout)
    if not result:
        return {}, {"status": "unavailable", "reason": "owner_response_invalid"}
    requested = _identity_multiset(source_refs)
    if requested is None or _identity_multiset(result.get("manifests")) != requested:
        return {}, {"status": "unavailable", "reason": "owner_export_reference_mismatch"}
    return result, None


def run_checks(
    catalog_config: Path,
    run_id: str,
    *,
    source_refs: list[dict] | None = None,
) -> tuple[dict, int]:
    checks: dict[str, dict] = {}
    problems: list[str] = []
    outcome = "ok"
    try:
        counts = read_catalog_status(catalog_config)
    except CatalogStatusUnavailable as exc:
        checks["catalog"] = {"status": "unavailable", "reason": exc.code}
        outcome = "blocked"
        problems.append(str(exc))
    else:
        checks["catalog"] = {"status": "available", **counts}
        if source_refs:
            bundle, refusal = _verify_sources(catalog_config, source_refs)
            if refusal:
                checks["source_verification"] = refusal
                outcome = (
                    "blocked" if refusal["status"] == "unavailable" else "not-ok"
                )
                problems.append(refusal["reason"])
            else:
                checks["source_verification"] = {
                    "status": "verified",
                    "source_count": len(source_refs),
                    "export_id": bundle.get("export_id"),
                }
    report = {
        "run_id": run_id,
        "checks": checks,
        "problems": problems,
        "triplet": {},
        "outcome": outcome,
        "ok": outcome == "ok",
    }
    return report, {"ok": 0, "not-ok": 1, "blocked": 2}[outcome]


@observed_entry
def main(argv: list[str] | None = None, *, runtime: Invocation) -> int:
    parser = DiagnosticParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-ref", action="append", type=Path, default=[],
                        help="Optional exact SourceRef JSON file to verify through the owner")
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args(argv)
    runtime.note_operation("daily-owner-read", external_work_possible=False)
    try:
        refs = [json.loads(path.read_bytes()) for path in args.source_ref]
    except (OSError, UnicodeError, json.JSONDecodeError):
        parser.error("could not read a SourceRef as JSON")
    run_id = args.run_id or time.strftime("%Y%m%dT%H%M%SZ")
    report, exit_code = run_checks(args.config.resolve(), run_id, source_refs=refs)
    out = args.report_root / run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report["checks"], ensure_ascii=False))
    if exit_code:
        runtime.note_native("daily_owner_read_failed")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(exit_cli(main))
