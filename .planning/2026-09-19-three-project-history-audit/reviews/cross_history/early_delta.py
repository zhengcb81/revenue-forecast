"""Map the archived copies onto already fully read root planning texts.

Only Markdown heading depth is normalized; all prose bytes after UTF-8 decode
must be equal. Unmatched source ranges are emitted for explicit human reading.
"""
from pathlib import Path
import difflib
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def norm(s):
    return re.sub(r'^#{1,6}\s+', '', s)
out=[]
for base, archived in [('findings.md','audit_review/findings.md'),('progress.md','audit_review/progress.md')]:
    a=(ROOT/base).read_text(encoding='utf-8-sig').splitlines()
    b=(ROOT/archived).read_text(encoding='utf-8-sig').splitlines()
    row={'read_base':base,'archive':archived,'base_sha256':hashlib.sha256((ROOT/base).read_bytes()).hexdigest(),
         'archive_sha256':hashlib.sha256((ROOT/archived).read_bytes()).hexdigest(),'matches':[],'novel_ranges':[]}
    for tag,a1,a2,b1,b2 in difflib.SequenceMatcher(a=list(map(norm,a)),b=list(map(norm,b)),autojunk=False).get_opcodes():
        if tag=='equal': row['matches'].append({'base':[a1+1,a2],'archive':[b1+1,b2]})
        elif b1!=b2: row['novel_ranges'].append({'range':[b1+1,b2],'text':'\n'.join(b[b1:b2])})
    out.append(row)
(HERE/'early_delta_mapping.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for row in out:
    print(row['archive'])
    for delta in row['novel_ranges']:
        print(f"LINES {delta['range'][0]}–{delta['range'][1]}")
        print(delta['text'])
