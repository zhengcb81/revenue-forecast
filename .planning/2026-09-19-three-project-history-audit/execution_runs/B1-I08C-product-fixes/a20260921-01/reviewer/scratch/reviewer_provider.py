import hashlib, json, os, sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()

raw = sys.stdin.read()
request = json.loads(raw)
private = Ed25519PrivateKey.from_private_bytes(b"\x09" * 32)
public = private.public_key().public_bytes_raw()
signature = private.sign(canonical(request).encode("ascii")).hex()
response = {
    "attestation_response_schema_version": "1.0",
    "request_id": request["request_id"],
    "payload_sha256": request["payload_sha256"],
    "domain_separator": request["domain_separator"],
    "issuer": "revenue-forecast/reviewer-b1",
    "key_id": "rf-reviewer-key",
    "fingerprint": hashlib.sha256(public).hexdigest()[:32],
    "algorithm": "ed25519",
    "signature": signature,
    "signed_at": "2026-07-12T00:00:00Z",
}
sys.stdout.write(json.dumps(response, sort_keys=True))
