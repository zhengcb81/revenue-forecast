"""Read-only coverage diagnostics over source dates and discovery/read receipts."""
from __future__ import annotations

from contracts.evidence import parse_iso_date, require


def analyze_communication_scope(record: dict, sources: dict, as_of_date: str) -> dict:
    scope = record.get("checked_scope")
    if scope is None:
        return {"category": record["category"], "coverage_complete": False,
                "status": "semantically_unverified", "reason": "legacy_scope_not_recorded"}
    require(isinstance(scope, dict) and set(scope) == {"schema_version", "category", "start_date", "end_date", "coverage_complete", "items"}, "communication checked_scope fields are invalid")
    require(scope["schema_version"] == "management-communication-scope/1" and scope["category"] == record["category"], "communication checked_scope category/schema mismatch")
    start = parse_iso_date(scope["start_date"], "communication scope start_date")
    end = parse_iso_date(scope["end_date"], "communication scope end_date")
    cutoff = parse_iso_date(as_of_date, "as_of_date")
    require(start <= end <= cutoff, "communication checked_scope interval is invalid")
    require(type(scope["coverage_complete"]) is bool and isinstance(scope["items"], list), "communication checked_scope completeness/items invalid")
    if record["category"] == "material_announcements_since_last_filing":
        dates = [parse_iso_date(s["published_date"], "filing published_date") for s in sources.values()
                 if s.get("source_type") in {"regulatory_filing", "exchange_filing"}]
        if dates:
            require(start == max(dates), "post-filing checked_scope must start at the latest available filing")
        require(end == cutoff, "post-filing checked_scope must extend through as_of_date")
    item_refs = set()
    read_sources = set()
    unresolved = []
    for item in scope["items"]:
        require(isinstance(item, dict) and set(item) <= {"item_ref", "source_id", "published_date", "content_role", "selected", "read", "skip_reason"}, "communication item fields invalid")
        ref = item.get("item_ref")
        require(isinstance(ref, str) and bool(ref.strip()) and ref not in item_refs, "communication item references must be unique")
        item_refs.add(ref)
        require(type(item.get("selected")) is bool and type(item.get("read")) is bool, "communication selection/read state must be explicit")
        require(item.get("content_role") in {"business_original", "discovery_index", "index_notice"}, "communication item role invalid")
        if item["read"]:
            require(item["selected"] and item["content_role"] == "business_original", "checked communication requires a read business original")
            sid = item.get("source_id")
            require(sid in sources, "read communication requires a registered source")
            published = parse_iso_date(sources[sid]["published_date"], "communication source date")
            require(start <= published <= end, "read communication source is outside checked interval")
            read_sources.add(sid)
        if item.get("published_date") is not None:
            published = parse_iso_date(item["published_date"], "discovery item published_date")
            require(start <= published <= end, "discovery item is outside checked interval")
        if item["selected"] and not item["read"]:
            unresolved.append(ref)
        elif not item["selected"]:
            require(isinstance(item.get("skip_reason"), str) and bool(item["skip_reason"].strip()), "unselected communication requires materiality/skip reason")
    require(read_sources == set(record.get("source_ids", [])), "communication source_ids must match actual read originals")
    complete = scope["coverage_complete"] and not unresolved
    return {"category": record["category"], "status": "verified_scope" if complete else "incomplete",
            "coverage_complete": complete, "start_date": scope["start_date"], "end_date": scope["end_date"],
            "discovered_item_refs": list(sorted(item_refs)), "read_source_ids": list(sorted(read_sources)),
            "unresolved_item_refs": unresolved, "reason": None if complete else "scope_or_selected_content_incomplete"}
