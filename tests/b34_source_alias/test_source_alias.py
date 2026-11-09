"""RF admission and transport through isolated public StockWiki protocol fixtures.

W09 frozen tracked reports are read-only; all test writes use temporary roots.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from report_catalog import CatalogError, ReportCatalog, import_w09  # noqa: E402
from owner_file_lock import OwnerFileLock  # noqa: E402
from report_catalog_identity_resolver import (  # noqa: E402
    BridgeConfig,
    IdentityBridgeError,
    resolve_identity,
)
import report_catalog_source_alias as alias  # noqa: E402

ENT = "ENT_1b2a4d3e-0000-4a1b-8c2d-000000000001"
SEC = "SEC_2c3b5e4f-0000-4b2c-9d3e-000000000001"
LABEL = "药明康德"
CANONICAL = "无锡药明康德新药开发股份有限公司"
# Read this exact, already frozen W09 reference; no new digest registry or
# host-specific golden is introduced by the management adapter tests.
REF = json.loads(
    (ROOT / "delivery/w09/forecast/main-forecast.json").read_text(encoding="utf-8")
)["sources"][0]["company_wiki_trace"]["source_ref"]

FIXTURE_CLI = r'''
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[sys.argv.index("--root") + 1])
state = json.loads((root / "controlled-owner.json").read_bytes())
if sys.argv[1] == "resolve":
    response = state["identity"]
    assert sys.argv[sys.argv.index("--entity-id") + 1] == response["entity_id"]
    if "--listing-id" in sys.argv:
        assert sys.argv[sys.argv.index("--listing-id") + 1] == response["entity"]["selected_listing_id"]
    if state["revoked"]:
        response["resolution_status"] = "identity_not_verified"
    receipt = "lookup_receipt_sha256"
else:
    assert sys.argv[1] == "read"
    response = state["proof"]
    query = json.load(sys.stdin)
    assert query["entity_id"] == state["identity"]["entity_id"]
    assert query["listing_id"] == response["selected_listing_id"]
    response["query"] = query
    if state["revoked"]:
        response["state"] = "unavailable"
    receipt = "receipt_sha256"
data = json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
response[receipt] = hashlib.sha256(data.encode()).hexdigest()
sys.stdout.buffer.write(json.dumps(response, ensure_ascii=False).encode())
'''


def controlled_code(root: Path) -> Path:
    code = root / "controlled-stockwiki-code"
    code.mkdir()
    for name in ("dashboard_identity_bridge_cli.py", "dashboard_issuer_proof_cli.py"):
        (code / name).write_text(FIXTURE_CLI, encoding="utf-8")
    return code


def owner_action(code: Path, payload: dict) -> dict:
    # This fixture owns its temporary protocol state. No external owner code,
    # storage or private API is needed by the RF test suite.
    assert (code / "dashboard_identity_bridge_cli.py").is_file()
    workspace = Path(payload["workspace"])
    state_path = workspace / "controlled-owner.json"
    if payload["action"] == "revoke":
        state = json.loads(state_path.read_bytes())
        assert payload["receipt_id"] in state["proof"]["owner_package"]["trusted_context"]["identity_receipts"]
        state["revoked"] = True
        state_path.write_text(json.dumps(state), encoding="utf-8")
        return {}

    workspace.mkdir()
    entity, security, name = payload["entity"], payload["security"], payload["canonical"]
    listing_id = "LST_00000000-0000-4000-8000-000000000001"
    receipt_id = "controlled-verified-issuer"
    binding_ref = "controlled-binding"
    listing = {"listing_id": listing_id, "security_id": security, "entity_id": entity,
               "listing_status": "active", "market": "CN", "currency": "CNY",
               "exchange_raw": "SSE", "exchange_mic": "XSHG",
               "ticker_raw": "603259", "ticker": "603259",
               "valid_from": "2020-01-01", "valid_to": None, "source_binding_ref": binding_ref}
    instrument = {"security_id": security, "entity_id": entity, "security_type": "ordinary",
                  "share_class": "A", "ordinary_security_ref": None, "adr_ratio": None}
    binding = {**listing, "binding_ref": binding_ref, "status": "active",
               "source_namespace": "cwp_source_export_v2", "source_record_id": payload["source_id"],
               "source_canonical_name": payload["alias"]}
    issuer = {"receipt_id": receipt_id, "kind": "verified_issuer", "effective_status": "active",
              "same_legal_issuer": True, "entity_id": entity, "identity_revision": 1,
              "canonical_name": name, "listing_ids": [listing_id], "security_ids": [security],
              "listing_attributes": {listing_id: binding}, "security_attributes": {security: instrument}}
    identity = {"schema_version": "stockwiki.dashboard_identity/1", "command": "resolve",
                "authority": "stockwiki", "entity_id": entity, "resolution_status": "resolved",
                "display_name": name, "source_revision": f"identity_schema_version=2.1.0;identity_revision=1;entity={entity}",
                "entity": {"entity_id": entity, "selected_listing_id": listing_id}}
    proof = {"schema_version": "stockwiki.dashboard_issuer_proof/1", "authority": "stockwiki",
             "state": "available", "library_revision": "not_provided_no_global_revision", "reason_codes": [],
             "identity_revision": 1, "selected_listing_id": listing_id, "owner_package": {
                 "object_type": "entity", "schema_version": "2.2.0",
                 "payload": {"identity_schema_version": "2.1.0", "identity_revision": 1,
                             "entity_id": entity, "identity_state": "verified", "canonical_name": name,
                             "listings": [listing], "securities": [instrument],
                             "verified_issuer_receipt_id": receipt_id},
                 "trusted_context": {"source_bindings": {binding_ref: binding},
                                     "market_registry": {"CN": ["XSHG"]},
                                     "identity_receipts": {receipt_id: issuer}},
             }}
    state_path.write_text(json.dumps({"identity": identity, "proof": proof, "revoked": False}), encoding="utf-8")
    return identity


@pytest.fixture(scope="module")
def code(tmp_path_factory):
    return controlled_code(tmp_path_factory.mktemp("rf-public-proof"))


def _native(tmp_path, code):
    workspace = tmp_path / "isolated-owner"
    response = owner_action(
        code,
        {
            "action": "create",
            "workspace": str(workspace),
            "entity": ENT,
            "security": SEC,
            "canonical": CANONICAL,
            "alias": LABEL,
            "source_id": REF["source_id"],
        },
    )
    listing = response["entity"]["selected_listing_id"]
    config = BridgeConfig(
        python=Path(sys.executable),
        cli=code / "dashboard_identity_bridge_cli.py",
        owner_root=code,
        sw_root=workspace,
        timeout_seconds=10,
        max_output_bytes=262144,
    )
    identity = resolve_identity(ENT, config=config, listing_id=listing)
    return config, listing, identity


@pytest.fixture
def native(tmp_path, code):
    return _native(tmp_path, code)


def frozen_results():
    return [
        json.loads(
            (ROOT / "delivery/w09/forecast" / (v + "-forecast.json")).read_text(
                encoding="utf-8"
            )
        )
        for v in ("main", "stress")
    ]


def stores(config):
    return {
        p.relative_to(config.sw_root).as_posix(): p.read_bytes()
        for p in config.sw_root.rglob("*")
        if p.is_file()
    }


def test_actual_public_owner_source_bound_admission(native, tmp_path):
    config, listing, identity = native
    original = [
        (ROOT / "delivery/w09/forecast" / (v + "-forecast.json")).read_bytes()
        for v in ("main", "stress")
    ]
    owner_before = stores(config)
    resolver = alias.make_source_alias_resolver(config, listing_id=listing)
    assert alias.w09_primary_source_refs(frozen_results(), LABEL) == [REF, REF]
    kwargs = dict(
        entity_id=ENT,
        listing_id=listing,
        analysis_subject_id=None,
        identity_evidence=identity,
        identity_resolver=lambda _: resolve_identity(
            ENT, config=config, listing_id=listing
        ),
    )
    catalog = ReportCatalog(
        root=ROOT, catalog_file=tmp_path / "controlled-catalog.jsonl"
    )
    if os.environ.get("B34_ALIAS_BASE_SOURCE"):
        spec = importlib.util.spec_from_file_location(
            "b34_base_catalog", os.environ["B34_ALIAS_BASE_SOURCE"]
        )
        base = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(base)
        receipt = base.import_w09(catalog, **kwargs)
    else:
        receipt = import_w09(catalog, **kwargs, source_alias_resolver=resolver)
    assert len(receipt["registered"]["reports"]) == 2
    run = catalog._index()[0]["w09-rf-research-20261023"]
    proof = run["source_bound_identity_evidence"]
    assert proof["canonical_name"] == CANONICAL
    assert proof["frozen_company_label"] == LABEL
    assert run["company"]["display_name"] == LABEL
    assert proof["primary_source_ref"] == REF
    assert len(catalog.list_reports(ENT)["items"]) == 2
    assert stores(config) == owner_before
    assert original == [
        (ROOT / "delivery/w09/forecast" / (v + "-forecast.json")).read_bytes()
        for v in ("main", "stress")
    ]


def test_mismatch_without_trusted_callback_is_rejected(native, tmp_path):
    config, listing, identity = native
    catalog = ReportCatalog(root=ROOT, catalog_file=tmp_path / "not-created.jsonl")
    with pytest.raises(CatalogError) as refused:
        import_w09(
            catalog,
            entity_id=ENT,
            listing_id=listing,
            analysis_subject_id=None,
            identity_evidence=identity,
            identity_resolver=lambda _: identity,
        )
    assert refused.value.code == "identity_unverified"
    assert not catalog.file.exists()
    assert resolve_identity(ENT, config=config, listing_id=listing) == identity


@pytest.fixture(scope="module")
def proof_case(tmp_path_factory, code):
    config, listing, identity = _native(
        tmp_path_factory.mktemp("proof-only-owner"), code
    )
    query = {"entity_id": ENT, "listing_id": listing, "as_of": "2026-11-01T00:00:00Z"}
    response = alias._read_proof(config, query)
    return config, listing, identity, response


@pytest.mark.parametrize(
    "change",
    [
        "entity",
        "revision",
        "canonical",
        "selected_listing",
        "security_entity",
        "security_type",
        "inactive_listing",
        "binding_entity",
        "binding_listing",
        "binding_security",
        "binding_source",
        "binding_alias",
        "binding_namespace",
        "binding_status",
        "receipt_revoked",
        "receipt_revision",
        "receipt_entity",
        "receipt_name",
        "receipt_same_issuer",
        "receipt_listing",
        "receipt_attribute",
        "receipt_source",
        "security_attribute",
        "missing_registry",
        "duplicate_listing",
        "unknown_package",
        "unknown_payload",
        "context_keys",
    ],
)
def test_owner_cross_references_refuse(proof_case, change):
    _, listing_id, identity, original = proof_case
    response = copy.deepcopy(original)
    package = response["owner_package"]
    payload = package["payload"]
    ctx = package["trusted_context"]
    listing = payload["listings"][0]
    security = payload["securities"][0]
    binding = ctx["source_bindings"][listing["source_binding_ref"]]
    receipt = ctx["identity_receipts"][payload["verified_issuer_receipt_id"]]
    changes = {
        "entity": lambda: payload.update(entity_id="foreign"),
        "revision": lambda: response.update(identity_revision=99),
        "canonical": lambda: payload.update(canonical_name="Other Inc"),
        "selected_listing": lambda: response.update(selected_listing_id="foreign"),
        "security_entity": lambda: security.update(entity_id="foreign"),
        "security_type": lambda: security.update(security_type="preferred"),
        "inactive_listing": lambda: listing.update(listing_status="delisted"),
        "binding_entity": lambda: binding.update(entity_id="foreign"),
        "binding_listing": lambda: binding.update(listing_id="foreign"),
        "binding_security": lambda: binding.update(security_id="foreign"),
        "binding_source": lambda: binding.update(source_record_id="urn:foreign"),
        "binding_alias": lambda: binding.update(source_canonical_name="药明康德股份"),
        "binding_namespace": lambda: binding.update(source_namespace="ticker_alias"),
        "binding_status": lambda: binding.update(status="retired"),
        "receipt_revoked": lambda: receipt.update(effective_status="revoked"),
        "receipt_revision": lambda: receipt.update(identity_revision=2),
        "receipt_entity": lambda: receipt.update(entity_id="foreign"),
        "receipt_name": lambda: receipt.update(canonical_name=LABEL),
        "receipt_same_issuer": lambda: receipt.update(same_legal_issuer=False),
        "receipt_listing": lambda: receipt.update(listing_ids=[]),
        "receipt_attribute": lambda: receipt["listing_attributes"][listing_id].update(
            ticker="OTHER"
        ),
        "receipt_source": lambda: receipt["listing_attributes"][listing_id].update(
            source_record_id="urn:foreign"
        ),
        "security_attribute": lambda: receipt["security_attributes"][SEC].update(
            share_class="foreign"
        ),
        "missing_registry": lambda: ctx.update(market_registry={}),
        "duplicate_listing": lambda: payload["listings"].append(dict(listing)),
        "unknown_package": lambda: package.update(schema_version="2.3.0"),
        "unknown_payload": lambda: payload.update(identity_schema_version="3.0.0"),
        "context_keys": lambda: ctx.update(caller_alias="fake"),
    }
    changes[change]()
    with pytest.raises(IdentityBridgeError):
        alias._validate_proof(
            response,
            entity_id=ENT,
            listing_id=listing_id,
            company_query=LABEL,
            ref=REF,
            identity=identity,
        )


def test_actual_owner_revocation_between_admission_reads(native, tmp_path, code):
    config, listing, identity = native
    trusted = alias.make_source_alias_resolver(config, listing_id=listing)
    calls = []

    def callback(*args):
        proof = trusted(*args)
        calls.append(proof)
        if len(calls) == 1:
            owner_action(
                code,
                {
                    "action": "revoke",
                    "workspace": str(config.sw_root),
                    "receipt_id": proof["verified_issuer_receipt_id"],
                },
            )
        return proof

    catalog = ReportCatalog(root=ROOT, catalog_file=tmp_path / "not-created.jsonl")
    with pytest.raises(IdentityBridgeError):
        import_w09(
            catalog,
            entity_id=ENT,
            listing_id=listing,
            analysis_subject_id=None,
            identity_evidence=identity,
            identity_resolver=lambda _: identity,
            source_alias_resolver=callback,
        )
    assert len(calls) == 1
    assert not catalog.file.exists()


@pytest.mark.parametrize(
    "change",
    [
        "different_ref",
        "rank_missing",
        "duplicate_primary",
        "wrong_name",
        "receipt_mismatch",
    ],
)
def test_primary_anchor_refuses_nonexact_frozen_sources(change):
    results = frozen_results()
    primary = results[1]["sources"][0]
    if change == "different_ref":
        primary["company_wiki_trace"]["source_ref"]["byte_size"] += 1
    elif change == "rank_missing":
        primary["source_rank"] = 2
    elif change == "duplicate_primary":
        results[1]["sources"].append(copy.deepcopy(primary))
    elif change == "wrong_name":
        primary["company_wiki_trace"]["source_manifest"]["display_name"] = CANONICAL
    else:
        primary["company_wiki_trace"]["read_receipt"]["source_id"] = "urn:other"
    with pytest.raises(IdentityBridgeError):
        alias.w09_primary_source_refs(results, LABEL)


def test_alias_requires_explicit_listing_and_workspace(native):
    config, _, identity = native
    with pytest.raises(IdentityBridgeError, match="source_alias_listing_required"):
        alias.make_source_alias_resolver(config)(ENT, LABEL, [REF, REF], identity)
    no_workspace = BridgeConfig(
        config.python, config.cli, config.owner_root, 10, 262144
    )
    with pytest.raises(IdentityBridgeError, match="source_alias_config_invalid"):
        alias._read_proof(
            no_workspace,
            {"entity_id": ENT, "listing_id": None, "as_of": "2026-11-01T00:00:00Z"},
        )


@pytest.mark.parametrize(
    "raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b"[]", b"\xff", b"not json"]
)
def test_protocol_rejects_ambiguous_or_invalid_json(raw):
    with pytest.raises(IdentityBridgeError):
        alias._json(raw)


@pytest.mark.parametrize(
    "mode,code",
    [
        ("oversize", "source_alias_output_too_large"),
        ("bad_hash", "source_alias_receipt_invalid"),
        ("wrong_query", "source_alias_unverified"),
        ("negative", "source_alias_unverified"),
        ("library_changed", "source_alias_unverified"),
        ("physical_path", "bridge_path_leak"),
        ("malformed", "source_alias_protocol_invalid"),
        ("nonzero", "source_alias_owner_refused"),
        ("timeout", "source_alias_timeout"),
    ],
)
def test_fixed_proof_subprocess_transport(tmp_path, mode, code):
    owner = tmp_path / "controlled-transport-owner"
    owner.mkdir()
    workspace = tmp_path / "controlled-workspace"
    workspace.mkdir()
    cli = owner / "dashboard_issuer_proof_cli.py"
    cli.write_text(
        """import hashlib,json,sys,time
mode = """
        + repr(mode)
        + """
query=json.load(sys.stdin)
if mode=='nonzero':
 print('private failure',file=sys.stderr);sys.exit(3)
if mode=='timeout':time.sleep(4)
if mode=='malformed':print('not json');sys.exit(0)
p={'schema_version':'stockwiki.dashboard_issuer_proof/1','authority':'stockwiki','state':'available',
   'reason_codes':[],'query':query,'library_revision':'not_provided_no_global_revision'}
if mode=='oversize':p['padding']='x'*8192
if mode=='wrong_query':p['query']={}
if mode=='negative':p['state']='unverified'
if mode=='library_changed':p['library_revision']='unknown_global_revision'
if mode=='physical_path':p['locator']=__file__
p['receipt_sha256']=hashlib.sha256(json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
if mode=='bad_hash':p['receipt_sha256']='0'*64
print(json.dumps(p))
""",
        encoding="utf-8",
    )
    config = BridgeConfig(
        Path(sys.executable),
        owner / "dashboard_identity_bridge_cli.py",
        owner,
        1 if mode == "timeout" else 5,
        4096,
        workspace,
    )
    with pytest.raises(IdentityBridgeError) as exc:
        alias._read_proof(
            config,
            {"entity_id": ENT, "listing_id": None, "as_of": "2026-11-01T00:00:00Z"},
        )
    assert exc.value.error_code == code
    assert str(tmp_path) not in str(exc.value)


@pytest.mark.parametrize(
    "change",
    [
        "bool_bytes",
        "empty_mime",
        "wrong_document",
        "wrong_source",
        "extra_path",
        "schema",
    ],
)
def test_bad_six_field_source_ref_is_rejected(change):
    ref = dict(REF)
    if change == "bool_bytes":
        ref["byte_size"] = True
    elif change == "empty_mime":
        ref["mime_type"] = ""
    elif change == "wrong_document":
        ref["document_id"] = "urn:other"
    elif change == "wrong_source":
        ref["source_id"] = "urn:other"
    elif change == "schema":
        ref["schema_version"] = "2.2"
    else:
        ref["path"] = "physical"
    with pytest.raises(IdentityBridgeError):
        alias._source_ref(ref)


def test_pathless_https_is_not_a_drive_letter_and_embedded_files_are_rejected(tmp_path):
    alias._assert_proof_pathless(
        {"evidence_ref": "https://example.invalid/issuer/evidence"}
    )
    with pytest.raises(IdentityBridgeError):
        alias._assert_proof_pathless({"evidence_ref": str(tmp_path / "private-file")})
    with pytest.raises(IdentityBridgeError):
        alias._assert_proof_pathless(
            {
                "evidence_ref": "https://example.invalid/?file="
                + str(tmp_path / "private-file")
            }
        )


def test_actual_admin_cli_uses_the_trusted_alias_callback(native, tmp_path):
    config, listing, _ = native
    config_file = tmp_path / "trusted-operator-config.json"
    config_file.write_text(
        json.dumps(
            {
                "python": str(config.python),
                "cli": str(config.cli),
                "owner_root": str(config.owner_root),
                "sw_root": str(config.sw_root),
                "timeout_seconds": 10,
                "max_output_bytes": 262144,
            }
        ),
        encoding="utf-8",
    )
    catalog = tmp_path / "public-admin-catalog.jsonl"
    completed = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-B",
            str(ROOT / "scripts/report_catalog_identity_cli.py"),
            "import-w09",
            "--entity-id",
            ENT,
            "--listing-id",
            listing,
            "--config",
            str(config_file),
            "--catalog-file",
            str(catalog),
        ],
        capture_output=True,
        timeout=120,
        cwd=ROOT,
    )
    assert completed.returncode == 0, completed.stderr.decode("utf-8")
    receipt = json.loads(completed.stdout)
    assert len(receipt["registered"]["reports"]) == 2
    assert receipt["identity_binding_mode"] == "source_bound_primary_annual"
    assert len(receipt["identity_alias_proof_sha256"]) == 64
    assert (
        len(ReportCatalog(root=ROOT, catalog_file=catalog).list_reports(ENT)["items"])
        == 2
    )


def test_fresh_owner_identity_lookup_rejects_stale_evidence(native):
    config, listing, identity = native
    stale = {
        **identity,
        "source_revision": identity["source_revision"].replace(
            "revision=1", "revision=9"
        ),
    }
    with pytest.raises(IdentityBridgeError, match="source_alias_identity_changed"):
        alias.make_source_alias_resolver(config, listing_id=listing)(
            ENT, LABEL, [REF, REF], stale
        )


@pytest.mark.parametrize(
    "locator",
    [
        "https://example.invalid:bad/issuer",
        "https://example.invalid:99999/issuer",
        "https://example.invalid:C:/private/issuer",
        "https://example.invalid:0/issuer",
        "https://example.invalid:/issuer",
        "https://example.invalid/issuer with space",
    ],
)
def test_https_port_and_authority_are_fully_validated(locator):
    with pytest.raises(IdentityBridgeError):
        alias._assert_proof_pathless({"evidence_ref": locator})


def test_https_valid_explicit_port_remains_supported():
    alias._assert_proof_pathless(
        {"evidence_ref": "https://example.invalid:443/issuer?q=source"}
    )


def _small_catalog_case(tmp_path):
    sys.path.insert(0, str(ROOT / "tests"))
    from test_report_catalog import _fixture

    return _fixture(tmp_path)


def test_trusted_append_guard_runs_after_validation_and_under_lock(
    tmp_path, monkeypatch
):
    catalog, _, _, run, attempt, report = _small_catalog_case(tmp_path)
    events = []
    original_validate = catalog._validate_report_artifact
    original_entries = catalog._entries

    def validate(item):
        result = original_validate(item)
        events.append("report-validated")
        return result

    def entries(raw=None):
        result = original_entries(raw)
        events.append("entries-read")
        return result

    monkeypatch.setattr(catalog, "_validate_report_artifact", validate)
    monkeypatch.setattr(catalog, "_entries", entries)

    def guard():
        assert events == ["entries-read", "report-validated"]
        assert len(list(catalog.file.parent.glob(f"{catalog.file.name}.*.tmp"))) == 1
        assert OwnerFileLock(catalog.file.with_name(catalog.file.name + ".lock")).is_locked()
        assert not catalog.file.exists()
        events.append("guard")

    catalog.add_records(
        runs=[run], attempts=[attempt], reports=[report], before_append=guard
    )
    assert events[-1] == "guard"
    assert catalog.file.exists()
    assert not OwnerFileLock(catalog.file.with_name(catalog.file.name + ".lock")).is_locked()


def test_append_guard_refusal_preserves_existing_catalog_and_releases_lock(tmp_path):
    catalog, _, _, run, attempt, report = _small_catalog_case(tmp_path)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    before = catalog.file.read_bytes()

    def guard():
        raise IdentityBridgeError(
            "source_alias_identity_changed", "controlled late owner revocation"
        )

    with pytest.raises(IdentityBridgeError):
        catalog.add_records(
            runs=[{**run, "run_id": "run-late-refused"}], before_append=guard
        )
    assert catalog.file.read_bytes() == before
    assert not OwnerFileLock(catalog.file.with_name(catalog.file.name + ".lock")).is_locked()


def test_default_append_keeps_original_private_call_signature(tmp_path, monkeypatch):
    catalog = ReportCatalog(
        root=tmp_path, catalog_file=tmp_path / "private-catalog.jsonl"
    )
    calls = []

    def legacy(*, runs=None, attempts=None, reports=None):
        calls.append((runs, attempts, reports))
        return {"legacy": True}

    monkeypatch.setattr(catalog, "_add_records_locked", legacy)
    assert catalog.add_records(runs=[{"controlled": "not-validated-by-stub"}]) == {
        "legacy": True
    }
    assert len(calls) == 1
    assert not catalog.file.exists()


def test_invalid_append_guard_refused_before_new_parent_is_created(tmp_path):
    target = tmp_path / "not-created" / "catalog.jsonl"
    catalog = ReportCatalog(root=tmp_path, catalog_file=target)
    with pytest.raises(CatalogError) as error:
        catalog.add_records(runs=[{}], before_append=True)
    assert error.value.code == "invalid_admission_guard"
    assert not target.parent.exists()
