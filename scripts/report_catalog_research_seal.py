"""Owner admission lock and immutable seal publication shared by RF writers."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile

from owner_file_lock import OwnerFileLock
from report_catalog_common import CatalogError, require as _require
from report_catalog_research_capture import owned_unlinked_path


def acquire_admission_lock(root: Path, path: Path) -> OwnerFileLock:
    """Hold an owner admission lock apart from the catalog append lock."""
    if path.exists():
        owned_unlinked_path(root, path)
    lock = OwnerFileLock(path)
    try:
        if not lock.acquire():
            raise CatalogError("catalog_busy", "another research admission is active")
        owned_unlinked_path(root, path)
    except OSError as exc:
        lock.release()
        raise CatalogError("catalog_unavailable", "research admission lock is unavailable") from exc
    except BaseException:
        lock.release()
        raise
    return lock


def release_admission_lock(lock: OwnerFileLock) -> None:
    lock.release()


def write_admission_seal(root: Path, seal: Path, body: bytes) -> None:
    """Publish complete immutable bytes, never a partially written final name."""
    if seal.exists():
        with owned_unlinked_path(root, seal).open("rb") as existing:
            preserved = existing.read(len(body) + 1)
        _require(
            preserved == body,
            "research_import_conflict",
            "sealed admission bytes disagree",
        )
        return
    descriptor, temporary = tempfile.mkstemp(
        prefix=".research-admission-", dir=seal.parent
    )
    staged = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        owned_unlinked_path(root, seal.parent)
        try:
            # Windows rename is atomic and refuses an existing destination.
            # POSIX rename would replace an existing seal, so use a new link.
            if os.name == "nt":
                os.rename(staged, seal)
            else:
                os.link(staged, seal)
        except FileExistsError:
            _require(
                owned_unlinked_path(root, seal).read_bytes() == body,
                "research_import_conflict",
                "sealed admission bytes disagree",
            )
    except OSError as exc:
        raise CatalogError(
            "catalog_unavailable", "sealed research evidence cannot be published"
        ) from exc
    finally:
        staged.unlink(missing_ok=True)
