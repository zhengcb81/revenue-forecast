"""Diagnose why a real signed publication fails re-verification."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(TREE / "scripts"))
sys.path.insert(0, str(TREE / "tests"))

import attestation_protocol as ap  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

FAKE = TREE / "tests" / "e2e_support" / "i08b_fake_provider.py"
tmp = Path(tempfile.mkdtemp())

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

key = Ed25519PrivateKey.generate()
public = key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
)
fingerprint = hashlib.sha256(public).hexdigest()[:32]
now = datetime.now(timezone.utc)
stamp = lambda off: (now + timedelta(seconds=off)).strftime("%Y-%m-%dT%H:%M:%SZ")

domain = {
    "trust_domain_schema_version": "1.0",
    "domain_separator": ap.DOMAIN_SEPARATOR,
    "public_keys": [{
        "name": "diag",
        "public_key": base64.b64encode(public).decode("ascii"),
        "fingerprint": fingerprint,
        "issuer": "revenue-forecast/host-a",
        "key_id": "diag-key",
        "algorithm": "ed25519",
        "environment": "production",
        "not_before": stamp(-86400),
        "not_after": stamp(86400),
        "status": "active",
        "revoked_at": None,
    }],
}
(tmp / "trust.json").write_text(json.dumps(domain), encoding="utf-8")
os.environ[ap.TRUST_DOMAIN_ENV_VAR] = str(tmp / "trust.json")
os.environ[ap.PROVIDER_ENV_VAR] = sys.executable
os.environ[ap.PROVIDER_ARGV_ENV_VAR] = json.dumps([str(FAKE)])
os.environ[ap.TIMEOUT_ENV_VAR] = "20"
os.environ[ap.STDOUT_LIMIT_ENV_VAR] = "65536"
os.environ[ap.MAX_WINDOW_ENV_VAR] = "3600"
os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(tmp / "registry.jsonl")
os.environ["I08B_FAKE_KEY_HEX"] = key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
).hex()
os.environ["I08B_FAKE_ISSUER"] = "revenue-forecast/host-a"
os.environ["I08B_FAKE_KEY_ID"] = "diag-key"
os.environ["I08B_FAKE_MODE"] = "ok"
os.environ["I08B_FAKE_SIGNED_AT"] = "+1"

# instrument the failure path
original_verify = ap.verify_publication_attestation


def traced(result):
    findings = original_verify(result)
    if findings:
        record = result.get("publication_attestation") or {}
        recomputed = ap.payload_sha256(result)
        print("FINDINGS           :", findings)
        print("record commitment  :", record.get("payload_sha256"))
        print("recomputed         :", recomputed)
        print("stated (top level) :", result.get("payload_sha256"))
        print("receipt projection :", (result.get("publication_receipt") or {}).get("validated_payload_sha256"))
        # show which keys the projection sees
        projection = {
            k: type(v).__name__
            for k, v in result.items()
            if k not in ("result_sha256", "publication_receipt", "publication_attestation")
            and k not in ap.UNSIGNED_APPENDIX_KEYS
        }
        print("projection keys    :", sorted(projection))
    return findings


ap.verify_publication_attestation = traced
try:
    result = run_forecast(forecast_document())
    print("RUN OK, commitment:", result.get("payload_sha256"))
except Exception as exc:  # noqa: BLE001
    print("RUN RAISED:", type(exc).__name__, exc)
