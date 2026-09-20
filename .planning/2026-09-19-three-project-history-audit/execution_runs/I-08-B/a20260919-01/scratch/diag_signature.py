"""Bisect helper: compare the payload the FAKE PROVIDER signed with the payload
the HOST reconstructs, and verify the signature over both."""

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

FAKE = TREE / "tests" / "e2e_support" / "i08b_fake_provider.py"

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import (  # noqa: E402
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

tmp = Path(tempfile.mkdtemp())
private = Ed25519PrivateKey.generate()
private_hex = private.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption(),
).hex()
public_bytes = private.public_key().public_bytes(
    encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
)
fingerprint = hashlib.sha256(public_bytes).hexdigest()[:32]
issuer = "revenue-forecast/host-a"
now = datetime.now(timezone.utc)
stamp = lambda offset: ap.rfc3339_z(now + timedelta(seconds=offset))

domain_doc = {
    "trust_domain_schema_version": "1.0",
    "domain_separator": ap.DOMAIN_SEPARATOR,
    "public_keys": [
        {
            "name": "diag",
            "public_key": base64.b64encode(public_bytes).decode("ascii"),
            "fingerprint": fingerprint,
            "issuer": issuer,
            "key_id": "rf-test-2026a",
            "algorithm": "ed25519",
            "environment": "production",
            "not_before": stamp(-86400),
            "not_after": stamp(86400),
            "status": "active",
            "revoked_at": None,
        }
    ],
}
domain_path = tmp / "trust.json"
domain_path.write_text(json.dumps(domain_doc), encoding="utf-8")
log_path = tmp / "calls.jsonl"

os.environ[ap.TRUST_DOMAIN_ENV_VAR] = str(domain_path)
os.environ[ap.PROVIDER_ENV_VAR] = sys.executable
os.environ[ap.TIMEOUT_ENV_VAR] = "20"
os.environ[ap.STDOUT_LIMIT_ENV_VAR] = "65536"
os.environ[ap.MAX_WINDOW_ENV_VAR] = "3600"
os.environ["I08B_FAKE_LOG"] = str(log_path)
os.environ["I08B_FAKE_KEY_HEX"] = private_hex
os.environ["I08B_FAKE_ISSUER"] = issuer
os.environ["I08B_FAKE_KEY_ID"] = "rf-test-2026a"
os.environ["I08B_FAKE_MODE"] = "ok"

request = ap.build_request(
    request_id=os.urandom(32).hex(),
    issued_at=stamp(-10),
    expires_at=stamp(600),
    payload_sha256=hashlib.sha256(b"payload").hexdigest(),
    input_sha256=hashlib.sha256(b"input").hexdigest(),
    result_sha256="",
    receipt_sha256="",
    requested_issuer=issuer,
)
result = ap.call_provider(
    request, timeout_seconds=20, stdout_limit_bytes=65536, extra_argv=[str(FAKE)]
)
print("call code:", result.code, "rc:", result.returncode, "detail:", result.detail)
if result.response is None:
    print("no response; bail")
    raise SystemExit(2)
response = ap.validate_response(result.response, request)
host_payload = ap.response_to_payload(response, request, gate_ids=())
log = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
print("log entries:", len(log))
client_entry = [entry for entry in log if "call" in entry][0]
provider_view = {
    "request_keys": sorted(client_entry["request"]),
    "request": client_entry["request"],
}
print("host request keys       :", sorted(request))
print("provider saw request    :", provider_view["request_keys"])
print("identical request dicts :", provider_view["request"] == request)

host_bytes = ap.canonical_bytes(host_payload)
host_msg = hashlib.sha256(host_bytes).hexdigest().encode("ascii")
print("host payload keys       :", sorted(host_payload))
print("host message            :", host_msg.decode())
signature = response["signature"]
public = Ed25519PublicKey.from_public_bytes(public_bytes)
try:
    public.verify(bytes.fromhex(signature), host_msg)
    print("VERIFY host payload     : OK")
except Exception as exc:  # noqa: BLE001
    print("VERIFY host payload     : FAIL", type(exc).__name__)
# reconstruct from the logged response fields the provider used
print("provider fingerprint    :", response["key_fingerprint"])
print("host fingerprint        :", fingerprint)
print("response signed_at      :", response["signed_at"])
print("request issued/expires  :", request["issued_at"], request["expires_at"])
print("host payload json       :", ap.canonical_text(host_payload))
