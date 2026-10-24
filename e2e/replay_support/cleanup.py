"""Exclusive attempt directories and restore proofs (W14 E06).

Rules enforced here:

- the caller's ``--work-root`` is never deleted or emptied; every run gets
  one exclusive ``attempt-<stamp>-<pid>`` child and all scratch lives inside
  it;
- deletion resolves the absolute path first and refuses anything outside the
  attempt directory this process created;
- the evidence directory is separate from scratch and is never removed;
  re-running into a populated evidence directory allocates a fresh attempt
  subdirectory instead of overwriting history.
"""

from __future__ import annotations

import itertools
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from .observe import tree_snapshot


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")

_SEQUENCE = itertools.count(1)


def _pid_token() -> str:
    return f"{os.getpid():x}"


class CleanupViolation(RuntimeError):
    pass


class AttemptSpace:
    """One owned attempt directory below a caller-provided root."""

    def __init__(self, work_root: Path, evidence_root: Path):
        self.work_root = work_root
        self.evidence_root = evidence_root
        self.stamp = _stamp()
        # pid + monotonic sequence: two attempts in the same second of the
        # same process still get distinct directories
        self.name = (f"attempt-{self.stamp}-{_pid_token()}"
                     f"-{next(_SEQUENCE):03d}")
        self.path = work_root / self.name
        self.initial_work_inventory: dict | None = None

    def allocate(self) -> "AttemptSpace":
        self.work_root.mkdir(parents=True, exist_ok=True)
        self.initial_work_inventory = tree_snapshot(self.work_root)
        if self.path.exists():
            raise CleanupViolation(
                f"attempt path already exists: {self.path}")
        self.path.mkdir(parents=True)
        return self

    def evidence_dir(self) -> Path:
        """Evidence lives beside scratch history; every attempt is a fresh
        subdirectory so prior receipts are never overwritten."""
        attempt_evidence = self.evidence_root / self.name
        attempt_evidence.mkdir(parents=True, exist_ok=True)
        return attempt_evidence

    # -- owned deletion ----------------------------------------------------

    def owned_path(self, candidate: Path) -> Path:
        resolved = candidate.resolve()
        mine = self.path.resolve()
        if mine != resolved and mine not in resolved.parents:
            raise CleanupViolation(
                f"refusing to delete outside the owned attempt: {resolved} "
                f"(owned root {mine})")
        return resolved

    def rmtree_owned(self, candidate: Path, *, attempts: int = 6,
                     wait: float = 1.0) -> bool:
        target = self.owned_path(candidate)
        for _ in range(attempts):
            if not target.exists():
                return True
            try:
                shutil.rmtree(target)
                return not target.exists()
            except (PermissionError, OSError):
                time.sleep(wait)
        return not target.exists()

    def cleanup(self) -> dict:
        """Remove ONLY this attempt's scratch; keep evidence and everything
        that pre-existed under work_root.

        The full before/after inventories (relpath -> size/mtime/sha256) are
        part of the report so reviewers can re-verify the restore claim from
        the persisted receipt instead of trusting a bare boolean (W14 F3).
        """
        gone = self.rmtree_owned(self.path)
        initial = dict(self.initial_work_inventory or {})
        if self.work_root.exists():
            after = tree_snapshot(self.work_root)
            remaining = sorted(p.name for p in self.work_root.iterdir())
        else:
            after, remaining = {}, []
        return {
            "attempt_removed": gone,
            "attempt_path": self.name,
            "work_root_remaining": remaining,
            "work_root_restored": after == initial,
            "initial_inventory": initial,
            "remaining_inventory": after,
            "added": sorted(set(after) - set(initial)),
            "removed": sorted(set(initial) - set(after)),
            "changed": sorted(k for k in set(initial) & set(after)
                              if initial[k] != after[k]),
        }
