"""FC-801: CloseGap binding + isolated bounded-batch execution face
(isolated implementation card I-03-D).

Base = the I-03-C override copy (binding-validation face). This attempt
adds the plan/quota edge demanded by I-03-D, WITHOUT touching any
production module:

- ``validate_close_gap_binding`` / ``CloseGapBinding`` unchanged (same
  value + same version gate, I-03-C);
- ``MAX_BATCH_SIZE = 8`` (I-03-A D5); the per-scenario actual batch cap
  is ``min(binding.max_items, MAX_BATCH_SIZE)`` — documented, not
  silently assumed;
- ``run_close_gap_transaction`` — the isolated close-gap call:
  pre-lock rediscover (metadata only) -> deterministic BARRIER seam ->
  in-lock rediscover -> stale-binding refusal at the REAL validation
  exits (``validate_close_gap_binding`` + ``validate_download_authorization``
  + the D6 stale hash gate) -> bounded batch with explicit per-candidate
  remaining-gap states -> in-stream byte budget -> save raw + sidecar ->
  registration through the R1-R7 gate order (referencing I-02-C's
  register_existing_raw gates; production wiring stays with the I-02
  owner) -> four frozen event types emitted.

Events (decision.md §1) share the I-02 journal envelope fields; the
legacy ``fetch_events`` integer is NOT an event substitute.

``_BARRIER_HOOK`` is a module-level test seam (default no-op): the
harness sets it to a callable receiving ``txn_id`` so the world mutates
between the two rediscover points. No production code is modified.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


CLOSE_GAP_SCHEMA_VERSION = "1.0"
HASH_SCHEMA_VERSION = 1
MAX_BATCH_SIZE = 8  # I-03-A D5 frozen bound

_BARRIER_HOOK = None  # test-only harness seam (decision.md §3)


@dataclass(frozen=True)
class CloseGapBinding:
    """FC-801: the input binding of one authorized close-gap download."""

    request_id: str
    gap_plan_hash: str
    policy_hash: str
    provider: str
    allowed_accessions: tuple[str, ...]
    max_items: int
    max_bytes: int
    expires_at: str
    hash_schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "gap_plan_hash": self.gap_plan_hash,
            "policy_hash": self.policy_hash,
            "provider": self.provider,
            "allowed_accessions": list(self.allowed_accessions),
            "max_items": self.max_items,
            "max_bytes": self.max_bytes,
            "expires_at": self.expires_at,
            "hash_schema_version": self.hash_schema_version,
        }


def _set(xs: tuple[str, ...]) -> set[str]:
    return set(xs)


def validate_close_gap_binding(binding: Any, authorization: Any) -> str | None:
    """Return an error string when the binding does NOT match the
    authorization exactly (same value + same version), else None."""
    if getattr(binding, "hash_schema_version", 0) != getattr(
        authorization, "hash_schema_version", None
    ):
        return (
            "binding version mismatch: binding and authorization must carry "
            "the same hash_schema_version (legacy binding refused)"
        )
    checks: tuple[tuple[str, Any, Any], ...] = (
        ("request_id", binding.request_id, authorization.request_id),
        ("gap_plan_hash", binding.gap_plan_hash, authorization.gap_plan_hash),
        ("policy_hash", binding.policy_hash, authorization.policy_hash),
        ("provider", binding.provider, authorization.provider),
        ("max_items", binding.max_items, authorization.max_items),
        ("max_bytes", binding.max_bytes, authorization.max_bytes),
        ("expires_at", binding.expires_at, authorization.expires_at),
    )
    for name, b_val, a_val in checks:
        if b_val != a_val:
            return f"binding mismatch on {name}"
    if _set(binding.allowed_accessions) != _set(authorization.allowed_accessions):
        return "binding mismatch on allowed_accessions"
    return None


def _txn_id(binding: CloseGapBinding) -> str:
    payload = json.dumps(binding.to_dict(), sort_keys=True, ensure_ascii=False)
    return (
        "urn:company-wiki:close-gap:sha256:"
        + hashlib.sha256(payload.encode("utf-8")).hexdigest()
    )


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class EventLedger:
    """The four frozen event types with I-02-shared envelope fields.

    Four separate structural event streams; ``fetch_events``-style
    counters are legacy compatibility numbers, never a substitute."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def record(self, outcome: str, envelope: dict[str, Any]) -> dict[str, Any]:
        row = {
            "schema_version": "1.0",
            "recorded_at": _utc_now(),
            "outcome": outcome,
            **envelope,
        }
        self.events.append(row)
        return row

    def counts(self) -> dict[str, int]:
        base = {
            "provider_fetch_attempt": 0,
            "bytes_received": 0,
            "raw_saved": 0,
            "registration_succeeded": 0,
        }
        for e in self.events:
            base[e["outcome"]] = base.get(e["outcome"], 0) + 1
        return base

    def total_bytes_received(self) -> int:
        return sum(
            e["chunk_bytes"] for e in self.events if e["outcome"] == "bytes_received"
        )


def _reason_result(
    *,
    txn: str,
    status: str,
    reason: str,
    gap_items: dict[str, Any] | None = None,
    processed: int = 0,
    remaining: int = 0,
    fetch_events: int = 0,
    plan_before_hash: str | None = None,
    plan_in_lock_hash: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "schema_version": CLOSE_GAP_SCHEMA_VERSION,
        "txn_id": txn,
        "status": status,
        "reason": reason,
        "fetch_events": fetch_events,
        "gap_items": gap_items or {},
        "processed_count": processed
        or sum(
            1 for st in (gap_items or {}).values() if st.get("state") in ("completed",)
        ),
        "remaining_count": remaining
        or sum(
            1
            for st in (gap_items or {}).values()
            if st.get("state")
            in (
                "pending_next_batch",
                "pending_authorized_not_fetched",
                "raw_saved_registration_pending",
            )
        ),
        "pending_accessions": sorted(
            cid
            for cid, st in (gap_items or {}).items()
            if st.get("state") not in ("completed", "completed_reused")
        ),
        "plan_before_lock_hash": plan_before_hash,
        "plan_in_lock_hash": plan_in_lock_hash,
    }
    out.update(extra)
    return out


def _candidate_id(cand: Any) -> str:
    return str(getattr(cand, "provider_document_id", "") or "")


def _candidate_url(cand: Any) -> str:
    return str(getattr(cand, "source_url", getattr(cand, "url", "")) or "")


def _ids(seq) -> list[str]:
    return [_candidate_id(c) for c in seq]


def _actionable(plan: Any) -> tuple[Any, ...]:
    """D5: missing + newer_revision, already in the D5 batch order."""
    return tuple(plan.missing) + tuple(plan.newer_revision)


def _plan(spec: dict[str, Any], planner: Any, request: Any) -> Any:
    return planner.build_gap_plan(
        request_id=request.request_id,
        as_of_date=request.as_of_date,
        document_kind=request.document_kind,
        entity=request.entity,
        market=request.market,
        local_handles=list(spec.get("local_handles", [])),
        remote_candidates=list(spec.get("remote_candidates", [])),
        provider_error=spec.get("provider_error"),
        policy_hash=spec.get("policy_hash", ""),
    )


def _blocking_states(plan: Any) -> dict[str, str]:
    """Explicit per-candidate blocked states (never silently dropped)."""
    out: dict[str, str] = {}
    for note in getattr(plan, "ambiguous_candidates", ()):
        out[str(note.get("id"))] = "blocked_ambiguous"
    for note in getattr(plan, "conflicting_candidates", ()):
        out[str(note.get("id"))] = "blocked_conflicting"
    for note in getattr(plan, "unknown_candidates", ()):
        out[str(note.get("id"))] = "blocked_unknown_metadata"
    return out


@dataclass
class _Saved:
    received_bytes: int = 0
    failed_reason: str | None = None
    raw_path: str | None = None
    sidecar_path: str | None = None


def stream_budget_over(
    *, cumulative_bytes: int, chunk_bytes: int, max_bytes: int
) -> tuple[bool, int]:
    """Fail-safe local re-check mirroring validate_stream_budget."""
    cum = cumulative_bytes + chunk_bytes
    return cum > max_bytes, cum


def run_close_gap_transaction(
    *,
    binding: CloseGapBinding,
    authorization: Any,
    planner: Any,
    request: Any,
    rediscover: Any,
    stream: Any,
    registrar: Any,
    auth_module: Any,
    ledger: EventLedger,
    now: str = "2026-07-01T00:00:00Z",
) -> dict[str, Any]:
    txn = _txn_id(binding)

    # Step 1: same-value + same-version binding gate (I-03-C face).
    err = validate_close_gap_binding(binding, authorization)
    if err is not None:
        return _reason_result(txn=txn, status="rejected", reason=err)

    # Step 2: pre-lock rediscover (metadata only, nothing fetched).
    pre = rediscover()
    plan_before = _plan(pre, planner, request)

    # Deterministic BARRIER seam: fires between the two rediscover
    # points; default no-op; the harness injects world mutations (G-D5).
    if _BARRIER_HOOK is not None:
        _BARRIER_HOOK(txn)

    # Step 3: in-lock rediscover + re-check.
    inlock = rediscover()
    if inlock is None:
        return _reason_result(
            txn=txn,
            status="rejected",
            reason="provider_error:discover_failed",
            plan_before_hash=plan_before.gap_hash,
        )
    plan_in = _plan(inlock, planner, request)

    gap_items: dict[str, Any] = {
        cid: {"state": st, "reason": "not actionable (explicit)"}
        for cid, st in _blocking_states(plan_in).items()
    }
    actionable = _actionable(plan_in)

    if not actionable:
        for h in getattr(plan_in, "reuse", ()):
            hid = str(getattr(h, "provider_document_id", "") or "")
            gap_items.setdefault(
                hid, {"state": "completed_reused", "reason": "local reusable handle"}
            )
        return _reason_result(
            txn=txn,
            status="completed",
            reason="gap_already_closed_or_reused",
            gap_items=gap_items,
            processed=len(
                [st for st in gap_items.values() if st["state"] == "completed_reused"]
            ),
            remaining=0,
            fetch_events=0,
            plan_before_hash=plan_before.gap_hash,
            plan_in_lock_hash=plan_in.gap_hash,
            latest_status=plan_in.latest_status,
            not_published_plan=plan_in.not_published,
            provider_unavailable_plan=plan_in.provider_unavailable,
        )

    if plan_in.gap_hash != binding.gap_plan_hash:
        # REAL validation exit #1: the receipt is bound to the OLD plan
        # hash; every candidate of the current plan fails validation.
        probe = actionable[0]
        auth_probe = auth_module.validate_download_authorization(
            authorization,
            probe,
            plan_hash=plan_in.gap_hash,
            now=now,
            items_already_fetched=0,
            bytes_already_fetched=0,
        )
        gap_items = dict(gap_items)
        for c in actionable:
            gap_items[_candidate_id(c)] = {
                "state": "pending_next_batch",
                "reason": "stale binding rejected (stale_gap_hash)",
            }
        return _reason_result(
            txn=txn,
            status="rejected",
            reason="stale_gap_hash",
            gap_items=gap_items,
            fetched=0,
            processed=0,
            remaining=len(actionable),
            fetch_events=0,
            plan_before_hash=plan_before.gap_hash,
            plan_in_lock_hash=plan_in.gap_hash,
            authorization_probe=auth_probe,
        )

    # Step 4: bounded batch (D5): actual cap = min(max_items, MAX_BATCH_SIZE).
    batch_cap = min(int(binding.max_items), MAX_BATCH_SIZE)
    batch = list(actionable[:batch_cap])
    later = list(actionable[batch_cap:])
    for cid in _ids(later):
        gap_items.setdefault(
            cid, {"state": "pending_next_batch", "reason": "beyond this batch cap"}
        )

    bytes_used = 0
    fetch_attempt = 0
    abort_reason: str | None = None
    for cand in batch:
        cid = _candidate_id(cand)
        if abort_reason is not None:
            gap_items[cid] = {
                "state": "pending_authorized_not_fetched",
                "reason": f"txn aborted earlier: {abort_reason}",
            }
            continue

        # REAL validation exit #2: per-candidate authorization.
        auth_err = auth_module.validate_download_authorization(
            authorization,
            cand,
            plan_hash=plan_in.gap_hash,
            now=now,
            items_already_fetched=0,
            bytes_already_fetched=bytes_used,
        )
        if auth_err is not None:
            gap_items[cid] = {
                "state": "pending_authorized_not_fetched",
                "reason": auth_err,
            }
            abort_reason = auth_err
            continue

        fetch_attempt += 1
        ledger.record(
            "provider_fetch_attempt",
            {
                "txn_id": txn,
                "request_id": binding.request_id,
                "provider": getattr(cand, "provider", ""),
                "provider_document_id": cid,
                "source_url": _candidate_url(cand),
                "authorization_receipt_hash": authorization.receipt_hash,
                "binding_plan_hash": plan_in.gap_hash,
                "declared_remote_size": getattr(cand, "remote_size", None),
            },
        )

        cand_request = replace(request, provider_document_id=cid)
        saved = _stream_and_save(
            txn,
            cand,
            binding,
            ledger,
            registrar,
            stream,
            cand_request,
            bytes_used=bytes_used,
        )
        bytes_used += saved.received_bytes
        if saved.failed_reason is None:
            reg = registrar.register(
                raw_path=Path(saved.raw_path),
                sidecar_path=Path(saved.sidecar_path),
                request=cand_request,
            )
            if reg.get("ok"):
                ledger.record(
                    "registration_succeeded",
                    {
                        "txn_id": txn,
                        "request_id": binding.request_id,
                        "provider": getattr(cand, "provider", ""),
                        "provider_document_id": cid,
                        "canonical_path": saved.raw_path,
                        "content_sha256": reg["content_sha256"],
                        "gates": reg["gates"],
                        "idempotent": bool(reg.get("idempotent")),
                    },
                )
                gap_items[cid] = {"state": "completed", "reason": "saved+registered"}
            else:
                gap_items[cid] = {
                    "state": "raw_saved_registration_pending",
                    "reason": f"registration: {reg['reason']}",
                }
        elif (
            saved.failed_reason == "byte_cap_exceeded_in_stream"
            or saved.failed_reason.startswith("provider_error")
        ):
            gap_items[cid] = {
                "state": "pending_authorized_not_fetched",
                "reason": saved.failed_reason,
            }
            abort_reason = saved.failed_reason
            idx = batch.index(cand)
            for rest in batch[idx + 1 :]:
                gap_items.setdefault(
                    _candidate_id(rest),
                    {
                        "state": "pending_authorized_not_fetched",
                        "reason": "txn aborted earlier (cap/provided failure)",
                    },
                )
                break
        else:  # defensive: unknown failure face -> keep explicit
            gap_items[cid] = {
                "state": "pending_authorized_not_fetched",
                "reason": saved.failed_reason,
            }
            abort_reason = saved.failed_reason

    completed = sum(
        1
        for st in gap_items.values()
        if st.get("state") in ("completed", "completed_reused")
    )
    pending = sum(
        1
        for st in gap_items.values()
        if st.get("state")
        in (
            "pending_next_batch",
            "pending_authorized_not_fetched",
            "raw_saved_registration_pending",
        )
    )
    if pending == 0 and completed == len(actionable) + len(
        [st for st in gap_items.values() if st.get("state") == "completed_reused"]
    ):
        status, reason = "completed", "gap_closed_downloaded"
    else:
        status = "completed_partial" if completed else "failed"
        reason = abort_reason or "remaining_gap > 0 (explicit pending retained)"
    return _reason_result(
        txn=txn,
        status=status,
        reason=reason,
        gap_items=gap_items,
        processed=completed,
        remaining=pending,
        fetch_events=fetch_attempt,
        plan_before_hash=plan_before.gap_hash,
        plan_in_lock_hash=plan_in.gap_hash,
    )


def _stream_and_save(
    txn: str,
    cand: Any,
    binding: CloseGapBinding,
    ledger: EventLedger,
    registrar: Any,
    stream: Any,
    request: Any,
    *,
    bytes_used: int = 0,
) -> _Saved:
    """Stream chunks; EVERY received chunk recorded (including the one
    that pushes the cumulative past the cap); raw+sidecar saved only
    with no over-cap; over_cap chunk stops the stream."""
    saved = _Saved()
    buf = bytearray()
    cum = bytes_used
    base = Path(registrar.raw_root)
    try:
        for chunk_index, chunk in enumerate(stream(cand)):
            over, cum = stream_budget_over(
                cumulative_bytes=cum,
                chunk_bytes=len(chunk),
                max_bytes=binding.max_bytes,
            )
            row = {
                "txn_id": txn,
                "request_id": binding.request_id,
                "provider": getattr(cand, "provider", ""),
                "provider_document_id": _candidate_id(cand),
                "source_url": _candidate_url(cand),
                "chunk_index": chunk_index,
                "chunk_bytes": len(chunk),
                "cumulative_bytes": cum,
                "max_bytes": binding.max_bytes,
                "over_cap": over,
                "stream_stopped": over,
            }
            ledger.record("bytes_received", row)
            buf.extend(chunk)
            if over:
                saved.received_bytes = cum
                saved.failed_reason = "byte_cap_exceeded_in_stream"
                return saved
    except Exception as exc:  # provider stream failure, truthfully kept
        saved.received_bytes = cum
        saved.failed_reason = f"provider_error:{type(exc).__name__}:{exc}"
        return saved
    content = bytes(buf)
    sha = hashlib.sha256(content).hexdigest()
    raw = base / f"{_candidate_id(cand)}_{sha[:12]}.pdf"
    sidecar = base / (raw.name + ".source.json")
    receipt = {
        "schema_version": "1.0",
        "retrieved_at": _utc_now(),
        "provider": getattr(cand, "provider", ""),
        "provider_document_id": _candidate_id(cand),
        "source_url": _candidate_url(cand),
        "content_sha256": sha,
        "byte_size": len(content),
    }
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(content)
    sidecar.write_text(
        json.dumps({"receipt": receipt}, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n",
        encoding="utf-8",
    )
    saved.received_bytes = len(content)
    saved.raw_path = str(raw)
    saved.sidecar_path = str(sidecar)
    ledger.record(
        "raw_saved",
        {
            "txn_id": txn,
            "request_id": binding.request_id,
            "provider": getattr(cand, "provider", ""),
            "provider_document_id": _candidate_id(cand),
            "source_url": _candidate_url(cand),
            "canonical_path": str(raw),
            "content_sha256": sha,
            "byte_size": len(content),
            "over_cap_received": False,
        },
    )
    return saved


# ---------------------------------------------------------------------------
# Registration face: a minimal store shell implementing the R1-R7 gate
# order that I-02-C froze for register_existing_raw (REFERENCE, not a
# second production registry):
#   R1 root policy reusable; R2 root containment; R3 adjacent sidecar at
#   <raw>.source.json; R4 provenance completeness (no filename infer);
#   R5 bytes recompute (sha256+size vs sidecar receipt); R6 explicit
#   request identity agreement; R7 registered docs must be active
#   (retired/quarantined refused; idempotent success when already active).
# ---------------------------------------------------------------------------


class MinimalRegistrar:
    """tmp-isolated sqlite store shell (NOT a production registry; feeds
    only the attempt's case increments; fakes stay inside A)."""

    REGISTERED = "registered"

    def __init__(
        self, raw_root: Path, *, root_policy: dict[str, Any], store_path: Path
    ) -> None:
        self.raw_root = Path(raw_root)
        self.root_policy = dict(root_policy)
        self.store_path = Path(store_path)
        conn = sqlite3.connect(self.store_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS documents ("
            "content_sha256 TEXT PRIMARY KEY, status TEXT NOT NULL)"
        )
        conn.commit()
        conn.close()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.store_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS documents ("
            "content_sha256 TEXT PRIMARY KEY, status TEXT NOT NULL)"
        )
        return conn

    def register(
        self, *, raw_path: Path, sidecar_path: Path, request: Any
    ) -> dict[str, Any]:
        gates: dict[str, bool] = {}

        def gate(name: str, ok: bool, reason: str) -> dict[str, Any] | None:
            gates[name] = bool(ok)
            if not ok:
                return {
                    "ok": False,
                    "reason": f"registration: {reason}",
                    "gates": gates,
                }
            return None

        # R1 root policy
        if (
            stop := gate(
                "R1_root_policy_reusable",
                bool(self.root_policy.get("reusable_for_filing")),
                "root_not_reusable",
            )
        ) is not None:
            return stop
        # R2 containment
        try:
            rp = Path(raw_path).resolve()
            in_root = str(rp).startswith(str(Path(self.raw_root).resolve()))
        except OSError:
            in_root = False
        if (
            stop := gate("R2_root_containment", in_root, "raw_out_of_root")
        ) is not None:
            return stop
        raw_path = Path(raw_path)
        # R3 adjacent sidecar
        sp = Path(sidecar_path)
        if (
            stop := gate(
                "R3_sidecar_adjacent",
                sp.exists() and sp.name == raw_path.name + ".source.json",
                "missing_sidecar",
            )
        ) is not None:
            return stop
        # R4 provenance completeness (never inferred from the filename)
        try:
            data = json.loads(sp.read_text(encoding="utf-8"))
            receipt = data["receipt"]
            need = (
                "provider",
                "provider_document_id",
                "content_sha256",
                "byte_size",
                "source_url",
            )
            complete = all(receipt.get(k) for k in need)
        except Exception:
            complete = False
            receipt = {}
        if (
            stop := gate("R4_provenance_complete", complete, "provenance_incomplete")
        ) is not None:
            return stop
        # R5 bytes recompute against CURRENT bytes
        blob = raw_path.read_bytes()
        sha = hashlib.sha256(blob).hexdigest()
        ok = sha == receipt.get("content_sha256") and len(blob) == int(
            receipt.get("byte_size", -2)
        )
        if (stop := gate("R5_bytes_recompute", ok, "bytes_mismatch")) is not None:
            return stop
        # R6 explicit request identity (never inferred)
        same = str(request.provider or "") == receipt.get("provider") and str(
            request.provider_document_id or ""
        ) == receipt.get("provider_document_id")
        if (
            stop := gate("R6_identity_contract", same, "identity_contract")
        ) is not None:
            return stop
        # R7 registered status
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT status FROM documents WHERE content_sha256=?",
                (sha,),
            ).fetchone()
            if row is not None and row[0] != self.REGISTERED:
                return {
                    "ok": False,
                    "reason": f"registration: status_not_active ({row[0]})",
                    "gates": gates,
                }
            idempotent = row is not None
            if row is None:
                conn.execute(
                    "INSERT INTO documents(content_sha256, status) VALUES(?,?)",
                    (sha, self.REGISTERED),
                )
            conn.commit()
        finally:
            conn.close()
        return {
            "ok": True,
            "reason": None,
            "gates": gates,
            "content_sha256": sha,
            "idempotent": idempotent,
        }


def resume_registration(
    *,
    binding: CloseGapBinding,
    authorization: Any,
    registrar: Any,
    request: Any,
    auth_module: Any,
    ledger: EventLedger,
    recovery_raw_path: str,
    recovery_sidecar_path: str,
    now: str = "2026-07-01T00:00:00Z",
) -> dict[str, Any]:
    """G-D8 retry face: ONLY the missing registration is restored.

    A prior ``raw_saved`` event for this binding is required; the
    provider stream is NEVER called (fetch stays 0); the R1-R7 gates
    re-verify CURRENT bytes against the durable sidecar; success emits
    registration_succeeded with gates R1..R7. The recovery location is
    given EXPLICITLY by the caller's manifest (I-02-C D-W02: never
    re-derived from file/dir names)."""
    txn = _txn_id(binding)
    err = validate_close_gap_binding(binding, authorization)
    if err is not None:
        return _reason_result(txn=txn, status="rejected", reason=err)
    prior_raw_saved = [e for e in ledger.events if e["outcome"] == "raw_saved"]
    if not prior_raw_saved:
        return _reason_result(
            txn=txn,
            status="failed",
            reason=(
                "resume_refused: no prior raw_saved evidence; re-download "
                "requires a NEW authorization, never a silent one"
            ),
        )
    reg = registrar.register(
        raw_path=Path(recovery_raw_path),
        sidecar_path=Path(recovery_sidecar_path),
        request=request,
    )
    if reg.get("ok"):
        entry = prior_raw_saved[-1]
        ledger.record(
            "registration_succeeded",
            {
                "txn_id": txn,
                "request_id": binding.request_id,
                "provider": entry.get("provider", ""),
                "provider_document_id": entry.get("provider_document_id", ""),
                "canonical_path": recovery_raw_path,
                "content_sha256": reg["content_sha256"],
                "gates": reg["gates"],
                "idempotent": bool(reg.get("idempotent")),
            },
        )
        return _reason_result(
            txn=txn,
            status="completed",
            reason="registration_recovered_fetch0",
            gap_items={
                entry.get("provider_document_id", ""): {
                    "state": "completed",
                    "reason": "registered (recovered, fetch=0)",
                }
            },
            processed=1,
            remaining=0,
            fetch_events=0,
            seed_gap_hash=binding.gap_plan_hash,
        )
    return _reason_result(
        txn=txn, status="failed", reason=reg["reason"], fetch_events=0
    )
