"""Read-only coverage diagnostics over source dates and discovery/read receipts."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from contracts.evidence import parse_iso_date, require


_FINANCIAL_KINDS = frozenset({"annual_report", "semi_annual_report", "quarterly_report"})
_IssuerKey = tuple[str | None, tuple[str, str] | None]


def _source_manifest(source: dict) -> dict | None:
    """Consume the producer-verified fine type; no second identity validation."""
    trace = source.get("company_wiki_trace")
    manifest = trace.get("source_manifest") if isinstance(trace, dict) else None
    return manifest if isinstance(manifest, dict) else None


def _issuer_key(source: dict) -> _IssuerKey:
    manifest = _source_manifest(source) or {}
    market, security = manifest.get("market"), manifest.get("security_id")
    return manifest.get("canonical_entity_id"), (market, security) if market and security else None


def _same_issuer(left: _IssuerKey, right: _IssuerKey) -> bool:
    left_entity, left_listing = left
    right_entity, right_listing = right
    if left_entity and right_entity:
        return left_entity == right_entity
    return left_listing is not None and left_listing == right_listing


def _issuer_documents(sources: dict, issuer_source_ids: Iterable[str] | None) -> set[str]:
    # Legacy single-issuer archives did not record listing identity.
    if issuer_source_ids is None or not any(_source_manifest(s) is not None for s in sources.values()):
        return set(sources)
    issuer_sources = set(issuer_source_ids)
    issuer_keys = [_issuer_key(sources[sid]) for sid in issuer_sources if sid in sources]
    return issuer_sources | {
        sid for sid, source in sources.items()
        if any(_same_issuer(_issuer_key(source), key) for key in issuer_keys)
    }


def _financial_filing_dates(sources: dict, cutoff: date) -> tuple[list[date], bool]:
    dates = []
    unknown_publication = False
    for source in sources.values():
        if source.get("source_type") not in {"regulatory_filing", "exchange_filing"}:
            continue
        manifest = _source_manifest(source)
        if manifest is not None and manifest.get("document_kind") not in _FINANCIAL_KINDS:
            continue
        if source.get("published_date") is None:
            unknown_publication = True
            continue
        published = parse_iso_date(source["published_date"], "filing published_date")
        if published <= cutoff:
            dates.append(published)
    return dates, unknown_publication


def analyze_communication_scope(
    record: dict, sources: dict, as_of_date: str, *, issuer_source_ids: Iterable[str] | None = None,
) -> dict:
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
    financial_anchor = None
    unknown_financial_publication = False
    post_filing = record["category"] == "material_announcements_since_last_filing"
    issuer_documents = _issuer_documents(sources, issuer_source_ids)
    if post_filing:
        issuer_filings = {sid: source for sid, source in sources.items() if sid in issuer_documents}
        dates, unknown_financial_publication = _financial_filing_dates(issuer_filings, cutoff)
        financial_anchor = max(dates, default=None)
    item_refs = set()
    read_sources = set()
    unresolved = []
    category_mismatches = []
    unknown_read_publication = False
    read_dates = []
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
            if sources[sid].get("published_date") is None:
                # Availability proves an as-of upper bound, not publication time.
                unknown_read_publication = True
            else:
                published = parse_iso_date(sources[sid]["published_date"], "communication source date")
                require(start <= published <= end, "read communication source is outside checked interval")
                read_dates.append(published)
            read_sources.add(sid)
            expected_types = {
                "latest_annual_filing": {"regulatory_filing", "exchange_filing"},
                "latest_results_release": {"company_release"},
                "latest_earnings_call": {"earnings_transcript"},
                "latest_investor_presentation": {"investor_presentation"},
                "latest_strategy_communication": {"company_release", "investor_presentation", "earnings_transcript"},
            }.get(record["category"])
            manifest = _source_manifest(sources[sid])
            wrong_annual_kind = (record["category"] == "latest_annual_filing" and
                                 manifest is not None and manifest.get("document_kind") != "annual_report")
            if (expected_types is not None and sources[sid].get("source_type") not in expected_types) or wrong_annual_kind:
                category_mismatches.append(sid)
        if item.get("published_date") is not None:
            published = parse_iso_date(item["published_date"], "discovery item published_date")
            require(start <= published <= end, "discovery item is outside checked interval")
        if item["selected"] and not item["read"]:
            unresolved.append(ref)
        elif not item["selected"]:
            require(isinstance(item.get("skip_reason"), str) and bool(item["skip_reason"].strip()), "unselected communication requires materiality/skip reason")
    require(read_sources == set(record.get("source_ids", [])), "communication source_ids must match actual read originals")
    missed_start = financial_anchor is not None and start > financial_anchor
    missed_end = post_filing and end < cutoff
    boundary_only = (financial_anchor is not None and financial_anchor < end
                     and bool(read_sources) and not unknown_read_publication
                     and all(published <= financial_anchor for published in read_dates))
    missing_financial_anchor = post_filing and financial_anchor is None
    unbound_reads = read_sources - issuer_documents
    complete = (scope["coverage_complete"] and not unresolved and not boundary_only
                and not missed_start and not missed_end and not category_mismatches and not missing_financial_anchor
                and not unbound_reads
                and not unknown_financial_publication and not unknown_read_publication)
    reason = ("source_issuer_not_bound" if unbound_reads else
              "source_category_not_supported" if category_mismatches else
              "financial_filing_anchor_publication_unknown" if unknown_financial_publication else
              "source_publication_unknown" if unknown_read_publication else
              "financial_filing_anchor_unavailable" if missing_financial_anchor else
              "starts_after_financial_filing_anchor" if missed_start else
              "ends_before_as_of_date" if missed_end else
              "boundary_filing_does_not_cover_later_interval" if boundary_only else
              "scope_or_selected_content_incomplete" if not complete else None)
    return {"category": record["category"], "status": "verified_scope" if complete else "incomplete",
            "coverage_complete": complete, "start_date": scope["start_date"], "end_date": scope["end_date"],
            "discovered_item_refs": list(sorted(item_refs)), "read_source_ids": list(sorted(read_sources)),
            "unresolved_item_refs": unresolved, "reason": reason}
