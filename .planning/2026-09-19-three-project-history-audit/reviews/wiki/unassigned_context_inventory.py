"""Identify paths outside communicated ownership; does not certify another reviewer's reading."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent; A=H.parent.parent
rows=json.loads((A/'inventory/scope_manifest.json').read_text(encoding='utf-8'))
out=[]; counts={}
for r in rows:
    if r['repo']!='company-wiki' or r['scope'].startswith('excluded'):continue
    p=r['path'].replace('\\','/')
    if p.startswith('docs/plans/source-catalog-worker-recovery-') or p=='docs/worker-investigation-2026-08-20.md':owner='wiki worker (completed text)'
    elif p.startswith(('docs/plans/painpoint-outcome-audit-','docs/plans/planning-sync-','docs/plans/data-lake-simplification-','assurance/fc/')):owner='root communicated scope (not certified by this inventory)'
    elif p.startswith('docs/archive/'):owner='root archive communicated scope'
    elif p.startswith(('docs/plans/portfolio-reuse-fix/','docs/plans/portfolio-reuse-automatic/','docs/plans/core-section-extraction/','docs/plans/catalog-space-remediation/')):owner='filing legacy special scope'
    elif '/' not in p or p.startswith('.mimocode/'):owner='filing legacy root scope; confirm hidden plan included'
    else:owner='ownership_not_confirmed'
    counts[owner]=counts.get(owner,0)+1
    if owner=='ownership_not_confirmed':out.append({'path':p,'lines':r['lines'],'scope':r['scope'],'inventory_owner':r.get('owner'),'note':'No full-read claim; ask root to bind owner or explicit engineering-context exclusion.'})
(H/'unassigned_engineering_context.json').write_text(json.dumps({'counts_by_communicated_owner':counts,'paths_needing_explicit_owner_or_exclusion':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'counts':counts,'paths':out},ensure_ascii=False))
