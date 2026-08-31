# 三仓完成计划全景图（2026-08-16 恢复会话快照）

> 数据来源：`assurance/unified_completion/state.json`（机器状态权威）+ 冻结注册表（25 CA + 92 ZR）+ README §6 A→J 顺序表。

## 总工作量

| 维度 | 数量 |
|---|---|
| 注册工作单元 | **117**（CA 25 + ZR 92） |
| 场景（验收 oracle） | **197**（旧 95 + 新 102，不相交） |
| 阶段 | **10**（A0 基线、B 证据/闭合、C 真只读契约、D 生命周期/roots、E broker/处理、F revenue/矿业、G 真实 E2E、H 动态审核、I 渐进发布、J 终验关闭） |
| 仓库 | 3（revenue-forecast 消费者、filing-fetch 编排、company-wiki 数据湖） |
| 唯一执行入口 | `audit_review/README.md`（§0 游标 + 机器 DAG） |

## 阶段地图（✓=全部完成，◐=进行中，○=未开始）

| 阶段 | 单元 | 状态 | 关键内容 |
|---|---|---|---|
| A0 基线与锁 | CA-001~004 + ZR-001~004（8） | **✓ 8/8** | 输入 hash、triplet、锁/CAS、机器状态、CodeGraph、legacy 处置、drift 重放、golden corpus |
| B Evidence/Closure 2.0 | CA-101~109（9） | **✓ 9/9** | 状态机、receipt、revision、command、scenario、ledger、三仓 closure、30 mutation、legacy gate |
| C 真只读与契约 | ZR-101~105 + ZR-201~206（11） | **✓ 11/11** | taxonomy✓、T1 runner✓、validator✓、质量基线✓、CI 契约✓、CatalogReader✓、typed queries✓、生产重接✓、锁 taxonomy✓、retry✓、SLO✓（ZR-206 全 closure） |
| D 生命周期、roots、时效 | ZR-301~307 + ZR-401~409（16） | **✓ 16/16** | 来源状态机✓、prompt-injection guard✓、readiness 决策图✓、producer journal✓、legacy 迁移验收✓、role DAG property✓、filing 分阶段 envelope✓、RootPolicy 3.0✓、adapter 路由契约✓（ZR-402）、dedupe/resolver 泛化✓（ZR-403）、envelope 加性✓（ZR-404）、policy containment✓（ZR-405 跨仓）、gap-plan 矩阵✓（ZR-406）、authorization-bound close-gap✓（ZR-407）、cross-process single-flight✓（ZR-408）、**future_lake 配置接入 + 三真实 root 旅程✓（ZR-409，阶段 D 出口）** |
| E broker/web/处理需求 | ZR-501~510（+ZR-304~306 迁移部分）（10） | ○ 0/10 | 七份研报语义产物、多实体错归、表格保真、ProcessingDemand |
| F revenue 与矿业 | ZR-601~611 + ZR-701~713（24） | ○ 0/24 | 矿山事实、会计桥、generator/validate/draft/formal、回测置信度 |
| G 真实 E2E | ZR-801~806（6） | ○ 0/6 | 三真实 root 用户旅程全绿 |
| H 动态审核与质量 | ZR-901~907 + CA-201~206（13） | ○ 0/13 | current-triplet PR 门、Daily/Weekly/Monthly、alert drill |
| I 渐进发布 | ZR-1001~1008 + CA-304（9） | ○ 0/9 | cohort 灰度、legacy 删除 |
| J 独立终验与关闭 | CA-301~306（替代 ZR-1101~1105）（6） | ○ 0/6 | 六目标 machine pass、旧计划关闭 |

## 当前进度

- **accepted 43 / 117（约 37%）**：A0 8 + B 9 + C 11 + D 16。
- **阶段 D（16 单元）✅ 16/16 完成（阶段 D 出口达成）**：ZR-301~307 + ZR-401~409 全 closure。
- **ZR-402~409 closure 摘要**：adapter 路由契约（36 tests）→ dedupe/resolver 泛化（7 tests）→ envelope 加性（11 tests）→ 跨仓 policy containment（18 tests，wiki+filing）→ gap-plan 正交矩阵（39 collected）→ authorization-bound close-gap（actionable union）→ cross-process single-flight oracle → **future_lake 配置接入 + 三真实 root 只读旅程（10 tests，产品 core diff=0）**。
- **机器游标**：`current_phase=E_broker_web_processing`，`current_next=ZR-501`。
- **场景**：197/197 unsatisfied（按设计：它们是各阶段验收 oracle，随阶段完成翻绿）。
- **已登记跨卡 findings（带 successor）**：BYPASS-001/MISSING-001→phase C/D、CI-001/LEGACY-CALLER-001→CA-201、ZR102-F1(P1 未授权 exact 下载)→ZR-407（已闭）、ZR103-REV-001(P2 receipt 语义)→CA-301、ZR203-IMPL-003(duplicates 遗留)→ZR-206（已闭）、ZR105-GAP-001~004→CA-201、**ZR401-REV-003(config 3.0 切换)→CA-303/阶段 I（ZR-409 再延期：产品代码变更违反 core-diff=0）**、ZR405-REV-002(close-gap 响应内嵌 policy_export)→ZR-407（已闭，随行复核未纳入，留 ZR-501+ 或 ADR）、mypy 基线 2 错误→后续质量卡/CA-201、ZR407-IMPL-005(owner 环境 18 失败)→后续环境 remediation、ZR409-REV-004(Dropbox 独有 annual 无 capture-ready——数据现状)→ZR-802/806 T3。
- **提交**：revenue fcap 本地 ~85 提交（含 closure）；company-wiki ~25 提交（…/71aa798/eb3aa79/726d63d）；filing 4 提交（…/3087f28/5a1c18f）；均未 push。三仓 HEAD：revenue（ZR-409 closure 提交进行中）、wiki 726d63d、filing 5a1c18f。

## 恢复路线（下一卡开始）

1. ZR-206 收尾（T2 探测证据落 JSON → implementer receipt → state walk → 独立复核 → closure）——恢复清单见 progress.md 停点节。
2. ZR-206 closure 后 C 阶段出口达成（READ-01~12 全绿 + SLO 冻结 + T2 零写指纹）→ D（ZR-301 首卡）。
3. D（ZR-301~409）→ E → F → G → H → I → J，每卡同一纪律：preflight→RED→最小实现→四层测试→receipt→独立复核→closure。

## 停点快照（2026-08-16 用户指示：全部停止，下次继续）

- **accepted 29/117**：CA-001~004、CA-101~109、ZR-001~004、ZR-101~105、ZR-201~205。
- **ZR-206（阶段 C 出口卡）**：preflight_locked；hermetic 8 测试绿；T2 真实 49.62GB 探测首轮 = SLO 门全过 + index 断言过 + **指纹漂移未决**（证据 JSON 已落盘）；worker 已恢复 enabled。
- **机器游标**：current_phase=C_read_only_and_contracts，current_next=ZR-206。
- **恢复第一步**：T2 指纹 diff 定位 → 重跑探测 → receipt/复核/closure → C 出口 → D（ZR-301）。

## 2026-08-17 阶段 D 快照

- **accepted 33/117**：A0 8 + B 9 + C 9（ZR-101~105,201~206）+ D 7（ZR-301~304）。
- 阶段 D 地图：ZR-301~307 + ZR-401~409（16 单元）→ **◐ 4/16**（301/302/303/304 closure；305 复核中；306/307/401~409 pending）。
- 机器游标：D_lifecycle_roots_freshness / ZR-305。
- 恢复第一步：收 ZR-305 复核 → closure → ZR-306（role DAG 最小失效，property tests）。

## 2026-08-17 阶段收尾快照

- **accepted 34/117**：A0 8 + B 9 + C 9 + D 8（ZR-301~305 closure；ZR-306 实现完成待复核）。
- 阶段 D 地图（16 单元）：**◐ 5/16 closure + 1 实现完成**（301~305 ✓；306 实现✓；307、401~409 pending）。
- 机器游标：D_lifecycle_roots_freshness / ZR-306。
- 恢复第一步：ZR-306 receipt → 独立复核 → closure → ZR-307 → ZR-401~409。

## 2026-08-18 收尾快照（用户指示：收尾并更新全部 planning docs 后停止）

- **accepted 36/117（约 31%）**：A0 8 + B 9 + C 11 + D 8。
- 阶段 D 地图（16 单元）：**◐ 8/16**——ZR-301~307 + ZR-401 全 closure（来源状态机/guard/决策图/journal/legacy 验收/role DAG/envelope/RootPolicy 3.0）；ZR-402~409 pending。
- ZR-401 closure 详情：wiki 251615e（12 tests，787 unit 绿）；复核 accepted（5 非阻断 findings；REV-003 生产 config 3.0 切换显式延期→ZR-402/403 或阶段 D 出口）；reviewer receipt canonical 97e562bd…。
- 机器游标：D_lifecycle_roots_freshness / **ZR-402**（未领取）。
- 三仓 HEAD（本地 fcap，未 push）：revenue fd017c9、wiki 251615e、filing df66796。
- 恢复第一步：ZR-402（adapter registry，`adapters/registry.py` 已有基础）→ ZR-403（dedupe/resolver 泛化）→ ZR-404~409（envelope/authorization/时效/下载）→ 阶段 D 出口 → E（ZR-501~510）。

## 2026-08-18 阶段 D 收官快照（用户指示：收官并更新全部 planning docs 后停止）

- **accepted 41/117（约 35%）**：A0 8 + B 9 + C 11 + D 13。
- 阶段 D 地图（16 单元）：**◐ 13/16**——ZR-301~307 + ZR-401~406 全 closure（来源状态机/guard/决策图/journal/legacy 验收/role DAG/envelope/RootPolicy 3.0/adapter 路由/dedupe 泛化/envelope 加性/policy containment/gap-plan 矩阵）；**ZR-407~409 pending**。
- 本轮五卡：ZR-402（wiki 57cd72e，36 tests，M1~M9 击杀表）→ ZR-403（wiki 87ee0ac，7 tests，四上下文+health→priority+shuffle）→ ZR-404（wiki f45f7ed，11 tests，envelope 加性+脱敏）→ ZR-405（wiki e56eb5f + filing 3087f28，18 tests，跨仓 policy containment）→ ZR-406（wiki 45ae721，39 collected，30 格矩阵；首轮 changes_required → delta accepted）。
- 机器游标：D_lifecycle_roots_freshness / **ZR-407**（未领取）。
- 三仓 HEAD（本地 fcap，未 push）：revenue c9a3add（ZR-406 closure 提交进行中）、wiki 45ae721、filing 3087f28。
- 恢复第一步：ZR-407（authorization-bound GapPlan/CloseGap，filing+wiki，含 ZR405-REV-002 后续）→ ZR-408（下载执行/single-flight）→ ZR-409（future_lake 生产切换，阶段 D 出口）→ E（ZR-501~510）。

## 2026-08-18 晚快照（ZR-407/408 closure → 阶段 D 剩 ZR-409）

- **accepted 42/117（约 36%）**：A0 8 + B 9 + C 11 + D 14。
- 阶段 D 地图（16 单元）：**◐ 14/16**——ZR-301~307 + ZR-401~408 全 closure；**ZR-409 pending**。
- ZR-407 closure：authorization-bound close-gap actionable union（missing+newer_revision；wiki bdffc54 + filing 5a1c18f，ensure 只读路径修复）；复核 accepted。
- ZR-408 closure：cross-process single-flight oracle 验收（产品零改动；wiki 71aa798，22 contract + 787 unit）；复核 accepted（3 info）。
- 机器游标：D_lifecycle_roots_freshness / **ZR-409**（未领取；阶段 D 出口卡：future_lake 生产切换，只改配置/adapter fixture、产品 core diff=0）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-408 closure 提交进行中）、wiki 71aa798、filing 5a1c18f。
- 恢复第一步：ZR-409（配置新增 future_lake + 三真实 root 用户旅程，EX/LT/DL/IDX/UJ 场景全绿）→ 阶段 D 出口 → E（ZR-501~510）。

## 2026-08-19 阶段 D 出口快照（ZR-409 closure → 阶段 E 启动）

- **accepted 43/117（约 37%）**：A0 8 + B 9 + C 11 + D 16。
- **阶段 D ✅ 16/16 完成（出口达成）**——ZR-301~307 生命周期子组 + ZR-401~409 roots/时效/下载 全 closure。
- ZR-409 closure：生产 config 第四根 future_lake（仅配置接入，产品 core diff=0）+ 三真实 root 只读旅程（companies 紫金 exact / dayu-only 金斯瑞 exact（companies 无同 hash 前提钉死）/ Dropbox 星环 fail-closed capture_incomplete——生产数据诚实现状）+ EX-08 生产形状 + 场景映射钉死；复核 accepted（5 info，REV-001/002 tidy）→ closure→**ZR-501**。
- 机器游标：**E_broker_web_processing** / ZR-501（未领取）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-409 closure 提交进行中）、wiki 726d63d、filing 5a1c18f。
- 恢复第一步：ZR-501（阶段 E 首卡：七份研报语义产物/多实体错归/表格保真/ProcessingDemand）。
## 2026-08-19 阶段 F 启动快照（ZR-701 closure → ZR-702）

- **accepted 54/117**：A0 8 + B 9 + C 11 + D 16 + E 10（阶段 E 全闭）+ F 1（ZR-701）。
- **阶段 E ✅ 10/10 完成（出口达成）**：ZR-501~510（broker metadata contract → sidecar 角色分离+首页身份 → 多实体 attribution guard → 页码保真 → typed table → section/chunk/fact → ProcessingDemand → scheduler 公平性 → HTML capture 身份门 → chunk attribution 错归=0）。
- ZR-701 closure：F1 入口（prepare_forecast 纯函数 + validate-only 零写 + draft/validated artifact + ProcessingDemand 提交）；首轮 changes_required（复杂度 ratchet 21>17）→ ff7429e 修复 → delta accepted。
- 机器游标：**F_revenue_mining** / ZR-702（未领取）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-701 closure 提交进行中）、wiki 26a6b22、filing 5a1c18f。
- 阶段 F 地图：◐ 1/13（ZR-701 已闭；F1：ZR-702~706/710；F2：ZR-601~611 先 ZR-610 会计 ADR；合流 ZR-609/709）。
- 恢复第一步：ZR-702（F1 后续）。

## 2026-08-21 阶段 F 快照（F1 全闭 → F2：ZR-601/602 closure，用户指示停止）

- **accepted 62/117（约 53%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 9（ZR-701~706/710 + ZR-601/602）。
- **F1 ✅ 7/7 完成（出口达成）**：ZR-701~706 + ZR-710（prepare_forecast/draft-formal/validate-only 门/schema 真源/文档清理/selector 契约/publication 事务）。
- **F2 双分支推进**：ZR-601（asset facts 数学契约，test-only 10 tests）closure；ZR-602（asset facts basis 契约：resource≠reserve 隔离 + ownership/标准/measurement date 加性 basis + 族内单位一致性门）closure——首轮 reviewer accepted（22/22 对抗断言），1 minor REV-001（unhashable ownership_basis 抛 TypeError）→ delta c9b0cfc 修复 + delta accepted；REV-001→info，REV-002~004 info。
- 机器游标：**F_revenue_mining** / **ZR-603**（未领取）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-602 closure commit 待提交；实现 cb82620 + delta c9b0cfc）、wiki 26a6b22、filing 5a1c18f。
- 阶段 F 地图：◐ 9/13（F1 7/7 闭 + F2 ZR-601/602；F2 剩余 ZR-603~608/611/707/711~713 + ZR-610 ADR）。
- **停止点（用户指示：本卡跑完后更新全部 planning docs 后停止）**：恢复第一步 = ZR-603（F2 ownership/consolidation timeline，DAG 解锁；README 阶段表提 ZR-610 会计 ADR 但 DAG 权威）。

## 2026-08-22 恢复快照（用户指示"继续"：ZR-603 closure → ZR-604）

- **accepted 63/117（约 54%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 10（ZR-701~706/710 + ZR-601~603）。
- **ZR-603 closure**：ownership/consolidation timeline + geography hierarchy（b52568b + delta 03d716e；29 tests；首轮 changes_required → delta accepted；REV-005 minor 登记 ZR-607 后续）；reviewer accepted，closure→ZR-604。
- 机器游标：**F_revenue_mining** / **ZR-604**（未领取）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-603 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。
- 阶段 F 地图：◐ 10/13（F1 7/7 闭 + F2 ZR-601~603；F2 剩余 ZR-604~608/611/707/711~713 + ZR-610 ADR）。

## 2026-08-22 ZR-604 实施快照

- **accepted 64/117 + ZR-604 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 10（ZR-701~706/710 + ZR-601~603）+ ZR-604 待复核/closure。
- **ZR-604 实施**：revenue 2636e55（冲突保存与人工 review：双 assertion + resolution status，11 tests，+238 行 3 文件）；全量 585+106 绿；state triplet_green；implementer receipt canonical 58159699；独立复核 reviewer-zr604-independent 运行中。
- 机器游标：**F_revenue_mining** / ZR-604（复核中）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 2636e55（ZR-604 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。
- 阶段 F 地图：◐ 10/13 + ZR-604 待闭（F1 7/7 闭 + F2 ZR-601~603 闭 + ZR-604 实施中；F2 剩余 ZR-605~608/611/707/711~713 + ZR-610 ADR）。

## 2026-08-22 ZR-604 closure 快照

- **accepted 65/117（约 55%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 11（ZR-701~706/710 + ZR-601~604）。
- **ZR-604 closure**：reviewer accepted（17/17 对抗断言，1 minor REV-001 null resolution_status 语义——登记后续）；closure→ZR-610。
- 机器游标：**F_revenue_mining** / **ZR-610**（未领取；会计 ADR 冻结——"无产品代码"卡）。
- 阶段 F 地图：◐ 11/13（F1 7/7 闭 + F2 ZR-601~604 闭；剩余 ZR-605~608/611/707/711~713 + ZR-610）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-604 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-610 closure 快照

- **accepted 66/117（约 56%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 12（ZR-701~706/710 + ZR-601~604 + ZR-610）。
- **ZR-610 closure**：独立会计 reviewer accepted（8 条决策全部通过会计合理性审查，2 info 非阻断）；closure→ZR-605。
- 机器游标：**F_revenue_mining** / **ZR-605**（未领取；MineYearOperation 输入合同——DAG 已解锁 ZR-605）。
- 阶段 F 地图：◐ 12/13（F1 7/7 闭 + F2 ZR-601~604+610 闭；剩余 ZR-605~608/611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-610 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-605 实施快照

- **accepted 66/117 + ZR-605 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 12（ZR-701~706/710 + ZR-601~604 + ZR-610）+ ZR-605 待复核/closure。
- **ZR-605 实施**：revenue b02f17b（MineYearOperation 输入合同：七字段必填 gap-on-missing + derive_saleable_volume + resource 模型驱动映射，30 tests）；全量 615+106 绿；state triplet_green；implementer receipt canonical 3f780700；独立复核 reviewer-zr605-independent 运行中。
- 机器游标：**F_revenue_mining** / ZR-605（复核中）。
- 阶段 F 地图：◐ 12/13 + ZR-605 待闭（F1 7/7 闭 + F2 ZR-601~604+610 闭 + ZR-605 实施中；剩余 ZR-606~608/611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue b02f17b（ZR-605 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-605 closure 快照

- **accepted 67/117（约 56%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 13（ZR-701~706/710 + ZR-601~605 + ZR-610）。
- **ZR-605 closure**：reviewer accepted（7/7 对抗断言组，1 minor inf 值未拒——登记 ZR-606 后续）；closure→ZR-606。
- 机器游标：**F_revenue_mining** / **ZR-606**（未领取；商业量价层）。
- 阶段 F 地图：◐ 13/13 进度过半（F1 7/7 闭 + F2 ZR-601~605+610 闭；剩余 ZR-606~608/611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-605 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-606 实施快照

- **accepted 67/117 + ZR-606 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 13（ZR-701~706/710 + ZR-601~605 + ZR-610）+ ZR-606 待复核/closure。
- **ZR-606 实施**：revenue cf3ada7（商业量价层：price/payability/TC-RC/premium/byproduct/FX/royalty 带 provenance，finite_number 数值加固，不重复计价，敏感性重算，24 tests）；全量 639+106 绿；state triplet_green；implementer receipt canonical 64f99205；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-606（复核中）。
- 阶段 F 地图：◐ 13/13 + ZR-606 待闭（F1 7/7 闭 + F2 ZR-601~605+610 闭 + ZR-606 实施中；剩余 ZR-607/608/611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue cf3ada7（ZR-606 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-606 closure 快照

- **accepted 68/117（约 57%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 14（ZR-701~706/710 + ZR-601~606 + ZR-610）。
- **ZR-606 closure**：reviewer accepted（首轮 → REV-001 minor delta 47fe715 → delta 复审 staged-not-committed → 落地后 accepted）；implementer receipt 重封 b07a951b；closure→ZR-607。
- 机器游标：**F_revenue_mining** / **ZR-607**（未领取；ownership/consolidation/internal flow 会计桥）。
- 阶段 F 地图：◐ 14/13 进度过半（F1 7/7 闭 + F2 ZR-601~606+610 闭；剩余 ZR-607/608/611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-606 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-607 实施快照

- **accepted 68/117 + ZR-607 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 14（ZR-701~706/710 + ZR-601~606 + ZR-610）+ ZR-607 待复核/closure。
- **ZR-607 实施**：revenue 073fd4d（internal flow 会计桥：可追踪 InternalFlow + gross/net elimination 桥，29 tests）；全量 674+106 绿；state triplet_green；implementer receipt canonical 05c102fb；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-607（复核中）。
- 阶段 F 地图：◐ 14/13 + ZR-607 待闭（F1 7/7 闭 + F2 ZR-601~606+610 闭 + ZR-607 实施中；剩余 ZR-608/611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 073fd4d（ZR-607 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-608 实施快照

- **accepted 69/117 + ZR-608 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 15（ZR-701~706/710 + ZR-601~607 + ZR-610）+ ZR-608 待复核/closure。
- **ZR-608 实施**：revenue 3081967（asset→segment→group reconciliation：容差门 + 诚实 fallback + 防伪收入，11 tests；ZR-607 closure 文件合入本 commit——流程偏差）；全量 685+106 绿；state triplet_green；implementer receipt canonical d5497096；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-608（复核中）。
- 阶段 F 地图：◐ 15/13 + ZR-608 待闭（F1 7/7 闭 + F2 ZR-601~607+610 闭 + ZR-608 实施中；剩余 ZR-611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 3081967（ZR-608 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-608 closure 快照

- **accepted 70/117（约 59%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 16（ZR-701~706/710 + ZR-601~608 + ZR-610）。
- **ZR-608 closure**：reviewer accepted（46/46 对抗断言，零 blocking，5 info/minor）；closure→ZR-611。
- 机器游标：**F_revenue_mining** / **ZR-611**（未领取；通用多矿合成 E2E）。
- 阶段 F 地图：◐ 16/13 进度过半（F1 7/7 闭 + F2 ZR-601~608+610 闭；剩余 ZR-611/707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-608 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-611 实施快照

- **accepted 70/117 + ZR-611 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 16（ZR-701~706/710 + ZR-601~608 + ZR-610）+ ZR-611 待复核/closure。
- **ZR-611 实施**：revenue 288ac88（通用多矿合成 E2E：八类场景全链确定性可重算，test-only 11 tests 零产品改动；ZR-608 closure 文件合入本 commit——流程偏差第二次）；全量 696+106 绿；state triplet_green；implementer receipt canonical 9667ac1c；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-611（复核中）。
- 阶段 F 地图：◐ 16/13 + ZR-611 待闭（F1 7/7 闭 + F2 ZR-601~608+610 闭 + ZR-611 实施中；剩余 ZR-707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 288ac88（ZR-611 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-611 closure 快照

- **accepted 71/117（约 60%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 17（ZR-701~706/710 + ZR-601~608 + ZR-610/611）。
- **ZR-611 closure**：reviewer accepted（独立数学重算 + 八类非空洞 + 确定性位级一致；1 minor + 5 info）；closure→ZR-609。
- 机器游标：**F_revenue_mining** / **ZR-609**（未领取；F2 合流：紫金 pilot + 第二家公司泛化）。
- 阶段 F 地图：◐ 17/13 进度过半（F1 7/7 闭 + F2 ZR-601~608+610/611 闭；剩余 ZR-609 合流 + ZR-707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-611 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-609 实施快照

- **accepted 71/117 + ZR-609 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 17（ZR-701~706/710 + ZR-601~608 + ZR-610/611）+ ZR-609 待复核/closure。
- **ZR-609 实施**：revenue e541d55（紫金 pilot + 第二家泛化：三主要资产逐矿可回答 + 纯金矿商泛化零硬编码，test-only 9 tests 零产品改动；父 404a2bb = ZR-611 closure 独立落地——修正无第三次流程偏差）；全量 705+106 绿；state triplet_green；implementer receipt canonical ee6dd908（初版修正）；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-609（复核中）。
- 阶段 F 地图：◐ 17/13 + ZR-609 待闭（F1 7/7 闭 + F2 ZR-601~608+610/611 闭 + ZR-609 实施中；剩余 ZR-707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue e541d55（ZR-609 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-22 ZR-609 closure 快照（停止点）

- **accepted 72/117（约 61%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 18（ZR-701~706/710 + ZR-601~609 + ZR-610/611）。
- **ZR-609 closure**：reviewer accepted（手算独立重算 + 25 项非空洞 + 零硬编码 tokenize 扫描；2 minor REV-001/002 已修正 + 3 info）；closure→ZR-711。
- 机器游标：**F_revenue_mining** / **ZR-711**（未领取；additive schema 3.8 opt-in + 3.7 兼容/converter）。
- 阶段 F 地图：◐ 18/13 进度过半（F1 7/7 闭 + F2 ZR-601~609+610/611 闭；剩余 ZR-707/711~713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-609 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。
- **停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：恢复第一步 = ZR-711（F2 additive schema 3.8 opt-in，DAG 已解锁）→ ZR-707（mixed recognition/gross-net）→ ZR-712/713（confidence 反博弈/rolling-origin backtest）。

## 2026-08-23 ZR-711 实施 + delta 修复快照（停止点）

- **accepted 72/117 + ZR-711 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 18（ZR-701~706/710 + ZR-601~609 + ZR-610/611）+ ZR-711 待 closure。
- **ZR-711 实施**：revenue b0d7291 + delta e75debb（additive schema 3.8 opt-in：3.8 词汇+EMIT、版本门 {3.7,3.8}、validate_operating_units 复用 validate_mine_year_operation、schema_optin converter 三函数、15 tests；REV-001 capture-integrity gate 修复——document.py:606 `==3.7`→`in {3.7,3.8}`）；全量 720+106 绿；implementer receipt canonical f273d1ee（初版修正中）；reviewer accepted（delta 复审通过）。
- 机器游标：**F_revenue_mining** / ZR-711（closure 待完成）。
- 阶段 F 地图：◐ 18/13 + ZR-711 待闭（F1 7/7 闭 + F2 ZR-601~609+610/611 闭 + ZR-711 delta 通过；剩余 ZR-707/712/713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue e75debb（ZR-711 delta commit）、wiki 26a6b22、filing 5a1c18f。
- **停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：恢复第一步 = ZR-711 closure → ZR-707（mixed recognition/gross-net）→ ZR-712/713（confidence 反博弈/rolling-origin backtest）。

## 2026-08-23 ZR-711 closure 快照（最终停止点）

- **accepted 73/117（约 62%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 19（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711）。
- **ZR-711 closure**：reviewer changes_required（REV-001 blocking：capture-integrity 门只认 3.7）→ delta e75debb 修复 + delta accepted（REV-001→resolved）；closure→ZR-707。
- 机器游标：**F_revenue_mining** / **ZR-707**（未领取；mixed recognition/gross-net）。
- 阶段 F 地图：◐ 19/13 进度过半（F1 7/7 闭 + F2 ZR-601~609+610/611+711 闭；剩余 ZR-707/712/713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-711 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。
- **最终停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：恢复第一步 = ZR-707 → ZR-712/713。

## 2026-08-23 ZR-707 实施快照

- **accepted 73/117 + ZR-707 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 19（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711）+ ZR-707 待复核/closure。
- **ZR-707 实施**：revenue fdb560e（mixed recognition/gross-net + multi-commodity product matrix，13 tests）；全量 733+106 绿；state triplet_green；implementer receipt canonical 91aefa2c；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-707（复核中）。
- 阶段 F 地图：◐ 19/13 + ZR-707 待闭（F1 7/7 闭 + F2 ZR-601~609+610/611+711 闭 + ZR-707 实施中；剩余 ZR-712/713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue fdb560e（ZR-707 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-23 ZR-707 closure 快照

- **accepted 74/117（约 62%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 20（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707）。
- **ZR-707 closure**：reviewer accepted（11/11 对抗断言，4 info）；closure→ZR-708。
- 机器游标：**F_revenue_mining** / **ZR-708**（未领取；重验不可变 snapshot/backtest 基础接线）。
- 阶段 F 地图：◐ 20/13 进度过半（F1 7/7 闭 + F2 ZR-601~609+610/611+711+707 闭；剩余 ZR-708/712/713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-707 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-23 ZR-708 实施快照

- **accepted 74/117 + ZR-708 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 20（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707）+ ZR-708 待复核/closure。
- **ZR-708 实施**：revenue a9405f8（already_satisfied 重验：snapshot 不可变/accuracy→confidence 消费链/四层 hash，test-only 7 tests 零产品改动）；全量 740+106 绿；state triplet_green；implementer receipt canonical a9f5b356；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-708（复核中）。
- 阶段 F 地图：◐ 20/13 + ZR-708 待闭（F1 7/7 闭 + F2 ZR-601~609+610/611+711+707 闭 + ZR-708 实施中；剩余 ZR-712/713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue a9405f8（ZR-708 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-23 ZR-708 closure 快照

- **accepted 75/117（约 63%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 21（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708）。
- **ZR-708 closure**：reviewer accepted（对抗探针全过，4 info）；closure→ZR-712。
- 机器游标：**F_revenue_mining** / **ZR-712**（未领取；confidence 反博弈）。
- 阶段 F 地图：◐ 21/13 进度过半（F1 7/7 闭 + F2 ZR-601~609+610/611+711+707/708 闭；剩余 ZR-712/713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-708 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-23 ZR-712 实施快照

- **accepted 75/117 + ZR-712 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 21（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708）+ ZR-712 待复核/closure。
- **ZR-712 实施**：revenue 2373c42（版本化 ConfidencePolicy + 反博弈：policy 数据化 + 六类 mutations 检测 + rating caps 重算，15 tests）；全量 755+106 绿；state triplet_green；implementer receipt canonical fcc237aa；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-712（复核中）。
- 阶段 F 地图：◐ 21/13 + ZR-712 待闭（F1 7/7 闭 + F2 ZR-601~609+610/611+711+707/708 闭 + ZR-712 实施中；剩余 ZR-713）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 2373c42（ZR-712 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-23 ZR-712 closure 快照（最终停止点）

- **accepted 76/117（约 64%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 22（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708 + ZR-712）。
- **ZR-712 closure**：reviewer accepted（首轮 36 探针 → REV-001/002/004 minor delta 修复 1c04684 → delta 45 探针全过 accepted）；closure→ZR-713。
- 机器游标：**F_revenue_mining** / **ZR-713**（未领取；紫金 rolling-origin 历史回测）。
- 阶段 F 地图：◐ 22/13 进度过半（F1 7/7 闭 + F2 ZR-601~609+610/611+711+707/708+712 闭；剩余 ZR-713 → ZR-709 合流：紫金五年预测用户旅程终验）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-712 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。
- **最终停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：恢复第一步 = ZR-713 → ZR-709（F2 合流）→ 阶段 G（ZR-801~806）。

## 2026-08-23 ZR-713 实施快照
- **accepted 76/117 + ZR-713 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 22（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708 + ZR-712）+ ZR-713 待复核/closure。
- **ZR-713 实施**：revenue cb34700（rolling-origin 引擎：严格 as-of 无 future actual、company/segment/mine-volume 三层、四层 immutable hash、cap 不伪造 metrics，10 tests）；全量 768+106 绿；state triplet_green；implementer receipt canonical 57c1d269；独立复核运行中。
- 机器游标：**F_revenue_mining** / ZR-713（复核中）。
- 阶段 F 地图：◐ 22/13 + ZR-713 待闭（F1 7/7 闭 + F2 ZR-601~609+610/611+711+707/708+712 闭；剩余 ZR-713 → ZR-709 合流）。
- 三仓 HEAD（本地 fcap，未 push）：revenue cb34700（ZR-713 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 2026-08-23 ZR-713 closure 快照（最终停止点）
- **accepted 77/117（约 65%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 23（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708 + ZR-712 + ZR-713）。
- **ZR-713 closure**：reviewer 首轮 changes_required（REV-001 blocking 三层非独立评估 + REV-002 minor hash 未绑 level/as_of）→ delta 3479718（segment 独立 wape、mine-volume ZR-605 契约 fail-closed、record 绑定 {level,as_of}、snapshot_id=快照身份；15 tests，全量 773+106，pre-commit 776+106 + E2E PASS）→ delta accepted（21/21 探针）；closure→ZR-709。
- 机器游标：**F_revenue_mining** / **ZR-709**（未领取；F2 合流：紫金五年预测用户旅程终验）。
- 阶段 F 地图：◐ 23/13 进度过半（F1 7/7 闭 + F2 ZR-601~609+610/611+711+707/708+712+713 闭——F2 常规链全闭；仅剩 ZR-709 合流终验）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-713 closure commit 待提交，实现 cb34700 + delta 3479718）、wiki 26a6b22、filing 5a1c18f。
- **最终停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：恢复第一步 = ZR-709（F2 合流）→ 阶段 G（ZR-801~806）。

## 2026-08-23 ZR-709 closure 快照（F 阶段全闭 → 进入 G）
- **accepted 78/117（约 66%）**：F **24/24 全闭**（新增 ZR-709）；current_phase=G_real_e2e，current_next=ZR-802（ZR-801 machine registry 已由 CA-105 唯一实现吸收）。
- **ZR-709 closure**（F2 合流：紫金五年预测用户旅程终验 fixture）：revenue ac68807（test-only 9 tests，产品零改动）——source_preparation 真实子进程链复用 + 五年 FY2026-2030 契约代数推导（权益链 0.396）+ reconcile 10/10 + 诚实 gap + draft/formal 可渲染可重放；复核 accepted（12/12 探针，4 info）；reviewer receipt canonical 40206902。
- 阶段 F 出口达成：generator/validate/draft/formal 发布闭环 ✅、矿山会计桥或诚实 gap ✅、可信回测/置信度 ✅。

## 2026-08-23 阶段 G 连续推进快照（ZR-802~805 → 收尾停止）
- **accepted 82/117（约 69%）**：G 4/6（ZR-802/803/804/805）；current_next=**ZR-806**（收官卡）。
- **ZR-802 closure**（组合旅程 across roots）：revenue 1b55f6f（7 tests）——五状态 existing/missing/stale/conflict/partial + 二次幂等 + 八阶段投影；复核 accepted（11 探针）；canonical 051e4f64。
- **ZR-803 closure**（chaos 六类故障×幂等恢复）：revenue b14ac3c（6 tests）——锁/中断/磁盘/篡改/乱序/时钟；复核 accepted（13 探针）；canonical 7e305256。
- **ZR-804 closure**（平台与安装形态）：revenue be8405c（5 tests）——大小写变体/缺省配置 fail-closed/sync-first 身份/无 Windows-only 构造；回填 receipt 联合复核 accepted（A-V1~V5）；canonical 46850f67；**流程偏差：曾跳过 receipt 直接开 ZR-805，ZRR805-REV-002 抓出闭环**。
- **ZR-805 closure**（T3 下载授权语义）：revenue 3fc5f3e + delta 295f138（3 tests）——filing-fetch opt-in 唯一 owner、journal 零下载独立 oracle（非空洞注入证明）、单一下载器；首轮 accepted → REV-001/002 delta → accepted；delta receipt b3efb845。
- 全量基线：782 → 800 → **803 passed + 106 subtests**；sync MATCH 151。
- 三仓 HEAD（本地 fcap，未 push）：revenue 295f138、wiki 26a6b22、filing 5a1c18f。
- **最终停止点（用户指示：收尾并更新全部 planning docs 后停止）**：恢复第一步 = ZR-806（真实 T2 三 root/broker/artifact/mine/forecast 样本收官）→ 阶段 H（ZR-901/CA-201 起）。

## 2026-08-23 ZR-806 实施快照
- **accepted 82/117 + ZR-806 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 24 + G 4（ZR-802~805）+ ZR-806 待复核/closure。
- **ZR-806 实施**：revenue b716a81（真实 T2 三 root 样本套件：固定 5 样本唯一/新鲜（AUD2-05 缺失即 blocked）+ 三 root resolve 只读旅程（REUSED_EXACT ×3 + MISSING ×1 fail-closed）+ 零写指纹 + sidecar 契约绑定，10 tests）；全量 813+106 绿；state triplet_green；implementer receipt canonical 2dd046b5；独立复核运行中。
- 机器游标：**G_real_e2e** / ZR-806（复核中）。

## 2026-08-23 ZR-806 closure 快照（阶段 G 全闭 → 阶段 H 入口）
- **accepted 83/117（约 70%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 24 + **G 5/6 全闭**（ZR-802~806；ZR-801 由 CA-105 吸收）。current_phase=**H_dynamic_audit**，current_next=**ZR-902**。
- **ZR-806 closure**：reviewer-zr806-independent accepted（15 commands；独立复算样本 hash/声明匹配、AUD2-05 temp 变体缺失样本套件 fail（3 failed/7 passed）、resolve 复跑 + 指纹/catalog 行数不变、sidecar 逐字段、git diff 零产品改动、回归 30 + ruff + ratchet + 全量 813+106 复跑；2 info）；reviewer receipt canonical 5a9ddad4；closure→ZR-902。
- **CRLF 教训**：README CRLF → closure-advance CAS-CONFLICT（read_text().encode() LF hash vs manifest 原始字节 CRLF hash）→ README 转 LF + manifest CAS 重建（findings 43）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-806 closure commit 待提交，实现 b716a81）、wiki 26a6b22、filing 5a1c18f。
- **最终停止点（用户指示：收尾并更新全部 planning docs 后停止）**：恢复第一步 = ZR-902（阶段 H：实际调度每日 Windows T2）→ ZR-903/901（阶段 H）。
- **防双写漂移（README §14 规则，2026-08-22 起）**：`accepted N/117` 计数唯一真源 = `assurance/unified_completion/state.json`；本快照段不再手工维护计数（需要时引用 state.json），逐卡详情以 progress.md 为准。

## 2026-08-23 阶段 H~I closure 快照（ZR-907 → ZR-1004）
- **ZR-907 closure**（drift patrol，阶段 H 收官）：revenue 2d2ab75——tools/drift_patrol.py 扩展（schema '3.6' 字面门 + manifest-verify 聚合，七类检查）；reviewer accepted；**发现真实漂移 ZR907-FIND-001**（company-wiki config_doctor vs future_lake）；closure→ZR-1001。**阶段 H 全闭**。
- **ZR-1001 closure**（release 预备，阶段 I 首卡）：revenue c473e97 + delta 3ed2661——tools/release_readiness.py（fingerprint/integrity/容量/备份/回滚 dry-run/授权六门）；reviewer accepted（REV-001/002 delta + DELTA-BLOCK-001 receipt 重签）；closure→ZR-1002。
- **ZR-1002 closure**（Reader 先上线，company-wiki）：wiki 6af6cc5——golden 零漂移/writer 保持/SLO/rollback/无迁移；reviewer accepted；closure→ZR-1003。
- **ZR-1003 closure**（lifecycle/safety/RootPolicy shadow assertions，company-wiki）：wiki 9a00df6——lifecycle/safety fail-closed/policy 拒绝/两周期确定性/active 不变/flag-only 回滚；reviewer accepted；closure→ZR-1004。
- **ZR-1004 closure**（四 root 小 cohort，revenue）：revenue 06d259c——companies exact/dayu exact/Dropbox fail-closed/future_lake 配置 + external write=0 + 同 request 幂等/失败恢复一致；reviewer accepted；closure→ZR-1005。**阶段 I 已闭 4/9**。
- 三仓 HEAD（本地 fcap，未 push）：revenue 06d259c（ZR-1004 实现）、wiki 9a00df6、filing 5a1c18f。
- **最终停止点（用户指示：更新全部 planning docs 后停止）**：恢复第一步 = ZR-1005（legacy artifact 分桶）→ ZR-1006~1009/CA-304。

## 2026-08-23 ZR-1005 closure 快照（阶段 I 已闭 5/9）
- **ZR-1005 closure**（legacy artifact 分桶与最小 canary backfill，company-wiki）：wiki abeaca8f——C1 真实 catalog dry-run（closed=True、result_hash 稳定、documents/sources/locations 行数零变化）；C2-C4 temp catalog apply（INSERT OR IGNORE shadow bindings 零删除）/幂等（re-apply skipped>0 created=[]）/only-bindable（bound_ids==bindable_ids）；4 测试函数；reviewer accepted（4 passed；canonical 07dda8b8 一致；delta 仅 wiki；REV-001 minor + 3 info）；reviewer receipt canonical 51879f67；closure→ZR-1006。**阶段 I 已闭 5/9**。
- **accepted 94/117（约 80%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 24 + G 5 + H 6 + I 5（ZR-1001~1005；计数真源 state.json）。
- 全量基线：896 passed + 106 subtests（零回归）；产品代码零改动。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-1005 closure docs commit 待提交）、wiki abeaca8f、filing 5a1c18f。
- 下一卡：ZR-1006（broker processing demand 最小 cohort——七份紫金先 1→3→7；质量门/成本/SLO；失败不污染旧 artifact）→ ZR-1007~1009/CA-304。

## 2026-08-23 ZR-1006 closure 快照（阶段 I 已闭 6/9）
- **ZR-1006 closure**（broker processing demand 最小 cohort，company-wiki）：wiki 35a1103——C1 生产只读快照（七份紫金 broker 全 active+0 artifact）；C2 DemandQueue+DemandScheduler ramp 1→3→7 严格前缀 + completed 终态；C3 质量门 only-bindable；C4 成本预算/deadline urgency/aging 防饿死；C5 失败隔离（terminal_failed 不污染旧 artifact；重试自写）；9 tests；reviewer accepted（3 info）；reviewer receipt canonical 772b3215；closure→ZR-1007。**阶段 I 已闭 6/9**。
- **accepted 95/117（约 81%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 24 + G 5 + H 6 + I 6（ZR-1001~1006；计数真源 state.json）。
- 全量基线：896 passed + 106 subtests（零回归）；产品代码零改动。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-1006 closure docs commit 待提交）、wiki 35a1103、filing 5a1c18f。
- 下一卡：ZR-1007（mine facts/model shadow 与旧分部模型对比，revenue 卡）→ ZR-1008（cutover）→ ZR-1009（legacy 删除）。

## 2026-08-23 ZR-1007 closure 快照（阶段 I 已闭 7/9）
- **ZR-1007 closure**（mine facts/model shadow vs legacy 分部模型，revenue）：revenue 887fd12——shadow 路径（MineYearOperation→resource model）手算等价 saleable×price、legacy 并存；逐 driver 差异归因；reconcile_layer 闭合/诚实 gap；mine-volume rolling backtest + as-of fail-closed；零 registry 写 + run_forecast 零调用；12 tests；reviewer accepted（2 minor+1 info）；reviewer receipt canonical 3775053f；closure→ZR-1008。**阶段 I 已闭 7/9**。
- **accepted 96/117（约 82%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 24 + G 5 + H 6 + I 7（ZR-1001~1007；计数真源 state.json）。
- 全量基线：908 passed + 106 subtests（零回归）；产品代码零改动。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-1007 closure docs commit 待提交）、wiki 35a1103、filing 5a1c18f。
- 下一卡：ZR-1008（source/revenue 新链 cohort cutover，revenue+三仓）→ ZR-1009（legacy 删除，CA-304 唯一拥有）。
