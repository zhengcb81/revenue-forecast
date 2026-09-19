from pathlib import Path
import json
H=Path(__file__).resolve().parent
W=Path('C:/Users/郑曾波/Projects/company-wiki/docs/plans')
O=W/'source-catalog-worker-recovery-2026-08-22'
B=W/'source-catalog-worker-recovery-v5-2026-09-03/baseline/plan'
out={}
for file,key in [('test_id_registry.v4.json','tests'),('gate_dag.v4.json','nodes')]:
    a=json.loads((O/file).read_text(encoding='utf-8-sig'));b=json.loads((B/file).read_text(encoding='utf-8-sig'))
    am={r['id']:r for r in a[key]};bm={r['id']:r for r in b[key]}
    changes=[{'id':i,'old':am[i],'baseline':bm.get(i)} for i in am if am[i]!=bm.get(i)]
    out[file]={'old_count':len(am),'baseline_count':len(bm),'unchanged_ids':[i for i in am if am[i]==bm.get(i)],'changes':changes,'added_ids':[i for i in bm if i not in am],'other_root_changes':{k:{'old':a.get(k),'baseline':b.get(k)} for k in a|b if k!=key and a.get(k)!=b.get(k)}}
(H/'old_json_semantic_diff.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for f,v in out.items():
    print(f, 'old',v['old_count'],'baseline',v['baseline_count'],'unchanged',len(v['unchanged_ids']),'added',v['added_ids'])
    for c in v['changes']:print(json.dumps(c,ensure_ascii=False))
    print('OTHER',json.dumps(v['other_root_changes'],ensure_ascii=False))
