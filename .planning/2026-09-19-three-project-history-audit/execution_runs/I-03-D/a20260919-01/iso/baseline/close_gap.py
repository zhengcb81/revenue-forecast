"""FC-801: CloseGap binding — same-value + same-version validation
(isolated implementation card I-03-C).

This iso copy carries ONLY the binding-validation boundary of
``close_gap.py`` (the card's allowed surface: "close_gap.py 中绑定校验
边界"). The full transaction's resolver/journal/lock execution face
(C15 batch truncation / completed_partial) stays with the production
module and is recorded as out of scope in handoff.json.

- ``CloseGapBinding`` additionally carries ``hash_schema_version`` —
  the binding is version-locked to the authorization (legacy bindings
  without an explicit version are refused, never auto-upgraded);
- ``validate_close_gap_binding(binding, authorization)`` is a pure
  fail-closed check that the binding and the authorization are the
  SAME values on every shared field (request_id, gap_plan_hash,
  policy_hash, provider, allowed_accessions as a set, max_items,
  max_bytes, expires_at) and the SAME binding version. Any difference
  returns a precise reason (DL-03: fetch=0 downstream); nothing is
  back-filled.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


CLOSE_GAP_SCHEMA_VERSION = "1.0"
HASH_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CloseGapBinding:
    """FC-801: the input binding of one authorized close-gap download."""

    request_id: str
    gap_plan_hash: str
    policy_hash: str
    provider: str
    allowed_accessions: tuple[str, ...]
    max_items: int
    max_bytes: int
    expires_at: str
    # I-03-C: version-locked to the authorization (same-value, same-version
    # binding). Legacy bindings (missing / non-1 version) are refused.
    hash_schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "gap_plan_hash": self.gap_plan_hash,
            "policy_hash": self.policy_hash,
            "provider": self.provider,
            "allowed_accessions": list(self.allowed_accessions),
            "max_items": self.max_items,
            "max_bytes": self.max_bytes,
            "expires_at": self.expires_at,
            "hash_schema_version": self.hash_schema_version,
        }


def _set(xs: tuple[str, ...]) -> set[str]:
    return set(xs)


def validate_close_gap_binding(binding: Any, authorization: Any) -> str | None:
    """Return an error string when the binding does NOT match the
    authorization exactly (same value + same version), else None."""
    if getattr(binding, "hash_schema_version", 0) != getattr(
        authorization, "hash_schema_version", None
    ):
        return (
            "binding version mismatch: binding and authorization must carry "
            "the same hash_schema_version (legacy binding refused)"
        )
    checks: tuple[tuple[str, Any, Any], ...] = (
        ("request_id", binding.request_id, authorization.request_id),
        ("gap_plan_hash", binding.gap_plan_hash, authorization.gap_plan_hash),
        ("policy_hash", binding.policy_hash, authorization.policy_hash),
        ("provider", binding.provider, authorization.provider),
        ("max_items", binding.max_items, authorization.max_items),
        ("max_bytes", binding.max_bytes, authorization.max_bytes),
        ("expires_at", binding.expires_at, authorization.expires_at),
    )
    for name, b_val, a_val in checks:
        if b_val != a_val:
            return f"binding mismatch on {name}"
    if _set(binding.allowed_accessions) != _set(authorization.allowed_accessions):
        return "binding mismatch on allowed_accessions"
    return None


def _txn_id(binding: CloseGapBinding) -> str:
    payload = json.dumps(binding.to_dict(), sort_keys=True, ensure_ascii=False)
    return (
        "urn:company-wiki:close-gap:sha256:"
        + hashlib.sha256(payload.encode("utf-8")).hexdigest()
    )
