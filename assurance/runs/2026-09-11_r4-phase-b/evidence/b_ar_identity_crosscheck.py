"""B.AR identity cross-check: catalog claims vs the INDEPENDENT registry snapshots.

`B-VR-BAR-04` (P2) established that my identity leg was same-source: the sidecar next to
the file and the catalog's `metadata.acquisition` are one artefact copied into the other,
so comparing them proves consistency, not identity.  The reviewer's conclusion was that
only the content hash and the sha embedded in `document_id` were independent.

There IS a genuinely independent identity source on this host, and this tool uses it:

    company-wiki/.source_catalog/security_master/{hk,cn,us}.json

those are versioned snapshots downloaded from the exchanges themselves (HKEX / CNINFO /
SEC - see `market`, `retrieved_at`, `sources` inside each file), i.e. a DIFFERENT
provenance from both the filing sidecar and the catalog.  For every sampled document that
declares a market + security_id (or carries a ticker entity) this tool looks the security
up in the registry and compares the registry's canonical name / aliases with the name the
catalog asserts, using the PRODUCT's own normaliser (imported, with its file identity
recorded, so a stale copy in site-packages cannot be mistaken for the repository's).

Read-only: it opens JSON files and the already-captured CLI stdout.  It never opens the
production catalog database, never runs a CLI, never touches the network, and writes only
`--out`.

    python b_ar_identity_crosscheck.py [--per-root 3] [--max-docs 20] [--out PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "a05-readonly-manifest-run.json"
SAMPLE_EVIDENCE = HERE / "b-ar-identity-hash.json"
REGISTRY_DIR = (HERE.parents[4] / "company-wiki" / ".source_catalog" / "security_master")
WIKI_SRC = HERE.parents[4] / "company-wiki" / "src"
MARKETS = ("hk", "cn", "us")


def _sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _load_rows() -> list[dict]:
    rows: list[dict] = []
    for name in ("a05-readonly-manifest-run-A05-2-stdout.txt",
                 "a05-readonly-manifest-run-A05-2b-stdout.txt"):
        path = HERE / name
        if path.is_file():
            rows.extend(json.loads(path.read_text(encoding="utf-8")))
    seen: dict[str, dict] = {}
    for row in rows:
        document_id = str(row.get("document_id") or "")
        if document_id and document_id not in seen:
            seen[document_id] = row
    return list(seen.values())


def _sample(rows: list[dict], per_root: int, max_docs: int) -> list[tuple[str, dict]]:
    by_root: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        locations = row.get("locations") or []
        root_id = str((locations[0].get("root_id") if locations else "") or "<no location>")
        by_root[root_id].append(row)
    sampled: list[tuple[str, dict]] = []
    for root_id in sorted(by_root):
        for row in sorted(by_root[root_id], key=lambda item: str(item.get("document_id"))):
            if len(sampled) >= max_docs:
                break
            if sum(1 for item in sampled if item[0] == root_id) >= per_root:
                break
            sampled.append((root_id, row))
    return sampled


def _registry_records(normalize) -> tuple[dict[str, dict], dict[str, dict], dict[str, list]]:
    """(by market+security_id, by market+ticker, by normalised NAME) from the snapshots.

    The NAME index is what makes the check work for rows that assert no numeric id: some
    rows carry a company NAME in the security_id field (measured: `cn / 周大生`), and the
    sidecar-only rows assert only a title.  A name hit across several markets is recorded
    as ambiguous rather than resolved by preference order.
    """
    by_id: dict[str, dict] = {}
    by_ticker: dict[str, dict] = {}
    by_name: dict[str, list] = defaultdict(list)
    for market in MARKETS:
        path = REGISTRY_DIR / f"{market}.json"
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for record in payload.get("records") or []:
            security_id = str(record.get("security_id") or "").strip()
            ticker = str(record.get("ticker") or "").strip()
            if security_id:
                by_id[f"{market}:{security_id.lstrip('0').casefold()}"] = record
            if ticker:
                by_ticker[f"{market}:{ticker.lstrip('0').casefold()}"] = record
            for name in (record.get("canonical_name"), *(record.get("aliases") or [])):
                text = str(name or "").strip()
                if text:
                    by_name[normalize(text)].append((market, record))
    return by_id, by_ticker, by_name


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-root", type=int, default=3)
    parser.add_argument("--max-docs", type=int, default=20)
    parser.add_argument("--out", type=Path, default=HERE / "b-ar-identity-crosscheck.json")
    args = parser.parse_args(argv)

    run = json.loads(RUN.read_text(encoding="utf-8"))
    rows = _load_rows()
    sampled = _sample(rows, args.per_root, args.max_docs)

    # The product's own normaliser, with its identity recorded (the reviewer's lesson:
    # prove WHICH copy of a module was imported, not just that one was).
    sys.path.insert(0, str(WIKI_SRC))
    from company_wiki.source_catalog import security_identity  # noqa: PLC0415

    normalize = security_identity._normalize_text
    module_path = Path(security_identity.__file__).resolve()
    normalizer_identity = {
        "module_file": str(module_path),
        "module_sha256_16": hashlib.sha256(module_path.read_bytes()).hexdigest()[:16],
        "in_repository": str(WIKI_SRC) in str(module_path),
    }

    by_id, by_ticker, by_name = _registry_records(normalize)
    registry_identity = {}
    for market in MARKETS:
        path = REGISTRY_DIR / f"{market}.json"
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        registry_identity[market] = {
            "file": path.name, "record_count": payload.get("record_count"),
            "retrieved_at": payload.get("retrieved_at"),
            "sources_len": len(payload.get("sources") or []),
            "sha256_16": hashlib.sha256(path.read_bytes()).hexdigest()[:16],
        }

    checks: list[dict] = []
    totals = Counter()
    for root_id, row in sampled:
        acquisition = (row.get("metadata") or {}).get("acquisition") or {}
        candidate = acquisition.get("candidate") or {}
        market = str(acquisition.get("market") or candidate.get("market") or "").strip().lower()
        security_id = str(acquisition.get("security_id") or candidate.get("security_id") or "").strip()
        entities = row.get("entities") or []
        ticker_entity = next((str(item.get("name") or "") for item in entities
                              if str(item.get("entity_id") or "").startswith("ticker:")), "")
        if not security_id and ticker_entity:
            security_id = ticker_entity
        entry: dict = {
            "root_id": root_id,
            "document_id": str(row.get("document_id")),
            "catalog_market": market or None,
            "catalog_security_id": security_id or None,
            "catalog_security_id_len": len(security_id),
        }
        # Identity has TWO separable legs and the first version of this tool conflated
        # them: the IDENTIFIER (does the registry know this ticker/security_id at all?)
        # and the NAME (does the registry's canonical name match a name the catalog
        # actually asserts?).  A document that asserts only a ticker cannot disagree on
        # a name - it simply has no name to compare (measured: 3 dayu rows were wrongly
        # reported as "disagree" that way).
        numeric_id = bool(security_id) and security_id.isdigit()
        if security_id and not numeric_id:
            entry["security_id_kind"] = "non_numeric (the catalog stores a NAME here)"
        company_name = str(acquisition.get("company_name") or candidate.get("entity") or "").strip()
        # What identity does the CATALOG actually assert on this row?  Three shapes exist
        # and all three are usable for a cross-source lookup:
        #   1. a company name in the metadata (company_raw sidecars),
        #   2. a company name stored in the `security_id` field (measured: cn / 周大生),
        #   3. a resolved ENTITY name (the `.pdf.source` rows carry 紫金矿业 / 星环科技
        #      entities even though they have no location and no acquisition block).
        # An `unresolved:*` entity asserts nothing, so it is not used.
        entity_names = [str(item.get("name") or "").strip() for item in (row.get("entities") or [])
                        if not str(item.get("entity_id") or "").startswith("unresolved:")]
        asserted: list[tuple[str, str]] = []
        if company_name:
            asserted.append(("metadata.company_name", company_name))
        if security_id and not numeric_id:
            asserted.append(("security_id_holds_a_name", security_id))
        for name in entity_names:
            if not name or name in {value for _, value in asserted}:
                continue
            if name.isdigit():
                # A ticker entity ("ticker:688031") names the security by IDENTIFIER, not
                # by name: comparing it against registry NAMES produced three false
                # "disagreements" in the first run of this tool.  It is covered by the
                # identifier leg instead.
                entry["entity_name_is_an_identifier"] = _sha16(name)
                continue
            asserted.append(("entity_name", name))
        entry["catalog_asserted_names"] = [
            {"source": source, "sha16": _sha16(value)} for source, value in asserted]
        entry["catalog_company_name_sha16"] = _sha16(company_name) if company_name else None
        entry["catalog_asserts_a_company_name"] = bool(asserted)

        record = None
        matched_via = None
        name_hits: list = []
        name_source = None
        if numeric_id:
            key = security_id.lstrip("0").casefold()
            markets = [market] if market in MARKETS else list(MARKETS)
            for candidate_market in markets:
                if f"{candidate_market}:{key}" in by_id:
                    record = by_id[f"{candidate_market}:{key}"]
                    matched_via = f"{candidate_market}_security_id"
                    break
            if record is None:
                for candidate_market in markets:
                    if f"{candidate_market}:{key}" in by_ticker:
                        record = by_ticker[f"{candidate_market}:{key}"]
                        matched_via = f"{candidate_market}_ticker"
                        break
        if record is None:
            # No numeric identifier (or it was not in the registry): try each NAME the
            # catalog asserts, in the order recorded above, against the registries.  This
            # is still cross-source (the registry is the independent side); a name that
            # hits several DISTINCT securities is recorded as ambiguous, not resolved by
            # preference order.
            for source, value in asserted:
                hits = by_name.get(normalize(value), [])
                if not hits:
                    continue
                distinct = {(str(item[1].get("market") or ""), str(item[1].get("security_id") or ""))
                            for item in hits}
                if len(distinct) > 1:
                    entry["status"] = "ambiguous_name"
                    entry["ambiguous_name_source"] = source
                    entry["name_lookup_hits"] = [
                        {"market": str(item[1].get("market") or ""),
                         "security_id": str(item[1].get("security_id") or "")}
                        for item in hits[:6]]
                    entry["reason"] = ("the asserted company name resolves to several "
                                       "distinct registry securities")
                    totals["ambiguous_name"] += 1
                    checks.append(entry)
                    break
                hit_market, record = hits[0]
                matched_via = f"{hit_market}_name"
                name_hits = hits
                name_source = source
                entry["name_lookup_source"] = source
                entry["name_lookup_hits"] = [
                    {"market": str(item[1].get("market") or ""),
                     "security_id": str(item[1].get("security_id") or "")}
                    for item in hits[:6]]
                break
            if entry.get("status") == "ambiguous_name":
                continue
        if record is None:
            entry["status"] = ("not_in_registry" if numeric_id
                               else "no_comparable_identifier")
            entry["reason"] = (
                "the row's numeric identifier is absent from the hk/cn/us snapshots"
                if numeric_id else
                ("the row carries no numeric identifier and no asserted name that the "
                 "registries know" if asserted else
                 "the row asserts no identity at all (no identifier, no name, no resolved "
                 "entity) - nothing to look up"))
            totals[entry["status"]] += 1
            checks.append(entry)
            continue

        canonical = str(record.get("canonical_name") or "")
        aliases = [str(item) for item in (record.get("aliases") or [])]
        registry_names = [canonical, *aliases]
        entry.update({
            "status": "in_registry",
            "matched_via": matched_via,
            "registry_market": str(record.get("market") or ""),
            "registry_security_id": str(record.get("security_id") or ""),
            "registry_canonical_sha16": _sha16(canonical) if canonical else None,
            "registry_alias_count": len(aliases),
            "registry_active": record.get("active"),
        })
        if numeric_id:
            # the identifier leg: the registry's own id/ticker equals the one the row uses
            entry["identifier_agree"] = (
                str(record.get("security_id") or "").lstrip("0").casefold()
                == security_id.lstrip("0").casefold()
                or str(record.get("ticker") or "").lstrip("0").casefold()
                == security_id.lstrip("0").casefold())
            totals["identifier_agree" if entry["identifier_agree"]
                   else "identifier_disagree"] += 1
        else:
            # the row had no numeric identifier: the match came from the NAME, so there is
            # nothing to agree or disagree about on the identifier leg.
            entry["identifier_agree"] = None
            entry["identifier_note"] = ("no numeric identifier on the row; matched by name")
        if asserted:
            # the name leg: the registry lists a name the CATALOG asserts (any of the three
            # shapes), under the product's own normalisation
            asserted_values = {normalize(value) for _, value in asserted}
            matches = [name for name in registry_names if name and normalize(name) in asserted_values]
            entry["matched_registry_names"] = [_sha16(name) for name in matches]
            entry["name_agree"] = bool(matches)
            totals["name_agree" if entry["name_agree"] else "name_disagree"] += 1
        else:
            entry["name_agree"] = None
            entry["name_comparison"] = ("not comparable: the row asserts no company name "
                                        "and no resolved entity name")
            totals["name_not_asserted"] += 1
        entry["index_rule"] = ("leading zeros stripped, casefolded; market taken from the "
                              "catalog when it declares one, otherwise the key must be "
                              "unambiguous across hk/cn/us")
        checks.append(entry)

    # The two tools must agree on WHICH documents were sampled, or the cross-check is
    # answering a different question than the record describes.
    recorded = json.loads(SAMPLE_EVIDENCE.read_text(encoding="utf-8"))["checks"]
    recorded_ids = sorted(str(item["document_id"]) for item in recorded)
    sampled_ids = sorted(str(row["document_id"]) for _, row in sampled)
    sample_agrees = recorded_ids == sampled_ids

    payload = {
        "tool": "b_ar_identity_crosscheck.py",
        "note": ("Cross-source identity check: the exchange registry snapshots (independent "
                 "provenance) vs the names the catalog/sidecar assert. Read-only; the "
                 "production catalog database was never opened."),
        "normalizer": normalizer_identity,
        "registry_snapshots": registry_identity,
        "source_run": {"manifest_id": run.get("manifest_id"),
                       "ran_at_utc": run.get("ran_at_utc")},
        "sample": {"per_root": args.per_root, "max_docs": args.max_docs,
                   "documents_checked": len(checks),
                   "sample_matches_identity_hash_evidence": sample_agrees},
        "totals": dict(sorted(totals.items())),
        "checks": checks,
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({"sample": payload["sample"], "totals": payload["totals"],
                      "registry": {key: {"records": value["record_count"],
                                         "retrieved_at": value["retrieved_at"]}
                                   for key, value in registry_identity.items()},
                      "normalizer_in_repository": normalizer_identity["in_repository"]},
                     ensure_ascii=True, indent=2))
    print(f"wrote {args.out.name}")
    return 0 if sample_agrees else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
