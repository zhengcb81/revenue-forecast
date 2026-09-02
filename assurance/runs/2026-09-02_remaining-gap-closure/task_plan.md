# 剩余缺口关闭实施计划（2026-09-02）

> 目标：把 2026-09-02 全面审查发现的未完成目标全部实现。每个工作单元必须有机器证据（测试 + 独立复核 + receipt），每一步完成后必须核实并更新本页进度。

## 1. 审查发现总表（全部 12 项缺口）

### A 类：代码缺陷（本轮已修复）

| ID | 缺口 | 证据 | 修复状态 |
|---|---|---|---|
| **A-1** | llm_summarizer.py:433 硬编码空 source_sha256 | SELECT 已 join `s.content_sha256 AS source_sha256` 但 INSERT 传 `""`；真实库 49 个产物被判 reusable | ✅ 已修复（afe5eb1）：`row["source_sha256"] if "source_sha256" in row.keys() else ""` |
| **A-2** | artifact_handle.py:98-100 validator 对空 source_sha 放行 | `if artifact_source_sha and ...` 条件短路空值 | ✅ 已修复（afe5eb1）：`if not artifact_source_sha: reject(artifact_source_sha_missing)` |
| **A-3** | runtime_policy.json policy_hash 漂移（77c1bdb7 ≠ c773099b） | ZR-409 第 4 root 配置后未重发快照 | ✅ 已修复（生产 CAS 重发，envelope=export 匹配） |

### B 类：部署动作（设计上明确延后，需自然时间/授权）

| ID | 缺口 | 性质 | 前置条件 |
|---|---|---|---|
| **B-1** | legacy 真实删除（R9 四 RED、quality.yml 行 133 真实调用、5 个 FC-150x N-1 待批） | 部署动作 | 两个 ≥24h 零 legacy_bridge_hits 自然观测窗口 + N-1 批准 |
| **B-2** | 自然时间动态审核（7 Daily + 2 Weekly + 1 Monthly + 1 alert drill） | 部署动作 | Windows 任务注册 + 真实运行累积（当前 ledger 为零） |
| **B-3** | 七份紫金研报真实语义处理（BR-01~26 scenario pending、0 artifacts/0 spans） | 部署动作 | KD-08 明示"不得批量处理真实研报"；需 cohort cutover 授权 |
| **B-4** | privacy_class 3.0 config 升级（生产 config 仍 schema 1.0） | 配置升级 | config_doctor 兼容 + 全量测试 |

### C 类：契约回溯工程（历史遗留）

| ID | 缺口 | 规模 | 修复方式 |
|---|---|---|---|
| **C-1** | 87/117 单元 12 receipt 不满足 CA-103 契约（reviewed_object_sha256 ≠ 11 canonical_hash；12 结构无效） | 87 个单元 | 重签发 12 receipt（按当前 CA-103 契约）或显式豁免早期 git-blob 语义 |
| **C-2** | scenario registry 197/197 全 pending、0 evidence_path、receipts 内 scenario_results 全空 | 197 个场景 | 回填真实执行证据（evidence_path + status=passed）或明确废弃并更新 closure-report |

### D 类：生产接线（代码层完备，物理入口未接）

| ID | 缺口 | 影响 | 修复方式 |
|---|---|---|---|
| **D-1** | v2 scanner 生产周期扫描物理入口仍走 v1 分支（cutover_decision 无 src 生产调用者） | 生产扫描仍是 v1 | scanner 主路径传 v2 flag 或接入 v2 adapter |
| **D-2** | worker LLM 出口无 privacy/receipt 过滤（llm_summarizer.summarize_catalog_with_llm SQL 无过滤；readiness_graph/source_lifecycle 无生产调用者） | 986 条 dropbox summary 无 receipt 仍可被 LLM 汇总 | worker 选数 SQL 接 privacy/receipt 过滤门 |
| **D-3** | 真实 roots E2E 套件被 CI --ignore（test_zr806 等仅在本地验收跑） | CI 不覆盖真实数据路径 | CI 加 windows-latest 单 job 或 self-hosted runner，把真实套件移回 |

## 2. 实施阶段（Phase 1→4）

### Phase 1：缺陷修复闭环（A 类 + D 类 1-2 项）

目标：已修复的 3 个缺陷闭环验证 + 剩余 2 个代码缺陷修复。

**工作单元**：

1. **GP-001**（A-1/A-2 回归验证）：空 source_sha 修复的三仓回归
   - 验证：wiki 全套测试 + revenue 全量回归 + filing 全套测试
   - 核实：CI 三仓全绿（push 后）
   - 检查点：真实库 49 个空 sha 产物被 validator 拒绝（assert）

2. **GP-002**（D-1 v2 scanner 生产切入）：scanner 主路径传 v2 flag
   - 修改：`scanner.py:833` `_scan_catalog_impl → scan_root_strategy(...)` 传 v2_scan_shadow 标志
   - 测试：wiki scanner_cutover 5 + scanner_facade 4 全绿 + 新增真实扫描测试（v2 分支执行）
   - 复核：独立 reviewer
   - 检查点：生产扫描日志显示 v2 adapter 路径被调用

3. **GP-003**（D-2 worker privacy 过滤）：worker LLM 出口加 privacy/receipt 门
   - 修改：llm_summarizer.py 的选数 SQL 增加 receipt/privacy 过滤条件（接 readiness_graph 或 source_lifecycle）
   - 测试：新增测试（无 receipt 的 private_user 文档不进选数）、wiki 全套回归
   - 复核：独立 reviewer
   - 检查点：986 条 dropbox summary 无 receipt 的文档不进 worker 选数

### Phase 2：契约回溯（C 类）

**工作单元**：

4. **GP-004**（C-1 receipt 重签发）：87 个单元 12 receipt 重签
   - 脚本：批量重生成 12_reviewer_receipt.json（reviewed_object_sha256=对应 11 canonical_hash，符合 CA-103 契约）
   - 保留原 receipt 为 `.legacy.json` 备份；新 receipt 用当前格式
   - 测试：批量 receipt-validate 112/117 通过（5 个 CA-001..004/101 旧格式 grandfathered）
   - 复核：独立 reviewer
   - 检查点：closure-report 87 incomplete → 0 incomplete

5. **GP-005**（C-2 scenario 证据回填）：197 场景真实执行证据
   - 写 scenario execution runner（逐场景真实执行 + evidence_path 记录）
   - 回填：197 个 scenario 的 status=passed + evidence_path（receipt/日志路径）
   - 测试：scenario-verify 从 197 unsatisfied → 0 unsatisfied
   - 复核：独立 reviewer
   - 检查点：scenario-verify 绿 + closure-report 完整

### Phase 3：生产接线（D-3 + B-4）

6. **GP-006**（D-3 真实 roots E2E 进 CI）：CI 加 windows-latest 单 job 或 self-hosted runner
   - 修改：.github/workflows/quality.yml 加 job `real-roots`（windows-latest，需 git clone sibling repos）
   - 测试：真实 roots 套件（test_zr806/test_zr1004 等）在 windows-latest 通过
   - 检查点：CI 三 job 全绿（ubuntu quality + ubuntu contract + windows real-roots）

7. **GP-007**（B-4 privacy_class 3.0 config 升级）：生产 config schema 1.0 → 3.0
   - 修改：config/source_catalog.yaml schema 升级 + privacy_class 字段
   - 测试：config_doctor 兼容 + wiki 全套回归
   - 检查点：config_doctor 绿 + config schema=3.0

### Phase 4：部署动作监督（B-1/B-2/B-3——这些需要自然时间/授权，不主动实施，但建立监督机制）

8. **GP-008**（B-1 legacy 删除准备）：注册 Windows 任务开始生产观测
   - 动作：注册 revenue_daily_t2 任务（schtasks /create）→ 每日跑 daily_t2_runner → 开始累积 legacy_bridge_hits 观测
   - 监督：连续 2 个 ≥24h 窗口零 hit 后 CA-304 可执行删除
   - 本计划只建立观测起点，不执行删除

9. **GP-009**（B-2 自然时间审核准备）：注册 Daily/Weekly/Monthly 调度任务
   - 动作：注册 schtasks（daily T2、weekly T3、monthly broker）→ 开始累积自然时间证据
   - 监督：7 Daily/2 Weekly/1 Monthly/1 alert drill 完成后回填 closure ledger
   - 本计划只注册调度起点，不等自然时间

10. **GP-010**（B-3 研报语义处理准备）：向 KD-08 提交 cohort cutover 授权请求
    - 动作：写授权申请文档（七份研报语义处理的范围/方法/风险）→ 等待批准
    - 本计划只提交申请，不执行处理

## 3. 每个工作单元的验收标准（统一）

每个 GP 必须满足：
- **RED→实施→GREEN**：先有失败测试，再修复，再绿
- **独立复核**：reviewer 独立重跑/重扫，写 12_reviewer_receipt.json
- **机器证据**：11 receipt canonical hash 可重算；12 指向 11 hash
- **状态机**：lock-acquire → preflight_locked → red_proved → implemented → focused_green → owner_repo_green → triplet_green → independent_review → accepted（在 state.json 中记录）
- **质量门**：ruff 0、mypy 0、coverage 不降、mutation patrol 全杀
- **文档更新**：完成后更新本页 progress.md（追加该 GP 的证据摘要）

## 4. 依赖顺序

```
GP-001（回归）→ GP-002（scanner）→ GP-003（worker）→ GP-004（receipt 重签）→ GP-005（scenario 回填）→ GP-006（CI 接线）→ GP-007（config 升级）
→ GP-008（legacy 观测起点）→ GP-009（调度注册）→ GP-010（cutover 申请）
```

## 5. 当前状态

- 已修复：A-1、A-2、A-3（2026-09-02 本轮审查发现，已 push 验证）
- ✅ **GP-001 完成**（2026-09-02）：三仓回归全绿
- ✅ **GP-002 完成**（wiki 9809127）：v2 scanner 生产切入（D-1 closed）
- ✅ **GP-003 完成**（wiki c3a99c8）：LLM exit receipt+privacy gate（D-2 closed）
- ✅ **GP-004 完成**（revenue 04556d5）：receipt 重签发 87→0 incomplete（C-1 closed）
- ✅ **GP-006 完成**（revenue 43fab74）：real-roots CI job + 9 sibling tests（D-3 closed）
- ✅ **GP-007 完成**（wiki c636516）：privacy_class 配置升级（B-4 closed）
- 📋 **GP-008/009 部署指南就绪**：schtasks register 命令文档化，需管理员权限执行
- ✅ **GP-010 申请文档完成**：cohort cutover 授权申请，待 KD-08 批准
- 进行中：GP-005（scenario 证据回填，197 scenarios）
- 机器状态：accepted 117/117，current_next=CA-201（终局游标）
- 三仓 CI：wiki 9809127 success / revenue 5e6f603 success（GP-004 在 assurance/，不影响 CI 测试路径）
