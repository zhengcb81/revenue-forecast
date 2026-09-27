"""I08CR-c7 — L3/F3 check E-L3.2: trust-loader shape (contracts.evidence.
_trusted_signer_public_keys) — static source extraction, no execution of referenced
attempts (the production module is parsed, not imported)."""
from __future__ import annotations

import ast
import json
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
EVID_FILE = RF / "scripts" / "contracts" / "evidence.py"


def main() -> int:
    src = EVID_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = {"target": str(EVID_FILE)}
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in (
            "_trusted_signer_public_keys",
            "_validate_host_signature",
        ):
            body_src = ast.get_source_segment(src, node) or ""
            out[node.name] = {
                "source": body_src,
                "parses_issuer": "issuer" in body_src,
                "parses_key_id": "key_id" in body_src,
                "mentions_fingerprint": "fingerprint" in body_src,
                "mentions_public_key": "public_key" in body_src or "public key" in body_src.lower(),
            }
            found = True
    out["loader_found"] = found
    loader = out.get("_trusted_signer_public_keys", {})
    ok = (
        found
        and loader.get("parses_issuer") is False
        and loader.get("parses_key_id") is False
        and loader.get("mentions_fingerprint") is True
    )
    out["interpretation"] = (
        "the trust domain resolves fingerprint -> public key with NO issuer/key_id fields; "
        "E21 as specified ('issuer != the trust-domain entry's issuer, or key_id mismatch') "
        "therefore needs the 12-field trust-entry schema (I-08-A E25, recorded NOT implemented) "
        "= a trust-schema cap change (oracle 7: stopped at its honest label)"
    )
    out["all_ok"] = ok
    (EVID / "E_L3_trust_loader.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("L3_E-L3.2_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
