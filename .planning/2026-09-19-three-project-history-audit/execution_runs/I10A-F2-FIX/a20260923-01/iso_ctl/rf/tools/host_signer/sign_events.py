"""Sign tool-event receipts with the host private key (R2.2).

Reads a JSONL of tool events, produces a JSONL of signed host receipts that
``contracts.evidence.validate_host_receipt`` accepts (signature +
public_key_fingerprint over the unsigned payload).  Run manually by the user —
an agent cannot invoke this from inside a run.

Event input (one JSON object per line):
    {"tool_name": "filing_fetch", "action": "download", "event_sha256": "...",
     "timestamp": "...", "issuer": "user@host", "environment": "win11"}

Usage:
    python tools/host_signer/sign_events.py --events events.jsonl \
        --private-key key.pem --output signed.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sign_receipt(
    event: dict[str, Any], private_key: Ed25519PrivateKey
) -> dict[str, Any]:
    receipt = {
        "host_receipt_schema_version": "1.0",
        "issuer": event["issuer"],
        "environment": event["environment"],
        "tool_name": event["tool_name"],
        "action": event["action"],
        "event_sha256": event["event_sha256"],
        "timestamp": event["timestamp"],
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    message = canonical_sha256(receipt).encode("ascii")
    signature = private_key.sign(message).hex()
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    fingerprint = hashlib.sha256(public_bytes).hexdigest()[:32]
    return {
        **receipt,
        "signature": signature,
        "public_key_fingerprint": fingerprint,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign host tool-event receipts")
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    private_key = Ed25519PrivateKey.from_private_bytes(
        serialization.load_pem_private_key(
            args.private_key.read_bytes(), password=None
        ).private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
        )
    )
    with args.output.open("w", encoding="utf-8", newline="\n") as out:
        for line in args.events.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            out.write(json.dumps(sign_receipt(event, private_key), sort_keys=True) + "\n")
    print(f"signed {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
