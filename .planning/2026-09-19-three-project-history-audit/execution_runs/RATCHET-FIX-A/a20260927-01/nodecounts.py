import ast, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
spec=importlib.util.spec_from_file_location("rat", r"C:\Users\郑曾波\Projects\company-wiki\tests\contract\test_fc1204_complexity_ratchet.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
targets={"adapters/parity.py":"run_parity","lock.py":None,"prompt_injection.py":"record_prompt_injection_review","store.py":"read_pipeline_status"}
base="src/company_wiki/source_catalog/"
def topfuncs(text):
    tree=ast.parse(text)
    out={}
    for n in tree.body:
        if isinstance(n,ast.FunctionDef) and not n.name.startswith("test_"):
            out[n.name]=n
    return tree,out
for rel,want in targets.items():
    text=open(base+rel,encoding="utf-8").read()
    tree,fs=topfuncs(text)
    rows=[]
    for name,n in fs.items():
        seg=ast.get_source_segment(text,n)
        t=ast.parse(seg)
        cnt={}
        for x in ast.walk(t):
            cnt[type(x).__name__]=cnt.get(type(x).__name__,0)+1
        base_v=1+m._mccabe(t)
        rows.append((base_v,name,{k:cnt.get(k,0) for k in ("IfExp","Try","Match","BoolOp","If","For","While","With","Assert","ExceptHandler")}))
    rows.sort(reverse=True)
    print("==",rel)
    for v,name,c in rows[:3]:
        print("  ",v,name,c)
