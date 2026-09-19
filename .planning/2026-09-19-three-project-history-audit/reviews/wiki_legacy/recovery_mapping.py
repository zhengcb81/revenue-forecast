from pathlib import Path
import json,difflib
HERE=Path(__file__).resolve().parent;ROOT=Path('C:/Users/郑曾波/Projects/company-wiki')
data=json.loads((HERE/'scope.json').read_text(encoding='utf-8'))
names=['.recover-task_plan-before-cw-merge-20260725-115819.md','.recover-task_plan-current-20260725-114504.md','task_plan_cw_recovery_20260725.md']
canonical=(ROOT/'task_plan.md').read_text(encoding='utf-8-sig').splitlines();mapping=[];novel=[]
for name in names:
 lines=(ROOT/name).read_text(encoding='utf-8-sig').splitlines()
 line_map={}
 for m in difflib.SequenceMatcher(None,lines,canonical,autojunk=False).get_matching_blocks():
  if m.size>=3:
   for i in range(m.size):line_map[m.a+i+1]=m.b+i+1
 for b in data['blocks']:
  if b['relative']!=name:continue
  ids=list(range(b['line_start'],b['line_end']+1))
  vals=[line_map.get(i) for i in ids]
  if all(v is not None for v in vals) and vals==list(range(vals[0],vals[0]+len(vals))):
   mapping.append(dict(b,canonical='task_plan.md',canonical_line_start=vals[0],canonical_line_end=vals[-1],mapping='exact text block within >=3-line exact run; same semantic text, retain source version identifier'))
  else:novel.append(b)
(HERE/'recovery_exact_mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'recovery_novel_blocks.json').write_text(json.dumps(novel,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(mapped=len(mapping),novel=len(novel))))
for b in novel:print('\n'+b['relative']+':'+str(b['line_start'])+'-'+str(b['line_end'])+'\n'+b['original_text'])
