"""Historical worker/revision conclusions and independently inspected version deltas."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;W=Path('C:/Users/郑曾波/Projects/company-wiki');B='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/'
f=H/'item_ledger.jsonl'; rows=[json.loads(s) for s in f.read_text(encoding='utf-8').splitlines() if s];seen={r['id'] for r in rows}
def add(i,path,line,promise,hist,ev,verdict,rec):
    if i in seen:return
    rows.append(dict(id=i,original=dict(repo='company-wiki',path=path,line=line),promise=promise,historical_status=hist,historical_evidence=ev,current_independent_evidence=ev,verdict=verdict,recommendation=rec,scope='worker historical evidence / revision transitions',assessment_limit='本轮全文/差异及只读证据复审；未重跑历史生产负载或未实施的修复。'));seen.add(i)
R=B+'baseline/history/plan_review_revision.v4.md'
add('WIKI-HIST-V1',R,3,'v1计划冻结，修改任何核心文件必须新revision','v1后被v2取代','原文v1 hash集和:20失效规则；baseline/plan/plan_review_findings.md PR001–035是v1审查反例，处置稿不是原v1 PASS。','superseded','只保留审计，不恢复为执行入口。')
add('WIKI-HIST-V2',R,25,'v2处置PR001–035，可在独立关闭P0/P1后供实施','仍须三类reviewer复审','原文:47明确条件未自动成立；v3又处置PR036–053和仍开放v1项。','superseded','以逐领域正式结论而非作者addressed标签关闭。')
add('WIKI-HIST-V3',R,88,'13核心hash MATCH后的v3审查完成','REVIEW_COMPLETE_FAIL / HISTORICAL_ONLY','原文三类reviewer均FAIL，PR054–066包含伪PASSED/分支等反例；hash匹配和实质FAIL可以同时为真。','historical_only','不要把manifest MATCH的局部PASS转写成计划或worker通过。')
add('WIKI-HIST-V4-CHECK',R,117,'7696 checks PASS;115nodes/29schema/315tests/18vectors','mechanical check PASS',':125–128原文明示该PASS不能替代三份正式verdict；:132起27bytes漂移导致失效。当前315/115已独立结构检查和逐项规划审查，没有把数量当运行覆盖。','supported_scoped','将机器结构、领域语义、实现、生产路径分开交付。')
add('WIKI-HIST-V4-INVALID',R,132,'v4因27 normative字节变化失效','INVALIDATED_FROZEN_BYTES','incident:10–18和:153–168记录16LF等价、11无法等价确认；高概率precommit恢复/autocrlf，但无进程写事件不能锁定唯一行为人。中止review不是技术FAIL也不是PASS。','historical_only','保持历史manifest，不重算覆盖；新基线重审，不宣称完整恢复v4。')
add('WIKI-HIST-V4-STALE-LAST',R,147,'当前未创建v5，未改变规范文件','当时历史续接状态','当前v5目录及51normative存在，原文lastline只是9/3时点；它不推翻后继v5，也不应被自动hook当当前nextstep。','superseded','历史正文标时点，当前路由只指向后继审计/退役，不自动续旧恢复。')
I=B+'baseline/investigation/worker-investigation-2026-08-20.md'
items=[
(12,'SQL相关EXISTS用于过滤无位置文档，但真实planner近二次扫描','8/12修复后生产退化','报告把具体commit、23530documents/25046active locations、EXPLAIN与对照实验串联；两文档功能例不触发生产索引选择。当前normalizer源码已变，不能从旧报告直接宣布当前仍为同一SQL。','historical_only','验收基于相同schema/stats/规模/分布的入口性能与全候选语义，不只加小fixture。'),
(21,'真实队列选择>902秒；替代非相关查询0.231秒','historical measured','报告:307–326对照仅最前三文档相同，虽能定位性能，不足证明force/retry/order/current-source全部等价。','historical_only','把性能诊断与替代查询正确性证明分开，未来全有序候选矩阵对比。'),
(24,'scan checkpoint/无heartbeat/uptime清零让故障反复重启且零产出','historical causal explanation','正文§12逐项对应源码和日志，44次scan/2.54h支持放大链；本轮不resume复现，避免资源消耗。','historical_only','业务成功里程碑、per-root checkpoint和有界SQL控制需联合canary。'),
(60,'persistent pause、process0、HKCU Run移除','8/20时点观察','该观察及9/10handover不能推出9/19全机无进程/任务；本轮只读control确为paused，未做全机高权限核查。','historical_only','把状态值/可见surface/时间记录，不以旧process0替当前状态。'),
(90,'HKCU Run经pythonw launcher开启worker','historical configured autostart','报告将登录自启与开机区分；恢复脚本仍可重新写Run能力，当前未调用。','historical_only','有效启动入口/账户/权限逐个列举，protectedhive未读记录unknown。'),
(199,'进入持续失败并重启','historical logs','卡在selecting next document且parser PID/path为空，CPU满单核、低physicalI/O支持SQL卡点；不等同所有格式parser性能都通过。','historical_only','用stage span和业务产出监控，禁止从进程活跃判healthy。'),
(221,'重复supervisor/实例锁噪声是同日另一问题','historical observation','报告将其与主SQL因果分开，避免把任何日志异常都当根因；单实例还需PID/Job安全验收。','historical_only','独立问题分别复现、分别关闭。'),
(307,'readonly SQL对照验证替代性能','historical experiment','原查询10s中断、forceindex1.413s、IN roots0.914s、去roots0.231s；只限当时SQLite库/前三候选。未本轮重跑。','historical_only','记完整schema/policy/SQLite/stats/样本和顺序；不把LIMIT3提升为全量等价。'),
(570,'具体修复步骤尚待实施','proposal','v5之后又增加primary_source_id、exact合同和双purpose授权；初版建议不应绕过后继门禁。','superseded','不沿旧文命令resume/Force覆盖Run或做无界生产对照。'),
(587,'加入生产规模性能回归','planned','v5 Q-P/Q-S细化N/2N与no-stat/绝对10s，是合理改善；未执行future tests，not implemented不记成产品bug。','not_deployed','在后继允许的scope逐项落测量证据。'),
(607,'非相关候选集合改写','planned SQL sketch','草图本身不是全语义证明，后v5 current-source更严格；去roots join先查orphan要求合理。','superseded','以最终current primarytuple和候选顺序要求设计实现。'),
(622,'添加覆盖或部分索引','planned optional strategy','v5 ADR-02先选NO_INDEX/INDEX，不能把建议索引当默认可在46GiB库自动创建。','superseded','只在明确分支和空间/中断验证后审生产迁移。'),
(641,'ANALYZE只作辅助','planned guardrail','避免测试环境stats偶然掩盖SQL复杂度，v5保持no stats矩阵。','supported_scoped','将无统计信息场景设必验，不把一次ANALYZE当长期修复。'),
(645,'scan成功即checkpoint','planned','旧cycleend问题在v5细化到perroot outcome+fingerprint，报告方案是起点而非完成实现。','not_deployed','检查crash/取消/offline/incomplete四类重试语义。'),
(657,'SQL进度回调提供heartbeat/control','planned','后v5明确VM activity≠businesssuccess，callback是proxy而非exactstep；不得只扩大watchdog。','not_deployed','同时约束liveness、deadline、pause和业务成功。'),
(676,'restart backoff按成功里程碑或稳定区间重置','old proposal','v5更严格要求full cycle success，旧健康时长替代标准不再足够。','superseded','保留持久failure预算，禁止timealive重置。'),
(686,'优化扫描，减少重复枚举','proposal','历史427s单次profile和5–6秒采样只足够找热点；v5多样本同输入对照比旧要求严格。','not_deployed','语义全量一致是速度验收前提，必须使用有效生产root adapter配置。'),
(699,'平衡normalizer/fingerprint/LLM','proposal','42s一条LLM、3:1batch是瓶颈假设，非服务率测量；v5加入arrival/drainSLO和OFF独立分支。','not_deployed','测长期到达率与backlog年龄，先验证授权/成本/未知结果处理。'),
(716,'容量维护与retention专项','proposal','46.22GiB主库+45.93GiBbackup和freelist0不授权删库；抽1000evidence平均9746 bytes不能估全库精确组成，rowid高水位不是行数。','not_deployed','先只读按表/页统计定位；破坏性维护另作review，不自动prune旧backup。'),
(756,'生产只读canary比较原/新查询','old runbook','旧原查询可能无界，v5先预算/超时且不在生产重跑已知昂贵原查询。','superseded','使用受界只读对照及明确中止条件。'),
(765,'单周期受控运行后再观察和恢复Run','old runbook','旧status wrapper会写diagnostic；原resume与New-ItemProperty -Force缺新的protected journal/atomicCAS/dormant/双purpose授权。后继v5+退役已取代。','superseded','禁止从此旧runbook恢复worker；只作为失败因果史。'),
(813,'不应加超时/无限重启/开并发掩盖问题','historical recommendations','与full cycle success、可中断查询、限制LLM预算等后继设计一致；属于正确约束非已实现证据。','supported_scoped','将反例写入真实入口测试，不能仅文档警告。'),
(856,'调查局限包括缺进程栈/短磁盘样本/无dbstat/scan近似','explicit limits','全文明确限制因果强度；不得移除这些限定而写成已证明所有磁盘/内存/parser均无问题。','supported_scoped','继续保留时间/取样/权限限制，当前变化需独立新证据。')]
for n,(line,promise,hist,ev,verdict,rec) in enumerate(items,1):add(f'WIKI-WORKER-HIST-{n:02d}',I,line,promise,hist,ev,verdict,rec)
# All old common text and all deltas were manually read. Exact rows preserve prior-version status.
old=json.loads((H/'old_version_mapping.json').read_text(encoding='utf-8'))
for n,r in enumerate(old,1):
    add(f'WIKI-OLD-MD-{n:02d}',r['old_path'],1,'旧版整份独立承诺与状态的版本定位：'+r['old_path'].split('/')[-1],'旧v1–v4副本；后被v5新基线/后继退役取代','共同正文完整复用已全读'+r['baseline_path']+'；全部旧侧差异已逐段读，精确line_mapping与sha见old_version_mapping.json。两版本字节不相同；旧PASS不继承，具体义务对应WIKI-PR/RQ/RK/TEST/NODE及历史轨迹。','superseded','仅作历史；保留旧状态与新状态映射，不将v5新增29test/2node投射回旧版。')
f.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
delta=json.loads((H/'old_json_semantic_diff.json').read_text(encoding='utf-8'))
(H/'old_machine_item_review.md').write_text('''# 旧版机器条目语义复审映射

旧 test registry 实际 286 个对象与 v5 对应对象逐字段相同，v5 新增 29 个；旧文若仍写 283，属于旧草稿状态漂移，不能称旧版跑过 315 个测试。共同对象的逐 ID 规划评估见 item_ledger.jsonl 的 WIKI-TEST 条目；映射仅复用人工语义阅读，不继承通过状态。

旧 DAG 113 节点，112 与 v5 对象相同，D12C 的 requires 从 G12B-POST 变为 G12C-RT；新增 D12C-RT/G12C-RT，引入两条 purpose-bound 用户授权及 disjoint 约束。全部差异已阅读 old_json_semantic_diff.json；共同节点人工评估见 WIKI-NODE 条目。旧 113 节点链不能得到新授权防护的信用。

判定：两个旧机器文件均 superseded。它们是计划数据，不是产品实现或成功运行台账；未选分支也不能统计为已通过。字节/字段相同映射不得用来跨版本继承 reviewer 签字。
''',encoding='utf-8')
print(f'{len(rows)} ledger entries; old revision and worker investigation histories persisted')
