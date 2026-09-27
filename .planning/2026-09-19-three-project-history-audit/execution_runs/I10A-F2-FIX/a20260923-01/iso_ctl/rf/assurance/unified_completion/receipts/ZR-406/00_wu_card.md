# ZR-406 工作单元卡（preflight）— 正交 local-match 与 provider freshness/coverage planner

- 领取时间：2026-08-18T21:50Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-406`；units.ZR-405.status=accepted + closure.next=ZR-406；锁 ZR-406（owner=zr406-implementer）。
- 依赖：ZR-403（accepted ✅）。Registry 依赖列=ZR-403。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 正交对齐验收。`gap_plan.build_gap_plan`（WU-4.2）已实现：local 可复用 handle × remote provider 元数据对齐，输出 reuse/missing/newer_revision/not_published/provider_unavailable/future + gap_hash。legacy FC-803（gap orchestration）implemented_not_independently_verified → 本卡钉死**正交矩阵**：local-match 状态（exact/equivalent/missing/ambiguous/unusable）× provider 状态（current/newer_period/newer_revision/not_published/unknown/future）+ as_of 防泄漏 + 非自然年/修订去重。
2. **production entrypoint 是什么？** 纯函数 `build_gap_plan`（gap_plan.py:85）+ 生产消费：close_gap._finalize（ZR-307 已接 envelope）、acquisition coordinator latest_as_of、service ensure。本卡验收侧：`tests/contract/test_zr406_gap_plan_orthogonality.py`（新增）；产品零改动预期。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 正交矩阵未钉死**：既有测试覆盖 current/newer_period/newer_revision/not_published/provider_unavailable/future 单维度各一例；**local 状态 × provider 状态的组合矩阵无系统化测试**（local=无 handle/MISSING、local=多 handle/AMBIGUOUS、local=capture-incomplete/unusable 的组合行为未钉死）。
   - **G2 未知日期 eligible 保守性未钉死**：remote 无 filing_date 的候选当前按 eligible 处理（`not _candidate_filed(c) or ...`）——保守进 gap 而非静默排除；无测试钉死该行为（防 as_of 泄漏方向 2）。
   - **G3 非自然年/修订去重未钉死**：同一 fiscal_year 多 period_end（非自然年财报年度跨自然年）无测试；amended+original 同周期只报一个 newer_revision（修订去重）无独立矩阵测试。
   - 既有已钉死（不重复）：future 排除（test_remote_after_as_of_excluded）、provider_unavailable 不伪绿、gap_hash 确定性/顺序无关、同周期多 accession。
4. **允许改哪些文件？** company-wiki 新增 `tests/contract/test_zr406_gap_plan_orthogonality.py`（如发现真实行为缺口则最小改 gap_plan.py，逐条记录）；revenue 侧 receipts/ZR-406/** 与 state.json。禁止：真实 catalog 写、下载。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-407（authorization-bound GapPlan/CloseGap）。本卡不做：下载授权（ZR-407）、下载执行（ZR-408）、未来根生产切换（ZR-409）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-405 accepted（机器状态；closure.next=ZR-406）。
- [x] triplet 冻结（领取时重读）：revenue（ZR-405 closure commit 后）、filing `3087f28…`、wiki `e56eb5f…`。
- [x] 现状代码事实：build_gap_plan 规则（provider_error→unavailable；future 排除；local_by_year/remote_by_year 对齐；同周期取最新 accession（amended 排序在后）；local 无对应 remote→reuse；remote 无对应 local→missing；无 missing 且无 newer_revision→not_published）；_hash_gap 确定性（排序键 fiscal_year+accession）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（验收测试）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——三缺口（G1~G3）。
- **Acceptance criteria**：
  - **C1 正交矩阵（杀 G1）**：数据驱动矩阵——local 状态（无/matched-exact/matched-equivalent/多 handle-ambiguous/capture-incomplete-unusable）× provider 状态（current/新周期/新修订/无更多/未知-error/未来）全组合断言（每格：reuse/missing/newer_revision/not_published/future 五元组 + gap_hash 确定性）。含局部状态语义映射：无 local→对应周期全 missing；多 local 同周期→取最新 accession 对齐；unusable local→不进入 reuse（不伪绿）。
  - **C2 as_of 防泄漏（杀 G2）**：future-dated（filing_date > as_of）→future 且不进 gap（既有）；**无 filing_date → eligible（保守进 gap，绝不静默丢弃）**；not_published 不被 future 候选否定。
  - **C3 非自然年/修订去重（杀 G3）**：同一 fiscal_year 多个 period_end 的 local/remote 归并到同一周期桶（无幻影 gap）；amended+original 同周期 → 仅最新 accession 进 newer_revision（去重）；本地已是最新修订 → reuse 不下载。
  - hermetic 全绿；wiki unit/contract 无回归；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、需要改 close-gap 语义 → 立即停止并登记。

## Annex：正交矩阵（local × provider）

| local \ provider | current | newer_period | newer_revision | not_published | unknown(err) | future |
|---|---|---|---|---|---|---|
| 无 local | missing | missing | — | not_published | unavailable+local∅ | future+not_published |
| exact 匹配 | reuse(0) | missing+reuse | newer_revision+reuse | not_published+reuse | unavailable+reuse | future+reuse |
| equivalent 匹配 | reuse(0) | 同上 | 同上 | 同上 | 同上 | 同上 |
| 多 handle | 最新对齐 reuse | missing+最新 reuse | newer_revision+全部 reuse | not_published+全部 reuse | unavailable+全部 reuse | future+全部 reuse |
| unusable | 不 reuse | 不 reuse | 不 reuse | 不 reuse | 不 reuse | 不 reuse |
