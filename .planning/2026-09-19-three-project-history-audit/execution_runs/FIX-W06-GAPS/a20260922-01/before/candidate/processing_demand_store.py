"""CANDIDATE (UNRATIFIED) — durable processing-demand store for I-06-A.

*** THIS FILE IS NOT A PRODUCT DECISION. ***

D-W06 requires the wiki source-review owner + security reviewer + RF consumer
owner to freeze the single persistent owner, its schema/migration/API and the
demand idempotency key BEFORE any implementation.  That signature does not
exist (see decision.md), so this reference implementation lives ONLY in the
attempt directory and exists to show that the frozen requirements are
implementable and observable:

  * one durable owner shared by every process (SQLite, stdlib only);
  * idempotency key = (source bytes sha256, review policy, role set);
  * registered BEFORE the safety verdict is applied, so the block is
    recoverable;
  * a structured failure (never a silent in-memory fallback) when the store
    cannot be written;
  * a paused worker is REPORTED, never resumed or started.

Key derivation, columns, file name and CLI surface are CANDIDATE choices and
must be replaced by whatever D-W06 freezes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

CANDIDATE_MARKER = "candidate-unratified-I-06-A-a20260919-01"

DEMAND_SCHEMA_VERSION = "1.0.0"

DEMAND_SCHEMA = """
CREATE TABLE IF NOT EXISTS processing_demands (
    demand_id TEXT PRIMARY KEY,
    demand_key TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    review_policy TEXT NOT NULL,
    role_set TEXT NOT NULL,
    gaps_json TEXT NOT NULL,
    request_sha256 TEXT NOT NULL,
    request_json TEXT NOT NULL,
    candidate_marker TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    lease_owner TEXT,
    lease_until REAL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_processing_demands_key
    ON processing_demands(demand_key, status);
"""


class DemandStoreError(RuntimeError):
    """The durable store could not be used — never fall back to memory."""


class DemandStoreUnavailable(DemandStoreError):
    """Writing/reading the durable store failed (permissions, disk, schema)."""


class ProcessingDemandRecord:
    def __init__(self, row: sqlite3.Row):
        self._row = row

    def to_dict(self) -> dict:
        row = self._row
        return {
            "demand_id": row["demand_id"],
            "demand_key": row["demand_key"],
            "kind": row["kind"],
            "status": row["status"],
            "source_id": row["source_id"],
            "source_sha256": row["source_sha256"],
            "review_policy": row["review_policy"],
            "role_set": row["role_set"],
            "gaps": json.loads(row["gaps_json"]),
            "request_sha256": row["request_sha256"],
            "attempts": row["attempts"],
            "lease_owner": row["lease_owner"],
            "lease_until": row["lease_until"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "candidate_marker": row["candidate_marker"],
        }


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def demand_key(*, source_sha256: str, review_policy: str, role_set: str) -> str:
    """The frozen idempotency triple: bytes identity + policy + roles."""
    return canonical_sha256(
        {
            "source_sha256": source_sha256,
            "review_policy": review_policy,
            "role_set": role_set,
        }
    )


class DurableDemandStore:
    """Single durable owner of the demand queue (CANDIDATE)."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path), timeout=10.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        return connection

    def _initialize(self) -> None:
        parent = self.database_path.parent
        try:
            parent.mkdir(parents=True, exist_ok=True)
            connection = self._connect()
        except (OSError, sqlite3.Error) as exc:
            raise DemandStoreUnavailable(
                f"demand store unavailable: {type(exc).__name__}: {exc}"
            ) from exc
        try:
            connection.executescript(DEMAND_SCHEMA)
            connection.commit()
        except sqlite3.Error as exc:
            raise DemandStoreUnavailable(
                f"demand store schema failed: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            connection.close()

    def register(
        self,
        *,
        kind: str,
        source_id: str,
        source_sha256: str,
        review_policy: str,
        role_set: str,
        gaps: list[dict],
        request: dict,
        now: float | None = None,
    ) -> tuple[dict, bool]:
        """Idempotent registration; returns (demand, created)."""
        self._initialize()
        stamp = time.time() if now is None else now
        key = demand_key(
            source_sha256=source_sha256,
            review_policy=review_policy,
            role_set=role_set,
        )
        request_sha = canonical_sha256(request)
        try:
            connection = self._connect()
        except (OSError, sqlite3.Error) as exc:
            raise DemandStoreUnavailable(
                f"demand store unavailable: {type(exc).__name__}: {exc}"
            ) from exc
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM processing_demands WHERE demand_key=? "
                "AND status IN ('pending','running','failed') "
                "ORDER BY created_at, demand_id LIMIT 1",
                (key,),
            ).fetchone()
            if existing is not None:
                connection.execute(
                    "UPDATE processing_demands SET updated_at=? WHERE demand_id=?",
                    (stamp, existing["demand_id"]),
                )
                connection.commit()
                refreshed = connection.execute(
                    "SELECT * FROM processing_demands WHERE demand_id=?",
                    (existing["demand_id"],),
                ).fetchone()
                return ProcessingDemandRecord(refreshed).to_dict(), False
            demand_id = f"demand-{uuid.uuid4().hex[:16]}"
            connection.execute(
                "INSERT INTO processing_demands(demand_id,demand_key,kind,status,"
                "source_id,source_sha256,review_policy,role_set,gaps_json,"
                "request_sha256,request_json,candidate_marker,attempts,created_at,"
                "updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    demand_id,
                    key,
                    kind,
                    "pending",
                    source_id,
                    source_sha256,
                    review_policy,
                    role_set,
                    json.dumps(gaps, ensure_ascii=False, sort_keys=True),
                    request_sha,
                    json.dumps(request, ensure_ascii=False, sort_keys=True),
                    CANDIDATE_MARKER,
                    0,
                    stamp,
                    stamp,
                ),
            )
            connection.commit()
            created = connection.execute(
                "SELECT * FROM processing_demands WHERE demand_id=?", (demand_id,)
            ).fetchone()
            return ProcessingDemandRecord(created).to_dict(), True
        except sqlite3.Error as exc:
            raise DemandStoreUnavailable(
                f"demand store write failed: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            connection.close()

    def list_active(self) -> list[dict]:
        self._initialize()
        try:
            connection = self._connect()
        except (OSError, sqlite3.Error) as exc:
            raise DemandStoreUnavailable(
                f"demand store unavailable: {type(exc).__name__}: {exc}"
            ) from exc
        try:
            rows = connection.execute(
                "SELECT * FROM processing_demands ORDER BY created_at, demand_id"
            ).fetchall()
        except sqlite3.Error as exc:
            raise DemandStoreUnavailable(
                f"demand store read failed: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            connection.close()
        return [ProcessingDemandRecord(row).to_dict() for row in rows]

    def claim(self, *, owner: str, lease_seconds: float = 300.0) -> dict | None:
        """Explicit single consumption grant (never automatic)."""
        self._initialize()
        stamp = time.time()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM processing_demands WHERE status IN ('pending','failed') "
                "AND (lease_until IS NULL OR lease_until < ?) "
                "ORDER BY created_at, demand_id LIMIT 1",
                (stamp,),
            ).fetchone()
            if row is None:
                connection.commit()
                return None
            connection.execute(
                "UPDATE processing_demands SET status='running', lease_owner=?, "
                "lease_until=?, updated_at=? WHERE demand_id=?",
                (owner, stamp + lease_seconds, stamp, row["demand_id"]),
            )
            connection.commit()
            claimed = connection.execute(
                "SELECT * FROM processing_demands WHERE demand_id=?",
                (row["demand_id"],),
            ).fetchone()
            return ProcessingDemandRecord(claimed).to_dict()
        finally:
            connection.close()


def read_worker_control(path: Path) -> dict:
    """Read-only view of the worker control file (never resumes anything)."""
    if not path.is_file():
        return {"path": str(path), "exists": False, "desired_state": None}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "path": str(path),
            "exists": True,
            "desired_state": None,
            "error": f"{type(exc).__name__}",
        }
    return {
        "path": str(path),
        "exists": True,
        "desired_state": payload.get("desired_state"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=f"candidate durable demand store ({CANDIDATE_MARKER})"
    )
    parser.add_argument("command", choices=("list", "claim"))
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--owner", default="cli")
    args = parser.parse_args(argv)
    store = DurableDemandStore(args.database)
    try:
        if args.command == "list":
            payload = {"demands": store.list_active(), "store": str(args.database)}
        else:
            claimed = store.claim(owner=args.owner)
            payload = {"claimed": claimed, "store": str(args.database)}
    except DemandStoreUnavailable as exc:
        sys.stdout.write(
            json.dumps(
                {"error": "demand_store_unavailable", "detail": str(exc)},
                ensure_ascii=False,
            )
        )
        sys.stdout.write("\n")
        return 4
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
