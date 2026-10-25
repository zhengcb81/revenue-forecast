# 独立审查报告 S3 — W16 B04 总额复算桥（只读静态审查）

- 审查人：S3（未参与实现）
- 工区：C:/Users/郑曾波/Projects/revenue-forecast-w16-basis，commit 84e2152f8717179a4b7999739dac092c442004c0（工作树除 delivery/ 外干净）
- 范围：scripts/research/revenue_basis.py（parse_revenue_basis / _parse_components /
  validate_basis_against_document / decimal_sum_matches）及
  scripts/contracts/document.py validate_historical_revenue 接线段（L161-255）
- 方法：通读源码 + git show 84e2152f 核对 W16 增量 + 单元测试定位 +
  只读运行 decimal_sum_matches/_parse_components 行为抽查（未改任何文件）

## 审查项结论

### 1. components 仅限 operations=total；强制双侧齐备；单侧拒绝 — PASS
- 仅 total 可携带：revenue_basis.py L213-217 `require(basis["operations"] == "total", ...)`
  （"components decompose the consolidated total"）。
- 双侧强制：L218-223 `declared == set(_COMPONENT_OPERATIONS)`，缺任一侧即报
  "must declare both continuing and discontinued operations before the total is recomputed"。
  _parse_components L152-160 限定每个 component 只能是 continuing/discontinued 且不得重复。
- 单侧数值巧合=总额仍拒绝：tests/test_w16_revenue_basis.py L279-286
  test_components_require_both_sides 用 continuing=150.0（=记录总额 150.0）单侧提交，
  断言 ForecastInputError；L301 test_components_only_on_total_operations 覆盖非 total 携带。

### 2. component claims 复用 exact_value 全套校验；期间钉死 FY{year} — PASS
- L231-238 与记录级（document.py L206-213）完全同参调用 validate_claim_ids：
  target_type="historical_revenue"、target_id=f"historical_revenue:{year}"、
  support_type="exact_value"（evidence.py L177-203 强制 support_type/target 匹配）。
- L242-248 复用 validate_historical_claim_alignment（L287-318，git diff 证实为从
  validate_historical_revenue 原样提取、消息字节兼容）：值 abs_tol=1e-9 对齐、
  全部 claim 期间 == f"FY{year}"（L312）、单位 == f"{currency} {unit}"（L315-318）。
  无第二个对齐实现。测试 L289 覆盖跨 component 借用 claim 被拒。

### 3. decimal_sum_matches 真用 Decimal + 文档容差 — PASS
- L412-418：Decimal(str(total))、Decimal(str(part))，window =
  Decimal(str(max(1.0, abs(total)))) * Decimal(str(tolerance))，即
  max(1,|total|)*tolerance 约定，与 document.py L251 基年对账容差同式；
  sum() 在 Decimal 序列上，无 float 连加；InvalidOperation/ValueError 返回 False。
- 容差取自文档 reconciliation_tolerance（revenue_basis.py L249-252，
  默认 1e-6；document.py L1049-1051 校验非负）。
- 只读抽查：0.1+0.2=0.3 判 True（float 连加会放大误差的用例）；
  1e9±1 在放缩窗口内 True；60+39.99 vs 100 判 False；非数值输入安全返回 False。

### 4. 无 as_reported↔restated 自动转换、无自造前期调整 — PASS
- statement_status 全部出现点：parse 枚举校验、basis_comparable L384-391
  （差异仅返回 not_comparable+理由，理由明言 "without an explicit restatement
  bridge the figures are not silently comparable"）、historical_basis_view 只读渲染。
- validate_basis_against_document 仅抛错不改值（docstring "never rewrites the
  observation"）；historical_basis_view "never mutates the history"。
  全模块无任何按 statement_status 改写/调整数值的路径；重述差异只进诊断。

### 5. 无 components 时不复算不报错（旧行为）— PASS
- 记录无 revenue_basis：parse_revenue_basis L94-95 返回 None，接线（document.py
  L220-221）整体跳过，normalized.append 逻辑与 W16 前一致。
- 有 basis 无 components：L211-212 `if components is not None` 跳过整个复算块。
- git show 84e2152f（document.py）：记录级三段对齐校验被原样搬入共享函数，
  无其他数值行为改动。

## Findings（均不阻断，无 中/高危）

- [S3-1/LOW/证据/suggestion] lint_input.py L181-190 仅调用 parse_revenue_basis
  （schema 层），双侧齐备与 Decimal 复算两类文档级校验不进 linter，而其旁注称
  "the linter and the engine report the same rule"，表述偏强。契约路径已完整强制，
  无数值风险。建议：linter 具备 data/claim_index，可补调文档级校验，或改写注释。
- [S3-2/LOW/证据/suggestion] component value 仅 finite 校验（revenue_basis.py L162），
  无 >=0 约束（记录级 value 有 document.py L195 的非负要求）。负 component 可经
  复算+exact_value claim 钉住，完整性无洞，但"终止经营收入为负"语义未经披露约束。
  建议：如无冲退语义预期，补非负校验或在模板注明允许理由。

## 总结

五项审查全部 PASS：总额=持续+终止复算桥仅在双侧齐备、同 FY 期间、同币种单位、
claim 全套对齐、Decimal+文档容差下执行；无任何重述自动转换或自造调整；
无声明/无 components 时保持 W16 前行为。2 个 LOW finding 均属边角改进。
