# ZR-603 RED 探针证据（drift_classified → red_proved）

- 日期：2026-08-22
- 探针命令与结果（全部在 revenue-forecast CWD，base python）：

## P1：ownership 计算词汇缺失（真实产品缺口）

```
grep ownership|consolidat|equity_share|effective_date|country|region scripts/*.py scripts/contracts/*.py scripts/forecast/*.py
→ 命中均为无关同名：
  - revenue_backtest/revenue_report 的 consolidated_forecast = 场景合并（low/base/high 汇总），非所有权并表
  - lint_input:445 segment_attribution = 驱动归因权重（growth driver tree）
  - constants.py:89 equity_share = ZR-602 ASSET_FACT_OWNERSHIP_BASES 枚举值（纯声明，无计算）
→ 无 ownership fraction、无 effective_date 时点查询、无链式权益计算
```

## P2：二次乘权益无防护（真实产品缺口）

```
grep equity|minority|ownership_pct|stake|holding → 零计算命中
→ 若收入已按权益法折算再乘链式权益（Kamoa/Porgera 双重折算模式）无 fail-closed 门
→ apply-once 防护不存在
```

## P3：地区层级缺失（真实产品缺口）

```
grep country|region|geo → 零命中
→ segment 校验（document.py:802- validate_segments）无 geography/ownership 键
→ 资产无法按国家/地区检索
```

## drift verdict

- `still_missing`：G1（ownership timeline 契约）/G2（不二次乘权益防护）/G3（地区层级）均为真实产品缺口——与 ZR-602 修复前形态相同（词汇与机制全缺）。
- 修复边界：新 `scripts/asset_ownership.py`（契约纯函数层——timeline 校验/时点查询/period 处理/链式权益/apply-once 门/geography 校验与索引）+ document.py validate_segments 加性调用（geography/ownership 键存在时校验，None 早退零 McCabe 增量）。不动模型公式语义、不动输出路径（golden 行为锁）、不做内部交易/对账（ZR-607/608）、不冻结 ADR（ZR-610）。
