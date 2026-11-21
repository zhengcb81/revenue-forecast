"""Atomic replacements of RF-owned durable artifacts."""

import os
from pathlib import Path
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
    finally:
        temporary.unlink(missing_ok=True)
