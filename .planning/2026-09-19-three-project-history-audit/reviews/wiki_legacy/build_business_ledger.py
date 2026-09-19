"""Engineering telemetry review per event and exact occurrence; no financial fact audit."""
from pathlib import Path
import json,csv,re,collections,hashlib
P=Path(__file__).resolve().parent;ROOT=Path(r'C:/Users/郑曾波/Projects/company-wiki')
events=json.loads((P/'business_log_events.json').read_text(encoding='utf-8'));blocks=json.loads((P/'scope.json').read_text(encoding='utf-8'))['blocks']
rules={
'query':('historical_only','879 exact repeated test-question save events and one concept-page save are historical side effects, not independent research evidence. Current test explicitly checks temp-root log, so historical contamination does not establish current test escape.','tests/unit/test_query.py217–251; current test_wiki scope; no production replay'),
'ingest':('historical_only','Input/output counts and topic fanout do not prove source fidelity; no immutable source/attempt/code hash or raw stdout is linked. Mixed download lines are a separate operation, not proof the ingest succeeded.','old audit_worklog and cross_verify report; source-only later retires research writer'),
'ingest_v2':('historical_only','LLM ingest files/entries/assessments telemetry lacks identity, source binding, model call receipts and actual consumer outcome. Kept per original run, not a proof of qualitative research accuracy.','47 dated occurrences with distinct quantities retained; old research lifecycle retired'),
'lint':('historical_only','Each event severity totals and every detail line retained; zero error only means this linter scope. Missing/broken links, generic-name discovery and candidate contradictions do not validate financial truth. Details omit INFO and often exact page context.','all 22 numeric lints independently count ERROR/WARNING detail rows; specific broken_link/config/frontmatter/cross_refs archetypes reviewed'),
'scheduler':('historical_only','Cycle completed is control flow completion, not all tasks successful: old Apr22 repeatedly processed files with zero added entries and 1–5 errors; no attempt ID lets adjacent concurrent events correlate reliably.','original Apr22 7075–7194; current source-only different worker reviewed separately'),
'collect_news':('historical_only','Per-company sums match all scheduler collection headers; counts/duplicates do not prove correct identity, relevance, persistence or downstream use; no URL/hash manifest in this telemetry.','22 scheduler sum checks; remaining five older aggregate-only receipts'),
'enrich':('superseded','Old assessment/judgment/compression write counts are retired research functionality, not current source platform acceptance; compression size reduction does not demonstrate preserved evidence.','AGENTS BOUNDARY-0; original dated counts retained'),
'distill':('superseded','Industry distill completion is retired research output; no accuracy or independent input evidence follows from count.','AGENTS BOUNDARY-0'),
'evolve':('superseded','Schema evolution measures metrics and generated character count, not correctness of suggested actions. CLAUDE current stale suggestions illustrate lifecycle handoff risk.','CLAUDE148–172; context ledger'),
'batch_download':('historical_only','119/36 file count alone lacks company/period/provider/path/hash and reusable-index receipt; no claim of present availability.','original Apr12 two events; filing current contract requires more'),
'download_reports':('historical_only','88 files one company only aggregate historical telemetry; lacks immutable source IDs and hashes; no re-download in audit.','original Apr12 event43'),
'consolidate':('superseded','33 pages compressed from17765 to9538 is size telemetry only; does not establish retention of citations or fact quality; old research writer retired.','BOUNDARY-0; original log119'),
'init':('historical_only','Project setup event gives original intent and filenames, not verified ongoing deployment or research accuracy.','root/archive versions are separately reviewed'),
'enrich_wiki --all':('superseded','Explicitly running in background, not completed; research assessment writer later retired.','original log2780; BOUNDARY-0'),
}
checks=[]
for i,e in enumerate(events,1):
 v,reason,evidence=rules[e['kind']];e.update(item_id=f'WIKI-LEGACY-EVENT-{i:04d}',reviewer='history_filing',verdict=v,reason=reason,current_evidence=evidence,financial_content_reviewed=False)
 if e['kind']=='collect_news' and 'scheduler采集' in e['message']:
  expected=int(re.search(r'采集 (\d+)',e['message']).group(1));actual=sum(int(x) for x in re.findall(r'\+(\d+)', '\n'.join(e['body'])))
  checks.append(dict(event_id=e['item_id'],check='company_sum',expected=expected,actual=actual,match=expected==actual))
 if e['kind']=='lint' and re.match(r'\d+ errors',e['message']):
  nums=list(map(int,re.findall(r'\d+',e['message'])));counts=collections.Counter(re.search(r'\[(\w+)\]',s).group(1) for s in e['body'] if re.search(r'\[(\w+)\]',s))
  checks.append(dict(event_id=e['item_id'],check='lint_severity_count',header=nums,detail=dict(counts),errors_match=nums[0]==counts['ERROR'],warnings_match=nums[1]==counts['WARNING'],info_details_omitted=nums[2]>0 and counts['INFO']==0))
 if e['file']=='log_2026-04-23.md' and e['start']==2774:
  e.update(verdict='insufficient_evidence',reason='Full5397/26316 event says cleanup2704 broken entries then zero errors; historical predecessor2637 warning cleanup may be legitimate, but no before/after archive/source reconciliation proves no-loss. Output lint zeros alone cannot close this contract.')
(P/'business_event_ledger.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),encoding='utf-8')
rows=[];structure=[];pending=[]
for b in blocks:
 if b['relative'] not in ['log.md','log_2026-04-23.md']:continue
 ev=next((e for e in events if e['file']==b['relative'] and e['start']<=b['line_start']<=e['end']),None)
 if not ev:structure.append(b);continue
 rows.append(dict(b,item_id=f'WIKI-LEGACY-BIZ-{len(rows)+1:04d}',event_id=ev['item_id'],reviewer='history_filing',verdict=ev['verdict'],historical_claim=b['original_text'],historical_evidence_scope='原事件工程遥测和证据充足性；重复同文本逐版本保留，未逐个复核投资事实',current_evidence=ev['current_evidence'],reason=ev['reason'],recommendation='用run/source/code/config hash与机器状态链接真实消费结果，区分fixture日志；旧投资writer不恢复'))
(P/'business_item_ledger.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in rows),encoding='utf-8')
with (P/'business_item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=dict(files=2,events=len(events),blocks_reviewed=len(rows),structural=len(structure),pending=len(pending),scope='event engineering telemetry, not financial content',event_kinds=dict(collections.Counter(e['kind'] for e in events)),verdicts=dict(collections.Counter(e['verdict'] for e in rows)),checks=checks)
for name,d in [('business_coverage',summary),('business_structural_exclusions',structure),('business_pending',pending)]:
 (P/(name+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(events),len(rows),len(structure),len(pending), 'count_check_failures',sum(c.get('match',c.get('errors_match',True) and c.get('warnings_match',True)) is False for c in checks))
