import importlib.util, sys, types
from pathlib import Path

# Register fake parent packages
cw = types.ModuleType("company_wiki")
cw.__path__ = []
sys.modules["company_wiki"] = cw
sc = types.ModuleType("company_wiki.source_catalog")
sc.__path__ = []
sys.modules["company_wiki.source_catalog"] = sc

base = Path(r"""C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-06-B\a20260919-01""")
spec = importlib.util.spec_from_file_location(
    "company_wiki.source_catalog.processing_demand",
    base / "iso" / "cw" / "src" / "company_wiki" / "source_catalog" / "processing_demand.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["company_wiki.source_catalog.processing_demand"] = mod
spec.loader.exec_module(mod)

DemandQueue = mod.DemandQueue
q = DemandQueue()
q.enqueue(key='k1', kind='review', now=0.0)
q.enqueue(key='k2', kind='review', now=1.0)
c = q.claim(owner='w1', now=2.0)
print(f'claimed: key={c.key}, status={c.status}, owner={c.lease_owner}')
d = q.complete(demand_id=c.demand_id, owner='w1', now=3.0)
print(f'completed: status={d.status}')
snap = q.snapshot()
print(f'snapshot: {len(snap)} demands, statuses={[s.status for s in snap]}')
print('ZR-507 direct test: PASS')
