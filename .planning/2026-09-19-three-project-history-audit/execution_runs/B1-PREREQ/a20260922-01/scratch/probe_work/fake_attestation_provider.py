"""Bounded fake attestation provider for the B1-I08C card (isolated fixture)."""
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def main() -> int:
    raw = sys.stdin.read()
    request = json.loads(raw)
    if os.environ.get("B1_FAKE_PROVIDER_MODE") == "refuse":
        sys.stderr.write("no private key available\n")
        return 11
    private = Ed25519PrivateKey.from_private_bytes(b"\x07" * 32)
    public = private.public_key().public_bytes_raw()
    # The signing target is the WHOLE request object, including the redundant
    # `canonical_payload_sha256` member (B1 oracle r1 §3.4 + revision r3 R3-2).
    signature = private.sign(canonical(request).encode("ascii")).hex()
    response = {
        "attestation_response_schema_version": "1.0",
        "request_id": request["request_id"],
        "payload_sha256": request["payload_sha256"],
        "domain_separator": request["domain_separator"],
        "issuer": os.environ.get("B1_FAKE_PROVIDER_ISSUER", ""),
        "key_id": os.environ.get("B1_FAKE_PROVIDER_KEY_ID", ""),
        "fingerprint": hashlib.sha256(public).hexdigest()[:32],
        "algorithm": "ed25519",
        "signature": signature,
        "signed_at": "2026-07-12T00:00:00Z",
    }
    sys.stdout.write(json.dumps(response, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
