"""Optional source annotations are observations, never access credentials."""
from __future__ import annotations

from datetime import datetime
import re
from typing import Any

_FIELDS = {"status", "source_sha256", "evidence_sha256", "policy_hash", "reviewed_at"}
_STATUSES = {"not_reviewed", "not_detected", "detected_and_ignored"}


def review_observation(value: Any, source_sha256: str | None) -> dict[str, str]:
    if value is None:
        return {"status": "absent", "prompt_injection_status": "not_reviewed"}
    reason = "invalid_source_review"
    if isinstance(value, dict) and set(value) == _FIELDS:
        digest = value.get("source_sha256")
        valid = (isinstance(value.get("status"), str) and value["status"] in _STATUSES
                 and (digest is None or digest == source_sha256))
        valid = valid and all(value.get(k) is None or (isinstance(value[k], str)
            and re.fullmatch(r"[a-f0-9]{64}", value[k]) is not None)
            for k in ("evidence_sha256", "policy_hash"))
        timestamp = value.get("reviewed_at")
        if timestamp is not None:
            try:
                parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                valid = valid and parsed.utcoffset() is not None
            except (ValueError, TypeError, AttributeError):
                valid = False
        if valid:
            return {"status": "available", "prompt_injection_status": value["status"]}
        if digest is not None and digest != source_sha256:
            reason = "foreign_source_review"
    return {"status": "unavailable", "prompt_injection_status": "not_reviewed", "reason": reason}
