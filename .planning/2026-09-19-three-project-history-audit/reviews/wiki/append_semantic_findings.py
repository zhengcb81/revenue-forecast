"""Reviewer-authored findings; no inferred review/PASS from keyword extraction."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent
p='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/'
records=[
 {'id':'WIKI-V5-SEM-01','original':{'repo':'company-wiki','path':p+'baseline/plan/test_acceptance_plan.md','line':609},'promise':'G11J必须验证WRITE-F01/WRITE-F02，RQ-056还映射G10R；注册表机械展开全部逐ID生命周期','historical_status':'v5 freeze accepted; inherited planning clauses, not implementation PASS','historical_evidence':'v5-freeze-review-test-dag-closure4.md:13,46,56；315 ID/115节点检查通过，但明确未做导入内容级语义审查。','current_independent_evidence':'test_id_registry.v4.json:4352/4377的revalidate_at只有G11B-A2/A3/BP/BFnn/G12A，不含G11J/G10R；traceability_matrix.md:105,215-227和test_acceptance_plan.md:609明列义务；当前51文件hash与manifest一致。JRN-S01/2/3未被明示为替代WRITE-F01/2。','verdict':'contradicted','severity':'P2','scope':'规划正文-注册表同步；不是已发生生产journal失败','recommendation':'后续新revision明确G11J崩溃注入的测试义务：补准确逐ID生命周期或显式撤换正文ID并说明等价覆盖；增加Gate×Test关系校验，不只token存在检查。'},
 {'id':'WIKI-V5-SEM-02','original':{'repo':'company-wiki','path':p+'baseline/plan/traceability_matrix.md','line':180},'promise':'LLM_ENABLED链D07E/G07E reviewer精确人数D=1、G=1','historical_status':'normative v4 mapping imported/frozen under v5 accepted','historical_evidence':'v5-freeze-review-test-dag-closure4.md:13,46计数与集合通过，:56排除内容语义审查','current_independent_evidence':'gate_dag.v4.json:39-40为llm_data_governance与control_security两角色，:163/165 reviewers_on_pass=2；agent_review_gates.md:262-264亦明确2名。traceability_matrix.md:162要求精确人数，:227不一致应fail closed。','verdict':'contradicted','severity':'P2','scope':'规划内部单表陈旧；机器DAG本身人数自洽','recommendation':'新revision修正矩阵该行，并用机器DAG生成或逐关系验证所有prose角色/人数表；保持生产当前paused，不把规划修订当部署验收。'},
 {'id':'WIKI-V5-SEM-03','original':{'repo':'company-wiki','path':p+'v5-freeze-review-test-dag-closure4.md','line':11},'promise':'测试/DAG轴最终accepted，四轮3条P2全部CLOSED','historical_status':'accepted','historical_evidence':'该报告:19-29逐配方exit1/隔离正例；:47-48历史9188与17/32+4+3；:53-56明确残余和未做内容级审查。','current_independent_evidence':'逐读首审至closure4的五份记录，父/子进程导入劫持和-m路径的修复范围逐轮收敛；本轮51/51哈希复算支持冻结字节仍一致，未重演临时攻击配方或运行9188原checker。','verdict':'supported_scoped','recommendation':'accepted仅用于冻结/checker检查面；PR001–105的业务实施或运行效果需独立证据。保留其自身明确的语义审查排除项。'}]
target=H/'item_ledger.jsonl'
existing=[json.loads(s) for s in target.read_text(encoding='utf-8').splitlines() if s.strip()]
known={r['id'] for r in existing}
with target.open('a',encoding='utf-8',newline='\n') as f:
 for r in records:
  if r['id'] not in known: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print('explicit findings appended')
