from pathlib import Path
import re,json
W=Path('C:/Users/郑曾波/Projects/company-wiki/docs/plans/source-catalog-worker-recovery-v5-2026-09-03')
for p in sorted(W.glob('*review*.md')):
    out=[]
    for n,s in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if not s.startswith('|'):continue
        first=s.split('|')[1].strip().replace('**','')
        if re.match(r'(?:TST-|SQL-|LIF-|HDD-|HDS-|NEW-|[FGH]\d)',first):out.append((n,first))
    print(p.name,json.dumps(out,ensure_ascii=False))
