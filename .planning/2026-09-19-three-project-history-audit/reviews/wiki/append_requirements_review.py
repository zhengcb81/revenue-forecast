"""Render manually assessed RQ/RK commitments, not infer verdict from wording."""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent; W=Path('C:/Users/郑曾波/Projects/company-wiki')
P='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/baseline/plan/'
f=H/'item_ledger.jsonl';rows=[json.loads(s) for s in f.read_text(encoding='utf-8').splitlines() if s];seen={r['id'] for r in rows}
# Each entry is a reviewer-authored assessment of the complete prose and machine definitions.
rq={
1:'N/2N与progress计量结合绝对10秒门，比旧2文档功能例强；需实际数据库规模、分布及SQLite版本证据。',
2:'加入primary_source_id/current hash，弥补最初只按document查artifact的语义；不能只以第一候选相同证明整候选有序等价。',
3:'no stats与多SQLite矩阵是合理设计；config doctor healthy、单机test PASS均不证明该矩阵。',
4:'verify-only ordinary open明确；旧ZR fixture依赖eager init不能据旧PASS否定此要求。须分开创建库和读库。',
5:'幂等、中断、ENOSPC条件都有对应未来分支；尚无生产升级run可以判已落实。',
6:'ADR-02 exactly-one与JSON DAG分支一致；未执行另一分支不等于跳过测试。',
7:'明确approximate progress callback不冒充exact VM step；计划计量元数据/复现实例合理，历史0.231秒不是新绝对门结果。',
8:'每root outcome/fingerprint比旧cycle-end checkpoint具体；需实际offline/incomplete返回值证明不误推进。',
9:'completed scan与未完成scan拆分正确；应对crash前后而非仅成功cycle作断言。',
10:'heartbeat/pause/stop/deadline分别验收，避免watchdog掩盖查询；纯回调活跃不是业务成功。',
11:'full-cycle business success和VM activity分离，直接回应原902秒循环。实现证据尚未交付。',
12:'废除uptime>=900清零是合理修复设计；不能把持续存活当成消除failure。',
13:'per-signature/global/no-success三类预算持久化避免交替失败绕过；需跨restart时钟及generation测试。',
14:'startup/backoff等候均需响应pause；计划明确有界而非sleep一次后才检查。',
15:'PID身份与Job Object对应orphan和重用风险；POSIX/tmp成功不能代替Windows真实Job行为。',
16:'reset-only旁支含独立D/OP/G，明确不授予resume；需验证control状态和latch都按合同变化。',
17:'scan性能以相同文件清单/语义不漏扫为条件；原427秒只是单次历史profile，不是新扫描加速验收。',
18:'cache/offline/rehash/path语义相互约束，30日重哈希是unchanged fast path的显式例外；需根adapter生产配置相同。',
19:'把battery gate前移到昂贵enumeration前，针对历史扫描先跑缺陷；计划不是已部署行为。',
20:'枚举全部parser路由且分启用/禁用证据，比旧3个HTML smoke完整；格式路由小样本只证明选定样本。',
21:'medium/oversize/error/cleanup为模板实例化，禁用需显式理由；不得把disabled当成功解析。',
22:'LLM需到达率1.2倍与7日backlog约束，原42秒单样本不能证明服务率；真实启用还需provider授权。',
23:'缓存按canonical request并逐document/source重绑定，避免跨文档重复用错；仍需实际normalized contract相同。',
24:'外部call崩溃记OUTCOME_UNKNOWN且零自动重发合理，不能仅DB状态推断provider零计费。',
25:'ADR-11独立LLM_OFF/ENABLED分支语义明确；runbook错误ADR编号另见SEM-07。',
26:'每stage/provider授权与OFF全deny有计划验收；未授权外发不是为了补测试而可执行。',
27:'默认生产delete=0与临时目录回归合理；H01后台自动prune风险仍需当前代码路径修复，root有新读证据。',
28:'明确不自动删除backup/VACUUM，合理隔离空间治理；旧磁盘46.22GiB不授权破坏性清理。',
29:'raw evidence保护与最小化收集有合同；日志“不含秘密”需内容级检查，不从文件hash推出。',
30:'scratch/测试/production路径隔离是约束；当前审计也遵守但这不替未来运行凭证。',
31:'config override按session传入，避免修改生产根；需验证所有子进程继承实际有效值。',
32:'external trust anchor/read-only release/TOCTOU防护形成闭环意图；冻结计划hash不等于已部署不可写release。',
33:'one-shot OP后pause防止整夜无界运行，未来A1/A2/A3逐步放量才可宣告。',
34:'PK/column/path precommit白名单比after-only净diff强；实际canonical import当前仍可能先写后fatal，应另行隔离验证。',
35:'BP/BF每次独立write合同避免授权复用，WRITE-*语义合理；具体Gate×Test关系缺口见SEM-01。',
36:'migration峰值空间、中断、ENOSPC为前置，旧库size不证明有足够空间做复制/建索引。',
37:'机器G11M-L-ADR分支定义明确；runbook:277写ADR-11=SCHEMA_DELTA，不能按此文字执行，见SEM-07。',
38:'missing/corrupt control fail-closed及旧heartbeat身份隔离合理；现desired_state=paused仅证明当前值。',
39:'startup delay每session一次合理，应跨子进程crash保持session身份。',
40:'至少2h且5连续成功是业务观察而非uptime门；失败清窗口，未运行此canary。',
41:'cycle先封exact write contract且新文档延后，避免观察中扩权限；WRITE-*在G11J映射缺口仍在。',
42:'12B新stage-bound授权，LLM_OFF只关闭provider不让整OP变N/A；计划合乎最小授权。',
43:'atomic create-if-absent与verify-preserve三分支明确保护第三方Run；历史强制覆盖命令已被取代，不能重用。',
44:'CAS后dormant、ARM/lease分层避免登录抢跑；需要Windows登录实际路径证据，JSON状态不能独立证明。',
45:'single-use token和崩溃/竞态合同明确；必须用并发原子消费测试而非串行两次请求。',
46:'G12B-POST保持PAUSED/process0，刻意不等于生产常驻恢复；验收应包括无child/egress/write。',
47:'新增D12C-RT/G12C-RT和两条purpose-bound授权，old113节点没有这层；315与115仅表示规划规模。',
48:'角色/人数/disjoint机器约束明确；traceability:180仍写LLM两Gate各1人而DAG各2，见SEM-02。',
49:'伪PASSED/FAIL/open P1/证据不足拒绝设计修补历史v3漏洞；freeze checker不等于future runtime ledger validator。',
50:'hash-chain/head/DAG/auth/OP规则为未来实现；当前机械计划检查只测结构/部分文字，不能替代实际append/next语义。',
51:'bootstrap在正式ledger之前有先后约束；实现尚未进正式Gate链，不能从schema文件存在推通过。',
52:'六prompt已分G10C/R并去未来依赖，但LLM_ENABLED direct join还漏G11M-L-ADR，见SEM-05。',
53:'漂移使下游失效是正确审签原则；v4事故证实旧PASS后来无效，不该复制为新PASS。',
54:'DAG/vectors/registry/catalog是严格data schema方向正确；本次逐ID/节点设计审查不等于全部schema安全审计。',
55:'静态OP catalog匹配动态sealed合同明确；必须验证真实写端执行合同而非只验证输入JSON。',
56:'journal首写前有D11J/G11J机器屏障；WRITE-F01/02 registry未含正文G11J/G10R revalidate义务，见SEM-01。',
57:'INDEX_REQUIRED只解开迁移前诊断门，不是性能PASS；迁移后正常10秒门设计避免循环依赖。',
58:'每runtime cycle重新授权/cap/journal防止一次总签字无限运行；未有G12C运行证据，不按计划文字宣称落实。',
59:'只按DAG exact角色人数而不笼统“全新”合理；prose当前仍存在一处1 vs2人冲突，见SEM-02。',
60:'保留ZR baseline同时显式fixture init避免为测试恢复产品eager DDL；历史39/40schema数字不能替实际fixture迁移验收。'
}
rk={
1:'有序全候选与source freshness需逐集合比对；旧前三候选匹配不足。',2:'无stats/不同planner分布是原两文档fixture没覆盖的关键维度。',3:'计量模式元数据须拒绝把proxy说成exact。',4:'分支未选不得实例化红测/实现，和一般“所有分支全跑”不同。',5:'ordinary read零DDL须含missing/old库反例。',6:'检查峰值而非仅当前free，生产迁移需单独批准。',7:'offline/incomplete不能当success推进。',8:'sqlite callback不可重入同连接，cleanup必须可复用连接。',9:'有heartbeat而无结果要触发circuit。',10:'不同failure signature也受global/no-success预算。',11:'reset不含resume/arm授权。',12:'PID重用和Job Object失败要fail-closed，不能只process名kill。',13:'相同输入清单/结果集作为性能改善前提。',14:'30日rehash给metadata spoof最终检测上限，不能称每次都识别。',15:'每启用route样本全，禁用单列不能报解析成功。',16:'真实Windows子进程树pause/stop证据必要。',17:'文档与当前source/artifact三者绑定，不能contenthash随意替代身份。',18:'cache结果重绑定到每document且校验模型版本。',19:'provider外部结果未知保守停下，不能自动重发求成功。',20:'备用provider也须freshstage授权。',21:'公开日志与获批raw分离，哈希不证明内容无密。',22:'net-zero后验diff抓不住错PK写，应precommit。',23:'journal角色正确，但Gate×Test遗漏见SEM-01，不能声称此风险已消除。',24:'每cycle封合同，新文档延后而非扩大旧合同。',25:'sentinel只能检测事后改动，OSdeny才是写前屏障。',26:'可信根不与被验证release同一可写目录。',27:'atomicCAS/thirdpartyconflict需保持现值，历史Force覆盖已过时。',28:'CAS与login间要dormant，删除Run不是通用补偿。',29:'并发token消费需单原子成功并拒绝replay。',30:'短期LLM授权不可变成无限backlog预算。',31:'OP12C不能顺带启动当前session，验证Gate本身readonly。',32:'原v3schema反例是真正FAIL，不能被v4候选处置自签CLOSED。',33:'只由validator输出next，不接受调用方authorednext。',34:'exactreviewer人数跨文档尚有冲突SEM-02。',35:'内部自洽hashchain不足，要独立protectedhead。',36:'六promptdirectjoin还不相等SEM-05，应从DAG生成比较。',37:'v4冻结事故表明签名后bytes变更应撤销而非继续沿用。',38:'每OP后pause+独立G，禁止最后补签过程。',39:'N/A需适用性证明，不能用来跳过整体生产OP授权。',40:'补偿写须显式OP，readonlyGate不能偷偷写。',41:'多资源半提交用intent/finalize，不猜测/覆盖第三方值。',42:'INDEX_REQUIRED不得算性能通过，迁移后重验10秒。',43:'每cyclefreshcontract/cap，不能只检查第一次。',44:'改fixture而不放宽产品reader，避免测试反向绑架接口。'
}
assert set(rq)==set(range(1,61));assert set(rk)==set(range(1,45))
path=P+'traceability_matrix.md'
for line,s in enumerate((W/path).read_text(encoding='utf-8').splitlines(),1):
    m=re.match(r'\| (RQ-|RK-)(\d+) \|',s)
    if not m:continue
    n=int(m[2]);kind=m[1].rstrip('-');i=f'WIKI-{kind}-{n:03d}'
    if i in seen:continue
    cells=[x.strip() for x in s.strip('|').split('|')]
    assessment=(rq if kind=='RQ' else rk)[n]
    semantic_gap=(kind=='RQ' and n in {37,48,52,56,59}) or (kind=='RK' and n in {23,34,36})
    verdict='insufficient_evidence' if semantic_gap else 'not_deployed' if kind=='RQ' else 'supported_scoped'
    rows.append(dict(id=i,original=dict(repo='company-wiki',path=path,line=line),promise=s,historical_status='规范性规划/风险映射，原文:3声明不是动态完成台账',historical_evidence='原文关联Evidence/Test/Gate及315 registry /115 DAG；没有相应生产OP运行完成凭证。',current_independent_evidence=assessment+' 已独立逐项阅读对应规划正文、ID定义/生命周期和机器节点；参见本目录plan_structure_checks.json和WIKI-TEST/WIKI-NODE记录。',verdict=verdict,recommendation='下一revision消除文本冲突，再依依赖逐Gate实施；验收保留原件、真实入口/有效配置、完整输入输出、适用性与未执行范围。',scope='planning obligation' if kind=='RQ' else 'risk recognized in plan, not claim of risk elimination',planning_assessment=assessment,assessment_limit='未运行未来实现；supported_scoped仅确认风险及检测设计有明确对应，不证明生产保护已存在。'))
    seen.add(i)
f.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
print(f'{len(rows)} total; added 60 individual requirements and 44 risk dispositions')
