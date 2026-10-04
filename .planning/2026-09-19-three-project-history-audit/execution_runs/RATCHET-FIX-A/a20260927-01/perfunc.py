import importlib.util, sys, ast
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
spec=importlib.util.spec_from_file_location("rat", r"C:\Users\郑曾波\Projects\company-wiki\tests\contract\test_fc1204_complexity_ratchet.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from pathlib import Path
base=Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog")
for rel in ["adapters/parity.py","lock.py","prompt_injection.py","store.py"]:
    p=base/rel
    text=p.read_text(encoding="utf-8")
    tree=ast.parse(text)
    rows=[]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg=ast.get_source_segment(text,node) or ""
            rows.append((1+m._mccabe(ast.parse(seg)), node.name, node.lineno))
    rows.sort(reverse=True)
    print(rel, "MAX=", rows[0][0] if rows else 0)
    for c,n,l in rows[:5]:
        print("   ", c, n, "line", l)
