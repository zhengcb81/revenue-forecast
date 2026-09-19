"""Human dispositions of the 16 fully read RF FC source documents."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
REVIEWS={
'FC-1001/00_wu_card.md':('supported_scoped','Three temporary roots, preseeded v2 artifacts and small fixture producer are a useful deterministic asset; no real-market capture or complete production pipeline is evidenced. Preserve corruption cases individually; fixture golden is not financial truth.'),
'FC-1003/00_wu_card.md':('insufficient_evidence','Coverage is the union of SCENARIO docstrings and accepted-owner receipt metadata, with waivers for missing owners. This proves a mapping, not that 95 live scenarios executed or preserved the original success conditions. Require execution IDs and archived observations per scenario.'),
'FC-1005/critical_mutation_evidence.md':('supported_scoped','The evidence table explicitly reuses earlier receipts and separately records the latest-entry mutation on 8/12. Reused mutation descriptions are not independent current reruns; keep per-class provenance and do not inflate kill counts.'),
'FC-1202/00_wu_card.md':('supported_scoped','Interpretation A centralizes explicit config and doctor checks; runtime dayu containment deliberately remains R4 backlog. This authorized boundary is valid and does not prove every production root policy was replaced.'),
'FC-1202/REVIEWER_REPORT.md':('supported_scoped','Reviewer found ordering-dependent negative evidence and measured 31 versus claimed 30 tests, used a Dropbox-present baseline to distinguish outcomes, and retained seven base RED cases. Rename-to-ImportError mutation is weaker than semantic routing change; focused/full suites support the declared config scope only.'),
'FC-1203/00_wu_card.md':('superseded','Original deletion list includes evaluate_candidate; later wiki review explicitly retains its live approved test use. Original delete-all wording must not be conflated with revised accepted cleanup. Extractive summarizer registration/schema/ISO fixes are separate functional obligations.'),
'FC-1204/00_wu_card.md':('supported_scoped','Branch coverage floors, changed-symbol complexity and critical-path typing are maintainability guardrails. They cannot independently prove root routing, natural cycles or economic forecast accuracy; frozen table amendments require explicit review.'),
'FC-1204/REVIEWER_REPORT.md':('supported_scoped','r1 independently rejected unreproducible mypy=0 and false mutation-kill claims; r2 fixed type commands but introduced E402; r3 accepted after Ruff fixes. Golden identity supports behavior preservation. Some stale receipt triplets/baselines remained info, so acceptance did not guarantee every receipt field was true. Do not erase these successful catches or copy their now-fixed errors as current.'),
'FC-1205/00_wu_card.md':('insufficient_evidence','The two named GBK sites have specific RED/GREEN requirements. PORT-03 first requires actual Linux CI run plus definition, but step 5 reduces evidence to ubuntu-latest definitions. Definition alone is not execution; exact run URL/head/result remains needed.'),
'FC-1205/REVIEWER_REPORT.md':('supported_scoped','Clean baseline/result, no encoding env override and reverse-edit kills give substantive evidence for two-site UTF8 fixes. Reviewer discovers a third sync_installations warning site and canonical sibling-layout dependency, both explicitly outside closure. PORT-03 was accepted as workflow-definition evidence, weaker than original actual-run requirement.'),
'FC-904/03_change_contract.md':('supported_scoped','Production prepare_source calls the imported-DAG selector and emits desired role closure; contract forbids writes and adds no producer execution. producer_events in this receipt is a plan, so parser/LLM=0 can coexist with missing artifacts and must not count as successful regeneration.'),
'FC-904/REVIEWER_REPORT.md':('supported_scoped','11 focused tests and three semantic mutation kills support selector behavior, independently repeated in current 31-pass targeted log. Reviewer measured 36 versus claimed 38 and full-suite 384+12 environmental failures versus claimed396pass, yet accepted scope. Selector wiring is real; downstream artifact production remains unproven.'),
'Phase-13/00_wu_card.md':('insufficient_evidence','Taxonomy literals, incremental scan errors, resolver SLO and capacity/concurrency are four separate claims. Repeated unchanged errors should not count as new incidents, but availability/freshness and unseen roots need independent denominators. Three-sample latency and 25 fixture drills do not prove production saturation or complete work.'),
'Phase-13/REVIEWER_REPORT.md':('supported_scoped','Reviewer independently measured taxonomy/scan-health and caught decorative latest mode plus parent-only RSS, while still accepting with follow-up. Current tools/slo_probe.py now emits latest_as_of, so that old issue is fixed. Current code still ignores resolver return codes and measures children only after blocking subprocess.run finishes; RSS falls back to parent and fast failed queries can pass. Static current evidence, not a production run.'),
'Phase-14/00_wave_ledger.md':('insufficient_evidence','R1/R8 combined switch and rollback, R2 observation, R3-R7 cited cohorts and blocked R9 are distinct states. EVIDENCE does not mean every original rollout step or natural cycle completed. Last paragraph still calls R1/R3-R5/R8 blocked after table marks applied/evidence: inconsistent snapshot cannot be a single authoritative completion report.'),
'Phase-14/01_r9_packet.md':('historical_only','Deletion packet is explicitly conditional on two natural 24h zero-hit windows; expected 8/15 time is not observed proof. Later R9 disposition must determine live deletion. Listed imports/CLI/flag removals and restore-mutation requirements remain individual obligations, not completed by preparing RED tests.')}
def main():
 rows=[];blocks=[]
 for rel,(verdict,reason) in REVIEWS.items():
  p=ROOT/'assurance/fc'/rel; lines=p.read_text(encoding='utf-8-sig').splitlines(); source=p.relative_to(ROOT).as_posix()
  row={'review_id':'RF-FC-DOC-'+str(len(rows)+1).zfill(3),'source_file':source,'start_line':1,'end_line':len(lines),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'full_text_read':True,'conclusion':verdict,'reason':reason,'current_evidence':['item_ledger.jsonl','logs/targeted_tests.txt','tools/slo_probe.py (current full source read)']}
  rows.append(row)
  i=0
  while i<len(lines):
   if not lines[i].strip():i+=1;continue
   start=i
   while i<len(lines) and lines[i].strip():i+=1
   text='\n'.join(lines[start:i]); structural=all(t.startswith('#') or set(t.strip())<=set('-| :') for t in lines[start:i])
   blocks.append({'source_file':source,'start_line':start+1,'end_line':i,'text':text,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'review_id':row['review_id'],'disposition':'structural_navigation' if structural else 'reviewed_in_document_context','document_conclusion':verdict,'reason':reason,'caution':'Shared conclusion qualifies this document scope; it does not turn every individual historical metadata field into a present failure.'})
 (OUT/'rf_fc_document_ledger.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf8')
 (OUT/'rf_fc_source_blocks.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in blocks)+'\n',encoding='utf8')
 print(len(rows),len(blocks))
if __name__=='__main__':main()
