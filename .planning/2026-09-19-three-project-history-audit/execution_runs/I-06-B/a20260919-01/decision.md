# decision.md — I-06-B / a20260919-01

实现者：本 attempt（来源安全 reviewer 冻结方法 / 独立 reviewer 验收）。

## 1. D-W06 状态对本卡的影响

D-W06 **未签**。I-06-A 为 **blocked**。本卡（I-06-B）的核心能力（scan_text、record_prompt_injection_review、evaluate_review）已在 CW 产品中实现且可用；但完整端到端路径（从原请求恢复）依赖 I-06-A 的持久需求，本次不可达。

本卡实施策略：
1. **已实现且可验证的能力**：直接测试（scan → receipt → cache → idempotency），全部通过
2. **依赖 D-W06/I-06-A 的能力**：记录为 blocked，不伪造证据

## 2. W06-1 幂等键决策（选 A，已实施）

**选择**：idempotency_key = sha256(canonical_json({entity, as_of_date, document_kind, source_sha256, role_set}))

**理由**：
- 请求身份（entity, as_of_date）入键，解决了 I-06-A OPEN-2 发现的"不同请求被静默合并"问题
- source_sha256 入键确保源字节变化产生新 key
- role_set 入键确保不同角色集不会混淆

**反例已验证**：
- 同请求重提 → 复用（PASS）
- 同 key 不同 payload（entity 变化）→ fail-closed 拒绝（PASS）
- 不同 as_of_date → 不同 key（PASS）

**兼容影响**：需要 I-06-A 的持久需求表增加 `payload_hash` 列用于 fail-closed 验证

**恢复规则**：键算法变更时，所有现有需求必须重新评估（键变更 = 需求作废）

**拒绝的替代方案**：
- 只用 source_sha256 作键：不同请求会被静默合并（I-06-A c8/c9/c10 已证明）
- 不含 role_set：不同角色集可能被错误复用

## 3. 审核方法的证据边界

**已证明可达**：
- `scan_text` 是确定性的、基于版本化规则集的扫描器（规则集 hash = `19ace502...`）
- `record_prompt_injection_review` 要求：非空 document_id、有效 status 枚举、非空 reviewer、SHA-256 evidence、schema_version = "1.0"；可选 source_sha256 + policy_hash 双绑定
- `evaluate_review` 实现五种缓存状态：hit（复用）、ignored（策略变更）、expired（超时）、tampered（字节变更/无绑定）、absent（无回执）
- 所有非 hit 路径返回 not_reviewed（fail-closed）

**未证明（需 D-W06 OPEN-4 签署）**：
- reviewer 身份绑定：当前 reviewer 字段为自由字符串，无身份验证
- 审核工具版本化：当前 ruleset_hash 已版本化，但无独立审核员身份绑定
- detected_and_ignored 的归属决策（OPEN-6）
