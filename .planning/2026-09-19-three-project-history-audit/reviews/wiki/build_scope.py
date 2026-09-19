"""Inventory only: no semantic review verdicts are inferred by this script."""
import collections, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
inv = json.loads((HERE.parent.parent / 'inventory/company-wiki.json').read_text(encoding='utf-8-sig'))
groups = collections.defaultdict(list)
for entry in inv['selected']:
    path = entry['path'].replace('\\', '/')
    parts = path.split('/')
    cluster = '/'.join(parts[:3]) if path.startswith('docs/plans/') else ('web/docs' if path.startswith('web/docs/') else '/'.join(parts[:2]) if path.startswith(('docs/','assurance/')) else 'root')
    groups[cluster].append(entry)
summary = []
for cluster, entries in sorted(groups.items()):
    summary.append({'cluster': cluster, 'files':len(entries), 'unique_hashes':len({e['sha256'] for e in entries}), 'lines':sum(e['lines'] for e in entries), 'bytes':sum(e['bytes'] for e in entries)})
(HERE/'scope_inventory_summary.json').write_text(json.dumps({'kind':'inventory_not_review','summary':summary},ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
mapping=[]
for entry in inv['selected']:
    mapping.append({'path':entry['path'], 'sha256':entry['sha256'], 'duplicate_paths':entry['duplicate_paths'], 'scope_candidate':'business_context' if entry['path'].replace('\\','/').startswith(('web/docs/','companies/')) else 'engineering_candidate', 'review_status':'pending_semantic_review'})
(HERE/'file_coverage_pending.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':len(mapping),'unique_hashes':len({e['sha256'] for e in mapping}),'clusters':len(summary)},ensure_ascii=False))
