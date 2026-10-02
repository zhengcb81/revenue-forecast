import sys, ast
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
import mccabe
for rel in ["adapters/parity.py","lock.py","prompt_injection.py","store.py"]:
    p="src/company_wiki/source_catalog/"+rel
    src=open(p,encoding="utf-8").read()
    tree=ast.parse(src)
    v=mccabe.PathGraphingAstVisitor()
    v.preorder(tree, v)
    rows=sorted(((g.complexity(), n) for n,g in v.graphs.items()), reverse=True)
    print("mccabe", rel, rows[:3])
