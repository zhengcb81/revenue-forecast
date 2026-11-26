"""File acquisition and atomic replacement for RF-owned durable artifacts."""

from collections.abc import Iterator
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import stat
import time
from typing import BinaryIO, Callable
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


def _ordinary_file(info: os.stat_result) -> bool:
    return stat.S_ISREG(info.st_mode) and not (
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def _regular_leaf(path: Path) -> os.stat_result:
    info = path.lstat()
    if not _ordinary_file(info):
        raise OSError(errno.EINVAL, "owner path must have an ordinary file leaf")
    return info


def open_regular_file(path: Path, *, append: bool = False) -> BinaryIO:
    """Open the configured leaf without reading or writing an unverified file."""
    path = native_path(path)
    flags = (os.O_RDWR | os.O_APPEND) if append else os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    if os.name == "posix":
        flags |= os.O_NOFOLLOW | os.O_NONBLOCK
    before: os.stat_result | None
    fd = None
    try:
        before = _regular_leaf(path)
    except FileNotFoundError:
        if not append:
            raise
        before = None
        try:
            fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o666)
        except FileExistsError:
            # A peer may have created the outbox before this exclusive open.
            # Reacquire that ordinary file once with the existing-file flags.
            before = _regular_leaf(path)

    # Parents may intentionally be configured aliases. Compare the leaf
    # before and after opening and never use the descriptor for I/O first.
    if fd is None:
        fd = os.open(path, flags)
    try:
        opened = os.fstat(fd)
        after = path.lstat()
        if (not _ordinary_file(opened) or not _ordinary_file(after)
                or not os.path.samestat(opened, after)
                or (before is not None and not os.path.samestat(before, opened))):
            raise OSError(errno.EAGAIN, "owner file identity changed while opening")
        return os.fdopen(fd, "a+b" if append else "rb")
    except BaseException:
        os.close(fd)
        raise


@contextmanager
def _staged_file(path: Path, data: bytes) -> Iterator[tuple[Path, Path]]:
    path = native_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".rf-{uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        yield temporary, path
    finally:
        temporary.unlink(missing_ok=True)


def replace_file_bytes(path: Path, data: bytes, *, before_replace: Callable[[], None] | None = None) -> None:
    """Prepare complete bytes in the same directory, then publish atomically."""
    with _staged_file(path, data) as (temporary, destination):
        if before_replace is not None:
            before_replace()
            os.replace(temporary, destination)
        else:
            _replace(temporary, destination)


def create_file_bytes(path: Path, data: bytes) -> None:
    """Publish complete bytes once. An existing destination raises FileExistsError."""
    with _staged_file(path, data) as (temporary, destination):
        if os.name == "nt":
            # Windows rename never replaces an existing destination.
            os.rename(temporary, destination)
        else:
            os.link(temporary, destination, follow_symlinks=False)


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
