"""B.VR sampled-commit probe (question g): reproduce the B03 dispositions.

Run twice - once against a tree whose resolver.py is the pre-disposition blob
(2f1ddab^) and once against HEAD - to show red -> green.
usage: python b06_review_b03probe.py <tree_root> <out.json>
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1])
OUT = Path(sys.argv[2])
sys.path.insert(0, str(TREE / "src"))

from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.resolver import (  # noqa: E402
    SourceRequest,
    SourceResolver,
    _inside_configured_roots,
    _read_verified_bytes,
)

BODY = b"%PDF-1.4 b03-sampled-commit"
DIGEST = hashlib.sha256(BODY).hexdigest()


class _Root:
    def __init__(self, path: Path):
        self.path = path


def sidecar(**overrides) -> dict:
    payload = {
        "schema_version": "1.0",
        "canonical_entity_id": "ent-acme",
        "display_name": "Acme",
        "market": "US",
        "security_id": "ACME",
        "source_title": "Acme 2025 Annual Report",
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "period_end": "2025-12-31",
        "filing_date": "2026-02-20",
        "form_type": "10-K",
        "provider": "sec",
        "provider_document_id": "doc-1",
        "source_url": "https://sec.gov/x/2025",
        "content_sha256": DIGEST,
        "retrieved_at": "2026-02-21T00:00:00Z",
        "collector_name": "sec_edgar",
        "collector_version": "1.0",
    }
    payload.update(overrides)
    return payload


class CountingBudget:
    """Cancels only on the Nth read of `.cancelled` (a cancellation that lands
    after the last in-loop check)."""

    def __init__(self, turn_true_on: int):
        self.turn_true_on = turn_true_on
        self.reads = 0
        self._cancelled = False

    @property
    def cancelled(self) -> bool:
        self.reads += 1
        if self.reads >= self.turn_true_on:
            self._cancelled = True
        return self._cancelled

    @cancelled.setter
    def cancelled(self, value: bool) -> None:
        self._cancelled = value

    def cancel(self) -> None:
        self._cancelled = True

    def take_candidate(self) -> str:
        return ""

    def charge(self, size: int) -> str:
        return ""

    def begin_request(self) -> None:
        return None


def main() -> None:
    out: dict[str, object] = {"tree": str(TREE)}
    tmp = Path(tempfile.mkdtemp(prefix="b03rv-"))
    # --- g1: containment -------------------------------------------------
    inside = tmp / "inside"
    inside.mkdir()
    (inside / "a.pdf").write_bytes(BODY)
    sibling = tmp / "inside_sibling"
    sibling.mkdir()
    (sibling / "b.pdf").write_bytes(BODY)
    out["containment"] = {
        "normal_file_inside_root": _inside_configured_roots(
            inside / "a.pdf", (_Root(inside),)
        ),
        "the_root_itself": _inside_configured_roots(inside, (_Root(inside),)),
        "sibling_with_shared_prefix": _inside_configured_roots(
            sibling / "b.pdf", (_Root(inside),)
        ),
        "volume_root_contains_drive_file": _inside_configured_roots(
            inside / "a.pdf", (_Root(Path(inside.anchor)),)
        ),
        "different_drive": _inside_configured_roots(
            inside / "a.pdf", (_Root(Path("Z:/nope")),)
        ),
        "anchor": inside.anchor,
    }
    # --- fixture catalog for the byte path -------------------------------
    base = tmp / "companies"
    target_dir = base / "Acme" / "raw" / "financial_reports" / "annual"
    target_dir.mkdir(parents=True)
    (target_dir / "2025.pdf").write_bytes(BODY)
    (target_dir / "2025.pdf.source.json").write_text(
        json.dumps(sidecar(), ensure_ascii=False), encoding="utf-8"
    )
    cat = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".source_catalog",
            reusable_root_kinds=("company_raw",),
            roots=(
                RootSpec(
                    "company_raw",
                    base,
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    reusable_for_filing=True,
                    canonical_write_target="companies",
                ),
            ),
        )
    )
    cat.scan()
    resolution = SourceResolver(cat).resolve(
        SourceRequest(
            entity="Acme",
            market="US",
            security_id="ACME",
            document_kind="annual_report",
            form_type="10-K",
            fiscal_year=2025,
            provider="sec",
            provider_document_id="doc-1",
            as_of_date="2026-08-10",
            mode="exact",
        )
    )
    handle = resolution.matches[0]
    resolver = SourceResolver(cat)
    # --- g2: pinned expected_content_sha256 ------------------------------
    wrong = hashlib.sha256(b"another version").hexdigest()
    mismatch = resolver.read_verified_bytes(handle, expected_content_sha256=wrong)
    match = resolver.read_verified_bytes(handle, expected_content_sha256=DIGEST)
    out["pinned_expected_hash"] = {
        "handle_content_sha256": handle.content_sha256,
        "wrong_expected": {
            "status": mismatch.status,
            "reason": mismatch.reason,
            "data_is_none": mismatch.data is None,
            "byte_size": mismatch.byte_size,
            "reported_content_sha256": mismatch.content_sha256[:12],
        },
        "matching_expected": {
            "status": match.status,
            "reason": match.reason,
            "byte_size": match.byte_size,
            "digest_matches": bool(match.data)
            and hashlib.sha256(match.data).hexdigest() == DIGEST,
        },
    }
    # --- g2b: the reviewer's P1 scenario - handle names A, file holds B ---
    drifted_dir = tmp / "drifted" / "Acme" / "raw" / "financial_reports" / "annual"
    drifted_dir.mkdir(parents=True)
    other_body = b"%PDF-1.4 a DIFFERENT version (B)"
    other_digest = hashlib.sha256(other_body).hexdigest()
    (drifted_dir / "2025.pdf").write_bytes(other_body)
    (drifted_dir / "2025.pdf.source.json").write_text(
        json.dumps(sidecar(content_sha256=other_digest), ensure_ascii=False),
        encoding="utf-8",
    )
    cat2 = SourceCatalog(
        CatalogConfig(
            project_root=tmp,
            catalog_dir=tmp / ".drifted_catalog",
            reusable_root_kinds=("company_raw",),
            roots=(
                RootSpec(
                    "company_raw",
                    tmp / "drifted",
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    reusable_for_filing=True,
                    canonical_write_target="companies",
                ),
            ),
        )
    )
    cat2.scan()
    resolution2 = SourceResolver(cat2).resolve(
        SourceRequest(
            entity="Acme",
            market="US",
            security_id="ACME",
            document_kind="annual_report",
            form_type="10-K",
            fiscal_year=2025,
            provider="sec",
            provider_document_id="doc-1",
            as_of_date="2026-08-10",
            mode="exact",
        )
    )
    handle2 = resolution2.matches[0]
    # now the file moves to version B while the INDEX still names A
    (drifted_dir / "2025.pdf").write_bytes(b"%PDF-1.4 version B on disk")
    on_disk = hashlib.sha256((drifted_dir / "2025.pdf").read_bytes()).hexdigest()
    drifted = SourceResolver(cat2).read_verified_bytes(
        handle2, expected_content_sha256=on_disk
    )
    out["drifted_copy_caller_pins_the_bytes_on_disk"] = {
        "indexed_handle_sha256": handle2.content_sha256[:12],
        "bytes_on_disk_sha256": on_disk[:12],
        "status": drifted.status,
        "reason": drifted.reason,
        "bytes_returned": drifted.data is not None,
        "reported_content_sha256": str(drifted.content_sha256)[:12],
    }
    # --- g3: cancellation tail guard -------------------------------------
    tails = {}
    for turn_on in (1, 2, 3, 4, 5):
        budget = CountingBudget(turn_on)
        data, status, reason, detail = _read_verified_bytes(
            target_dir / "2025.pdf", expected_sha256=DIGEST, budget=budget
        )
        tails[f"cancel_on_access_{turn_on}"] = {
            "budget_accesses": budget.reads,
            "status": status or "(bytes returned)",
            "reason": reason,
            "reason_detail": detail,
            "bytes_returned": data is not None,
        }
    out["cancellation_tail_guard"] = tails
    out["cancellation_note"] = (
        "access #1 = entry check, #2/#3 = in-loop checks for a 1-chunk file, "
        "#4 = TAIL guard (post-2f1ddab only)"
    )
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
