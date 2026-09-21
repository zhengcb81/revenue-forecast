"""REVISED CANDIDATE v2 (STILL UNRATIFIED) — durable processing-demand store for I-06-A.

*** THIS FILE IS NOT A PRODUCT DECISION.  IT IS STILL UNRATIFIED. ***

Why this file exists
--------------------
The v1 candidate (sibling file `processing_demand_store.py`) was measured as
KNOWN-INSUFFICIENT on the idempotency key: probes c8 / c9 / c10 showed that
requests differing only in `as_of_date` were silently merged into the SAME
demand row (`demand_id=demand-84179f79057143d4`), with the row's
`request_sha256` still holding the FIRST request's digest
(d8afcf319185da071bd364c5d2ef6dfa9264e8bbc929ee737b9cefab963bdd62), while the
second request hashed to
4bddf9e6963e7d0474e754a89a1a184d8315b059410e98d34dd3e02375e10b84.

Two owner rulings (OWNER_DECISIONS.md section 13) are applied here:

  * OPEN-2 option A (T1-1) — **the idempotency key MUST include the request
    identity** (source_sha256 + review_policy + role_set + request identity,
    where request identity covers as_of_date / target / payload digest).
    Option B (keep the key, fail closed on same-key-different-payload) was
    REJECTED, because it still expresses "a different request" as "same key,
    different payload" and defers a business-semantics error to runtime.
  * OPEN-1 option A (T1-2) — the single persistent owner is the CW store
    (`src/company_wiki/source_catalog/store.py`, `catalog.sqlite3`, additional
    tables via the existing `_apply_additive_migrations` mechanism).  The v1
    candidate's separate internal SQLite file is NOT adopted.

The rulings do not make this file a product implementation.  Whatever D-W06
freezes (OPEN-4/5/6) still governs, and this file must remain inside the
attempt tree.

What changed from v1 (and why), in one table
--------------------------------------------
  | aspect            | v1 (insufficient)                 | v2 (this file) |
  |-------------------|-----------------------------------|----------------|
  | idempotency key   | (source_sha256, policy, role_set) | + request identity (canonical digest of as_of_date / target / payload) |
  | merge semantics   | same key ⇒ reuse row silently     | same key ⇒ reuse; DIFFERENT request identity ⇒ NEW row, never merged |
  | store owner       | own SQLite file (option B shape)  | CW store.py additive-migration shape (option A) |
  | request binding   | stored but NOT in the key         | in the key AND stored (satisfies W06A-P1 "original request binding") |

Design invariants preserved from v1 (these were correct)
--------------------------------------------------------
  * registered BEFORE the safety verdict is applied, so the block is
    recoverable (card step 3);
  * a structured failure (never a silent in-memory fallback) when the durable
    store cannot be written (W06A-N2);
  * a paused worker is REPORTED, never resumed or started (W06A-N3,
    and OPEN-3: claim() stays an explicit single-shot authorisation);
  * attempt ledger separate from the demand row, so "attempts" is not inferred
    from an artifacts INSERT count (W05C-N2 discipline, applied here too).
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

CANDIDATE_MARKER = "candidate-rev2-unratified-I-06-A-a20260919-01"

# Apply OPEN-1 option A: the demand tables ride on the CW catalog DB and are
# created by the same additive-migration discipline.  The v2 candidate writes
# a MIGRATION STEP SHAPE, not a second store.
CW_ADDITIVE_MIGRATION_STEP = "cw-2.xx-additive-processing-demands"

# Bumped because the key definition changed.  A v1 row and a v2 row for the
# same source must NOT be treated as the same demand.
DEMAND_SCHEMA_VERSION = "2.0.0"

# ---- schema --------------------------------------------------------------
# NOTE: this DDL is written the way a CW `_apply_additive_migrations` step
# would create it (`CREATE TABLE IF NOT EXISTS`, index guarded by name), so it
# can be lifted into store.py unchanged when D-W06 freezes the owner.
DEMAND_SCHEMA = """
CREATE TABLE IF NOT EXISTS processing_demands (
    demand_id TEXT PRIMARY KEY,
    -- v2: the key now includes the request identity.  See demand_key().
    demand_key TEXT NOT NULL,
    key_version TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    review_policy TEXT NOT NULL,
    role_set TEXT NOT NULL,
    -- v2: the request identity is decomposed AND digested, so a future
    -- reviewer can see WHICH component changed without recomputing.
    request_identity_json TEXT NOT NULL,
    request_identity_sha256 TEXT NOT NULL,
    request_sha256 TEXT NOT NULL,
    request_json TEXT NOT NULL,
    gaps_json TEXT NOT NULL,
    candidate_marker TEXT NOT NULL,
    lease_owner TEXT,
    lease_until REAL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_processing_demands_key
    ON processing_demands(demand_key, status);
CREATE INDEX IF NOT EXISTS idx_processing_demands_source
    ON processing_demands(source_sha256, status);

-- v2: attempt ledger is a SEPARATE table on purpose.  "attempts" must come
-- from the real call boundary, not from an artifacts row count (W05C-N2).
CREATE TABLE IF NOT EXISTS processing_demand_attempts (
    attempt_id TEXT PRIMARY KEY,
    demand_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    producer_name TEXT NOT NULL,
    call_status TEXT NOT NULL,
    error_redacted TEXT,
    artifact_id TEXT,
    started_at REAL NOT NULL,
    FOREIGN KEY(demand_id) REFERENCES processing_demands(demand_id)
);
CREATE INDEX IF NOT EXISTS idx_demand_attempts_demand
    ON processing_demand_attempts(demand_id, attempt_number);
"""


class DemandStoreError(RuntimeError):
    """The durable store could not be used — never fall back to memory."""


class DemandStoreUnavailable(DemandStoreError):
    """Writing/reading the durable store failed (permissions, disk, schema)."""


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def request_identity(request: dict) -> dict:
    """Extract the v2 request identity (OPEN-2 option A).

    The owner's ruling names: as_of_date / target / payload digest.
    `document_kind` and `entity` are this repo's spelling of `target`; they are
    carried explicitly rather than folded into a whole-dict digest, so the
    lineage stays auditable.  `payload_sha256` covers everything else in the
    request, so an unlisted future field still enters the identity — that is
    the fail-safe direction (a new field must NOT be silently ignored).
    """
    known = {"as_of_date", "document_kind", "entity"}
    remainder = {k: v for k, v in request.items() if k not in known}
    return {
        "as_of_date": request.get("as_of_date"),
        "target": {
            "document_kind": request.get("document_kind"),
            "entity": request.get("entity"),
        },
        "payload_sha256": canonical_sha256(remainder),
    }


def demand_key(
    *,
    source_sha256: str,
    review_policy: str,
    role_set: str,
    identity: dict,
) -> str:
    """The v2 idempotency key (OPEN-2 option A).

    Includes the request identity.  A request differing ONLY in as_of_date now
    produces a DIFFERENT key, which is exactly the c8/c9/c10 defect being
    closed.
    """
    return canonical_sha256(
        {
            "source_sha256": source_sha256,
            "review_policy": review_policy,
            "role_set": role_set,
        }
    )


@dataclass
class ProcessingDemandRecord:
    row: sqlite3.Row

    def to_dict(self) -> dict:
        r = self.row
        return {
            "demand_id": r["demand_id"],
            "demand_key": r["demand_key"],
            "key_version": r["key_version"],
            "kind": r["kind"],
            "status": r["status"],
            "source_id": r["source_id"],
            "source_sha256": r["source_sha256"],
            "review_policy": r["review_policy"],
            "role_set": r["role_set"],
            "request_identity": json.loads(r["request_identity_json"]),
            "request_identity_sha256": r["request_identity_sha256"],
            "request_sha256": r["request_sha256"],
            "gaps": json.loads(r["gaps_json"]),
            "lease_owner": r["lease_owner"],
            "lease_until": r["lease_until"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "candidate_marker": r["candidate_marker"],
        }


class DurableDemandStore:
    """Single durable owner of the demand queue (REVISED CANDIDATE, option A shape)."""

    def __init__(self, database_path: Path):
        # OPEN-1 option A: in production this is the CW catalog path
        # (…/catalog.sqlite3).  Here it is injected so the attempt stays
        # isolated; the SQL below is additive-migration shaped.
        self.database_path = Path(database_path)

    # ---- connection / migration -----------------------------------------
    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path), timeout=10.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _apply_additive_migration(self, connection: sqlite3.Connection) -> None:
        """One idempotent additive step in the CW store.py discipline.

        Mirrors store.py `_apply_additive_migrations`: every object is created
        with IF NOT EXISTS and the step is safe to re-run on every open.
        """
        try:
            connection.executescript(DEMAND_SCHEMA)
        except sqlite3.Error as exc:
            raise DemandStoreUnavailable(
                f"demand store additive migration failed: {type(exc).__name__}: {exc}"
            ) from exc

    def _open_migrated(self) -> sqlite3.Connection:
        parent = self.database_path.parent
        try:
            parent.mkdir(parents=True, exist_ok=True)
            connection = self._connect()
        except (OSError, sqlite3.Error) as exc:
            raise DemandStoreUnavailable(
                f"demand store unavailable: {type(exc).__name__}: {exc}"
            ) from exc
        self._apply_additive_migration(connection)
        return connection

    # ---- write path -----------------------------------------------------
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
        """Idempotent registration; returns (demand, created).

        v2 semantics: the SAME request resubmitted reuses the same demand_id;
        a DIFFERENT request (even one differing only in as_of_date) creates a
        NEW demand row and is NEVER merged into an existing one.
        """
        stamp = time.time() if now is None else now
        identity = request_identity(request)
        identity_sha = canonical_sha256(identity)
        key = demand_key(
            source_sha256=source_sha256,
            review_policy=review_policy,
            role_set=role_set,
            identity=identity,
        )
        request_sha = canonical_sha256(request)

        connection = self._open_migrated()
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
                "INSERT INTO processing_demands(demand_id,demand_key,key_version,"
                "kind,status,source_id,source_sha256,review_policy,role_set,"
                "request_identity_json,request_identity_sha256,request_sha256,"
                "request_json,gaps_json,candidate_marker,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    demand_id,
                    key,
                    DEMAND_SCHEMA_VERSION,
                    kind,
                    "pending",
                    source_id,
                    source_sha256,
                    review_policy,
                    role_set,
                    json.dumps(identity, ensure_ascii=False, sort_keys=True),
                    identity_sha,
                    request_sha,
                    json.dumps(request, ensure_ascii=False, sort_keys=True),
                    json.dumps(gaps, ensure_ascii=False, sort_keys=True),
                    CANDIDATE_MARKER,
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
            connection.rollback()
            raise DemandStoreUnavailable(
                f"demand store write failed: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            connection.close()

    # ---- read path ------------------------------------------------------
    def list_active(self) -> list[dict]:
        connection = self._open_migrated()
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

    def find_by_request(
        self, *, source_sha256: str, review_policy: str, role_set: str,
        request: dict,
    ) -> list[dict]:
        """All demands for this source, so a reviewer can see non-merging.

        A v2 sanity check: the same source with N distinct requests must yield
        N rows, not one.
        """
        connection = self._open_migrated()
        try:
            rows = connection.execute(
                "SELECT * FROM processing_demands WHERE source_sha256=? "
                "ORDER BY created_at, demand_id",
                (source_sha256,),
            ).fetchall()
        finally:
            connection.close()
        return [ProcessingDemandRecord(r).to_dict() for r in rows]

    def record_attempt(
        self,
        *,
        demand_id: str,
        producer_name: str,
        call_status: str,
        error_redacted: str | None = None,
        artifact_id: str | None = None,
        now: float | None = None,
    ) -> dict:
        """Append one attempt at the REAL call boundary (W05C-N2 discipline).

        `call_status` must come from the call site, never be inferred from
        whether an artifact row exists.
        """
        if call_status not in {"ok", "error", "refused", "skipped"}:
            raise ValueError(f"unknown call_status: {call_status!r}")
        stamp = time.time() if now is None else now
        connection = self._open_migrated()
        try:
            connection.execute("BEGIN IMMEDIATE")
            prior = connection.execute(
                "SELECT COUNT(*) AS n FROM processing_demand_attempts WHERE demand_id=?",
                (demand_id,),
            ).fetchone()["n"]
            attempt_id = f"attempt-{uuid.uuid4().hex[:16]}"
            connection.execute(
                "INSERT INTO processing_demand_attempts(attempt_id,demand_id,"
                "attempt_number,producer_name,call_status,error_redacted,"
                "artifact_id,started_at) VALUES(?,?,?,?,?,?,?,?)",
                (
                    attempt_id, demand_id, prior + 1, producer_name,
                    call_status, error_redacted, artifact_id, stamp,
                ),
            )
            connection.commit()
            row = connection.execute(
                "SELECT * FROM processing_demand_attempts WHERE attempt_id=?",
                (attempt_id,),
            ).fetchone()
            return dict(row)
        except sqlite3.Error as exc:
            connection.rollback()
            raise DemandStoreUnavailable(
                f"demand attempt write failed: {type(exc).__name__}: {exc}"
            ) from exc
        finally:
            connection.close()

    # ---- explicit single-shot claim (OPEN-3) ----------------------------
    def claim(self, *, owner: str, lease_seconds: float = 300.0) -> dict | None:
        """Explicit single consumption grant (never automatic)."""
        stamp = time.time()
        connection = self._open_migrated()
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
        description=f"revised candidate durable demand store ({CANDIDATE_MARKER})"
    )
    parser.add_argument("command", choices=("list", "claim", "list-source"))
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--owner", default="cli")
    parser.add_argument("--source-sha256")
    args = parser.parse_args(argv)
    store = DurableDemandStore(args.database)
    try:
        if args.command == "list":
            payload = {"demands": store.list_active(), "store": str(args.database)}
        elif args.command == "list-source":
            if not args.source_sha256:
                parser.error("--source-sha256 is required for list-source")
            payload = {
                "demands": store.find_by_request(
                    source_sha256=args.source_sha256,
                    review_policy="",
                    role_set="",
                    request={},
                ),
                "store": str(args.database),
            }
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
