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
## 停止点（2026-08-20 晚：用户指令停止）
- 当前游标：F_revenue_mining / ZR-704。
- accepted 56/117（F 阶段 3/13：ZR-701~703）。
- 恢复第一步：ZR-704（F1 后续：draft/formal 互换/故障注入/幂等）。
- 三仓 HEAD：revenue 49a8793、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-21：F1 全闭 → F2 ZR-601/602 closure，用户指示更新全部 planning docs 后停止）
- **accepted 62/117（约 53%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 9（ZR-701~706/710 + ZR-601/602）。
- **F1 出口**：ZR-701~706 + ZR-710 7/7 全闭（prepare_forecast/draft-formal/validate-only 门/schema 真源/文档清理/selector 契约/publication 事务）。
- **ZR-601 closure**（F2 首卡 asset facts 数学契约）：revenue 1d32047（10 tests 产品零改动）；reviewer-zr601-independent accepted（26/26 对抗断言；1 minor docstring 3-period 标签 + 1 info 范围 diff）；reviewer receipt canonical d5cf7a5a；closure→ZR-602。
- **ZR-602 closure**（F2 第二卡 asset facts basis 契约）：revenue cb82620 + delta c9b0cfc（4 文件 +333/-1 + REV-001 修复，20 tests）——G1 resource≠reserve 语义隔离钉死（机制已存在）；G2 basis 加性契约（ownership_basis ∈ {one_hundred_percent, equity_share, consolidated} + reporting_standard + measurement_date ISO，携带即强制完整，半成品 fail-closed）；G3 族内单位一致性门（按维度分组归一化，kt-vs-t 漂移拒绝；换算表归 ZR-610 ADR）。全量 540+106 绿；ruff/ratchet 全过；首轮 reviewer accepted（22/22 对抗断言）→ REV-001（unhashable ownership_basis 抛 TypeError）delta 修复 → delta accepted（REV-001→info）；reviewer receipt canonical 7c972a4e；closure→ZR-603。
- **停止点（用户指示：本卡跑完后更新全部 planning docs 后停止）**：ZR-603 未领取；恢复第一步 = ZR-603（F2 ownership/consolidation timeline——DAG 解锁 ZR-603，README 阶段表提 ZR-610 会计 ADR 但以 DAG 为准）→ ZR-604~608/611/707/711~713 + ZR-610 会计 ADR。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-602 closure commit 待提交；实现 cb82620 + delta c9b0cfc）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 恢复：ZR-603 closure → ZR-604）
- **accepted 63/117（约 54%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 10（ZR-701~706/710 + ZR-601~603）。
- **ZR-603 closure**（F2 第三卡 ownership/consolidation timeline + geography hierarchy）：revenue b52568b + delta 03d716e（+500 行 3 文件，29 tests）——effective-dated fractions（fail-closed 回溯/收购语义/pro-rata 日加权）、chain product 一次连乘（0.6×0.7=0.42）、apply-once 权益门（equity_share=already applied/consolidated=not discounted）、additive segment geography/ownership keys + searchable country index。首轮 changes_required（REV-001 isinstance guard + REV-002~004 类型泄漏）→ delta 修复 + delta accepted（REV-005 minor 登记 ZR-607 后续）；reviewer receipt canonical 18462dd9；closure→ZR-604。
- 下一卡：ZR-604（F2 从表格抽取/冲突保存/人工 review——DAG 已解锁 ZR-604）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-603 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-604 实施完成）
- **accepted 63/117 + ZR-604 实施完成**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 10（ZR-701~706/710 + ZR-601~603）+ ZR-604 待复核/closure。
- **ZR-604 实施**（F2 第四卡冲突保存与人工 review）：revenue 2636e55（+238 行 3 文件，11 tests）——semantic_groups 硬失败→双 assertion（primary/secondary）+ resolution status（accepted/rejected/pending_review/under_review）加性扩展；冲突参数均带 resolution_status + ≤1 accepted → 允许共存，否则原行为硬失败（backward compatible）。全量 585+106 绿；implementer receipt canonical 58159699；独立复核 reviewer-zr604-independent 运行中。
- 下一卡（closure 后）：ZR-605（F2 MineYearOperation 输入合同——DAG 依赖 ZR-604,ZR-610；ZR-610 未解锁，以 DAG 为准）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 2636e55（ZR-604 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-610 closure → ZR-605）
- **accepted 65/117（约 56%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 12（ZR-701~706/710 + ZR-601~604 + ZR-610）。
- **ZR-610 closure**（F2 会计 ADR 冻结）：独立会计 reviewer accepted（8 条决策全部通过会计合理性审查，2 info 非阻断）；closure→ZR-605。
- 下一卡：**ZR-605**（F2 MineYearOperation 输入合同——DAG 已解锁；"volume/grade/recovery/payable/product/period/scenario；必须遵守已批准矿业 ADR；缺字段有 gap，不默认为 0"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-610 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-605 实施完成）
- **ZR-605 实施完成**（F2 MineYearOperation 输入合同）：revenue b02f17b（+289 行 2 文件，30 tests）——七字段必填 gap-on-missing（volume/grade/recovery/payable/product/period/scenario，不默认 0）、derive_saleable_volume = volume×grade×recovery×payable、to_resource_model_drivers 映射 resource 模型。全量 615+106 绿；implementer receipt canonical 3f780700；独立复核 reviewer-zr605-independent 运行中。
- 下一卡（closure 后）：ZR-606（F2 商业量价层——DAG 依赖 ZR-605；"price/payability/TC-RC/premium/byproduct/FX/royalty"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue b02f17b（ZR-605 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-604 closure → ZR-610）
- **accepted 64/117（约 55%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 11（ZR-701~706/710 + ZR-601~604）。
- **ZR-604 closure**（F2 第四卡冲突保存与人工 review）：reviewer accepted（17/17 对抗断言，1 minor null resolution_status 语义——登记后续）；closure→ZR-610。
- 下一卡：**ZR-610**（F2 会计 ADR 冻结——DAG 已解锁；"无产品代码；独立会计review accepted；明确逐矿贡献是模型估计、不是披露事实"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-604 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-605 closure → ZR-606）
- **accepted 66/117（约 56%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 13（ZR-701~706/710 + ZR-601~605 + ZR-610）。
- **ZR-605 closure**（F2 MineYearOperation 输入合同）：reviewer accepted（7/7 对抗断言组，1 minor inf 值未拒——登记 ZR-606 后续）；closure→ZR-606。
- 下一卡：**ZR-606**（F2 商业量价层——DAG 已解锁；"price/payability/TC-RC/premium/byproduct/FX/royalty；每个变量有来源/假设/期限；多商品与副产品不重复计价；敏感性可重算"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-605 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-606 实施完成）
- **ZR-606 实施完成**（F2 商业量价层）：revenue cf3ada7（+312 行 2 文件，24 tests）——price/payability/TC-RC/premium/byproduct/FX/royalty 带完整 provenance（value/source/assumption/period，finite_number 加固）、不重复计价（byproduct 独立加项）、纯函数净收入可敏感性重算。全量 639+106 绿；implementer receipt canonical 64f99205；独立复核 reviewer-zr606-independent 运行中。
- 下一卡（closure 后）：ZR-607（F2 ownership/consolidation/internal flow 会计桥——DAG 依赖 ZR-603,ZR-606；"equity vs consolidation、内部转冶炼/贸易、gross/net、elimination 可追踪"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue cf3ada7（ZR-606 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-606 closure → ZR-607）
- **accepted 67/117（约 57%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 14（ZR-701~706/710 + ZR-601~606 + ZR-610）。
- **ZR-606 closure**（F2 商业量价层）：delta 47fe715（REV-001 saleable_volume finite_number）；delta 复审 staged-not-committed 教训（pre-commit 钩子运行时）；implementer receipt 重封 b07a951b；reviewer accepted，closure→ZR-607。
- 下一卡：**ZR-607**（F2 ownership/consolidation/internal flow 会计桥——DAG 已解锁；"equity vs consolidation、内部转冶炼/贸易、gross/net、elimination 可追踪"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-606 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-607 实施完成）
- **ZR-607 实施完成**（F2 internal flow 会计桥）：revenue 073fd4d（+318 行 2 文件，29 tests）——可追踪 InternalFlow（八字段）+ internal_revenue + eliminate_internal_revenue gross/net 桥（net=external 内部消除不重复计，period/scenario 过滤）。全量 674+106 绿；implementer receipt canonical 05c102fb；独立复核 reviewer-zr607-independent 运行中。
- 下一卡（closure 后）：ZR-608（F2 asset→segment→group reconciliation——DAG 依赖 ZR-607；"容差内才标 modeled；不闭合则回退到分部并列 gap；禁止产量×价格伪收入"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 073fd4d（ZR-607 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-608 实施完成）
- **ZR-608 实施完成**（F2 asset→segment→group reconciliation）：revenue 3081967（+107 行 reconciliation.py + 11 tests）——reconcile_layer 容差门（reconciled_modeled vs gap）、fallback_segment_listing（分部并列 + 显式 gap）、gap_report 防伪收入（NaN/inf 拒绝、缺资产=gap）。全量 685+106 绿；implementer receipt canonical d5497096；独立复核 reviewer-zr608-independent 运行中。注：ZR-607 closure 文件被合入本 commit（流程偏差）。
- 下一卡（closure 后）：ZR-611（F2 通用多矿合成 E2E——DAG 依赖 ZR-605~608,ZR-610；"控股、权益法、多金属、内供、跨币种、爬坡、gap、residual"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 3081967（ZR-608 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-608 closure → ZR-611）
- **accepted 69/117（约 59%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 16（ZR-701~706/710 + ZR-601~608 + ZR-610）。
- **ZR-608 closure**（F2 asset→segment→group reconciliation）：reviewer accepted（46/46 对抗断言，零 blocking）；closure→ZR-611。
- 下一卡：**ZR-611**（F2 通用多矿合成 E2E——DAG 已解锁；"控股、权益法、多金属、内供、跨币种、爬坡、gap、residual；生产代码公司/矿名 hardcode=0"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-608 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-611 实施完成）
- **ZR-611 实施完成**（F2 通用多矿合成 E2E）：revenue 288ac88（test-only 11 tests 零产品改动）——合成多矿公司八类场景（控股/权益法/多金属/内供/跨币种/爬坡/gap/residual）全链确定性可重算 + 手算对照；生产代码零硬编码验证。全量 696+106 绿；implementer receipt canonical 9667ac1c；独立复核 reviewer-zr611-independent 运行中。注：ZR-608 closure 文件被合入本 commit（流程偏差第二次）。
- 下一卡（closure 后）：ZR-711（F2 additive schema 3.8 opt-in——DAG 已解锁）→ ZR-707（mixed recognition/gross-net）→ ZR-712/713（confidence 反博弈/rolling-origin backtest）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 288ac88（ZR-611 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-611 closure → ZR-609）
- **accepted 70/117（约 60%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 17（ZR-701~706/710 + ZR-601~608 + ZR-610/611）。
- **ZR-611 closure**（F2 通用多矿合成 E2E）：reviewer accepted（独立数学重算匹配 + 八类非空洞 + 确定性位级一致）；closure→ZR-609。
- 下一卡：**ZR-609**（F2 合流：紫金 pilot + 第二家不同结构矿企泛化——DAG 已解锁；"紫金主要资产覆盖、逐矿可回答范围清楚；第二家公司无需产品硬编码"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-611 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-609 实施完成）
- **ZR-609 实施完成**（F2 合流：紫金 pilot + 第二家泛化）：revenue e541d55（test-only 9 tests 零产品改动）——紫金三主要资产（卡莫阿-卡库拉权益链 0.396/巨龙全资/紫金山金+银副产品）逐矿可回答走 F2 全链 + 第二家纯金矿商泛化零硬编码。全量 705+106 绿；implementer receipt canonical ee6dd908（初版 f314d7d9 修正：base_triplet 404a2bb）；独立复核 reviewer-zr609-independent 运行中。
- 下一卡（closure 后）：ZR-711（F2 additive schema 3.8 opt-in）→ ZR-707（mixed recognition/gross-net）→ ZR-712/713（confidence 反博弈/rolling-origin backtest）。
- 三仓 HEAD（本地 fcap，未 push）：revenue e541d55（ZR-609 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-22 ZR-609 closure → 停止点）
- **accepted 71/117（约 61%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 18（ZR-701~706/710 + ZR-601~609 + ZR-610/611）。
- **ZR-609 closure**（F2 合流：紫金 pilot + 第二家泛化）：reviewer accepted（手算独立重算 + 25 项非空洞 + 零硬编码 tokenize 扫描；REV-001/002 已修正：ZR-611 closure 实际独立落地 404a2bb、receipt 重封 ee6dd908）；closure→ZR-711。
- **停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：下一卡 ZR-711（F2 additive schema 3.8 opt-in——DAG 已解锁）未领取；恢复第一步 = ZR-711 → ZR-707（mixed recognition/gross-net）→ ZR-712/713（confidence 反博弈/rolling-origin backtest）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-609 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-711 实施 + delta 完成）
- **ZR-711 实施完成**（F2 additive schema 3.8 opt-in）：revenue b0d7291 + delta e75debb（7 文件 +283/-6 + REV-001 修复，15 tests）——3.8 词汇+EMIT、版本门 {3.7,3.8}、validate_operating_units 复用 validate_mine_year_operation、schema_optin converter 三函数（3.7→3.8 加空 gap / 3.8→3.7 strip / round-trip）、capture-integrity gate 修复。全量 720+106 绿；implementer receipt canonical f273d1ee（初版修正中）；reviewer accepted。
- **停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：下一卡 ZR-711 closure 待完成；恢复第一步 = ZR-711 closure → ZR-707 → ZR-712/713。
- 三仓 HEAD（本地 fcap，未 push）：revenue e75debb（ZR-711 delta commit）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-711 closure → 最终停止点）
- **accepted 72/117（约 62%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 19（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711）。
- **ZR-711 closure**（F2 additive schema 3.8 opt-in）：reviewer changes_required（REV-001 capture-integrity 门）→ delta e75debb 修复 + delta accepted；closure→ZR-707。
- **最终停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：下一卡 ZR-707（F2 mixed recognition/gross-net——DAG 已解锁）未领取；恢复第一步 = ZR-707 → ZR-712/713（confidence 反博弈/rolling-origin backtest）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-711 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-707 实施完成）
- **ZR-707 实施完成**（F2 mixed recognition/gross-net + multi-commodity）：revenue fdb560e（+244 行 2 文件，13 tests）——validate_mixed_recognition（混合 recognition 合法）、validate_commodity_matrix（multi-commodity 分段）、validate_presentation_consistency（gross/net 声明）。全量 733+106 绿；implementer receipt canonical 91aefa2c；独立复核 reviewer-zr707-independent 运行中。
- 下一卡（closure 后）：ZR-712（F2 confidence 反博弈——DAG 依赖 ZR-708；"duplicate/split/plug/zero-impact/one-observation/wrong-record mutations 全杀"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue fdb560e（ZR-707 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-707 closure → ZR-708）
- **accepted 73/117（约 62%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 20（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707）。
- **ZR-707 closure**（F2 mixed recognition/gross-net + multi-commodity）：reviewer accepted（11/11 对抗断言，4 info）；closure→ZR-708。
- 下一卡：**ZR-708**（F2 重验不可变 snapshot/backtest 基础接线——DAG 已解锁；"已有能力若当前 triplet 全绿则 already_satisfied；否则修复；accuracy record 实际可被 forecast 消费"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-707 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-708 实施完成）
- **ZR-708 实施完成**（F2 重验不可变 snapshot/backtest）：revenue a9405f8（test-only 7 tests 零产品改动）——already_satisfied 重验：snapshot 确定性/不可变/tamper 拒绝、accuracy_record → run_forecast → confidence.historical_accuracy 消费链、四层 hash 链接、未来 actual 拒绝。全量 740+106 绿；implementer receipt canonical a9f5b356；独立复核 reviewer-zr708-independent 运行中。
- 下一卡（closure 后）：ZR-712（F2 confidence 反博弈——DAG 依赖 ZR-708；"duplicate/split/plug/zero-impact/one-observation/wrong-record mutations 全杀"）→ ZR-713（紫金 rolling-origin）。
- 三仓 HEAD（本地 fcap，未 push）：revenue a9405f8（ZR-708 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-708 closure → ZR-712）
- **accepted 74/117（约 63%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 21（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708）。
- **ZR-708 closure**（F2 already_satisfied 重验）：reviewer accepted（4 info）；closure→ZR-712。
- 下一卡：**ZR-712**（F2 confidence 反博弈——DAG 已解锁；"duplicate/split/plug/zero-impact/one-observation/wrong-record mutations 全杀；rating caps 可重算"）→ ZR-713（紫金 rolling-origin）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-708 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-712 实施完成）
- **ZR-712 实施完成**（F2 版本化 ConfidencePolicy + 反博弈）：revenue 2373c42（+380 行 6 文件，15 tests）——policy 数据化（version/weights/rating_caps，未知版本 fail-closed）、六类博弈 mutations 检测（duplicate/split/plug/zero-impact/one-observation/wrong-record）、recompute_rating caps 驱动。全量 755+106 绿；implementer receipt canonical fcc237aa；独立复核 reviewer-zr712-independent 运行中。
- 下一卡（closure 后）：ZR-713（F2 紫金 rolling-origin 历史回测——DAG 依赖 ZR-708,ZR-712；"严格 as-of 无 future actual；company/segment/mine-volume 分层；四层 immutable hashes"）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 2373c42（ZR-712 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-712 closure → 停止点，含 docs 一致性修复）
- **accepted 75/117（约 64%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 22（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708 + ZR-712）。
- **ZR-712 closure**（F2 版本化 ConfidencePolicy + 反博弈）：reviewer 首轮 accepted（36 探针全过）→ REV-001/002/004 minor（raw ValueError/NaN rating/KeyError caps）delta 修复 1c04684 + delta accepted（45 探针全过，REV-001/002/004 resolved，REV-003 info 保留）；reviewer receipt canonical 6d1c07a3；closure→ZR-713。
- **停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：下一卡 ZR-713（F2 紫金 rolling-origin——DAG 已解锁）未领取；恢复第一步 = ZR-713 → ZR-709（F2 合流：紫金五年预测用户旅程终验——依赖 ZR-705~708/ZR-710~713/ZR-609/ZR-611）→ 阶段 G（ZR-801~806）。
- **docs 一致性修复（本次）**：audit_review/findings.md 补 ZR-608/ZR-611/ZR-708 缺失条目 + 各卡 closure 计数统一（71→75/117）；剩余卡描述补 ZR-709 合流卡（此前零提及）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-712 closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-713 实施完成）
- **ZR-713 实施完成**（F2 紫金 rolling-origin 历史回测）：revenue cb34700（+285 行 2 文件，10 tests）——严格 as-of 无 future actual（泄漏 fail-closed）、company/segment/mine-volume 三层、四层 immutable hash 链、窗口不足 → capped（不伪造 metrics）。全量 768+106 绿；implementer receipt canonical 57c1d269；独立复核 reviewer-zr713-independent 运行中。
- 下一卡（closure 后）：ZR-709（F2 合流：紫金五年预测用户旅程终验——依赖 ZR-705~708/ZR-710~713/ZR-609/ZR-611）。
- 三仓 HEAD（本地 fcap，未 push）：revenue cb34700（ZR-713 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-713 closure → 停止点）
- **accepted 76/117（约 65%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 23（ZR-701~706/710 + ZR-601~609 + ZR-610/611 + ZR-711 + ZR-707/708 + ZR-712 + ZR-713）。
- **ZR-713 closure**（F2 rolling-origin 历史回测）：reviewer 首轮 **changes_required**（REV-001 blocking：三层 byte-identical 非独立评估——segment 层发 company wape、mine-volume 未用 ZR-605 契约；REV-002 minor：level/as_of 未绑 hash 链、snapshot_id 非快照身份）→ delta 修复 3479718（segment 独立 wape、mine-volume 走 ZR-605 契约 fail-closed、record_sha256 绑定 {level,as_of}、snapshot_id=快照身份；+5 回归 15 tests，全量 773+106，pre-commit 776+106 + E2E PASS）→ delta 复审 **accepted**（21/21 探针全过）；reviewer receipt canonical 8125837d；closure→ZR-709（F2 合流卡——F2 常规链全闭）。
- **停止点（用户指示：本阶段工作做完后更新全部 planning docs 后停止）**：下一卡 ZR-709（F2 合流：紫金五年预测用户旅程终验——依赖 ZR-705~708/ZR-710~713/ZR-609/ZR-611）未领取；恢复第一步 = ZR-709 → 阶段 G（ZR-801~806）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-713 closure commit 待提交，实现 cb34700 + delta 3479718）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-709 closure → F 阶段全闭 → 进入阶段 G）
- **accepted 77/117（约 66%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + **F 24/24 全闭**（新增 ZR-709）。current_phase=**G_real_e2e**，current_next=**ZR-802**（README §6 阶段 G 首卡；ZR-801 machine registry 已由 CA-105 唯一实现吸收，§7 重叠归属）。
- **ZR-709 closure**（F2 合流：紫金五年预测用户旅程终验 fixture）：revenue ac68807（test-only +919 行 1 文件，9 tests，产品零改动）——J1 真实 source_preparation 子进程链复用年报+研究沟通（reuse_receipt 全链可解释：outcome=reused_existing/bundle_status/download/parser/llm=0/producer_events DAG 角色；缺失 kind fail-closed exit 3 + ProcessingDemand 补齐路径）；J2 五年 FY2026-2030 输入由 F2 契约函数代数推导（MineYearOperation→commercial terms→权益链 0.396→realized_price 恒等闭合），mine 贡献×segment 引擎值 reconcile_layer 10/10 reconciled_modeled、公司层三段勾稽闭合、未建模白银 +120=gap/fallback gap=120 不冒充收入、internal flow net==total 不重复计、schema 3.8 operating_units 45 条嵌入 formal 直跑且与 3.7 rel=1e-12 零漂移 + converter 往返 canonical 相等；J3 draft 渲染零注册（gate_ids=[]）、formal 位级重放 + snapshot 回放 PASS。质量门：journey 9/9、全量 782+106 零回归（基线 773）、ruff 0、sync MATCH 147、pre-commit 全套绿。
- **独立复核 accepted**（reviewer-zr709-independent，干净 checkout ac68807）：V1 产品 diff=0、V2 全量复放 782+106、V3 12/12 对抗探针（Kamoa FY2028 手算位精确、+1% 伪造价格 → reconcile 翻 gap、容差语义、draft 零写）、V4 无空断言、V5 3.8 零漂移复验、V6 生产树硬编码零新增、V7 卡片/receipt hash 全对。4 info（嵌套 checkout 位置性失败非回归、state base_triplet 常量约定、J1 断言强度备注、既有 ADR docstring 提及）。reviewer receipt canonical 40206902…；closure receipt state_sha 73e10e70…/control 102b02f4…。
- 流程记录：pre-commit 安装同步门首拦（安装副本缺新文件）→ `sync_installations.py --apply` MATCH 147 后重提成功；复核 worktree `.review-zr709-clean` 用后即删。
- **下一卡：ZR-802**（组合旅程：existing/partial/missing/stale/conflict across roots——从 revenue 入口、三进程、第二次调用、阶段 receipt 与调用预算准确）。F 阶段出口达成：generator/validate/draft/formal 发布闭环 ✅、矿山会计桥或诚实 gap ✅、可信回测/置信度 ✅。
- 三仓 HEAD（本地 fcap，未 push）：revenue ac68807（实现；closure 提交进行中）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-802 closure → 阶段 G 推进中）
- **accepted 78/117**：G 1/6（ZR-802）。current_next=**ZR-803**。
- **ZR-802 closure**（组合旅程 across roots）：revenue 1b55f6f（test-only +353，7 tests，产品零改动）——五状态（existing 精确预算复用 / missing 计数不变式零伪造 / future-dated stale 拒绝 / 跨根双候选 ambiguous fail-closed / partial 读子集+DAG 最小生产闭包）+ C2 二次幂等 + C3 八阶段真实键投影。全量 789+106；ruff 0；sync MATCH 148。复核 accepted（11 探针；1 minor parser≥1 属上游信封内部计数登记后续、3 info）；reviewer receipt canonical 051e4f64。
- 流程调整（用户指示）：复核子代理在实现提交后立即派出后台跑，等待间隙主线做下一卡预研，不空转。
- 下一卡：ZR-803（chaos/property/mutation：锁、中断、磁盘、篡改、顺序、时钟——critical mutation 100% kill）。

## 最新状态（2026-08-23 阶段 G 连续推进 ZR-802~805 → 用户指示收尾停止）
- **accepted 81/117**：G 4/6（ZR-802/803/804/805）。current_phase=G_real_e2e，current_next=**ZR-806**（收官卡）。
- **ZR-802 closure**（组合旅程 across roots）：revenue 1b55f6f（7 tests）——五状态 existing/missing/stale/conflict/partial + C2 二次幂等 + C3 八阶段真实键投影。复核 accepted（11 探针；1 minor parser≥1 上游内部计数）。canonical 051e4f64。
- **ZR-803 closure**（六类故障×幂等恢复）：revenue b14ac3c（6 tests）——锁 WAL 写事务不阻只读旅程+释放同身份复用、中断注册零孤儿精确一次、磁盘结构化 exit2 无半写、篡改单字节拒绝原工件仍有效、乱序结构化拒绝后正常评估、时钟未来日期信息集外。复核 accepted（13 探针；2 minor+2 info）。canonical 7e305256。
- **ZR-804 closure**（平台与安装形态）：revenue be8405c（5 tests）——大小写变体同 source_id、缺省配置 fail-closed 无静默 sibling、安装副本 sync-first 身份逐字一致、活跃脚本无 Windows-only 构造。回填 receipt 后联合复核 accepted（A-V1~V5；CREATE_NO_WINDOW=守卫放行；drift 独立门在 fc1004:82）。reviewer canonical 46850f67（非标准序列化已按 CA-102 重封）。**流程偏差登记**：本卡曾跳过 receipt/复核直接开 ZR-805，由 ZRR805-REV-002 抓出后闭环（见 findings F-G2）。
- **ZR-805 closure**（T3 下载授权语义）：revenue 3fc5f3e + delta 295f138（3 tests）——T3 执行唯一 owner=filing-fetch opt-in 门（结构钉死）、未授权请求 journal 零 downloaded_new（JSONL 独立 oracle）、入口显式 --allow-download 单一下载器。首轮 accepted（fc646953；REV-001 oracle 接线空洞即修 + REV-002 簿记）→ delta 复核 accepted（B-V1~V4 非空洞性注入证明）。delta receipt b3efb845。
- 全量基线演进：782 → 800 → **803 passed + 106 subtests**（每卡零回归）；sync MATCH 151。
- 新发现入 findings F-G1~F-G4（oracle 空洞注入式证明 / 簿记跳步对策 / manifest 覆盖 tests 推论 / 嵌套 checkout 位置性常态）。
- **停止点（用户指示：收尾并更新全部 planning docs 后停止）**：ZR-806 未领取；恢复第一步 = ZR-806（真实 T2 三 root/broker/artifact/mine/forecast 样本收官）→ 阶段 H（ZR-901/CA-201 起）。
- 三仓 HEAD（本地 fcap，未 push）：revenue 295f138、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-806 实施完成）
- **ZR-806 实施完成**（阶段 G 收官：真实 T2 三 root 样本）：revenue b716a81（+253 行 1 文件，10 tests）——固定 5 样本清单（companies 紫金 FY2025/FY2024、dayu 1548 FY2021、Dropbox 星环 FY2024/东吴研报）唯一/新鲜（AUD2-05 缺失即 blocked）+ 三 root resolve 只读旅程（REUSED_EXACT ×3 + MISSING ×1 fail-closed）+ 零写指纹（浅指纹 + catalog 行数）+ Zijin/星环 sidecar 契约绑定。全量 813+106 绿；implementer receipt canonical 2dd046b5；独立复核 reviewer-zr806-independent 运行中。
- 下一卡（closure 后）：ZR-902（阶段 H 首卡：实际调度每日 Windows T2）。
- 三仓 HEAD（本地 fcap，未 push）：revenue b716a81（ZR-806 实现 commit；closure commit 待提交）、wiki 26a6b22、filing 5a1c18f。

## 最新状态（2026-08-23 ZR-806 closure → 阶段 H 入口）
- **accepted 82/117（约 70%）**：A0 8 + B 9 + C 11 + D 16 + E 10 + F 24 + **G 5/6 全闭**（ZR-802~806；ZR-801 由 CA-105 吸收）。current_phase=**H_dynamic_audit**，current_next=**ZR-902**。
- **ZR-806 closure**（真实 T2 样本收官）：reviewer-zr806-independent **accepted**（15 commands 全绿；独立复算 5 样本 hash 唯一/声明匹配、AUD2-05 temp 变体缺失样本套件 fail "blocked, never swap samples"（3 failed/7 passed）、resolve 四旅程复跑 + 指纹/catalog 行数不变、sidecar 逐字段匹配、git diff 零产品改动、回归 30 + ruff + ratchet + 全量 813+106 复跑 167.84s、receipt-validate OK；2 info：REV-001 星环 sidecar schema 较窄（Zijin 全字段枚举仅适用 Zijin）、REV-002 AUD2-05 用 temp 副本）；reviewer receipt canonical 5a9ddad4；closure→ZR-902（阶段 H 首卡）。
- **CRLF 教训**：README CRLF 行尾导致 closure-advance CAS-CONFLICT（read_text().encode() LF hash vs manifest 原始字节 CRLF hash）→ README 转 LF + manifest CAS 重建解决（findings 43）。
- **停止点（用户指示：收尾并更新全部 planning docs 后停止）**：下一卡 ZR-902（实际调度每日 Windows T2——依赖 ZR-806；"schedule/runner/权限/原子报告/<=24h freshness/release 消费全证明；不仅是脚本存在"）未领取；恢复第一步 = ZR-902 → ZR-903（每周/发布前 T3）/ZR-901（PR 门）。
- 三仓 HEAD（本地 fcap，未 push）：revenue（ZR-806 closure commit 待提交，实现 b716a81）、wiki 26a6b22、filing 5a1c18f。
