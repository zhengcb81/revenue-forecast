# ZR-1007 工作单元卡（preflight）— I：mine facts/model shadow 与旧分部模型对比

- 领取时间：2026-08-31T12:55Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1007`（ZR-1006 closure → ZR-1007）；锁 ZR-1007（owner=zr1007-implementer，nonce 0a752806…）。
- 依赖：ZR-1006（broker cohort，accepted ✅）、ZR-609（Zijin pilot 全链，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 第七卡——mine facts/model shadow 与旧分部模型对比（registry："差异归因、reconciliation、backtest；不自动替换生产预测"）。现状缺口（RED）：ZR-605/609 有 MineYearOperation→resource model 单路径；无"shadow 与旧分部模型并存对比 + 差异归因 + reconcile + mine-volume backtest + 零写（不替换生产）"组合验收。
2. **production entrypoint 是什么？** revenue `to_resource_model_drivers`（ZR-605 C3）→ `calculate_model_path("resource")`（shadow 新链）；旧分部模型 `direct_growth`/`unit_sales`（model_registry 注册）；`reconcile_layer`/`gap_report`（ZR-608）；`run_rolling_backtest`（ZR-713 mine-volume level）；`publication_registry`（R1.2，必须零写）。
3. **RED？** glob tests/**/*zr1007* → 零命中；无 shadow/旧模型并存对比测试；grep shadow/mine_facts/旧分部/差异归因 → 现有测试零命中。
4. **允许改哪些文件？** revenue：新 `tests/test_zr1007_mine_shadow.py`；receipts/ZR-1007/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、publication registry 写、下载、LLM。
5. **下一单元解锁？** ZR-1008（source/revenue 新链 cohort cutover，三仓）。本卡不做：真实切换生产预测（部署）、formal forecast 生成（draft 边界）。

## Acceptance criteria

- **C1 shadow 路径可算**：MineYearOperation → to_resource_model_drivers → calculate_model_path("resource") 输出 == saleable_volume × realized_price（手算 427.5×5.0=2137.5）；旧分部模型路径并存可算（direct_growth 100→110/121）。
- **C2 差异归因**：mine-facts driver 变化（volume +20%、recovery 0.9→0.8、price 5→6）各自产生可归因 delta（Δ=Δdriver 贡献）；旧模型只响应自己的 driver。
- **C3 reconciliation**：shadow 逐矿贡献对 legacy 合计 reconcile_layer 闭合（reconciled_modeled）；不闭合时 gap_report 诚实报 gap（difference 如实，不伪造为收入）。
- **C4 backtest**：run_rolling_backtest mine-volume level 分解 saleable_volume（2 矿 427.5+855.0=1282.5）；future actual leak → ForecastInputError fail-closed。
- **C5 零替换**：shadow + legacy 计算全程 publication registry 零写（_append 打桩即炸）；run_forecast 零调用（spy 断言）——生产预测输出不变。
- **C6 质量门（卡级）**：相邻回归（ZR-605/609/713）零回退、revenue 全量零回归（基线 896+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 纯内存计算（无 catalog/网络/LLM）；publication registry 由 conftest 隔离到 tmp；不生成 formal forecast；不写任何 registry/文件。
