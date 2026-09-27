# ZR-404 工作单元卡（preflight）— envelope 带 policy snapshot 一致性、候选排除 trace、canonical location rationale

- 领取时间：2026-08-18T20:55Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-404`；units.ZR-403.status=accepted + closure.next=ZR-404；锁 ZR-404（owner=zr404-implementer）。
- 依赖：ZR-403（accepted ✅）。Registry 依赖列=ZR-403。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D envelope 一致性证据。现状 `build_resolution_envelope`（FC-704/FC-902/FC-905-a）已带 outcome/download_events/policy_hash/activation_epoch/bundle/prompt_injection/parser/llm，但缺：候选排除 trace（resolution.debug_trace 已生成但未随 envelope 输出）、canonical location rationale（谁胜出+为什么+路径脱敏）、cohorts/source hash 一致性（policy/epoch/cohort/source hash 四键同源未表达）、policy_snapshot 形状 fail closed。
2. **production entrypoint 是什么？** `resolver.build_resolution_envelope`（cli resolve/ensure + close_gap._finalize 三个生产调用方）；消费方 filing `validate_resolution_envelope`（filing_contracts.py:237，对未知字段宽容=加性 N/N-1 安全）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 排除 trace 未输出**：debug_trace 在 ResolutionResult 内已生成（per-candidate why-not），envelope 不携带。
   - **G2 canonical rationale 缺失**：无"哪个 canonical location 胜出+选择规则+脱敏路径"的结构化输出。
   - **G3 policy 一致性四键不全**：policy_hash+epoch 有，cohorts 与 source hash 无；policy_snapshot 形状无校验（坏 hash/epoch/cohorts 静默透传，非 fail closed）。
   - **G4 路径脱敏缺失**：canonical_path 绝对路径随 envelope 输出，无 ${PROJECT_ROOT}/${USER_PROFILE} token 化。
4. **允许改哪些文件？** company-wiki resolver.py（ResolutionEnvelope + build_resolution_envelope + _redact_path）+ cli.py/close_gap.py（两个 envelope 调用点传 project_root）+ 新测试 tests/contract/test_zr404_envelope_trace_rationale.py。禁止：改 filing（加性契约，filing 侧零改动）、真实 catalog 写、下载。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-405（filing 透明验证任意 policy-allowed root）。本卡不做：filing 侧改动、bundle 内容改造、envelope schema_version 升级（保持 "1.0" 加性）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-403 accepted（机器状态；closure.next=ZR-404）。
- [x] triplet 冻结（领取时重读）：revenue `ce8152a…`（ZR-403 closure commit）、filing `df66796…`、wiki `57cd72e…`（ZR-404 实现提交 f45f7ed 为 result）。
- [x] 现状代码事实：ResolutionEnvelope 字段（FC-704/902/905-a）；`_STRUCTURAL_OUTCOME`/`_ENVELOPE_OUTCOME_BY_JOURNAL`/`_ENVELOPE_DOWNLOAD_OUTCOMES`；debug_trace 存在于 ResolutionResult；filing validate_resolution_envelope 校验已知键、容忍未知键（加性安全）；schema_version 两侧均 "1.0"。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（resolver/cli/close_gap + 测试）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——四缺口（G1~G4）确认（见 red 探针）。
- **Acceptance criteria**：
  - **C1 policy/epoch/cohort/source hash 四键一致性（杀 G3）**：policy_snapshot 提供时 policy_hash/activation_epoch/cohorts 同源输出；source_sha256=匹配 handle 的 content hash；无 snapshot 时诚实 None（不伪造）。
  - **C2 冲突 fail closed（杀 G3）**：policy_snapshot 非 dict、policy_hash 非 64-hex、current_epoch 非文本、active_cohorts 非 str 列表/元组 → ValueError；形状规则与 filing 校验器逐字一致（0-9a-f{64}）。
  - **C3 候选排除 trace（杀 G1）**：envelope 携带 resolution.debug_trace（per-candidate why-not；匹配时含 matched 行）。
  - **C4 canonical location rationale + 路径脱敏（杀 G2/G4）**：有匹配时输出 {canonical_location_id, canonical_path（${PROJECT_ROOT}/${USER_PROFILE} token 化）, selection, source_sha256}；envelope JSON 全串无绝对项目路径。
  - **C5 加性 N/N-1（契约）**：schema_version 保持 "1.0"；旧键不变；filing validate_resolution_envelope 接受新字段并透传；序列化确定性保持。
  - 质量门：unit/contract 无回归；复杂度 ratchet（resolver.py 冻结 max 不超）；FC-1201 allowlist 不漂移；mypy 零新增错误（基线既有 2 条记入 finding）；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、需要改 filing 或 schema_version → 立即停止。

## Annex：envelope 字段矩阵（ZR-404 加性）

| 字段 | 来源 | 缺省 |
|---|---|---|
| policy_hash / activation_epoch | policy_snapshot（严格形状） | None |
| cohorts | policy_snapshot.active_cohorts（str 列表） | None |
| source_sha256 | matches[0].content_sha256 | None |
| candidate_exclusion_trace | resolution.debug_trace | () |
| canonical_location_rationale | matches[0] handle + project_root 脱敏 | None |
