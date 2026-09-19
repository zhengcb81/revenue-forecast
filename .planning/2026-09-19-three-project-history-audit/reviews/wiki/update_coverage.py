from pathlib import Path
import json
H=Path(__file__).resolve().parent
p=H/'read_coverage.json'; x=json.loads(p.read_text(encoding='utf-8'))
b='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/'
added=['baseline/plan/'+n for n in ['task_plan.md','acceptance_thresholds.md','gate_state_machine.md','test_acceptance_plan.md','ledger_validator_contract.md','traceability_matrix.md','plan_review_findings.md','agent_review_gates.md','gate_dag.v4.json']]
added += ['v5-freeze-review-test-dag'+s+'.md' for s in ['', '-closure','-closure2','-closure3','-closure4']]
x['full_text_read']=list(dict.fromkeys(x['full_text_read']+[b+n for n in added]))
x['selected_sections_read']=[r for r in x['selected_sections_read'] if r['path'] not in x['full_text_read']]
x['semantic_assessment_records']={'ledger':'item_ledger.jsonl','test_ids':315,'dag_nodes':115,'boundary':'Each is a plan-obligation review, not runtime PASS; per-ID definition/lifecycle and reviewer-authored 36 family assessments retained. Two text/registry defects flagged separately.'}
x['uncompleted_main_clusters']=['v5 remaining execution/runbook/prompts/history and freeze-axis reviews','old worker recovery version-by-version semantic review','historical closeout conditions reconciliation']
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(x['full_text_read']))
