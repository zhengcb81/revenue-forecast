"""Single-writer, TTL, owner-bound lock protocol for shared control resources.

Resources: plan manifests, machine state, README control fields, receipts,
registries.  Semantics:

- **acquire** publishes a lock record exclusively; a second concurrent
  acquirer receives an explicit :class:`LockConflict` (no silent
  last-write-wins).
- A lock is bound to ``(resource, owner)``; only the owning identity may
  **release** it — impersonation is rejected.
- Locks carry a TTL.  An expired lock may be broken by any acquirer, but the
  break itself races through exclusive publish, so at most one breaker wins
  per lock generation.
- Renewal by the same owner is a CAS write on the lock record: if someone
  else broke or replaced the record in between, renewal fails with
  :class:`CASConflict`.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from uc.casfile import (
    CASConflict,
    cas_update,
    exclusive_publish,
    sha256_bytes,
    sha256_file,
)

DEFAULT_TTL_SECONDS = 3600
LOCK_SUFFIX = ".lock.json"
_NAME_OK = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")


class LockConflict(Exception):
    """Another owner currently holds an unexpired lock on this resource."""

    def __init__(self, resource: str, held_by: str, expires_at: str) -> None:
        self.resource = resource
        self.held_by = held_by
        self.expires_at = expires_at
        super().__init__(
            f"lock conflict on '{resource}': held by {held_by} until {expires_at}"
        )


class LockOwnershipError(Exception):
    """A release/renew was attempted by an identity that does not hold the lock."""


class LockMissingError(Exception):
    """A release was attempted but no lock record exists."""


def _sanitize_resource(resource: str) -> str:
    if not resource or any(ch not in _NAME_OK for ch in resource):
        raise ValueError(f"invalid resource name: {resource!r}")
    return resource


@dataclass(frozen=True)
class LockRecord:
    resource: str
    owner: str
    nonce: str
    acquired_at_utc: str
    expires_at_utc: str
    ttl_seconds: int
    base_manifest_sha256: str | None

    def to_json(self) -> bytes:
        return json.dumps(
            {
                "resource": self.resource,
                "owner": self.owner,
                "nonce": self.nonce,
                "acquired_at_utc": self.acquired_at_utc,
                "expires_at_utc": self.expires_at_utc,
                "ttl_seconds": self.ttl_seconds,
                "base_manifest_sha256": self.base_manifest_sha256,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")

    def is_expired(self, now_utc: datetime | None = None) -> bool:
        now = now_utc or datetime.now(timezone.utc)
        expires = datetime.fromisoformat(self.expires_at_utc)
        return now >= expires


def lock_path(lock_dir: Path, resource: str) -> Path:
    return lock_dir / f"{_sanitize_resource(resource)}{LOCK_SUFFIX}"


def _load(path: Path) -> LockRecord | None:
    try:
        payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    try:
        return LockRecord(
            resource=payload["resource"],
            owner=payload["owner"],
            nonce=payload["nonce"],
            acquired_at_utc=payload["acquired_at_utc"],
            expires_at_utc=payload["expires_at_utc"],
            ttl_seconds=int(payload["ttl_seconds"]),
            base_manifest_sha256=payload.get("base_manifest_sha256"),
        )
    except (KeyError, TypeError, ValueError):
        return None  # corrupt record = unreadable; treated as absent, never trusted


def _break_if_unchanged(path: Path, expected_hash: str, attempts: int = 200) -> bool:
    """Move ``path`` aside ONLY while its content still hashes to
    ``expected_hash``.

    Generation guard: a retrying rename must never move a NEWER lock that a
    peer published at the same path after we read the old record.  Returns
    True when this caller moved the file, False when the file vanished or its
    content changed (somebody else broke/replaced it first).
    """
    for attempt in range(attempts):
        try:
            if sha256_file(path) != expected_hash:
                return False
            tombstone = path.with_name(f"{path.name}.expired.{uuid.uuid4().hex}")
            path.rename(tombstone)
            return True
        except FileNotFoundError:
            return False
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.005)
    raise AssertionError("unreachable")


def acquire(
    lock_dir: Path,
    resource: str,
    owner: str,
    ttl: int = DEFAULT_TTL_SECONDS,
    base_manifest_sha256: str | None = None,
    now_utc: datetime | None = None,
) -> LockRecord:
    """Acquire (or renew) the lock for ``resource`` as ``owner``.

    Raises :class:`LockConflict` when another owner holds a live lock.
    """
    if ttl <= 0:
        raise ValueError("ttl must be positive")
    path = lock_path(lock_dir, resource)
    now = now_utc or datetime.now(timezone.utc)
    for _attempt in range(4):
        record = _load(path) if path.exists() else None
        if record is None:
            if path.exists():
                # Corrupt record: never trusted.  Break it generation-guarded
                # so we cannot move a fresh lock a peer just published.
                try:
                    corrupt_hash = sha256_file(path)
                except FileNotFoundError:
                    continue
                _break_if_unchanged(path, corrupt_hash)
                continue
            new_record = LockRecord(
                resource=resource,
                owner=owner,
                nonce=uuid.uuid4().hex,
                acquired_at_utc=now.isoformat(),
                expires_at_utc=(now + timedelta(seconds=ttl)).isoformat(),
                ttl_seconds=ttl,
                base_manifest_sha256=base_manifest_sha256,
            )
            if exclusive_publish(path, new_record.to_json()):
                return new_record
            continue  # lost the create race; re-read
        if record.owner == owner:
            renewed = LockRecord(
                resource=resource,
                owner=owner,
                nonce=record.nonce,
                acquired_at_utc=record.acquired_at_utc,
                expires_at_utc=(now + timedelta(seconds=ttl)).isoformat(),
                ttl_seconds=ttl,
                base_manifest_sha256=base_manifest_sha256,
            )
            try:
                cas_update(path, renewed.to_json(), sha256_bytes(record.to_json()))
            except CASConflict:
                continue  # record changed under us; re-read
            return renewed
        if record.is_expired(now):
            _break_if_unchanged(path, sha256_bytes(record.to_json()))
            continue  # re-race exclusive create (whether we broke it or lost)
        raise LockConflict(resource, record.owner, record.expires_at_utc)
    raise LockConflict(resource, "<race-undecided>", now.isoformat())


def _unlink_if_unchanged(path: Path, expected_hash: str, attempts: int = 200) -> bool:
    """Unlink ``path`` only while its content still hashes to
    ``expected_hash``.  Returns False when the file vanished or its content
    changed (a peer broke/replaced the lock generation)."""
    for attempt in range(attempts):
        try:
            if sha256_file(path) != expected_hash:
                return False
            path.unlink()
            return True
        except FileNotFoundError:
            return False
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.005)
    raise AssertionError("unreachable")


def release(lock_dir: Path, resource: str, owner: str, nonce: str) -> None:
    """Release the lock.  Only the recorded owner with the matching nonce may,
    and only the exact lock generation that was verified gets removed."""
    path = lock_path(lock_dir, resource)
    if not path.exists():
        raise LockMissingError(resource)
    record = _load(path)
    if record is None or record.owner != owner or record.nonce != nonce:
        raise LockOwnershipError(
            f"'{owner}' cannot release '{resource}': lock is held by "
            f"{record.owner if record else '<unreadable>'} (nonce mismatch or corrupt)"
        )
    if not _unlink_if_unchanged(path, sha256_bytes(record.to_json())):
        raise LockOwnershipError(
            f"'{owner}' cannot release '{resource}': lock generation changed "
            "under release (broken or replaced by a peer) — re-read and retry"
        )


def status(lock_dir: Path, resource: str) -> LockRecord | None:
    """Current lock record, if any (an expired-but-unbroken record is still
    reported; callers check :meth:`LockRecord.is_expired`)."""
    path = lock_path(lock_dir, resource)
    if not path.exists():
        return None
    return _load(path)
