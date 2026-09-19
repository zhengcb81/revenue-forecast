"""Read-only discovery of engineering planning histories; output only in this plan."""
from pathlib import Path
import subprocess, json, hashlib, re
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
PROJECTS = OUT.parents[2]
SEED_NAME = re.compile(r'(task[_-]?plan|findings|progress|implementation|audit|review|closure|acceptance|execution|receipt|gate|backlog|completion|plan)', re.I)
PLAN_PARTS = {'plans', '.planning', 'planning', 'audit_review', 'review_audit', 'assurance', 'drills'}
SKIP = ['.git/**', '.venv/**', 'venv/**', 'node_modules/**', '__pycache__/**', '.pytest_cache/**']

def main():
    dest=OUT/'inventory'; dest.mkdir(exist_ok=True)
    total=[]; errors=[]; baseline={}
    for repo in ['revenue-forecast','filing-fetch','company-wiki']:
        root=PROJECTS/repo
        cmd=['rg','--files','--hidden','--no-ignore','-g','*.md']
        for pattern in SKIP: cmd += ['-g','!'+pattern]
        p=subprocess.run(cmd,cwd=root,capture_output=True,encoding='utf-8',errors='replace')
        errors.append({'repo':repo,'command':cmd,'exit':p.returncode,'stderr':p.stderr})
        names=sorted(set(p.stdout.splitlines()))
        records=[]; unselected=[]
        for rel in names:
            path=root/rel
            if path.is_relative_to(OUT): continue
            parts={s.lower() for s in Path(rel).parts}
            reason=[]
            if parts&PLAN_PARTS: reason.append('planning_or_assurance_directory')
            if SEED_NAME.search(path.stem): reason.append('planning_filename')
            if 'docs' in parts: reason.append('project_documentation_context')
            if len(Path(rel).parts)==1: reason.append('project_root_document')
            if not reason:
                unselected.append(rel);continue
            try:
                raw=path.read_bytes(); content=raw.decode('utf-8-sig')
            except (OSError,UnicodeError) as exc:
                errors.append({'repo':repo,'path':rel,'error':str(exc)});continue
            sha=hashlib.sha256(raw).hexdigest()
            records.append({'repo':repo,'path':rel,'absolute_path':str(path),'sha256':sha,
                            'bytes':len(raw),'lines':len(content.splitlines()),'selection':reason,
                            'unit_ids':sorted(set(re.findall(r'\b(?:FC|ZR|WR|WU|GP|RF|FF|CW|R|P|EX|UJ|LT|B|N)[- ]?\d+(?:[-.][A-Za-z0-9]+)*\b',content)))})
        byhash={}
        for r in records: byhash.setdefault(r['sha256'],[]).append(r['path'])
        for r in records: r['duplicate_paths']=byhash[r['sha256']]
        report={'repo':repo,'root':str(root),'discovered_markdown':len(names),'selected':records,
                'unselected_paths':unselected,'dedup_unique':len(byhash)}
        (dest/f'{repo}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        total+=records
        baseline[repo]={}
        for name,args in [('head',['rev-parse','HEAD']),('status',['status','--short']),('diff_stat',['diff','--stat'])]:
            p=subprocess.run(['git','-C',str(root),*args],capture_output=True,encoding='utf-8',errors='replace')
            baseline[repo][name]={'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
        print(json.dumps({'repo':repo,'markdown':len(names),'selected':len(records),'unique':len(byhash),'selected_bytes':sum(r['bytes'] for r in records)},ensure_ascii=False))
    summary={'created_utc':datetime.now(timezone.utc).isoformat(),'method':'Recursive rg inventory, then filename/directory selection. Selection is not semantic review; unselected paths retained for coverage challenge.','records':total,'errors':errors}
    (dest/'all_documents.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'repo_baseline.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
