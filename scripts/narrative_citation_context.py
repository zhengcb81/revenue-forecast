"""Resolve RF citation closure from an already validated CWP reading context.

RF consumes the source owner's support/context partition instead of treating every
transported span as an independent fact, and keeps a bounded coverage diagnostic.
This module is pure: no IO, no clock, no network, no model, no source re-parse and
no new source knowledge. The wire contract stays with
``company_wiki_narrative_contracts``; here only the invariants this adapter relies
on are re-checked, with a named refusal instead of a silent guess.

Reading coverage is a diagnostic, never a permission gate: unread/opaque/deferred
pages, sampling ``limited``, an incomplete layout or a missing ``reading_context``
never block a consumption on their own.
"""

from __future__ import annotations

import re
from typing import Any, NoReturn, TypeGuard

TRACE_SCHEMA = "revenue-narrative-citation-trace/1"
CONTEXT_EVIDENCE_LIMIT = 32
COVERAGE_NOTE = "diagnostic_only_not_a_permission_gate"
ATTRIBUTION = {
    "du-production-reading/1": "groups_only",
    "du-production-reading/2": "source_owned_views",
    "du-production-reading/3": "source_owned_views",
    "du-production-reading/4": "source_owned_views",
}
QUESTION_ROLES = frozenset({"analyst", "investor_question"})
UNREAD_LISTS = ("opaque_pages", "deferred_pages", "deferred_unit_ids", "unassigned_unit_ids")
_SHA = re.compile(r"[0-9a-f]{64}\Z")


class NarrativeCitationError(ValueError):
    """Named citation-closure refusal; ``code`` is stable and machine readable."""

    def __init__(self, code: str, detail: str = ""):
        self.code, self.detail = code, detail
        super().__init__(f"{code}: {detail}" if detail else code)


def _fail(code: str, detail: str = "") -> NoReturn:
    raise NarrativeCitationError(code, detail)


def _object(value: Any) -> TypeGuard[dict[str, Any]]:
    return isinstance(value, dict)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _id_list(value: Any, *, field: str) -> list[str]:
    if not isinstance(value, list) or any(not _identifier(item) for item in value):
        _fail("narrative_citation_reading_invalid", f"{field} is not a span id list")
    if len(set(value)) != len(value):
        _fail("narrative_citation_reading_invalid", f"{field} repeats an id")
    return value


def _spans(value: dict) -> dict[str, dict]:
    spans = value.get("evidence_spans")
    if spans is None:
        return {}
    if not isinstance(spans, list):
        _fail("narrative_citation_reading_invalid", "evidence_spans is not a list")
    by_id: dict[str, dict] = {}
    for span in spans:
        if not _object(span) or not _identifier(span.get("span_id")):
            _fail("narrative_citation_reading_invalid", "a transported span has no identity")
        if span["span_id"] in by_id:
            _fail("narrative_citation_reading_invalid", "a transported span id is duplicated")
        by_id[span["span_id"]] = span
    return by_id


def _source_role(span: dict) -> str | None:
    structured = span.get("structured_value")
    if not _object(structured):
        return None
    role = structured.get("source_role")
    return role if _nonempty_text(role) else None


def _group(group: Any, spans: dict[str, dict], attributed: bool, *, support_use: bool = False) -> dict:
    if not _object(group):
        _fail("narrative_citation_reading_invalid", "a reading group is not an object")
    group_id = group.get("group_id")
    if not _identifier(group_id):
        _fail("narrative_citation_reading_invalid", "a reading group has no identity")
    evidence = _id_list(group.get("evidence_ids"), field="a reading group")
    if not evidence:
        _fail("narrative_citation_reading_invalid", "a reading group has no evidence")
    missing = [key for key in evidence if key not in spans]
    if missing:
        _fail("narrative_citation_reading_invalid", "a reading group references a non-transported span")
    if len({spans[key]["source_id"] for key in evidence}) != 1:
        _fail("narrative_citation_reading_invalid", "a reading group mixes original parents")
    views: list[dict] = []
    if attributed:
        raw_views = group.get("citation_views")
        if not isinstance(raw_views, list) or not raw_views:
            _fail("narrative_citation_reading_invalid", "an attributed group has no citation view")
        seen_support: set[frozenset] = set()
        for raw in raw_views:
            if not _object(raw):
                _fail("narrative_citation_reading_invalid", "a citation view is not an object")
            support = _id_list(raw.get("support_evidence_ids"), field="a support set")
            context = _id_list(raw.get("context_evidence_ids"), field="a context set")
            if not support:
                _fail("narrative_citation_reading_invalid", "a citation view has no support")
            if set(support).intersection(context):
                _fail("narrative_citation_reading_invalid", "a citation view overlaps support and context")
            if set(support).union(context) != set(evidence):
                _fail("narrative_citation_reading_invalid", "a citation view does not partition its group")
            identity = frozenset(support)
            if identity in seen_support:
                _fail("narrative_citation_reading_invalid", "a support set is published twice")
            seen_support.add(identity)
            capability = {}
            if support_use:
                use, reason = raw.get("reading_support_use"), raw.get("reading_support_reason")
                if (not isinstance(use, str) or use not in {"support", "context_only", "unresolved"}
                        or not isinstance(reason, str) or re.fullmatch(r"[a-z][a-z0-9_]{0,79}", reason) is None):
                    _fail("narrative_citation_reading_invalid", "a source view has no valid support capability")
                capability = {"reading_support_use": use, "reading_support_reason": reason}
            views.append({"support": support, "context": context, **capability})
    return {
        "group_id": group_id,
        "kind": group.get("kind") if _nonempty_text(group.get("kind")) else None,
        "section_role": (
            group.get("section_role") if _nonempty_text(group.get("section_role")) else None
        ),
        "evidence_ids": evidence,
        "views": views,
    }


def _reading(value: dict | None) -> dict | None:
    if value is None:
        return None
    if not _object(value):
        _fail("narrative_citation_reading_invalid", "the narrative context is not an object")
    reading = value.get("reading_context")
    if reading is None:
        return None
    if not _object(reading):
        _fail("narrative_citation_reading_invalid", "reading_context is not an object")
    if reading.get("schema_version") not in ATTRIBUTION:
        _fail("narrative_citation_reading_invalid", "unsupported reading_context schema")
    return reading


def _groups(value: dict | None) -> tuple[dict | None, list[dict], str]:
    reading = _reading(value)
    spans = _spans(value or {})
    if reading is None:
        return None, [], "absent"
    raw_groups = reading.get("groups")
    if not isinstance(raw_groups, list):
        _fail("narrative_citation_reading_invalid", "reading groups are not a list")
    attributed = ATTRIBUTION[reading["schema_version"]] == "source_owned_views"
    groups = [_group(group, spans, attributed,
                     support_use=reading["schema_version"] == "du-production-reading/4") for group in raw_groups]
    seen: set[str] = set()
    for group in groups:
        if group["group_id"] in seen:
            _fail("narrative_citation_reading_invalid", "a reading group id is duplicated")
        seen.add(group["group_id"])
    return reading, groups, ATTRIBUTION[reading["schema_version"]]


def _count(value: Any) -> int | None:
    """A published count, or ``None`` when the wire does not carry a usable one."""
    return value if type(value) is int and value >= 0 else None


def _page_count(value: Any) -> int | None:
    if not isinstance(value, list) or any(type(page) is not int or page < 1 for page in value):
        return None
    return len(value)


def _id_count(value: Any) -> int | None:
    if not isinstance(value, list) or any(not _identifier(item) for item in value):
        return None
    return len(value)


def _unread_trace(reading: dict | None) -> dict:
    """Coverage is a diagnostic: an unreadable or malformed block degrades to ``null``."""
    unread = reading.get("unread") if reading is not None else None
    if not _object(unread):
        return {
            "counts": None, "limited": None, "opaque_pages": None, "deferred_pages": None,
            "deferred_unit_ids": None, "unassigned_unit_ids": None,
            "native_scan": None, "structure_complete": None,
        }
    pages = {name: _page_count(unread.get(name)) for name in ("opaque_pages", "deferred_pages")}
    units = {name: _id_count(unread.get(name)) for name in ("deferred_unit_ids", "unassigned_unit_ids")}
    counts = unread.get("counts")
    limited = unread.get("limited")
    resolved: dict | None = None
    if _object(counts) and set(counts) == set(UNREAD_LISTS) and type(limited) is bool:
        candidate = {name: _count(counts[name]) for name in UNREAD_LISTS}
        available = {"opaque_pages": pages["opaque_pages"], "deferred_pages": pages["deferred_pages"],
                     "deferred_unit_ids": units["deferred_unit_ids"],
                     "unassigned_unit_ids": units["unassigned_unit_ids"]}
        if all(value is not None and (observed := available[name]) is not None and value >= observed
               for name, value in candidate.items()):
            resolved = candidate
    native_scan = unread.get("native_scan")
    structure = unread.get("structure_complete")
    return {
        "counts": resolved,
        "limited": limited if resolved is not None else None,
        "opaque_pages": pages["opaque_pages"],
        "deferred_pages": pages["deferred_pages"],
        "deferred_unit_ids": units["deferred_unit_ids"],
        "unassigned_unit_ids": units["unassigned_unit_ids"],
        "native_scan": native_scan if _nonempty_text(native_scan) else None,
        "structure_complete": structure if type(structure) is bool else None,
    }


def _deferred_trace(reading: dict | None) -> dict:
    deferred = reading.get("deferred") if reading is not None else None
    listed = len(deferred) if isinstance(deferred, list) else None
    count = _count(reading.get("deferred_count")) if reading is not None else None
    limited = reading.get("deferred_limited") if reading is not None else None
    if listed is None or count is None or count < listed or type(limited) is not bool:
        return {"count": None, "listed": listed, "limited": None}
    return {"count": count, "listed": listed, "limited": limited}


def _diagnostics_trace(reading: dict | None) -> list[dict] | None:
    if reading is None or "selection_diagnostics" not in reading:
        return None
    rows = reading["selection_diagnostics"]
    if not isinstance(rows, list):
        return None
    result = []
    for row in rows:
        count = _count(row.get("count")) if _object(row) else None
        if count is None or not _nonempty_text(row.get("code")):
            return None
        result.append({"code": row["code"], "count": count})
    return result


def _layout_complete(reading: dict | None) -> bool | None:
    if reading is None:
        return None
    layout = reading.get("layout_coverage")
    complete = layout.get("complete") if _object(layout) else None
    return complete if type(complete) is bool else None


def reading_trace(value: dict | None) -> dict:
    """Bounded reading-attribution and coverage diagnostics; never a judgement."""
    reading, groups, attribution = _groups(value)
    result = {
        "present": reading is not None,
        "schema_version": reading["schema_version"] if reading is not None else None,
        "attribution": attribution,
        "group_count": len(groups),
        "citation_view_count": sum(len(group["views"]) for group in groups),
        "unread": _unread_trace(reading),
        "deferred": _deferred_trace(reading),
        "selection_diagnostics": _diagnostics_trace(reading),
        "layout_complete": _layout_complete(reading),
        "coverage_note": COVERAGE_NOTE,
    }
    if reading is not None and reading["schema_version"] == "du-production-reading/4":
        result["support_use_counts"] = {
            use: sum(view["reading_support_use"] == use for group in groups for view in group["views"])
            for use in ("support", "context_only", "unresolved")
        }
    return result


def selection(binding: dict) -> tuple[str | None, int | None]:
    """Parse the two optional selection fields; any other shape is a named refusal."""
    if not _object(binding):
        _fail("narrative_citation_binding_fields", "the binding is not an object")
    group_id = binding.get("citation_group_id")
    view = binding.get("citation_view")
    if group_id is not None and not _identifier(group_id):
        _fail("narrative_citation_binding_fields", "citation_group_id is not a group id")
    if view is not None and (type(view) is not int or view < 0):
        _fail("narrative_citation_binding_fields", "citation_view is not a non-negative index")
    return group_id, view


def _projected(span: dict, projected: bool) -> dict | None:
    """A projected `/3` span keeps its own original parent, locator and pointer."""
    if not projected:
        return None
    structured = span.get("structured_value")
    if not _object(structured):
        _fail("narrative_citation_span_invalid", "a projected span has no binding object")
    parent_sha = structured.get("parent_content_sha256")
    locator = structured.get("source_locator")
    pointer = structured.get("pointer")
    if not (isinstance(parent_sha, str) and _SHA.fullmatch(parent_sha) is not None
            and _nonempty_text(locator) and _nonempty_text(pointer)):
        _fail("narrative_citation_span_invalid", "a projected span lacks its own parent/pointer")
    return {
        "parent_source_id": span.get("source_id"),
        "parent_sha256": parent_sha,
        "source_locator": locator,
        "pointer": pointer,
    }


def _resolution(span: dict, *, closure: str, projected: bool, group: dict | None = None,
                view_index: int | None = None, views: dict | None = None) -> dict:
    context_ids: list[str] | None = None
    support_ids: list[str] | None = None
    evidence: list[dict] | None = None
    if views is not None:
        support_ids = list(views["support"])
        context_ids = list(views["context"])
        evidence = []
    result = {
        "span_id": span.get("span_id"),
        "closure": closure,
        "group_id": group["group_id"] if group else None,
        "group_kind": group["kind"] if group else None,
        "section_role": group["section_role"] if group else None,
        "view_index": view_index,
        "source_role": _source_role(span),
        "support_evidence_ids": support_ids,
        "context_evidence_ids": context_ids,
        "context_evidence": evidence,
        "context_evidence_count": None if context_ids is None else len(context_ids),
        "context_evidence_limited": None if context_ids is None else False,
        "projected": _projected(span, projected),
    }
    if views is not None and "reading_support_use" in views:
        result.update(reading_support_use=views["reading_support_use"],
                      reading_support_reason=views["reading_support_reason"])
    return result


def _context_evidence(resolution: dict, spans: dict[str, dict]) -> None:
    if resolution["context_evidence_ids"] is None:
        return
    limited = resolution["context_evidence_ids"][:CONTEXT_EVIDENCE_LIMIT]
    resolution["context_evidence"] = [
        {
            "span_id": key,
            "locator": spans[key].get("locator"),
            "source_role": _source_role(spans[key]),
        }
        for key in limited
    ]
    resolution["context_evidence_limited"] = len(limited) < resolution["context_evidence_count"]


def resolve_span(value: dict, *, span_id: str, group_id: str | None = None,
                 view: int | None = None) -> dict:
    """Resolve one transported span to its source-owned support/context closure.

    The span's own parent and pointer are recorded; nothing is merged across
    parents. ``group_id``/``view`` are the explicit selection fields; a genuine
    ambiguity is refused instead of taking the first legal view.
    """
    reading, groups, attribution = _groups(value)
    spans = _spans(value)
    projected = _object(value) and value.get("schema_version") == "revenue-narrative-context/3"
    if span_id not in spans:
        _fail("narrative_citation_span_unknown", f"{span_id} is not a transported span")
    span = spans[span_id]
    candidates = [group for group in groups if span_id in group["evidence_ids"]]
    if group_id is not None:
        if group_id not in {group["group_id"] for group in groups}:
            _fail("narrative_citation_group_unknown", f"{group_id} is not a reading group")
        candidates = [group for group in candidates if group["group_id"] == group_id]
        if not candidates:
            _fail("narrative_citation_group_unknown", f"{group_id} does not contain the span")
    if attribution == "source_owned_views":
        capability_owned = reading is not None and reading["schema_version"] == "du-production-reading/4"
        slots = [
            (group, index)
            for group in candidates
            for index, views in enumerate(group["views"])
            if span_id in views["support"]
        ]
        if view is not None:
            if len(candidates) != 1:
                _fail("narrative_citation_group_ambiguous",
                      "an explicit view needs exactly one candidate reading group")
            group = candidates[0]
            if view >= len(group["views"]):
                _fail("narrative_citation_view_unknown",
                      f"the resolved group has {len(group['views'])} citation views")
            if span_id not in group["views"][view]["support"]:
                _fail("narrative_citation_view_not_support",
                      f"span is not support in citation view {view}")
            if capability_owned and group["views"][view]["reading_support_use"] != "support":
                _fail("narrative_citation_" + group["views"][view]["reading_support_use"],
                      "the selected source view does not grant independent factual support")
            slots = [(group, view)]
        else:
            available = [(group, index) for group, index in slots
                         if not capability_owned or group["views"][index]["reading_support_use"] == "support"]
            if capability_owned and slots and not available:
                use = "unresolved" if any(group["views"][index]["reading_support_use"] == "unresolved"
                                          for group, index in slots) else "context_only"
                _fail("narrative_citation_"+use, "the source views do not grant independent factual support")
            slots = available
        if len(slots) == 1:
            group, index = slots[0]
            resolution = _resolution(span, closure="citation_view", projected=projected,
                                     group=group, view_index=index, views=group["views"][index])
        elif not candidates:
            if capability_owned:
                _fail("narrative_citation_unresolved", "the source published no support view for this span")
            resolution = _resolution(span, closure="ungrouped", projected=projected)
        elif not slots:
            _fail("narrative_citation_context_only",
                  "the source only places this span in the context partition")
        elif len({group["group_id"] for group, _index in slots}) > 1:
            _fail("narrative_citation_group_ambiguous",
                  "the span is support in more than one reading group")
        else:
            _fail("narrative_citation_view_ambiguous",
                  "the span is support in more than one citation view")
    else:
        if view is not None:
            _fail("narrative_citation_view_unknown", "this reading context has no citation views")
        if not candidates:
            resolution = _resolution(span, closure="ungrouped", projected=projected)
        else:
            # A groups-only reading publishes no support/context partition, so the
            # published-first group is recorded deterministically (no semantic
            # promotion); ``citation_group_id`` can name another one.
            resolution = _resolution(span, closure="reading_group", projected=projected,
                                     group=candidates[0])
    if resolution["source_role"] in QUESTION_ROLES:
        _fail("narrative_citation_source_role_refused",
              f"source_role {resolution['source_role']} cannot support an RF parameter claim")
    _context_evidence(resolution, spans)
    return resolution


def citation_dependency(*, resolution: dict, claim_id: str, parameter_id: str) -> dict:
    """One claim/parameter closure entry; the existing dependencies stay untouched."""
    result = {
        "claim_id": claim_id,
        "parameter_id": parameter_id,
        "span_id": resolution["span_id"],
        "closure": resolution["closure"],
        "group_id": resolution["group_id"],
        "group_kind": resolution["group_kind"],
        "section_role": resolution["section_role"],
        "view_index": resolution["view_index"],
        "source_role": resolution["source_role"],
        "support_evidence_ids": resolution["support_evidence_ids"],
        "context_evidence_ids": resolution["context_evidence_ids"],
        "context_evidence": resolution["context_evidence"],
        "context_evidence_count": resolution["context_evidence_count"],
        "context_evidence_limited": resolution["context_evidence_limited"],
        "projected": resolution["projected"],
    }
    if "reading_support_use" in resolution:
        result.update(reading_support_use=resolution["reading_support_use"],
                      reading_support_reason=resolution["reading_support_reason"])
    return result


def trace_status(dependencies: list[dict]) -> str:
    closures = [item.get("closure") for item in dependencies]
    if not closures:
        return "not_consumed"
    unique = set(closures)
    if unique == {"citation_view"}:
        return "closed"
    if unique == {"reading_group"}:
        return "group_only"
    if unique == {"ungrouped"}:
        return "ungrouped"
    return "partial"


def citation_trace(value: dict | None, *, dependencies: list[dict] | None = None) -> dict:
    """The versioned citation trace; the only place the closure is retained."""
    entries = [dict(item) for item in (dependencies or [])]
    known = [item for item in entries if item.get("context_evidence_count") is not None]
    return {
        "schema_version": TRACE_SCHEMA,
        "status": trace_status(entries),
        "reading": reading_trace(value),
        "dependencies": entries,
        "counts": {
            "dependencies": len(entries),
            "view_closed": sum(item.get("closure") == "citation_view" for item in entries),
            "group_only": sum(item.get("closure") == "reading_group" for item in entries),
            "ungrouped": sum(item.get("closure") == "ungrouped" for item in entries),
            "context_evidence": sum(item["context_evidence_count"] for item in known),
            "context_evidence_unknown": len(entries) - len(known),
            "context_evidence_limited": sum(bool(item.get("context_evidence_limited")) for item in known),
        },
    }
