import importlib.util, sys
sys.stdout.reconfigure(encoding="utf-8",errors="backslashreplace")
spec=importlib.util.spec_from_file_location("rat", r"C:\Users\郑曾波\Projects\company-wiki\tests\contract\test_fc1204_complexity_ratchet.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from pathlib import Path
base=Path(r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog")
for rel in ["adapters/parity.py","lock.py","prompt_injection.py","store.py"]:
    p=base/rel
    print(rel, m._max_complexity(p.read_text(encoding="utf-8")), "frozen=", m.FROZEN_MAX.get(rel))
print("FROZEN_MAX=", m.FROZEN_MAX)
