"""Source-preserving linkage for full-read cards and RED records.

This does not independently assign paragraph verdicts by keyword. Each paragraph
retains the already reviewer-authored unit assessment, with specific clause
overrides in deep_clause_ledger.jsonl. Structural headings are explicit exclusions.
"""
from pathlib import Path
import json,hashlib,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
units={x['item_id']:x for x in map(json.loads,(OUT/'item_ledger.jsonl').read_text(encoding='utf8').splitlines())}
reads=json.loads((OUT/'source_read_manifest.json').read_text(encoding='utf8'))
deep=list(map(json.loads,(OUT/'deep_clause_ledger.jsonl').read_text(encoding='utf8').splitlines()))
rows=[]
for entry in reads:
 file=entry['path']
 if entry['full_read_state']!='full_read' or not file.startswith('assurance/unified_completion/receipts/'):continue
 unit=file.split('/')[3];lines=(ROOT/file).read_text(encoding='utf-8-sig').splitlines();start=None;chunks=[]
 for n,line in enumerate(lines+[''],1):
  if line.strip() and start is None:start=n
  if not line.strip() and start is not None:chunks.append((start,n-1,'\n'.join(lines[start-1:n-1])));start=None
 for begin,end,body in chunks:
  structural=all(re.fullmatch(r'\s*(?:#{1,6}\s+.*|[-_*]{3,})\s*',s) for s in body.splitlines())
  linked=[x['item_id'] for x in deep if x['source_file']==file and begin<=x['source_line']<=end]
  u=units[unit]
  rows.append({'block_id':f'RF-CARD-{len(rows)+1:05}','file':file,'line_start':begin,'line_end':end,'file_sha256':entry['sha256'],'text_sha256':hashlib.sha256(body.encode()).hexdigest(),'text':body,'source_read_state':'full_read','classification':'structure_excluded' if structural else 'semantic_obligation_linked','semantic_item_id':None if structural else unit,'deep_clause_ids':linked,'review_conclusion':None if structural else u['conclusion'],'review_reason':'Pure heading/separator; no independent technical promise' if structural else u['reason'],'assessment_scope':'Unit-level obligation disposition shared across repeated card/RED source occurrences; it does not assert that every metadata field fails when the unit verdict is contradicted. Historical RED facts are not automatically current defects; current scope and explicit overrides reside in referenced ledgers.'})
(OUT/'card_source_blocks.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf8')
print(json.dumps({'full_read_card_red_adr_documents':len({x['file'] for x in rows}),'source_blocks':len(rows),'semantic_blocks':sum(x['classification']=='semantic_obligation_linked' for x in rows),'structural_blocks':sum(x['classification']=='structure_excluded' for x in rows)},ensure_ascii=False))
