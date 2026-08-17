# ZR-302 工作单元卡（preflight）— prompt-injection scanner/reviewer receipt 的生成、缓存与失效

- 领取时间：2026-08-17T20:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-302`；units.ZR-301.status=accepted + closure.next=ZR-302；`uc next` 解锁列表含 ZR-302。
- 依赖：ZR-301（accepted ✅）。Registry 依赖列=ZR-301。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 安全 receipts。现状：`prompt_injection.py` 已有 FC-905 的 receipt 写入/读取（status ∈ {not_detected, detected_and_ignored}，存于 `documents.metadata_json["prompt_injection_review"]`，schema 1.0），但 receipt **未绑定 source/policy hash**、**无缓存命中/忽略/过期/篡改判定**、扫描器未接入。ZR-301 的 safety 阶段目前只能区分"有 receipt / 无 receipt"，无法回答"这个 receipt 还新鲜吗？规则集变了吗？源字节变了吗？"。
2. **production entrypoint 是什么？** 本卡 shadow 侧：新增 `prompt_injection_guard.py`（扫描器 + 缓存求值，纯函数/只读 reader，不写 catalog 的求值路径；receipt 生成仍走既有 `record_prompt_injection_review` 写入路径并**增量绑定** source_sha256/policy_hash）。不接生产 CLI（ZR-303 统一决策图接线）。
3. **哪个 current-triplet 行为是 RED？** receipt 无 source/policy hash 绑定（无法检测过期/篡改/规则集变更）；`not_reviewed` 语义存在但缺少"命中/忽略/过期/篡改"四类缓存判定的显式结果。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/prompt_injection_guard.py`（新模块，复杂度≤10）+ 增量扩展 `prompt_injection.py`（record 增加可选绑定字段，保持既有 N-1 行为）+ `tests/unit/test_prompt_injection_guard.py` + `tests/contract/test_zr302_prompt_injection_guard.py`；revenue 侧 receipts/ZR-302/** 与 state.json。禁止：写 catalog 的求值路径、改既有 receipt 读取语义、接生产入口、改 reader/锁/schema。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-303（统一 machine decision graph）。本卡不接线生产（ZR-303）；不做 artifact validator（ZR-304）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-301 accepted（机器状态；closure.next=ZR-302）。
- [x] triplet 冻结（领取时重读）：revenue `181a497…`（ZR-301 receipt commit 后）、filing `0e5d209…`、wiki `09deecb…`。
- [x] 现状代码事实：`prompt_injection.py` record/read 已 fail-closed（status 枚举、reviewer 非空、evidence_sha256 64-hex、schema 1.0）；`read_prompt_injection_review` 对 malformed receipt 返回 None（调用方视为 not_reviewed）；`source_lifecycle._safety_reviewed`（ZR-301）已按"无 receipt→unknown"消费；complexity frozen prompt_injection.py ≤15、coverage ≥73%。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品新模块）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——receipt 无 hash 绑定、无缓存生命周期判定、无扫描器。
- **Acceptance criteria**：
  - `PROMPT_INJECTION_GUARD_SCHEMA_VERSION`/`SCHEMA`：版本化扫描器+缓存求值 schema。
  - 扫描器：`scan_text(text, ruleset_hash)` 确定性检测注入模式 → (status, matches)；未知 ruleset hash fail closed；ruleset 版本化（patterns + hash 绑定）。
  - receipt 生成（增量扩展 `record_prompt_injection_review` 可选 `source_sha256`/`policy_hash`）：提供时强校验（64-hex），写入 receipt dict；未提供时保持既有行为（N-1 兼容）。
  - 缓存求值 `evaluate_review(store, document_id, *, source_sha256, policy_hash, now, ttl_seconds)` → `{status, cache_state}`：
    - `hit`：receipt 有效 + source_sha256 匹配 + policy_hash 匹配 + 未过期 → 转发 receipt status；
    - `ignored`：policy_hash 不匹配（规则集已变）→ not_reviewed（绝不用旧规则集伪绿）；
    - `expired`：reviewed_at 超过 TTL → not_reviewed；
    - `tampered`：source_sha256 不匹配（源字节已变）或 receipt malformed → not_reviewed（fail closed）；
    - `absent`：无 receipt → not_reviewed。
  - `not_reviewed` 永不伪绿：四类失效均显式返回 not_reviewed + cache_state。
  - hermetic 测试：命中/忽略/过期/篡改/缺失五场景、TTL 边界、malformed fail-closed、扫描器确定性、ruleset 未知 hash 拒绝、N-1（无绑定字段的旧 receipt 仍可读）；复杂度≤10；wiki unit/contract 全绿。
- **Stop conditions / handoff**：求值路径写 catalog、改既有 receipt 语义、接生产入口 → 立即停止。

## Annex：缓存判定矩阵

| 场景 | receipt 存在 | source_sha256 匹配 | policy_hash 匹配 | 未过期 | 结果 |
|---|---|---|---|---|---|
| hit | ✓ | ✓ | ✓ | ✓ | 转发 status |
| ignored | ✓ | ✓ | ✗ | — | not_reviewed（规则集变更） |
| expired | ✓ | ✓ | ✓ | ✗ | not_reviewed |
| tampered | ✓ | ✗ | — | — | not_reviewed（源字节变更） |
| malformed | 无效 | — | — | — | not_reviewed（cache_state=absent，fail closed） |
| absent | ✗ | — | — | — | not_reviewed |
