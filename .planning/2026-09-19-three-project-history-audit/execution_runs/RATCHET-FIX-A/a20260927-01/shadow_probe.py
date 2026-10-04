import ast, sys
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
base="src/company_wiki/source_catalog/"
for rel in ["adapters/parity.py","lock.py","prompt_injection.py","store.py"]:
    tree=ast.parse(open(base+rel,encoding="utf-8").read())
    asyncs=[n.name for n in tree.body if isinstance(n,ast.AsyncFunctionDef)]
    nested=[]
    for n in tree.body:
        if isinstance(n,(ast.If,ast.Try,ast.With,ast.For,ast.While)):
            for c in ast.walk(n):
                if isinstance(c,(ast.FunctionDef,ast.AsyncFunctionDef)): nested.append(c.name)
    methods=0
    for n in ast.walk(tree):
        if isinstance(n,ast.ClassDef):
            methods+=sum(1 for c in n.body if isinstance(c,(ast.FunctionDef,ast.AsyncFunctionDef)))
    print(rel, "async_top=",asyncs, "defs_in_module_blocks=",nested, "methods=",methods)
