"""Index source blocks. This extraction never assigns a review verdict."""
from pathlib import Path
import hashlib, json, re

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1]
manifest = json.loads((PLAN / 'inventory/scope_manifest.json').read_text(encoding='utf-8'))
rows = [x for x in manifest if x['repo'] == 'company-wiki' and any(
    part in x['path'].replace('\\', '/') for part in ('painpoint-outcome-audit-2026-09-05/', 'planning-sync-2026-09-04/'))]
blocks = []
for row in rows:
    path = Path(row['absolute_path'])
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    start, current, fence, heading = 0, [], False, ''
    def flush():
        global current
        if current:
            value = '\n'.join(current)
            if not re.fullmatch(r'[-| :]+', value.strip()):
                blocks.append({'source_file': str(path), 'relative': row['path'].replace('\\','/'),
                    'line_start': start, 'line_end': start + len(current) - 1,
                    'original_text': value, 'heading': heading, 'file_sha256': row['sha256'],
                    'review_status': 'pending'})
            current = []
    for n, line in enumerate(lines, 1):
        if line.startswith('```'):
            if not fence: flush(); start = n
            current.append(line); fence = not fence
            if not fence: flush()
            continue
        if fence: current.append(line); continue
        if not line.strip(): flush(); continue
        if re.match(r'^\s*(?:#+\s|[-*]\s|\d+\.\s|\|)', line):
            flush(); start = n
        elif not current: start = n
        if line.startswith('#'): heading = line
        current.append(line)
    flush()
(HERE / 'source_blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding='utf-8')
(HERE / 'files.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'files': len(rows), 'blocks_pending_review': len(blocks)}, ensure_ascii=False))
