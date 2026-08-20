# ZR-705 工作单元卡（preflight）— F1：draft/formal 分离与互换攻击门（REV-06~08）

- 领取时间：2026-08-21T00:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-705`，ZR-704 accepted + closure→ZR-705（phase=F_revenue_mining；状态机自动跳过阶段 E 已闭的 ZR-505）；锁 ZR-705（owner=zr705-implementer）。
- 依赖：ZR-701（✅ draft mode）、ZR-702/703（✅ schema 真源）、ZR-704（✅ validate-only 门）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F1 第五卡：**draft/formal 分离（REV-06~08）**——draft 可 render 不发布；formal 强门+签名；互换/重 hash 攻击失败。机制已存在（build_draft_receipt gate_ids=[] / build_publication_receipt 需 VerificationContext 强门 / validate_publication_receipt 强校验），但互换/重 hash 攻击失败路径无钉死测试。
2. **production entrypoint 是什么？** `revenue_publication.py`（build_draft_receipt / build_publication_receipt / validate_publication_receipt）+ `revenue_report.render_markdown`（draft 可 render）+ `validate_published_forecast`（强门）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 互换攻击无钉死**：draft receipt 冒充 formal（formal_output_mode 篡改）→ 消费者接受？无测试断言拒绝。
   - **G2 重 hash 攻击无钉死**：篡改 result（改数值）后 receipt 的 validated_payload_sha256 失配 → validate_publication_receipt 拒绝？无测试。
   - **G3 draft 可 render 不发布无钉死**：draft 结果 render_markdown 可用 + 不触发 registry 注册。
4. **允许改哪些文件？** revenue：新测试 `tests/test_zr705_draft_formal_swap.py`（REV-06~08 门测试）；可能少量产品代码（若探针发现缺口）；revenue receipts/ZR-705/**。禁止：改 validator/receipt 契约语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-710（publication 事务 REV-09）。本卡不做：publication 事务/故障注入（ZR-710）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-704 accepted（closure.next=ZR-705；ZR-505 已 E 阶段闭自动跳过）。
- [x] triplet 冻结：revenue（ZR-704 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：build_draft_receipt gate_ids=[] + formal_output_mode=draft；build_publication_receipt 需 VerificationContext（不能自签）+ attestation_status；validate_publication_receipt 校验 payload hash/gate_ids/engine 版本。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（REV-06~08 门测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 draft 可 render 不发布（REV-06）**：draft 结果 `render_markdown` 可用（draft receipt 不阻塞 render）；draft 结果不注册 publication_registry（entry 数不变）。
  - **C2 formal 强门+签名（REV-07）**：formal 结果 receipt 含 gate_ids（非空）+ attestation_status ∈ {host_signed, unattested}；无 VerificationContext 时 build_publication_receipt 抛 TypeError（不能自签）。
  - **C3 互换攻击失败（REV-08a）**：draft receipt 改 formal_output_mode="formal" → validate_publication_receipt 拒绝（gate_ids=[] ≠ 期望门）；formal receipt 改 formal_output_mode="draft" → 拒绝。
  - **C4 重 hash 攻击失败（REV-08b）**：篡改 result（改某 segment 数值）→ 旧 receipt 的 validated_payload_sha256 失配 → validate_publication_receipt 拒绝；重算 receipt_sha256 不修复（payload 失配独立校验）。
  - 质量门：revenue tests/ 全量无回归；ruff clean；ratchet 绿。
- **Stop conditions / handoff**：改 validator/receipt 契约语义、真实 catalog 写、下载、LLM → 立即停止。

## Annex：REV-06~08 判定矩阵

| 攻击/场景 | 期望 |
|---|---|
| draft receipt 篡改 formal_output_mode="formal" | validate_publication_receipt 拒绝 |
| formal receipt 篡改 formal_output_mode="draft" | 拒绝 |
| 篡改 result 数值（payload hash 失配） | 拒绝 |
| 重算 receipt_sha256（payload 仍失配） | 仍拒绝 |
| build_publication_receipt 无 VerificationContext | TypeError（不能自签） |
| draft 结果 render_markdown | 可用（draft 不阻塞 render） |
| draft 结果 registry | 不注册（entry 数不变） |
