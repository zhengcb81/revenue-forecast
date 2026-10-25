# W16-RF-BASIS 作者复审记录

独立审查执行方式（用户指定）：单一大审查agent连续三次因模型后端繁忙中断后，拆分为 S1–S5（静态，并发）+ S6（执行型，审修复后的最终代码）六个独立小片。全部审查agent未参与实现；原始分片报告与最终汇总见 [independent_review.md](independent_review.md) 及 review_s1…s6 文件。

## 作者处置汇总

| Finding | 严重度 | 内容 | 作者处置 | 复测 |
|---|---|---|---|---|
| S5-1 | Medium | engine_unit 别名拼写（usd_万 等）被误拒"not a money unit"；且未校验 engine_unit 尺度与文档单位一致 | 修复：DU5 公共 `money_unit_currency`/`money_unit_scale_factor`（input_quantities.py，本卡可写层）；revenue_basis 删除复制正则/私有表直查，改调公共层并新增尺度一致性校验 | 新增 `test_input_quantity_accepts_du5_alias_engine_unit`（usd_百万 别名通过）与 `test_input_quantity_scale_mismatch_is_rejected`（usd_yi 尺度拒绝）；41 W16 测试绿 |
| S2-1 | Low | `_engine_unit_currency` 复制 DU5 `_normalize_unit` 正则 | 同 S5-1 一并消除（正则与私有表访问均删除） | 同上 |
| S3-2 | Low | component value 无非负约束 | 修复：`_parse_components` require(value>=0)，消息含"cannot be negative" | `test_negative_component_value_is_rejected` 绿 |
| S5-2 | Low | 非数字 extracted_value 裸 ValueError（沿袭旧代码，W16 components 增加入口） | 修复：`_extract_matches` 安全比较（TypeError/ValueError → False），不再崩溃 | `test_non_numeric_extracted_value_does_not_crash` 绿（得到字段化 mismatch 错误） |
| S4-1 | Low | ytd 期间混淆未走 CLI | 修复：CLI 案例一 `test_ytd_period_kind_is_rejected`（目录"错 年累计 ytd"，断言 stderr 含 ytd+年累计） | CLI 9 例绿 |
| S4-2 | Info | 非 ASCII 目录仅成功例使用 | 顺带修复：ytd 错误案例用中文目录；子进程 env 钉 PYTHONIOENCODING/PYTHONUTF8 | 同上 |
| S3-1 | Low | lint 注释"same rule as engine"表述偏强 | 修复：注释如实写明 lint 只做 schema 层、文档级校验引擎所有（95c25c4b） | test_lint_input 23 绿 |
| S2-2 | Info | legacy 输入报告新增诊断小节 → 字节级 diff | 记录不改：COMMON/卡片允许加法诊断；渲染措辞符合"不把未声明说成已核实"；已写入 handoff 兼容边界 | — |
| S5-3 | Info | lint finding message/path 前缀冗余 | 记录不改：观感问题，机读字段完整 | — |

S6（执行型，0 finding）复核了修复后代码：独立运行 W16 41 测试、回归 41、真实 CLI 中文/空格目录端到端、7 个自建反例（反向重述混合、非基年组件、4 种输出篡改突变、复数单位拼写、claim 期间错配）全部正确判定。

## 复审后测试状态（cb60bd21 + 95c25c4b）

- `python -m pytest -q tests/test_w16_revenue_basis.py tests/test_w16_revenue_basis_cli.py` → 41 passed
- `python -m pytest -q tests/test_data_contract.py tests/test_recognition_bridge.py tests/test_publication_pipeline.py tests/test_golden_behavior_lock.py tests/test_du5_money_unit_registry.py tests/test_input_quantity_conversion.py tests/test_du5_root_unit_boundaries.py tests/test_lint_input.py` → 172 passed, 1 skipped, 59 subtests
- `python tools/pre_push_gate.py` → GREEN（ruff+mypy 12 文件；595 passed 1 skipped）
- S6 独立复跑同样全绿（见 review_s6_exec.md）

未解决本范围 finding：0。状态可 COMPLETE（ROOT 接收另计）。
