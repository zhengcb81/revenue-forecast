"""Source-revision GapPlan (isolated implementation card I-03-B).

I-03-A-frozen rewrite of the pure planner: recency is decided by
(filed_at, accepted_at validation, revision chains) on the frozen period
key ``(kind, period_start, period_end)`` — NEVER by provider-document-ID
lexicographic order (persisting defect at old L167-170 / L228-242, rule
``max(accession lexicographic, amended)``, is deleted).

Frozen semantics implemented (I-03-A D1-D6, oracle C01-C15):

- D1  period key = (kind, period_start, period_end); fiscal_year is a
      derived display label (period_end year); missing period =>
      explicit unknown bucket; same FY different periods never merge;
- D2  filed_at is the sole recency primary; accepted_at validates
      (accepted_at < filed_at => conflicting) or substitutes with a
      degraded date_basis; four explicit states: ordered /
      ambiguous_same_day / conflicting / unknown_missing_date;
- D3  remote with later filed_at => newer_revision; remote only older =>
      local NOT demoted, latest_status=unknown_if_remote_confirmed_newer;
- D4  already_covered / not_published / no_gap are independent fields;
      latest_status five-value enum; future (filed_at > as_of) into an
      explicit future bucket, never blocking the as_of view;
      empty provider success != not_published (conservative false while
      no adapter exhaustiveness declaration exists — I-03-A open note);
- D5  planner-facing ordering only: actionable candidates sorted
      (period_start DESC, filed_at DESC, provider_document_id); batch
      execution/completed_partial stay I-03-C;
- D6  gap_hash = SHA-256 over canonical JSON of every qualification
      field, hash_schema_version=1; authorization epoch binding stays
      I-03-C; the provider id appears in the hash only inside the frozen
      determinism sort key, never as a recency signal.

Caller contract unchanged: same keyword interface; prior GapPlan fields
untouched; new fields additive with defaults; callers keep consuming
this single output without modification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


GAP_PLAN_SCHEMA_VERSION = "1.0"
HASH_SCHEMA_VERSION = 1

LATEST_LOCAL_CONFIRMED = "local_is_latest_confirmed"
LATEST_NEWER_REMOTE = "newer_remote_available"
LATEST_UNKNOWN_REMOTE_NEWER = "unknown_if_remote_confirmed_newer"
LATEST_UNKNOWN_PROVIDER = "unknown_provider_failed"
LATEST_UNKNOWN_EMPTY = "unknown_empty_success"

STATE_ORDERED = "ordered"
STATE_AMBIGUOUS = "ambiguous_same_day"
STATE_CONFLICTING = "conflicting"
STATE_UNKNOWN_DATE = "unknown_missing_date"

_OK = "ok"
_UNKEYED = "explicit_unknown"


@dataclass(frozen=True)
class GapPlan:
    schema_version: str
    request_id: str
    as_of_date: str
    document_kind: str
    entity: str
    market: str
    reuse: tuple[Any, ...] = ()
    missing: tuple[Any, ...] = ()
    newer_revision: tuple[Any, ...] = ()
    not_published: bool = False
    provider_unavailable: bool = False
    provider_reason: str | None = None
    future: tuple[Any, ...] = ()
    gap_hash: str = ""
    # --- I-03-A additive frozen fields (D1-D6) ---
    latest_status: str = ""
    already_covered: bool = False
    no_gap: bool = True
    hash_schema_version: int = HASH_SCHEMA_VERSION
    ambiguous_candidates: tuple[Any, ...] = ()
    conflicting_candidates: tuple[Any, ...] = ()
    unknown_candidates: tuple[Any, ...] = ()
    superseded_remote: tuple[Any, ...] = ()
    unusable_local: tuple[Any, ...] = ()
    period_reports: tuple[Any, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "as_of_date": self.as_of_date,
            "document_kind": self.document_kind,
            "entity": self.entity,
            "market": self.market,
            "reuse": [h.to_dict() if hasattr(h, "to_dict") else h for h in self.reuse],
            "missing": [
                c.to_dict() if hasattr(c, "to_dict") else c for c in self.missing
            ],
            "newer_revision": [
                c.to_dict() if hasattr(c, "to_dict") else c for c in self.newer_revision
            ],
            "not_published": self.not_published,
            "provider_unavailable": self.provider_unavailable,
            "provider_reason": self.provider_reason,
            "future": [
                c.to_dict() if hasattr(c, "to_dict") else c for c in self.future
            ],
            "gap_hash": self.gap_hash,
            "latest_status": self.latest_status,
            "already_covered": self.already_covered,
            "no_gap": self.no_gap,
            "hash_schema_version": self.hash_schema_version,
            "ambiguous_candidates": _raw(self.ambiguous_candidates),
            "conflicting_candidates": _raw(self.conflicting_candidates),
            "unknown_candidates": _raw(self.unknown_candidates),
            "superseded_remote": _raw(self.superseded_remote),
            "unusable_local": _raw(self.unusable_local),
            "period_reports": _raw(self.period_reports),
        }


def _raw(items: tuple[Any, ...]) -> list[Any]:
    out = []
    for i in items:
        if isinstance(i, dict):
            out.append({k: v for k, v in i.items() if k != "object"})
        else:
            out.append(i.to_dict() if hasattr(i, "to_dict") else i)
    return out


def _candidate_id(candidate: Any) -> str:
    return str(getattr(candidate, "provider_document_id", "") or "")


def _candidate_kind(candidate: Any, default: str) -> str:
    return str(
        getattr(candidate, "document_kind", None)
        or getattr(candidate, "kind", None)
        or default
    )


def _candidate_dates(candidate: Any) -> tuple[str | None, str | None]:
    """Local handles expose filed_at/published_date; remote candidates
    filing_date (mapping declared and approved in iso_patching.md)."""
    filed = (
        getattr(candidate, "filed_at", None)
        or getattr(candidate, "filing_date", None)
        or getattr(candidate, "published_date", None)
    )
    accepted = getattr(candidate, "accepted_at", None)
    return (str(filed) if filed else None, str(accepted) if accepted else None)


def _date_state(candidate: Any) -> tuple[str, str | None]:
    """D2 four-state, never a boolean. Returns (state, effective_date)."""
    filed, accepted = _candidate_dates(candidate)
    if not filed and not accepted:
        return STATE_UNKNOWN_DATE, None
    if filed and accepted and accepted < filed:
        return STATE_CONFLICTING, None
    if not filed and accepted:
        return STATE_ORDERED, accepted  # degraded: date_basis=accepted_at
    return STATE_ORDERED, filed


def _period_key(candidate: Any, default_kind: str) -> tuple[str, str]:
    kind = _candidate_kind(candidate, default_kind)
    ps = getattr(candidate, "period_start", None)
    pe = getattr(candidate, "period_end", None)
    if not ps or not pe:
        return f"{kind}|unknown|unknown", _UNKEYED
    return f"{kind}|{ps}|{pe}", _OK


def _candidate_amended(candidate: Any) -> bool:
    return bool(getattr(candidate, "amended", False))


def _usable_handles_split(handles: list[Any]) -> tuple[list[Any], list[Any]]:
    """ZR-406: capture-incomplete handles are never reusable evidence."""
    usable, unusable = [], []
    for h in handles:
        if getattr(h, "capture_ready", True) is False:
            unusable.append(h)
        else:
            usable.append(h)
    return usable, unusable


def _families(items: list[Any], default_kind: str) -> dict[str, dict[str, list[Any]]]:
    """Group by frozen period key; missing period and bad dates go to
    explicit non-actionable buckets — never silently dropped (D1/D2)."""
    groups: dict[str, dict[str, list[Any]]] = {}
    for item in items:
        key, confidence = _period_key(item, default_kind)
        state, _eff = _date_state(item)
        bucket = groups.setdefault(key, {_OK: [], _UNKEYED: []})
        if confidence != _OK:
            bucket[_UNKEYED].append(item)
        elif state == STATE_UNKNOWN_DATE:
            bucket.setdefault(STATE_UNKNOWN_DATE, []).append(item)
        elif state == STATE_CONFLICTING:
            bucket.setdefault(STATE_CONFLICTING, []).append(item)
        else:
            bucket[_OK].append(item)
    return groups


def _sort_key(candidate: Any, default_kind: str = "") -> tuple:
    """D6 deterministic sort key (recency-neutral; accession only here)."""
    filed, accepted = _candidate_dates(candidate)
    return (
        _candidate_kind(candidate, default_kind),
        str(getattr(candidate, "period_start", "") or ""),
        str(getattr(candidate, "period_end", "") or ""),
        filed or "",
        accepted or "",
        str(getattr(candidate, "provider", "") or ""),
        _candidate_id(candidate),
        str(getattr(candidate, "revision", "") or ""),
        str(getattr(candidate, "source_url", getattr(candidate, "url", "")) or ""),
    )


def _batch_key(candidate: Any) -> tuple[str, str, str]:
    """D5 batch order: period_start DESC, filed_at DESC, provider_document_id.
    DESC over ISO strings via inverted codepoints (total order, pure)."""
    filed, _accepted = _candidate_dates(candidate)
    return (
        _invert(str(getattr(candidate, "period_start", "") or "")),
        _invert(filed or ""),
        _candidate_id(candidate),
    )


def _invert(s: str) -> str:
    return "".join(chr(0x10FFFF - ord(ch)) for ch in s)


def _same_day_state(day_members: list[Any]) -> tuple[str, Any]:
    """D2: one amended sub-document over amended=false bases => ordered;
    otherwise ambiguous_same_day (no silent pick, no ID pick)."""
    if len(day_members) == 1:
        return STATE_ORDERED, day_members[0]
    amended = [c for c in day_members if _candidate_amended(c)]
    bases = [c for c in day_members if not _candidate_amended(c)]
    if len(amended) == 1 and bases:
        return STATE_ORDERED, amended[0]
    return STATE_AMBIGUOUS, None


def _newest_remote(remotes: list[Any]) -> tuple[str, Any, list[Any]]:
    """Recency purely by effective filed date (order of the input list is
    irrelevant: bins by date, takes max date, resolves same-day chains)."""
    by_date: dict[str, list[Any]] = {}
    for c in remotes:
        by_date.setdefault(_date_state(c)[1] or "", []).append(c)
    latest_date = max(by_date)
    latest_day = by_date[latest_date]
    superseded = [c for d, cs in by_date.items() if d != latest_date for c in cs]
    state, newest = _same_day_state(latest_day)
    if state == STATE_ORDERED and newest is not None:
        superseded.extend(c for c in latest_day if c is not newest)
    return state, newest, superseded


def _candidate_note(candidate: Any, reason: str) -> dict[str, Any]:
    filed, accepted = _candidate_dates(candidate)
    return {
        "reason": reason,
        "id": _candidate_id(candidate),
        "kind": _candidate_kind(candidate, ""),
        "period_start": str(getattr(candidate, "period_start", "") or ""),
        "period_end": str(getattr(candidate, "period_end", "") or ""),
        "filed_at": filed or "",
        "accepted_at": accepted or "",
        "url": str(
            getattr(candidate, "source_url", getattr(candidate, "url", "")) or ""
        ),
        "object": candidate,
    }


def _qualification(candidate: Any, entity: str, market: str) -> dict[str, Any]:
    filed, accepted = _candidate_dates(candidate)
    return {
        "entity": entity,
        "market": market,
        "kind": _candidate_kind(candidate, ""),
        "period_start": str(getattr(candidate, "period_start", "") or ""),
        "period_end": str(getattr(candidate, "period_end", "") or ""),
        "fiscal_year": getattr(candidate, "fiscal_year", None),
        "provider": str(getattr(candidate, "provider", "") or ""),
        "id": _candidate_id(candidate),
        "filed_at": filed or "",
        "accepted_at": accepted or "",
        "revision": str(getattr(candidate, "revision", "") or ""),
        "amended": _candidate_amended(candidate),
        "url": str(
            getattr(candidate, "source_url", getattr(candidate, "url", "")) or ""
        ),
    }


def _notes_payload(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stripped = [{k: v for k, v in n.items() if k != "object"} for n in notes]
    return sorted(
        stripped, key=lambda n: json.dumps(n, sort_keys=True, ensure_ascii=False)
    )


def _hash_gap(
    *,
    request_id: str,
    as_of_date: str,
    document_kind: str,
    entity: str,
    market: str,
    reuse: list[Any],
    missing: list[Any],
    newer_revision: list[Any],
    future: list[Any],
    superseded_remote: list[Any],
    ambiguous: list[dict[str, Any]],
    conflicting: list[dict[str, Any]],
    unknown: list[dict[str, Any]],
    unusable_local: list[Any],
    provider_unavailable: bool,
    provider_reason: str | None,
    latest_status: str,
    not_published: bool,
    no_gap: bool,
    policy_hash: str = "",
) -> str:
    """D6: canonical JSON SHA-256 over every qualification field
    (hash_schema_version=1) PLUS the policy epoch binding (I-03-C: the
    plan-level D6 field ``policy_hash`` — I-03-B's deferred placeholder —
    joins the hash, so a policy-epoch change invalidates the plan hash).
    Any qualification change => different hash (old authorization
    fail-closed at the I-03-C validate step)."""
    payload: dict[str, Any] = {
        "hash_schema_version": HASH_SCHEMA_VERSION,
        "request_id": request_id,
        "as_of_date": as_of_date,
        "document_kind": document_kind,
        "entity": entity,
        "market": market,
        "policy_hash": policy_hash,
        "latest_status": latest_status,
        "not_published": not_published,
        "provider_unavailable": provider_unavailable,
        "provider_reason": provider_reason,
        "no_gap": no_gap,
        "reuse": [_qualification(h, entity, market) for h in reuse],
        "missing": [_qualification(c, entity, market) for c in missing],
        "newer_revision": [_qualification(c, entity, market) for c in newer_revision],
        "future": [_qualification(c, entity, market) for c in future],
        "superseded_remote": [
            _qualification(c, entity, market) for c in superseded_remote
        ],
        "unusable_local": [_qualification(h, entity, market) for h in unusable_local],
        "ambiguous_candidates": _notes_payload(ambiguous),
        "conflicting_candidates": _notes_payload(conflicting),
        "unknown_candidates": _notes_payload(unknown),
    }
    blob = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_gap_plan(
    *,
    request_id: str,
    as_of_date: str,
    document_kind: str,
    entity: str,
    market: str,
    local_handles: list[Any],
    remote_candidates: list[Any],
    provider_error: str | None = None,
    policy_hash: str = "",
) -> GapPlan:
    """Align local reusable handles with remote provider metadata under the
    frozen (kind, period_start, period_end) period key and filed_at
    recency (I-03-A D1-D6). Pure function: metadata only, no network.
    ``policy_hash`` binds the policy epoch into the gap hash (I-03-C)."""
    usable, unusable = _usable_handles_split(local_handles)

    unknown_candidates: list[dict[str, Any]] = []
    conflicting_candidates: list[dict[str, Any]] = []
    ambiguous_candidates: list[dict[str, Any]] = []
    future: list[Any] = []
    reuse: list[Any] = []
    missing: list[Any] = []
    newer_revision: list[Any] = []
    superseded_remote: list[Any] = []
    period_reports: list[dict[str, Any]] = []
    fk = document_kind

    def side_note(obj: Any, is_local: bool) -> dict[str, Any] | None:
        key, confidence = _period_key(obj, fk)
        state, _eff = _date_state(obj)
        if confidence != _OK:
            what = "period_missing_local" if is_local else "period_missing_metadata"
            return _candidate_note(obj, what)
        if state == STATE_CONFLICTING:
            return _candidate_note(obj, "accepted_at_before_filed_at")
        if state == STATE_UNKNOWN_DATE:
            return _candidate_note(obj, STATE_UNKNOWN_DATE)
        return None

    if provider_error:
        # Provider failure: keep local reusable evidence, never claim
        # up-to-date; locals with bad/missing metadata stay explicit.
        for h in usable:
            note = side_note(h, is_local=True)
            if note:
                if note["reason"] == "accepted_at_before_filed_at":
                    conflicting_candidates.append(note)
                else:
                    unknown_candidates.append(note)
        ordered_reuse = sorted(usable, key=lambda h: _sort_key(h, fk))
        return GapPlan(
            schema_version=GAP_PLAN_SCHEMA_VERSION,
            request_id=request_id,
            as_of_date=as_of_date,
            document_kind=document_kind,
            entity=entity,
            market=market,
            reuse=tuple(ordered_reuse),
            not_published=False,
            provider_unavailable=True,
            provider_reason=provider_error,
            latest_status=LATEST_UNKNOWN_PROVIDER,
            already_covered=bool(usable),
            no_gap=True,
            conflicting_candidates=tuple(conflicting_candidates),
            unknown_candidates=tuple(unknown_candidates),
            unusable_local=tuple(
                _candidate_note(h, "capture_ready_false") for h in unusable
            ),
            gap_hash=_hash_gap(
                request_id=request_id,
                as_of_date=as_of_date,
                document_kind=document_kind,
                entity=entity,
                market=market,
                reuse=ordered_reuse,
                missing=[],
                newer_revision=[],
                future=[],
                superseded_remote=[],
                ambiguous=[],
                conflicting=conflicting_candidates,
                unknown=unknown_candidates,
                unusable_local=unusable,
                provider_unavailable=True,
                provider_reason=provider_error,
                latest_status=LATEST_UNKNOWN_PROVIDER,
                not_published=False,
                no_gap=True,
                policy_hash=policy_hash,
            ),
        )

    local_families = _families(usable, fk)
    remote_families = _families(remote_candidates, fk)
    period_keys = sorted(set(local_families) | set(remote_families))

    local_groups_total = 0
    local_groups_confirmed = 0
    local_groups_unconfirmed = 0
    any_eligible_remote = False
    any_local_seen = False

    for key in period_keys:
        lgrp = local_families.get(key, {_OK: [], _UNKEYED: []})
        rgrp = remote_families.get(key, {_OK: [], _UNKEYED: []})
        locals_ok = list(lgrp[_OK])
        locals_unkeyed = list(lgrp[_UNKEYED])
        remotes_ok = list(rgrp[_OK])
        remotes_unknown = list(rgrp.get(STATE_UNKNOWN_DATE, []))
        remotes_conflicting = list(rgrp.get(STATE_CONFLICTING, []))
        remotes_unkeyed = list(rgrp[_UNKEYED])

        unknown_candidates.extend(
            _candidate_note(c, "period_missing_local") for c in locals_unkeyed
        )
        unknown_candidates.extend(
            _candidate_note(c, "period_missing_metadata") for c in remotes_unkeyed
        )
        conflicting_candidates.extend(
            _candidate_note(c, "accepted_at_before_filed_at")
            for c in remotes_conflicting
        )
        unknown_candidates.extend(
            _candidate_note(c, STATE_UNKNOWN_DATE) for c in remotes_unknown
        )

        eligible: list[Any] = []
        for c in remotes_ok:
            _state, eff = _date_state(c)
            if eff is not None and eff > as_of_date:
                future.append(c)
            else:
                eligible.append(c)
        if eligible:
            any_eligible_remote = True
        if locals_ok or locals_unkeyed:
            any_local_seen = True

        local_max = max(
            (_date_state(h)[1] for h in locals_ok if _date_state(h)[1]), default=None
        )
        local_ids = {_candidate_id(h) for h in locals_ok}
        group_state = STATE_ORDERED
        resolution = None

        if locals_ok:
            reuse.extend(locals_ok)

        derived_fy = None
        for member in locals_ok + eligible:
            pe = str(getattr(member, "period_end", "") or "")
            if pe[:4].isdigit():
                derived_fy = int(pe[:4])
                break

        if eligible:
            sel_state, newest, older = _newest_remote(eligible)
            superseded_remote.extend(older)
            group_state = sel_state
            if sel_state == STATE_AMBIGUOUS:
                by_date: dict[str, list[Any]] = {}
                for c in eligible:
                    by_date.setdefault(_date_state(c)[1] or "", []).append(c)
                day_members = sorted(
                    by_date[max(by_date)], key=lambda c: _sort_key(c, fk)
                )
                for c in day_members:
                    ambiguous_candidates.append(_candidate_note(c, STATE_AMBIGUOUS))
                resolution = STATE_AMBIGUOUS
                local_groups_unconfirmed += 1 if locals_ok else 0
            elif _candidate_id(newest) in local_ids:
                local_groups_total += 1
                local_groups_confirmed += 1
                resolution = LATEST_LOCAL_CONFIRMED
            elif locals_ok:
                local_groups_total += 1
                local_groups_unconfirmed += 1
                if local_max is None:
                    unknown_candidates.append(
                        _candidate_note(newest, "local_date_missing")
                    )
                    resolution = "unknown_local_date_missing"
                elif _date_state(newest)[1] > local_max:
                    newer_revision.append(newest)
                    resolution = LATEST_NEWER_REMOTE
                elif _date_state(newest)[1] < local_max:
                    superseded_remote.append(newest)  # reverse: local not demoted (D3)
                    resolution = LATEST_UNKNOWN_REMOTE_NEWER
                else:
                    is_chain = _candidate_amended(newest) and any(
                        not _candidate_amended(h)
                        and _date_state(h)[1] == _date_state(newest)[1]
                        for h in locals_ok
                    )
                    if is_chain:
                        newer_revision.append(newest)
                        resolution = LATEST_NEWER_REMOTE
                    else:
                        ambiguous_candidates.append(
                            _candidate_note(newest, "cross_local_same_day")
                        )
                        for h in locals_ok:
                            if _date_state(h)[1] == _date_state(newest)[1]:
                                ambiguous_candidates.append(
                                    _candidate_note(h, "cross_local_same_day")
                                )
                        group_state = STATE_AMBIGUOUS
                        resolution = STATE_AMBIGUOUS
            else:
                missing.append(newest)
                resolution = "missing_newest_only"
        elif locals_ok:
            if (
                remotes_ok
                or future
                or remotes_unknown
                or remotes_conflicting
                or remotes_unkeyed
            ):
                local_groups_total += 1
                local_groups_unconfirmed += 1
                resolution = LATEST_UNKNOWN_REMOTE_NEWER
            else:
                resolution = LATEST_UNKNOWN_REMOTE_NEWER

        pe_part = key.split("|")[2] if key.count("|") == 2 else ""
        derived_fy = derived_fy or (
            int(pe_prefix) if (pe_prefix := pe_part[:4]).isdigit() else None
        )
        period_reports.append(
            {
                "period_key": key,
                "fiscal_year_label": derived_fy,
                "state": group_state,
                "resolution": resolution,
                "local_ids": sorted(_candidate_id(h) for h in locals_ok),
            }
        )

    reuse_sorted = sorted(reuse, key=lambda c: _sort_key(c, fk))
    missing_sorted = sorted(missing, key=_batch_key)
    newer_sorted = sorted(newer_revision, key=_batch_key)
    future_sorted = sorted(future, key=lambda c: _sort_key(c, fk))
    superseded_sorted = sorted(superseded_remote, key=lambda c: _sort_key(c, fk))

    no_gap = not missing_sorted and not newer_sorted

    # D4 decision table for latest_status (five-value enum, always set):
    if missing_sorted or newer_sorted:
        latest_status = LATEST_NEWER_REMOTE
    elif not any_local_seen and not any_eligible_remote:
        latest_status = LATEST_UNKNOWN_EMPTY
    elif any_local_seen and local_groups_total > 0 and local_groups_unconfirmed == 0:
        latest_status = LATEST_LOCAL_CONFIRMED
    else:
        latest_status = LATEST_UNKNOWN_REMOTE_NEWER

    return GapPlan(
        schema_version=GAP_PLAN_SCHEMA_VERSION,
        request_id=request_id,
        as_of_date=as_of_date,
        document_kind=document_kind,
        entity=entity,
        market=market,
        reuse=tuple(reuse_sorted),
        missing=tuple(missing_sorted),
        newer_revision=tuple(newer_sorted),
        not_published=False,  # conservative: no exhaustive-knowledge field exists
        provider_unavailable=False,
        provider_reason=None,
        future=tuple(future_sorted),
        latest_status=latest_status,
        already_covered=bool(reuse_sorted),
        no_gap=no_gap,
        ambiguous_candidates=tuple(ambiguous_candidates),
        conflicting_candidates=tuple(conflicting_candidates),
        unknown_candidates=tuple(unknown_candidates),
        superseded_remote=tuple(superseded_sorted),
        unusable_local=tuple(
            _candidate_note(h, "capture_ready_false") for h in unusable
        ),
        period_reports=tuple(period_reports),
        gap_hash=_hash_gap(
            request_id=request_id,
            as_of_date=as_of_date,
            document_kind=document_kind,
            entity=entity,
            market=market,
            reuse=reuse_sorted,
            missing=missing_sorted,
            newer_revision=newer_sorted,
            future=future_sorted,
            superseded_remote=superseded_sorted,
            ambiguous=ambiguous_candidates,
            conflicting=conflicting_candidates,
            unknown=unknown_candidates,
            unusable_local=unusable,
            provider_unavailable=False,
            provider_reason=None,
            latest_status=latest_status,
            not_published=False,
            no_gap=no_gap,
            policy_hash=policy_hash,
        ),
    )
