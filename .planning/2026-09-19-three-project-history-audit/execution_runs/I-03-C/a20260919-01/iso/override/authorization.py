"""WU-4.3 + FC-801: authorization-bound minimal download (isolated
implementation card I-03-C).

I-03-A D6-frozen binding face for a DownloadAuthorization (schema 1.1):

- the receipt binds the exact GapPlan hash (which, from I-03-B/C, carries
  every qualification field + the policy epoch, so any URL / date /
  period / provider / revision / policy change yields a NEW plan hash);
- the receipt hash is a canonical-JSON SHA-256 over a nested payload —
  no field concatenation ambiguity; the allowed accession set is sorted
  INSIDE the hash, so an approved-set reorder does not change the receipt;
- ``validate_download_authorization`` is fail-closed and ordered:
  schema version gate (legacy receipts are EXPLICITLY invalidated — no
  auto-upgrade, no field back-fill), receipt-hash self-check, stale plan
  hash, expiry (a 1-second-late clock is expired), provider REQUIRED
  (a missing provider no longer default-passes), accession membership,
  item/byte caps. Every refusal happens with fetch=0 downstream.

The clock is injected as a string parameter (frozen test clock); no
production code is modified: this file is an iso attempt copy.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any


AUTHORIZATION_SCHEMA_VERSION = "1.1"
HASH_SCHEMA_VERSION = 1
_ISO_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _is_sha256_hex(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
    )


@dataclass(frozen=True)
class DownloadAuthorization:
    schema_version: str
    request_id: str
    gap_plan_hash: str
    # FC-801 (DL-03): the RuntimePolicySnapshot hash the download is bound
    # to — a download authorized under a different policy is not reusable.
    policy_hash: str
    provider: str
    allowed_accessions: tuple[str, ...]
    max_items: int
    max_bytes: int
    expires_at: str
    receipt_hash: str
    # I-03-C: binding version — legacy receipts carry no version and are
    # explicitly refused (never auto-upgraded).
    hash_schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "gap_plan_hash": self.gap_plan_hash,
            "policy_hash": self.policy_hash,
            "provider": self.provider,
            "allowed_accessions": list(self.allowed_accessions),
            "max_items": self.max_items,
            "max_bytes": self.max_bytes,
            "expires_at": self.expires_at,
            "receipt_hash": self.receipt_hash,
            "hash_schema_version": self.hash_schema_version,
        }

    def receipt_payload(self) -> dict[str, Any]:
        return {
            "hash_schema_version": self.hash_schema_version,
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "gap_plan_hash": self.gap_plan_hash,
            "policy_hash": self.policy_hash,
            "provider": self.provider,
            "allowed_accessions": sorted(self.allowed_accessions),
            "max_items": self.max_items,
            "max_bytes": self.max_bytes,
            "expires_at": self.expires_at,
        }


def _receipt_hash(payload: dict[str, Any]) -> str:
    blob = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_download_authorization(
    *,
    request_id: str,
    gap_plan_hash: str,
    policy_hash: str,
    provider: str,
    allowed_accessions: tuple[str, ...],
    max_items: int,
    max_bytes: int,
    expires_at: str,
) -> DownloadAuthorization:
    """Create a deterministic download authorization receipt.

    Fail-closed at build time: no implicit defaults (I-03-A D6 — a
    missing provider is NOT authorized, caps must be real caps, the
    expiry must be a canonical UTC instant)."""
    if not request_id or not gap_plan_hash or not policy_hash or not provider:
        raise ValueError("request_id/gap_plan_hash/policy_hash/provider required")
    if not _is_sha256_hex(gap_plan_hash):
        raise ValueError("gap_plan_hash must be a SHA-256 hex digest")
    if not _is_sha256_hex(policy_hash):
        raise ValueError("policy_hash must be a SHA-256 hex digest")
    if _ISO_Z.match(expires_at) is None:
        raise ValueError("expires_at must be canonical YYYY-MM-DDTHH:MM:SSZ")
    if not isinstance(max_items, int) or isinstance(max_items, bool) or max_items <= 0:
        raise ValueError("max_items must be a positive integer")
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
        raise ValueError("max_bytes must be a positive integer")
    if not allowed_accessions or any(
        not isinstance(a, str) or not a for a in allowed_accessions
    ):
        raise ValueError("allowed_accessions must be a non-empty list of accessions")
    receipt = DownloadAuthorization(
        schema_version=AUTHORIZATION_SCHEMA_VERSION,
        request_id=request_id,
        gap_plan_hash=gap_plan_hash,
        policy_hash=policy_hash,
        provider=provider,
        allowed_accessions=tuple(allowed_accessions),
        max_items=max_items,
        max_bytes=max_bytes,
        expires_at=expires_at,
        receipt_hash="",
    )
    receipt_hash = _receipt_hash(receipt.receipt_payload())
    return DownloadAuthorization(
        schema_version=AUTHORIZATION_SCHEMA_VERSION,
        request_id=request_id,
        gap_plan_hash=gap_plan_hash,
        policy_hash=policy_hash,
        provider=provider,
        allowed_accessions=tuple(allowed_accessions),
        max_items=max_items,
        max_bytes=max_bytes,
        expires_at=expires_at,
        receipt_hash=receipt_hash,
        hash_schema_version=1,
    )


def validate_download_authorization(
    authorization: DownloadAuthorization,
    candidate: Any,
    *,
    plan_hash: str,
    now: str,
    items_already_fetched: int = 0,
    bytes_already_fetched: int = 0,
) -> str | None:
    """Return an error string if the candidate may NOT be fetched under the
    receipt, else None (fetch=0 on every refusal). Fail-closed order:
    version gate -> receipt self-check -> plan hash -> expiry -> provider
    (required) -> accession -> caps."""
    if authorization.schema_version != AUTHORIZATION_SCHEMA_VERSION:
        return (
            "unsupported authorization schema_version "
            f"{authorization.schema_version!r}: legacy receipt requires "
            "explicit re-authorization (no auto-upgrade)"
        )
    if authorization.hash_schema_version != HASH_SCHEMA_VERSION:
        return (
            "unsupported hash_schema_version "
            f"{authorization.hash_schema_version!r}: legacy receipt requires "
            "explicit re-authorization"
        )
    if _receipt_hash(authorization.receipt_payload()) != authorization.receipt_hash:
        return "authorization receipt hash mismatch"
    if authorization.gap_plan_hash != plan_hash:
        return "authorization is bound to a different gap plan (stale_gap_hash)"
    if not _ISO_Z.match(now):
        return "validate clock not a canonical UTC instant"
    if now > authorization.expires_at:
        return "authorization expired"
    provider = str(getattr(candidate, "provider", "") or "")
    if not provider:
        return "provider not authorized: (missing provider on candidate)"
    if provider.lower() != authorization.provider:
        return f"provider not authorized: {provider.lower()}"
    accession = str(getattr(candidate, "provider_document_id", "") or "")
    if accession not in authorization.allowed_accessions:
        return f"accession not authorized: {accession}"
    if items_already_fetched >= authorization.max_items:
        return "item cap reached"
    size = int(getattr(candidate, "remote_size", 0) or 0)
    if size < 0:
        return "candidate reports a negative size (unknown-sized candidate refused)"
    if bytes_already_fetched + size > authorization.max_bytes:
        return "byte cap exceeded"
    return None
