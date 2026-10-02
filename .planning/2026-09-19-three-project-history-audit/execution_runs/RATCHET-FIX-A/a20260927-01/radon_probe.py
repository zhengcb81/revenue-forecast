import sys
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
from radon.complexity import cc_visit
from pathlib import Path
base=Path("src/company_wiki/source_catalog")
for rel in ["adapters/parity.py","lock.py","prompt_injection.py","store.py"]:
    text=(base/rel).read_text(encoding="utf-8")
    cs=cc_visit(text)
    cs.sort(key=lambda c:-c.complexity)
    print(rel, [(c.complexity, c.name) for c in cs[:3]])
