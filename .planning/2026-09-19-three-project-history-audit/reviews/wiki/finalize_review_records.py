"""Explicit reviewer-authored record updates; no candidate auto-classification."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
f=p/'item_ledger.jsonl'
rows=[json.loads(s) for s in f.read_text(encoding='utf-8').splitlines() if s.strip()]
anchors={'WIKI-V5-01':25,'WIKI-V5-02':36,'WIKI-V5-05':62}
for row in rows:
    if row['id'] in anchors:
        row['original']['line']=anchors[row['id']]
new={
 'id':'WIKI-ROOT-01',
 'original':{'repo':'company-wiki','path':'config/source_catalog.yaml','line':30},
 'promise':'ZR-409：未来根仅CONFIG ONLY + registered sidecar adapter加入，无产品代码修改',
 'historical_status':'第四根配置说明/能力承诺',
 'historical_evidence':'future_lake以明确root_id和sidecar_filing_v1配置；该例本身只覆盖第四个指定根',
 'current_independent_evidence':'scripts/config_doctor.py:80-99硬编码_ALLOWED_DIRECTORY_ROOTS={dropbox_stock,future_lake}，任何第五个directory根ID即使合法adapter/read_only/reusable仍被标problem；本轮静态审查，未创建第五根或运行扫描',
 'verdict':'contradicted',
 'recommendation':'泛化承诺应限缩为两个白名单root，或后续按统一RootPolicy能力验证替代名称白名单；保留明确授权/读写边界。新增第五根隔离测试才能宣称通用扩展。'
}
rows=[r for r in rows if r['id']!=new['id']]+[new]
f.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')

coverage={
 'scope':'v5/recovery/production; manual semantic review coverage, not full repository completion',
 'full_text_read':[
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/task_plan.md',
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/README.md',
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/v5-freeze-record.md',
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/v5-version-contract.md',
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/v5-version-contract-review-rev4.md',
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/reviews/import-review-2026-09-03.md',
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/reviews/old-plan-retirement-result.md',
  'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/v5-freeze-review-lifecycle-security-closure3.md'
 ],
 'selected_sections_read':[
  {'path':'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/baseline/plan/task_plan.md','lines':['180-213','601-608','790-829'],'remaining':'other promises pending semantic review'},
  {'path':'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/v5-freeze-review-handover-state.md','lines':['1-32'],'remaining':'truncated tail not claimed complete'},
  {'path':'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/progress.md','lines':['1-101'],'remaining':'tail only partial tool display'},
  {'path':'docs/plans/source-catalog-worker-recovery-v5-2026-09-03/baseline/history/v4-freeze-integrity-incident-2026-09-03.md','lines':['1-28','104-178'],'remaining':'per-file table not fully read'},
  {'path':'docs/contaminated_entries_review.md','lines':['1-18','tail20'],'remaining':'business rows context; full removal/categorization validation delegated'}
 ],
 'metadata_only_not_semantic_review':['51 normative file hashes/size','373 selected path/byte/hash mapping','keyword discovery excerpts from other plans'],
 'delegated_to_root_or_other_reviewer':['root/CW/archive/portfolio/core/catalog-space to history_filing','painpoint/R4/FC to root','nested snapshot to root'],
 'uncompleted_main_clusters':['v5 baseline detailed execution/acceptance/agent gates and 115 DAG nodes/315 test IDs individually','remaining SQL/test-DAG/lifecycle historical review closure chains','legacy worker recovery full body and version deltas']
}
(p/'read_coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
