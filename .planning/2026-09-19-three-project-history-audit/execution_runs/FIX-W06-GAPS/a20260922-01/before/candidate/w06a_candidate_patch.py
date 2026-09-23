"""W06A candidate overlay: the only change source_preparation.py would need.

*** CANDIDATE, UNRATIFIED — lives in iso/candidate, never in a product tree. ***

It restructures `prepare_source` so that:

  1. the request is validated enough to have a durable identity;
  2. a demand is REGISTERED before the not_reviewed safety verdict is applied;
  3. a store failure raises (no silent in-memory fallback) so `demand_queued`
     is never reported when the demand was not persisted;
  4. the block message carries demand_id + next_action, so the block is
     recoverable and observable;
  5. a paused worker is reported, never resumed.

Wiring choice (also a CANDIDATE): the store path, worker-control path and role
set come from the environment (RF_W06_DEMAND_STORE / RF_W06_WORKER_CONTROL /
RF_W06_ROLE_SET).  D-W06 must freeze the real injection point.
"""

from __future__ import annotations

import os
from pathlib import Path

_CANDIDATE = True
_CANDIDATE_MARKER = "candidate-unratified-I-06-A-a20260919-01"


def _demand_gaps(envelope: dict, handle: dict) -> list[dict]:
    """The structured gap of THIS request (never a fabricated review)."""
    bundle = envelope.get("bundle")
    roles_needing_production: list[str] = []
    if isinstance(bundle, dict):
        valid = bundle.get("valid_handles")
        if isinstance(valid, dict):
            roles_needing_production = sorted(
                role for role in ("normalized", "summary", "sections", "markdown")
                if role not in valid
            )
    gaps: list[dict] = []
    status = envelope.get("prompt_injection_status")
    if status in (None, "not_reviewed"):
        gaps.append(
            {
                "gap": "review_required",
                "detail": "prompt_injection_status is not reviewed",
                "observed": status,
                "resolves_by": "run the approved review method for this source",
            }
        )
    for role in roles_needing_production:
        gaps.append(
            {
                "gap": "artifact_missing",
                "detail": f"no reusable {role} artifact in the envelope bundle",
                "observed": role,
                "resolves_by": f"produce the {role} artifact, then retry",
            }
        )
    return gaps


def _register_demand(*, request: dict, handle: dict, envelope: dict) -> dict:
    """Register the durable demand; never raise away the SAFETY verdict.

    F-I06A-02 (review): when the store cannot be written, the security block
    (`prompt injection not reviewed`) must still be the message the caller
    sees.  The store failure is attached to it as structured detail instead of
    replacing it, so a broken store can never hide the safety verdict.
    """
    from processing_demand_store import (
        DemandStoreUnavailable,
        DurableDemandStore,
        read_worker_control,
    )

    worker = read_worker_control(
        Path(os.environ.get("RF_W06_WORKER_CONTROL", ""))
    )
    database = os.environ.get("RF_W06_DEMAND_STORE")
    if not database:
        return {
            "demand_id": None,
            "demand_key": None,
            "created": False,
            "status": "not_registered",
            "gaps": _demand_gaps(envelope, handle),
            "worker": worker,
            "store_error": (
                "demand_store_unavailable: RF_W06_DEMAND_STORE is not "
                "configured (the candidate refuses to fall back to memory)"
            ),
            "candidate_marker": _CANDIDATE_MARKER,
        }
    role_set = os.environ.get("RF_W06_ROLE_SET", "normalized,sections")
    review_policy = str(envelope.get("policy_hash") or "unset-policy")
    try:
        store = DurableDemandStore(Path(database))
        demand, created = store.register(
            kind="source_review_and_production",
            source_id=str(handle.get("source_id") or ""),
            source_sha256=str(handle.get("snapshot_sha256") or ""),
            review_policy=review_policy,
            role_set=role_set,
            gaps=_demand_gaps(envelope, handle),
            request=request,
        )
    except DemandStoreUnavailable as exc:
        return {
            "demand_id": None,
            "demand_key": None,
            "created": False,
            "status": "not_registered",
            "gaps": _demand_gaps(envelope, handle),
            "worker": worker,
            "store_error": f"demand_store_unavailable: {exc}",
            "candidate_marker": _CANDIDATE_MARKER,
        }
    return {
        "demand_id": demand["demand_id"],
        "demand_key": demand["demand_key"],
        "created": created,
        "status": demand["status"],
        "gaps": demand["gaps"],
        "worker": worker,
        "store_error": None,
        "candidate_marker": _CANDIDATE_MARKER,
    }


def block_message(*, prompt_injection_status: str, registration: dict | None) -> str:
    """The refusal text: the SECURITY verdict first, always present.

    A store failure is an ADDITIONAL structured clause of the same block
    (F-I06A-02), never a replacement: the caller must always be able to see
    that the source is unreviewed, and separately that the demand was not
    persisted (`demand_queued` is absent in that case).
    """
    base = (
        "prompt injection not reviewed — source preparation blocked per policy "
        f"(prompt_injection_status={prompt_injection_status})"
    )
    if registration is None:
        return base
    worker = registration.get("worker") or {}
    resume = (
        "worker desired_state is 'paused' — resume requires an explicit "
        "authorised action; this call does not resume it"
        if worker.get("desired_state") == "paused"
        else "worker is not paused"
    )
    gaps = registration.get("gaps") or []
    first = gaps[0].get("resolves_by") if gaps else "review the source"
    store_error = registration.get("store_error")
    if store_error:
        return (
            f"{base}; demand_store_error={store_error}; gaps={len(gaps)} "
            f"next_action={first}; {resume}"
        )
    return (
        f"{base}; demand_queued demand_id={registration['demand_id']} "
        f"source={registration['demand_key'][:16]} gaps={len(gaps)} "
        f"next_action={first}; {resume}"
    )
