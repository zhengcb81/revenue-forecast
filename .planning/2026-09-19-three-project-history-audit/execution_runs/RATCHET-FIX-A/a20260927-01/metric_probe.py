import ast, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
spec=importlib.util.spec_from_file_location("rat", r"C:\Users\郑曾波\Projects\company-wiki\tests\contract\test_fc1204_complexity_ratchet.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
M=m._mccabe
def variant(node, ifexp=False, match1=False, matchcases=False, elif_=False, ternary_skip=False):
    total=0
    for c in ast.iter_child_nodes(node):
        total+=variant(c, ifexp, match1, matchcases, elif_)
    if isinstance(node,(ast.If,ast.For,ast.While,ast.And,ast.Or,ast.ExceptHandler,ast.comprehension,ast.Assert,ast.With)):
        total+=1
    if isinstance(node,ast.BoolOp): total+=len(node.values)-1
    if ifexp and isinstance(node,ast.IfExp): total+=1
    if isinstance(node,ast.Match):
        if match1: total+=1
        elif matchcases: total+=len(node.cases)
    return total
files=["adapters/parity.py","lock.py","prompt_injection.py","store.py"]
base="src/company_wiki/source_catalog/"
print("=== walk-based (all funcs incl. methods/nested) with test _mccabe ===")
for rel in files:
    text=open(base+rel,encoding="utf-8").read()
    tree=ast.parse(text)
    best=(0,"")
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and not n.name.startswith("test_"):
            seg=ast.get_source_segment(text,n) or ""
            try: v=1+M(ast.parse(seg))
            except SyntaxError: v=0
            if v>best[0]: best=(v,n.name)
    print(rel, best)
print("=== top-level, variants (ifexp / match1 / matchcases) ===")
for rel in files:
    text=open(base+rel,encoding="utf-8").read()
    tree=ast.parse(text)
    rows={"ifexp":[],"match1":[],"matchcases":[]}
    for n in tree.body:
        if isinstance(n,ast.FunctionDef) and not n.name.startswith("test_"):
            seg=ast.get_source_segment(text,n) or ""
            t=ast.parse(seg)
            rows["ifexp"].append((1+variant(t,ifexp=True),n.name))
            rows["match1"].append((1+variant(t,match1=True),n.name))
            rows["matchcases"].append((1+variant(t,matchcases=True),n.name))
    for k,v in rows.items():
        v.sort(reverse=True); print(rel,k,v[0])
