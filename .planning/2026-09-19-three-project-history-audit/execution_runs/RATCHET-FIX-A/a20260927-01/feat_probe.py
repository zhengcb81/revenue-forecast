import ast, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
spec=importlib.util.spec_from_file_location("rat", "tests/contract/test_fc1204_complexity_ratchet.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
base="src/company_wiki/source_catalog/"
def feats(text, fname):
    tree=ast.parse(text)
    target=None
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==fname:
            target=n
    t=ast.parse(ast.get_source_segment(text,target))
    c={}
    def visit(node, parent=None):
        for ch in ast.iter_child_nodes(node):
            visit(ch, node)
            c[type(ch).__name__]=c.get(type(ch).__name__,0)+1
        if isinstance(node, ast.If) and parent is not None and isinstance(parent, ast.If) and parent.orelse and len(parent.orelse)==1 and parent.orelse[0] is node:
            c["ELIF"]=c.get("ELIF",0)+1
    visit(t)
    return c
targets={"adapters/parity.py":"run_parity","lock.py":"_process_identity","prompt_injection.py":"record_prompt_injection_review","store.py":"read_pipeline_status"}
for rel,fn in targets.items():
    text=open(base+rel,encoding="utf-8").read()
    tree=ast.parse(text)
    top=[n for n in tree.body if isinstance(n,ast.FunctionDef) and not n.name.startswith("test_")]
    T={}
    for n in top:
        seg=ast.get_source_segment(text,n)
        T[n.name]=1+m._mccabe(ast.parse(seg))
    c=feats(text, fn)
    print("==",rel,fn,"testmetric=",T.get(fn))
    print("   ELIF=",c.get("ELIF",0)," IfInOrelse=", end=" ")
    # count If nodes whose parent chain... use else-present counts
    keys=sorted(c.items(), key=lambda kv:-kv[1])
    print({k:v for k,v in keys if k in ("If","IfExp","Try","BoolOp","And","Or","comprehension","With","Assert","ExceptHandler","For","While","Return","Raise","Match","NamedExpr","ELIF")})
    print("   top funcs:", sorted(T.items(), key=lambda kv:-kv[1])[:3])
