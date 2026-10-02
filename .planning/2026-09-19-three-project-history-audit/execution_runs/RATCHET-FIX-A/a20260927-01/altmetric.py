import ast, sys
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
def mccabe(node):
    total=0
    for c in ast.iter_child_nodes(node):
        total+=mccabe(c)
    if isinstance(node,(ast.If,ast.For,ast.While,ast.And,ast.Or,ast.ExceptHandler,ast.comprehension,ast.Assert,ast.With)):
        total+=1
    if isinstance(node,ast.BoolOp):
        total+=len(node.values)-1
    if isinstance(node,ast.IfExp):
        total+=1
    if isinstance(node,ast.Match):
        total+=len(node.cases)
    return total
files=["src/company_wiki/source_catalog/adapters/parity.py","src/company_wiki/source_catalog/lock.py","src/company_wiki/source_catalog/prompt_injection.py","src/company_wiki/source_catalog/store.py"]
for f in files:
    text=open(f,encoding="utf-8").read()
    tree=ast.parse(text)
    best=(0,None)
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and not n.name.startswith("test_"):
            seg=ast.get_source_segment(text,n) or ""
            try: v=1+mccabe(ast.parse(seg))
            except SyntaxError: v=0
            if v>best[0]: best=(v,n.name)
    print(f, "max-all-funcs-with-ifexp/match=", best)
