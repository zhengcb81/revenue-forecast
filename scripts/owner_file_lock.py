"""Stable file mutex for durable RF owner stores on Windows and POSIX."""

from __future__ import annotations

import errno
import os
from pathlib import Path


class OwnerFileLock:
    """The kernel owns the lease. The lock path is never unlinked by a contender."""

    def __init__(self, path: Path):
        self.path = path
        self._fd: int | None = None

    @staticmethod
    def _try_lock(fd: int) -> bool:
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                raise
            return False
        return True

    def acquire(self) -> bool:
        if self._fd is not None:
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            if not self._try_lock(fd):
                return False
            self._fd = fd
            return True
        finally:
            if self._fd != fd:
                os.close(fd)

    def release(self) -> None:
        fd, self._fd = self._fd, None
        if fd is not None:
            os.close(fd)

    def is_locked(self) -> bool:
        if self._fd is not None:
            return True
        try:
            fd = os.open(self.path, os.O_RDWR)
        except FileNotFoundError:
            return False
        try:
            return not self._try_lock(fd)
        finally:
            os.close(fd)
