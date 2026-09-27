"""Generate an Ed25519 key pair for the host signer (R2.2).

The private key stays with the user (file-permission protected); the public
key goes into the trusted-key whitelist that revenue-forecast validates
signatures against:

    config/trusted_signer_public_keys.json
    {"public_keys": [{"name": "...", "public_key": "<base64>", "fingerprint": "<hex>"}]}

Usage:
    python tools/host_signer/keygen.py --output key.pem [--name host-1]
"""

from __future__ import annotations

import argparse
import base64
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a host-signer Ed25519 key pair")
    parser.add_argument("--output", type=Path, required=True, help="private key PEM path")
    parser.add_argument("--name", default="host-signer", help="label for the whitelist entry")
    args = parser.parse_args()
    private_key = Ed25519PrivateKey.generate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    fingerprint = hashlib.sha256(public_bytes).hexdigest()[:32]
    print(f"private key written: {args.output} (protect this file!)")
    print("whitelist entry:")
    print(
        '{"name": "%s", "public_key": "%s", "fingerprint": "%s"}'
        % (args.name, base64.b64encode(public_bytes).decode("ascii"), fingerprint)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
