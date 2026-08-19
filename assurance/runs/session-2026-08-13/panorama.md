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
