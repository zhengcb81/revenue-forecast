# ZR-707 工作单元卡（preflight）— F2：扩展模型组合与 schema 表达 mixed recognition/gross-net

- 领取时间：2026-08-23T06:15Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-707`，ZR-711 accepted + closure→ZR-707；锁 ZR-707。
- 依赖：ZR-608（✅ reconciliation）、ZR-610（✅ 会计 ADR）、ZR-711（✅ schema 3.8 opt-in）。Registry 依赖列=ZR-608,ZR-610,ZR-711。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 扩展模型组合——mixed recognition（同公司不同分部可有不同收入确认模式：modeled_as_recognized vs lagged_activity）、mixed gross/net presentation（不同分部可有不同展示口径）、mine×commodity×product 多维矩阵、segment bridge 正确性、贸易/其他活动不用单一错误 presentation 近似。
2. **production entrypoint 是什么？** `scripts/contracts/constants.py`（已有 RECOGNITION_MODES/PRESENTATIONS）、`scripts/contracts/document.py`（validate_recognition_metadata、mixed-mode 验证）、`scripts/forecast/segments.py`（segment_bridge）。
3. **RED？** 探针：RECOGNITION_MODES/PRESENTATIONS 已存在；segment_bridge 已存在；multi-commodity product matrix 零实现；mixed-mode 组合无显式验证测试。
4. **允许改哪些文件？** revenue：新 `scripts/mixed_recognition.py`（mixed-mode 验证 + multi-commodity + presentation 矫正）、新 `tests/test_zr707_mixed_recognition.py`；revenue receipts/ZR-707/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-712（confidence 反博弈）。本卡不做：confidence policy（ZR-712）、backtest（ZR-713）。

## Acceptance criteria
- **C1 mixed recognition 组合验证**：同公司不同分部可使用不同 recognition mode（modeled_as_recognized/lagged_activity）——validate_document 接受 mixed-mode 文档；每个分部独立校验自己的 recognition metadata；mixed 组合不引发冲突。
- **C2 multi-commodity product matrix**：同一 mine 可以有多个 commodity lines（铜+金副产品）——每个 commodity 独立计算 saleable_volume；product_revenue = Σ(commodity_volume × commodity_price)；不重复计价（byproduct 独立加项）。
- **C3 presentation 矫正**：trading/other 活动必须声明正确的 presentation（gross/net）——不靠单一错误 presentation 近似；segment bridge 一致性（各分部 presentation 与 group 合并口径一致）。
