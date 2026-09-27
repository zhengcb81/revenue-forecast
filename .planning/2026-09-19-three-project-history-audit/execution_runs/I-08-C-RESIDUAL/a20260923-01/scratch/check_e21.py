"""I08CR-c6 — L3/F3 check E-L3.1: static E21 scan + signed-request field membership.

Scans the CURRENT production scripts tree (post-promotion bytes) and B1's fixed copy.
Read-only; results enumerated exactly (file:line:text)."""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
TMP = Path(os.environ.get("TEMP", r"C:\Windows\Temp")) / "I08C-RESIDUAL-a20260923-01"
FIXED = TMP / "fixed" / "rf" / "scripts"

SIGNED_REQUEST_KEYS_EXPECTED_ABSENT = {"issuer", "key_id"}


def scan(root: Path):
    hits = []
    for p in sorted(root.rglob("*.py")):
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if "issuer_key_binding_mismatch" in line or "E21" in line:
                hits.append({"file": str(p), "line": i, "text": line.strip()})
    return hits


def request_keys(pub: Path):
    """Find publication_attestation_request() (or equivalent) and collect literal keys."""
    src = pub.read_text(encoding="utf-8")
    tree = ast.parse(src)
    result = {"function": None, "literal_keys": [], "canonical_call_covered_fields": []}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "attestation_request" in node.name:
            result["function"] = node.name
            for sub in ast.walk(node):
                if isinstance(sub, ast.Dict):
                    for k in sub.keys:
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            result["literal_keys"].append(k.value)
            break
    # what the signed canonical request covers, per the F3 text
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "canonical_sha256":
            result["canonical_call_covered_fields"].append("canonical_sha256(<request dict>) @line %d" % node.lineno)
    return result


def main() -> int:
    out = {}
    out["production_scan"] = scan(RF / "scripts")
    out["fixed_copy_scan"] = scan(FIXED) if FIXED.exists() else "fixed copy not prepared yet"
    rq = request_keys(RF / "scripts" / "revenue_publication.py")
    out["signed_request_shape"] = rq
    keys = set(rq["literal_keys"])
    out["issuer_key_id_in_signed_request"] = {
        "issuer": "issuer" in keys,
        "key_id": "key_id" in keys,
    }
    out["raise_sites"] = [
        h for h in out["production_scan"] if h["text"].startswith("raise ")
    ]

    ok = (
        len(out["raise_sites"]) == 0
        and not out["issuer_key_id_in_signed_request"]["issuer"]
        and not out["issuer_key_id_in_signed_request"]["key_id"]
    )
    out["all_ok"] = ok  # frozen expectation: claim documented, raised nowhere, ids unsigned
    (EVID / "E_L3_e21_scan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("L3_E-L3.1_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
