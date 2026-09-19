from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent; P=H.parents[1]; W=P.parents[2]/'company-wiki'
prefix='docs/plans/data-lake-simplification-2026-09-07/'
spec=[('.mimocode/plans/1784577918407-neon-planet.md',1,142,'historical_only','最早三市场实测设计有明确真实原文要求，却在V1允许成功/缺失/身份冲突全部作为预期，V6只看local canonical_path不能证明零网络；calculator消费JSON不等价实际读取PDF。其安装/目录/模块状态是旧日期，不应执行旧pip/mkdir命令或当今天未安装。','reviews/company_cases/independent_checks.json; reviews/revenue/deep_clause_ledger.jsonl','以实际公开source入口、I/O trace、二次零下载和正式结果验收；各失败状态与成功分开。'),
(prefix+'README.md',1,140,'supported_scoped','完整阅读诊断与四增量/七验收；明确只读规划无真实E2E/性能成果。位置透明、同hash健康副本、query/open/request能力分离、第五root零consumer改动是合理目标，后继R4并未全部兑现。原文明确95门不是每文件运行门，不能误报实际每次读文件都查CA/ZR。','reviews/wiki/review.md; reviews/revenue/r4_document_ledger.jsonl; reviews/cross_history/current_recheck.json','保留减法方向与必要身份/完整性/动作授权约束，不引入第四套DAG；普通读取不等待长期发布观察。'),
(prefix+'task_plan.md',1,11,'supported_scoped','三个勾选只完成诊断与建议，不称产品实施。9/9补充明确v5仅冻结输入、legacy有活跃调用者，需要替代后退役。','reviews/wiki/review.md; reviews/cross_history/item_ledger.jsonl','已退役目标不复活，现读链按实际调用与替代计划评估。'),
(prefix+'findings.md',1,28,'historical_only','每条配置/调用路径观察有明确HEAD和时间；承认原先双白名单说法过时、public不等可写、已有统一索引。当前部分路径已有R4后继，旧canonical选择/默认策略不得不经复核就报今日漏洞；当前生产adapter缺失另有真实证据。','reviews/wiki/review.md; reviews/revenue/r4_document_ledger.jsonl; reviews/filing/review.md','单独保存当时诊断与现行实现差异，支持readiness分层/健康副本/一次决策。'),
(prefix+'progress.md',1,11,'supported_scoped','交付范围清楚，主动撤回artifact_backfill零读者和3a删除资格是有效更正；预计9/12门开只是计划时间，须实际自然日志而非预测日期认证。','reviews/cross_history/item_ledger.jsonl; reviews/revenue/deep_clause_ledger.jsonl','不可在当前审计执行旧删除/恢复指令；用真实证据决定后继完成。')]
cases=[];rows=[];cov=[]
for i,(f,a,b,v,q,e,fix) in enumerate(spec,1):
 path=W/f; raw=path.read_bytes();ls=raw.decode('utf-8-sig').splitlines();h=hashlib.sha256(raw).hexdigest();cid=f'FCTX-{i:02}'
 cases.append(dict(case_id=cid,file=f,start=a,end=b,verdict=v,rationale=q,evidence=e,remedy=fix))
 for n,l in enumerate(ls,1):
  if l.strip():rows.append(dict(occurrence_id=f'FCTXL-{len(rows)+1:04}',source_file=str(path),file_sha256=h,line_start=n,line_end=n,original_text=l,manual_case_id=cid,verdict=v,rationale=q,evidence=e,remedy=fix,reviewer='root',read_status='fully_read'))
 cov.append(dict(source_file=str(path),file=f,sha256=h,lines=len(ls),read_status='fully_read',semantic_cases=[cid]))
(H/'manual_cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
(H/'item_ledger.jsonl').write_text(''.join(json.dumps(z,ensure_ascii=False)+'\n' for z in rows),encoding='utf8')
(H/'coverage.json').write_text(json.dumps(dict(files=cov,summary=dict(files=len(cov),occurrences=len(rows),manual_cases=len(cases))),ensure_ascii=False,indent=2),encoding='utf8')
print(len(rows))
