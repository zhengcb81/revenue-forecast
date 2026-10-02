# FC-1204 ratchet measurement harness (authoritative metric = the test's own code).
import importlib.util
import sys
import ast
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
spec = importlib.util.spec_from_file_location(
    "rat", str(REPO / "tests" / "contract" / "test_fc1204_complexity_ratchet.py")
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

BASE = REPO / "src" / "company_wiki" / "source_catalog"
TARGETS = {
    "observability.py": 6,
    "prune_retired_evidence.py": 12,
    "adapters/conformance.py": 8,
}

rc = 0
for rel, frozen in TARGETS.items():
    text = (BASE / rel).read_text(encoding="utf-8")
    file_max = m._max_complexity(text)
    table_frozen = m.FROZEN_MAX.get(rel)
    ok = file_max <= frozen
    rc = 0 if rc else (0 if ok else 1)
    print(f"{rel}: max={file_max} target={frozen} frozen_table={table_frozen} {'OK' if ok else 'FAIL'}")
    tree = ast.parse(text)
    per = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            c = 1 + m._mccabe(ast.parse(seg))
            per.append((c, node.name, node.lineno))
    for c, name, lineno in sorted(per, reverse=True)[:8]:
        print(f"    L{lineno:>4} {c:>3}  {name}")
print("RESULT:", "PASS" if rc == 0 else "FAIL")
sys.exit(rc)
