"""Read-only metadata checks for engineering context; business bodies are not fact checked."""
from pathlib import Path
import re,json,hashlib
H=Path(__file__).resolve().parent;W=Path('C:/Users/郑曾波/Projects/company-wiki')
p=W/'docs/contaminated_entries_review.md';t=p.read_text(encoding='utf-8').splitlines()
groups=[]
for n,s in enumerate(t,1):
    m=re.fullmatch(r'## (.+) \((\d+) 条污染条目\)',s)
    if m:groups.append({'line':n,'group':m[1],'declared_count':int(m[2])})
links=[]
for n,s in enumerate(t,1):
    for q in re.findall(r'\[来源\]\(([^)]+)\)',s):
        if '://' in q:continue
        target=(p.parent/q).resolve()
        links.append({'line':n,'starts_parent3':q.startswith('../../../'),'within_current_repo':target.is_relative_to(W.resolve())})
out={'scope':'engineering headers/counts/link-boundary only; no statement that all removed business entries were fact-checked or should be deleted',
 'path':p.relative_to(W).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'lines':len(t),'groups':groups,'declared_sum':sum(r['declared_count'] for r in groups),'pollution_source_heading_count':sum(s.startswith('### 污染源:') for s in t),'relative_source_link_count':len(links),'outside_repo_links_by_current_document_base':sum(not q['within_current_repo'] for q in links),'source_link_samples':links[:3]+links[-3:],
 'action_items_arithmetic':{'before':15674,'claimed_removed':5038,'expected_after':15674-5038,'claimed_after':10642,'difference':10642-(15674-5038)},
 'quality_report_sum':{'pages':91+25+3,'entries':3166+6893+583},
 'gate_weight_disagreement':{'GATE_SYSTEM_md_168_172':[30,25,20,15,10],'user_manual_273_277':[25,25,20,15,15],'bound':'historical documents conflict; neither accepted as present investment adjudication'},
 'scope_count_reconciliation':{'selected':373,'excluded_business':126,'engineering_or_history':247,'web_context_retained':['web/docs/index.md','web/docs/tags.md','web/docs/产业链导航.md','web/docs/图谱.md']}}
(H/'engineering_context_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='groups'},ensure_ascii=False))
