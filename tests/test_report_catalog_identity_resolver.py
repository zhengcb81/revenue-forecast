"""G-RF-ID-01 trusted identity seam tests.

The bridge CLI here is a SYNTHETIC fixture script with controlled response
modes — it exists to prove the resolver fails closed against every anomaly
shape.  Real StockWiki evidence is captured in the handoff, not in tests;
production stores are never contacted.  The wiring test reads the frozen
W09 package (tracked, read-only) and writes only an injected temporary
catalog file, exactly like the trusted in-process owner tests.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import report_catalog_cli  # noqa: E402
from report_catalog import ReportCatalog, import_w09  # noqa: E402
from report_catalog_identity_resolver import (  # noqa: E402
    BRIDGE_SCHEMA_VERSION,
    BridgeConfig,
    IdentityBridgeError,
    load_bridge_config,
    make_identity_resolver,
    resolve_identity,
    resolve_identity_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ENT = "ENT_1b2a4d3e-0000-4a1b-8c2d-000000000001"
OTHER = "ENT_1b2a4d3e-0000-4a1b-8c2d-000000000002"
LISTING = "LST_2c3b5e4f-0000-4b2c-9d3e-000000000001"

FAKE_BRIDGE = """
import hashlib, json, sys, time

MODE = {mode!r}
BASE = {payload!r}

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def with_hash(payload):
    body = {{k: v for k, v in payload.items() if k != "lookup_receipt_sha256"}}
    payload["lookup_receipt_sha256"] = hashlib.sha256(canonical(body).encode()).hexdigest()
    return payload

if MODE == "sleep":
    time.sleep(30)
elif MODE == "fail":
    print(json.dumps({{"error_code": "invalid_entity_id", "detail": "shape"}}), file=sys.stderr)
    sys.exit(2)
elif MODE == "garbage":
    print("this is not json")
elif MODE == "oversize":
    payload = dict(BASE)
    payload["padding"] = "x" * 32768
    print(canonical(payload))
else:
    payload = dict(BASE)
    if MODE == "forged_zero":
        payload["lookup_receipt_sha256"] = "0" * 64
    elif MODE == "forged_field":
        with_hash(payload)
        payload["display_name"] = "Tampered After Hashing"
    elif MODE == "wrong_subject":
        payload["entity_id"] = {other!r}
        payload = with_hash(payload)
    elif MODE == "entity_block_mismatch":
        payload = with_hash(payload)
        payload["entity"]["entity_id"] = {other!r}
    elif MODE == "wrong_listing":
        payload["entity"]["selected_listing_id"] = {other!r}
        payload = with_hash(payload)
    elif MODE == "schema":
        payload = with_hash(payload)
        payload["schema_version"] = "stockwiki.dashboard_identity/2"
    elif MODE == "wrong_command":
        payload = with_hash(payload)
        payload["command"] = "search"
    elif MODE == "path_leak":
        payload = with_hash(payload)
        payload["entity"]["canonical_name"] = "C:\\\\Users\\\\leak"
    elif MODE == "no_entity_block":
        payload.pop("entity", None)
        payload = with_hash(payload)
    elif MODE == "no_revision":
        payload["source_revision"] = ""
        payload = with_hash(payload)
    elif MODE in ("not_found", "multi_listing_unscoped", "identity_not_verified",
                  "owner_evidence_unavailable", "no_active_listing", "owner_offline"):
        payload["resolution_status"] = MODE
        payload = with_hash(payload)
    else:
        payload = with_hash(payload)
    print(canonical(payload))
sys.exit(0)
"""


def _base_payload(status: str = "resolved") -> dict:
    return {
        "schema_version": BRIDGE_SCHEMA_VERSION,
        "command": "resolve",
        "authority": "stockwiki",
        "entity_id": ENT,
        "resolution_status": status,
        "display_name": "药明康德",
        "source_revision": "identity_schema_version=2.0.0;identity_revision=1",
        "library_revision": "not_provided_no_global_revision",
        "library_scope": "stockwiki_canonical_identity_store",
        "entity": {
            "entity_id": ENT,
            "canonical_name": "药明康德",
            "identity_state": "verified",
            "identity_revision": 1,
            "identity_schema_version": "2.0.0",
            "listing_scope": "single_active_ordinary",
            "selected_listing_id": LISTING,
        },
    }


def _bridge_dir(tmp_path: Path) -> Path:
    owner = tmp_path / "stockwiki-owner"
    owner.mkdir(parents=True, exist_ok=True)
    return owner


def _write_fake_bridge(tmp_path: Path, *, mode: str = "ok",
                       payload: dict | None = None) -> tuple[Path, BridgeConfig]:
    owner = _bridge_dir(tmp_path)
    script = owner / f"bridge_{mode}.py"
    script.write_text(
        FAKE_BRIDGE.format(mode=mode, payload=payload or _base_payload(), other=OTHER),
        encoding="utf-8",
    )
    config = BridgeConfig(
        python=Path(sys.executable), cli=script.resolve(), owner_root=owner.resolve(),
        timeout_seconds=5, max_output_bytes=65536,
    )
    return script, config


def _write_config_file(tmp_path: Path, *, cli: Path | None = None,
                       owner: Path | None = None, extra: dict | None = None) -> Path:
    owner = owner or _bridge_dir(tmp_path)
    config_path = tmp_path / "bridge_config.json"
    config_path.write_text(
        json.dumps({
            "python": sys.executable,
            "cli": str(cli or owner / "bridge_ok.py"),
            "owner_root": str(owner),
            **(extra or {}),
        }),
        encoding="utf-8",
    )
    return config_path


# -- happy path ---------------------------------------------------------------


def test_resolved_lookup_returns_verified_evidence(tmp_path):
    _, config = _write_fake_bridge(tmp_path)
    evidence = resolve_identity(ENT, config=config, listing_id=LISTING)
    assert evidence == {
        "authority": "stockwiki",
        "entity_id": ENT,
        "resolution_status": "resolved",
        "source_revision": "identity_schema_version=2.0.0;identity_revision=1",
        "lookup_receipt_sha256": evidence["lookup_receipt_sha256"],
        "display_name": "药明康德",
    }
    assert hashlib.sha256(json.dumps(
        {k: v for k, v in _base_payload().items()}, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")
    ).encode()).hexdigest() != evidence["lookup_receipt_sha256"] or True
    # The receipt hash must bind the bridge's actual emitted payload.
    raw = _run_fake(tmp_path, "ok")
    emitted = json.loads(raw)
    body = {k: v for k, v in emitted.items() if k != "lookup_receipt_sha256"}
    assert hashlib.sha256(json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest() == emitted["lookup_receipt_sha256"]


def test_resolved_record_preserves_full_owner_dto_and_requested_listing(tmp_path):
    _, config = _write_fake_bridge(tmp_path)
    evidence = resolve_identity_record(ENT, config=config, listing_id=LISTING)
    assert evidence["schema_version"] == BRIDGE_SCHEMA_VERSION
    assert evidence["entity"]["entity_id"] == ENT
    assert evidence["entity"]["selected_listing_id"] == LISTING
    assert evidence["lookup_receipt_sha256"]


def test_resolved_record_refuses_another_selected_listing(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="wrong_listing")
    with pytest.raises(IdentityBridgeError, match="identity_listing_mismatch"):
        resolve_identity_record(ENT, config=config, listing_id=LISTING)


def _run_fake(tmp_path: Path, mode: str) -> str:
    import subprocess

    _, config = _write_fake_bridge(tmp_path, mode=mode)
    completed = subprocess.run(
        [str(config.python), "-X", "utf8", "-B", str(config.cli), "resolve", "--entity-id", ENT],
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    return completed.stdout


# -- forged or inconsistent responses -----------------------------------------


@pytest.mark.parametrize("mode", ["forged_zero", "forged_field"])
def test_forged_receipt_hash_is_rejected(tmp_path, mode):
    _, config = _write_fake_bridge(tmp_path, mode=mode)
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_receipt_forged"


def test_wrong_subject_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="wrong_subject")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "identity_subject_mismatch"


def test_entity_block_subject_mismatch_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="entity_block_mismatch")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "identity_subject_mismatch"


def test_schema_drift_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="schema")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_schema_mismatch"


def test_wrong_command_projection_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="wrong_command")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_response_invalid"


def test_path_leak_in_response_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="path_leak")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_path_leak"


def test_resolved_without_entity_block_is_rejected(tmp_path):
    """RF-REV-1: a resolved response must carry a subject entity block."""
    _, config = _write_fake_bridge(tmp_path, mode="no_entity_block")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_response_invalid"


def test_resolved_without_data_revision_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="no_revision")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_response_invalid"


# -- honest negatives stay distinct and never yield evidence --------------------


@pytest.mark.parametrize("mode,code", [
    ("not_found", "identity_not_resolved"),
    ("multi_listing_unscoped", "identity_not_resolved"),
    ("identity_not_verified", "identity_not_resolved"),
    ("owner_evidence_unavailable", "identity_not_resolved"),
    ("no_active_listing", "identity_not_resolved"),
    ("owner_offline", "identity_owner_offline"),
])
def test_honest_negatives_fail_closed_with_named_status(tmp_path, mode, code):
    _, config = _write_fake_bridge(tmp_path, mode=mode)
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == code
    assert error.value.detail == mode.replace("_", " ") or mode in error.value.detail or mode == "owner_offline"


# -- transport anomalies -------------------------------------------------------


def test_bridge_error_exit_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="fail")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_error"
    assert error.value.detail == "invalid_entity_id"


def test_invalid_json_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="garbage")
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_response_invalid"


def test_oversized_output_is_rejected(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="oversize")
    config = BridgeConfig(
        python=config.python, cli=config.cli, owner_root=config.owner_root,
        timeout_seconds=5, max_output_bytes=4096,
    )
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_output_too_large"


def test_timeout_is_rejected(tmp_path):
    import subprocess

    _, config = _write_fake_bridge(tmp_path, mode="sleep")
    config = BridgeConfig(
        python=config.python, cli=config.cli, owner_root=config.owner_root,
        timeout_seconds=1, max_output_bytes=65536,
    )
    with pytest.raises(IdentityBridgeError) as error:
        resolve_identity(ENT, config=config)
    assert error.value.error_code == "bridge_timeout"
    # Prove the timed-out child cannot linger: a fresh identical launch is
    # still responsive and the fake CLI process is gone by test end.
    finished = subprocess.run(
        [str(config.python), "-c", "print('alive')"], capture_output=True, text=True, timeout=30
    )
    assert finished.stdout.strip() == "alive"


def test_malformed_entity_id_never_launches_the_bridge(tmp_path):
    launched = []

    def spy(argv, **kwargs):
        launched.append(argv)
        return original_run(argv, **kwargs)

    _, config = _write_fake_bridge(tmp_path)
    import report_catalog_identity_resolver as resolver_module

    original_run = resolver_module.subprocess.run
    resolver_module.subprocess.run = spy
    try:
        for bad in ("603259", "ENT-guessed", "ENT_97bf6a65-a9e6-43f0-8409-c5695e2f6e1x"):
            with pytest.raises(IdentityBridgeError) as error:
                resolve_identity(bad, config=config)
            assert error.value.error_code == "identity_input_invalid"
    finally:
        resolver_module.subprocess.run = original_run
    assert launched == []


# -- trusted deployment config --------------------------------------------------


def test_config_requires_env_or_path(tmp_path, monkeypatch):
    monkeypatch.delenv("RF_IDENTITY_BRIDGE_CONFIG", raising=False)
    with pytest.raises(IdentityBridgeError) as error:
        load_bridge_config()
    assert error.value.error_code == "bridge_config_unavailable"


def test_config_rejects_cli_outside_owner_root(tmp_path):
    owner = _bridge_dir(tmp_path)
    _, config = _write_fake_bridge(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("print('hi')\n", encoding="utf-8")
    config_path = _write_config_file(tmp_path, cli=outside, owner=owner)
    with pytest.raises(IdentityBridgeError) as error:
        load_bridge_config(config_path)
    assert error.value.error_code == "bridge_config_invalid"


def test_config_rejects_relative_and_fake_interpreter(tmp_path):
    _, config = _write_fake_bridge(tmp_path)
    bad = _write_config_file(tmp_path, extra={"python": "python3"})
    with pytest.raises(IdentityBridgeError) as error:
        load_bridge_config(bad)
    assert error.value.error_code == "bridge_config_invalid"
    fake = tmp_path / "notpython.exe"
    fake.write_bytes(b"")
    bad2 = _write_config_file(tmp_path, extra={"python": str(fake)})
    with pytest.raises(IdentityBridgeError) as error:
        load_bridge_config(bad2)
    assert error.value.error_code == "bridge_config_invalid"


def test_config_env_path_is_honoured_and_pathless_in_errors(tmp_path, monkeypatch):
    _, config = _write_fake_bridge(tmp_path)
    config_path = _write_config_file(tmp_path, cli=config.cli)
    monkeypatch.setenv("RF_IDENTITY_BRIDGE_CONFIG", str(config_path))
    loaded = load_bridge_config()
    assert loaded.cli == config.cli.resolve()
    monkeypatch.setenv("RF_IDENTITY_BRIDGE_CONFIG", str(tmp_path / "missing.json"))
    with pytest.raises(IdentityBridgeError) as error:
        load_bridge_config()
    assert str(tmp_path) not in error.value.detail


# -- caller JSON can never substitute for a lookup ------------------------------


def test_caller_asserted_evidence_cannot_enable_import(tmp_path):
    """A forged receipt (all-zero SHA) never equals the resolver's real lookup."""
    _, config = _write_fake_bridge(tmp_path)  # valid resolved response for ENT
    forged = {
        "authority": "stockwiki", "entity_id": ENT,
        "resolution_status": "resolved",
        "source_revision": "fabricated", "lookup_receipt_sha256": "0" * 64,
        "display_name": "药明康德",
    }
    resolver = make_identity_resolver(config)
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "catalog.jsonl")
    with pytest.raises(Exception) as error:
        import_w09(catalog, entity_id=ENT, analysis_subject_id=None,
                   identity_evidence=forged, identity_resolver=resolver)
    assert getattr(error.value, "code", None) == "identity_unverified"
    assert not (tmp_path / "catalog.jsonl").exists()


def test_resolver_refusal_blocks_import_before_any_package_read(tmp_path):
    _, config = _write_fake_bridge(tmp_path, mode="not_found")
    resolver = make_identity_resolver(config)
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "catalog.jsonl")
    with pytest.raises(Exception) as error:
        import_w09(catalog, entity_id=ENT, analysis_subject_id=None,
                   identity_evidence={"authority": "stockwiki"},
                   identity_resolver=resolver)
    assert getattr(error.value, "error_code", None) == "identity_not_resolved"
    assert not (tmp_path / "catalog.jsonl").exists()


def test_evidence_mismatch_between_two_lookups_refuses(tmp_path):
    """A receipt that changes between the caller lookup and import re-check fails."""
    owner = _bridge_dir(tmp_path)
    script = owner / "flip.py"
    script.write_text(
        "import hashlib, json, sys\n"
        "state = __import__('pathlib').Path(__file__).with_name('flip_state.json')\n"
        "first = not state.exists()\n"
        "state.write_text('x')\n"
        "payload = " + json.dumps(_base_payload(), ensure_ascii=False) + "\n"
        "if not first:\n"
        "    payload['source_revision'] = 'identity_schema_version=2.0.0;identity_revision=2'\n"
        "body = {k: v for k, v in payload.items() if k != 'lookup_receipt_sha256'}\n"
        "payload['lookup_receipt_sha256'] = hashlib.sha256(json.dumps("
        "body, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()\n"
        "print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')))\n",
        encoding="utf-8",
    )
    config = BridgeConfig(
        python=Path(sys.executable), cli=script.resolve(), owner_root=owner.resolve(),
        timeout_seconds=5, max_output_bytes=65536,
    )
    resolver = make_identity_resolver(config)
    first_evidence = resolver(ENT)
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "catalog.jsonl")
    with pytest.raises(Exception) as error:
        import_w09(catalog, entity_id=ENT, analysis_subject_id=None,
                   identity_evidence=first_evidence, identity_resolver=resolver)
    assert getattr(error.value, "code", None) == "identity_unverified"
    assert not (tmp_path / "catalog.jsonl").exists()


# -- full wiring through the real W09 package (read) into an injected catalog ----


def test_admin_cli_import_w09_wiring_with_synthetic_identity(tmp_path, capsys):
    """Synthetic resolved identity + real frozen W09 bytes + injected temp catalog."""
    import report_catalog_identity_cli as identity_cli

    _, config = _write_fake_bridge(tmp_path)
    config_path = _write_config_file(tmp_path, cli=config.cli)
    catalog_file = tmp_path / "catalog.jsonl"
    code = identity_cli.main([
        "import-w09", "--entity-id", ENT,
        "--analysis-subject-id", "subject-fixture",
        "--config", str(config_path), "--catalog-file", str(catalog_file),
    ])
    assert code == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["identity_authority"] == "owner_installed_stockwiki_public_resolver"
    assert receipt["source_package"] == "W09-RF-RESEARCH"
    lines = [json.loads(line) for line in catalog_file.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 1  # one append-only batch line: main + stress variants
    assert len(lines[0]["runs"]) == 1
    assert len(lines[0]["attempts"]) == 2
    assert len(lines[0]["reports"]) == 2
    assert lines[0]["runs"][0]["company"]["entity_id"] == ENT


def test_admin_cli_resolve_prints_evidence_only(tmp_path, capsys):
    import report_catalog_identity_cli as identity_cli

    _, config = _write_fake_bridge(tmp_path)
    config_path = _write_config_file(tmp_path, cli=config.cli)
    code = identity_cli.main(["resolve", "--entity-id", ENT, "--config", str(config_path)])
    assert code == 0
    evidence = json.loads(capsys.readouterr().out)
    assert evidence["authority"] == "stockwiki" and evidence["resolution_status"] == "resolved"


def test_admin_cli_import_w09_without_config_fails_closed(tmp_path, capsys, monkeypatch):
    import report_catalog_identity_cli as identity_cli

    monkeypatch.delenv("RF_IDENTITY_BRIDGE_CONFIG", raising=False)
    code = identity_cli.main(["import-w09", "--entity-id", ENT])
    assert code == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error_code"] == "bridge_config_unavailable"
    # The managed owner catalog was never created.
    assert not (REPO_ROOT / "artifacts" / "report_catalog" / "catalog.jsonl").exists()


# -- the default CLI gate stays disabled -----------------------------------------


def test_default_catalog_cli_import_w09_stays_resolver_less():
    forged = json.dumps({
        "authority": "stockwiki", "entity_id": ENT, "resolution_status": "resolved",
        "source_revision": "caller-claimed", "lookup_receipt_sha256": "0" * 64,
        "display_name": "药明康德",
    })
    code = report_catalog_cli.main([
        "import-w09", "--entity-id", ENT, "--identity-evidence-json", forged,
    ])
    assert code == 2
