# ZR-711 工作单元卡（preflight）— F2：additive schema 3.8 opt-in 与 3.7 兼容/converter

- 领取时间：2026-08-23T00:45Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-711`，ZR-609 accepted + closure→ZR-711；锁 ZR-711。
- 依赖：ZR-701（✅ schema 真源）、ZR-610（✅ 会计 ADR）。Registry 依赖列=ZR-701,ZR-610。

## 领取前五问

1. **推进哪个用户目标/痛点？** F2 additive schema 3.8 opt-in——在 3.7 之上加性引入矿业层（operating units/consolidation），3.7 canonical hash 零回归；converter 只加 gap 不猜值；flag 可回滚。
2. **production entrypoint 是什么？** `scripts/contracts/constants.py`（3.8 词汇）+ `scripts/schema_compatibility.py`（EMIT 矩阵）+ `scripts/contracts/document.py`（版本门 + operating_units 校验）+ 新 `scripts/schema_optin.py`（converter）。
3. **RED？** 探针：document.py:79 严格 `schema_version == "3.7"`；SUPPORTED/EMIT 无 3.8；operating_units 词汇零命中——3.8 opt-in 与 converter 零实现。
4. **允许改哪些文件？** revenue：constants.py、schema_compatibility.py、document.py（版本门 + helper 调用）、新 scripts/schema_optin.py、新 tests/test_zr711_schema_optin.py；receipts/ZR-711/**。禁止：改 3.7 校验语义（零回归）、golden hash 变更、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** 解锁 ZR-707（依赖 ZR-711）。本卡不做：mixed recognition/gross-net 模型组合（ZR-707）、backtest（ZR-708/713）。

## Acceptance criteria
- **C1 3.7 零回归**：FORECAST_SCHEMA_VERSION 保持 "3.7"；全量测试零回归（golden behavior hash 不变）；3.7 文档校验行为逐字不变。
- **C2 3.8 opt-in**：文档可声明 schema_version "3.8"（版本门接受 {3.7, 3.8}）；加性键 `operating_units`（列表）存在时校验——每个条目必须通过 validate_mine_year_operation（复用 ZR-605 七字段契约，缺字段 gap fail-closed）；缺省（无键）兼容。词汇：SUPPORTED_FORECAST_SCHEMA_VERSIONS += "3.8"；SCHEMA_EMIT_ENGINES["3.8"] = {ENGINE_VERSION}（保持 SUPPORTED ⊆ EMIT 一致性）。
- **C3 converter 只加 gap 可回滚**：convert_3_7_to_3_8——版本号 → 3.8 + operating_units 置空列表（显式 gap，绝不猜测矿数据）；convert_3_8_to_3_7——版本号回 3.7 + 剥离 3.8 加性键；round-trip convert_3_8_to_3_7(convert_3_7_to_3_8(doc)) 与原文档语义相等（canonical equality）。
