# RED.md — CA-204 Monthly broker/mine/forecast 泛化审核（阶段 H CA 部分第三卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-204 验收套件**：glob tests/**/*ca204* → 零命中。
- **G2 无 Monthly 泛化组合验收**：ZR-609（Zijin pilot + 第二矿企泛化）、ZR-709（紫金 journey）、ZR-713（rolling backtest）各自存在；无"固定+轮换样本 registry + 紫金 shadow + 第二矿企 + 非矿企 + 表格/错归复验 + 产品特例扫描=0 + backtest/confidence"一体验收。
- **G3 真实现状（只读确认）**：golden corpus 12 samples（broker_research 7 含 changjiang 多实体、audited_filing 2、company_release 1、revenue_forecast_input/result_draft 各 1）；scripts/ 零硬编码（git grep 紫金矿业/601899 → ZERO）。

## 既有能力（不重复建设）

- ZR-609 第二矿企（纯金生产商无控股链单货币）全链；ZR-709 紫金 journey（draft/formal/replay + reconcile）；ZR-713 rolling backtest + snapshot；ZR-503/504/505 多实体/表格保真 golden anchors；confidence_policy（detect_gaming_mutations/recompute_rating/validate）；golden_corpus.json 冻结样本。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca204_monthly_generalization.py`（8 tests：C1 固定+轮换 registry + 缺失 BLOCKED；C2 紫金 shadow journey；C3 第二矿企链闭合；C4 非矿模型引擎路径；C5 表格/错归 anchors + 零硬编码扫描；C6 snapshot replay + confidence 资产），产品零改动。
