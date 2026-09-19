"""Explicit reviewer full-read log; extraction and checklist reading are not full-read."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
FULL_CARDS=set('CA-001 CA-002 CA-003 CA-004 CA-101 CA-102 CA-103 CA-104 CA-106 CA-107 CA-108 CA-109 CA-201 CA-202 CA-203 CA-204 CA-205 CA-206 CA-301 CA-302 CA-305'.split())
FULL_CARDS.update(f'ZR-{n:03}' for n in [1,2,3,4,*range(101,106),*range(201,207),*range(301,308),*range(401,410),*range(501,511),*range(601,612),701,706,707,708,709,711,713,801,802,803,804])
FULL_CARDS.update('CA-303 CA-304 CA-306'.split())
FULL_CARDS.update(f'ZR-{n:03}' for n in [702,703,704,705,710,712,805,806,*range(901,908),*range(1001,1010),*range(1101,1106)])
FULL_FILES=set('''IMPLEMENTATION_PLAN.md
PLANNING_STATUS.md
review_audit/findings.md
docs/buy_side_model_audit_2026-09-18.md
docs/buy_side_review_2026-09-18.md
audit_review/2026-09-18_real_company_skill_audit/AUDIT_REPORT.md
audit_review/2026-08-13_three_repo_completion_rebaseline_plan/completion_audit.md
audit_review/2026-08-13_three_repo_completion_rebaseline_plan/legacy_fc_status_registry.md
audit_review/2026-08-13_three_repo_completion_rebaseline_plan/legacy_transition_matrix.md
audit_review/2026-08-09_full_completion_assurance_plan/work_unit_registry.md
audit_review/2026-08-09_full_completion_assurance_plan/legacy_plan_disposition.md
audit_review/2026-08-13_zijin_data_lake_remediation_plan/work_unit_registry.md
assurance/runs/2026-09-11_r4-phase-b/task_plan.md
assurance/runs/2026-09-11_r4-phase-b/r4-final-status.md'''.splitlines())
ROOT_ASSIGNED=set('''findings.md
progress.md
audit_review/findings.md
audit_review/progress.md
audit_review/2026-08-08_adversarial_plan/findings.md
audit_review/2026-08-08_adversarial_plan/progress.md'''.splitlines())
PARTIAL={'AUDIT_REPORT.md':'lines 1-155','FILING_FETCH_AUDIT.md':'lines 1-120','task_plan.md':'all 567 checkbox leaves + explanatory context; not all non-checkbox prose','audit_review/2026-08-09_data_lake_refactor_plan/task_plan.md':'all 74 WU blocks and global requirements, not all remaining prose','audit_review/2026-08-13_three_repo_completion_rebaseline_plan/completion_assurance_registry.md':'all CA original obligations; introductory text not fully confirmed'}
def main():
 from r4_read_reviews import REVIEWS
 FULL_FILES.update(REVIEWS)
 from additional_read_reviews import REVIEWS as ADDITIONAL_REVIEWS
 FULL_FILES.update(ADDITIONAL_REVIEWS)
 FULL_FILES.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'assurance/fc').rglob('*.md'))
 for name in ['2026-08-09_data_lake_refactor_plan','2026-08-09_full_completion_assurance_plan','2026-08-12_zijin_skill_run_audit','2026-09-18_real_company_skill_audit']:
  ROOT_ASSIGNED.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'audit_review'/name).rglob('*.md'))
 FULL_FILES.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'assurance/unified_completion/receipts').glob('*/red/RED.md'))
 FULL_FILES.add('assurance/unified_completion/receipts/ZR-610/adr_mining_accounting.md')
 scope=json.loads((OUT/'document_scope.json').read_text(encoding='utf8'))
 units=json.loads((OUT/'unit_ledger.base.json').read_text(encoding='utf8'))
 for u in units:
  if u['item_id'] in FULL_CARDS and u['card_file']:
   FULL_FILES.add(u['card_file'].replace('\\','/'))
 checkbox_files={x['source_file'].replace('\\','/') for x in map(json.loads,(OUT/'checklist_ledger.jsonl').read_text(encoding='utf8').splitlines())}
 result=[]
 for x in scope:
  path=x['path'].replace('\\','/')
  state='full_read' if path in FULL_FILES else 'partial_read' if path in PARTIAL or path in checkbox_files else 'not_full_read'
  owner='root' if path in ROOT_ASSIGNED else 'history_filing' if any(n in path for n in ['2026-08-13_three_repo_completion_rebaseline_plan','2026-08-13_zijin_data_lake_remediation_plan']) else 'history_revenue'
  result.append({'path':path,'sha256':x['sha256'],'lines':x['lines'],'full_read_state':state,'owner':owner,'reading_note':'Full text actually read; conclusions are separate item ledgers' if state=='full_read' else PARTIAL.get(path,'All checkbox contexts read, remaining prose pending' if path in checkbox_files else 'Not certified read; mechanical extraction is not review'),'semantic_audit_complete':False})
 (OUT/'source_read_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 counts={s:sum(x['full_read_state']==s for x in result) for s in ['full_read','partial_read','not_full_read']}
 coverage={'document_count':len(scope),'document_lines':sum(x['lines'] for x in scope),'primary_units':{'CA':25,'ZR':92,'FC':71,'WU':74},'primary_semantic_dispositions':262,'checklist_leaves':776,'checklist_semantic_groups':93,'checklist_pending':0,'registered_models_reviewed':31,'additional_wiki_fc_full_read_documents':29,'source_read_states':counts,'root_assigned_documents':sum(x['owner']=='root' for x in result),'caution':'262 unit-level sufficiency conclusions, 776 checkbox leaves and 31 models are reviewed. These do not imply all history prose reviewed. source_read_manifest.json reports full/partial reading conservatively; whole-history audit remains in progress.'}
 (OUT/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(coverage,ensure_ascii=False))
if __name__=='__main__':main()
