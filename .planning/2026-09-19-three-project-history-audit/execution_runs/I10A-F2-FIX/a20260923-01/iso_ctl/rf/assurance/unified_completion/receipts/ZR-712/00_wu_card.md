# ZR-712 工作单元卡（preflight）— F2：版本化 ConfidencePolicy 与反博弈

- 领取时间：2026-08-23T07:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-712`，ZR-708 accepted + closure→ZR-712；锁 ZR-712。
- 依赖：ZR-708（✅ 不可变 snapshot/backtest——accuracy record 消费链已验）。Registry 依赖列=ZR-708。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 版本化 ConfidencePolicy 与反博弈——confidence 计算策略版本化（policy version + 权重/rating caps 数据化而非硬编码），duplicate/split/plug/zero-impact/one-observation/wrong-record 六类博弈 mutations 全杀；rating caps 可重算。
2. **production entrypoint 是什么？** `scripts/analysis/confidence.py`（calculate_confidence 权重/rating 硬编码）+ `scripts/contracts/evidence.py`（validate_historical_accuracy_records）。
3. **RED？** 探针：confidence.py 权重 20/25/10/15/15/15 与 rating 阈值 80/55 硬编码（无 policy 对象、无版本）；无博弈检测（duplicate/split/plug/zero-impact/one-observation/wrong-record 六类 mutation 均无显式拒绝/披露）；test_scenarios_confidence 仅覆盖 duplicate sensitivity/source rank/segment crossing 三例。
4. **允许改哪些文件？** revenue：新 `scripts/confidence_policy.py`（policy 版本化 + 六类博弈检测 + rating 重算）、新 `tests/test_zr712_confidence_policy.py`；若需接线则 confidence.py 调用 policy 校验（加性）。禁止：改置信度公式语义（存量权重不变）、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-713（紫金 rolling-origin）。本卡不做：rolling-origin backtest（ZR-713）。

## Acceptance criteria
- **C1 版本化 policy**：CONFIDENCE_POLICY_VERSION；validate_confidence_policy(policy)——未知版本 fail-closed；policy 携带权重表 + rating caps（数据化）。
- **C2 六类博弈 mutations 全杀**：
  - duplicate：重复 accuracy record（同 backtest_id / 同 observation key）→ 拒绝
  - split：同观测被拆成多条（同 year+source+value 多记录）→ 拒绝
  - plug：无 hash 链接（缺 record_sha256 或 mismatch）→ 拒绝
  - zero-impact：无实际影响的记录 → 不提升 score（诚实披露）
  - one-observation：单观测 → history_score 封顶（不显著提升）
  - wrong-record：篡改记录（hash mismatch）→ 拒绝
- **C3 rating caps 可重算**：recompute_rating(score, caps) 从 policy caps 重算 rating（high/medium/low），与 confidence.py 现有 80/55 阈值一致（存量零回归）。
