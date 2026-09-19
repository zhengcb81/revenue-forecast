"""Format a manually authored semantic ledger; do not infer verdicts."""
import csv, json
from pathlib import Path
p=Path(__file__).resolve().parent
rows=[json.loads(line) for line in (p/'item_ledger.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
allowed={'supported_scoped','contradicted','insufficient_evidence','not_deployed','superseded','historical_only','not_applicable'}
assert len({r['id'] for r in rows})==len(rows)
assert all(r['verdict'] in allowed for r in rows)
with (p/'item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['id','repo','path','line','promise','historical_status','historical_evidence','current_independent_evidence','verdict','recommendation','severity','scope','planning_assessment','assessment_limit']
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for r in rows:
        out={k:v for k,v in r.items() if k!='original'};out.update(r['original'])
        out={k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in out.items()}
        writer.writerow(out)
print(f'Validated and formatted {len(rows)} manually reviewed commitment records; no pending item was auto-approved.')
