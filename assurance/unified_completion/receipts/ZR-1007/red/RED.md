# RED.md — ZR-1007 mine facts/model shadow 与旧分部模型对比（阶段 I 第七卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1007 验收套件**：glob `tests/**/*zr1007*` → 零命中。
- **G2 无 shadow/旧模型并存对比**：grep shadow/mine_facts/旧分部/差异归因 → test_zr60x/70x 零命中；ZR-605 仅单路径（to_resource_model_drivers → resource model），无"shadow vs legacy 并存 + 归因 + reconcile + backtest + 零写"组合。
- **G3 机制在位（不重复建设）**：mine_year_operation.to_resource_model_drivers（{saleable_volume, realized_price}）；model_registry resource/direct_growth/unit_sales 已注册；reconciliation.reconcile_layer/gap_report（ZR-608）；rolling_backtest.run_rolling_backtest mine-volume level（ZR-713）；publication_registry（R1.2）。

## 既有能力（不重复建设）

- ZR-605 C3 drivers→resource model；ZR-608 reconcile_layer/gap_report；ZR-609 pilot 全链；ZR-713 rolling backtest（mine-volume 分解 + as-of 纪律）；test_models.make_parameters/YEARS；test_backtest.actuals_document；test_zr713._window。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1007_mine_shadow.py`（12 tests：C1 shadow 可算 + legacy 并存；C2 差异归因；C3 reconcile/诚实 gap；C4 mine-volume backtest + as-of；C5 零 registry 写 + run_forecast 零调用），产品零改动。
