# REGISTRY-CLOSURE a20260923-01 — REM-05 judged verification (read-only over sealed trees).
# Proves: (1) `_VALUE` is dead code (assigned once, never loaded) in BOTH the r6 generation
# tree and the production company-wiki copy; (2) the annotation patch is behaviour-neutral
# (identical outputs on a shape corpus covering auth/assignment/C13/quoted/bare families);
# (3) both original and patched files compile.
import ast
import importlib.util
import json
import sys
from pathlib import Path

ATTEMPT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\REGISTRY-CLOSURE\a20260923-01")
ORIG = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01\iso\product_narrow_r6\src\company_wiki\source_catalog\observability.py")
PROD = Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\observability.py")
PATCHED = ATTEMPT / "fix_rem05" / "observability_r6tree_annotated_full.py"

out = []

def dead_proof(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assigns = loads = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "_VALUE":
                    assigns += 1
        if isinstance(node, ast.Name) and node.id == "_VALUE" and isinstance(node.ctx, ast.Load):
            loads += 1
    return {"file": str(path), "_VALUE_assigns": assigns, "_VALUE_loads": loads,
            "verdict": "DEAD-CODE-CONFIRMED" if assigns == 1 and loads == 0 else "NOT-DEAD"}

out.append(("ast_r6_tree", dead_proof(ORIG)))
out.append(("ast_production", dead_proof(PROD)))
out.append(("ast_patched", dead_proof(PATCHED)))

def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m  # required so dataclasses/annotations resolve during exec
    spec.loader.exec_module(m)
    return m

corpus = [
    "Authorization: Bearer abc123",
    "Authorization: token abc123",
    "Authorization: Bo?t\nSYNTHETIC_AUDIT_TOKEN",
    "Authorization: Bearer\nfoo\n<marker>",
    "Authorization:\ndoc=17",
    "Authorization:\ndoc=17\nstage=summarize",
    "Authorization: Bearer\n  MARKSECRET",
    "Authorization: Bearer abc\nSYNTHETIC_AUDIT_TOKEN",
    "token=AAA token2=BBB",
    "api_key=AAA api_key2=BBB",
    "password: iron steel",
    "password: 'iron steel'",
    "refresh_token=AAA access_token=BBB token_2=CCC",
    "doc=17; stage=summarize",
    "url=https://x/y?api_key=AAA",
    "Authorization: Basic dXNlcjpwYXNz",
    "Authorization: negotiate opaque",
    "secret=<none>",
    "export GITHUB_TOKEN=AAA",
    "Authorization: 'quoted value here'",
]

try:
    m_orig = load_mod("obs_orig_probe", ORIG)
    m_patched = load_mod("obs_patched_probe", PATCHED)
    fn = None
    for cand in ("redact_text", "redact"):
        if hasattr(m_orig, cand):
            fn = cand
            break
    rows = []
    identical = True
    for s in corpus:
        a = getattr(m_orig, fn)(s)
        b = getattr(m_patched, fn)(s)
        rows.append({"input": s, "orig": a, "patched": b, "same": a == b})
        identical = identical and (a == b)
    out.append(("behavior_identity", {"fn": fn, "n": len(corpus), "all_identical": identical, "rows": rows}))
    # also prove key_is_credential unchanged for the REM-06 probe keys (context only)
    keys = ["token2", "secret2", "password2", "api_key2", "token_2", "refresh_token", "access_token"]
    out.append(("key_is_credential_context", {k: (getattr(m_orig, "key_is_credential")(k), getattr(m_patched, "key_is_credential")(k)) for k in keys}))
except Exception as e:  # noqa: BLE001
    out.append(("behavior_identity", {"ERROR": repr(e)}))

import py_compile
for p in (str(PATCHED),):
    try:
        py_compile.compile(p, doraise=True, cfile=str(ATTEMPT / "fix_rem05" / "_compile_probe.pyc"))
        out.append(("compile_patched", "OK"))
    except Exception as e:  # noqa: BLE001
        out.append(("compile_patched", repr(e)))

print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
