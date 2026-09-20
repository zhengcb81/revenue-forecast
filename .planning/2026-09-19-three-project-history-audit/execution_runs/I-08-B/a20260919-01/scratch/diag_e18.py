"""Direct diagnostic of the E18 window rule with a hand-built payload."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(TREE / "scripts"))
sys.path.insert(0, str(TREE / "tests"))

import attestation_protocol as ap  # noqa: E402
from test_attestation_provider_protocol import _clock  # noqa: E402

base = datetime.now(timezone.utc)
stamp = _clock(base)
print("base       :", ap.rfc3339_z(base))
print("stamp(-600):", stamp(-600))
print("stamp(-500):", stamp(-500))
print("stamp(-599):", stamp(-599))

payload = {
    "attestation_payload_schema_version": "1.0",
    "domain_separator": ap.DOMAIN_SEPARATOR,
    "issuer": "revenue-forecast/host-a",
    "key_id": "k",
    "key_fingerprint": "a" * 32,
    "algorithm": "ed25519",
    "request_id": "b" * 64,
    "issued_at": stamp(-600),
    "expires_at": stamp(-500),
    "signed_at": stamp(-599),
    "input_sha256": "c" * 64,
    "payload_sha256": "d" * 64,
    "result_sha256": "",
    "receipt_sha256": "",
    "engine_version": ap.ENGINE_VERSION,
    "forecast_schema_version": ap.FORECAST_SCHEMA_VERSION,
    "publication_receipt_schema_version": ap.PUBLICATION_RECEIPT_SCHEMA_VERSION,
    "validator_version": ap.ENGINE_VERSION,
    "gate_ids": [],
}
print("field set ok:", sorted(payload) == sorted(ap.PAYLOAD_FIELDS))
try:
    ap.validate_payload(payload)
    print("VALIDATE   : NO ERROR  <-- unexpected")
except ap.AttestationError as exc:
    print("VALIDATE   :", exc.code)

# break it explicitly, as a control
payload["signed_at"] = stamp(600)
try:
    ap.validate_payload(payload)
    print("CONTROL    : NO ERROR  <-- unexpected")
except ap.AttestationError as exc:
    print("CONTROL    :", exc.code)
