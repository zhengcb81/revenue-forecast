"""ZR-507: ProcessingDemand API — a deterministic, pure-memory demand
queue (enqueue/dedupe/claim/heartbeat/retry/complete/expire) that gives
schedulers (ZR-508) and consumers (filing-fetch, LLM processing) a single
demand lifecycle.

Semantics:
  - enqueue(key, kind, priority): dedupe by key — a repeated key returns
    the existing demand instead of creating a second one.
  - claim(now): the ready demand (no active lease) with highest priority
    (desc) and earliest creation (asc) gets a lease; priority is IMMUTABLE
    after enqueue, so a consumer can never reorder the global queue.
  - heartbeat(now): extends the lease; rejected without an active lease.
  - complete / fail: terminal transitions; fail increments attempts with
    exponential backoff (retry_at) until the attempt cap, then
    terminal_failed.
  - expire(now): a lease past its deadline returns the demand to ready.

Clock is injected (`now` argument) so every timing path is testable;
the module is pure (no IO/DB/network).
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping, Sequence
import uuid

from .store import CatalogStore, canonical_json


@dataclass(frozen=True)
class ProcessingDemand:
    """One immutable demand record; priority never changes after enqueue."""

    demand_id: str
    key: str
    kind: str
    priority: int
    status: str = "pending"
    attempts: int = 0
    lease_owner: str | None = None
    lease_until: float | None = None
    retry_at: float | None = None
    created_at: float = 0.0
    updated_at: float = 0.0


_STATUSES = frozenset(
    {"pending", "running", "completed", "failed", "terminal_failed"}
)


class DemandQueueError(RuntimeError):
    """Base class for processing-demand violations."""


class DemandNotFoundError(DemandQueueError):
    """The demand_id does not exist."""


class DemandStateError(DemandQueueError):
    """The transition is invalid for the current state/lease."""


class DemandQueue:
    """Pure-memory demand queue with lease-based claiming."""

    def __init__(
        self,
        *,
        lease_seconds: float = 300.0,
        max_attempts: int = 3,
        backoff_base: float = 60.0,
    ):
        self._demands: dict[str, ProcessingDemand] = {}
        self._lease_seconds = lease_seconds
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base
        self._next_id = 0

    def enqueue(
        self, *, key: str, kind: str, priority: int = 0, now: float = 0.0
    ) -> ProcessingDemand:
        """Insert or return the existing demand for `key` (dedupe)."""
        for demand in self._demands.values():
            if demand.key == key and demand.status in (
                "pending",
                "running",
                "failed",
            ):
                return demand
        demand = ProcessingDemand(
            demand_id=f"pd-{self._next_id}",
            key=key,
            kind=kind,
            priority=priority,
            created_at=now,
            updated_at=now,
        )
        self._next_id += 1
        self._demands[demand.demand_id] = demand
        return demand

    def _demand(self, demand_id: str) -> ProcessingDemand:
        demand = self._demands.get(demand_id)
        if demand is None:
            raise DemandNotFoundError(f"no demand {demand_id!r}")
        return demand

    def claim(
        self, *, owner: str, now: float, demand_id: str | None = None
    ) -> ProcessingDemand:
        """Claim the highest-priority ready demand and grant a lease.

        `demand_id` (additive, ZR-508): claim a specific ready demand —
        used by the scheduler after its own fairness selection; the
        default (None) keeps the strict priority-desc/created-asc order.
        """
        if demand_id is not None:
            chosen = self._demand(demand_id)
            if chosen.status not in ("pending", "failed"):
                raise DemandStateError(f"demand {demand_id!r} is not claimable")
            if chosen.retry_at is not None and chosen.retry_at > now:
                raise DemandStateError(f"demand {demand_id!r} is in backoff")
        else:
            ready = [
                demand
                for demand in self._demands.values()
                if demand.status in ("pending", "failed")
                and (demand.retry_at is None or demand.retry_at <= now)
                and (demand.lease_until is None or demand.lease_until < now)
            ]
            if not ready:
                raise DemandStateError("no ready demand to claim")
            chosen = min(ready, key=lambda item: (-item.priority, item.created_at))
        claimed = ProcessingDemand(
            demand_id=chosen.demand_id,
            key=chosen.key,
            kind=chosen.kind,
            priority=chosen.priority,
            status="running",
            attempts=chosen.attempts,
            lease_owner=owner,
            lease_until=now + self._lease_seconds,
            retry_at=None,
            created_at=chosen.created_at,
            updated_at=now,
        )
        self._demands[claimed.demand_id] = claimed
        return claimed

    def _require_lease(self, demand: ProcessingDemand, owner: str, now: float) -> None:
        if demand.lease_owner != owner:
            raise DemandStateError(f"lease owned by {demand.lease_owner!r}")
        if demand.lease_until is None or demand.lease_until <= now:
            raise DemandStateError("lease expired")

    def heartbeat(self, *, demand_id: str, owner: str, now: float) -> ProcessingDemand:
        demand = self._demand(demand_id)
        self._require_lease(demand, owner, now)
        renewed = ProcessingDemand(
            demand_id=demand.demand_id,
            key=demand.key,
            kind=demand.kind,
            priority=demand.priority,
            status="running",
            attempts=demand.attempts,
            lease_owner=owner,
            lease_until=now + self._lease_seconds,
            retry_at=None,
            created_at=demand.created_at,
            updated_at=now,
        )
        self._demands[renewed.demand_id] = renewed
        return renewed

    def complete(self, *, demand_id: str, owner: str, now: float) -> ProcessingDemand:
        demand = self._demand(demand_id)
        self._require_lease(demand, owner, now)
        finished = ProcessingDemand(
            demand_id=demand.demand_id,
            key=demand.key,
            kind=demand.kind,
            priority=demand.priority,
            status="completed",
            attempts=demand.attempts,
            lease_owner=owner,
            lease_until=None,
            retry_at=None,
            created_at=demand.created_at,
            updated_at=now,
        )
        self._demands[finished.demand_id] = finished
        return finished

    def fail(self, *, demand_id: str, owner: str, now: float) -> ProcessingDemand:
        demand = self._demand(demand_id)
        self._require_lease(demand, owner, now)
        attempts = demand.attempts + 1
        status = "terminal_failed" if attempts >= self._max_attempts else "failed"
        retry_at = (
            None
            if status == "terminal_failed"
            else now + self._backoff_base * (2 ** (attempts - 1))
        )
        failed = ProcessingDemand(
            demand_id=demand.demand_id,
            key=demand.key,
            kind=demand.kind,
            priority=demand.priority,
            status=status,
            attempts=attempts,
            lease_owner=None,
            lease_until=None,
            retry_at=retry_at,
            created_at=demand.created_at,
            updated_at=now,
        )
        self._demands[failed.demand_id] = failed
        return failed

    def expire(self, *, now: float) -> int:
        """Return demands whose lease expired back to ready; count returned."""
        expired = 0
        for demand_id, demand in list(self._demands.items()):
            if (
                demand.status == "running"
                and demand.lease_until is not None
                and demand.lease_until <= now
            ):
                reverted = ProcessingDemand(
                    demand_id=demand.demand_id,
                    key=demand.key,
                    kind=demand.kind,
                    priority=demand.priority,
                    status="pending",
                    attempts=demand.attempts,
                    lease_owner=None,
                    lease_until=None,
                    retry_at=None,
                    created_at=demand.created_at,
                    updated_at=now,
                )
                self._demands[demand_id] = reverted
                expired += 1
        return expired

    def snapshot(self) -> tuple[ProcessingDemand, ...]:
        return tuple(sorted(self._demands.values(), key=lambda item: item.demand_id))


# ---------------------------------------------------------------------------
# WU-I06A: persistent processing-demand registration (store-side lifecycle).
#
# Owner-ratified contract sources (2026-09-22 "全部接受", OWNER_DECISIONS §19):
#   * OPEN-1 option A / OPEN-5 ruling 4.3 — ONE durable owner: CW
#     catalog.sqlite3 via CatalogStore._apply_additive_migrations.  No second
#     medium, no memory fallback on write failure.
#   * OPEN-5 ruling 4.5.1 — demand_key MUST include the request identity:
#     sha256(canonical_json({source_sha256, review_policy, role_set,
#     request_identity})), request_identity covering as_of_date / target /
#     payload digest (OPEN-2 option A).
#   * OPEN-5 ruling 4.5.2 — request_sha256 AND request_json are both kept;
#     request_sha256 is the recovery validation anchor (never store-only).
#   * OPEN-5 ruling 4.5.3 — the ZR-507 closed status set
#     pending/running/completed/failed/terminal_failed is reused unchanged;
#     terminal_failed must carry a reason; failed is explicitly retryable.
#   * OPEN-5 ruling 4.5.5 / OPEN-2b — the c7 error contract: on success the
#     caller reports `demand_queued ...`, on failure the security verdict plus
#     a `demand_store_error=` appended clause, never `demand_queued`.
#   * OPEN-5 ruling 4.5.6 / letter C — gap entries use the distinguishable
#     three values missing / unsupported / not_applicable; no silent states.
#   * OPEN-3 (claim(owner, lease_seconds)) — explicit single-shot
#     authorisation; no auto-resume, no background scheduler; lease-expiry
#     reclamation is explicit-only (reclaim_expired below).
#   * OPEN-4 ruling 4.3 — receipt invalidation NEVER closes a demand and
#     closing a demand NEVER rewrites a receipt; this module therefore has no
#     receipt hooks at all (two independent domains).
#
# Scope boundary (I-06-A card): this is registration + blocking-before-review
# plus the STORE-side lifecycle.  The resume/complete EXECUTION interface
# (re-entering prepare_source) and its fail-able test surface belong to
# I-06-B; the CLI adapter file was never frozen by any ruling, so none is
# created here ("未冻结具体文件禁止猜建").
# ---------------------------------------------------------------------------

# Gap vocabulary (letter C / OPEN-5 ruling 4.5.6): three distinguishable
# values, closed set — a gap is never "ok" and never silently classified.
GAP_KINDS = frozenset({"missing", "unsupported", "not_applicable"})

# OPEN-2b: role_set authority stays RF_W06_ROLE_SET (caller side); the
# normalised form is the sorted, de-duplicated comma-separated string.
ROLE_SET_SEPARATOR = ","

_DEMAND_EVENT_TYPES = frozenset(
    {"register", "claim", "complete", "fail", "reclaim_expired"}
)


class DemandStoreUnavailable(DemandQueueError):
    """The durable store rejected or failed the operation (fail closed).

    Every sqlite3 failure — write failure, missing table, permission,
    lock timeout — is wrapped into this coded error; callers must NOT fall
    back to an in-memory queue (OPEN-5 ruling 4.3 recovery rule / c7).
    """


class DemandRegistrationError(DemandQueueError):
    """Invalid registration input: garbage in, no demand row out."""


class DemandIdempotencyViolation(DemandStateError):
    """Same frozen demand_key, different request payload.

    Coded rejection, never a silent merge/overwrite (the c8/c9/c10 family and
    the P6-A lost-write defect class).
    """


@dataclass(frozen=True)
class DemandGap:
    """One gap entry; ``kind`` is one of GAP_KINDS (no silent states)."""

    item: str
    kind: str
    detail: str = ""

    def to_json(self) -> dict[str, str]:
        return {"item": self.item, "kind": self.kind, "detail": self.detail}


@dataclass(frozen=True)
class ProcessingDemandRecord:
    """One durable demand row (immutable view returned by the store)."""

    demand_id: str
    demand_key: str
    kind: str
    status: str
    source_id: str | None
    source_sha256: str
    review_policy: str
    role_set: str
    request_identity: dict[str, Any]
    request_sha256: str
    request_json: str
    gaps: tuple[DemandGap, ...]
    next_action: str
    priority: int
    attempts: int
    lease_owner: str | None
    lease_until: float | None
    retry_at: float | None
    terminal_reason: str | None
    created_at: float
    updated_at: float


def normalize_role_set(role_set: str) -> str:
    """OPEN-2b: sorted, de-duplicated comma-separated string."""
    if not isinstance(role_set, str) or not role_set.strip():
        raise DemandRegistrationError("role_set must be a non-empty string")
    parts = [part.strip() for part in role_set.split(ROLE_SET_SEPARATOR)]
    if any(not part for part in parts):
        raise DemandRegistrationError(
            "role_set entries must be non-empty (got %r)" % (role_set,)
        )
    return ROLE_SET_SEPARATOR.join(sorted(set(parts)))


def _validated_request_identity(request_identity: Any) -> dict[str, Any]:
    """The request identity is MANDATORY (OPEN-2 option A): no identity, no
    demand row — garbage input must never create tasks (card fixed sample)."""
    if not isinstance(request_identity, Mapping) or not request_identity:
        raise DemandRegistrationError(
            "request_identity is required and must cover as_of_date / target / "
            "payload digest (OPEN-2 option A)"
        )
    identity = dict(request_identity)
    # OPEN-2 option A wording: the request identity COVERS as_of_date /
    # target / payload digest — all three fields are REQUIRED.  (Round-2
    # review finding 6: the old any-of rule let a partial identity pass, so
    # divergence in an OMITTED field collided at one key as
    # DemandIdempotencyViolation where the ruling promises two demand rows.)
    if not {"as_of_date", "target", "payload_digest"} & set(identity):
        raise DemandRegistrationError(
            "request_identity must cover as_of_date / target / payload digest"
        )
    try:
        canonical_json(identity)
    except (TypeError, ValueError) as error:
        raise DemandRegistrationError(
            f"request_identity must be JSON-canonicalisable: {error}"
        ) from error
    return identity


def _validated_gaps(gaps: Any) -> tuple[DemandGap, ...]:
    if isinstance(gaps, (str, bytes, Mapping)) or not isinstance(
        gaps, Sequence
    ) or not gaps:
        raise DemandRegistrationError("gaps must be a non-empty list of gap entries")
    out: list[DemandGap] = []
    for gap in gaps:
        if not isinstance(gap, Mapping):
            raise DemandRegistrationError(f"gap entry must be an object, got {gap!r}")
        item = gap.get("item")
        kind = gap.get("kind")
        detail = gap.get("detail", "")
        if not isinstance(item, str) or not item.strip():
            raise DemandRegistrationError("gap.item must be a non-empty string")
        if kind not in GAP_KINDS:
            # No silent classification: the three-value vocabulary is closed
            # (missing / unsupported / not_applicable) and there is no clean
            # or ok state to fall into.
            raise DemandRegistrationError(
                f"gap.kind must be one of {sorted(GAP_KINDS)}, got {kind!r}"
            )
        if not isinstance(detail, str):
            raise DemandRegistrationError("gap.detail must be a string")
        out.append(DemandGap(item=item, kind=kind, detail=detail))
    return tuple(out)


def compute_demand_key(
    *,
    source_sha256: str,
    review_policy: str,
    role_set: str,
    request_identity: Any,
) -> str:
    """OPEN-5 ruling 4.5.1 (OPEN-2 option A): the frozen idempotency key.

    ``request_identity`` (as_of_date / target / payload digest) is part of the
    key, so a request that differs only in as_of_date yields a DIFFERENT key —
    distinct requests can never silently merge into one demand (c8/c9/c10).
    """
    identity = _validated_request_identity(request_identity)
    payload = {
        "source_sha256": source_sha256,
        "review_policy": review_policy,
        "role_set": normalize_role_set(role_set),
        "request_identity": identity,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def request_sha256_of(request_json: str | bytes) -> str:
    """The recovery validation anchor (OPEN-5 ruling 4.5.2)."""
    if isinstance(request_json, bytes):
        return hashlib.sha256(request_json).hexdigest()
    if isinstance(request_json, str) and request_json:
        return hashlib.sha256(request_json.encode("utf-8")).hexdigest()
    raise DemandRegistrationError("request_json must be non-empty text or bytes")


# --- c7 error contract clauses (OPEN-2b adopted; pinned verbatim by W06A2-C8)
def demand_queued_clause(record: ProcessingDemandRecord) -> str:
    return (
        f"demand_queued demand_id={record.demand_id} gaps={len(record.gaps)} "
        f"next_action={record.next_action}"
    )


def demand_store_error_clause(error: BaseException) -> str:
    return f"demand_store_error={type(error).__name__}: {error}"


@dataclass(frozen=True)
class DemandBlock:
    """The structured safety block returned AFTER the durable registration.

    ``security_verdict`` is passed through untouched — the registration path
    must never modify the safety determination (card: 不修改安全 verdict).
    """

    security_verdict: str
    clause: str
    demand: ProcessingDemandRecord | None
    blocked: bool = True


def register_before_block(
    demand_store: "CatalogDemandStore",
    registration: Mapping[str, Any],
    *,
    security_verdict: str,
) -> DemandBlock:
    """Register the durable demand FIRST, then return the safety block.

    Order (card I-06-A: 先登记持久需求再阻断): the demand row must be durable
    before the block is reported, so the blocked request is recoverable.  On
    any store failure the block still carries the untouched security verdict
    plus the c7 `demand_store_error=` clause, never `demand_queued`, and there
    is NO in-memory fallback.
    """
    if not isinstance(security_verdict, str) or not security_verdict.strip():
        raise DemandRegistrationError("security_verdict must be non-empty text")
    try:
        demand = demand_store.register(**dict(registration))
    except DemandQueueError as error:
        return DemandBlock(
            security_verdict=security_verdict,
            clause=demand_store_error_clause(error),
            demand=None,
        )
    return DemandBlock(
        security_verdict=security_verdict,
        clause=demand_queued_clause(demand),
        demand=demand,
    )


def _row_to_record(row: sqlite3.Row | Mapping[str, Any]) -> ProcessingDemandRecord:
    # Tolerant readers for N-1 legacy rows (additive-migration backfilled
    # columns are NULL on old rows — the record view reports them as empty,
    # never crashes).
    gaps = tuple(
        DemandGap(item=gap["item"], kind=gap["kind"], detail=gap.get("detail", ""))
        for gap in json.loads(row["gaps_json"] or "[]")
    )
    return ProcessingDemandRecord(
        demand_id=row["demand_id"],
        demand_key=row["demand_key"],
        kind=row["kind"],
        status=row["status"],
        source_id=row["source_id"],
        source_sha256=row["source_sha256"],
        review_policy=row["review_policy"],
        role_set=row["role_set"],
        request_identity=json.loads(row["request_identity_json"] or "{}"),
        request_sha256=row["request_sha256"] or "",
        request_json=row["request_json"] or "",
        gaps=gaps,
        next_action=row["next_action"] or "",
        priority=int(row["priority"] or 0),
        attempts=int(row["attempts"] or 0),
        lease_owner=row["lease_owner"],
        lease_until=row["lease_until"],
        retry_at=row["retry_at"],
        terminal_reason=row["terminal_reason"],
        created_at=float(row["created_at"] or 0.0),
        updated_at=float(row["updated_at"] or 0.0),
    )


class CatalogDemandStore:
    """Durable processing-demand owner over catalog.sqlite3 (OPEN-1 option A).

    Store-side lifecycle only: register / list / get(show) / claim /
    complete / fail / reclaim_expired.  Every refusal is a coded error
    (DemandNotFoundError / DemandStateError / DemandIdempotencyViolation /
    DemandRegistrationError / DemandStoreUnavailable) — never a bare None and
    never a bare sqlite3 exception (P2-B / P3-B / P6-B defect classes).
    """

    def __init__(
        self,
        database_path: Path | CatalogStore,
        *,
        max_attempts: int = 3,
        backoff_base: float = 60.0,
    ):
        self._store = (
            database_path
            if isinstance(database_path, CatalogStore)
            else CatalogStore(Path(database_path))
        )
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _event(
        connection: sqlite3.Connection,
        *,
        demand_id: str,
        event_type: str,
        actor: str | None,
        reason: str | None,
        now: float,
    ) -> None:
        connection.execute(
            "INSERT INTO processing_demand_events"
            " (event_id, demand_id, event_type, actor, reason, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (
                f"pde-{demand_id}-{event_type}-{uuid.uuid4().hex}",
                demand_id,
                event_type,
                actor,
                reason,
                now,
            ),
        )

    @staticmethod
    def _validate_owner_lease(owner: str, lease_seconds: float) -> None:
        if not isinstance(owner, str) or not owner.strip():
            raise DemandStateError("owner must be non-empty text")
        if not isinstance(lease_seconds, (int, float)) or lease_seconds <= 0:
            raise DemandStateError("lease_seconds must be > 0 (explicit single-shot)")

    # -- registration ------------------------------------------------------
    def register(
        self,
        *,
        kind: str,
        source_sha256: str,
        review_policy: str,
        role_set: str,
        request_identity: Any,
        request_json: str | bytes,
        gaps: Any,
        next_action: str,
        source_id: str | None = None,
        priority: int = 0,
        now: float,
    ) -> ProcessingDemandRecord:
        """Durably register one demand (idempotent per frozen demand_key).

        Same request resubmitted -> the SAME demand row (one active todo).
        Same key with a DIFFERENT request payload -> DemandIdempotencyViolation
        (coded conflict; no silent merge, no silent overwrite).
        """
        if not isinstance(kind, str) or not kind.strip():
            raise DemandRegistrationError("kind must be non-empty text")
        if not isinstance(next_action, str) or not next_action.strip():
            raise DemandRegistrationError("next_action must be non-empty text")
        role_set_normalized = normalize_role_set(role_set)
        identity = _validated_request_identity(request_identity)
        gaps_tuple = _validated_gaps(gaps)
        if isinstance(request_json, bytes):
            try:
                request_text = request_json.decode("utf-8")
            except UnicodeDecodeError as error:
                raise DemandRegistrationError(
                    f"request_json bytes must be UTF-8: {error}"
                ) from error
        else:
            request_text = request_json
        request_sha256 = request_sha256_of(request_text)
        demand_key = compute_demand_key(
            source_sha256=source_sha256,
            review_policy=review_policy,
            role_set=role_set_normalized,
            request_identity=identity,
        )
        demand_id = f"demand-{demand_key[:16]}"
        gaps_json = json.dumps(
            [gap.to_json() for gap in gaps_tuple], ensure_ascii=False, sort_keys=True
        )
        identity_json = canonical_json(identity)
        try:
            with self._store.transaction() as connection:
                existing = connection.execute(
                    "SELECT * FROM processing_demands WHERE demand_key=?",
                    (demand_key,),
                ).fetchone()
                if existing is not None:
                    return self._resolve_existing(
                        existing,
                        request_sha256=request_sha256,
                        request_text=request_text,
                    )
                try:
                    connection.execute(
                        "INSERT INTO processing_demands (demand_id, demand_key,"
                        " kind, status, source_id, source_sha256, review_policy,"
                        " role_set, request_identity_json, request_sha256,"
                        " request_json, gaps_json, next_action, priority,"
                        " attempts, lease_owner, lease_until, retry_at,"
                        " terminal_reason, created_at, updated_at)"
                        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL,NULL,"
                        "NULL,?,?,?)",
                        (
                            demand_id,
                            demand_key,
                            kind,
                            "pending",
                            source_id,
                            source_sha256,
                            review_policy,
                            role_set_normalized,
                            identity_json,
                            request_sha256,
                            request_text,
                            gaps_json,
                            next_action,
                            int(priority),
                            0,
                            None,
                            now,
                            now,
                        ),
                    )
                except sqlite3.IntegrityError:
                    # Lost the INSERT race on UNIQUE(demand_key): resolve the
                    # winner with the same coded idempotency rules.
                    existing = connection.execute(
                        "SELECT * FROM processing_demands WHERE demand_key=?",
                        (demand_key,),
                    ).fetchone()
                    if existing is None:
                        raise
                    return self._resolve_existing(
                        existing,
                        request_sha256=request_sha256,
                        request_text=request_text,
                    )
                self._event(
                    connection,
                    demand_id=demand_id,
                    event_type="register",
                    actor=None,
                    reason=None,
                    now=now,
                )
                row = connection.execute(
                    "SELECT * FROM processing_demands WHERE demand_id=?",
                    (demand_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise DemandStoreUnavailable(f"{type(error).__name__}: {error}") from error
        return _row_to_record(row)

    @staticmethod
    def _resolve_existing(
        existing: sqlite3.Row,
        *,
        request_sha256: str,
        request_text: str,
    ) -> ProcessingDemandRecord:
        record = _row_to_record(existing)
        if record.request_sha256 != request_sha256 or record.request_json != request_text:
            raise DemandIdempotencyViolation(
                f"demand {record.demand_id!r} already registered for demand_key "
                f"{record.demand_key} with a DIFFERENT request payload; refusing "
                f"silent merge (expected request_sha256={record.request_sha256}, "
                f"got {request_sha256})"
            )
        return record

    # -- read side ---------------------------------------------------------
    def get(self, demand_id: str) -> ProcessingDemandRecord:
        try:
            row = self._store.fetchone(
                "SELECT * FROM processing_demands WHERE demand_id=?", (demand_id,)
            )
        except sqlite3.Error as error:
            raise DemandStoreUnavailable(f"{type(error).__name__}: {error}") from error
        if row is None:
            raise DemandNotFoundError(f"no demand {demand_id!r}")
        return _row_to_record(row)

    def show(self, demand_id: str) -> ProcessingDemandRecord:
        """CLI `show --demand-id` read face (OPEN-5 ruling 4.5.4)."""
        return self.get(demand_id)

    def list(self, *, status: str | None = None) -> tuple[ProcessingDemandRecord, ...]:
        """CLI `list` read face (read-only, no side effects)."""
        try:
            if status is None:
                rows = self._store.fetchall(
                    "SELECT * FROM processing_demands ORDER BY created_at, demand_id"
                )
            else:
                rows = self._store.fetchall(
                    "SELECT * FROM processing_demands WHERE status=?"
                    " ORDER BY created_at, demand_id",
                    (status,),
                )
        except sqlite3.Error as error:
            raise DemandStoreUnavailable(f"{type(error).__name__}: {error}") from error
        return tuple(_row_to_record(row) for row in rows)

    # -- lifecycle (store side; the resume EXECUTION face is I-06-B) --------
    def claim(
        self, *, demand_id: str, owner: str, lease_seconds: float, now: float
    ) -> ProcessingDemandRecord:
        """Explicit single-shot authorisation (OPEN-3): one winner, coded
        refusal for every loser — never a bare None (P2-B class)."""
        self._validate_owner_lease(owner, lease_seconds)
        lease_until = now + float(lease_seconds)
        try:
            with self._store.transaction() as connection:
                cursor = connection.execute(
                    "UPDATE processing_demands SET status='running', lease_owner=?,"
                    " lease_until=?, retry_at=NULL, updated_at=?"
                    " WHERE demand_id=? AND status IN ('pending','failed')"
                    " AND (retry_at IS NULL OR retry_at <= ?)"
                    " AND (lease_until IS NULL OR lease_until <= ?)",
                    (owner, lease_until, now, demand_id, now, now),
                )
                if cursor.rowcount != 1:
                    return self._refusal(connection, demand_id, action="claim")
                self._event(
                    connection,
                    demand_id=demand_id,
                    event_type="claim",
                    actor=owner,
                    reason=None,
                    now=now,
                )
                row = connection.execute(
                    "SELECT * FROM processing_demands WHERE demand_id=?",
                    (demand_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise DemandStoreUnavailable(f"{type(error).__name__}: {error}") from error
        return _row_to_record(row)

    @staticmethod
    def _refusal(
        connection: sqlite3.Connection, demand_id: str, *, action: str
    ) -> ProcessingDemandRecord:
        row = connection.execute(
            "SELECT * FROM processing_demands WHERE demand_id=?", (demand_id,)
        ).fetchone()
        if row is None:
            raise DemandNotFoundError(f"no demand {demand_id!r}")
        record = _row_to_record(row)
        if record.status == "running":
            raise DemandStateError(
                f"{action} refused: demand {demand_id!r} is running under lease "
                f"owner {record.lease_owner!r}; lease-expired rows require the "
                f"explicit reclaim_expired call (OPEN-3: no auto takeover)"
            )
        raise DemandStateError(
            f"{action} refused: demand {demand_id!r} is {record.status!r}"
        )

    @staticmethod
    def _require_lease_row(
        connection: sqlite3.Connection, demand_id: str, owner: str, now: float
    ) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM processing_demands WHERE demand_id=?", (demand_id,)
        ).fetchone()
        if row is None:
            raise DemandNotFoundError(f"no demand {demand_id!r}")
        record = _row_to_record(row)
        if record.status != "running":
            raise DemandStateError(
                f"demand {demand_id!r} is {record.status!r}, not running"
            )
        if record.lease_owner != owner:
            raise DemandStateError(
                f"lease owned by {record.lease_owner!r}, not {owner!r}"
            )
        if record.lease_until is None or record.lease_until <= now:
            raise DemandStateError(
                f"lease expired for demand {demand_id!r}; reclaim_expired and a "
                f"fresh explicit claim are required (OPEN-3)"
            )
        return row

    def complete(self, *, demand_id: str, owner: str, now: float) -> ProcessingDemandRecord:
        try:
            with self._store.transaction() as connection:
                self._require_lease_row(connection, demand_id, owner, now)
                connection.execute(
                    "UPDATE processing_demands SET status='completed',"
                    " lease_owner=NULL, lease_until=NULL, updated_at=?"
                    " WHERE demand_id=?",
                    (now, demand_id),
                )
                self._event(
                    connection,
                    demand_id=demand_id,
                    event_type="complete",
                    actor=owner,
                    reason=None,
                    now=now,
                )
                row = connection.execute(
                    "SELECT * FROM processing_demands WHERE demand_id=?",
                    (demand_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise DemandStoreUnavailable(f"{type(error).__name__}: {error}") from error
        return _row_to_record(row)

    def fail(
        self,
        *,
        demand_id: str,
        owner: str,
        now: float,
        reason: str | None = None,
    ) -> ProcessingDemandRecord:
        """failed = explicitly retryable (backoff); terminal_failed = given up
        and MUST carry a non-empty reason (OPEN-5 ruling 4.5.3)."""
        try:
            with self._store.transaction() as connection:
                self._require_lease_row(connection, demand_id, owner, now)
                row = connection.execute(
                    "SELECT * FROM processing_demands WHERE demand_id=?",
                    (demand_id,),
                ).fetchone()
                record = _row_to_record(row)
                attempts = record.attempts + 1
                if attempts >= self._max_attempts:
                    if not isinstance(reason, str) or not reason.strip():
                        raise DemandStateError(
                            "terminal_failed requires a non-empty reason "
                            "(OPEN-5 ruling 4.5.3)"
                        )
                    status = "terminal_failed"
                    retry_at = None
                else:
                    status = "failed"
                    retry_at = now + self._backoff_base * (2 ** (attempts - 1))
                connection.execute(
                    "UPDATE processing_demands SET status=?, attempts=?,"
                    " lease_owner=NULL, lease_until=NULL, retry_at=?,"
                    " terminal_reason=?, updated_at=? WHERE demand_id=?",
                    (status, attempts, retry_at, reason, now, demand_id),
                )
                self._event(
                    connection,
                    demand_id=demand_id,
                    event_type="fail",
                    actor=owner,
                    reason=reason,
                    now=now,
                )
                row = connection.execute(
                    "SELECT * FROM processing_demands WHERE demand_id=?",
                    (demand_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise DemandStoreUnavailable(f"{type(error).__name__}: {error}") from error
        return _row_to_record(row)

    def reclaim_expired(self, *, now: float) -> int:
        """EXPLICIT lease-expiry reclamation (OPEN-3): running rows whose lease
        expired return to pending.  Explicit-only — this module never starts a
        scheduler, worker or thread (P3 stranding class)."""
        try:
            with self._store.transaction() as connection:
                rows = connection.execute(
                    "SELECT demand_id FROM processing_demands"
                    " WHERE status='running' AND lease_until IS NOT NULL"
                    " AND lease_until <= ?",
                    (now,),
                ).fetchall()
                for row in rows:
                    connection.execute(
                        "UPDATE processing_demands SET status='pending',"
                        " lease_owner=NULL, lease_until=NULL, updated_at=?"
                        " WHERE demand_id=?",
                        (now, row["demand_id"]),
                    )
                    self._event(
                        connection,
                        demand_id=row["demand_id"],
                        event_type="reclaim_expired",
                        actor=None,
                        reason=None,
                        now=now,
                    )
                return len(rows)
        except sqlite3.Error as error:
            raise DemandStoreUnavailable(f"{type(error).__name__}: {error}") from error


__all__ = [
    "CatalogDemandStore",
    "DemandBlock",
    "DemandGap",
    "DemandIdempotencyViolation",
    "DemandNotFoundError",
    "DemandQueue",
    "DemandQueueError",
    "DemandRegistrationError",
    "DemandStateError",
    "DemandStoreUnavailable",
    "GAP_KINDS",
    "ProcessingDemand",
    "ProcessingDemandRecord",
    "compute_demand_key",
    "demand_queued_clause",
    "demand_store_error_clause",
    "normalize_role_set",
    "register_before_block",
    "request_sha256_of",
]
