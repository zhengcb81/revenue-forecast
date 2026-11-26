"""Atomic replacements of RF-owned durable artifacts."""

import os
from pathlib import Path
import time
from typing import Callable
from uuid import uuid4


def native_path(path: Path) -> Path:
    """Address the same file in the Windows extended namespace, including UNC paths."""
    if os.name != "nt":
        return path
    absolute = os.path.abspath(path)
    if absolute.startswith(("\\\\?\\", "\\\\.\\")):
        return Path(absolute)
    if absolute.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + absolute[2:])
    return Path("\\\\?\\" + absolute)


def replace_file_bytes(path: Path, data: bytes, *, before_replace: Callable[[], None] | None = None) -> None:
    """Prepare complete bytes in the same directory, then publish atomically."""
    path = native_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".rf-{uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if before_replace is not None:
            before_replace()
            os.replace(temporary, path)
        else:
            _replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _replace(temporary: Path, path: Path) -> None:
    # Windows readers may briefly hold the old or new name without delete
    # sharing. Keep the same fully-written replacement while the handle closes.
    for delay in (0.01, 0.02, 0.04, 0.08, 0):
        try:
            os.replace(temporary, path)
        except PermissionError as exc:
            if not delay or os.name != "nt" or getattr(exc, "winerror", None) not in (5, 32, 33):
                raise
            time.sleep(delay)
        else:
            return
