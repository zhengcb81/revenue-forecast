"""ZR-001 replay: filing-fetch production counterexamples (hermetic).

F1 — external-root handles are default-rejected: production
``_handle_from_resolution`` calls ``validate_handle`` without a
RootPolicySnapshot, so containment falls back to ``<wiki>/companies``; a
Dropbox-root handle is rejected at the filing boundary.

F2 — SQLite lock errors are misclassified as fatal: only a structured
``CatalogOperationLockedError`` maps to ``catalog_locked`` (retryable); the
raw ``OperationalError("database is locked")`` form is fatal, so the
deadline-aware retry loop never runs for it.

Usage:  python -B assurance/unified_completion/replays/zr001_filing.py

Emits evidence files into ``replays/evidence/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FILING_ROOT = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
sys.path.insert(0, str(FILING_ROOT / "scripts"))

import fetch_filing  # noqa: E402
from filing_contracts import FilingFetchError, validate_handle  # noqa: E402

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_evidence(name: str, payload: dict, evidence_dir: Path) -> Path:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / name
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def f1_external_root_default_rejected(root: Path) -> dict:
    """A capture-ready handle whose canonical file lives under a Dropbox-like
    root is rejected because production passes no policy snapshot."""
    wiki_root = root / "wiki_root"
    (wiki_root / "companies").mkdir(parents=True, exist_ok=True)
    dropbox = root / "dropbox_root" / "Stock"
    dropbox.mkdir(parents=True)
    pdf = dropbox / "some_broker_file.pdf"
    pdf.write_bytes(b"%PDF-1.4\n" + b"x" * 64)
    handle = {
        "request_id": "zr001-f1",
        "document_id": "doc-zr001-f1",
        "source_id": "src-zr001-f1",
        "title": "Some broker report",
        "published_date": "2026-03-20",
        "https_url": "https://example.com/report.pdf",
        "canonical_path": str(pdf),
        "snapshot_sha256": sha256_bytes(pdf.read_bytes()),
        "retrieved_at": "2026-08-14T00:00:00Z",
        "provider": "manual",
        "provider_document_id": "zr001-f1",
        "collector_name": "replay",
        "collector_version": "1",
        "byte_size": pdf.stat().st_size,
        "mime_type": "application/pdf",
        "capture_ready": True,
    }
    request = {
        "company_query": "Replay Co",
        "document_kind": "broker_research",
        "fiscal_year": 2026,
        "as_of_date": "2026-08-14",
    }
    try:
        validate_handle(handle, request, wiki_root)
        outcome = "accepted"
        message = ""
    except FilingFetchError as exc:
        outcome = "rejected"
        message = f"code={exc.code}; {exc}"
    # The policy-snapshot path exists in the signature; production never
    # supplies it.  Pin that call-site fact with line numbers.
    source = (FILING_ROOT / "scripts" / "fetch_filing.py").read_text(encoding="utf-8")
    call_line = next(
        (
            lineno
            for lineno, line in enumerate(source.splitlines(), start=1)
            if line.strip() == "validate_handle(handle, request, root)"
        ),
        None,
    )
    return {
        "handle_root": str(dropbox),
        "wiki_root": str(wiki_root),
        "outcome": outcome,
        "message": message,
        "production_call_site": {
            "file": "scripts/fetch_filing.py",
            "line": call_line,
            "passes_policy_snapshot": False,
        },
        "observed_at_utc": utc_now(),
    }


def f2_lock_error_misclassified(root: Path) -> dict:
    """The production subprocess wrapper maps only structured
    CatalogOperationLockedError to ``catalog_locked``; a raw SQLite
    OperationalError('database is locked') stays fatal (retryable=False),
    so the retry loop never engages for the real lock form."""
    command = ["python", "-m", "company_wiki", "resolve", "{}"]
    outcomes = {}
    for label, stderr_text in (
        (
            "raw_sqlite_operational_error",
            '{"error_type": "OperationalError", "error": "database is locked"}',
        ),
        (
            "structured_catalog_operation_locked",
            '{"error_type": "CatalogOperationLockedError", "error": "operation lock live"}',
        ),
    ):
        original = fetch_filing.subprocess.run

        def fake_run(*_args, **_kwargs):
            return subprocess.CompletedProcess(
                args=["python"],
                returncode=1,
                stdout="",
                stderr=stderr_text,
            )

        fetch_filing.subprocess.run = fake_run
        try:
            try:
                fetch_filing._run_company_wiki_json(
                    command=command,
                    root=root,
                    timeout_seconds=5.0,
                    action="resolve",
                )
                outcomes[label] = {"raised": False}
            except FilingFetchError as exc:
                outcomes[label] = {
                    "raised": True,
                    "code": exc.code,
                    "retryable": exc.retryable,
                }
        finally:
            fetch_filing.subprocess.run = original
    return {
        "outcomes": outcomes,
        "retry_loop_retries_only": "catalog_locked",
        "observed_at_utc": utc_now(),
    }


def product_code_hashes() -> dict:
    files = [
        "scripts/fetch_filing.py",
        "scripts/filing_contracts.py",
    ]
    return {
        rel: hashlib.sha256((FILING_ROOT / rel).read_bytes()).hexdigest()
        for rel in files
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=EVIDENCE_DIR,
        help="write evidence here (default: the sealed evidence dir)",
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="zr001_filing_") as tmp:
        root = Path(tmp)
        outputs = {
            "f1_external_root_default_rejected.json": f1_external_root_default_rejected(
                root
            ),
            "f2_lock_error_misclassified.json": f2_lock_error_misclassified(root),
        }
    filing_head = subprocess.run(
        ["git", "-C", str(FILING_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    for name, payload in outputs.items():
        payload["product_code_hashes"] = product_code_hashes()
        payload["filing_head"] = filing_head
        write_evidence(name, payload, args.evidence_dir)
    for name in sorted(outputs):
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
