"""Diagnostic: exercise the provider handshake directly and print every step."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO / "tests"))
sys.path.insert(0, str(REPO / "scripts"))

import revenue_core  # noqa: E402
from contracts.evidence import canonical_sha256  # noqa: E402
from revenue_publication import publication_attestation_request  # noqa: E402

SOURCE = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\B1-I08C-product-fixes\a20260921-01\test_b1_rem.py"
)

tmp = Path(tempfile.mkdtemp(prefix="b1_diag_"))
provider = tmp / "fake_attestation_provider.py"
text = SOURCE.read_text(encoding="utf-8")
start = text.index("FAKE_PROVIDER_SOURCE = '''") + len("FAKE_PROVIDER_SOURCE = '''")
end = text.index("'''", start)
provider.write_text(text[start:end].replace("\\\\x07", "\\x07"), encoding="utf-8")

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

private = Ed25519PrivateKey.from_private_bytes(b"\x07" * 32)
public = private.public_key().public_bytes_raw()
fingerprint = hashlib.sha256(public).hexdigest()[:32]
domain = json.dumps(
    {
        "public_keys": [
            {
                "name": "diag",
                "key_id": "rf-b1-test-key",
                "issuer": "revenue-forecast/host-b1",
                "public_key": base64.b64encode(public).decode("ascii"),
                "fingerprint": fingerprint,
            }
        ]
    },
    sort_keys=True,
)
trust = tmp / "trusted_signer_public_keys.json"
trust.write_text(domain, encoding="utf-8")

os.environ["REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS"] = str(trust)
os.environ["B1_FAKE_PROVIDER_ISSUER"] = "revenue-forecast/host-b1"
os.environ["B1_FAKE_PROVIDER_KEY_ID"] = "rf-b1-test-key"
os.environ["REVENUE_ATTESTATION_PROVIDER"] = str(provider)
os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(tmp / "registry.jsonl")

request = publication_attestation_request(
    request_id="a" * 64, payload_sha256="b" * 64, result_sha256="c" * 64
)
print("REQUEST:", json.dumps(request, sort_keys=True))

proc = subprocess.run(
    [str(provider)],
    input=json.dumps(request, sort_keys=True).encode("utf-8"),
    capture_output=True,
    check=False,
)
print("PROVIDER RC:", proc.returncode)
print("PROVIDER STDERR:", proc.stderr.decode("utf-8", "replace")[:500])
raw = proc.stdout.decode("utf-8", "replace")
print("PROVIDER STDOUT:", raw[:600])
response = json.loads(raw)
print("RESPONSE FINGERPRINT:", response.get("fingerprint"), "expected", fingerprint)

message = canonical_sha256(request).encode("ascii")
print("MESSAGE:", message)
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    Ed25519PublicKey.from_public_bytes(public).verify(
        bytes.fromhex(response["signature"]), message
    )
    print("DIRECT VERIFY: OK")
except Exception as exc:  # noqa: BLE001 - diagnostic
    print("DIRECT VERIFY FAILED:", type(exc).__name__, exc)

print("TRUSTED KEYS LOADED:", list(revenue_core.__dict__ and {}))
from contracts.evidence import _trusted_signer_public_keys  # noqa: E402

print("trusted:", list(_trusted_signer_public_keys()))

try:
    identity = revenue_core._validate_attestation_response(request, response)
    print("HOST VALIDATE: OK", identity)
except Exception as exc:  # noqa: BLE001 - diagnostic
    print("HOST VALIDATE FAILED:", type(exc).__name__, exc)
print("attestation_last_failure:", revenue_core.attestation_last_failure())
print("capability:", revenue_core.attestation_capability())
print("failure after capability:", revenue_core.attestation_last_failure())
