import importlib.util, sys, ast, subprocess
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
spec=importlib.util.spec_from_file_location("rat", r"C:\Users\郑曾波\Projects\company-wiki\tests\contract\test_fc1204_complexity_ratchet.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
files=["src/company_wiki/source_catalog/adapters/parity.py","src/company_wiki/source_catalog/lock.py","src/company_wiki/source_catalog/prompt_injection.py","src/company_wiki/source_catalog/store.py"]
for f in files:
    out=subprocess.run(["git","show","HEAD:"+f],capture_output=True)
    text=out.stdout.decode("utf-8")
    tree=ast.parse(text)
    rows=[]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg=ast.get_source_segment(text,node) or ""
            rows.append((1+m._mccabe(ast.parse(seg)), node.name, node.lineno))
    rows.sort(reverse=True)
    print(f, "HEAD max=", rows[0][0], rows[0][1], "| worktree max=", m._max_complexity(open(f,encoding="utf-8").read()))
    print("   top3:", rows[:3])
    # async functions?
    asyncs=[n.name for n in tree.body if isinstance(n, ast.AsyncFunctionDef)]
    if asyncs: print("   async top-level:", asyncs)
