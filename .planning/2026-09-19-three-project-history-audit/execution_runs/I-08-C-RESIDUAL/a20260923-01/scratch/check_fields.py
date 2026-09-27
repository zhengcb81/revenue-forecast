"""I08CR-c2 — L1/F1 check E-L1.3: three-way 10-field measurement.

(a) AST of the fixed tree's revenue_publication.py  (source: B1 iso/fixed/rf, copied
    read-only into %TEMP% first so nothing is imported/executed from a referenced attempt)
(b) AST of B1's frozen test module ATTESTATION_FIELDS
(c) runtime import of the %TEMP% fixed copy -> len(PUBLICATION_ATTESTATION_FIELDS)

Also prepares the %TEMP% copies used by I08CR-c4/c5 (fixed tree + reviewer M6 mutant).
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
EVID = ATT / "evidence"
PLAN = ATT.parents[2]
B1 = PLAN / "execution_runs" / "B1-I08C-product-fixes" / "a20260921-01"
TMP = Path(os.environ.get("TEMP", r"C:\Windows\Temp")) / "I08C-RESIDUAL-a20260923-01"

FROZEN_SET = {
    "attestation_payload_schema_version",
    "domain_separator",
    "issuer",
    "key_id",
    "algorithm",
    "fingerprint",
    "request_id",
    "payload_sha256",
    "signed_at",
    "signature",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract_set_literal(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    try:
                        return set(ast.literal_eval(node.value))
                    except Exception:
                        if isinstance(node.value, ast.Call) and node.value.args:
                            return set(ast.literal_eval(node.value.args[0]))
    return None


def main() -> int:
    out = {"frozen_expected_set": sorted(FROZEN_SET), "frozen_expected_count": 10}

    # ---- prep %TEMP% copies (used by c2/c4/c5) ----
    fixed_dst = TMP / "fixed" / "rf"
    m6_dst = TMP / "m6" / "rf"
    fixed_src = B1 / "iso" / "fixed" / "rf"
    m6_src = B1 / "reviewer" / "scratch" / "mutations" / "M6" / "rf"
    if not fixed_dst.exists():
        shutil.copytree(fixed_src, fixed_dst)
    if not m6_dst.exists():
        shutil.copytree(m6_src, m6_dst)
    out["temp_copies"] = {
        "fixed": str(fixed_dst),
        "m6": str(m6_dst),
        "identity_fixed_publication": {
            "src": sha(fixed_src / "scripts" / "revenue_publication.py"),
            "dst": sha(fixed_dst / "scripts" / "revenue_publication.py"),
        },
        "identity_m6_publication": {
            "src": sha(m6_src / "scripts" / "revenue_publication.py"),
            "dst": sha(m6_dst / "scripts" / "revenue_publication.py"),
        },
    }

    # ---- (a) fixed-tree AST ----
    a = extract_set_literal(fixed_dst / "scripts" / "revenue_publication.py", "PUBLICATION_ATTESTATION_FIELDS")
    out["a_fixed_tree_ast"] = {
        "members": sorted(a) if a is not None else None,
        "count": len(a) if a is not None else None,
        "equals_frozen_set": a == FROZEN_SET,
    }

    # ---- (b) frozen-test AST ----
    b = extract_set_literal(B1 / "test_b1_rem.py", "ATTESTATION_FIELDS")
    out["b_frozen_test_ast"] = {
        "members": sorted(b) if b is not None else None,
        "count": len(b) if b is not None else None,
        "equals_frozen_set": b == FROZEN_SET,
    }

    # ---- (c) runtime import from the %TEMP% copy ----
    scripts = str(fixed_dst / "scripts")
    for p in list(sys.path):
        if p in (scripts,):
            sys.path.remove(p)
    sys.path.insert(0, scripts)
    import revenue_publication as rp  # noqa: E402

    rt = set(rp.PUBLICATION_ATTESTATION_FIELDS)
    out["c_runtime_import"] = {
        "imported_from": str(Path(rp.__file__).resolve()),
        "count": len(rt),
        "members": sorted(rt),
        "equals_frozen_set": rt == FROZEN_SET,
    }

    ok = (
        out["a_fixed_tree_ast"]["equals_frozen_set"]
        and out["b_frozen_test_ast"]["equals_frozen_set"]
        and out["c_runtime_import"]["equals_frozen_set"]
        and out["temp_copies"]["identity_fixed_publication"]["src"]
        == out["temp_copies"]["identity_fixed_publication"]["dst"]
        and out["temp_copies"]["identity_m6_publication"]["src"]
        == out["temp_copies"]["identity_m6_publication"]["dst"]
    )
    out["all_ok"] = ok
    (EVID / "E_L1_fieldcount_threeway.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    print("L1_E-L1.3_ALL_OK:", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
