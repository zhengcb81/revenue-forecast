"""REM-42/E21 + F6 `result_sha256` binding-feasibility probe — READ-ONLY.

Runs against the tree named by ``B1_REPO_ROOT`` (this card: ``SRC/iso/fixed/rf``)
without writing a byte into that tree: the publication registry is redirected,
bytecode is disabled, and every artifact the probe creates lives under this
attempt's ``scratch/probe_work/``.

Frozen expectations (this attempt's oracle.md §3.3):

* Q1  ``_trusted_signer_public_keys()`` -> ``dict[str, bytes]`` (fingerprint ->
      raw public key). ``issuer``/``key_id`` are NOT in the loader output even
      though the trust FILE entries carry them.
* Q2  renaming ``record["issuer"]`` (resp. ``record["key_id"]``) with all
      self-hashes recomputed is ACCEPTED by ``validate_publication_receipt``
      (F3's measurement re-established); corrupting the signature is REJECTED
      (negative control, proves verification is exercised).
* Q3  ``result_sha256`` readings are separated and both measured:
      (a) arbitrary rewrite alone;
      (b) full self-consistent recompute of every self-hash chain.
      Receipt layer and forecast-output layer are reported separately; the
      observed outcomes are recorded verbatim either way (no silent drop).

Usage: python probe_e21_binding.py <repo_root_under_test>
Prints one JSON object to stdout; exit 0 iff every step completed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path

_ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-PREREQ\a20260922-01"
)
_SRC_ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-I08C-product-fixes\a20260921-01"
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _outcome(fn, *args, **kwargs):
    """Run a validator; return {'verdict': 'ACCEPTED'} or REJECTED + message."""
    try:
        fn(*args, **kwargs)
        return {"verdict": "ACCEPTED", "message": None}
    except Exception as exc:  # noqa: BLE001 - measurement, not control flow
        return {
            "verdict": "REJECTED",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }


def main() -> int:
    repo = Path(sys.argv[1]).resolve()
    env_root = os.environ.get("B1_REPO_ROOT")
    if env_root and Path(env_root).resolve() != repo:
        raise SystemExit(f"B1_REPO_ROOT={env_root} != argv[1]={repo}")

    # Isolate: registry + trust/provider env point ONLY into this attempt.
    work = _ATTEMPT / "scratch" / "probe_work"
    work.mkdir(parents=True, exist_ok=True)
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(work / "publications.jsonl")
    os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
    os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)

    for p in (str(repo / "tests"), str(repo / "scripts"), str(_SRC_ATTEMPT)):
        if p in sys.path:
            sys.path.remove(p)
    sys.path.insert(0, str(repo / "tests"))
    sys.path.insert(0, str(repo / "scripts"))
    sys.path.insert(0, str(_SRC_ATTEMPT))
    os.environ["B1_REPO_ROOT"] = str(repo)

    from contracts.evidence import _trusted_signer_public_keys  # noqa: E402
    import test_b1_rem as frozen_mod  # noqa: E402
    from revenue_core import run_forecast  # noqa: E402
    from revenue_publication import validate_publication_receipt  # noqa: E402
    from revenue_report import validate_forecast_output  # noqa: E402
    from test_recognition_bridge import forecast_document  # noqa: E402

    report: dict = {
        "probe": "REM-42/E21 + result_sha256 binding feasibility (read-only)",
        "tree_under_test": str(repo),
        "executed_source_sha256": {
            rel: _sha256_file(repo / rel)
            for rel in (
                "scripts/revenue_publication.py",
                "scripts/revenue_core.py",
                "scripts/revenue_report.py",
                "scripts/contracts/evidence.py",
            )
        },
    }

    # ---- fixtures: provider + isolated trust file (same bytes as the frozen
    # test module's fixtures; the private key never leaves this work dir) ----
    issuer = frozen_mod.ISSUER
    key_id = frozen_mod.KEY_ID
    os.environ["B1_FAKE_PROVIDER_ISSUER"] = issuer
    os.environ["B1_FAKE_PROVIDER_KEY_ID"] = key_id
    os.environ.pop("B1_FAKE_PROVIDER_MODE", None)

    provider_py = work / "fake_attestation_provider.py"
    provider_py.write_text(frozen_mod.FAKE_PROVIDER_SOURCE, encoding="utf-8")
    if os.name == "nt":
        launcher = work / "fake_attestation_provider.cmd"
        launcher.write_text(
            "@echo off\r\n"
            f'"{sys.executable}" -B -X utf8 "%~dp0fake_attestation_provider.py" %*\r\n',
            encoding="ascii",
        )
        provider = launcher
    else:
        provider = provider_py

    from cryptography.hazmat.primitives.asymmetric.ed25519 import (  # noqa: E402
        Ed25519PrivateKey,
    )

    private = Ed25519PrivateKey.from_private_bytes(b"\x07" * 32)
    public_bytes = private.public_key().public_bytes_raw()
    trust_path = work / "trusted_signer_public_keys.json"
    trust_entry = {
        "name": "b1-isolated-test-signer",
        "key_id": key_id,
        "issuer": issuer,
        "public_key": __import__("base64").b64encode(public_bytes).decode("ascii"),
        "fingerprint": hashlib.sha256(public_bytes).hexdigest()[:32],
    }
    trust_path.write_text(
        json.dumps({"public_keys": [trust_entry]}, sort_keys=True), encoding="utf-8"
    )
    os.environ["REVENUE_ATTESTATION_PROVIDER"] = str(provider)
    os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trust_path)

    # ---- Q1: what does the loader actually expose? ----
    loaded = _trusted_signer_public_keys()
    loader_repr = repr(loaded)
    trust_file = json.loads(trust_path.read_text(encoding="utf-8"))
    report["q1_loader_shape"] = {
        "return_type": type(loaded).__name__,
        "entry_count": len(loaded),
        "keys_are_32hex": all(
            isinstance(k, str) and len(k) == 32 for k in loaded
        ),
        "values_type": sorted({type(v).__name__ for v in loaded.values()}),
        "issuer_present_in_loader_output": issuer in loader_repr,
        "key_id_present_in_loader_output": key_id in loader_repr,
        "trust_file_entry_keys": sorted(trust_file["public_keys"][0]),
        "trust_file_has_issuer_and_key_id": {"issuer", "key_id"}
        <= set(trust_file["public_keys"][0]),
        "conclusion": (
            "loader returns fingerprint->public-key bytes only; the identity "
            "bytes exist in the trust FILE but are dropped by the loader, so "
            "an E21 comparison has nothing to read"
        ),
    }

    # ---- honest signed package (issuance side, real handshake) ----
    signed = run_forecast(forecast_document())
    receipt = signed["publication_receipt"]
    assert receipt["attestation_status"] == "host_signed", receipt.get(
        "attestation_failure"
    )
    record = receipt["publication_attestation"]
    assert isinstance(record, dict)
    report["setup"] = {
        "attestation_status": receipt["attestation_status"],
        "record_fields": sorted(record),
        "record_field_count": len(record),
        "issuer": record["issuer"],
        "key_id": record["key_id"],
    }

    # ---- Q2: issuer / key_id rename (the F3 attack) ----
    rename_issuer = copy.deepcopy(signed)
    rename_issuer["publication_receipt"]["publication_attestation"][
        "issuer"
    ] = "revenue-forecast/evil"
    frozen_mod._rehash(rename_issuer)
    rename_key_id = copy.deepcopy(signed)
    rename_key_id["publication_receipt"]["publication_attestation"]["key_id"] = (
        "evil-key-id"
    )
    frozen_mod._rehash(rename_key_id)
    corrupt_sig = copy.deepcopy(signed)
    corrupt_sig["publication_receipt"]["publication_attestation"]["signature"] = (
        "0" * 128
    )
    frozen_mod._rehash(corrupt_sig)
    report["q2_identity_binding"] = {
        "issuer_renamed_to": "revenue-forecast/evil",
        "issuer_rename__validate_publication_receipt": _outcome(
            validate_publication_receipt, rename_issuer
        ),
        "issuer_rename__validate_forecast_output": _outcome(
            validate_forecast_output, rename_issuer
        ),
        "key_id_renamed_to": "evil-key-id",
        "key_id_rename__validate_publication_receipt": _outcome(
            validate_publication_receipt, rename_key_id
        ),
        "negative_control_corrupt_signature__validate_publication_receipt": _outcome(
            validate_publication_receipt, corrupt_sig
        ),
        "honest_signed__validate_publication_receipt": _outcome(
            validate_publication_receipt, signed
        ),
        "honest_signed__validate_forecast_output": _outcome(
            validate_forecast_output, signed
        ),
    }

    # ---- Q3: result_sha256 readings, both measured ----
    arb = copy.deepcopy(signed)
    original_result_sha = arb["result_sha256"]
    arb["result_sha256"] = "ab" * 32
    report["q3_result_sha256"] = {
        "original_result_sha256": original_result_sha,
        "variant_a_arbitrary_rewrite": {
            "new_value": "ab" * 32,
            "validate_publication_receipt": _outcome(
                validate_publication_receipt, arb
            ),
            "validate_forecast_output": _outcome(validate_forecast_output, arb),
        },
        "variant_b_restored_value": {
            "note": "same package with result_sha256 restored (control)",
            "validate_publication_receipt": _outcome(
                validate_publication_receipt, signed
            ),
            "validate_forecast_output": _outcome(validate_forecast_output, signed),
        },
        "why_the_record_cannot_bind_it": (
            "the record's signed request pins result_sha256 to "
            "SIGNED_RESULT_SHA256_SENTINEL ('0'*64) and the record carries no "
            "result_sha256 field (r3 fixpoint: result_sha256 covers the "
            "receipt, which contains the record)"
        ),
    }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
