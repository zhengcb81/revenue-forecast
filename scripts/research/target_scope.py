"""Resolve declared management scope against the one native segment list.

Segments are flat external-revenue contributions, already reconciled by RF.
This module selects them; it does not infer a hierarchy from names, add company
adjustments to subsets, or calculate a second revenue forecast.
"""
from __future__ import annotations

from contracts.evidence import require


def resolve_scope_segments(data: dict, scope: dict) -> tuple[dict, ...]:
    """Use identical members for validation, dependency ancestry and measurement.

    The limited segment_group shape references native names exactly once.
    Nested groups and adjustment selections are deliberately not part of v1.
    A historical custom scope stays unresolved rather than gaining members by
    matching its display name.
    """
    segments = tuple(data.get("segments", ()))
    kind = scope.get("type")
    if kind == "company":
        return segments
    if kind == "custom":
        return ()
    index = {segment["name"]: segment for segment in segments}
    if kind == "segment":
        name = scope.get("name")
        require(name in index, "unknown management target segment")
        return (index[name],) if name in index else ()
    require(kind == "segment_group", "unsupported management target scope")
    require(set(scope) == {"type", "name", "segment_names"}, "segment_group_fields_are_not_exact")
    members = scope.get("segment_names")
    require(isinstance(members, list) and bool(members), "segment_group_members_required")
    if not isinstance(members, list) or not members:
        return ()
    valid_names = all(isinstance(name, str) and bool(name.strip()) for name in members)
    require(valid_names, "segment_group_member_must_be_name")
    if not valid_names:
        return ()
    require(len(members) == len(set(members)), "segment_group_duplicate_member")
    require(all(name in index for name in members), "segment_group_unknown_member")
    selected = tuple(index[name] for name in members if name in index)
    base_ids = [segment["base_revenue_parameter_id"] for segment in selected
                if isinstance(segment.get("base_revenue_parameter_id"), str)]
    require(len(base_ids) == len(set(base_ids)), "segment_group_overlapping_base")
    return selected
