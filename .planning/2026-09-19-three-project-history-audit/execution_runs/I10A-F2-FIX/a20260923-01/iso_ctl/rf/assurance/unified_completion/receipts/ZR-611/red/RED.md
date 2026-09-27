# ZR-611 RED 探针证据

- 日期：2026-08-22
- RED：无单一产品缺口——ZR-601~608+610 各模块单测已绿，但**组合旅程不存在**：控股链+权益法+多金属+内供+跨币种+爬坡+gap+residual 八类场景未跨层串起来。
- 探针：各模块 import 冒烟已过（asset_ownership/mine_year_operation/commercial_terms/internal_flow/reconciliation 均独立可导入可调用）；无跨层合成验证。
- drift verdict: `still_missing`（组合旅程缺失）。修复：test-only E2E——新 `tests/test_zr611_synthetic_e2e.py` 合成多矿公司全链旅程，每类场景确定性可重算。
