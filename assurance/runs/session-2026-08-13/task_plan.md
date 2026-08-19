# 三仓改进项目实施计划 — Session 工作记忆（非任务权威，仅作工作文件）

> 唯一执行入口仍是 `audit_review/README.md`；本文件只是实施者的工作记忆，不构成第二个领取入口。

## 决策（用户确认 2026-08-13）
- 从 CA-001 连续推进 A→J，仅在 README 停线/blocked 条件暂停。
- 规划文件位置：`assurance/runs/session-2026-08-13/`（已批准）。
- 独立 reviewer：不共享实施上下文的子代理 + 干净 checkout。
- 资源授权：本机可用资源直接使用；需要新凭据/权限时报告 blocked。
- Git：本地提交（fcap），不 push。

## 最新状态（2026-08-16，恢复会话后再次停点）
- **机器状态**：`current_phase=C_read_only_and_contracts`，`current_next=ZR-206`。
- **accepted 29 单元**：CA-001~004、CA-101~109、ZR-001~004、ZR-101~105、ZR-201~205。
- **ZR-204 已 closure**（锁/错误 taxonomy）：独立复核 accepted（矩阵 7 项全对、15 单测绿、受影响 contract 仅 3 个已知既有失败）；closure→ZR-205。
- **ZR-205 已 closure**（filing deadline-aware retry）：filing 0e5d209；canonical 码消费 + jitter/cap/deadline + 信封对账；328 tests + 91.45% branch + ratchet 34 + mypy；复核 accepted（ZR205-REV-002 low 措辞修正）；ZR102-F2 filing 侧关闭；ZR102-F1 移交 ZR-407。
- **ZR-206（live writer + 49GB SLO，阶段 C 出口卡）in_progress**：preflight_locked；hermetic 8 测试绿（live-writer 长事务、50 并发、1M spans SLO、covering-index、内存门、零写指纹 twin）；T2 真实 49.62GB 探测运行器（assurance/unified_completion/t2/zr206_t2_probe.py）收尾中；冻结 SLO 门已写卡片（status/health p95≤12000ms 等）。
- **下一步（恢复时从这继续）**：ZR-206 收尾（T2 证据 JSON → implementer receipt → state walk → 独立复核 → closure）→ C 阶段出口达成 → D（ZR-301 起）。

## Phase A0（基线与锁）— 状态：completed ✅
- CA-001 计划锁/CAS → CA-002 环境冻结 → CA-003 CodeGraph → CA-004 旧计划处置 → ZR-001 drift 重放 → ZR-003 golden corpus → ZR-002/004 共享证据关闭：全部 accepted + closure。
- 产出：机器状态/锁/CAS、输入 hash、envfreeze、codegraph 冻结、71 FC legacy 处置、drift_ledger（15 项 still-failing）、12 样本脱敏 corpus。

## Phase B（Evidence/Closure 2.0）— 状态：completed ✅
- CA-101 严格状态机 → CA-102 receipt schema → CA-103 revision 配对 → CA-104 command attestation → CA-105 197 场景注册表 → CA-106 side-effect ledger → CA-107 三仓 Closure 2.0 → CA-108 30 mutation kill=100% → CA-109 旧 gate 隔离：全部 accepted + closure。

## Phase C（真只读与契约）— 状态：in_progress（27/33 单元中 C 部分 8/11）
- [x] ZR-101 八阶段跨仓 taxonomy（wiki observability 2.0）— accepted ✅
- [x] ZR-102 hermetic 三进程 T1 runner（6 场景 + 真实路径硬拒绝 + 4 findings）— accepted ✅
- [x] ZR-103 closure/receipt/command validator（§7 共享证据关闭）— accepted ✅
- [x] ZR-104 三仓质量基线/ratchet（product-tree 绑定）— accepted ✅
- [x] ZR-105 current-triplet CI required checks 契约（诚实 9-gap → CA-201）— accepted ✅
- [x] ZR-201 CatalogReader 协议+只读工厂 — accepted ✅
- [x] ZR-202 typed read queries（11 方法 + schema fail-closed + query_only）— accepted ✅
- [x] ZR-203 生产只读入口重接 Reader（service/CLI/resolver；writer-init 显式化；golden 等价）— accepted ✅
- [x] ZR-204 DB busy/locked/operation-lock/timeout/paused taxonomy — accepted + closure（wiki 65a9e330+a4ea60d+ad54026；复核 accepted）
- [x] ZR-205 filing deadline-aware retry + 错误透明转发（依赖 ZR-204）— accepted + closure（filing 0e5d209）
- [ ] ZR-206 live writer + 49GB 级只读 SLO/压力验收（依赖 ZR-203~205）— **实现完成（hermetic 8 测试绿 + T2 探测收尾），receipt/复核/closure 未做**；恢复第一步

## Phase D（生命周期、roots、时效/下载）— 状态：pending
- ZR-301~307 + ZR-401~409（16 单元）：source lifecycle 状态机、RootPolicy 3.0、adapter registry、dedupe、revision 闭环。

## Phase E（broker/web/处理需求）— 状态：pending
- ZR-501~510（+ZR-304~306 迁移部分）：七份研报语义产物、多实体错归、表格保真、ProcessingDemand。

## Phase F（revenue 与矿业）— 状态：pending
- ZR-601~611 + ZR-701~713（24 单元）：矿山事实、会计桥、generator/validate/draft/formal、回测置信度。

## Phase G（真实 E2E）— 状态：pending
- ZR-801~806：三真实 root 用户旅程全绿。

## Phase H（动态审核与质量）— 状态：pending
- ZR-901~907 + CA-201~206：current-triplet PR 门、Daily/Weekly/Monthly、alert drill。

## Phase I（渐进发布）— 状态：pending
- ZR-1001~1008 + CA-304：cohort 灰度、legacy 删除。

## Phase J（独立终验与关闭）— 状态：pending
- CA-301~306（替代 ZR-1101~1105）：六目标 machine pass、旧计划关闭。

## 关键约束（每次操作前自查）
- 产品代码/配置/旧计划/catalog/roots/CI：只读（写路径按卡明确授权）。
- 外部 roots 零写；无授权不下载、不外发。
- 不动用户 dirty 文件（wiki 的 llm_cost_log.csv、settings.local.json 等）。
- 冻结规范 hash 漂移 → 立即释放锁并停线。
- 恢复实施后延续既有纪律：preflight 卡 → RED → 最小实现 → 四层测试 → receipt（真实 sha、实跑后写命令结果）→ 独立复核 → closure。

## 最新状态（2026-08-17 阶段 D 续推）
- **accepted 33/117**：CA-001~004、CA-101~109、ZR-001~004、ZR-101~105、ZR-201~205、ZR-301~304。
- **ZR-305**：independent_review（legacy 五桶迁移验收，wiki 080d20c，产品零改动）。
- **下一步**：ZR-305 复核/closure → ZR-306（role DAG 最小失效）→ ZR-307（filing 分阶段 envelope）→ ZR-401~409（RootPolicy 3.0/roots/时效）。

## 最新状态（2026-08-17 阶段收尾）
- **accepted 34/117**：A0 8 + B 9 + C 9 + D 8（ZR-301~305）。
- **ZR-306**：preflight_locked；实现完成（wiki a608980，6 property tests 绿）；receipt/复核/closure 未做。
- **下一步（恢复时）**：ZR-306 收尾 → ZR-307（filing 分阶段 envelope）→ ZR-401~409（RootPolicy 3.0/roots/时效/授权下载）→ 阶段 D 出口。

## 最新状态（2026-08-18 阶段 D 收尾 → 用户指示停止）
- **accepted 36/117**：A0 8 + B 9 + C 11（ZR-101~105、ZR-201~206）+ D 8（ZR-301~307 + ZR-401）。
- **ZR-306 closure**：role DAG 最小失效 property tests（wiki a608980，6 tests，产品零改动）；复核 accepted。
- **ZR-307 closure**：filing 分阶段 envelope + resolution trace（filing df66796，338 tests）；复核 accepted。
- **ZR-401 closure（RootPolicy 3.0 严格加载器）**：wiki 251615e（12 tests，unit 787 绿，McCabe max 8，mypy clean）；独立复核 **accepted**（5 条非阻断 findings：REV-001 privacy_class 隐式默认措辞、REV-002 contract 计数过报、REV-003 生产 config 未切 3.0（已记录显式决策：延期至 ZR-402/403 或阶段 D 出口，回滚纪律保持）、REV-004 环境、REV-005 plan_sha256 漂移）；reviewer receipt canonical 97e562bd…；state accepted + closure-advance → **ZR-402**；revenue closure commit 45da179（pre-commit 全套 470+106 绿）。
- **阶段 D 地图**：◐ 8/16（ZR-301~307 + ZR-401 closure；ZR-402~409 pending）。
- **停止点（用户指示：收尾并更新全部 planning docs 后停止）**：ZR-402 未领取；恢复第一步 = ZR-402（adapter registry，`adapters/registry.py` 已有基础）→ ZR-403（dedupe/resolver 泛化）→ ZR-404~409（envelope/authorization/时效/下载）→ 阶段 D 出口 → E（ZR-501~510）。

## 最新状态（2026-08-18 阶段 D 收官 → 用户指示：收官 + 更新全部 planning docs 后停止）
- **accepted 41/117**：A0 8 + B 9 + C 11 + D 13（ZR-301~307 + ZR-401~406）。
- **ZR-402 closure**（adapter registry 路由契约）：wiki 57cd72e（36 tests：kind/ID 无关路由 + 零 kind 分支机械门 + M1~M9 mutation 击杀表）；复核 accepted（3 info）；closure→ZR-403（7d11199）。
- **ZR-403 closure**（dedupe/resolver 泛化）：wiki 87ee0ac（7 tests：四上下文含 future_lake、health→priority、读不写 canonical、10-shuffle 稳定）；复核 accepted（1 info REV-001 措辞）；closure→ZR-404（ce8152a）。
- **ZR-404 closure**（envelope 加性扩展）：wiki f45f7ed（11 tests：policy/epoch/cohort/source-hash 一致 + 排除 trace + canonical rationale 脱敏 + 冲突 fail closed；schema 保持 1.0）；复核 accepted（3 info）；closure→ZR-405（63fb5a4）。
- **ZR-405 closure**（跨仓 policy-root containment）：wiki e56eb5f（policy-export 端点 + resolve/ensure 响应内嵌 + export 可复用性归一化）+ filing 3087f28（响应内嵌消费 + hash 对 policy document 计算 + envelope 交叉校验；13 tests + 1 skip）；复核 accepted（1 minor REV-002 close-gap 后续 + 3 info）；closure→ZR-406（e8478f9）。
- **ZR-406 closure**（正交 gap-plan 矩阵）：wiki 45ae721（39 collected = 30 格参数化矩阵 5 local × 6 provider + 9 聚焦；capture_ready 防御过滤；cli.py ratchet 维护）；首轮复核 changes_required（REV-001 计数 12≠13、REV-002 矩阵 24/30）→ 修正为真·数据驱动 30 格 + 诚实计数 → delta 复核 accepted（2 minor 转录）；closure→ZR-407（revenue commit 进行中）。
- **阶段 D 地图**：◐ 13/16（ZR-301~307 + ZR-401~406 closure；**ZR-407/408/409 pending**——authorization-bound GapPlan、下载执行、future_lake 生产切换）。
- **停止点（用户指示：收官并更新全部 planning docs 后停止）**：ZR-407 未领取；恢复第一步 = ZR-407（authorization-bound GapPlan/CloseGap 支持 missing 与 newer_revision；filing + wiki 双仓；含 ZR405-REV-002 后续：close-gap 响应内嵌 policy_export）→ ZR-408（staging→validate→canonical commit、single-flight）→ ZR-409（future_lake 生产切换，阶段 D 出口）→ E（ZR-501~510）。

## 最新状态（2026-08-18 晚：ZR-407/408 closure 补提交与收尾）
- **补提交**：ZR-407 三仓产物落库——wiki `bdffc54`（actionable union + ensure 只读路径）、filing `5a1c18f`（_gap_plan_has_actionable_candidate）、revenue `6145dad`（closure + receipts）；ZR-408 prep `71aa798`（跨进程 single-flight oracle）。
- **ZR-407 closure 确认**：accepted（reviewer-zr407-independent）→ closure→ZR-408（state 已含，补提交完成）。
- **ZR-408 closure**：验收钉死卡（产品零改动）——FC-801/FC-804/canonical-writer/ratchet 22 passed + unit 787 + 跨进程 spawn 双进程 single-flight oracle（fetch log 恰一条、fetch_events=[0,1]、documents=1）；implementer receipt canonical 81210bf2…；复核 accepted（3 info：REV-001 命令标签转录、REV-002 CRLF blob hash、REV-003 既有线程级 flake）→ closure→**ZR-409**（revenue commit 进行中）。
- **accepted 42/117**：A0 8 + B 9 + C 11 + D 14。
- **阶段 D 地图**：◐ 14/16；**ZR-409 pending**（future_lake 生产切换，阶段 D 出口：只改配置/adapter fixture、产品 core diff=0、EX/LT/DL/IDX/UJ 场景全绿）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-408 closure 提交进行中）、wiki 71aa798、filing 5a1c18f。

## 最新状态（2026-08-19：阶段 D 出口达成 → 阶段 E 启动）
- **accepted 43/117**：A0 8 + B 9 + C 11 + D 16（ZR-301~307 + ZR-401~409 全闭）。
- **阶段 D 出口（ZR-409 closure）**：生产 config 新增第四根 future_lake（directory + sidecar_filing_v1，仅配置接入，产品 core diff=0）；三真实 root 只读旅程（companies 紫金 601899/2025 exact、dayu-only 金斯瑞 HK1548/2021 exact 且 companies 无同 hash 前提钉死、Dropbox 星环 688031/2024 fail-closed capture_incomplete——生产数据诚实现状、紫金跨根共享 canonical=companies）；EX-08 生产形状扫描/导出；EX/LT/DL/IDX/UJ 场景→测试映射钉死并复跑全绿。复核 accepted（5 info：REV-001/002 文档措辞与死代码已 tidy，wiki 726d63d）。closure→**ZR-501**，phase=**E_broker_web_processing**。
- **阶段 D 地图**：✅ **16/16 完成**（ZR-301~307 生命周期子组 + ZR-401~409 roots/时效/下载）。
- **阶段 E 地图**：◐ 0/10（ZR-501~510 + ZR-304~306 迁移部分：七份研报语义产物、多实体错归、表格保真、ProcessingDemand）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-409 closure 提交进行中）、wiki 726d63d、filing 5a1c18f。
- 恢复第一步：ZR-501（阶段 E 首卡）。
## 停止点（2026-08-19 晚：用户指示本阶段完成后更新全部 planning docs 后停止）
- 本阶段完成：阶段 E 全闭（ZR-501~510 10/10）+ ZR-701（F1 入口）closure；accepted 54/117。
- 恢复第一步：ZR-702（F1 后续：generator→linter→engine 闭环钉死/输入 schema 单一真源）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-701 closure 提交进行中）、wiki 26a6b22、filing 5a1c18f。
