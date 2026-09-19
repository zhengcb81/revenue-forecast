from pathlib import Path
import json, hashlib, difflib
H=Path(__file__).resolve().parent
W=Path('C:/Users/郑曾波/Projects/company-wiki')
B='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/'
p=H/'read_coverage.json'; x=json.loads(p.read_text(encoding='utf-8'))
new=['baseline/plan/README.md','baseline/plan/implementation_agent_prompts.md','baseline/plan/findings.md']
new += ['v5-freeze-review-sql-performance'+s+'.md' for s in ['', '-closure','-closure2','-closure3']]
new += ['v5-freeze-review-lifecycle-security'+s+'.md' for s in ['', '-closure','-closure2']]
x['full_text_read']=list(dict.fromkeys(x['full_text_read']+[B+n for n in new]))
x['selected_sections_read']=[r for r in x['selected_sections_read'] if r['path'] not in x['full_text_read']]
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[]
old=W/'docs/plans/source-catalog-worker-recovery-2026-08-22'
for a in sorted(old.glob('*.md')):
    n=a.name
    target=('baseline/history/progress.v4.md' if n=='progress.md' else 'baseline/history/plan_review_revision.v4.md' if n=='plan_review_revision.md' else 'baseline/plan/'+n)
    b=W/B/target
    ab=a.read_bytes();bb=b.read_bytes()
    at=ab.decode('utf-8-sig').splitlines();bt=bb.decode('utf-8-sig').splitlines()
    row={'old_path':a.relative_to(W).as_posix(),'baseline_path':b.relative_to(W).as_posix(),'old_lines':len(at),'baseline_lines':len(bt),'bytes_equal':ab==bb,'lines_equal':at==bt,'old_sha256':hashlib.sha256(ab).hexdigest(),'baseline_sha256':hashlib.sha256(bb).hexdigest()}
    delta=''.join(difflib.unified_diff([s+'\n' for s in at],[s+'\n' for s in bt],fromfile=row['old_path'],tofile=row['baseline_path'],n=4))
    if delta:
        out=H/'old_version_diffs'/f'{n}.diff';out.parent.mkdir(exist_ok=True);out.write_text(delta,encoding='utf-8');row['diff_path']=out.relative_to(H).as_posix();row['diff_lines']=len(delta.splitlines())
    rows.append(row)
(H/'old_version_mapping.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'full_text_read':len(x['full_text_read']),'old_versions':rows},ensure_ascii=False))
