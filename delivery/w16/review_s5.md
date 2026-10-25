# W16 独立审查 — S5（兼容性与代码质量，只读静态审查）

- 工区: `C:/Users/郑曾波/Projects/revenue-forecast-w16-basis`，commit `84e2152f`（对照 `84e2152f~1`）
- 审查人: S5（未参与实现）｜日期: 2026-10-25｜方式: 源码比对 + 只读内存执行验证 + ruff
- 结论: **通过（有条件）**。6 项审查中 6 项 PASS/基本 PASS；findings 共 3 条（1 Medium、1 Low、1 Info），无阻断性缺陷。

## Findings

### S5-1 [Medium] `_engine_unit_currency` 漏掉 DU5 别名拼写，误拒合法 engine_unit
- 证据: `scripts/research/revenue_basis.py:353-359` 仅做 `[-\s]+→_` + lower 后查 `_UNIT_DESCRIPTIONS`（只含**规范名**键）；而 DU5 的 `_normalize_unit`（`scripts/research/input_quantities.py:164-176`）经 `_UNIT_ALIASES` 别名表解析。实测（内存执行）：`validate_input_quantity_record` 接受 `engine_unit="usd units"`/`"usd 万"`/`"rmb_亿元"`，随后 `_validate_history_input_quantity`（revenue_basis.py:330-334）却报 "is not a money unit" —— fail-closed 的假阴性，拒绝合法输入且报错信息误导。
- 建议: 在 `input_quantities` 暴露公共 helper（如 `engine_unit_currency(unit)`，内部走 `_UNIT_ALIASES`→description），revenue_basis 改调它；这同时消除读私有表和重复归一化两个问题。临时规避: engine_unit 写规范拼写（如 `usd_unit`、`usd_10k`）。
- 关于读 DU5 私有表本身（trade-off）: 现无公共 unit→currency API（`money_currency` 只收币种拼写），reach-in 是务实选择；真正的缺陷在只复制了一半归一化逻辑（本 finding 的根因），而非私有访问本身。

### S5-2 [Low, 沿袭] `float(extracted)` 对非数字字符串抛裸 ValueError
- 证据: `revenue_basis.py:301-310` 的 walrus + `float(extracted)`：`extracted_value="12,345"` 时实测抛 `ValueError: could not convert string to float`（非 ForecastInputError、无字段定位）。`validate_evidence_claims` 只对 parameter 目标 claim 做 `finite_number(extracted_value)`（`document.py:728-731`），historical_revenue 目标不校验数字类型。该表达式自旧版 document.py 逐字搬移（`84e2152f~1` 同段），非 W16 回归；但 W16 新增 components 路径（revenue_basis.py:242-248）使其多一个可达入口。
- 建议: 用 `finite_number` 风格守卫或 `try/except ValueError → require(False, ...)`，把崩溃转为字段化 ForecastInputError。

### S5-3 [Info] lint finding 的 message 与 path 冗余
- 证据: `lint_input.py:184-190`，path=`historical_revenue.{year}.revenue_basis`，message=`str(exc)` 又以 `historical_revenue[{year}].revenue_basis...` 开头。仅观感问题，不影响机读。

## 分项结论（各给证据）

1. **消息字节兼容 — PASS**: 旧三条（`84e2152f~1` document.py）与新 `validate_historical_claim_alignment`（revenue_basis.py:287-318，label 默认 `"historical revenue "` 带尾随空格）逐字符比对一致；内存执行实测输出 `historical revenue claim value/period/unit mismatch: 2020` 三条与旧串完全相同。unit 比较值由 document.py:218 原样传入 `f"{data['currency']} {data['unit']}"`，检查顺序（value→period→unit）未变。
2. **lint 行为 — PASS**: 新增块整体在 `if "revenue_basis" in record:` 之内（lint_input.py:180），legacy 记录零新 finding（实测：仅剩既有 claim 引用项）；坏 basis 实测产生恰好 1 条 `revenue_basis` 类 finding（parse 首错即抛）且不崩溃（`parse_revenue_basis` 内无裸 float/IO，`except ForecastInputError` 精确捕获）。跨文档规则留给引擎属设计声明，非缺陷。
3. **模板 — PASS**: W16 对 `generate_input_template.py` 的全部变更是 `_comment` 追加 12 行说明句（diff 确认，无结构键变更、historical_revenue 骨架未加 revenue_basis），纯加法；`_comment` 为既有自由文本键，生成文档 schema 不变，仍是合法 legacy 输入。
4. **revenue_basis.py 质量 — 基本 PASS（见 S5-1/S5-2）**: 无网络/文件 IO（imports 仅 math/re/decimal/typing + 本地模块）；无全局可变状态（模块级常量只读，函数均构造新容器返回）；唯一 `except`（`decimal_sum_matches` revenue_basis.py:406-418）捕后返回 False = 判定不可勾稽 → fail-closed，不吞错；私有表访问评估见 S5-1。
5. **ruff — PASS**: `python -m ruff check`（五文件）"All checks passed!"，exit 0（ruff 0.15.18）。
6. **render 只读 — PASS**: `_historical_basis_view_for_result`（revenue_report.py:1521-1537）只读 result；`historical_basis_view`（revenue_basis.py:421-529）全部构建新 dict，`source_ids` 经 `list(...)` 拷贝（:513），不回写 history/result；`_basis_comparability_lines`/`_base_adoption_lines`/渲染循环（revenue_report.py:1540-1700）均只读取 view 与 record。
