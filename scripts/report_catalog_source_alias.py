"""Trusted, source-bound W09 label admission via StockWiki's public proof CLI.

The configured owner CLI validates its complete G2b package. This consumer
checks its exact cross-references to the frozen primary SourceRef and the
fresh identity lookup; it never infers a company from a name or a ticker.
Integrity hashes are not signatures. Authority comes from the fixed, trusted
owner deployment, never from caller-supplied proof JSON.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urlsplit

from report_catalog_identity_resolver import (
    BridgeConfig, IdentityBridgeError, _assert_pathless, resolve_identity,
)

_FIELDS = {"schema_version", "document_id", "source_id", "content_sha256", "byte_size", "mime_type"}
_HEX = re.compile(r"[0-9a-f]{64}")


def _check(condition: Any, code: str = "source_alias_unverified") -> None:
    if not condition:
        raise IdentityBridgeError(code, "source-bound owner proof refused")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _object(value: Any) -> dict[str, Any]:
    _check(isinstance(value, dict))
    return value


def _text(value: Any) -> str:
    _check(isinstance(value, str) and bool(value) and value == value.strip())
    return value


def _source_ref(value: Any) -> dict[str, Any]:
    value = _object(value)
    _check(set(value) == _FIELDS)
    digest = value.get("content_sha256")
    _check(isinstance(digest, str) and _HEX.fullmatch(digest))
    _check(value.get("schema_version") == "2.0"
           and value.get("document_id") == "urn:company-wiki:document:sha256:" + digest
           and value.get("source_id") == "urn:company-wiki:source:sha256:" + digest
           and type(value.get("byte_size")) is int and value["byte_size"] > 0
           and value.get("mime_type") == "application/pdf")
    return value


def w09_primary_source_refs(results: list[dict[str, Any]], company_query: str) -> list[dict[str, Any]]:
    """Extract only each validated W09 report's unique rank-one annual filing."""
    refs = []
    _check(len(results) == 2)
    for result in results:
        sources = result.get("sources")
        _check(isinstance(sources, list))
        assert isinstance(sources, list)
        primary = [source for source in sources if isinstance(source, dict)
                   and type(source.get("source_rank")) is int and source["source_rank"] == 1
                   and isinstance(source.get("company_wiki_trace"), dict)
                   and isinstance(source["company_wiki_trace"].get("source_manifest"), dict)
                   and source["company_wiki_trace"]["source_manifest"].get("document_kind") == "annual_report"]
        _check(len(primary) == 1)
        source = primary[0]
        trace = _object(source.get("company_wiki_trace"))
        ref = _source_ref(trace.get("source_ref"))
        manifest = _object(trace.get("source_manifest"))
        receipt = _object(trace.get("read_receipt"))
        _check(source.get("source_type") == "regulatory_filing"
               and source.get("source_id") == ref["source_id"]
               and manifest.get("display_name") == company_query
               and manifest.get("document_kind") == "annual_report"
               and manifest.get("fiscal_period") == "FY"
               and manifest.get("fiscal_year") == result.get("base_year")
               and receipt.get("status") == "ok")
        for key in _FIELDS - {"schema_version"}:
            _check(manifest.get(key) == ref[key])
        for key in {"document_id", "source_id", "content_sha256", "byte_size"}:
            _check(receipt.get(key) == ref[key])
        refs.append(dict(ref))
    _check(refs[0] == refs[1])
    return refs


def _json(raw: bytes) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            _check(key not in result, "source_alias_protocol_invalid")
            result[key] = value
        return result

    def constant(_: str) -> None:
        raise IdentityBridgeError("source_alias_protocol_invalid", "non-finite JSON refused")

    try:
        return _object(json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise IdentityBridgeError("source_alias_protocol_invalid", "proof JSON refused") from exc


def _assert_proof_pathless(value: Any, depth: int = 0) -> None:
    _check(depth <= 24, "source_alias_protocol_invalid")
    if isinstance(value, dict):
        for key, child in value.items():
            _assert_proof_pathless(key, depth + 1)
            _assert_proof_pathless(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            _assert_proof_pathless(child, depth + 1)
    elif isinstance(value, str) and value.startswith("https://"):
        try:
            url = urlsplit(value)
            # urlsplit defers port validation until this property is read.
            # Looking only at hostname would accept :bad, :99999 or :C:.
            port = url.port
            _check(url.scheme == "https" and bool(url.hostname)
                   and not url.username and not url.password
                   and (port is None or 1 <= port <= 65535)
                   and not url.netloc.endswith(":")
                   and not any(ord(char) <= 32 or ord(char) == 127 for char in value),
                   "source_alias_protocol_invalid")
            # HTTPS is a public evidence locator, not the `s:/` drive-shaped
            # substring the legacy identity-only scanner would detect.
            for part in (url.netloc, url.path, url.query, url.fragment):
                _assert_pathless(part)
        except ValueError as exc:
            raise IdentityBridgeError("source_alias_protocol_invalid", "evidence URL refused") from exc
    else:
        _check(not isinstance(value, str) or not value.startswith("/"), "bridge_path_leak")
        _assert_pathless(value)


def _read_proof(config: BridgeConfig, query: dict[str, Any]) -> dict[str, Any]:
    # Requiring the explicit workspace avoids a default-root alias authority.
    _check(config.sw_root is not None, "source_alias_config_invalid")
    cli = config.owner_root / "dashboard_issuer_proof_cli.py"
    _check(config.cli == config.owner_root / "dashboard_identity_bridge_cli.py"
           and cli.is_file() and cli.resolve() == cli, "source_alias_config_invalid")
    argv = [str(config.python), "-X", "utf8", "-B", str(cli), "read", "--root", str(config.sw_root)]
    # Files bound memory even if a faulty trusted child emits too much. Read
    # only limit+1 after it exits; never return raw stderr or physical paths.
    try:
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            completed = subprocess.run(argv, input=_canonical(query), stdout=stdout, stderr=stderr,
                                       timeout=config.timeout_seconds, cwd=config.owner_root)
            _check(completed.returncode == 0, "source_alias_owner_refused")
            stdout.seek(0)
            raw = stdout.read(config.max_output_bytes + 1)
    except subprocess.TimeoutExpired as exc:
        raise IdentityBridgeError("source_alias_timeout", "owner proof deadline exceeded") from exc
    except OSError as exc:
        raise IdentityBridgeError("source_alias_unavailable", "owner proof unavailable") from exc
    _check(len(raw) <= config.max_output_bytes, "source_alias_output_too_large")
    response = _json(raw)
    _assert_proof_pathless(response)
    _check(response.get("schema_version") == "stockwiki.dashboard_issuer_proof/1"
           and response.get("authority") == "stockwiki" and response.get("state") == "available"
           and response.get("library_revision") == "not_provided_no_global_revision"
           and response.get("reason_codes") == [] and response.get("query") == query)
    _check(response.get("receipt_sha256") == _sha({key: value for key, value in response.items()
                                                if key != "receipt_sha256"}),
           "source_alias_receipt_invalid")
    return response


def _validate_proof(response: dict[str, Any], *, entity_id: str, listing_id: str,
                    company_query: str, ref: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]:
    package = _object(response.get("owner_package"))
    _check(set(package) == {"object_type", "schema_version", "payload", "trusted_context"}
           and package.get("object_type") == "entity" and package.get("schema_version") == "2.2.0")
    payload = _object(package.get("payload"))
    context = _object(package.get("trusted_context"))
    _check(set(context) == {"source_bindings", "market_registry", "identity_receipts"})
    _check(payload.get("identity_schema_version") == "2.1.0")
    revision = payload.get("identity_revision")
    _check(type(revision) is int and revision > 0 and response.get("identity_revision") == revision
           and payload.get("entity_id") == entity_id and payload.get("identity_state") == "verified"
           and payload.get("canonical_name") == identity.get("display_name")
           and response.get("selected_listing_id") == listing_id)
    # The identity bridge revisions the stored 2.0/2.1 row; G2b exports a
    # 2.1 projection. They are distinct schema layers, not interchangeable.
    _check(bool(re.fullmatch(
        rf"identity_schema_version=2\.[01]\.0;identity_revision={revision};entity={re.escape(entity_id)}",
        identity.get("source_revision", ""))))
    listings = payload.get("listings")
    securities = payload.get("securities")
    _check(isinstance(listings, list) and isinstance(securities, list))
    assert isinstance(listings, list) and isinstance(securities, list)
    selected = [item for item in listings if isinstance(item, dict) and item.get("listing_id") == listing_id]
    _check(len(selected) == 1)
    listing = selected[0]
    security_id = _text(listing.get("security_id"))
    security = [item for item in securities if isinstance(item, dict) and item.get("security_id") == security_id]
    _check(len(security) == 1 and security[0].get("entity_id") == entity_id
           and security[0].get("security_type") == "ordinary"
           and listing.get("entity_id") == entity_id and listing.get("listing_status") == "active")
    binding_ref = _text(listing.get("source_binding_ref"))
    bindings = _object(context.get("source_bindings"))
    binding = _object(bindings.get(binding_ref))
    _check(binding.get("binding_ref") == binding_ref and binding.get("entity_id") == entity_id
           and binding.get("security_id") == security_id and binding.get("listing_id") == listing_id
           and binding.get("status") == "active"
           and binding.get("source_namespace") == "cwp_source_export_v2"
           and binding.get("source_record_id") == ref["source_id"]
           and binding.get("source_canonical_name") == company_query)
    for key in ("market", "exchange_raw", "exchange_mic", "ticker_raw", "ticker", "valid_from", "valid_to"):
        _check(key in listing and key in binding and binding[key] == listing[key])
    registry = _object(context.get("market_registry"))
    market = _text(listing.get("market"))
    mics = registry.get(market)
    _check(isinstance(mics, list))
    assert isinstance(mics, list)
    _check(listing.get("exchange_mic") in mics)
    receipt_id = _text(payload.get("verified_issuer_receipt_id"))
    receipts = _object(context.get("identity_receipts"))
    _check(set(receipts) == {receipt_id})
    receipt = _object(receipts.get(receipt_id))
    _check(receipt.get("receipt_id") == receipt_id and receipt.get("kind") == "verified_issuer"
           and receipt.get("effective_status") == "active" and receipt.get("same_legal_issuer") is True
           and receipt.get("entity_id") == entity_id and receipt.get("identity_revision") == revision
           and receipt.get("canonical_name") == payload["canonical_name"]
           and listing_id in receipt.get("listing_ids", []) and security_id in receipt.get("security_ids", []))
    attrs = _object(_object(receipt.get("listing_attributes")).get(listing_id))
    for key in ("security_id", "currency", "market", "exchange_raw", "exchange_mic", "ticker_raw", "ticker",
                "source_binding_ref", "listing_status", "valid_from", "valid_to"):
        _check(key in attrs and key in listing and attrs[key] == listing[key])
    for key in ("source_namespace", "source_record_id", "source_canonical_name"):
        _check(attrs.get(key) == binding[key])
    security_attrs = _object(_object(receipt.get("security_attributes")).get(security_id))
    for key in ("security_type", "share_class", "ordinary_security_ref", "adr_ratio"):
        _check(key in security_attrs and key in security[0] and security_attrs[key] == security[0][key])
    return {"schema_version": "rf-source-bound-identity/1", "authority": "stockwiki",
            "entity_id": entity_id, "listing_id": listing_id, "security_id": security_id,
            "canonical_name": payload["canonical_name"], "frozen_company_label": company_query,
            "identity_revision": revision, "identity_source_revision": identity["source_revision"],
            "identity_lookup_receipt_sha256": identity["lookup_receipt_sha256"],
            "verified_issuer_receipt_id": receipt_id, "source_binding": binding,
            "primary_source_ref": ref, "issuer_proof_receipt_sha256": response["receipt_sha256"],
            "issuer_proof_query": response["query"]}


def make_single_source_alias_resolver(
    config: BridgeConfig, *, listing_id: str | None = None, operation_as_of: str | None = None
) -> Callable[..., dict[str, Any]]:
    """Bind one verified original to the current owner-issued source binding."""
    as_of = (datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
             if operation_as_of is None else operation_as_of)
    _check(isinstance(as_of, str) and bool(re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", as_of)), "source_alias_protocol_invalid")

    def resolver(
        entity_id: str,
        company_query: str,
        source_ref: dict[str, Any],
        identity_evidence: dict[str, Any],
    ) -> dict[str, Any]:
        _check(isinstance(listing_id, str), "source_alias_listing_required")
        ref = _source_ref(source_ref)
        _check(
            identity_evidence.get("entity_id") == entity_id
            and identity_evidence.get("authority") == "stockwiki"
            and identity_evidence.get("resolution_status") == "resolved"
        )
        fresh = resolve_identity(entity_id, config=config, listing_id=listing_id)
        _check(fresh == identity_evidence, "source_alias_identity_changed")
        query = {"entity_id": entity_id, "listing_id": listing_id, "as_of": as_of}
        response = _read_proof(config, query)
        assert listing_id is not None
        try:
            result = _validate_proof(
                response,
                entity_id=entity_id,
                listing_id=listing_id,
                company_query=company_query,
                ref=ref,
                identity=fresh,
            )
        except (TypeError, KeyError, ValueError) as exc:
            raise IdentityBridgeError(
                "source_alias_protocol_invalid", "owner package shape refused"
            ) from exc
        _check(
            resolve_identity(entity_id, config=config, listing_id=listing_id) == fresh,
            "source_alias_identity_changed",
        )
        return result

    return resolver


def make_source_alias_resolver(
    config: BridgeConfig, *, listing_id: str | None = None
) -> Callable[..., dict[str, Any]]:
    """W09 wrapper still requires the two separately validated report anchors."""
    single = make_single_source_alias_resolver(config, listing_id=listing_id)

    def resolver(
        entity_id: str,
        company_query: str,
        source_refs: list[dict[str, Any]],
        identity_evidence: dict[str, Any],
    ) -> dict[str, Any]:
        _check(
            isinstance(source_refs, list)
            and len(source_refs) == 2
            and _source_ref(source_refs[0]) == _source_ref(source_refs[1])
        )
        return single(entity_id, company_query, source_refs[0], identity_evidence)

    return resolver
