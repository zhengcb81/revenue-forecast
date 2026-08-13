# FC 工作单元验收登记表

> 这是 71 个 FC 的唯一状态索引。详细行为以 `task_plan.md` 为准，执行纪律以 `implementation_runbook.md` 为准。实施时不得复制出第二张状态表。

## 1. 状态规则

- 合法状态：`pending`、`preflight_locked`、`red_proved`、`implemented`、`focused_green`、`repo_green`、`cross_repo_green`、`real_verified`、`rollback_verified`、`independent_review`、`accepted`、`blocked`、`failed`。
- 除 Phase 0 的计划基线外，当前全部为 `pending`。
- 状态只能由 validator 根据证据推进；自然语言、提交信息、PR 标签或实施者自评不能改变状态。
- 表中前置 FC 未全部 `accepted` 时，不得取得 execution lock。
- “主证据”是最低要求；task plan、scenario registry 或影响分析要求更多证据时取并集，不能取更小集合。

## 2. Phase 0：基线（计划层已完成）

| FC | 状态 | 前置 | Owner | 主证据/出口 |
|---|---|---|---|---|
| FC-000 | completed_plan_baseline | 无 | 三仓 | 三个 40 位 HEAD=upstream、dirty allowlist、CodeGraph health |
| FC-001 | completed_plan_baseline | FC-000 | company-wiki | 生产只读统计、root/catalog fingerprint、现状矛盾清单 |
| FC-002 | completed_plan_baseline | FC-001 | revenue | 已知缺陷→scenario/phase 映射，无未登记 P1/P2 |

## 3. Phase 1：契约与治理

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-101 | accepted | FC-002 | 三仓 | ownership RED、ADR hashes、N/N-1 兼容表、重复 owner=0（receipt: assurance/fc/FC-101/；reviewer-fc101-independent accepted 2026-08-10） |
| FC-102 | accepted | FC-101 | revenue | 95 scenario registry 一致性、重复/缺失/矛盾/假 E2E mutation（receipt: assurance/fc/FC-102/；reviewer-fc102-independent accepted 2026-08-10；硬覆盖门属 FC-1003） |
| FC-103 | accepted | FC-101 | revenue | receipt validator 负向全集；旧 25 receipts 不得误通过（receipt: assurance/fc/FC-103/；reviewer-fc103-independent accepted 2026-08-10；6 负向 mutation 实测拒绝） |
| FC-104 | accepted | FC-101、102、103 | revenue | current triplet manifest；sibling 漂移 RED；完整组合 GREEN（receipt: assurance/fc/FC-104/；reviewer-fc104-independent accepted 2026-08-10） |

## 4. Phase 2：运行时控制平面

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-201 | accepted | FC-104 | company-wiki | CTRL-01/02/05；CAS、未知 flag、并发 snapshot、读取失败关闭（receipt: company-wiki/assurance/fc/FC-201/；reviewer-fc201-independent accepted 2026-08-10；16 tests + 3 mutations） |
| FC-202 | accepted | FC-201 | company-wiki | resolver flag/epoch/cohort SQL 条件；删除任一条件 mutation 必死（receipt: company-wiki/assurance/fc/FC-202/；reviewer-fc202-independent accepted 2026-08-10；15 tests + 6 mutations killed） |
| FC-203 | accepted | FC-202 | company-wiki | CTRL-03/04；preview/apply/rollback、重复/中断/陈旧 hash（receipt: company-wiki/assurance/fc/FC-203/；reviewer-fc203-independent accepted 2026-08-10；11 tests + 3 mutations + fault injection） |
| FC-204 | accepted | FC-203；用户写授权 | company-wiki | 16 active assertion 副本演练、T4 最小 cohort、响应级 rollback（receipt: company-wiki/assurance/fc/FC-204/；reviewer-fc204-independent accepted 2026-08-10；生产状态只读复核通过） |
| FC-205 | accepted | FC-204 | company-wiki | production caller reachability、CTRL 全集、双控制面 forbidden=0（receipt: company-wiki/assurance/fc/FC-205/；reviewer-fc205-independent accepted 2026-08-10；4 gate tests + adversarial + 2 wiring mutations killed） |

## 5. Phase 3：RootPolicy 与扫描解耦

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-301 | accepted | FC-205 | company-wiki | RootPolicy 2.x schema、1.x doctor、未知/可写外部 root fail closed（receipt: company-wiki/assurance/fc/FC-301/；reviewer-fc301-independent accepted 2026-08-10；11 tests + 5 mutations killed） |
| FC-302 | accepted | FC-301 | company-wiki | 三 adapter production caller>=1；scanner root-specific branch 新增=0（receipt: company-wiki/assurance/fc/FC-302/；reviewer-fc302-independent accepted 2026-08-10；9 tests + 3 mutations killed） |
| FC-303 | accepted | FC-302 | company-wiki | v1/v2 frozen corpus shadow parity、差异 ledger、EX-08 mutation（receipt: company-wiki/assurance/fc/FC-303/；reviewer-fc303-r2 accepted 2026-08-10（F1 changes_required → 修复后复审通过）；8 tests + 4 mutations killed） |
| FC-304 | accepted | FC-303 | company-wiki | future_lake 配置-only T1；产品 Python diff=0（receipt: company-wiki/assurance/fc/FC-304/；reviewer-fc304-independent accepted 2026-08-10；5 tests + 2 mutations killed + 独立 config-only 链复放） |
| FC-305 | accepted | FC-304 | company-wiki | 两轮 shadow diff 解释完毕、真实根 fingerprint 不变、fallback 可用（receipt: company-wiki/assurance/fc/FC-305/；reviewer-fc305-independent accepted 2026-08-10；5 tests + 2 mutations killed + 独立 fingerprint 复现） |

## 6. Phase 4：Catalog 与 provenance 迁移

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-401 | accepted | FC-305 | company-wiki | MIG-01/02/03/07；副本 dry-run/resume/idempotency/资源上界（receipt: company-wiki/assurance/fc/FC-401/；reviewer-fc401-independent accepted 2026-08-10；7 tests + 3 mutations killed） |
| FC-402 | accepted | FC-401 | company-wiki | SAFE-01~04、MIG-05；零猜测、四分桶守恒（receipt: company-wiki/assurance/fc/FC-402/；reviewer-fc402-independent accepted 2026-08-10；9 tests + 4 mutations killed） |
| FC-403 | accepted | FC-402 | company-wiki | proposal/approval/activation 分权；伪 receipt/policy hash mutation（receipt: company-wiki/assurance/fc/FC-403/；reviewer-fc403-independent accepted 2026-08-10；7 tests + 3 mutations killed） |
| FC-404 | accepted | FC-403 | company-wiki | root/market/kind coverage ledger；输入=全部分桶之和（receipt: company-wiki/assurance/fc/FC-404/；reviewer-fc404-independent accepted 2026-08-10；7 tests + 2 mutations killed + 只读字节级验证） |
| FC-405 | accepted | FC-404 | company-wiki | MIG-02/04/06/07/08；灾难恢复和 catalog integrity（receipt: company-wiki/assurance/fc/FC-405/；reviewer-fc405-independent accepted 2026-08-10；6 drill tests + 2 mutations killed + 独立 47-source drill） |

## 7. Phase 5：Dropbox 闭环

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-501 | accepted | FC-205、301、405 | company-wiki/filing | DBX-02~06；只读 RootPolicy、sidecar、containment；第二 allowlist=0（receipt: company-wiki/assurance/fc/FC-501/；reviewer-fc501-r2 accepted 2026-08-10（F1 changes_required → 修复后复审通过）；wiki 5 tests + filing 6 tests；3 mutations + RED-base killed） |
| FC-502 | accepted | FC-501 | company-wiki | registry→adapter→admission→assertion production trace；Dropbox 写=0（receipt: company-wiki/assurance/fc/FC-502/；reviewer-fc502-independent accepted 2026-08-10；4 tests + 1 mutation killed + DBX-01/03/04/07 独立复放） |
| FC-503 | accepted | FC-502 | company-wiki | 真实只读候选分桶；中国平安等不可证明样本保持 fail closed（receipt: company-wiki/assurance/fc/FC-503/；reviewer-fc503-independent accepted 2026-08-10；7 tests + 6 mutations killed + 真实 root 两轮零写 replay） |
| FC-504 | accepted | FC-503；用户样本授权（2026-08-10 用户决策：排他性条款放宽） | company-wiki | 机制 r1 accepted + 样本 r2 accepted（reviewer-fc504-independent 2026-08-10 + reviewer-fc504-r2 2026-08-10；4 真实 canary 注册：紫金矿业 601899 FY2024/25 + 星环科技 688031 FY2024/25；eligible=4；跨根重复按 EX-04 记录） |
| FC-505 | accepted | FC-504 | 三仓 | EX-03、DBX-01~08、IDX 适用项、external write=0、rollback trace（receipt: revenue-forecast/assurance/fc/FC-505/；reviewer-fc505-independent accepted 2026-08-10；4 chain tests + 2 mutations killed + 真实 replay 2/2 REUSED_EXACT + resolver-MISSING 缺口关闭） |

## 8. Phase 6：companies/dayu 等价与多根泛化 — 状态：completed（2026-08-11）

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-601 | accepted | FC-305、405 | company-wiki | CompanyRaw v1/v2 parity、EX-01、canonical writer 不变（receipt: company-wiki/assurance/fc/FC-601/；reviewer-fc601-independent accepted 2026-08-10；7 tests + 4 mutations killed + EX-01 真实 CN/HK/US 3/3 REUSED_EXACT） |
| FC-602 | accepted | FC-601 | company-wiki | >=2 dayu-only、EX-02、HK/US identity、capture failure 原因关闭（receipt: company-wiki/assurance/fc/FC-602/；reviewer-fc602-independent accepted 2026-08-10；10 tests + 5 mutations killed + EX-02 真实 dayu-only 2/2 + capture-incomplete 原因关闭） |
| FC-603 | accepted | FC-602 | company-wiki | EX-04~07、AR-09；扫描顺序 mutation 不影响结果（receipt: company-wiki/assurance/fc/FC-603/；reviewer-fc603-independent accepted 2026-08-10；6 tests + 3 mutations killed + canonical 四层防御确认） |
| FC-604 | accepted | FC-603、FC-505 | 三仓 | companies/dayu/Dropbox 同请求矩阵；root-specific 业务分支=0（receipt: company-wiki/assurance/fc/FC-604/；reviewer-fc604-independent accepted 2026-08-11；4 tests + 1 mutation killed + provider 归一化修复） |

## 9. Phase 7：统一 resolver

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-701 | accepted | FC-604 | company-wiki | normalized-only production trace；legacy metadata caller=0（receipt: company-wiki/assurance/fc/FC-701/；reviewer-fc701-independent accepted 2026-08-11；7 tests + 2 mutations killed + legacy owner gate + config_doctor 契约） |
| FC-702 | accepted | FC-701 | company-wiki | SAFE-01~07；别名/市场/前导零；弱匹配 mutation 必死（receipt: company-wiki/assurance/fc/FC-702/；reviewer-fc702-independent accepted 2026-08-11；7 tests + 1 mutation killed + CW-2.27H soft-match 移除） |
| FC-703 | accepted | FC-702 | company-wiki | SQL pushdown、EX-07、OPS-03、p50/p95/内存预算（receipt: company-wiki/assurance/fc/FC-703/；reviewer-fc703-independent r1 REJECTED（WHERE-pin 投影可满足）→ r2 receipt-level REJECTED → r3 ACCEPTED 2026-08-11；5 tests + M1/M3 killed（WHERE 区域断言）+ fail-closed replay + 23521 docs 延迟基线） |
| FC-704 | accepted | FC-703 | company-wiki | outcome/journal 对账；伪 download_calls mutation 必死（receipt: company-wiki/assurance/fc/FC-704/；reviewer-fc704-independent accepted 2026-08-11；9+3+4 tests + M1/M2 killed（伪回执恢复、journal 对账移除）+ 零写验证 + 真实链 E2E 端到端） |
| FC-705 | accepted | FC-704 | company-wiki | legacy observer 真实 seam、两个>=24h zero-hit 窗口、可回滚（receipt: company-wiki/assurance/fc/FC-705/；reviewer-fc705-independent r1 CHANGES_REQUIRED（F1 关闭门不可达 + F2 base hash）→ r2 ACCEPTED 2026-08-11；16 tests + M1/M2/M3 killed + completed-window gate（leg10g 簿记流）+ 真实 seam canary 观察 + 现场 drill 4/4 reused_exact 零 bridge hit） |

## 10. Phase 8：latest 与下载

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-801 | accepted | FC-704 | company-wiki | CloseGap contract；DL-02/03/07/09、LT-10；事务 journal（receipt: company-wiki/assurance/fc/FC-801/；reviewer-fc801-independent accepted 2026-08-11；7+2 tests + M1/M4 killed（policy 绑定、commit 绕过经 LT-10 guard）+ 固定步骤事务 + authorization policy_hash 绑定 + CLI close-gap） |
| FC-802 | accepted | FC-801 | filing-fetch | allow_download 两分支；GAP 不误映射 not_found；不复制策略（receipt: company-wiki/assurance/fc/FC-802/；reviewer-fc802-independent r1 REJECTED（F1：ensure 缺 --mode + main() 包装 gap）→ r2 REJECTED（F-r2-1 死代码回归测试）→ r3 ACCEPTED 2026-08-11；7 tests + M1/M2 killed + 现场端到端 gap 结构化验证） |
| FC-803 | accepted | FC-802 | filing-fetch | DL-01~10、LT-01~10；只补 gap、第二次 fetch/write=0（receipt: company-wiki/assurance/fc/FC-803/；reviewer-fc803-independent accepted 2026-08-11；5 T1 跨进程 spy 测试 + M1/M2b killed + 3 个真实缺陷修复（close-gap 按 missing candidate 绑定、CLI 缺参、staging 清理 id）） |
| FC-804 | accepted | FC-803 | company-wiki/filing | DL-08/09、OPS-02；single-flight、崩溃恢复、幂等（receipt: company-wiki/assurance/fc/FC-804/；reviewer-fc804-independent accepted 2026-08-11；5 tests + M1/M2 killed（锁移除 2-fetch、重试禁用）+ 锁内重查 journal 证据 + 锁界实测） |
| FC-805 | accepted | FC-804；真实下载授权 | filing-fetch | CN/HK/US T3、bytes/provider hash、首次/二次计数（receipt: company-wiki/assurance/fc/FC-805/；reviewer-fc805-independent accepted 2026-08-11；真实 cninfo/dayu 三市场下载 3/3 + M1 击杀（hint 移除 3.4s 现场失败）+ skip-not-pass 门 + discovery 年份推导修复） |

## 11. Phase 9：工件复用

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-901 | accepted | FC-405、704 | company-wiki | 7712 artifacts dry-run 分桶、MIG-01/03/05、零删除（receipt: company-wiki/assurance/fc/FC-901/；reviewer-fc901-independent accepted 2026-08-11；11 tests + M1/M2 killed + 全量套件 2209 passed 零新失败；can_accept gate exit 0） |
| FC-902 | accepted | FC-901 | company-wiki | SourceBundle production caller>=1、snapshot 一致、unknown role fail closed（receipt: company-wiki/assurance/fc/FC-902/；reviewer-fc902-independent accepted 2026-08-11；7 tests + M1/M2/M3 killed + 全量套件零新失败（1 pre-existing worker-bootstrap timing flake 证明在 base 复现）+ can_accept gate exit 0） |
| FC-903 | accepted | FC-902 | filing-fetch | N/N-1 bundle contract；unavailable 显式；转发不改决策（receipt: filing-fetch/assurance/fc/FC-903/；reviewer-fc903-independent accepted 2026-08-11；9 tests + M1/M2/M3 killed + 全量 276 passed 零失败 + pre-commit hermetic/E2E/install-sync 全绿 + can_accept gate exit 0） |
| FC-904 | accepted | FC-903 | revenue | selector production caller；AR-01~09；最小 DAG 重算（receipt: revenue-forecast/assurance/fc/FC-904/；reviewer-fc904-independent accepted 2026-08-11；11 tests + M1/M2/M3 killed + 全量 396 passed（主树）/worktree 环境 12 个 sibling-layout 失败在 base 相同=零新失败 + can_accept gate exit 0；2 low-severity 非阻塞 finding F1/F2 记录于 REVIEWER_REPORT） |
| FC-905 | accepted | FC-904 | 三仓 | journal 权威计数、prompt-injection receipt、hash/version mutation（FC-905-a 生产侧 reviewer-fc905a-independent accepted + FC-905-b 消费侧 reviewer-fc905b-independent accepted，均 2026-08-11；-a 9 tests + M1~M4 killed；-b revenue 6 + filing 7 tests + M1~M4 killed；全量 revenue 402 / filing 283 零失败；receipts: company-wiki/assurance/fc/FC-905/；can_accept exit 0 x2） |
| FC-906 | **accepted（-a/-b/-c/-d 全部 accepted 2026-08-12）→ Phase 9 COMPLETE** | FC-905；必要时生产迁移授权 | 三仓 | 每类真实 bound artifact>=1；T2 artifact_read>0、producer=0。**子拆分（2026-08-11 用户批准路径 C，runbook §10）**：-a v2 producer 绑定元数据（accepted；3 producer 打 schema_version+ISO created_at；3 tests+M1~M3）→ -b 角色适用性合同说明（accepted；markdown 冗余、consumer_analysis 消费者侧；3 护栏 tests）→ -c **生产 canary apply（accepted）**：9506 无-location 队列饿死修复（0ee0d09）+ 副本演练 + 生产 apply（15 normalize+11 sections+3 真实 LLM summary → 29 v2 artifacts 全 REUSABLE + 29 journal + 15 策略 receipts）；FC-901 apply=NO-OP；零删除 → -d **T2 消费证据（accepted）**：真实链消费 artifact_read=['normalized']、journal 不变（producer=0）、旧 unbound 不复用；两个 FC-902 生产缺口修复（列 stamp a61dd35 + derived root 6a76000）。receipts: company-wiki/assurance/fc/FC-906/（×4 组）；can_accept exit 0 ×4 |

## 12. Phase 10：跨进程 E2E

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1001 | **accepted（2026-08-12，reviewer-fc1001-independent）** | FC-505、604、805、906 | revenue | 三根 fixture、corruption/lock/move variants、manifest hash、外写=0（feat e54d9e3：IsolatedLake 三根布局 + sidecars + v2 artifacts（列+metadata）+ 5 corruption 变体 + 确定性 manifest hash 无真实路径；9 tests + M-loc/M-hash 击杀；revenue 全量 411 passed 零失败；另修 FC-505 pre-existing 日期漂移 test-only；can_accept exit 0） |
| FC-1002 | **accepted（2026-08-12，reviewer-fc1002-independent）** | FC-1001 | revenue | revenue→filing→wiki 三进程 trace；边界 spy；process_count>=3（feat 2154032：真实三进程链测试 3 个（exact 零副作用/trace/DAG closure；psutil 确认 5 OS 进程超门限）；fixture 扩展：review receipts、security_master、wiki config、companies 移 wiki_root；M1 击杀；revenue 全量 414 passed 零失败；can_accept exit 0） |
| FC-1003 | **accepted（2026-08-12，reviewer-fc1003-independent-r3；三轮 review 闭环）** | FC-1002 | 三仓 | 95 scenario registry 全覆盖；无重复/遗漏/skip/伪绿色（机器覆盖门 scenario_coverage.py：SCENARIO 标注+receipts 并集、未来 Phase 显式 deferred、**required gaps=0**（87 covered+14 deferred）、ast.parse 编译验证标记文件；UJ-01/02/04/07 真实旅程测试；三仓 SCENARIO 标注；r1 F1（wiki marker SyntaxError）→r2 F2（guard 未密封）→r3 accepted；发现 filing-fetch legacy containment 拒 dayu 根（FC-1202 范围）；can_accept exit 0） |
| FC-1004 | pending | FC-1003 | 三仓 | PORT-01~03、安装态、Windows 中文/空格、Linux golden trace |
| FC-1005 | **accepted（2026-08-12，reviewer-fc1005-independent）→ Phase 10 COMPLETE** | FC-1004 | 三仓 | critical mutation kill=100%；chaos/fault injection 全绿（机器门 critical_mutation_gate.py：8 类 × ≥1 击杀证据（receipts + 证据文件）；M-latest 现场击杀（close_gap re-resolve 移除 → cg05/cg07 死，reviewer 重放确认）；chaos 证据（FC-405/804）；gate 8/8 OK；revenue 434 passed 零失败；can_accept exit 0；1 low 非阻塞（hash 归一化）） |

## 13. Phase 11：动态审核

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1101 | **accepted（2026-08-12，reviewer-fc1101-independent-r3；三轮 review）** | FC-1005 | 三仓/revenue | current-triplet required gate；T0/T1/quality/architecture 全集（manifest 驱动 CI sibling checkout 替代硬编码 pin；commits-exist 防伪门；pin 扫描 7+hex + 负向控制；r1 F1 manifest 滞后/r2 F2 0x08 正则——r3 accepted；can_accept exit 0） |
| FC-1102 | **accepted（2026-08-12，reviewer-fc1102-independent）** | FC-1101 | revenue + Windows runner | 每日 T2、AUD-01~05/08、只读 fingerprint、隔离 audit output（tools/daily_t2_runner.py：mode=ro+query_only；triplet/samples/scan health/legacy hits/latency/roots fingerprint/trend deltas；隔离报告；非零退出；生产冒烟 0.011s、scan errors 212（vs 基线 155 真实恶化已入跟踪）；4 tests + M1 击杀；revenue 443 passed 零失败；P3 findings F1-F3 记 Phase 11 exit gate 前置；can_accept exit 0） |
| FC-1103 | **accepted（2026-08-12，reviewer-fc1103-independent）** | FC-1101、805 | filing/revenue | 每周 T3、AUD-06、CN/HK/US、首次/二次零下载（weekly_t3_runner.py：无 --force=BLOCKED exit 2（告警非绿）；--force 跑真实 FC-805 套件（reviewer 亲跑 CN/HK/US 214s 全绿）；隔离报告；guard-bypass mutation 击杀；revenue 446 passed 零失败；can_accept exit 0） |
| FC-1104 | pending | FC-1102、1103 | revenue | dashboard/ledger、freshness/SLO/triplet gate、历史不可覆盖 |
| FC-1105 | **accepted（2026-08-12，reviewer-fc1105-independent）→ Phase 11 COMPLETE** | FC-1104 | revenue | AUD-01~08 故障注入；每类漏报均让 release 非零退出（fault-injection 矩阵：陈旧 manifest/缺样本/policy 漂移（关闭 FC-1102 F1）/Dropbox sidecar/健壮性；IsolatedLake +runtime_policy；5 fault tests + 2 mutations；revenue 456 passed 零失败；can_accept exit 0） |

## 14. Phase 12：代码质量

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1201 | **accepted（2026-08-12，reviewer-fc1201-independent；can_accept exit 0）→ Phase 12 启动，FCAP 59/71** | FC-701、1005 | company-wiki | root-hardcode frozen ratchet（FC-304 门 allowlist 精确 pin，新增文件→测试红）+ 注释清理（resolver/observability/entity_resolver 移出 allowlist，零行为）；5 新 contract 测试；EX-08 保持绿；全量 wiki 2241 passed/0 failed；M1（allowlist 涨）+M2（token 删）双杀。reviewer 干净 worktree 重放（RED-at-base 第二 worktree F-6 规则）。v1 scanner 7 分支 = R9 backlog；canonical_writer/cli DEFERRED（loader-blocked follow-up）。feat `0c6c2c9` + receipt `8817521` + closure `b3b45aa` |
| FC-1202 | accepted（2026-08-12，reviewer-fc1202-independent；Interpretation A 见 findings 58） | FC-1201 | 三仓 | 单一 RootPolicy；重复 allowlist=0；隐式 sibling path=0 |
| FC-1203 | accepted（2026-08-12，reviewer-fc1203-independent；Interpretation A 修订版见 findings 59 + 03_change_contract） | FC-1202 | 三仓 | dead production symbols、依赖环、test-only helper；行为场景无回归 |
| FC-1204 | accepted（2026-08-13，reviewer-fc1204-independent r3 三轮 review；a/b/c 子链见 findings 60/61 + WU 卡） | FC-1203 | 三仓 | coverage/type/complexity ratchet；阈值下降 mutation/CI 必败 |
| FC-1205 | accepted（2026-08-13，reviewer-fc1205-independent r1） | FC-1204 | 三仓 | 统一错误 schema、PORT-01~03、日志脱敏、编码失败关闭 |

## 15. Phase 13：运行质量

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1301 | pending | FC-704、905 | 三仓 | 版本化 reason taxonomy；trace 完整且路径/内容脱敏 |
| FC-1302 | pending | FC-1301 | company-wiki | OPS-01、AUD-05；scan health 阈值和非零退出 |
| FC-1303 | pending | FC-703、1302 | company-wiki | 49GB catalog SLO；p50/p95/p99、内存、锁等待、回归预算 |
| FC-1304 | pending | FC-1303 | company-wiki/filing | OPS-02/03、DL-08/09、MIG-07；容量/并发/恢复 |

## 16. Phase 15：总关闭

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1501 | pending | Phase 14 R9 | revenue | 所有 FC/scenario/receipt/freshness/triplet 的机器 closure |
| FC-1502 | pending | FC-1501 | 独立 reviewer | CodeGraph 反向审查、旁路/硬编码/skip/人工步骤=0 |
| FC-1503 | pending | FC-1502 | 独立 reviewer + 三仓 | UJ-01~08、三 root-only、CN/HK/US、Windows 真实旅程 |
| FC-1504 | pending | FC-1503 | release owner | 两个>=24h T2、最近7天 T3、rollback/re-activate 演练 |
| FC-1505 | pending | FC-1504 | closure validator | 六目标 evidence map、最终 ledger exit=0、状态更新为 complete |

## 17. 阶段放行规则

Phase 14 的 R0–R9 是发布波次而非 FC，不计入 71 个 FC；每波必须消费前置 Phase release package 并生成独立 release receipt。一个 Phase 只有在本表中其全部 FC=`accepted`、对应 mandatory scenarios 全部通过、`unresolved_findings` 为空且独立 phase review=`pass` 后才能放行。

