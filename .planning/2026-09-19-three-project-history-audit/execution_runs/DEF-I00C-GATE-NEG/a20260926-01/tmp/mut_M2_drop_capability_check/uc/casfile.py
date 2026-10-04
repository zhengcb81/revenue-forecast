"""Content-addressed, compare-and-swap atomic file updates.

Invariants
----------
1. A publish is atomic: the target either has the old content or the complete
   new content; a crash can never leave a half-written target.
2. ``cas_update`` refuses to replace a target whose current hash differs from
   the expected base hash — a concurrent modification is *detected*, never
   silently overwritten.
3. ``exclusive_publish`` wins for at most one caller; every other caller is
   told explicitly instead of silently winning last-write.

Windows note: exclusive publish uses a same-directory temp file plus
``os.link`` (hard link) — creating the final name fails atomically when it
already exists.  The temp and final names always live in the same directory,
so they share one volume.
"""

from __future__ import annotations

import hashlib
import os
import time
import uuid
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")

CHUNK = 1 << 20


def retry_sharing_violation(
    op: Callable[[], T],
    attempts: int = 200,
    delay: float = 0.005,
) -> T:
    """Windows: an open read handle (no FILE_SHARE_DELETE) makes ``unlink``/
    ``replace`` raise PermissionError (WinError 32) while a concurrent reader
    holds the file.  Retry briefly — the reader's handle closes quickly — and
    re-raise after the bounded attempts."""
    for attempt in range(attempts):
        try:
            return op()
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
    raise AssertionError("unreachable")


class CASConflict(Exception):
    """A compare-and-swap write was refused because the base hash changed."""

    def __init__(self, path: Path, expected_sha256: str, actual_sha256: str) -> None:
        self.path = path
        self.expected_sha256 = expected_sha256
        self.actual_sha256 = actual_sha256
        super().__init__(
            f"CAS conflict on {path}: expected {expected_sha256[:12]}…, "
            f"found {actual_sha256[:12]}… (concurrent modification)"
        )


def sha256_bytes(data: bytes) -> str:
    """Hex SHA-256 of a byte string."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Hex SHA-256 of a file's content (missing file raises FileNotFoundError)."""
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def read_bytes(path: Path) -> bytes:
    """Read a whole file as bytes."""
    with open(path, "rb") as fh:
        return fh.read()


def exclusive_publish(target: Path, data: bytes) -> bool:
    """Atomically create ``target`` with ``data`` iff it does not exist.

    Returns True when this caller won the race, False when the target already
    existed (nothing was written).  Never overwrites an existing target.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.parent / f".{target.name}.tmp.{uuid.uuid4().hex}"
    with open(temp, "xb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    try:
        retry_sharing_violation(lambda: os.link(temp, target))
    except FileExistsError:
        return False
    finally:
        temp.unlink(missing_ok=True)
    return True


def atomic_replace(target: Path, data: bytes) -> None:
    """Atomically replace ``target`` with ``data`` (unconditional replace).

    Used only where the caller already holds the resource lock or has just
    verified the CAS base hash inside ``cas_update``.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.parent / f".{target.name}.tmp.{uuid.uuid4().hex}"
    with open(temp, "xb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    try:
        retry_sharing_violation(lambda: os.replace(temp, target))
    finally:
        temp.unlink(missing_ok=True)


def cas_update(target: Path, data: bytes, expected_sha256: str) -> str:
    """Replace ``target`` with ``data`` only if its current hash is the
    expected one.  Raises :class:`CASConflict` when the target is missing or
    its hash differs (a concurrent modification is *detected*, never silently
    overwritten).  Returns the new content hash."""
    if not target.exists():
        raise CASConflict(target, expected_sha256, "<missing>")
    actual = sha256_file(target)
    if actual != expected_sha256:
        raise CASConflict(target, expected_sha256, actual)
    atomic_replace(target, data)
    return sha256_bytes(data)


def cas_apply(
    target: Path,
    transform: Callable[[bytes], bytes],
    expected_sha256: str,
) -> str:
    """Read-transform-write under strict CAS.  Callers retry on
    :class:`CASConflict` after re-reading (three-way merge)."""
    current = read_bytes(target) if target.exists() else b""
    new_data = transform(current)
    return cas_update(target, new_data, expected_sha256)


def guarded_update(
    lock_dir: Path,
    resource: str,
    owner: str,
    target: Path,
    transform: Callable[[bytes], bytes],
    ttl_seconds: int = 3600,
) -> str:
    """The canonical shared-resource write path: resource lock -> read ->
    CAS write -> post-write re-read verification -> release.

    Among protocol-abiding writers (who all take the same lock) updates can
    never be lost.  If a rogue writer interferes inside the window, the
    post-write re-read detects it and raises :class:`CASConflict` instead of
    silently accepting a lost update.  Returns the new content hash.
    """
    from uc.lock import acquire, release

    record = acquire(lock_dir, resource, owner, ttl=ttl_seconds)
    try:
        current = read_bytes(target) if target.exists() else b""
        new_data = transform(current)
        if not target.exists():
            if not exclusive_publish(target, new_data):
                raise CASConflict(target, "<absent>", sha256_file(target))
            new_hash = sha256_bytes(new_data)
        else:
            new_hash = cas_update(target, new_data, sha256_bytes(current))
        actual = sha256_file(target)
        if actual != new_hash:
            raise CASConflict(target, new_hash, actual)
        return new_hash
    finally:
        release(lock_dir, resource, owner, record.nonce)
